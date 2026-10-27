"""Pipeline de Ingesta, Limpieza y Normalización del Tipo de Cambio Oficial del BCB (US-28).

Fuente oficial: Banco Central de Bolivia (BCB) - Gráfico Evolutivo de Cotizaciones
URL: https://www.bcb.gob.bo/grafico_evolutivo/
Endpoints oficiales en vivo identificados:
- Histórico: https://www.bcb.gob.bo/grafico_evolutivo/assets/datos-grafico-evolutivo.js
- Dinámico diario: https://www.bcb.gob.bo/grafico_evolutivo/tco-runtime.php

Salidas procesadas:
- data/raw/Tipo_de_cambio.csv (delimitador ';')
- data/processed/tipo_cambio_diario_bcb.csv
- data/processed/tipo_cambio_mensual_bcb.csv
- data/processed/tipo_cambio_historico_bolivia.csv
"""

from __future__ import annotations

import json
import logging
import os
import re
import ssl
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BCB_ExchangeRate")

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

BCB_RAW_CSV = RAW_DIR / "Tipo_de_cambio.csv"
BCB_DAILY_PROCESSED_CSV = PROCESSED_DIR / "tipo_cambio_diario_bcb.csv"
BCB_MONTHLY_PROCESSED_CSV = PROCESSED_DIR / "tipo_cambio_mensual_bcb.csv"
HISTORIC_TC_CSV = PROCESSED_DIR / "tipo_cambio_historico_bolivia.csv"

BCB_HISTORIC_JS_URL = "https://www.bcb.gob.bo/grafico_evolutivo/assets/datos-grafico-evolutivo.js"
BCB_RUNTIME_PHP_URL = "https://www.bcb.gob.bo/grafico_evolutivo/tco-runtime.php"

# Cache en memoria para consultas rápidas
_CACHED_MONTHLY_RATES: Dict[Tuple[int, int], float] = {}
_CACHED_DAILY_RATES: Dict[str, float] = {}


def fetch_live_bcb_exchange_rates(timeout_sec: int = 15) -> Optional[pd.DataFrame]:
    """Descarga de forma automatizada las cotizaciones oficiales en vivo desde los endpoints web del BCB.

    Combina el bloque histórico base (datos-grafico-evolutivo.js) con el flujo dinámico diario (tco-runtime.php).
    """
    logger.info("Intentando conexión con los servicios oficiales en vivo del Banco Central de Bolivia...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Data-Industry-Insulina/1.0"}
    all_data_points: List[Tuple[str, float]] = []

    try:
        # 1. Tramo base histórico
        req_hist = urllib.request.Request(BCB_HISTORIC_JS_URL, headers=headers)
        with urllib.request.urlopen(req_hist, context=ctx, timeout=timeout_sec) as resp:
            content_hist = resp.read().decode("utf-8", errors="ignore")
            match = re.search(r"DATOS_GRAFICO_EVOLUTIVO\s*=\s*(\{.*?\});", content_hist, re.DOTALL)
            if match:
                data_json = json.loads(match.group(1))
                points = data_json.get("tipo_de_cambio", {}).get("datos", [])
                for fecha, valor in points:
                    all_data_points.append((str(fecha), float(valor)))
                logger.info(f"Tramo histórico base BCB descargado ({len(points)} registros)")

        # 2. Tramo dinámico diario reciente
        req_dyn = urllib.request.Request(BCB_RUNTIME_PHP_URL, headers=headers)
        with urllib.request.urlopen(req_dyn, context=ctx, timeout=timeout_sec) as resp:
            content_dyn = resp.read().decode("utf-8", errors="ignore")
            match_dyn = re.search(r"BCB_TCO_DB\s*=\s*(\[.*?\]);", content_dyn, re.DOTALL)
            if match_dyn:
                points_dyn = json.loads(match_dyn.group(1))
                for fecha, valor in points_dyn:
                    all_data_points.append((str(fecha), float(valor)))
                logger.info(f"Tramo dinámico diario BCB descargado ({len(points_dyn)} registros)")

        if not all_data_points:
            return None

        df = pd.DataFrame(all_data_points, columns=["Fecha", "Valor"])
        df.drop_duplicates(subset=["Fecha"], keep="last", inplace=True)
        df.sort_values(by="Fecha", inplace=True)
        df.reset_index(drop=True, inplace=True)
        logger.info(f"Total serie oficial en vivo descargada: {len(df)} días ({df['Fecha'].min()} a {df['Fecha'].max()})")
        return df

    except Exception as exc:
        logger.warning(f"No se pudo descargar en vivo desde el portal BCB ({exc}). Se usará archivo local de respaldo.")
        return None


def load_raw_bcb_exchange_rate(file_path: Optional[Path] = None, try_live_fetch: bool = True) -> pd.DataFrame:
    """Carga y valida el archivo CSV crudo oficial del Banco Central de Bolivia.

    Si try_live_fetch es True, intenta actualizar desde la web oficial; si no,
    lee el CSV local data/raw/Tipo_de_cambio.csv delimitado con ';'.
    """
    path = Path(file_path) if file_path else BCB_RAW_CSV
    
    if try_live_fetch and not file_path:
        live_df = fetch_live_bcb_exchange_rates(timeout_sec=8)
        if live_df is not None and not live_df.empty:
            # Guardar versión sincronizada en data/raw con delimitador ';'
            os.makedirs(RAW_DIR, exist_ok=True)
            live_df.to_csv(BCB_RAW_CSV, sep=";", index=False, encoding="utf-8-sig")
            logger.info(f"Archivo crudo actualizado en: {BCB_RAW_CSV}")
            df = live_df.copy()
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
            return df.dropna(subset=["Fecha", "Valor"]).reset_index(drop=True)

    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo oficial del BCB en: {path}. "
            f"Descargue el archivo desde https://www.bcb.gob.bo/grafico_evolutivo/ "
            f"y deposítelo en data/raw/Tipo_de_cambio.csv"
        )

    # El archivo del BCB está delimitado por punto y coma ';'
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, sep=";", encoding="latin1")

    # Si por error vino delimitado por coma
    if df.shape[1] == 1 and ";" in df.columns[0]:
        df = pd.read_csv(path, sep=";", encoding="utf-8-sig")

    df.columns = [c.strip().capitalize() for c in df.columns]

    if "Fecha" not in df.columns or "Valor" not in df.columns:
        raise ValueError(
            f"Estructura inválida en archivo BCB. Columnas esperadas: ['Fecha', 'Valor']. "
            f"Columnas detectadas: {list(df.columns)}"
        )

    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    if df["Fecha"].isna().any():
        logger.warning(f"Se descartaron {df['Fecha'].isna().sum()} filas con fecha inválida.")
        df = df.dropna(subset=["Fecha"]).copy()

    if df["Valor"].dtype == object:
        df["Valor"] = (
            df["Valor"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.strip()
        )
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")

    df = df.dropna(subset=["Valor"]).copy()
    df.sort_values(by="Fecha", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def process_bcb_exchange_rates(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Genera las series diaria y mensual normalizadas con métricas de régimen y variación."""
    df_daily = raw_df.copy()
    df_daily["fecha_iso"] = df_daily["Fecha"].dt.strftime("%Y-%m-%d")
    df_daily["gestion"] = df_daily["Fecha"].dt.year
    df_daily["mes"] = df_daily["Fecha"].dt.month
    df_daily["dia"] = df_daily["Fecha"].dt.day
    df_daily["fecha_periodo"] = df_daily["Fecha"].dt.strftime("%Y-%m")
    df_daily["tipo_cambio_oficial_bob_usd"] = df_daily["Valor"].round(4)

    def clasificar_regimen(row):
        g = row["gestion"]
        m = row["mes"]
        if g <= 2022:
            return "Régimen de paridad fija (6.86/6.96 oficial)"
        elif g == 2023 and m < 10:
            return "Transición / Estabilidad cambiaria inicial"
        elif g == 2023 and m >= 10:
            return "Inicio de fluctuación y divergencia cambiaria"
        elif g == 2024:
            return "Régimen fluctuante interbancario de reposición"
        elif g == 2025:
            return "Régimen fluctuante con alta volatilidad"
        else:  # 2026
            return "Régimen de cotización fluctuante diaria BCB"

    df_daily["regimen_cambiario"] = df_daily.apply(clasificar_regimen, axis=1)
    df_daily["fuente_oficial"] = "Banco Central de Bolivia (BCB - Grafico Evolutivo)"

    # Serie mensual consolidada
    monthly_agg = df_daily.groupby(["gestion", "mes", "fecha_periodo"]).agg(
        dias_observados=("tipo_cambio_oficial_bob_usd", "count"),
        tipo_cambio_promedio_bob_usd=("tipo_cambio_oficial_bob_usd", "mean"),
        tipo_cambio_cierre_bob_usd=("tipo_cambio_oficial_bob_usd", "last"),
        tipo_cambio_minimo_bob_usd=("tipo_cambio_oficial_bob_usd", "min"),
        tipo_cambio_maximo_bob_usd=("tipo_cambio_oficial_bob_usd", "max"),
        regimen_cambiario=("regimen_cambiario", "last")
    ).reset_index()

    monthly_agg["tipo_cambio_promedio_bob_usd"] = monthly_agg["tipo_cambio_promedio_bob_usd"].round(4)
    monthly_agg["tipo_cambio_cierre_bob_usd"] = monthly_agg["tipo_cambio_cierre_bob_usd"].round(4)
    monthly_agg["tipo_cambio_minimo_bob_usd"] = monthly_agg["tipo_cambio_minimo_bob_usd"].round(4)
    monthly_agg["tipo_cambio_maximo_bob_usd"] = monthly_agg["tipo_cambio_maximo_bob_usd"].round(4)

    monthly_agg.sort_values(by=["gestion", "mes"], inplace=True)
    monthly_agg["variacion_intermensual_pct"] = (
        monthly_agg["tipo_cambio_promedio_bob_usd"].pct_change() * 100
    ).fillna(0.0).round(2)
    monthly_agg["fuente_oficial"] = "Banco Central de Bolivia (BCB - Grafico Evolutivo)"

    return df_daily, monthly_agg


def run_bcb_pipeline(file_path: Optional[Path] = None, try_live_fetch: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Ejecuta el pipeline de ingesta del tipo de cambio oficial del BCB y exporta artefactos."""
    logger.info("=== INICIANDO PIPELINE DE TIPO DE CAMBIO OFICIAL BCB (US-28) ===")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_bcb_exchange_rate(file_path, try_live_fetch=try_live_fetch)
    df_daily, df_monthly = process_bcb_exchange_rates(raw_df)

    # Exportar datasets procesados
    df_daily.to_csv(BCB_DAILY_PROCESSED_CSV, index=False, encoding="utf-8-sig")
    df_monthly.to_csv(BCB_MONTHLY_PROCESSED_CSV, index=False, encoding="utf-8-sig")

    # Retrocompatibilidad
    df_compat = df_monthly[[
        "gestion", "mes", "fecha_periodo", "tipo_cambio_promedio_bob_usd", "regimen_cambiario"
    ]].rename(columns={"tipo_cambio_promedio_bob_usd": "tipo_cambio_bob_usd"})
    df_compat.to_csv(HISTORIC_TC_CSV, index=False, encoding="utf-8-sig")

    # Actualizar cache en memoria
    global _CACHED_MONTHLY_RATES, _CACHED_DAILY_RATES
    _CACHED_MONTHLY_RATES = {
        (int(r["gestion"]), int(r["mes"])): float(r["tipo_cambio_promedio_bob_usd"])
        for _, r in df_monthly.iterrows()
    }
    _CACHED_DAILY_RATES = {
        str(r["fecha_iso"]): float(r["tipo_cambio_oficial_bob_usd"])
        for _, r in df_daily.iterrows()
    }

    logger.info(f"Serie diaria oficial BCB exportada: {len(df_daily)} registros ({BCB_DAILY_PROCESSED_CSV.name})")
    logger.info(f"Serie mensual oficial BCB exportada: {len(df_monthly)} periodos ({BCB_MONTHLY_PROCESSED_CSV.name})")
    logger.info("=== PIPELINE BCB COMPLETADO EXITOSAMENTE ===")

    return df_daily, df_monthly


def get_official_exchange_rate(gestion: int, mes: int, fecha_especifica: Optional[str] = None) -> float:
    """Retorna la cotización oficial del BCB para una gestión y mes dados (o fecha diaria específica)."""
    global _CACHED_MONTHLY_RATES, _CACHED_DAILY_RATES

    if not _CACHED_MONTHLY_RATES:
        if BCB_MONTHLY_PROCESSED_CSV.exists():
            df_m = pd.read_csv(BCB_MONTHLY_PROCESSED_CSV)
            _CACHED_MONTHLY_RATES = {
                (int(r["gestion"]), int(r["mes"])): float(r["tipo_cambio_promedio_bob_usd"])
                for _, r in df_m.iterrows()
            }
        elif BCB_RAW_CSV.exists():
            _, df_m = run_bcb_pipeline(try_live_fetch=False)
        else:
            return 11.82 if gestion >= 2026 else (6.86 if gestion <= 2022 else 6.96)

    if fecha_especifica and not _CACHED_DAILY_RATES and BCB_DAILY_PROCESSED_CSV.exists():
        df_d = pd.read_csv(BCB_DAILY_PROCESSED_CSV)
        _CACHED_DAILY_RATES = {
            str(r["fecha_iso"]): float(r["tipo_cambio_oficial_bob_usd"])
            for _, r in df_d.iterrows()
        }

    if fecha_especifica and fecha_especifica in _CACHED_DAILY_RATES:
        return _CACHED_DAILY_RATES[fecha_especifica]

    if (gestion, mes) in _CACHED_MONTHLY_RATES:
        return _CACHED_MONTHLY_RATES[(gestion, mes)]

    if gestion == 2026:
        oct_2026 = _CACHED_MONTHLY_RATES.get((2026, 10))
        if oct_2026 is not None:
            return oct_2026

    return 6.86 if gestion <= 2022 else 11.82


if __name__ == "__main__":
    d, m = run_bcb_pipeline()
    print("\nÚltimos 10 periodos mensuales del tipo de cambio oficial BCB:")
    print(m.tail(10)[["gestion", "mes", "fecha_periodo", "tipo_cambio_promedio_bob_usd", "variacion_intermensual_pct", "regimen_cambiario"]])
