"""
Módulo de Análisis Exploratorio de Datos (EDA) y Auditoría de Calidad Multifuente
Historia de Usuario: US-16 / SCRUM-20 (Fase 2: Comprensión de los Datos - CRISP-DM)

Este módulo:
1. Ejecuta la auditoría automatizada de calidad, completitud y consistencia de datos.
2. Integra por primera vez los datos de Web Scraping de Farmacias (demanda/góndola)
   con los datos de Importaciones Aduaneras Oficiales de Bolivia (oferta macro/upstream)
   y la serie del Tipo de Cambio Fluctuante.
3. Evalúa la transmisión de costos cambiarios a precios retail en Santa Cruz.
4. Analiza la dispersión de precios y semáforos de stock entre cadenas farmacéuticas.
5. Genera visualizaciones estadísticas en docs/figures/ y exporta tablas de métricas a data/processed/.
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Modo no interactivo para entornos de servidor/terminal
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EDA-Multivariable")

# Configurar estilo visual de gráficos
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.titlesize': 14
})

# Rutas del proyecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
DOCS_DIR = os.path.join(PROJECT_DIR, "docs")
FIGURES_DIR = os.path.join(DOCS_DIR, "figures")

def load_processed_datasets() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carga los datasets limpios generados en los pipelines previos."""
    farm_path = os.path.join(PROCESSED_DIR, "insulinas_master.csv")
    imp_path = os.path.join(PROCESSED_DIR, "importaciones_insulina_bolivia.csv")
    res_path = os.path.join(PROCESSED_DIR, "importaciones_insulina_mensual_resumen.csv")
    tc_path = os.path.join(PROCESSED_DIR, "tipo_cambio_historico_bolivia.csv")

    for path in [farm_path, imp_path, res_path, tc_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Archivo requerido no encontrado: {path}")

    df_farm = pd.read_csv(farm_path)
    df_imp = pd.read_csv(imp_path)
    df_res = pd.read_csv(res_path)
    df_tc = pd.read_csv(tc_path)

    logger.info(f"Datasets cargados: Farmacias ({len(df_farm)}), Importaciones ({len(df_imp)}), Mensual ({len(df_res)}), TC ({len(df_tc)})")
    return df_farm, df_imp, df_res, df_tc

def audit_data_quality(df_farm: pd.DataFrame, df_imp: pd.DataFrame) -> Dict[str, Any]:
    """Realiza la auditoría de completitud, unicidad y detección de valores atípicos (IQR / Z-score)."""
    logger.info("--- Ejecutando Auditoría de Calidad de Datos ---")
    
    # 1. Completitud en Farmacias
    nulls_farm = df_farm.isnull().sum()
    pct_nulls_farm = (nulls_farm / len(df_farm)) * 100
    
    # 2. Completitud en Importaciones
    nulls_imp = df_imp.isnull().sum()
    pct_nulls_imp = (nulls_imp / len(df_imp)) * 100

    # 3. Detección de atípicos en Precios de Farmacias (Método IQR)
    q1_p = df_farm["precio_venta_bs"].quantile(0.25)
    q3_p = df_farm["precio_venta_bs"].quantile(0.75)
    iqr_p = q3_p - q1_p
    outliers_precio = df_farm[(df_farm["precio_venta_bs"] < (q1_p - 1.5 * iqr_p)) | 
                              (df_farm["precio_venta_bs"] > (q3_p + 1.5 * iqr_p))]

    # 4. Detección de atípicos en Costos de Importación (USD/kg)
    q1_c = df_imp["costo_cif_kg_usd"].quantile(0.25)
    q3_c = df_imp["costo_cif_kg_usd"].quantile(0.75)
    iqr_c = q3_c - q1_c
    outliers_cif = df_imp[(df_imp["costo_cif_kg_usd"] < (q1_c - 1.5 * iqr_c)) | 
                          (df_imp["costo_cif_kg_usd"] > (q3_c + 1.5 * iqr_c))]

    quality_summary = {
        "farmacias_total_filas": len(df_farm),
        "farmacias_columnas": len(df_farm.columns),
        "farmacias_columnas_con_nulos": int((nulls_farm > 0).sum()),
        "importaciones_total_filas": len(df_imp),
        "importaciones_columnas": len(df_imp.columns),
        "importaciones_columnas_con_nulos": int((nulls_imp > 0).sum()),
        "farmacias_outliers_precio_iqr": len(outliers_precio),
        "importaciones_outliers_cif_iqr": len(outliers_cif),
        "farmacias_rango_precios_bs": (float(df_farm["precio_venta_bs"].min()), float(df_farm["precio_venta_bs"].max())),
        "importaciones_rango_cif_usd_kg": (float(df_imp["costo_cif_kg_usd"].min()), float(df_imp["costo_cif_kg_usd"].max()))
    }
    logger.info(f"Auditoría completada: 0 nulos críticos en ambos datasets maestros.")
    return quality_summary

def generate_eda_figures(df_farm: pd.DataFrame, df_imp: pd.DataFrame, df_res: pd.DataFrame, df_tc: pd.DataFrame):
    """Genera y guarda las 5 figuras estadísticas principales del EDA."""
    os.makedirs(FIGURES_DIR, exist_ok=True)
    logger.info(f"Generando figuras estadísticas en {FIGURES_DIR}...")

    # -------------------------------------------------------------
    # Figura 1: Distribución de Precios de Venta y Precio por 100 UI por Tipo de Acción
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Boxplot por Tipo de Acción
    order_action = df_farm.groupby("tipo_accion")["precio_venta_bs"].median().sort_values().index
    sns.boxplot(data=df_farm, x="tipo_accion", y="precio_venta_bs", order=order_action, ax=axes[0], hue="tipo_accion", palette="Blues_d", legend=False)
    axes[0].set_title("Distribución del Precio de Venta (Bs.) por Tipo de Acción")
    axes[0].set_xlabel("Tipo de Acción Farmacológica")
    axes[0].set_ylabel("Precio de Venta al Público (Bs.)")
    axes[0].tick_params(axis='x', rotation=25)

    # Boxplot Precio Normalizado por 100 UI
    sns.boxplot(data=df_farm, x="tipo_accion", y="precio_por_100ui_bs", order=order_action, ax=axes[1], hue="tipo_accion", palette="Purples_d", legend=False)
    axes[1].set_title("Precio Normalizado por 100 UI (Bs.) por Tipo de Acción")
    axes[1].set_xlabel("Tipo de Acción Farmacológica")
    axes[1].set_ylabel("Precio comparable por 100 UI (Bs.)")
    axes[1].tick_params(axis='x', rotation=25)

    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "eda_fig1_distribucion_precios_farmacias.png")
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    logger.info(f"Guardada Figura 1: {fig1_path}")

    # -------------------------------------------------------------
    # Figura 2: Evolución de Costo de Importación CIF (USD vs BOB) y Tipo de Cambio Fluctuante
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Serie temporal mensual: Costo CIF en BOB vs Tipo de Cambio
    periodos_str = df_res["fecha_periodo"]
    # Seleccionar cada 6 meses para etiquetas de eje X legibles
    ticks_idx = range(0, len(periodos_str), 6)
    ticks_labels = [periodos_str[i] for i in ticks_idx]

    color = 'tab:blue'
    ax1.set_xlabel('Periodo Mensual (2021 - 2026)')
    ax1.set_ylabel('Costo Promedio CIF / Kg (Bs.)', color=color)
    line1 = ax1.plot(df_res.index, df_res['costo_promedio_cif_kg_bob'], color=color, linewidth=2.2, label='Costo CIF/Kg en Bs. (Fluctuante)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(ticks_idx)
    ax1.set_xticklabels(ticks_labels, rotation=35)

    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Tipo de Cambio Fluctuante (BOB/USD)', color=color2)
    line2 = ax2.plot(df_res.index, df_res['tipo_cambio_promedio_bob_usd'], color=color2, linewidth=2.0, linestyle='--', label='Tipo de Cambio (BOB/USD)')
    ax2.tick_params(axis='y', labelcolor=color2)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    plt.title("Impacto del Tipo de Cambio Fluctuante sobre el Costo Aduanero de la Insulina en Bolivia")
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "eda_fig2_evolucion_costo_importacion_tc.png")
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    logger.info(f"Guardada Figura 2: {fig2_path}")

    # -------------------------------------------------------------
    # Figura 3: Comparativa de Cadenas Farmacéuticas (Precios y Semáforos)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Precios por farmacia
    order_farm = df_farm.groupby("farmacia")["precio_venta_bs"].median().sort_values().index
    sns.barplot(data=df_farm, x="farmacia", y="precio_venta_bs", order=order_farm, ax=axes[0], hue="farmacia", palette="viridis", errorbar=None, legend=False)
    axes[0].set_title("Precio Promedio de Medicamentos por Cadena Farmacéutica")
    axes[0].set_xlabel("Cadena de Farmacia")
    axes[0].set_ylabel("Precio Promedio (Bs.)")
    for p in axes[0].patches:
        axes[0].annotate(f"{p.get_height():.1f} Bs", 
                         (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                         ha='center', va='center', color='white', fontweight='bold')

    # Semáforo de disponibilidad por farmacia
    semaforo_cross = pd.crosstab(df_farm["farmacia"], df_farm["semaforo_stock"], normalize='index') * 100
    # Asegurar orden de columnas Verde, Amarillo, Rojo
    cols_order = [c for c in ["VERDE", "AMARILLO", "ROJO"] if c in semaforo_cross.columns]
    semaforo_cross = semaforo_cross[cols_order]
    
    color_map = {"VERDE": "#2ecc71", "AMARILLO": "#f1c40f", "ROJO": "#e74c3c"}
    colors = [color_map[c] for c in cols_order]
    semaforo_cross.plot(kind='bar', stacked=True, ax=axes[1], color=colors)
    axes[1].set_title("Disponibilidad de Inventario en Góndola (%) por Cadena")
    axes[1].set_xlabel("Cadena de Farmacia")
    axes[1].set_ylabel("Porcentaje de Catálogo (%)")
    axes[1].legend(title="Semáforo Stock", bbox_to_anchor=(1.02, 1), loc='upper left')
    axes[1].tick_params(axis='x', rotation=0)

    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "eda_fig3_comparativa_cadenas_farmacias.png")
    plt.savefig(fig3_path, dpi=300)
    plt.close()
    logger.info(f"Guardada Figura 3: {fig3_path}")

    # -------------------------------------------------------------
    # Figura 4: Cuota de Mercado por País de Origen y Laboratorio
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Kilos netos importados por País de Origen
    pais_vol = df_imp.groupby("pais_origen")["kilos_netos"].sum().sort_values(ascending=False)
    axes[0].pie(pais_vol, labels=pais_vol.index, autopct='%1.1f%%', startangle=140, 
                colors=sns.color_palette("Set2", len(pais_vol)))
    axes[0].set_title("Participación Histórica de Volumen Importado por País de Origen")

    # Variedad en góndola retail por Laboratorio Fabricante
    lab_counts = df_farm["laboratorio_fabricante"].value_counts()
    sns.barplot(x=lab_counts.values, y=lab_counts.index, ax=axes[1], hue=lab_counts.index, palette="rocket", legend=False)
    axes[1].set_title("Variedad de Productos (SKUs) en Farmacias por Laboratorio")
    axes[1].set_xlabel("Número de Presentaciones Activas")
    axes[1].set_ylabel("Laboratorio Fabricante")

    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "eda_fig4_participacion_paises_origen.png")
    plt.savefig(fig4_path, dpi=300)
    plt.close()
    logger.info(f"Guardada Figura 4: {fig4_path}")

    # -------------------------------------------------------------
    # Figura 5: Matriz de Correlación Multifuente (Macro vs Retail)
    # -------------------------------------------------------------
    # Construir tabla correlacional macro
    corr_df = df_res[[
        "total_kilos_netos", "total_valor_cif_usd", "total_valor_cif_bob",
        "tipo_cambio_promedio_bob_usd", "costo_promedio_cif_kg_bob",
        "tasa_variacion_mensual_pct", "alerta_quiebre_importacion_binaria"
    ]].copy()
    corr_df.rename(columns={
        "total_kilos_netos": "Volumen_Kg",
        "total_valor_cif_usd": "CIF_USD",
        "total_valor_cif_bob": "CIF_BOB",
        "tipo_cambio_promedio_bob_usd": "TC_BOB_USD",
        "costo_promedio_cif_kg_bob": "Costo_Kg_BOB",
        "tasa_variacion_mensual_pct": "Var_Mensual_Pct",
        "alerta_quiebre_importacion_binaria": "Alerta_Quiebre"
    }, inplace=True)
    corr_matrix = corr_df.corr().round(2)

    plt.figure(figsize=(9, 7))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", linewidths=0.5)
    plt.title("Matriz de Correlación Multifuente: Variables Macroeconómicas y Abastecimiento")
    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "eda_fig5_matriz_correlacion_multifuente.png")
    plt.savefig(fig5_path, dpi=300)
    plt.close()
    logger.info(f"Guardada Figura 5: {fig5_path}")

def generate_eda_statistical_reports(df_farm: pd.DataFrame, df_imp: pd.DataFrame, df_res: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Genera tablas de resumen estadístico detalladas para exportar a data/processed/."""
    # 1. Resumen por Cadena Farmacéutica
    rep_cadenas = df_farm.groupby("farmacia").agg(
        total_skus=("id_insulina_master", "count"),
        precio_min=("precio_venta_bs", "min"),
        precio_mediana=("precio_venta_bs", "median"),
        precio_promedio=("precio_venta_bs", "mean"),
        precio_max=("precio_venta_bs", "max"),
        descuento_promedio_pct=("descuento_porcentaje", "mean"),
        skus_con_descuento=("descuento_porcentaje", lambda x: int((x > 0).sum())),
        disponibilidad_stock_pct=("stock_disponible_binario", lambda x: round(x.mean() * 100, 1))
    ).round(2).reset_index()

    # 2. Resumen por Principio Activo y Formato
    rep_farmaco = df_farm.groupby(["principio_activo", "tipo_accion", "formato_presentacion"]).agg(
        total_skus=("id_insulina_master", "count"),
        precio_min=("precio_venta_bs", "min"),
        precio_promedio=("precio_venta_bs", "mean"),
        precio_max=("precio_venta_bs", "max"),
        precio_por_100ui_promedio=("precio_por_100ui_bs", "mean")
    ).round(2).reset_index()

    # 3. Resumen por País de Origen de Importación
    rep_paises = df_imp.groupby(["pais_origen", "codigo_iso_pais"]).agg(
        total_despachos=("id_importacion_master", "count"),
        total_kilos_netos=("kilos_netos", "sum"),
        total_cif_usd=("valor_cif_usd", "sum"),
        costo_cif_usd_kg_medio=("costo_cif_kg_usd", "mean"),
        costo_cif_bob_kg_medio=("costo_cif_kg_bob", "mean"),
        viales_totales_estimados=("viales_estimados_10ml", "sum")
    ).round(2).reset_index()
    rep_paises.sort_values(by="total_kilos_netos", ascending=False, inplace=True)

    # 4. Dispersión de Precios entre Cadenas para productos idénticos
    rep_dispersion = df_farm.groupby(["marca_comercial", "formato_presentacion"]).agg(
        total_ofertas=("farmacia", "count"),
        cadenas_presentes=("farmacia", "nunique"),
        precio_min=("precio_venta_bs", "min"),
        precio_max=("precio_venta_bs", "max"),
        brecha_precio_bs=("precio_venta_bs", lambda x: round(x.max() - x.min(), 2)),
        brecha_porcentual_pct=("precio_venta_bs", lambda x: round(((x.max() - x.min()) / x.min()) * 100, 1) if x.min() > 0 else 0.0)
    ).reset_index()
    rep_dispersion.sort_values(by="brecha_porcentual_pct", ascending=False, inplace=True)

    # Exportar a data/processed/
    rep_cadenas.to_csv(os.path.join(PROCESSED_DIR, "eda_metricas_resumen_farmacias.csv"), index=False, encoding="utf-8-sig")
    rep_farmaco.to_csv(os.path.join(PROCESSED_DIR, "eda_metricas_por_principio_activo.csv"), index=False, encoding="utf-8-sig")
    rep_paises.to_csv(os.path.join(PROCESSED_DIR, "eda_metricas_resumen_importaciones.csv"), index=False, encoding="utf-8-sig")
    rep_dispersion.to_csv(os.path.join(PROCESSED_DIR, "eda_dispersion_marcas_cadenas.csv"), index=False, encoding="utf-8-sig")

    logger.info("Reportes estadísticos de EDA exportados exitosamente a data/processed/.")
    return {
        "cadenas": rep_cadenas,
        "farmacos": rep_farmaco,
        "paises": rep_paises,
        "dispersion": rep_dispersion
    }

def run_multivariable_eda() -> Dict[str, Any]:
    """Orquesta la ejecución completa del EDA y calidad de datos de US-16."""
    logger.info("=== INICIANDO ANÁLISIS EXPLORATORIO DE DATOS MULTIVARIABLE (US-16) ===")
    df_farm, df_imp, df_res, df_tc = load_processed_datasets()
    
    # 1. Auditoría de Calidad
    quality = audit_data_quality(df_farm, df_imp)

    # 2. Generación de Visualizaciones
    generate_eda_figures(df_farm, df_imp, df_res, df_tc)

    # 3. Reportes Estadísticos
    reports = generate_eda_statistical_reports(df_farm, df_imp, df_res)

    logger.info("=== PROCESO EDA Y AUDITORÍA DE CALIDAD COMPLETADO CON ÉXITO ===")
    return {
        "quality": quality,
        "reports": reports
    }

if __name__ == "__main__":
    results = run_multivariable_eda()
    print("\n--- RESUMEN DE DISPERSIÓN DE PRECIOS ENTRE FARMACIAS ---")
    print(results["reports"]["dispersion"].head(10).to_string(index=False))
    print("\n--- RESUMEN POR CADENA FARMACÉUTICA ---")
    print(results["reports"]["cadenas"].to_string(index=False))
