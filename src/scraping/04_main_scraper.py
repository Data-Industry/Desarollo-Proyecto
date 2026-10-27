"""
Orquestador Principal de Web Scraping de Insulina en Bolivia
Ejecuta la extracción periódica de catálogos en Farmacorp y Farmacias Chávez,
consolida el dataset maestro y lo exporta a data/raw/.
"""

import os
import sys
import datetime
import logging
import pandas as pd
import json

# Agregar src al path si se ejecuta directamente
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from src.scraping.scraper_farmacorp import scrape_farmacorp
from src.scraping.scraper_chavez import scrape_chavez
from src.scraping.scraper_telchi import scrape_telchi

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ScraperOrchestrator")

def run_pipeline() -> pd.DataFrame:
    """Ejecuta los scrapers configurados y genera los datasets estructurados en data/raw/."""
    start_time = datetime.datetime.now()
    logger.info("=== INICIANDO PIPELINE DE EXTRACCIÓN DE INSULINAS (BOLIVIA) ===")
    
    # 1. Extracción de Farmacorp
    farmacorp_data = []
    try:
        farmacorp_data = scrape_farmacorp()
    except Exception as e:
        logger.error(f"Falla al ejecutar scraper de Farmacorp: {e}")

    # 2. Extracción de Farmacias Chávez
    chavez_data = []
    try:
        chavez_data = scrape_chavez()
    except Exception as e:
        logger.error(f"Falla al ejecutar scraper de Farmacias Chávez: {e}")

    # 3. Extracción de Farmacias Telchi
    telchi_data = []
    try:
        telchi_data = scrape_telchi()
    except Exception as e:
        logger.error(f"Falla al ejecutar scraper de Farmacias Telchi: {e}")

    # Consolidar registros
    all_records = farmacorp_data + chavez_data + telchi_data
    if not all_records:
        logger.error("No se extrajeron registros en ninguna de las fuentes.")
        return pd.DataFrame()

    df = pd.DataFrame(all_records)

    # Ordenar y asegurar tipos de datos
    df["precio_bs"] = pd.to_numeric(df["precio_bs"], errors="coerce")
    df["precio_regular_bs"] = pd.to_numeric(df["precio_regular_bs"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Directorio de destino
    raw_dir = os.path.join(PROJECT_DIR, "data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")
    csv_timestamped = os.path.join(raw_dir, f"insulina_precios_stock_{timestamp_str}.csv")
    csv_latest = os.path.join(raw_dir, "insulina_precios_stock_latest.csv")
    json_latest = os.path.join(raw_dir, "insulina_precios_stock_latest.json")

    # Exportación con tolerancia a bloqueos de archivo (ej. si el usuario tiene el CSV abierto en Excel)
    try:
        df.to_csv(csv_timestamped, index=False, encoding="utf-8-sig")
    except Exception as e:
        logger.warning(f"No se pudo guardar copia histórica timestamped: {e}")

    try:
        df.to_csv(csv_latest, index=False, encoding="utf-8-sig")
    except PermissionError:
        fallback_csv = os.path.join(raw_dir, "insulina_precios_stock_latest_updated.csv")
        df.to_csv(fallback_csv, index=False, encoding="utf-8-sig")
        logger.warning(f"El archivo '{csv_latest}' está abierto en otra aplicación (ej. Excel). Se guardó en '{fallback_csv}'.")
    except Exception as e:
        logger.error(f"Error guardando CSV principal: {e}")
    
    # Exportar JSON estructurado
    try:
        with open(json_latest, "w", encoding="utf-8") as f:
            json.dump(all_records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando JSON: {e}")

    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    logger.info(f"=== PIPELINE COMPLETADO EXITOSAMENTE EN {elapsed:.2f} SEGUNDOS ===")
    logger.info(f"Total productos extraídos: {len(df)}")
    logger.info(f"  - Farmacorp: {len(farmacorp_data)}")
    logger.info(f"  - Farmacias Chávez: {len(chavez_data)}")
    logger.info(f"  - Farmacias Telchi: {len(telchi_data)}")
    logger.info(f"Datasets generados en: {raw_dir}")

    return df

if __name__ == "__main__":
    df_result = run_pipeline()
    if not df_result.empty:
        print("\n--- RESUMEN ANALÍTICO DE PRECIOS Y STOCK POR CADENA ---")
        summary = df_result.groupby(["farmacia", "estado_stock"]).agg(
            total_items=("nombre_comercial", "count"),
            precio_min=("precio_bs", "min"),
            precio_promedio=("precio_bs", "mean"),
            precio_max=("precio_bs", "max")
        ).round(2)
        print(summary)
