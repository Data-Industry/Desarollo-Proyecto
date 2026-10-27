"""
Pipeline ETL: Limpieza, Estandarización y Normalización de Insulinas
Historia de Usuario: US-22 (Fase 3: Preparación de los Datos - CRISP-DM)

Este módulo procesa los datasets crudos generados por el web scraping, descarta
insumos desechables (jeringas, agujas, otros fármacos) y normaliza las variables
médicas y económicas para generar el dataset maestro en data/processed/.
"""

import os
import sys
import glob
import logging
import pandas as pd
import numpy as np
import json
from typing import Tuple, Dict, Any, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ETL-Insulinas")

# Rutas del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# Lista de palabras clave para descartar insumos descartables y fármacos no insulina
EXCLUDE_TERMS = [
    "jeringa", "aguja", "denosumab", "densimab", "resyniv", 
    "acido hialur", "hialuronico", "ibesia", "toallita", "panal", "pañal"
]

def parse_presentation(title: str) -> Tuple[float, int, str]:
    """
    Extrae el volumen en ml, la concentración en UI/ml y el formato de presentación.
    """
    t = title.lower()
    
    # Detección de volumen
    if "10 ml" in t or "10ml" in t or "x 10 ml" in t:
        volumen = 10.0
    elif "1.5 ml" in t or "1.5ml" in t or "15 ml" in t or "toujeo" in t:
        volumen = 1.5
    elif "3 ml" in t or "3ml" in t or "solostar" in t or "lapicera" in t or "cartucho" in t:
        volumen = 3.0
    else:
        volumen = 10.0  # Viales estándar tradicionales

    # Detección de concentración
    if "300" in t and ("toujeo" in t or "300ui" in t or "300 u" in t):
        concentracion = 300
    else:
        concentracion = 100

    # Detección de formato físico
    if any(k in t for k in ["solostar", "lapicero", "lapicera", "pluma"]):
        formato = "Lapicero Prellenado (Pluma)"
    elif any(k in t for k in ["cartucho", "cart", "pen"]):
        formato = "Cartucho para Pluma Reutilizable"
    else:
        formato = "Vial / Frasco Ampolla"

    return volumen, concentracion, formato

def identify_brand_and_lab(title: str) -> Tuple[str, str]:
    """Identifica la marca comercial canónica y el laboratorio fabricante."""
    t = title.lower()
    if "lantus" in t:
        return "Lantus", "Sanofi-Aventis"
    elif "toujeo" in t:
        return "Toujeo", "Sanofi-Aventis"
    elif "apidra" in t:
        return "Apidra", "Sanofi-Aventis"
    elif "basalog" in t:
        return "Basalog", "Biocon Biologics"
    elif "insugen" in t:
        return "Insugen", "Biocon Biologics"
    elif "novolin 70" in t or "novolin 70-30" in t or "novolin 70 30" in t:
        return "Novolin 70/30", "Novo Nordisk"
    elif "novolin r" in t:
        return "Novolin R", "Novo Nordisk"
    elif "novolin n" in t:
        return "Novolin N", "Novo Nordisk"
    elif "glinux" in t:
        return "Glinux N", "Laboratorios Bagó"
    elif "humodar c25" in t:
        return "Humodar C25", "Laboratorios Beta"
    elif "humodar r" in t:
        return "Humodar R", "Laboratorios Beta"
    elif "humodar n" in t or "humodar b" in t:
        return "Humodar NPH", "Laboratorios Beta"
    elif "densulin r" in t:
        return "Densulin R", "Denver Farma"
    elif "densulin n" in t:
        return "Densulin N", "Denver Farma"
    elif "densulent" in t:
        return "Densulent", "Denver Farma"
    elif "glaritus" in t:
        return "Glaritus", "Wockhardt"
    elif "glaripen" in t:
        return "Glaripen", "Wockhardt"
    elif "asparpen" in t:
        return "Asparpen", "Wockhardt"
    return "Insulina Genérica", "No especificado"

def identify_pharmacology(brand: str, title: str) -> Tuple[str, str, str]:
    """Clasifica principio activo, tipo de acción y origen biológico."""
    t = f"{brand} {title}".lower()
    if any(k in t for k in ["glargina", "lantus", "basalog", "toujeo", "glaritus", "glaripen", "densulent"]):
        return "Insulina Glargina", "Acción Prolongada (Basal)", "Análogo de Insulina"
    elif "glulisina" in t or "apidra" in t:
        return "Insulina Glulisina", "Acción Rápida (Prandial)", "Análogo de Insulina"
    elif "aspart" in t or "asparpen" in t:
        return "Insulina Asparta", "Acción Ultrarrápida (Prandial)", "Análogo de Insulina"
    elif any(k in t for k in ["70/30", "70 30", "70-30", "c25", "combinada", "mixtard"]):
        return "Insulina Humana Mixta / Bifásica", "Acción Mixta / Bifásica", "Insulina Humana ADN Recombinante"
    elif any(k in t for k in [" r", "regular", "neutra", "rapida", "rápida"]):
        return "Insulina Humana Regular (R)", "Acción Rápida (Prandial)", "Insulina Humana ADN Recombinante"
    elif any(k in t for k in [" n", "nph", "isof", " b "]):
        return "Insulina Humana NPH (N)", "Acción Intermedia (Basal)", "Insulina Humana ADN Recombinante"
    return "Insulina Humana", "Acción Intermedia", "Insulina Humana"

def run_etl_pipeline() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta el pipeline de ETL completo:
    1. Carga el dataset crudo consolidado.
    2. Aplica filtros de exclusión (descartando descartables y fármacos no insulina).
    3. Normaliza variables clínicas, farmacológicas y económicas.
    4. Genera métricas de estandarización (precio/ml, precio/100 UI, semáforo).
    5. Exporta el dataset maestro limpio y la bitácora de descartes a data/processed/.
    """
    logger.info("=== INICIANDO PIPELINE ETL DE LIMPIEZA Y NORMALIZACIÓN (US-22) ===")
    
    # 1. Cargar el dataset crudo más reciente
    raw_csv = os.path.join(RAW_DIR, "insulina_precios_stock_latest.csv")
    if not os.path.exists(raw_csv):
        # Intentar buscar el CSV con timestamp más reciente
        csv_candidates = glob.glob(os.path.join(RAW_DIR, "insulina_precios_stock_*.csv"))
        if not csv_candidates:
            raise FileNotFoundError(f"No se encontraron datasets crudos en {RAW_DIR}")
        raw_csv = max(csv_candidates, key=os.path.getctime)

    logger.info(f"Cargando dataset crudo desde: {raw_csv}")
    df_raw = pd.read_csv(raw_csv)
    logger.info(f"Total registros crudos leídos: {len(df_raw)}")

    cleaned_records: List[Dict[str, Any]] = []
    discarded_records: List[Dict[str, Any]] = []

    for _, row in df_raw.iterrows():
        title = str(row.get("nombre_comercial", "")).strip()
        price = float(row.get("precio_bs", 0.0))
        t_lower = title.lower()

        # Criterio de exclusión: descartables, jeringas y medicamentos no insulina
        is_non_insulin = any(k in t_lower for k in ["denosumab", "densimab", "resyniv", "acido hialur", "hialuronico", "ibesia"])
        is_desechable = price < 15.0 or any(k in t_lower for k in ["jeringa", "aguja", "toallita", "panal", "pañal"])
        if is_non_insulin or is_desechable:
            motivo = "Medicamento fuera de alcance (No insulina)" if is_non_insulin else "Insumo descartable (Jeringa / Aguja)"
            discarded_records.append({
                "id_origen": row.get("id_origen"),
                "farmacia": row.get("farmacia"),
                "nombre_comercial": title,
                "precio_bs": price,
                "motivo_descarte": motivo
            })
            continue

        # Normalización médica y farmacológica
        brand, lab = identify_brand_and_lab(title)
        principio_activo, tipo_accion, origen_bio = identify_pharmacology(brand, title)
        vol_ml, conc_ui_ml, formato = parse_presentation(title)
        
        # Cálculos de unidades y precios normalizados
        unidades_totales = int(vol_ml * conc_ui_ml)
        precio_lista = float(row.get("precio_regular_bs", price))
        if pd.isna(precio_lista) or precio_lista < price:
            precio_lista = price
        
        descuento_pct = round(((precio_lista - price) / precio_lista) * 100, 1) if precio_lista > price else 0.0
        precio_por_ml = round(price / vol_ml, 2)
        precio_por_100ui = round(price / (unidades_totales / 100), 2)

        # Normalización del estado de inventario y semáforo
        stock_raw = str(row.get("estado_stock", "")).strip().lower()
        if "agotado" in stock_raw:
            estado_norm = "AGOTADO"
            stock_bin = 0
            alerta = 1
            semaforo = "ROJO"
        elif "últimas" in stock_raw or "ultimas" in stock_raw:
            estado_norm = "ULTIMAS_UNIDADES"
            stock_bin = 1
            alerta = 1
            semaforo = "AMARILLO"
        else:
            estado_norm = "DISPONIBLE"
            stock_bin = 1
            alerta = 0
            semaforo = "VERDE"

        # Código canónico único master
        farm_prefix = "FMC" if "Farmacorp" in str(row.get("farmacia")) else ("CHV" if "Chávez" in str(row.get("farmacia")) else "TEL")
        id_master = f"INS-{farm_prefix}-{len(cleaned_records)+1:03d}"

        cleaned_records.append({
            "id_insulina_master": id_master,
            "id_origen": row.get("id_origen"),
            "farmacia": row.get("farmacia"),
            "marca_comercial": brand,
            "principio_activo": principio_activo,
            "tipo_accion": tipo_accion,
            "origen_biologico": origen_bio,
            "laboratorio_fabricante": lab,
            "formato_presentacion": formato,
            "volumen_ml": vol_ml,
            "concentracion_ui_ml": conc_ui_ml,
            "unidades_totales_ui": unidades_totales,
            "precio_venta_bs": round(price, 2),
            "precio_lista_bs": round(precio_lista, 2),
            "descuento_porcentaje": descuento_pct,
            "precio_por_ml_bs": precio_por_ml,
            "precio_por_100ui_bs": precio_por_100ui,
            "estado_stock": estado_norm,
            "stock_disponible_binario": stock_bin,
            "alerta_quiebre_stock": alerta,
            "semaforo_stock": semaforo,
            "sucursal": row.get("sucursal", "Santa Cruz de la Sierra"),
            "ciudad": "Santa Cruz de la Sierra",
            "departamento": "Santa Cruz",
            "url_producto": row.get("url_producto", ""),
            "timestamp_extraccion": row.get("timestamp")
        })

    df_cleaned = pd.DataFrame(cleaned_records)
    df_discarded = pd.DataFrame(discarded_records)

    # Ordenar por marca y precio
    df_cleaned.sort_values(by=["principio_activo", "marca_comercial", "precio_venta_bs"], inplace=True)
    df_cleaned.reset_index(drop=True, inplace=True)

    # Exportación a data/processed/
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    master_csv = os.path.join(PROCESSED_DIR, "insulinas_master.csv")
    master_json = os.path.join(PROCESSED_DIR, "insulinas_master.json")
    discard_csv = os.path.join(PROCESSED_DIR, "descartes_insumos_desechables.csv")

    df_cleaned.to_csv(master_csv, index=False, encoding="utf-8-sig")
    df_discarded.to_csv(discard_csv, index=False, encoding="utf-8-sig")
    
    with open(master_json, "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

    logger.info(f"=== PIPELINE ETL COMPLETADO EXITOSAMENTE ===")
    logger.info(f"Medicamentos de insulina limpios y normalizados: {len(df_cleaned)}")
    logger.info(f"Insumos / fármacos no insulina descartados: {len(df_discarded)}")
    logger.info(f"Dataset maestro guardado en: {master_csv}")
    logger.info(f"Bitácora de descartes guardada en: {discard_csv}")

    return df_cleaned, df_discarded

if __name__ == "__main__":
    df_clean, df_disc = run_etl_pipeline()
    print("\n--- RESUMEN DEL DATASET MAESTRO POR PRINCIPIO ACTIVO Y ACCIÓN ---")
    summary = df_clean.groupby(["principio_activo", "tipo_accion"]).agg(
        total_productos=("id_insulina_master", "count"),
        precio_min=("precio_venta_bs", "min"),
        precio_promedio=("precio_venta_bs", "mean"),
        precio_max=("precio_venta_bs", "max")
    ).round(2)
    print(summary)
