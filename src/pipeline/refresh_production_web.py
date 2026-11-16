"""Refresh transaccional de datos frescos para la web pública (SCRUM-52 / US-37).

Este módulo no ejecuta scraping ni reentrena modelos. Selecciona un snapshot
local, valida sus datos, aplica el modelo de producción existente, prepara el
HTML y su manifest en staging y publica únicamente si todos los gates pasan.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import joblib
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
MODEL_PATH = PROJECT_DIR / "models" / "modelo_produccion_stock.joblib"
MODEL_METADATA_PATH = PROJECT_DIR / "models" / "modelo_metadata.json"
BCB_PATH = PROCESSED_DIR / "tipo_cambio_diario_bcb.csv"
BRANCHES_PATH = PROCESSED_DIR / "farmacias_geolocalizadas.csv"
ROOT_HTML = PROJECT_DIR / "mvp_comparador_jubilados.html"
UI_HTML = PROJECT_DIR / "src" / "ui" / "mvp_comparador_jubilados.html"
MANIFEST_PATH = PROCESSED_DIR / "web_bundle_manifest.json"

ALLOWED_PHARMACIES = {"Farmacorp", "Farmacias Chávez", "Farmacias Telchi"}
ALLOWED_STOCK_STATES = {"DISPONIBLE", "ULTIMAS_UNIDADES", "AGOTADO", "NO_VERIFICADO"}
ALLOWED_STOCK_EVIDENCE = {"SOURCE_REPORTED", "CATALOG_ONLY", "UNKNOWN"}
ALLOWED_RISK_STATES = {"VERDE_ESTABLE", "AMARILLO_RIESGO_MODERADO", "ROJO_ALTO_RIESGO"}
ALLOWED_BRANCH_STATES = {"ASIGNADO", "SIN_EVIDENCIA", "AMBIGUO_EN_BORDE"}

BCB_WARNING_DAYS = 3
BCB_ERROR_DAYS = 7
RETAIL_WARNING_HOURS = 24
RETAIL_ERROR_HOURS = 72
BUNDLE_SCHEMA_VERSION = 1
TARGET_TYPE = "CURRENT_STOCK_PROXY"

REQUIRED_SNAPSHOT_COLUMNS = {
    "id_origen", "farmacia", "nombre_comercial", "precio_bs",
    "precio_regular_bs", "estado_stock", "url_producto", "timestamp",
}


class InputValidationError(RuntimeError):
    """Input inexistente, antiguo o inconsistente (exit code 2)."""


class ProcessingError(RuntimeError):
    """Fallo preparando features o ejecutando el modelo (exit code 3)."""


class IntegrityError(RuntimeError):
    """El bundle candidato no superó sus gates (exit code 4)."""


class PublicationError(RuntimeError):
    """Falló la sustitución transaccional de producción (exit code 5)."""


@dataclass
class SnapshotSelection:
    path: Path
    sha256: str
    extracted_at: datetime


@dataclass
class RefreshPaths:
    raw_dir: Path = RAW_DIR
    bcb_path: Path = BCB_PATH
    branches_path: Path = BRANCHES_PATH
    model_path: Path = MODEL_PATH
    model_metadata_path: Path = MODEL_METADATA_PATH
    root_html: Path = ROOT_HTML
    ui_html: Path = UI_HTML
    manifest_path: Path = MANIFEST_PATH


class Reporter:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def ok(self, message: str) -> None:
        print(f"[OK] {message}")

    def warning(self, message: str) -> None:
        print(f"[WARNING] {message}")

    def error(self, message: str) -> None:
        print(f"[ERROR] {message}")

    def detail(self, message: str) -> None:
        if self.verbose:
            print(f"[DETAIL] {message}")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _parse_timestamp(value: object, field: str) -> datetime:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        raise InputValidationError(f"INVALID_TIMESTAMP: {field} contiene una fecha inválida: {value!r}")
    return parsed.to_pydatetime()


def snapshot_extraction_time(path: Path) -> datetime:
    """Obtiene la fecha real del contenido; usa el nombre solo como respaldo."""
    try:
        timestamps = pd.read_csv(path, usecols=["timestamp"])["timestamp"]
        parsed = pd.to_datetime(timestamps, utc=True, errors="coerce").dropna()
        if not parsed.empty:
            return parsed.max().to_pydatetime()
    except (ValueError, OSError, pd.errors.ParserError):
        pass

    match = re.search(r"(\d{8})_(\d{6})", path.stem)
    if match:
        return datetime.strptime("".join(match.groups()), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    raise InputValidationError(f"INVALID_TIMESTAMP: no se pudo fechar el snapshot {path}")


def resolve_snapshot(raw_dir: Path = RAW_DIR, explicit_input: Optional[Path] = None) -> SnapshotSelection:
    if explicit_input is not None:
        path = explicit_input.expanduser().resolve()
        if not path.is_file():
            raise InputValidationError(f"INPUT_NOT_FOUND: no existe el snapshot solicitado: {path}")
        return SnapshotSelection(path, sha256_file(path), snapshot_extraction_time(path))

    candidates = set(raw_dir.glob("insulina_precios_stock_20??????_??????.csv"))
    latest = raw_dir / "insulina_precios_stock_latest.csv"
    if latest.is_file():
        candidates.add(latest)
    if not candidates:
        raise InputValidationError(f"INPUT_NOT_FOUND: no se encontraron snapshots en {raw_dir}")

    selections: List[SnapshotSelection] = []
    errors: List[str] = []
    for path in sorted(candidates):
        try:
            selections.append(SnapshotSelection(path, sha256_file(path), snapshot_extraction_time(path)))
        except InputValidationError as exc:
            errors.append(str(exc))
    if not selections:
        raise InputValidationError("INPUT_NOT_FOUND: ningún snapshot tiene una fecha válida. " + "; ".join(errors))
    return max(
        selections,
        key=lambda item: (
            item.extracted_at,
            item.path.name != "insulina_precios_stock_latest.csv",
            item.path.name,
        ),
    )


def _normalise_stock(raw_state: object, pharmacy: str) -> Tuple[str, str, Optional[str]]:
    text = str(raw_state or "").strip().casefold()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

    if pharmacy == "Farmacias Telchi":
        return "NO_VERIFICADO", "CATALOG_ONLY", "STOCK_UNVERIFIED"
    if text == "disponible":
        return "DISPONIBLE", "SOURCE_REPORTED", None
    if text in {"ultimas unidades", "ultima unidad", "ultimas_unidades"}:
        return "ULTIMAS_UNIDADES", "SOURCE_REPORTED", None
    if text == "agotado":
        return "AGOTADO", "SOURCE_REPORTED", None
    if text in {"no_verificado", "no verificado", "desconocido", "unknown", ""}:
        return "NO_VERIFICADO", "UNKNOWN", "STOCK_UNVERIFIED"
    return "NO_VERIFICADO", "UNKNOWN", "STOCK_UNVERIFIED"


def _valid_url(value: object) -> bool:
    text = str(value or "").strip()
    parsed = urlparse(text)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_snapshot(
    selection: SnapshotSelection,
    now: Optional[datetime] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    now = now or utc_now()
    try:
        raw = pd.read_csv(selection.path)
    except Exception as exc:
        raise InputValidationError(f"INVALID_SNAPSHOT: no se pudo leer {selection.path}: {exc}") from exc
    if raw.empty:
        raise InputValidationError("EMPTY_SNAPSHOT: el snapshot no contiene registros")

    missing = REQUIRED_SNAPSHOT_COLUMNS.difference(raw.columns)
    if missing:
        raise InputValidationError(f"INVALID_SCHEMA: faltan columnas: {sorted(missing)}")

    warnings: List[str] = []
    duplicate_mask = raw.duplicated(keep="first")
    if duplicate_mask.any():
        warnings.append(f"EXACT_DUPLICATES: se deduplicaron {int(duplicate_mask.sum())} filas exactas")
        raw = raw.loc[~duplicate_mask].copy()

    duplicate_keys = raw.duplicated(["farmacia", "id_origen"], keep=False)
    if duplicate_keys.any():
        keys = raw.loc[duplicate_keys, ["farmacia", "id_origen"]].drop_duplicates().to_dict("records")
        raise InputValidationError(f"CONFLICTING_DUPLICATE: producto/farmacia con valores incompatibles: {keys}")

    current = pd.to_numeric(raw["precio_bs"], errors="coerce")
    invalid_current = current.isna() | ~np.isfinite(current) | current.le(0)
    if invalid_current.any():
        rows = raw.index[invalid_current].tolist()
        raise InputValidationError(f"INVALID_PRICE: precio actual nulo, no finito o <= 0 en filas {rows}")

    regular_text = raw["precio_regular_bs"].astype("string")
    has_regular = regular_text.notna() & regular_text.str.strip().ne("")
    regular = pd.to_numeric(raw["precio_regular_bs"], errors="coerce")
    invalid_regular = has_regular & (regular.isna() | ~np.isfinite(regular) | regular.lt(current))
    if invalid_regular.any():
        rows = raw.index[invalid_regular].tolist()
        raise InputValidationError(f"INVALID_REGULAR_PRICE: precio regular inválido o menor al actual en filas {rows}")

    unknown_pharmacies = sorted(set(raw["farmacia"].dropna().astype(str)) - ALLOWED_PHARMACIES)
    if unknown_pharmacies or raw["farmacia"].isna().any():
        raise InputValidationError(f"UNKNOWN_PHARMACY: {unknown_pharmacies or ['valor nulo']}")

    invalid_urls = ~raw["url_producto"].map(_valid_url)
    if invalid_urls.any():
        raise InputValidationError(f"INVALID_URL: URL vacía o inválida en filas {raw.index[invalid_urls].tolist()}")

    timestamps = raw["timestamp"].map(
        lambda value: pd.to_datetime(value, utc=True, errors="coerce")
    )
    if timestamps.isna().any():
        raise InputValidationError(f"INVALID_TIMESTAMP: filas {raw.index[timestamps.isna()].tolist()}")
    if (timestamps > pd.Timestamp(now) + pd.Timedelta(minutes=5)).any():
        raise InputValidationError("INVALID_TIMESTAMP: el snapshot contiene fechas futuras")

    age_hours = (now - selection.extracted_at).total_seconds() / 3600
    if age_hours > RETAIL_ERROR_HOURS:
        raise InputValidationError(
            f"RETAIL_STALE: última extracción {selection.extracted_at.isoformat()}; antigüedad {age_hours:.1f} horas"
        )
    if age_hours > RETAIL_WARNING_HOURS:
        warnings.append(f"RETAIL_STALE_WARNING: antigüedad {age_hours:.1f} horas")

    raw = raw.copy()
    raw["precio_bs"] = current.astype(float)
    raw["precio_regular_bs"] = regular.where(has_regular, np.nan)
    stocks = [_normalise_stock(row.estado_stock, str(row.farmacia)) for row in raw.itertuples()]
    raw["stock_actual"] = [item[0] for item in stocks]
    raw["stock_evidence"] = [item[1] for item in stocks]
    for pharmacy, warning in zip(raw["farmacia"], [item[2] for item in stocks]):
        if warning:
            message = f"{warning}: {pharmacy} aparece en catálogo sin confirmación de inventario"
            if message not in warnings:
                warnings.append(message)

    if not set(raw["stock_actual"]).issubset(ALLOWED_STOCK_STATES):
        raise InputValidationError("INVALID_STOCK: estado normalizado fuera del catálogo")
    if not set(raw["stock_evidence"]).issubset(ALLOWED_STOCK_EVIDENCE):
        raise InputValidationError("INVALID_STOCK_EVIDENCE: evidencia fuera del catálogo")
    return raw.sort_values(["farmacia", "id_origen"], kind="stable").reset_index(drop=True), warnings


def _etl_helpers() -> Tuple[Any, Any, Any]:
    module = importlib.import_module("src.etl.01_etl_insulinas")
    return module.identify_brand_and_lab, module.identify_pharmacology, module.parse_presentation


def prepare_products(raw: pd.DataFrame) -> pd.DataFrame:
    """Reconstruye solo las features ya definidas por el ETL, sin escribir archivos."""
    identify_brand_and_lab, identify_pharmacology, parse_presentation = _etl_helpers()
    records: List[Dict[str, Any]] = []
    excluded_non_insulin = ("denosumab", "densimab", "resyniv", "acido hialur", "hialuronico", "ibesia")
    disposable = ("jeringa", "aguja", "toallita", "panal", "pañal")

    for row in raw.itertuples(index=False):
        title = str(row.nombre_comercial).strip()
        lowered = title.casefold()
        if any(term in lowered for term in excluded_non_insulin):
            continue
        if float(row.precio_bs) < 15 or any(term in lowered for term in disposable):
            continue

        if pd.isna(row.precio_regular_bs):
            raise ProcessingError(f"MISSING_MODEL_FEATURE: precio_regular_bs requerido por el modelo para {row.id_origen}")
        brand, lab = identify_brand_and_lab(title)
        principle, action, origin = identify_pharmacology(brand, title)
        volume, concentration, presentation = parse_presentation(title)
        total_units = int(volume * concentration)
        sale = float(row.precio_bs)
        regular = float(row.precio_regular_bs)
        discount = round(((regular - sale) / regular) * 100, 1) if regular > sale else 0.0
        stable_id = "WEB-" + hashlib.sha256(f"{row.farmacia}|{row.id_origen}".encode("utf-8")).hexdigest()[:16]
        records.append({
            "id_insulina_master": stable_id,
            "id_origen": str(row.id_origen),
            "farmacia": str(row.farmacia),
            "marca_comercial": brand,
            "principio_activo": principle,
            "tipo_accion": action,
            "origen_biologico": origin,
            "laboratorio_fabricante": lab,
            "formato_presentacion": presentation,
            "volumen_ml": float(volume),
            "concentracion_ui_ml": int(concentration),
            "unidades_totales_ui": total_units,
            "precio_venta_bs": sale,
            "precio_lista_bs": regular,
            "descuento_porcentaje": discount,
            "precio_por_ml_bs": round(sale / volume, 2),
            "precio_por_100ui_bs": round(sale / (total_units / 100), 2),
            "stock_actual": str(row.stock_actual),
            "stock_evidence": str(row.stock_evidence),
            "url_producto": str(row.url_producto),
            "timestamp_extraccion": pd.to_datetime(row.timestamp, utc=True).isoformat(),
        })
    if not records:
        raise ProcessingError("NO_VALID_PRODUCTS: no quedó al menos una insulina válida")
    return pd.DataFrame(records).sort_values(["farmacia", "id_origen"], kind="stable").reset_index(drop=True)


def load_model_metadata(path: Path) -> Dict[str, Any]:
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProcessingError(f"INVALID_MODEL_METADATA: {exc}") from exc
    threshold = metadata.get("umbral_clinico_produccion")
    if not isinstance(threshold, (int, float)) or not math.isfinite(float(threshold)) or not 0 < float(threshold) < 1:
        raise ProcessingError("INVALID_MODEL_METADATA: umbral_clinico_produccion inválido")
    numeric = metadata.get("caracteristicas_numericas")
    categorical = metadata.get("caracteristicas_categoricas")
    if not isinstance(numeric, list) or not isinstance(categorical, list):
        raise ProcessingError("INVALID_MODEL_METADATA: faltan listas de características")
    return metadata


def validate_prediction_frame(predictions: pd.DataFrame, expected_ids: Sequence[str], threshold: float) -> None:
    required = {"id_insulina_master", "probabilidad_riesgo", "riesgo_predictivo", "model_threshold"}
    missing = required.difference(predictions.columns)
    if missing:
        raise ProcessingError(f"PREDICTION_MISSING: faltan columnas {sorted(missing)}")
    if predictions["id_insulina_master"].duplicated().any():
        raise ProcessingError("PREDICTION_DUPLICATE: existe más de una predicción por ID")
    if set(predictions["id_insulina_master"]) != set(expected_ids):
        raise ProcessingError("PREDICTION_MISSING: las predicciones no corresponden exactamente a los productos")
    probability = pd.to_numeric(predictions["probabilidad_riesgo"], errors="coerce")
    if probability.isna().any() or not probability.between(0, 1).all():
        raise ProcessingError("INVALID_PROBABILITY: la probabilidad debe estar entre 0 y 1")
    if not set(predictions["riesgo_predictivo"]).issubset(ALLOWED_RISK_STATES):
        raise ProcessingError("INVALID_RISK_STATE: semáforo fuera del catálogo")
    thresholds = pd.to_numeric(predictions["model_threshold"], errors="coerce")
    if thresholds.isna().any() or not np.allclose(thresholds, float(threshold), rtol=0, atol=1e-12):
        raise ProcessingError("THRESHOLD_MISMATCH: el umbral no coincide con modelo_metadata.json")


def run_model_inference(
    products: pd.DataFrame,
    model_path: Path,
    metadata_path: Path,
) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
    if not model_path.is_file():
        raise ProcessingError(f"MODEL_NOT_FOUND: {model_path}")
    metadata = load_model_metadata(metadata_path)
    features = metadata["caracteristicas_numericas"] + metadata["caracteristicas_categoricas"]
    missing = [feature for feature in features if feature not in products.columns]
    if missing:
        raise ProcessingError(f"MISSING_MODEL_FEATURE: {missing}")
    try:
        model = joblib.load(model_path)
        probabilities = np.asarray(model.predict_proba(products[features]))[:, 1]
    except Exception as exc:
        raise ProcessingError(f"MODEL_INFERENCE_FAILED: {exc}") from exc
    if len(probabilities) != len(products):
        raise ProcessingError("PREDICTION_MISSING: el modelo no devolvió una predicción por producto")

    threshold = float(metadata["umbral_clinico_produccion"])
    risk = np.select(
        [probabilities >= threshold, probabilities >= threshold * 0.6],
        ["ROJO_ALTO_RIESGO", "AMARILLO_RIESGO_MODERADO"],
        default="VERDE_ESTABLE",
    )
    predictions = pd.DataFrame({
        "id_insulina_master": products["id_insulina_master"],
        "probabilidad_riesgo": probabilities.astype(float),
        "riesgo_predictivo": risk,
        "model_threshold": threshold,
    })
    validate_prediction_frame(predictions, products["id_insulina_master"].tolist(), threshold)
    merged = products.merge(predictions, on="id_insulina_master", how="left", validate="one_to_one")
    return merged, metadata, sha256_file(model_path)


def validate_bcb(path: Path, now: Optional[datetime] = None) -> Tuple[Dict[str, Any], List[str]]:
    now = now or utc_now()
    if not path.is_file():
        raise InputValidationError(f"BCB_NOT_FOUND: {path}")
    try:
        data = pd.read_csv(path)
    except Exception as exc:
        raise InputValidationError(f"BCB_INVALID: no se pudo leer la cotización: {exc}") from exc
    required = {"fecha_iso", "tipo_cambio_oficial_bob_usd", "fuente_oficial"}
    missing = required.difference(data.columns)
    if data.empty or missing:
        raise InputValidationError(f"BCB_INVALID: dataset vacío o faltan columnas {sorted(missing)}")
    dates = pd.to_datetime(data["fecha_iso"], utc=True, errors="coerce")
    if dates.isna().any():
        raise InputValidationError("BCB_INVALID_DATE: existe una fecha inválida")
    latest_index = dates.idxmax()
    latest_date = dates.loc[latest_index].to_pydatetime()
    if latest_date > now + pd.Timedelta(minutes=5):
        raise InputValidationError("BCB_FUTURE_DATE: la cotización tiene fecha futura")
    value = pd.to_numeric(pd.Series([data.loc[latest_index, "tipo_cambio_oficial_bob_usd"]]), errors="coerce").iloc[0]
    if pd.isna(value) or not math.isfinite(float(value)) or float(value) <= 0:
        raise InputValidationError("BCB_INVALID_VALUE: la cotización debe ser numérica, finita y positiva")
    source = str(data.loc[latest_index, "fuente_oficial"] or "").strip()
    if not source:
        raise InputValidationError("BCB_SOURCE_MISSING: la fuente no está identificada")
    age_days = (now.date() - latest_date.date()).days
    if age_days > BCB_ERROR_DAYS:
        raise InputValidationError(
            f"BCB_STALE: última cotización {latest_date.date().isoformat()}; antigüedad {age_days} días"
        )
    warnings: List[str] = []
    if age_days > BCB_WARNING_DAYS:
        warnings.append(f"BCB_STALE_WARNING: antigüedad {age_days} días")
    return {
        "value": float(value),
        "date": latest_date.date().isoformat(),
        "source": source,
        "direction": "BOB_PER_USD",
        "sha256": sha256_file(path),
    }, warnings


def prepare_branches(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise InputValidationError(f"BRANCHES_NOT_FOUND: {path}")
    data = pd.read_csv(path)
    required = {"farmacia", "id_sucursal", "nombre_sucursal", "direccion", "ciudad", "anillo_asignado", "estado_anillo"}
    missing = required.difference(data.columns)
    if data.empty or missing:
        raise InputValidationError(f"BRANCHES_INVALID: dataset vacío o faltan columnas {sorted(missing)}")
    if not set(data["estado_anillo"]).issubset(ALLOWED_BRANCH_STATES):
        raise InputValidationError("BRANCHES_INVALID: estado_anillo fuera del catálogo")
    invalid_unassigned = data["estado_anillo"].isin({"SIN_EVIDENCIA", "AMBIGUO_EN_BORDE"}) & data["anillo_asignado"].notna()
    if invalid_unassigned.any():
        raise InputValidationError("BRANCHES_INVALID: un registro sin evidencia o ambiguo tiene anillo asignado")
    assigned = data["estado_anillo"].eq("ASIGNADO")
    numeric_anillo = pd.to_numeric(data["anillo_asignado"], errors="coerce")
    if (assigned & (~numeric_anillo.between(1, 8))).any():
        raise InputValidationError("BRANCHES_INVALID: anillo asignado fuera de 1..8")
    result = data.copy()
    result["anillo_asignado"] = numeric_anillo.where(assigned, np.nan)
    return result.sort_values(["farmacia", "id_sucursal"], kind="stable").reset_index(drop=True)


def risk_stock_warnings(products: pd.DataFrame) -> List[str]:
    disagreement = products["stock_actual"].eq("DISPONIBLE") & products["riesgo_predictivo"].eq("ROJO_ALTO_RIESGO")
    warnings: List[str] = []
    if disagreement.any():
        warnings.append(f"RISK_STOCK_DISAGREEMENT: {int(disagreement.sum())} registros con stock disponible y riesgo rojo")
    if products["riesgo_predictivo"].nunique() == 1:
        warnings.append(f"SINGLE_RISK_CLASS: todos los registros tienen {products['riesgo_predictivo'].iloc[0]}")
    return warnings


def _git_version(project_dir: Path) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=project_dir,
            check=True, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def calculate_input_fingerprint(
    selection: SnapshotSelection,
    bcb: Dict[str, Any],
    branches_path: Path,
    model_hash: str,
    model_metadata_path: Path,
) -> str:
    pipeline_source = Path(__file__)
    ui_source = PROJECT_DIR / "src" / "ui" / "generar_mvp_interactivo.py"
    payload = {
        "snapshot": selection.sha256,
        "bcb": bcb["sha256"],
        "branches": sha256_file(branches_path),
        "model": model_hash,
        "model_metadata": sha256_file(model_metadata_path),
        "pipeline_source": sha256_file(pipeline_source),
        "ui_source": sha256_file(ui_source),
        "configuration": {
            "bcb_warning_days": BCB_WARNING_DAYS,
            "bcb_error_days": BCB_ERROR_DAYS,
            "retail_warning_hours": RETAIL_WARNING_HOURS,
            "retail_error_hours": RETAIL_ERROR_HOURS,
            "schema": BUNDLE_SCHEMA_VERSION,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(canonical)


def _load_existing_manifest(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_manifest(
    selection: SnapshotSelection,
    products: pd.DataFrame,
    branches: pd.DataFrame,
    bcb: Dict[str, Any],
    model_metadata: Dict[str, Any],
    model_hash: str,
    warnings: Sequence[str],
    fingerprint: str,
    generated_at: datetime,
) -> Dict[str, Any]:
    manifest: Dict[str, Any] = {
        "generated_at": generated_at.astimezone(timezone.utc).isoformat(),
        "data_as_of": selection.extracted_at.astimezone(timezone.utc).isoformat(),
        "source_snapshot": {"filename": selection.path.name, "sha256": selection.sha256},
        "model": {
            "name": str(model_metadata.get("modelo_produccion", "Unknown")),
            "sha256": model_hash,
            "threshold": float(model_metadata["umbral_clinico_produccion"]),
            "target_type": TARGET_TYPE,
        },
        "currency": "BOB",
        "currency_direction": bcb["direction"],
        "currency_date": bcb["date"],
        "currency_source": bcb["source"],
        "product_count": int(len(products)),
        "pharmacy_chain_count": int(products["farmacia"].nunique()),
        "branch_count": int(len(branches)),
        "warnings": sorted(set(warnings)),
        "bundle_schema_version": BUNDLE_SCHEMA_VERSION,
        "input_fingerprint": fingerprint,
    }
    version = _git_version(PROJECT_DIR)
    if version:
        manifest["pipeline_version"] = version
    return manifest


def deterministic_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build_candidate_html(
    products: pd.DataFrame,
    branches: pd.DataFrame,
    manifest: Dict[str, Any],
) -> str:
    module = importlib.import_module("src.ui.generar_mvp_interactivo")
    medications, branch_records, summary = module.compilar_datos_reales(
        df_master=products,
        df_preds=products[["id_insulina_master", "probabilidad_riesgo", "riesgo_predictivo"]],
        df_geo=branches,
        metadata=manifest,
    )
    return module.construir_html_mvp(medications, branch_records, summary, metadata=manifest)


def validate_manifest(manifest: Dict[str, Any]) -> None:
    required = {
        "generated_at", "data_as_of", "source_snapshot", "model", "currency",
        "currency_date", "product_count", "pharmacy_chain_count", "branch_count",
        "warnings", "bundle_schema_version", "input_fingerprint",
    }
    missing = required.difference(manifest)
    if missing:
        raise IntegrityError(f"MANIFEST_INVALID: faltan campos {sorted(missing)}")
    if manifest["currency"] != "BOB" or manifest.get("currency_direction") != "BOB_PER_USD":
        raise IntegrityError("MANIFEST_INVALID: moneda o dirección incorrecta")
    if manifest["product_count"] < 1 or manifest["bundle_schema_version"] != 1:
        raise IntegrityError("MANIFEST_INVALID: conteo o versión inválidos")


def validate_candidate_html(html: str, manifest: Dict[str, Any]) -> None:
    if not html.strip() or len(html.encode("utf-8")) < 1000:
        raise IntegrityError("BUNDLE_EMPTY: el HTML candidato está vacío o incompleto")
    required_fragments = [
        "const DATA_MEDICAMENTOS =", "const DATA_SUCURSALES =", "const DATA_METADATA =",
        manifest["input_fingerprint"], manifest["source_snapshot"]["filename"],
        "stock_actual", "stock_evidence", "riesgo_predictivo", "probabilidad_riesgo",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in html]
    if missing:
        raise IntegrityError(f"BUNDLE_INVALID: faltan elementos {missing}")
    critical_patterns = [r"\bTODO\b", r"\bPLACEHOLDER\b", r"__BUNDLE_[A-Z_]+__", r"\bNaN\b"]
    for pattern in critical_patterns:
        if re.search(pattern, html):
            raise IntegrityError(f"UNRESOLVED_PLACEHOLDER: {pattern}")


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(content)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _restore(path: Path, previous: Optional[bytes]) -> None:
    if previous is None:
        if path.exists():
            path.unlink()
    else:
        _atomic_write(path, previous)


def publish_bundle(html: str, manifest_text: str, paths: RefreshPaths) -> None:
    previous_ui = paths.ui_html.read_bytes() if paths.ui_html.exists() else None
    previous_manifest = paths.manifest_path.read_bytes() if paths.manifest_path.exists() else None
    try:
        _atomic_write(paths.ui_html, html.encode("utf-8"))
        _atomic_write(paths.manifest_path, manifest_text.encode("utf-8"))
        # Artefacto público canónico: siempre se reemplaza al final.
        _atomic_write(paths.root_html, html.encode("utf-8"))
    except Exception as exc:
        try:
            _restore(paths.ui_html, previous_ui)
            _restore(paths.manifest_path, previous_manifest)
        except Exception as rollback_exc:
            raise PublicationError(f"PUBLISH_FAILED: {exc}; ROLLBACK_FAILED: {rollback_exc}") from exc
        raise PublicationError(f"PUBLISH_FAILED: {exc}") from exc


def run_refresh(
    paths: Optional[RefreshPaths] = None,
    explicit_input: Optional[Path] = None,
    dry_run: bool = False,
    verbose: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    paths = paths or RefreshPaths()
    now = now or utc_now()
    reporter = Reporter(verbose)

    selection = resolve_snapshot(paths.raw_dir, explicit_input)
    reporter.ok(f"Snapshot encontrado: {selection.path.name}")
    reporter.ok(f"Snapshot SHA-256: {selection.sha256}")
    reporter.ok(f"Fecha real de extracción: {selection.extracted_at.isoformat()}")

    raw, warnings = validate_snapshot(selection, now=now)
    products = prepare_products(raw)
    reporter.ok(f"{len(products)} productos válidos")

    bcb, bcb_warnings = validate_bcb(paths.bcb_path, now=now)
    warnings.extend(bcb_warnings)
    reporter.ok(f"Cotización BCB válida: {bcb['date']} ({bcb['direction']})")

    branches = prepare_branches(paths.branches_path)
    reporter.ok(f"{len(branches)} sucursales validadas sin inferir anillos")

    products, model_metadata, model_hash = run_model_inference(
        products, paths.model_path, paths.model_metadata_path
    )
    warnings.extend(risk_stock_warnings(products))
    for warning in sorted(set(warnings)):
        reporter.warning(warning)

    fingerprint = calculate_input_fingerprint(
        selection, bcb, paths.branches_path, model_hash, paths.model_metadata_path
    )
    existing = _load_existing_manifest(paths.manifest_path)
    same_inputs = bool(existing and existing.get("input_fingerprint") == fingerprint)
    generated_at = (
        _parse_timestamp(existing["generated_at"], "generated_at")
        if same_inputs and existing and existing.get("generated_at")
        else now
    )
    manifest = build_manifest(
        selection, products, branches, bcb, model_metadata, model_hash,
        warnings, fingerprint, generated_at,
    )

    with tempfile.TemporaryDirectory(prefix="web-refresh-", dir=PROJECT_DIR) as staging_name:
        staging = Path(staging_name)
        html = build_candidate_html(products, branches, manifest)
        manifest_text = deterministic_json(manifest)
        candidate_html = staging / "mvp_comparador_jubilados.html"
        candidate_manifest = staging / "web_bundle_manifest.json"
        candidate_html.write_text(html, encoding="utf-8")
        candidate_manifest.write_text(manifest_text, encoding="utf-8")
        validate_manifest(json.loads(candidate_manifest.read_text(encoding="utf-8")))
        validate_candidate_html(candidate_html.read_text(encoding="utf-8"), manifest)
        reporter.ok("Bundle candidato y manifest superaron los gates de integridad")

        if same_inputs and paths.root_html.is_file() and paths.manifest_path.is_file():
            current_manifest = paths.manifest_path.read_text(encoding="utf-8")
            current_html = paths.root_html.read_text(encoding="utf-8")
            if current_manifest == manifest_text and current_html == html:
                reporter.ok("NO_CHANGES: los inputs y el bundle vigente son idénticos")
                return {"status": "NO_CHANGES", "manifest": manifest, "warnings": sorted(set(warnings))}

        if dry_run:
            reporter.ok("DRY_RUN: candidato validado; producción no fue modificada")
            return {"status": "DRY_RUN", "manifest": manifest, "warnings": sorted(set(warnings))}

        publish_bundle(html, manifest_text, paths)
        reporter.ok("Bundle publicado de forma segura; HTML raíz reemplazado al final")
        return {"status": "PUBLISHED", "manifest": manifest, "warnings": sorted(set(warnings))}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Snapshot CSV local explícito.")
    parser.add_argument("--dry-run", action="store_true", help="Valida y prepara sin publicar.")
    parser.add_argument("--verbose", action="store_true", help="Muestra hashes y fechas detalladas.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    reporter = Reporter(args.verbose)
    try:
        run_refresh(explicit_input=args.input, dry_run=args.dry_run, verbose=args.verbose)
        return 0
    except InputValidationError as exc:
        reporter.error(str(exc))
        return 2
    except ProcessingError as exc:
        reporter.error(str(exc))
        return 3
    except IntegrityError as exc:
        reporter.error(str(exc))
        return 4
    except PublicationError as exc:
        reporter.error(str(exc))
        return 5
    except Exception as exc:
        reporter.error(f"UNEXPECTED_PROCESSING_ERROR: {exc}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
