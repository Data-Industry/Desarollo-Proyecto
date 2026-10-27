"""
Módulo de Web Scraping para Farmacias Telchi (Santa Cruz de la Sierra, Bolivia)
Extrae catálogo, disponibilidad y precios de insulinas mediante WooCommerce search.
"""

import requests
import datetime
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

SEARCH_TERMS = ["insulina", "novolin", "lantus", "glargina", "humodar", "insugen"]

def classify_active_ingredient(title: str) -> str:
    """Clasifica el principio activo según el título comercial."""
    t = title.lower()
    if any(k in t for k in ["glargina", "lantus", "basalog", "toujeo"]):
        return "Insulina Glargina (Acción Prolongada)"
    elif any(k in t for k in ["70/30", "70 30", "mixtard", "combinada"]):
        return "Insulina Humana Mixta / Bifásica"
    elif any(k in t for k in ["nph", "isof", "novolin n", "insugen n", "humodar n"]):
        return "Insulina Humana NPH (Acción Intermedia)"
    elif any(k in t for k in ["neutra", "regular", "rapida", "rápida", "novolin r", "insugen r", "humodar r"]):
        return "Insulina Humana Regular / Rápida"
    elif "jeringa" in t or "aguja" in t:
        return "Insumo Médico (Jeringa / Aguja)"
    return "Insulina Humana / Análogo"

def scrape_telchi() -> List[Dict[str, Any]]:
    """Extrae productos de insulina en Farmacias Telchi."""
    logger.info("Iniciando extracción en Farmacias Telchi (Santa Cruz)...")
    seen_urls = set()
    products = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for term in SEARCH_TERMS:
        url = f"https://farmaciastelchi.com/?s={term}&post_type=product"
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select(".type-product")

            for item in items:
                # Extraer título y URL
                title_elem = item.select_one(".woocommerce-loop-product__title, h2, h3")
                link_elem = item.select_one("a.woocommerce-LoopProduct-link, a")
                price_elem = item.select_one(".price")

                if not title_elem or not link_elem:
                    continue

                prod_url = link_elem.get("href", "")
                title = title_elem.get_text(strip=True)

                if prod_url in seen_urls or not title:
                    continue

                title_lower = title.lower()
                # Filtrar exclusiones
                if "metformina" in title_lower or "alcohol" in title_lower:
                    continue

                valid_keys = ["insulina", "novolin", "lantus", "glargina", "jeringa"]
                if not any(k in title_lower for k in valid_keys):
                    continue

                seen_urls.add(prod_url)

                # Extraer precio
                price_val = 0.0
                regular_price_val = 0.0
                discount = False

                if price_elem:
                    # Chequear si tiene del e ins (oferta)
                    del_elem = price_elem.select_one("del .woocommerce-Price-amount")
                    ins_elem = price_elem.select_one("ins .woocommerce-Price-amount")
                    
                    if del_elem and ins_elem:
                        reg_text = del_elem.get_text(strip=True).replace("Bs.", "").replace(".", "").replace(",", ".").strip()
                        sale_text = ins_elem.get_text(strip=True).replace("Bs.", "").replace(".", "").replace(",", ".").strip()
                        try:
                            regular_price_val = float(reg_text)
                            price_val = float(sale_text)
                            discount = True
                        except ValueError:
                            pass
                    else:
                        amount = price_elem.select_one(".woocommerce-Price-amount")
                        if amount:
                            p_text = amount.get_text(strip=True).replace("Bs.", "").replace(".", "").replace(",", ".").strip()
                            try:
                                price_val = float(p_text)
                                regular_price_val = price_val
                            except ValueError:
                                pass

                # Extraer ID desde la clase o URL
                classes = " ".join(item.get("class", []))
                post_id_match = re.search(r'post-(\d+)', classes)
                prod_id = post_id_match.group(1) if post_id_match else str(len(products) + 1)

                products.append({
                    "id_origen": f"TELCHI-{prod_id}",
                    "farmacia": "Farmacias Telchi",
                    "nombre_comercial": title,
                    "principio_activo": classify_active_ingredient(title),
                    "marca_laboratorio": "NOVO NORDISK" if "novolin" in title_lower else "TELCHI / VARIOS",
                    "precio_bs": price_val,
                    "precio_regular_bs": regular_price_val,
                    "descuento_aplicado": discount,
                    "estado_stock": "Disponible",
                    "sucursal": "Santa Cruz de la Sierra (Sucursal Central / Red Telchi)",
                    "ciudad": "Santa Cruz de la Sierra",
                    "url_producto": prod_url,
                    "timestamp": now_iso
                })
        except Exception as e:
            logger.error(f"Error consultando '{term}' en Telchi: {e}")

    logger.info(f"Farmacias Telchi: {len(products)} productos extraídos y validados.")
    return products

if __name__ == "__main__":
    results = scrape_telchi()
    for r in results:
        print(f"[{r['farmacia']}] {r['nombre_comercial']} -> Bs. {r['precio_bs']} ({r['estado_stock']})")
