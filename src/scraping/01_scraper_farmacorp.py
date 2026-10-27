"""
Módulo de Web Scraping para Farmacorp Bolivia
Extrae catálogo, disponibilidad y precios de insulinas y medicamentos relacionados.
"""

import requests
import datetime
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Términos clave para rastreo de insulinas en el catálogo
SEARCH_TERMS = [
    "insulina",
    "lantus",
    "glargina",
    "basalog",
    "novolin",
    "insugen",
    "glinux",
    "humodar",
    "apidra",
    "toujeo",
    "humalog",
    "tresiba",
    "densulin",
    "asparpen",
    "glaritus",
    "glaripen"
]

# Palabras clave excluyentes para evitar falsos positivos
EXCLUDE_KEYWORDS = [
    "shampoo", "toallita", "panal", "pañal", "jabon", "jabón", 
    "desmaquillante", "esmalte", "chocolate", "helado", "crema",
    "hisopo", "cotonete", "magnesio", "vitamina d3", "jugo"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def classify_active_ingredient(title: str) -> str:
    """Clasifica el principio activo según el título comercial."""
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
    elif any(k in t for k in ["70/30", "70 30", "combinada", "c25", "mixtard", "biphasic"]):
        return "Insulina Humana Mixta / Bifásica"
    elif any(k in t for k in ["nph", "insugen n", "glinux n", "novolin n", "densulin n", "humodar nph"]):
        return "Insulina Humana NPH (Acción Intermedia)"
    elif any(k in t for k in ["rapida", "rápida", "regular", "insugen r", "novolin r", "humodar r", "densulin r"]):
        return "Insulina Humana Regular / Rápida"
    elif "jeringa" in t or "aguja" in t:
        return "Insumo Médico (Jeringa / Aguja)"
    return "Insulina Humana / Análogo"

def scrape_farmacorp() -> List[Dict[str, Any]]:
    """Ejecuta la extracción de productos de insulina en Farmacorp."""
    logger.info("Iniciando extracción en Farmacorp Bolivia...")
    seen_ids = set()
    products = []
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for term in SEARCH_TERMS:
        url = f"https://farmacorp.com/search/suggest.json?q={term}&resources[type]=product&resources[limit]=25"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code != 200:
                logger.warning(f"Error {resp.status_code} al buscar '{term}' en Farmacorp")
                continue
            
            data = resp.json()
            items = data.get("resources", {}).get("results", {}).get("products", [])
            for item in items:
                prod_id = item.get("id")
                title = item.get("title", "").strip()
                
                # Filtrar duplicados y falsos positivos
                if prod_id in seen_ids or not title:
                    continue
                
                title_lower = title.lower()
                if any(bad in title_lower for bad in EXCLUDE_KEYWORDS):
                    continue
                
                # Debe contener al menos una referencia médica válida
                valid_medic_terms = ["insulina", "lantus", "glargina", "basalog", "novolin", "insugen", "glinux", "humodar", "apidra", "toujeo", "jeringa", "densulin", "asparpen", "glaritus"]
                if not any(v in title_lower for v in valid_medic_terms):
                    continue
                
                seen_ids.add(prod_id)
                price_str = item.get("price", "0")
                try:
                    price_val = float(price_str)
                except ValueError:
                    price_val = 0.0

                available = item.get("available", False)
                stock_status = "Disponible" if available else "Agotado"
                handle = item.get("handle", "")
                prod_url = f"https://farmacorp.com/products/{handle}" if handle else "https://farmacorp.com"
                
                # Opcional: obtener datos del producto detallado (precio regular de lista)
                compare_price = None
                vendor = item.get("vendor", "")
                try:
                    det_resp = requests.get(f"https://farmacorp.com/products/{handle}.json", headers=HEADERS, timeout=8)
                    if det_resp.status_code == 200:
                        prod_det = det_resp.json().get("product", {})
                        vendor = prod_det.get("vendor", vendor)
                        variants = prod_det.get("variants", [])
                        if variants:
                            cp = variants[0].get("compare_at_price")
                            if cp:
                                compare_price = float(cp)
                except Exception:
                    pass

                products.append({
                    "id_origen": f"FARMACORP-{prod_id}",
                    "farmacia": "Farmacorp",
                    "nombre_comercial": title,
                    "principio_activo": classify_active_ingredient(title),
                    "marca_laboratorio": vendor or "No especificado",
                    "precio_bs": price_val,
                    "precio_regular_bs": compare_price if compare_price else price_val,
                    "descuento_aplicado": bool(compare_price and compare_price > price_val),
                    "estado_stock": stock_status,
                    "sucursal": "Santa Cruz de la Sierra (Cobertura Red Farmacorp)",
                    "ciudad": "Santa Cruz de la Sierra",
                    "url_producto": prod_url,
                    "timestamp": now_iso
                })
        except Exception as e:
            logger.error(f"Excepción consultando término '{term}' en Farmacorp: {e}")

    logger.info(f"Farmacorp: {len(products)} productos extraídos y validados.")
    return products

if __name__ == "__main__":
    results = scrape_farmacorp()
    for r in results:
        print(f"[{r['farmacia']}] {r['nombre_comercial']} -> Bs. {r['precio_bs']} ({r['estado_stock']})")
