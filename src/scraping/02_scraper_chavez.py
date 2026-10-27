"""
Módulo de Web Scraping para Farmacias Chávez Bolivia
Extrae catálogo, disponibilidad y precios de insulinas mediante automatización Playwright.
"""

import asyncio
import datetime
import logging
import re
from typing import List, Dict, Any
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXCLUDE_KEYWORDS = [
    "shampoo", "toallita", "panal", "pañal", "jabon", "jabón", 
    "desmaquillante", "esmalte", "crema", "pomada", "polvo",
    "glicenex", "glucophage", "glucovance", "meglyn", "metformina"
]

def classify_active_ingredient(title: str) -> str:
    """Clasifica el principio activo según la denominación comercial."""
    t = title.lower()
    if any(k in t for k in ["glargina", "lantus", "basalog", "toujeo", "glaritus", "glaripen"]):
        return "Insulina Glargina (Acción Prolongada)"
    elif any(k in t for k in ["glulisina", "apidra"]):
        return "Insulina Glulisina (Acción Rápida)"
    elif any(k in t for k in ["aspart", "asparpen", "novorapid"]):
        return "Insulina Asparta (Acción Ultrarrápida)"
    elif any(k in t for k in ["lispro", "humalog"]):
        return "Insulina Lispro (Acción Rápida)"
    elif any(k in t for k in ["degludec", "tresiba"]):
        return "Insulina Degludec (Acción Ultralarga)"
    elif any(k in t for k in ["70/30", "70 30", "combinada", "c25", "mixtard"]):
        return "Insulina Humana Mixta / Bifásica"
    elif any(k in t for k in ["nph", "insugen n", "glinux n", "novolin n", "densulin n", "humodar nph", "humodar n"]):
        return "Insulina Humana NPH (Acción Intermedia)"
    elif any(k in t for k in ["rapida", "rápida", "regular", "insugen r", "novolin r", "humodar r", "densulin r"]):
        return "Insulina Humana Regular / Rápida"
    elif "jeringa" in t or "aguja" in t:
        return "Insumo Médico (Jeringa / Aguja)"
    return "Insulina Humana / Análogo"

async def _scrape_chavez_async() -> List[Dict[str, Any]]:
    """Función asíncrona interna que ejecuta Playwright para Farmacias Chávez."""
    products = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    seen_urls = set()

    async with async_playwright() as p:
        logger.info("Iniciando navegador headless para Farmacias Chávez...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        try:
            # Navegar a la página de inicio
            await page.goto("https://www.farmaciaschavez.com.bo", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            # Localizar input de búsqueda
            search_input = await page.wait_for_selector('input[type="text"], input[type="search"]', timeout=10000)
            if search_input:
                await search_input.fill("insulina")
                await page.wait_for_timeout(1000)
                await page.keyboard.press("Enter")
                logger.info("Búsqueda de 'insulina' enviada en Farmacias Chávez. Esperando resultados...")
                await page.wait_for_timeout(5000)

            # Extraer los elementos de productos del DOM
            raw_items = await page.evaluate('''() => {
                const results = [];
                const links = document.querySelectorAll('a[href*="/p/"]');
                links.forEach(a => {
                    const text = a.innerText.trim();
                    const href = a.href;
                    results.push({ text, href });
                });
                return results;
            }''')

            for item in raw_items:
                href = item.get("href", "")
                text = item.get("text", "")
                if href in seen_urls or not text:
                    continue

                lines = [l.strip() for l in text.split("\n") if l.strip()]
                # Verificar que sea producto de insulina
                full_text = " ".join(lines).lower()
                if any(bad in full_text for bad in EXCLUDE_KEYWORDS):
                    continue
                
                # Criterio médico
                valid_keys = ["insulina", "lantus", "glargina", "basalog", "novolin", "insugen", "glinux", "humodar", "apidra", "toujeo", "jeringa", "densulin", "asparpen", "glaritus", "glaripen"]
                if not any(k in full_text for k in valid_keys):
                    continue

                seen_urls.add(href)

                # Parsear nombre comercial (usualmente la última o penúltima línea que no es precio ni ahorro)
                title = ""
                for l in reversed(lines):
                    if not l.startswith("Bs") and not l.startswith("(Bs") and not l.startswith("Ahorra") and not "unidades" in l.lower() and not "canasta" in l.lower():
                        title = l
                        break
                if not title:
                    title = lines[-1]

                # Parsear precios: "Bs 1.390,35", "(Bs 1.495)"
                price_val = 0.0
                regular_price_val = 0.0
                discount = False
                stock_status = "Disponible"

                if "últimas unidades" in full_text or "ultimas unidades" in full_text:
                    stock_status = "Últimas unidades"

                for l in lines:
                    # Precio actual
                    if l.startswith("Bs ") and not l.startswith("(Bs"):
                        clean_num = l.replace("Bs ", "").replace(".", "").replace(",", ".").strip()
                        try:
                            price_val = float(clean_num)
                        except ValueError:
                            pass
                    # Precio regular tachado
                    elif l.startswith("(Bs "):
                        clean_num = l.replace("(Bs ", "").replace(")", "").replace(".", "").replace(",", ".").strip()
                        try:
                            regular_price_val = float(clean_num)
                            discount = True
                        except ValueError:
                            pass

                if not regular_price_val or regular_price_val < price_val:
                    regular_price_val = price_val

                # Extraer ID desde la URL (ej: lantus-100-ui-insulina-glargina-x-10-ml-7503 -> 7503)
                url_match = re.search(r'-(\d+)$', href)
                item_id = url_match.group(1) if url_match else str(len(products) + 1)

                products.append({
                    "id_origen": f"CHAVEZ-{item_id}",
                    "farmacia": "Farmacias Chávez",
                    "nombre_comercial": title,
                    "principio_activo": classify_active_ingredient(title),
                    "marca_laboratorio": "No especificado",
                    "precio_bs": price_val,
                    "precio_regular_bs": regular_price_val,
                    "descuento_aplicado": discount,
                    "estado_stock": stock_status,
                    "sucursal": "Santa Cruz de la Sierra (Sucursal Central / Cobertura Red)",
                    "ciudad": "Santa Cruz de la Sierra",
                    "url_producto": href,
                    "timestamp": now_iso
                })

        except Exception as e:
            logger.error(f"Error extrayendo datos de Farmacias Chávez: {e}")
        finally:
            await browser.close()

    logger.info(f"Farmacias Chávez: {len(products)} productos extraídos y validados.")
    return products

def scrape_chavez() -> List[Dict[str, Any]]:
    """Envoltorio síncrono para ejecutar el scraper de Farmacias Chávez."""
    return asyncio.run(_scrape_chavez_async())

if __name__ == "__main__":
    results = scrape_chavez()
    for r in results:
        print(f"[{r['farmacia']}] {r['nombre_comercial']} -> Bs. {r['precio_bs']} ({r['estado_stock']})")
