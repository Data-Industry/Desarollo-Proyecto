"""Construye un calendario de pagos e integra variables explicativas al retail.

SCRUM-37 / US-23. El módulo separa una regla operativa solicitada en Jira de
la ventana oficial de disponibilidad de pensiones. También conserva el dato
original y deja trazabilidad cuando en el futuro sea necesario completar un
valor faltante con evidencia suficiente.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


# ============================================================
# PASO 1: Configuración y rutas
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
FIGURES_DIR = PROJECT_DIR / "docs" / "figures"

RETAIL_INPUT_PATH = PROCESSED_DIR / "retail_stock_historico_consolidado.csv"
CALENDAR_OUTPUT_PATH = PROCESSED_DIR / "calendario_rentas_2026.csv"
RETAIL_OUTPUT_PATH = PROCESSED_DIR / "retail_stock_imputado_calendario.csv"

REGLA_PAGO_RENTA = "Días 1 al 5 de cada mes y último día calendario del mes"
FUENTE_REGLA_PAGO_RENTA = (
    "REGLA_OPERATIVA_JIRA_NO_VALIDADA_COMO_CALENDARIO_OFICIAL"
)
REGLA_PAGO_PENSION_OFICIAL = (
    "Ventana de disponibilidad mensual de pensiones: días 1 al 7"
)
FUENTE_PAGO_PENSION_OFICIAL = (
    "Normativa/Gestora: disponibilidad mensual de pensiones del día 1 al 7 "
    "(evidencia oficial externa revisada por el proyecto)"
)


# ============================================================
# PASO 2: Construcción del calendario
# ============================================================

def build_calendar(year: int = 2026) -> pd.DataFrame:
    """Crea una tabla con una fila por cada día del año indicado.

    Recibe el año calendario y devuelve fecha, año, mes, día, nombre del día,
    indicador de fin de semana e indicador de último día del mes.
    """
    fechas = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
    calendario = pd.DataFrame({"fecha": fechas})
    calendario["anio"] = calendario["fecha"].dt.year
    calendario["mes"] = calendario["fecha"].dt.month
    calendario["dia"] = calendario["fecha"].dt.day
    calendario["dia_semana"] = calendario["fecha"].dt.day_name(locale="C")
    calendario["es_fin_semana"] = calendario["fecha"].dt.dayofweek.ge(5)
    calendario["es_ultimo_dia_mes"] = calendario["fecha"].dt.is_month_end
    return calendario


# ============================================================
# PASO 3: Creación de variables de pago
# ============================================================

def _nearest_signed_distance(
    fecha: pd.Timestamp, payment_dates: Sequence[pd.Timestamp]
) -> int:
    """Devuelve la distancia firmada al día de pago más cercano.

    Recibe una fecha y días marcados como pago. Un valor negativo significa que
    la fecha está antes del pago elegido; uno positivo, que está después. Si hay
    empate, se elige el pago más temprano para que el resultado sea repetible.
    """
    candidates = sorted(
        ((abs((fecha - pago).days), pago) for pago in payment_dates),
        key=lambda item: (item[0], item[1]),
    )
    pago_elegido = candidates[0][1]
    return int((fecha - pago_elegido).days)


def add_payment_variables(calendario: pd.DataFrame) -> pd.DataFrame:
    """Agrega reglas de pago, fuentes y ventana de impacto de tres días.

    Recibe un calendario diario que contiene ``fecha`` y devuelve una copia con
    la regla operativa de Jira, la ventana oficial 1--7 y la distancia al pago
    operativo más cercano. La ventana temporal incluye tres días antes y tres
    días después de cada fecha operativa.
    """
    resultado = calendario.copy()
    resultado["fecha"] = pd.to_datetime(resultado["fecha"])

    # La regla de Jira se conserva separada porque no constituye evidencia de
    # un calendario oficial de Banco Unión.
    resultado["dia_pago_renta"] = (
        resultado["fecha"].dt.day.between(1, 5)
        | resultado["fecha"].dt.is_month_end
    ).astype(int)
    resultado["regla_pago_renta"] = REGLA_PAGO_RENTA
    resultado["fuente_regla_pago_renta"] = FUENTE_REGLA_PAGO_RENTA

    # Esta variable significa disponibilidad normativa, no retiro efectivo de
    # cada persona jubilada en esos días.
    resultado["dia_pago_pension_oficial"] = (
        resultado["fecha"].dt.day.between(1, 7)
    ).astype(int)
    resultado["regla_pago_pension_oficial"] = REGLA_PAGO_PENSION_OFICIAL
    resultado["fuente_pago_pension_oficial"] = FUENTE_PAGO_PENSION_OFICIAL

    payment_dates = resultado.loc[
        resultado["dia_pago_renta"].eq(1), "fecha"
    ].tolist()
    resultado["distancia_dias_pago_renta"] = resultado["fecha"].map(
        lambda fecha: _nearest_signed_distance(fecha, payment_dates)
    )
    resultado["ventana_pago_renta_3d"] = (
        resultado["distancia_dias_pago_renta"].abs().le(3)
    ).astype(int)
    return resultado


# ============================================================
# PASO 4: Detección de valores faltantes
# ============================================================

def detect_missing_values(retail: pd.DataFrame) -> Dict[str, int]:
    """Cuenta faltantes en los tres campos retail considerados en esta historia.

    Recibe las observaciones retail y devuelve un diccionario con los conteos
    de ``precio_bs``, ``estado_stock`` y ``stock_disponible_binario``.
    """
    columns = ["precio_bs", "estado_stock", "stock_disponible_binario"]
    return {column: int(retail[column].isna().sum()) for column in columns}


# ============================================================
# PASO 5: Imputación conservadora
# ============================================================

def _median_from_groups(
    data: pd.DataFrame,
    row: pd.Series,
    value_column: str,
    group_options: Iterable[Tuple[List[str], str]],
    minimum_observations: int,
) -> Tuple[Optional[float], Optional[str]]:
    """Busca una mediana por grupos ordenados sin usar un promedio global.

    Recibe datos, una fila faltante, el campo numérico y las agrupaciones a
    revisar. Devuelve el valor central del primer grupo con evidencia suficiente
    y el nombre del método; si no existe, devuelve valores nulos.
    """
    observed = data[data[value_column].notna()]
    for keys, method in group_options:
        if row[keys].isna().any():
            continue
        mask = pd.Series(True, index=observed.index)
        for key in keys:
            mask &= observed[key].eq(row[key])
        candidates = observed.loc[mask, value_column]
        if len(candidates) >= minimum_observations:
            # Mediana: valor central; reduce la influencia de precios extremos.
            return float(candidates.median()), method
    return None, None


def impute_prices(retail: pd.DataFrame, minimum_observations: int = 3) -> pd.DataFrame:
    """Completa precios faltantes sólo cuando un grupo comparable tiene evidencia.

    Recibe retail y un mínimo de observaciones. Devuelve una copia con precio
    original, precio resultante, bandera y método. Usa mediana por farmacia y
    marca; como segunda opción, farmacia y principio activo. Sin evidencia, el
    faltante se conserva.
    """
    result = retail.copy()
    result["precio_bs_original"] = result["precio_bs"]
    result["precio_bs_imputado"] = result["precio_bs"]
    result["precio_fue_imputado"] = False
    result["metodo_imputacion_precio"] = "SIN_IMPUTACION_VALOR_OBSERVADO"

    options = [
        (["farmacia", "marca_comercial"], "MEDIANA_FARMACIA_MARCA_COMERCIAL"),
        (["farmacia", "principio_activo"], "MEDIANA_FARMACIA_PRINCIPIO_ACTIVO"),
    ]
    missing_indices = result.index[result["precio_bs"].isna()]
    for index in missing_indices:
        value, method = _median_from_groups(
            result, result.loc[index], "precio_bs", options, minimum_observations
        )
        if value is None:
            result.at[index, "metodo_imputacion_precio"] = "SIN_EVIDENCIA_SUFICIENTE"
            continue
        result.at[index, "precio_bs_imputado"] = value
        result.at[index, "precio_fue_imputado"] = True
        result.at[index, "metodo_imputacion_precio"] = method
    return result


def _mode_from_groups(
    data: pd.DataFrame,
    row: pd.Series,
    value_column: str,
    group_options: Iterable[Tuple[List[str], str]],
    minimum_observations: int,
) -> Tuple[Optional[str], Optional[str]]:
    """Busca una moda clara por grupos ordenados.

    Recibe datos categóricos y devuelve el valor más frecuente cuando hay un
    único ganador y suficientes observaciones. La moda es el valor que aparece
    con mayor frecuencia; un empate se mantiene como faltante por prudencia.
    """
    observed = data[data[value_column].notna()]
    for keys, method in group_options:
        if row[keys].isna().any():
            continue
        mask = pd.Series(True, index=observed.index)
        for key in keys:
            mask &= observed[key].eq(row[key])
        candidates = observed.loc[mask, value_column]
        if len(candidates) < minimum_observations:
            continue
        counts = candidates.value_counts()
        if len(counts) and (len(counts) == 1 or counts.iloc[0] > counts.iloc[1]):
            return str(counts.index[0]), method
    return None, None


def impute_stock_status(retail: pd.DataFrame, minimum_observations: int = 3) -> pd.DataFrame:
    """Completa estados de stock faltantes sólo con una moda clara y suficiente.

    Recibe retail y un mínimo de observaciones. Devuelve columnas originales e
    imputadas de estado. No modifica anillos, coordenadas ni lags, porque esos
    campos requieren otra clase de evidencia.
    """
    result = retail.copy()
    result["estado_stock_original"] = result["estado_stock"]
    result["estado_stock_imputado"] = result["estado_stock"]
    result["stock_fue_imputado"] = False
    result["metodo_imputacion_stock"] = "SIN_IMPUTACION_VALOR_OBSERVADO"

    options = [
        (["farmacia", "marca_comercial"], "MODA_FARMACIA_MARCA_COMERCIAL"),
        (["farmacia", "principio_activo"], "MODA_FARMACIA_PRINCIPIO_ACTIVO"),
    ]
    missing_indices = result.index[result["estado_stock"].isna()]
    for index in missing_indices:
        value, method = _mode_from_groups(
            result, result.loc[index], "estado_stock", options, minimum_observations
        )
        if value is None:
            result.at[index, "metodo_imputacion_stock"] = "SIN_EVIDENCIA_SUFICIENTE"
            continue
        result.at[index, "estado_stock_imputado"] = value
        result.at[index, "stock_fue_imputado"] = True
        result.at[index, "metodo_imputacion_stock"] = method
    return result


def apply_conservative_imputation(
    retail: pd.DataFrame, minimum_observations: int = 3
) -> pd.DataFrame:
    """Aplica trazabilidad de precio y stock sin alterar las columnas originales.

    Recibe retail y el mínimo de evidencia. Devuelve el mismo retail con las
    columnas de auditoría de ambas reglas de imputación.
    """
    return impute_stock_status(
        impute_prices(retail, minimum_observations), minimum_observations
    )


# ============================================================
# PASO 6: Unión con datos retail
# ============================================================

def merge_retail_with_calendar(retail: pd.DataFrame, calendar: pd.DataFrame) -> pd.DataFrame:
    """Une cada observación retail con su fecha de calendario sin crear filas.

    Recibe retail con ``timestamp`` y un calendario diario. Devuelve el retail
    con las variables de pago de su misma fecha. La unión conserva exactamente
    el número de observaciones originales.
    """
    result = retail.copy()
    result["fecha"] = pd.to_datetime(result["timestamp"], utc=True, errors="coerce").dt.tz_localize(None).dt.normalize()
    calendar_columns = [
        "fecha", "dia_pago_renta", "ventana_pago_renta_3d",
        "distancia_dias_pago_renta", "dia_pago_pension_oficial",
    ]
    merged = result.merge(
        calendar[calendar_columns], on="fecha", how="left", validate="many_to_one"
    )
    if len(merged) != len(retail):
        raise ValueError("La unión con el calendario no debe crear observaciones nuevas.")
    return merged


# ============================================================
# PASO 7: Resumen de resultados
# ============================================================

def build_summary(before: Dict[str, int], final_retail: pd.DataFrame, calendar: pd.DataFrame) -> Dict[str, int]:
    """Resume tamaños, faltantes e imputaciones para auditoría y documentación.

    Recibe conteos previos, retail final y calendario. Devuelve números enteros
    que describen lo observado, sin inferir efectos sobre demanda o stock.
    """
    after = detect_missing_values(final_retail)
    return {
        "dias_calendario": int(len(calendar)),
        "dias_pago_renta": int(calendar["dia_pago_renta"].sum()),
        "dias_ventana_pago_renta_3d": int(calendar["ventana_pago_renta_3d"].sum()),
        "dias_pago_pension_oficial": int(calendar["dia_pago_pension_oficial"].sum()),
        "observaciones_retail_cruzadas": int(len(final_retail)),
        "faltantes_precio_antes": before["precio_bs"],
        "faltantes_stock_antes": before["estado_stock"],
        "faltantes_binario_antes": before["stock_disponible_binario"],
        "faltantes_precio_despues": after["precio_bs"],
        "faltantes_stock_despues": after["estado_stock"],
        "faltantes_binario_despues": after["stock_disponible_binario"],
        "precios_imputados": int(final_retail["precio_fue_imputado"].sum()),
        "stocks_imputados": int(final_retail["stock_fue_imputado"].sum()),
    }


def generate_figures(calendar: pd.DataFrame, before: Dict[str, int], final_retail: pd.DataFrame) -> None:
    """Genera dos gráficos simples del calendario y de faltantes antes/después.

    Recibe el calendario, faltantes iniciales y retail final. Guarda imágenes
    PNG para explicar la preparación de datos; no estima efectos causales.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Calendario por día del año: azul para pago, naranja para la ventana ±3.
    fig, ax = plt.subplots(figsize=(14, 3.5))
    ax.scatter(calendar["fecha"], calendar["ventana_pago_renta_3d"], s=12,
               color="#f4a261", label="Ventana ±3 días")
    pagos = calendar[calendar["dia_pago_renta"].eq(1)]
    ax.scatter(pagos["fecha"], pagos["dia_pago_renta"], s=28,
               color="#1d4ed8", label="Regla operativa Jira")
    ax.set_title("Calendario 2026: regla operativa de renta y ventana temporal")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Día marcado")
    ax.set_yticks([0, 1])
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "calendario_pago_rentas_2026.png", dpi=180)
    plt.close(fig)

    after = detect_missing_values(final_retail)
    labels = ["Precio", "Estado stock", "Stock binario"]
    before_values = [before["precio_bs"], before["estado_stock"], before["stock_disponible_binario"]]
    after_values = [after["precio_bs"], after["estado_stock"], after["stock_disponible_binario"]]
    positions = range(len(labels))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([position - 0.18 for position in positions], before_values, width=0.36, label="Antes")
    ax.bar([position + 0.18 for position in positions], after_values, width=0.36, label="Después")
    ax.set_xticks(list(positions), labels)
    ax.set_ylabel("Cantidad de valores faltantes")
    ax.set_title("Faltantes antes y después de la imputación conservadora")
    ax.legend()
    # Cuando todos los conteos son cero, se conserva una escala legible en vez
    # de permitir que la biblioteca dibuje valores negativos alrededor de cero.
    if max(before_values + after_values) == 0:
        ax.set_ylim(0, 1)
    for position, value in enumerate(before_values):
        ax.text(position - 0.18, value + 0.03, str(value), ha="center")
    for position, value in enumerate(after_values):
        ax.text(position + 0.18, value + 0.03, str(value), ha="center")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "faltantes_imputacion_scrum37.png", dpi=180)
    plt.close(fig)


def run_pipeline() -> Dict[str, int]:
    """Ejecuta calendario, trazabilidad, unión y exportaciones de SCRUM-37.

    No recibe parámetros. Lee el retail consolidado, guarda los dos CSV y las
    figuras, y devuelve un resumen verificable del procesamiento.
    """
    retail = pd.read_csv(RETAIL_INPUT_PATH)
    missing_before = detect_missing_values(retail)
    calendar = add_payment_variables(build_calendar(2026))
    retail_imputed = apply_conservative_imputation(retail)
    final_retail = merge_retail_with_calendar(retail_imputed, calendar)

    calendar.to_csv(CALENDAR_OUTPUT_PATH, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    final_retail.to_csv(RETAIL_OUTPUT_PATH, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    generate_figures(calendar, missing_before, final_retail)
    return build_summary(missing_before, final_retail, calendar)


if __name__ == "__main__":
    print(run_pipeline())
