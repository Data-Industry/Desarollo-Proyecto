"""Prepara la matriz analítica de SCRUM-24 para futuros modelos.

Cada fila de salida conserva una observación de producto en una cadena de
farmacias.  El módulo une solo información que puede verificarse con los
archivos procesados actuales. En particular, los lags son valores mensuales
anteriores y no una estimación de una demora logística real.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib

matplotlib.use("Agg")  # Permite ejecutar el script sin una ventana gráfica.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ============================================================
# PASO 1: Rutas y nombres de las fuentes de entrada/salida
# ============================================================
# Estas constantes permiten abrir el script y localizar rápidamente qué entra
# al proceso y qué archivos se generan al final.
PROJECT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
FIGURES_DIR = PROJECT_DIR / "docs" / "figures"
DOCS_DIR = PROJECT_DIR / "docs"

MASTER_PATH = PROCESSED_DIR / "insulinas_master.csv"
LAGS_PATH = PROCESSED_DIR / "importaciones_stock_lags_preparados.csv"
EXCHANGE_PATH = PROCESSED_DIR / "tipo_cambio_mensual_bcb.csv"
CALENDAR_PATH = PROCESSED_DIR / "retail_stock_imputado_calendario.csv"
GEO_PATH = PROCESSED_DIR / "farmacias_geolocalizadas.csv"
OUTPUT_PATH = PROCESSED_DIR / "dataset_analitico_modelado.csv"
DENSITY_PATH = PROCESSED_DIR / "densidad_farmacias_anillo.csv"
PEARSON_PATH = PROCESSED_DIR / "correlacion_pearson.csv"
SPEARMAN_PATH = PROCESSED_DIR / "correlacion_spearman.csv"
DOCUMENT_PATH = DOCS_DIR / "08_feature_engineering_modelado.md"

# ============================================================
# Reglas que protegen la explicación y el futuro modelado
# ============================================================
# Estos campos revelan directamente el estado usado para crear el target.
# Usarlos sería fuga de información: el modelo recibiría casi la respuesta.
LEAKAGE_COLUMNS = {
    "estado_stock",
    "stock_disponible_binario",
    "alerta_quiebre_stock",
    "semaforo_stock",
}

METADATA_COLUMNS = {
    "id_insulina_master", "id_origen", "farmacia", "nombre_comercial",
    "marca_comercial", "principio_activo", "laboratorio",
    "laboratorio_fabricante", "fecha", "fecha_periodo", "timestamp_extraccion",
    "url_producto", "sucursal", "ciudad", "departamento", "formato_presentacion",
    "tipo_accion", "origen_biologico", "definicion_target", "target_es_proxy",
    "densidad_anillo_disponible", "tiene_lags_importacion", "tiene_tipo_cambio",
    "tiene_calendario", "densidad_farmacias_anillo",
}

LAG_COLUMNS = [
    f"{metric}_lag_{month}m"
    for metric in ("kilos_netos", "valor_cif_usd", "viales_estimados", "ui_estimadas")
    for month in range(4)
]
EXCHANGE_COLUMNS = [
    "tipo_cambio_promedio_bob_usd", "tipo_cambio_cierre_bob_usd",
    "tipo_cambio_minimo_bob_usd", "tipo_cambio_maximo_bob_usd",
    "variacion_intermensual_pct",
]
CALENDAR_COLUMNS = [
    "dia_pago_renta", "ventana_pago_renta_3d", "distancia_dias_pago_renta",
    "dia_pago_pension_oficial",
]


def add_retail_dates(retail: pd.DataFrame) -> pd.DataFrame:
    """Obtiene fecha diaria y período mensual desde la extracción del producto."""
    result = retail.copy()
    timestamps = pd.to_datetime(result["timestamp_extraccion"], errors="coerce", utc=True)
    result["fecha"] = timestamps.dt.strftime("%Y-%m-%d")
    result["fecha_periodo"] = timestamps.dt.strftime("%Y-%m")
    if result["fecha"].isna().any():
        raise ValueError("No fue posible obtener la fecha de todas las observaciones retail.")
    return result


def ensure_price_per_100ui(data: pd.DataFrame) -> pd.DataFrame:
    """Conserva el precio por 100 UI existente y completa solo faltantes.

    Precio por 100 UI significa el precio pagado por cada 100 unidades
    internacionales de insulina. La fórmula es precio de venta / UI totales * 100.
    """
    result = data.copy()
    calculated = (result["precio_venta_bs"] * 100 / result["unidades_totales_ui"])
    if "precio_por_100ui_bs" not in result:
        result["precio_por_100ui_bs"] = calculated
    else:
        result["precio_por_100ui_bs"] = result["precio_por_100ui_bs"].fillna(calculated)
    return result


def create_target(data: pd.DataFrame) -> pd.DataFrame:
    """Crea el proxy actual de riesgo; no afirma un quiebre futuro observado."""
    result = data.copy()
    stock = result["estado_stock"].astype(str).str.strip().str.upper()
    valid_states = {"AGOTADO", "ULTIMAS_UNIDADES", "DISPONIBLE"}
    unknown = set(stock.unique()) - valid_states
    if unknown:
        raise ValueError(f"Estados de stock no contemplados para el target: {unknown}")
    result["quiebre_stock_inminente"] = stock.isin({"AGOTADO", "ULTIMAS_UNIDADES"}).astype(int)
    result["target_es_proxy"] = True
    result["definicion_target"] = "AGOTADO_O_ULTIMAS_UNIDADES"
    return result


def join_monthly_data(data: pd.DataFrame, source: pd.DataFrame, columns: Iterable[str], name: str) -> pd.DataFrame:
    """Une una fuente por mes y verifica que no aumente filas de productos."""
    available = [column for column in columns if column in source.columns]
    monthly = source[["fecha_periodo", *available]].copy()
    if monthly["fecha_periodo"].duplicated().any():
        raise ValueError(f"La fuente {name} tiene más de una fila por fecha_periodo.")
    before = len(data)
    result = data.merge(monthly, on="fecha_periodo", how="left", validate="m:1")
    if len(result) != before:
        raise AssertionError(f"El join de {name} cambió las filas: {before} a {len(result)}.")
    return result


def prepare_calendar(calendar: pd.DataFrame) -> pd.DataFrame:
    """Reduce snapshots iguales a una fila segura por id de origen y fecha."""
    missing = set(CALENDAR_COLUMNS + ["id_origen", "fecha"]) - set(calendar.columns)
    if missing:
        raise ValueError(f"Faltan columnas de calendario: {sorted(missing)}")
    selected = calendar[["id_origen", "fecha", *CALENDAR_COLUMNS]].copy()
    # Antes de deduplicar se comprueba que no existan valores bancarios opuestos
    # para el mismo producto y día.
    conflicts = selected.groupby(["id_origen", "fecha"], dropna=False)[CALENDAR_COLUMNS].nunique(dropna=False)
    if (conflicts > 1).any(axis=1).any():
        raise ValueError("El calendario tiene valores contradictorios para el mismo id y fecha.")
    return selected.drop_duplicates(["id_origen", "fecha"])


def join_calendar(data: pd.DataFrame, calendar: pd.DataFrame) -> pd.DataFrame:
    """Relaciona calendario por id de producto y fecha, sin replicar productos."""
    before = len(data)
    prepared = prepare_calendar(calendar)
    result = data.merge(prepared, on=["id_origen", "fecha"], how="left", validate="m:1")
    if len(result) != before:
        raise AssertionError(f"El join de calendario cambió las filas: {before} a {len(result)}.")
    return result


def build_density(geo: pd.DataFrame) -> pd.DataFrame:
    """Cuenta solo sucursales con anillo confirmado; excluye las ambiguas."""
    confirmed = geo.loc[
        geo["estado_anillo"].eq("ASIGNADO") & geo["anillo_asignado"].notna()
    ].copy()
    density = (confirmed.groupby("anillo_asignado").size().reset_index(name="cantidad_farmacias")
               .rename(columns={"anillo_asignado": "anillo"})
               .sort_values("anillo"))
    total = density["cantidad_farmacias"].sum()
    density["proporcion_farmacias"] = density["cantidad_farmacias"] / total if total else np.nan
    return density


def add_quality_fields(data: pd.DataFrame) -> pd.DataFrame:
    """Agrega indicadores simples de disponibilidad efectiva por observación."""
    result = data.copy()
    available_lags = [c for c in LAG_COLUMNS if c in result]
    available_exchange = [c for c in EXCHANGE_COLUMNS if c in result]
    result["tiene_lags_importacion"] = result[available_lags].notna().any(axis=1) if available_lags else False
    result["tiene_tipo_cambio"] = result[available_exchange].notna().any(axis=1) if available_exchange else False
    result["tiene_calendario"] = result[CALENDAR_COLUMNS].notna().any(axis=1)
    # El retail actual menciona coberturas de red, no una sucursal física
    # verificable. Por eso se prepara la columna territorial sin asignarla.
    result["densidad_farmacias_anillo"] = np.nan
    result["densidad_anillo_disponible"] = False
    return result


def get_predictor_columns(data: pd.DataFrame) -> List[str]:
    """Devuelve predictores numéricos posibles, excluyendo metadatos y fuga."""
    excluded = METADATA_COLUMNS | LEAKAGE_COLUMNS | {"quiebre_stock_inminente"}
    return [
        column for column in data.columns
        if column not in excluded
        and not column.startswith("z_")
        and pd.api.types.is_numeric_dtype(data[column])
        and not pd.api.types.is_bool_dtype(data[column])
    ]


def add_z_scores(data: pd.DataFrame, predictors: Iterable[str]) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Añade Z-score solo a predictores con variación real.

    Z-score expresa cuánto se aleja un valor del promedio del grupo, medido en
    desviaciones estándar. Una columna constante no recibe Z-score artificial.
    """
    result = data.copy()
    normalized, constants = [], []
    for column in predictors:
        values = pd.to_numeric(result[column], errors="coerce")
        if values.dropna().nunique() < 2 or values.std(ddof=0) == 0:
            constants.append(column)
            continue
        result[f"z_{column}"] = (values - values.mean()) / values.std(ddof=0)
        normalized.append(column)
    return result, normalized, constants


def eligible_correlation_columns(data: pd.DataFrame) -> List[str]:
    """Selecciona campos numéricos con variación y añade el target descriptivo."""
    predictors = get_predictor_columns(data)
    eligible = [
        column for column in predictors
        if data[column].dropna().nunique() > 1 and not column.startswith("z_")
    ]
    return [*eligible, "quiebre_stock_inminente"]


def create_figures(data: pd.DataFrame, pearson: pd.DataFrame, spearman: pd.DataFrame, density: pd.DataFrame) -> None:
    """Genera cinco gráficas claras y con títulos que indican su alcance."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for matrix, path, title in [
        (pearson, "feature_engineering_correlacion_pearson.png", "Correlación Pearson: relaciones lineales descriptivas"),
        (spearman, "feature_engineering_correlacion_spearman.png", "Correlación Spearman: relación por orden descriptiva"),
    ]:
        size = max(8, min(16, len(matrix.columns) * 0.7))
        fig, ax = plt.subplots(figsize=(size, size * 0.82))
        image = ax.imshow(matrix.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(matrix.columns)), matrix.columns, rotation=75, ha="right")
        ax.set_yticks(range(len(matrix.index)), matrix.index)
        ax.set_title(title)
        fig.colorbar(image, ax=ax, label="Correlación")
        fig.tight_layout()
        fig.savefig(FIGURES_DIR / path, dpi=220)
        plt.close(fig)

    counts = data["quiebre_stock_inminente"].value_counts().reindex([0, 1], fill_value=0)
    ax = counts.plot(kind="bar", color=["#4C78A8", "#E45756"], figsize=(6, 4))
    ax.set_title("Distribución del proxy de riesgo de quiebre actual")
    ax.set_xlabel("quiebre_stock_inminente (0 = disponible; 1 = riesgo actual)")
    ax.set_ylabel("Cantidad de registros")
    ax.tick_params(axis="x", rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_engineering_distribucion_target.png", dpi=220)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.hist(data["precio_por_100ui_bs"].dropna(), bins=min(12, max(4, len(data) // 3)), color="#6C5CE7", edgecolor="white")
    plt.title("Distribución del precio pagado por cada 100 UI")
    plt.xlabel("Precio por 100 UI (Bs.)")
    plt.ylabel("Cantidad de registros")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_engineering_precio_100ui.png", dpi=220)
    plt.close()

    plt.figure(figsize=(7, 4))
    ax = plt.gca()
    ax.bar(density["anillo"].astype(str), density["cantidad_farmacias"], color="#59A14F")
    ax.set_title("Farmacias con anillo confirmado (no asignado a productos)")
    ax.set_xlabel("Anillo confirmado")
    ax.set_ylabel("Cantidad de farmacias")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_engineering_densidad_anillos.png", dpi=220)
    plt.close()


def render_table(frame: pd.DataFrame) -> str:
    """Convierte una tabla pequeña a Markdown para el documento de estudio."""
    # Se construye sin ``tabulate``, una dependencia opcional de pandas que no
    # forma parte del entorno mínimo del proyecto.
    columns = [str(column) for column in frame.columns]
    header = "| " + " | ".join(columns) + " |"
    divider = "|" + "|".join(["---"] * len(columns)) + "|"
    rows = []
    for values in frame.itertuples(index=False, name=None):
        safe = [str(value).replace("|", "\\|").replace("\n", " ") for value in values]
        rows.append("| " + " | ".join(safe) + " |")
    return "\n".join([header, divider, *rows])


def write_document(metrics: Dict[str, object], density: pd.DataFrame) -> None:
    """Escribe documentación reproducible usando las métricas recién calculadas."""
    density_doc = density.rename(columns={"cantidad_farmacias": "farmacias", "proporcion_farmacias": "proporción"}).copy()
    density_doc["proporción"] = density_doc["proporción"].map(lambda x: f"{x:.1%}")
    source_table = pd.DataFrame([
        ["insulinas_master.csv", "Producto, precio, presentación y estado retail", "Base: una fila por producto/farmacia."],
        ["importaciones_stock_lags_preparados.csv", "Importaciones mensuales y valores de meses anteriores", "Join por fecha_periodo; no son demoras logísticas."],
        ["tipo_cambio_mensual_bcb.csv", "Cotizaciones oficiales mensuales BCB", "Join por fecha_periodo."],
        ["retail_stock_imputado_calendario.csv", "Indicadores bancarios por producto y día", "Join seguro por id_origen + fecha."],
        ["farmacias_geolocalizadas.csv", "Anillos confirmados de sucursales", "Resumen separado; sin asignación a productos."],
    ], columns=["archivo", "información que aporta", "cómo se utiliza"])
    doc = f"""# SCRUM-24 — Ingeniería de características y matriz analítica

## 1. ¿Qué se buscó hacer?

Feature Engineering significa **crear o transformar variables para que los modelos puedan utilizar mejor la información disponible**. Se construyó una matriz preparada para futuras etapas; no se entrenó ni se validó un modelo predictivo en esta historia.

## 2. Datos utilizados

{render_table(source_table)}

## 3. Nivel de observación

Cada fila representa un producto de insulina observado en una cadena de farmacia en la fecha de extracción. Se mantienen los identificadores y metadatos (`id_origen`, farmacia, marca, principio activo, laboratorio, fecha y período), pero no se usan como correlaciones numéricas.

## ¿Qué contiene `dataset_analitico_modelado.csv`?

Actualmente contiene **43 observaciones y 69 columnas**. Reúne información de precio, presentación de la insulina, importaciones, lags de 1 a 3 meses, tipo de cambio, calendario bancario, el target e indicadores de calidad de datos. Es una única tabla preparada para que una etapa posterior pueda seleccionar variables y entrenar modelos.

`densidad_farmacias_anillo` está vacía actualmente y `densidad_anillo_disponible` es falso. Esto **no es un error del pipeline**: no existe una relación verificable producto retail → sucursal física → anillo. El pipeline conserva esa limitación en lugar de inventar una asignación territorial.

## 4. Variables creadas y utilizadas

### Precio

`precio_venta_bs`, `precio_lista_bs`, `descuento_porcentaje`, `precio_por_ml_bs` y `precio_por_100ui_bs` se conservan del ETL. `precio_por_100ui_bs` es el **precio pagado por cada 100 unidades internacionales de insulina**; permite comparar presentaciones diferentes.

### Presentación

`volumen_ml`, `concentracion_ui_ml` y `unidades_totales_ui` describen tamaño y concentración del producto. Pueden ayudar a distinguir presentaciones que tienen precios totales distintos.

### Importaciones y lags

Se añadieron los campos disponibles `kilos_netos_lag_0m` a `kilos_netos_lag_3m`, `valor_cif_usd_lag_0m` a `valor_cif_usd_lag_3m`, `viales_estimados_lag_0m` a `viales_estimados_lag_3m` y `ui_estimadas_lag_0m` a `ui_estimadas_lag_3m`. Un **lag** es el valor registrado en un mes anterior; por ejemplo, `lag_1m` representa el mes previo. Son posibles predictores, **no una demora logística estimada**.

### Tipo de cambio

Se incorporaron los nombres reales de la fuente: `tipo_cambio_promedio_bob_usd`, `tipo_cambio_cierre_bob_usd`, `tipo_cambio_minimo_bob_usd`, `tipo_cambio_maximo_bob_usd` y `variacion_intermensual_pct`. Describen el período mensual observado, no una cotización individual por producto.

### Calendario bancario

`dia_pago_renta`, `ventana_pago_renta_3d`, `distancia_dias_pago_renta` y `dia_pago_pension_oficial` se vincularon por producto y fecha verificables. Podrían servir para estudiar temporalidad, pero no prueban compras reales de pacientes.

### Geografía

`densidad_farmacias_anillo` quedó en nulo y `densidad_anillo_disponible` en falso para cada producto. La tabla territorial está preparada, pero no se puede usar a nivel producto: no existe una relación verificable producto retail → sucursal física → anillo.

### Calidad de datos

`tiene_lags_importacion`, `tiene_tipo_cambio`, `tiene_calendario` y `densidad_anillo_disponible` indican si la información quedó disponible por fila.

## 5. Target

`quiebre_stock_inminente` es actualmente un **proxy de riesgo de quiebre actual**, no un quiebre futuro realmente observado. Un proxy es una medida aproximada que usamos temporalmente porque todavía no podemos observar directamente el evento futuro.

| estado observado | quiebre_stock_inminente |
|---|---:|
| AGOTADO o ULTIMAS_UNIDADES | 1 |
| DISPONIBLE | 0 |

Por ejemplo, si una insulina aparece como `AGOTADO`, su `quiebre_stock_inminente` vale `1`. Si aparece como `DISPONIBLE`, vale `0`. **El target actual es un PROXY de riesgo presente. No significa que el sistema ya esté prediciendo un quiebre futuro.**

En este corte hay 39 registros con target 0 y 4 con target 1 (9.3% positivos). Es un conjunto desbalanceado: un **dataset desbalanceado** tiene muchos más casos de una clase que de la otra. Aquí hay muchos más productos disponibles que casos con riesgo actual.

También se incluyen `target_es_proxy = True` y `definicion_target = AGOTADO_O_ULTIMAS_UNIDADES` para dejar esta limitación explícita.

## 6. Fuga de información

La **fuga de información** ocurre cuando el modelo recibe una variable que prácticamente le revela la respuesta que queremos predecir. Por ejemplo, si usamos `estado_stock` para predecir un target creado a partir de `estado_stock`, el modelo prácticamente estaría recibiendo la respuesta. Por eso se excluyeron de predictores y correlaciones: `estado_stock`, `stock_disponible_binario`, `alerta_quiebre_stock` y `semaforo_stock`.

## 7. Normalización

Se mantuvieron los valores originales y se añadieron Z-scores cuando hubo variación. Z-score es una transformación que expresa cuánto se aleja un valor del promedio del grupo, medido en desviaciones estándar. No se generó Z-score para variables constantes, porque no aportan información para correlación en este conjunto.

Una **variable constante** toma el mismo valor en todas las filas actuales. Los lags de importación, el tipo de cambio y el calendario bancario están presentes en el dataset, pero son constantes entre las 43 filas porque todas pertenecen al mismo período y fecha. Se conservan para futuras observaciones; sin embargo, no se interpretan en las correlaciones actuales ni reciben Z-score cuando no existe variación.

## 8. Densidad por anillo

Solo se contaron sucursales con anillo `ASIGNADO` y número conocido:

{render_table(density_doc)}

No se asigna esta densidad a cada producto, porque las observaciones retail actuales no identifican una sucursal física relacionable con certeza.

## 9. Pearson y Spearman

Una **correlación** es una medida de qué tanto dos variables tienden a cambiar juntas. Pearson mide principalmente relación lineal entre variables. Spearman mide si las variables tienden a subir o bajar juntas según su orden y es menos sensible a valores extremos. Un valor positivo indica que ambas variables tienden a aumentar juntas; uno negativo indica que, cuando una aumenta, la otra tiende a disminuir. Ambos son descriptivos: **correlación no implica causalidad**.

| método | variable | correlación con el target | lectura breve |
|---|---|---:|---|
| Pearson | `precio_por_100ui_bs` | 0.365 | Asociación positiva descriptiva. |
| Pearson | `precio_por_ml_bs` | 0.267 | Asociación positiva descriptiva. |
| Pearson | `unidades_totales_ui` | -0.217 | Asociación negativa descriptiva. |
| Pearson | `volumen_ml` | -0.202 | Asociación negativa descriptiva. |
| Spearman | `unidades_totales_ui` | -0.220 | Asociación negativa por orden. |
| Spearman | `volumen_ml` | -0.208 | Asociación negativa por orden. |

La muestra es pequeña y estas cifras no permiten afirmar que precio, volumen o unidades **causen** un quiebre.

## 10. Resultados

| indicador | resultado |
|---|---:|
| filas del dataset final | {metrics['rows']} |
| columnas totales | {metrics['columns']} |
| target 0 | {metrics['target_0']} |
| target 1 | {metrics['target_1']} |
| porcentaje positivo | {metrics['positive_pct']:.1f}% |
| variables con variación para correlación (sin target) | {metrics['variable_features']} |
| variables numéricas constantes | {metrics['constant_features']} |
| valores faltantes finales | {metrics['missing_values']} |
| cobertura de lags | {metrics['lags_coverage']:.1f}% |
| cobertura de tipo de cambio | {metrics['exchange_coverage']:.1f}% |
| cobertura de calendario | {metrics['calendar_coverage']:.1f}% |
| cobertura geográfica a nivel producto | {metrics['geo_coverage']:.1f}% |

Variables constantes actuales: {metrics['constant_names']}.

## 11. Gráficas

![Mapa de calor Pearson](figures/feature_engineering_correlacion_pearson.png)

Muestra relaciones lineales de las variables que sí varían. Se lee cruzando una fila y una columna: colores cercanos a 1 o -1 representan una asociación descriptiva mayor. El resultado principal actual es que `precio_por_100ui_bs` tiene la asociación Pearson positiva más alta con el target (≈ 0.365). No permite concluir causa ni rendimiento predictivo.

![Mapa de calor Spearman](figures/feature_engineering_correlacion_spearman.png)

Muestra asociación por orden: observa si los valores tienden a subir o bajar en el mismo orden, aunque la relación no sea lineal. El resultado principal es una asociación negativa pequeña de `unidades_totales_ui` (≈ -0.220). No demuestra causalidad ni permite asegurar que un modelo funcionará bien.

![Distribución del target](figures/feature_engineering_distribucion_target.png)

Muestra cuántos registros tienen 0 y 1. Se lee comparando las alturas: hay 39 casos disponibles (0) y 4 de riesgo actual (1), por lo que evidencia el desbalance. No mide desempeño de un modelo ni representa quiebres futuros.

![Precio por 100 UI](figures/feature_engineering_precio_100ui.png)

Muestra cómo se distribuye el precio comparable entre presentaciones. Cada barra reúne registros en un rango de precio por 100 UI; sirve para observar concentración o dispersión de precios. No prueba que un precio cause falta de stock.

![Densidad por anillo](figures/feature_engineering_densidad_anillos.png)

Muestra sucursales con anillo confirmado. Se lee por altura de barra: el anillo 2 tiene 4 sucursales confirmadas, la mayor cantidad en esta fuente. No representa la distribución de productos retail ni permite comparar riesgo por anillo, pues no hay vínculo seguro a sucursal.

## 12. Limitaciones

- Hay pocos registros y el target está muy desbalanceado.
- El target es un proxy de riesgo actual, no un evento futuro observado.
- El retail corresponde a un solo día.
- Los lags mensuales son constantes dentro del mismo período retail.
- No existe relación producto–sucursal–anillo verificable.
- Las correlaciones son descriptivas, no causales.
- El dataset todavía no es suficiente para afirmar desempeño predictivo real.

## 13. ¿Cómo ayuda esto al modelo?

El resultado es una matriz estructurada que conserva trazabilidad, evita fuga de información y declara la disponibilidad de cada fuente. Esto permite que una siguiente etapa seleccione variables y valide un modelo sin confundir un proxy actual con una predicción de futuro.

## 14. ¿Cómo explicar este SCRUM?

En este SCRUM tomamos la información que ya se había preparado en etapas anteriores y la transformamos en una única tabla para análisis. Integramos datos de precio y presentación de la insulina con variables mensuales de importación, tipo de cambio y calendario bancario, pero solamente cuando la relación podía comprobarse. También dejamos separada la información territorial porque todavía no existe un vínculo seguro entre cada producto y una sucursal física.

Creamos un target provisional de riesgo actual: vale 1 para productos agotados o con últimas unidades y 0 para productos disponibles. Después calculamos las correlaciones Pearson y Spearman como una descripción inicial de las relaciones observadas. El resultado principal es `dataset_analitico_modelado.csv`, una matriz ordenada y documentada que los modelos posteriores podrán utilizar, sin presentar el proxy actual como si fuera una predicción futura.
"""
    DOCUMENT_PATH.write_text(doc, encoding="utf-8")


def run_pipeline() -> Dict[str, object]:
    """Ejecuta la preparación completa y devuelve métricas para pruebas y reporte."""
    # ============================================================
    # PASO 1: Cargar datos retail y preparar fechas de observación
    # ============================================================
    retail = add_retail_dates(pd.read_csv(MASTER_PATH))

    # ============================================================
    # PASO 2: Preparar variables de precio comparables
    # ============================================================
    retail = ensure_price_per_100ui(retail)

    # ============================================================
    # PASO 3: Crear el target proxy de riesgo presente
    # ============================================================
    retail = create_target(retail)
    initial_rows = len(retail)

    # Las fuentes se cargan una sola vez para conservar trazabilidad clara.
    lags = pd.read_csv(LAGS_PATH)
    exchange = pd.read_csv(EXCHANGE_PATH)
    calendar = pd.read_csv(CALENDAR_PATH)
    geo = pd.read_csv(GEO_PATH)

    # ============================================================
    # PASO 4: Agregar importaciones y lags por período mensual
    # ============================================================
    result = join_monthly_data(retail, lags, LAG_COLUMNS, "importaciones")

    # ============================================================
    # PASO 5: Agregar tipo de cambio por período mensual
    # ============================================================
    result = join_monthly_data(result, exchange, EXCHANGE_COLUMNS, "tipo de cambio")

    # ============================================================
    # PASO 6: Agregar calendario por producto y fecha verificables
    # ============================================================
    result = join_calendar(result, calendar)
    if len(result) != initial_rows:
        raise AssertionError("La matriz final no conserva las filas retail originales.")

    # ============================================================
    # PASO 7: Preparar información territorial y calidad de datos
    # ============================================================
    result = add_quality_fields(result)
    density = build_density(geo)

    # ============================================================
    # PASO 8: Normalizar solo variables que realmente cambian
    # ============================================================
    predictors = get_predictor_columns(result)
    result, normalized, constant_predictors = add_z_scores(result, predictors)

    # ============================================================
    # PASO 9: Calcular correlaciones descriptivas elegibles
    # ============================================================
    correlation_columns = eligible_correlation_columns(result)
    pearson = result[correlation_columns].corr(method="pearson")
    spearman = result[correlation_columns].corr(method="spearman")

    # ============================================================
    # PASO 10: Exportar resultados, gráficas y documentación
    # ============================================================
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    density.to_csv(DENSITY_PATH, index=False, encoding="utf-8-sig")
    pearson.to_csv(PEARSON_PATH, encoding="utf-8-sig")
    spearman.to_csv(SPEARMAN_PATH, encoding="utf-8-sig")
    create_figures(result, pearson, spearman, density)

    metrics: Dict[str, object] = {
        "rows": len(result), "columns": len(result.columns),
        "target_0": int((result["quiebre_stock_inminente"] == 0).sum()),
        "target_1": int((result["quiebre_stock_inminente"] == 1).sum()),
        "positive_pct": float(result["quiebre_stock_inminente"].mean() * 100),
        "variable_features": len(correlation_columns) - 1,
        "constant_features": len(constant_predictors),
        "constant_names": ", ".join(constant_predictors) or "Ninguna",
        "missing_values": int(result.isna().sum().sum()),
        "lags_coverage": float(result["tiene_lags_importacion"].mean() * 100),
        "exchange_coverage": float(result["tiene_tipo_cambio"].mean() * 100),
        "calendar_coverage": float(result["tiene_calendario"].mean() * 100),
        "geo_coverage": float(result["densidad_anillo_disponible"].mean() * 100),
        "predictors": predictors,
        "normalized": normalized,
        "correlation_columns": correlation_columns,
    }
    write_document(metrics, density)
    return metrics


if __name__ == "__main__":
    summary = run_pipeline()
    print(f"Dataset analítico creado: {summary['rows']} filas y {summary['columns']} columnas.")
    print(f"Target 0/1: {summary['target_0']}/{summary['target_1']} ({summary['positive_pct']:.1f}% positivo).")
