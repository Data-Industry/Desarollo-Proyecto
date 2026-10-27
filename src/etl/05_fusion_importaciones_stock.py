"""Preparación auditable de la fusión importaciones--stock para SCRUM-42.

Esta etapa consolida snapshots de retail y produce un mapeo candidato revisable.
No estima ni declara un desfase temporal estadístico: el retail disponible cubre
únicamente un día de octubre de 2026.
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd

import importlib
try:
    _mod_etl = importlib.import_module("src.etl.01_etl_insulinas")
except ImportError:
    _mod_etl = importlib.import_module("01_etl_insulinas")
identify_brand_and_lab = _mod_etl.identify_brand_and_lab
identify_pharmacology = _mod_etl.identify_pharmacology
parse_presentation = _mod_etl.parse_presentation


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

HISTORICAL_COLUMNS = [
    "snapshot_id", "archivo_origen", "timestamp", "fecha", "fecha_periodo",
    "farmacia", "id_origen", "nombre_comercial", "marca_comercial", "principio_activo",
    "marca_laboratorio", "precio_bs", "estado_stock", "stock_disponible_binario",
    "sucursal", "ciudad",
]
MAPPING_COLUMNS = [
    "descripcion_importacion_original", "descripcion_importacion_normalizada",
    "marca_importada_detectada", "marca_retail", "principio_activo_retail",
    "laboratorio_retail", "presentacion_retail", "tipo_match", "nivel_confianza",
    "cardinalidad", "requiere_revision", "observaciones",
]
IMPORT_MASTER_PATH = PROCESSED_DIR / "importaciones_insulina_bolivia.csv"
IMPORT_SUMMARY_PATH = PROCESSED_DIR / "importaciones_insulina_mensual_resumen.csv"


def _semaforo_importacion(desviacion: object) -> Tuple[int, str]:
    """Aplica la misma regla preventiva del ETL de importaciones."""
    if pd.notna(desviacion) and desviacion < -30.0:
        return 1, "ROJO"
    if pd.notna(desviacion) and desviacion <= -15.0:
        return 1, "AMARILLO"
    return 0, "VERDE"


def build_santa_cruz_import_monthly(
    import_master_path: Path = IMPORT_MASTER_PATH,
    import_summary_path: Path = IMPORT_SUMMARY_PATH,
) -> pd.DataFrame:
    """Agrega importaciones cuyo destino declarado es Santa Cruz por mes calendario.

    El resumen nacional aporta el calendario de períodos observados. Cuando el
    maestro no contiene despachos a Santa Cruz en un mes, los totales son cero
    por agregación y los costos por kilo no definidos permanecen como ``NaN``.
    """
    imports = pd.read_csv(import_master_path)
    national_summary = pd.read_csv(import_summary_path)
    periods = national_summary[["fecha_periodo"]].drop_duplicates().sort_values("fecha_periodo")
    santa_cruz = imports[imports["departamento_destino"].eq("Santa Cruz")].copy()
    aggregate = santa_cruz.groupby("fecha_periodo", as_index=False).agg(
        total_despachos=("id_importacion_master", "count"),
        total_kilos_netos=("kilos_netos", "sum"),
        total_kilos_brutos=("kilos_brutos", "sum"),
        total_valor_cif_usd=("valor_cif_usd", "sum"),
        total_valor_cif_bob=("valor_cif_bob", "sum"),
        total_viales_estimados=("viales_estimados_10ml", "sum"),
        total_ui_estimadas=("unidades_internacionales_ui_estimadas", "sum"),
    )
    monthly = periods.merge(aggregate, on="fecha_periodo", how="left")
    total_columns = [column for column in aggregate.columns if column != "fecha_periodo"]
    monthly[total_columns] = monthly[total_columns].fillna(0)
    monthly["total_despachos"] = monthly["total_despachos"].astype(int)
    monthly["costo_promedio_cif_kg_usd"] = (
        monthly["total_valor_cif_usd"] / monthly["total_kilos_netos"]
    ).where(monthly["total_kilos_netos"].ne(0)).round(2)

    previous = monthly["total_kilos_netos"].shift(1)
    monthly["tasa_variacion_mensual_pct"] = (
        (monthly["total_kilos_netos"] / previous - 1) * 100
    ).where(previous.ne(0)).round(1)
    monthly.loc[monthly.index[0], "tasa_variacion_mensual_pct"] = 0.0
    monthly["promedio_movil_3m_kg"] = (
        monthly["total_kilos_netos"].rolling(window=3, min_periods=1).mean().round(1)
    )
    deviation = (
        (monthly["total_kilos_netos"] - monthly["promedio_movil_3m_kg"])
        / monthly["promedio_movil_3m_kg"] * 100
    ).where(monthly["promedio_movil_3m_kg"].ne(0))
    alert_and_semaforo = deviation.map(_semaforo_importacion)
    monthly["alerta_quiebre_importacion_binaria"] = alert_and_semaforo.map(lambda value: value[0])
    monthly["semaforo_abastecimiento_upstream"] = alert_and_semaforo.map(lambda value: value[1])
    monthly["fuente_importacion_estado"] = "NO_VALIDADA_OFICIALMENTE"
    monthly["fuente_importacion_tipo"] = "DATASET_GENERADO_POR_ETL"
    monthly["lag_estimado_estadisticamente"] = False
    return monthly


def build_prepared_import_lags(import_monthly: pd.DataFrame) -> pd.DataFrame:
    """Construye predictores temporales; no estima un lag logístico ni óptimo."""
    prepared = import_monthly.sort_values("fecha_periodo").reset_index(drop=True).copy()
    lag_sources = {
        "total_kilos_netos": "kilos_netos",
        "total_valor_cif_usd": "valor_cif_usd",
        "total_viales_estimados": "viales_estimados",
        "total_ui_estimadas": "ui_estimadas",
    }
    for source, alias in lag_sources.items():
        for months in range(4):
            prepared[f"{alias}_lag_{months}m"] = prepared[source].shift(months)
    prepared["lag_preparado"] = True
    prepared["lag_estimado_estadisticamente"] = False
    prepared["fuente_importacion_estado"] = "NO_VALIDADA_OFICIALMENTE"
    prepared["fuente_importacion_tipo"] = "DATASET_GENERADO_POR_ETL"
    prepared["nota_lags"] = (
        "Predictores temporales preparados a partir de importaciones mensuales; "
        "no son una estimación estadística del tiempo logístico."
    )
    return prepared


def build_monthly_import_retail_fusion(
    retail_summary: pd.DataFrame,
    prepared_lags: pd.DataFrame,
) -> pd.DataFrame:
    """Enriquece solo filas retail existentes mediante una unión temporal mensual."""
    fusion = retail_summary.merge(prepared_lags, on="fecha_periodo", how="left", validate="many_to_one")
    fusion["cobertura_retail_meses"] = retail_summary["fecha_periodo"].nunique()
    fusion["suficiente_para_estimacion_lag"] = False
    fusion["lag_estimado_estadisticamente"] = False
    fusion["fuente_importacion_estado"] = "NO_VALIDADA_OFICIALMENTE"
    fusion["fuente_importacion_tipo"] = "DATASET_GENERADO_POR_ETL"
    fusion["tipo_fusion"] = "TEMPORAL_MENSUAL"
    fusion["nivel_inferencia"] = "DESCRIPTIVO"
    fusion["lag_interpretacion"] = "PREDICTORES_PREPARADOS_NO_ESTIMADOS"
    return fusion


def normalize_text(value: object) -> str:
    """Normaliza texto solo para comparación; nunca reemplaza el valor original."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("/", " ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text)).strip()


def file_content_hash(path: Path) -> str:
    """Hash SHA-256 del contenido, para deduplicar aliases y copias exactas."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_stock_status(value: object) -> Tuple[str, int]:
    """Normaliza disponibilidad categórica, sin inferir cantidades de inventario."""
    status = normalize_text(value)
    if "agotado" in status:
        return "AGOTADO", 0
    if "ultima" in status and "unidad" in status:
        return "ULTIMAS_UNIDADES", 1
    return "DISPONIBLE", 1


def discover_unique_snapshots(raw_dir: Path = RAW_DIR) -> Tuple[List[Path], List[Path]]:
    """Devuelve (archivos detectados, snapshots únicos), usando hash de contenido."""
    candidates = sorted(raw_dir.glob("insulina_precios_stock_*.csv"))
    unique: List[Path] = []
    hashes = set()
    for path in candidates:
        content_hash = file_content_hash(path)
        if content_hash not in hashes:
            hashes.add(content_hash)
            unique.append(path)
    return candidates, unique


def _prepare_snapshot(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    required = {"id_origen", "farmacia", "nombre_comercial", "timestamp"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"Snapshot inválido {path.name}; faltan columnas: {sorted(missing)}")

    records = []
    snapshot_id = f"SNAP-{file_content_hash(path)[:12]}"
    for _, row in raw.iterrows():
        timestamp = pd.to_datetime(row.get("timestamp"), utc=True, errors="coerce")
        if pd.isna(timestamp):
            raise ValueError(f"Timestamp inválido en {path.name}: {row.get('timestamp')}")
        title = str(row.get("nombre_comercial", ""))
        brand, _ = identify_brand_and_lab(title)
        principle, _, _ = identify_pharmacology(brand, title)
        stock_status, available = normalize_stock_status(row.get("estado_stock"))
        records.append({
            "snapshot_id": snapshot_id,
            "archivo_origen": path.name,
            "timestamp": timestamp.isoformat(),
            "fecha": timestamp.date().isoformat(),
            "fecha_periodo": timestamp.strftime("%Y-%m"),
            "farmacia": row.get("farmacia"),
            "id_origen": row.get("id_origen"),
            "nombre_comercial": title,
            "marca_comercial": brand,
            "principio_activo": row.get("principio_activo") or principle,
            "marca_laboratorio": row.get("marca_laboratorio"),
            "precio_bs": pd.to_numeric(row.get("precio_bs"), errors="coerce"),
            "estado_stock": stock_status,
            "stock_disponible_binario": available,
            "sucursal": row.get("sucursal"),
            "ciudad": row.get("ciudad"),
        })
    return pd.DataFrame(records, columns=HISTORICAL_COLUMNS)


def build_retail_history(raw_dir: Path = RAW_DIR) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Consolida todos los snapshots no duplicados y conserva su archivo de origen."""
    detected, unique = discover_unique_snapshots(raw_dir)
    if not unique:
        raise FileNotFoundError(f"No se encontraron snapshots en {raw_dir}")
    history = pd.concat([_prepare_snapshot(path) for path in unique], ignore_index=True)
    history.sort_values(["timestamp", "farmacia", "id_origen"], inplace=True)
    history.reset_index(drop=True, inplace=True)
    return history, {"snapshots_detectados": len(detected), "snapshots_unicos": len(unique)}


def build_monthly_retail_summary(history: pd.DataFrame) -> pd.DataFrame:
    """Resume disponibilidad categórica; no convierte observaciones en stock cuantitativo.

    ``productos_stock_normal``, ``productos_ultimas_unidades`` y
    ``productos_agotados`` son categorías mutuamente excluyentes. En cambio,
    ``productos_disponibles`` es una métrica de disponibilidad efectiva: suma
    stock normal y últimas unidades, pues ambos estados indican que el producto
    todavía puede adquirirse.
    """
    group_columns = ["fecha_periodo", "farmacia", "principio_activo"]
    if "marca_comercial" in history.columns and history["marca_comercial"].notna().any():
        group_columns.append("marca_comercial")
    summary = history.groupby(group_columns, dropna=False).agg(
        # Cada fila es una observación de producto dentro de un snapshot. No se
        # deduplica entre snapshots, porque la disponibilidad puede cambiar.
        productos_observados=("id_origen", "size"),
        productos_stock_normal=("estado_stock", lambda s: int((s == "DISPONIBLE").sum())),
        productos_agotados=("estado_stock", lambda s: int((s == "AGOTADO").sum())),
        productos_ultimas_unidades=("estado_stock", lambda s: int((s == "ULTIMAS_UNIDADES").sum())),
    ).reset_index()
    summary["productos_disponibles"] = (
        summary["productos_stock_normal"] + summary["productos_ultimas_unidades"]
    )
    summary["tasa_disponibilidad"] = (
        summary["productos_disponibles"] / summary["productos_observados"]
    ).round(4)
    return summary.sort_values(group_columns).reset_index(drop=True)


def _retail_catalog(history: pd.DataFrame) -> pd.DataFrame:
    catalog_rows = []
    for title in history["nombre_comercial"].dropna().unique():
        brand, lab = identify_brand_and_lab(title)
        if brand == "Insulina Genérica":
            continue
        principle, _, _ = identify_pharmacology(brand, title)
        _, _, presentation = parse_presentation(title)
        catalog_rows.append({
            "marca_retail": brand,
            "principio_activo_retail": principle,
            "laboratorio_retail": lab,
            "presentacion_retail": presentation,
        })
    return pd.DataFrame(catalog_rows).drop_duplicates().sort_values(
        ["marca_retail", "principio_activo_retail", "presentacion_retail"]
    )


def build_import_retail_mapping(
    history: pd.DataFrame,
    import_path: Path = PROCESSED_DIR / "importaciones_insulina_bolivia.csv",
) -> pd.DataFrame:
    """Crea candidatos transparentes por marcas explícitas, sin unión fuzzy automática."""
    imports = pd.read_csv(import_path)
    catalog = _retail_catalog(history)
    mapping_rows = []
    for description in sorted(imports["descripcion_comercial"].dropna().unique()):
        normalized = normalize_text(description)
        matches = catalog[catalog["marca_retail"].map(lambda brand: normalize_text(brand) in normalized)]
        detected_brands = matches["marca_retail"].unique().tolist()
        if matches.empty:
            mapping_rows.append({
                "descripcion_importacion_original": description,
                "descripcion_importacion_normalizada": normalized,
                "marca_importada_detectada": "",
                "marca_retail": "",
                "principio_activo_retail": "",
                "laboratorio_retail": "",
                "presentacion_retail": "",
                "tipo_match": "NO_MAPEABLE",
                "nivel_confianza": "BAJA",
                "cardinalidad": "SIN_CORRESPONDENCIA",
                "requiere_revision": True,
                "observaciones": "No hay marca retail canónica explícita en la descripción de importación.",
            })
            continue

        cardinality = "MUCHOS_A_MUCHOS" if len(detected_brands) > 1 else (
            "UNO_A_MUCHOS" if len(matches) > 1 else "UNO_A_UNO"
        )
        for _, retail in matches.iterrows():
            mapping_rows.append({
                "descripcion_importacion_original": description,
                "descripcion_importacion_normalizada": normalized,
                "marca_importada_detectada": retail["marca_retail"],
                "marca_retail": retail["marca_retail"],
                "principio_activo_retail": retail["principio_activo_retail"],
                "laboratorio_retail": retail["laboratorio_retail"],
                "presentacion_retail": retail["presentacion_retail"],
                "tipo_match": "DIRECTO",
                "nivel_confianza": "ALTA" if cardinality == "UNO_A_UNO" else "MEDIA",
                "cardinalidad": cardinality,
                "requiere_revision": cardinality != "UNO_A_UNO",
                "observaciones": (
                    "Marca explícita; la descripción contiene varias marcas o presentaciones y no "
                    "autoriza una unión final sin revisión." if cardinality != "UNO_A_UNO"
                    else "Marca explícita identificada en ambas fuentes; validar presentación si se usará para fusión."
                ),
            })
    return pd.DataFrame(mapping_rows, columns=MAPPING_COLUMNS)


def run_pipeline() -> Dict[str, object]:
    """Genera los artefactos preparatorios de SCRUM-42, sin estimar lags."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    history, snapshot_metrics = build_retail_history()
    summary = build_monthly_retail_summary(history)
    mapping = build_import_retail_mapping(history)
    santa_cruz_imports = build_santa_cruz_import_monthly()
    prepared_lags = build_prepared_import_lags(santa_cruz_imports)
    fusion = build_monthly_import_retail_fusion(summary, prepared_lags)

    history.to_csv(PROCESSED_DIR / "retail_stock_historico_consolidado.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(PROCESSED_DIR / "retail_stock_mensual_resumen.csv", index=False, encoding="utf-8-sig")
    mapping.to_csv(PROCESSED_DIR / "mapeo_productos_importacion_retail.csv", index=False, encoding="utf-8-sig")
    santa_cruz_imports.to_csv(PROCESSED_DIR / "importaciones_santa_cruz_mensual.csv", index=False, encoding="utf-8-sig")
    prepared_lags.to_csv(PROCESSED_DIR / "importaciones_stock_lags_preparados.csv", index=False, encoding="utf-8-sig")
    fusion.to_csv(PROCESSED_DIR / "importaciones_stock_fusion_mensual.csv", index=False, encoding="utf-8-sig")

    confidence_counts = mapping["nivel_confianza"].value_counts().to_dict()
    return {
        **snapshot_metrics,
        "registros_consolidados": len(history),
        "periodos_retail": sorted(history["fecha_periodo"].unique().tolist()),
        "resumen_mensual": summary,
        "correspondencias_confianza": confidence_counts,
        "mapeo": mapping,
        "importaciones_santa_cruz": santa_cruz_imports,
        "lags_preparados": prepared_lags,
        "fusion_mensual": fusion,
    }


if __name__ == "__main__":
    results = run_pipeline()
    print(f"Snapshots detectados: {results['snapshots_detectados']}")
    print(f"Snapshots únicos: {results['snapshots_unicos']}")
    print(f"Registros consolidados: {results['registros_consolidados']}")
    print(f"Períodos retail: {results['periodos_retail']}")
    print(f"Importaciones Santa Cruz: {len(results['importaciones_santa_cruz'])} períodos")
    print(f"Fusión mensual: {len(results['fusion_mensual'])} filas")
    print("No se calculó ningún lag estadístico.")
