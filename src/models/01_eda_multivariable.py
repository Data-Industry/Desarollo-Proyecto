"""Módulo de Análisis Exploratorio de Datos (EDA) y Auditoría de Calidad Multifuente (US-16 / SCRUM-20).

Fase CRISP-DM: Fase 2 - Comprensión de los Datos
Integra y audita de forma unificada:
1. Datos de disponibilidad y góndola retail consolidada (US-20, US-22, US-27).
2. Datos de importaciones aduaneras de insulina (NANDINA 3004.31.00.00, US-21).
3. Datos oficiales de tipo de cambio del Banco Central de Bolivia (US-28).
4. Fusión mensual y predictores de desfase temporal preparados (US-27).
5. Geolocalización de sucursales y cobertura por anillos urbanos (US-03).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib
matplotlib.use("Agg")  # Modo headless para ejecución en terminal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EDA-Multivariable")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.titlesize": 14,
})

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
DOCS_DIR = PROJECT_DIR / "docs"
FIGURES_DIR = DOCS_DIR / "figures"


def load_all_fused_datasets() -> Dict[str, pd.DataFrame]:
    """Carga todos los datasets maestros, consolidados y fusionados del proyecto."""
    paths = {
        "farmacias_master": PROCESSED_DIR / "insulinas_master.csv",
        "retail_consolidado": PROCESSED_DIR / "retail_stock_historico_consolidado.csv",
        "retail_resumen": PROCESSED_DIR / "retail_stock_mensual_resumen.csv",
        "importaciones_master": PROCESSED_DIR / "importaciones_insulina_bolivia.csv",
        "importaciones_resumen": PROCESSED_DIR / "importaciones_insulina_mensual_resumen.csv",
        "importaciones_scz": PROCESSED_DIR / "importaciones_santa_cruz_mensual.csv",
        "lags_preparados": PROCESSED_DIR / "importaciones_stock_lags_preparados.csv",
        "fusion_mensual": PROCESSED_DIR / "importaciones_stock_fusion_mensual.csv",
        "mapeo_catalogo": PROCESSED_DIR / "mapeo_productos_importacion_retail.csv",
        "farmacias_geo": PROCESSED_DIR / "farmacias_geolocalizadas.csv",
        "tipo_cambio_bcb": PROCESSED_DIR / "tipo_cambio_historico_bolivia.csv",
    }

    loaded = {}
    for key, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Archivo requerido no encontrado: {path}")
        loaded[key] = pd.read_csv(path)

    logger.info(
        f"11 Datasets multifuente cargados exitosamente: "
        f"Retail Master ({len(loaded['farmacias_master'])}), "
        f"Retail Consolidado ({len(loaded['retail_consolidado'])}), "
        f"Importaciones Master ({len(loaded['importaciones_master'])}), "
        f"Fusión Mensual US-27 ({len(loaded['fusion_mensual'])}), "
        f"Geolocalizadas US-03 ({len(loaded['farmacias_geo'])}), "
        f"TC BCB ({len(loaded['tipo_cambio_bcb'])})"
    )
    return loaded


def audit_multisource_data_quality(datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Realiza la auditoría de completitud, unicidad y detección de atípicos (IQR)."""
    logger.info("--- Ejecutando Auditoría Integral de Calidad de Datos ---")
    df_farm = datasets["farmacias_master"]
    df_imp = datasets["importaciones_master"]
    df_fusion = datasets["fusion_mensual"]
    df_geo = datasets["farmacias_geo"]

    nulls_farm = df_farm.isnull().sum()
    nulls_imp = df_imp.isnull().sum()
    nulls_fusion = df_fusion.isnull().sum()

    # Outliers en precios (IQR)
    q1_p = df_farm["precio_venta_bs"].quantile(0.25)
    q3_p = df_farm["precio_venta_bs"].quantile(0.75)
    iqr_p = q3_p - q1_p
    outliers_precio = df_farm[
        (df_farm["precio_venta_bs"] < (q1_p - 1.5 * iqr_p))
        | (df_farm["precio_venta_bs"] > (q3_p + 1.5 * iqr_p))
    ]

    # Outliers en costo CIF (USD/kg)
    q1_c = df_imp["costo_cif_kg_usd"].quantile(0.25)
    q3_c = df_imp["costo_cif_kg_usd"].quantile(0.75)
    iqr_c = q3_c - q1_c
    outliers_cif = df_imp[
        (df_imp["costo_cif_kg_usd"] < (q1_c - 1.5 * iqr_c))
        | (df_imp["costo_cif_kg_usd"] > (q3_c + 1.5 * iqr_c))
    ]

    quality_summary = {
        "retail_master_filas": len(df_farm),
        "retail_master_columnas": len(df_farm.columns),
        "retail_master_nulos_criticos": int((nulls_farm > 0).sum()),
        "retail_outliers_precio_iqr": len(outliers_precio),
        "retail_rango_precios_bs": [float(df_farm["precio_venta_bs"].min()), float(df_farm["precio_venta_bs"].max())],
        "importaciones_master_filas": len(df_imp),
        "importaciones_columnas": len(df_imp.columns),
        "importaciones_nulos_criticos": int((nulls_imp > 0).sum()),
        "importaciones_outliers_cif_iqr": len(outliers_cif),
        "importaciones_rango_cif_usd_kg": [float(df_imp["costo_cif_kg_usd"].min()), float(df_imp["costo_cif_kg_usd"].max())],
        "fusion_mensual_filas": len(df_fusion),
        "fusion_mensual_periodos": sorted(df_fusion["fecha_periodo"].unique().tolist()),
        "geolocalizacion_sucursales_total": len(df_geo),
        "geolocalizacion_anillos_asignados": int((df_geo["estado_anillo"] == "ASIGNADO").sum()),
        "tipo_cambio_bcb_periodos": len(datasets["tipo_cambio_bcb"]),
        "tipo_cambio_bcb_rango_2026": [
            float(datasets["tipo_cambio_bcb"][datasets["tipo_cambio_bcb"]["gestion"] == 2026]["tipo_cambio_bob_usd"].min()),
            float(datasets["tipo_cambio_bcb"][datasets["tipo_cambio_bcb"]["gestion"] == 2026]["tipo_cambio_bob_usd"].max())
        ]
    }

    json_path = PROCESSED_DIR / "eda_calidad_auditoria_completa.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(quality_summary, f, ensure_ascii=False, indent=2)

    logger.info(f"Auditoría de calidad exportada a {json_path.name}")
    return quality_summary


def generate_eda_figures(datasets: Dict[str, pd.DataFrame]) -> None:
    """Genera las 6 figuras analíticas del EDA integrando todas las fuentes procesadas."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    df_farm = datasets["farmacias_master"]
    df_imp = datasets["importaciones_master"]
    df_res = datasets["importaciones_resumen"]
    df_tc = datasets["tipo_cambio_bcb"]
    df_fusion = datasets["fusion_mensual"]
    df_geo = datasets["farmacias_geo"]
    df_lags = datasets["lags_preparados"]

    logger.info(f"Generando figuras estadísticas en {FIGURES_DIR}...")

    # -------------------------------------------------------------
    # Figura 1: Distribución de Precios de Venta y por 100 UI
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    order_action = df_farm.groupby("tipo_accion")["precio_venta_bs"].median().sort_values().index

    sns.boxplot(
        data=df_farm, x="tipo_accion", y="precio_venta_bs",
        order=order_action, ax=axes[0], hue="tipo_accion", palette="Blues_d", legend=False
    )
    axes[0].set_title("Distribución del Precio de Venta (Bs.) por Acción Farmacológica")
    axes[0].set_xlabel("Tipo de Acción")
    axes[0].set_ylabel("Precio al Público (Bs.)")
    axes[0].tick_params(axis="x", rotation=25)

    sns.boxplot(
        data=df_farm, x="tipo_accion", y="precio_por_100ui_bs",
        order=order_action, ax=axes[1], hue="tipo_accion", palette="Purples_d", legend=False
    )
    axes[1].set_title("Precio Normalizado por 100 UI (Bs.) por Acción Farmacológica")
    axes[1].set_xlabel("Tipo de Acción")
    axes[1].set_ylabel("Precio comparable por 100 UI (Bs.)")
    axes[1].tick_params(axis="x", rotation=25)

    plt.tight_layout()
    fig1_path = FIGURES_DIR / "eda_fig1_distribucion_precios_farmacias.png"
    plt.savefig(fig1_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figura 2: Evolución de Costo Aduanero CIF y Tipo de Cambio Oficial BCB
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(12, 5))
    periodos_str = df_res["fecha_periodo"]
    ticks_idx = range(0, len(periodos_str), 6)
    ticks_labels = [periodos_str[i] for i in ticks_idx]

    color1 = "tab:blue"
    ax1.set_xlabel("Periodo Mensual (2021 - 2026)")
    ax1.set_ylabel("Costo Promedio CIF / Kg (Bs.)", color=color1)
    line1 = ax1.plot(df_res.index, df_res["costo_promedio_cif_kg_bob"], color=color1, linewidth=2.2, label="Costo CIF/Kg en BOB (Oficial BCB)")
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_xticks(ticks_idx)
    ax1.set_xticklabels(ticks_labels, rotation=35)

    ax2 = ax1.twinx()
    color2 = "tab:red"
    ax2.set_ylabel("Tipo de Cambio Oficial BCB (BOB/USD)", color=color2)
    line2 = ax2.plot(df_res.index, df_res["tipo_cambio_promedio_bob_usd"], color=color2, linewidth=2.0, linestyle="--", label="Cotización Oficial BCB (BOB/USD)")
    ax2.tick_params(axis="y", labelcolor=color2)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="upper left")
    plt.title("Evolución de Costos CIF y Cotización Oficial del BCB (2021-2026)")
    plt.tight_layout()
    fig2_path = FIGURES_DIR / "eda_fig2_evolucion_costo_importacion_tc.png"
    plt.savefig(fig2_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figura 3: Comparativa de Cadenas Farmacéuticas (Precios y Disponibilidad)
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    order_farm = df_farm.groupby("farmacia")["precio_venta_bs"].median().sort_values().index

    sns.barplot(
        data=df_farm, x="farmacia", y="precio_venta_bs",
        order=order_farm, ax=axes[0], hue="farmacia", palette="viridis", errorbar=None, legend=False
    )
    axes[0].set_title("Precio Promedio de Insulinas por Cadena Farmacéutica")
    axes[0].set_xlabel("Cadena")
    axes[0].set_ylabel("Precio Promedio (Bs.)")
    for p in axes[0].patches:
        axes[0].annotate(f"{p.get_height():.1f} Bs",
                         (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                         ha="center", va="center", color="white", fontweight="bold")

    semaforo_cross = pd.crosstab(df_farm["farmacia"], df_farm["semaforo_stock"], normalize="index") * 100
    cols_order = [c for c in ["VERDE", "AMARILLO", "ROJO"] if c in semaforo_cross.columns]
    semaforo_cross = semaforo_cross[cols_order]
    color_map = {"VERDE": "#2ecc71", "AMARILLO": "#f1c40f", "ROJO": "#e74c3c"}
    colors = [color_map[c] for c in cols_order]
    semaforo_cross.plot(kind="bar", stacked=True, ax=axes[1], color=colors)
    axes[1].set_title("Disponibilidad en Góndola (%) por Cadena")
    axes[1].set_xlabel("Cadena")
    axes[1].set_ylabel("Porcentaje de Catálogo (%)")
    axes[1].legend(title="Semáforo Stock", bbox_to_anchor=(1.02, 1), loc="upper left")
    axes[1].tick_params(axis="x", rotation=0)

    plt.tight_layout()
    fig3_path = FIGURES_DIR / "eda_fig3_comparativa_cadenas_farmacias.png"
    plt.savefig(fig3_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figura 4: Participación de Importaciones y Variedad por Laboratorio
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    pais_vol = df_imp.groupby("pais_origen")["kilos_netos"].sum().sort_values(ascending=False)
    axes[0].pie(pais_vol, labels=pais_vol.index, autopct="%1.1f%%", startangle=140,
                colors=sns.color_palette("Set2", len(pais_vol)))
    axes[0].set_title("Participación Histórica de Volumen Importado por País")

    lab_counts = df_farm["laboratorio_fabricante"].value_counts()
    sns.barplot(x=lab_counts.values, y=lab_counts.index, ax=axes[1], hue=lab_counts.index, palette="rocket", legend=False)
    axes[1].set_title("Variedad de Medicamentos en Farmacias por Laboratorio")
    axes[1].set_xlabel("Presentaciones Activas (SKUs)")
    axes[1].set_ylabel("Laboratorio")

    plt.tight_layout()
    fig4_path = FIGURES_DIR / "eda_fig4_participacion_paises_origen.png"
    plt.savefig(fig4_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figura 5: Matriz de Correlación Multifuente (Macro + Lags Preparados)
    # -------------------------------------------------------------
    lags_sub = df_lags[[
        "total_kilos_netos", "total_valor_cif_usd", "total_valor_cif_bob",
        "kilos_netos_lag_1m", "kilos_netos_lag_2m", "kilos_netos_lag_3m",
        "alerta_quiebre_importacion_binaria"
    ]].dropna()

    corr_cols = {
        "total_kilos_netos": "Vol_Kg_t0",
        "total_valor_cif_usd": "CIF_USD_t0",
        "total_valor_cif_bob": "CIF_BOB_t0",
        "kilos_netos_lag_1m": "Lag_1m_Kg",
        "kilos_netos_lag_2m": "Lag_2m_Kg",
        "kilos_netos_lag_3m": "Lag_3m_Kg",
        "alerta_quiebre_importacion_binaria": "Alerta_Quiebre"
    }
    corr_df = lags_sub.rename(columns=corr_cols).corr().round(2)

    plt.figure(figsize=(9, 7))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", linewidths=0.5)
    plt.title("Matriz de Correlación Multifuente: Variables Macro y Lags Temporales Preparados")
    plt.tight_layout()
    fig5_path = FIGURES_DIR / "eda_fig5_matriz_correlacion_multifuente.png"
    plt.savefig(fig5_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figura 6: Cobertura Territorial de Farmacias por Anillos Urbanos (US-03)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    geo_assigned = df_geo[df_geo["estado_anillo"] == "ASIGNADO"].copy()
    geo_assigned["anillo_num"] = pd.to_numeric(geo_assigned["anillo_asignado"], errors="coerce")
    anillos_count = geo_assigned.groupby(["anillo_num", "farmacia"]).size().unstack(fill_value=0)

    anillos_count.plot(kind="bar", stacked=True, ax=ax, colormap="tab10")
    ax.set_title("Distribución Territorial de Sucursales Farmacéuticas por Anillo Urbano (Santa Cruz)")
    ax.set_xlabel("Anillo Urbano (1 al 8)")
    ax.set_ylabel("Cantidad de Sucursales")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Cadena Farmacéutica")

    plt.tight_layout()
    fig6_path = FIGURES_DIR / "eda_fig6_geolocalizacion_anillos_scz.png"
    plt.savefig(fig6_path, dpi=300)
    plt.close()

    logger.info("Las 6 figuras estadísticas fueron generadas exitosamente en docs/figures/.")


def generate_eda_statistical_reports(datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """Genera y exporta tablas analíticas normalizadas a data/processed/."""
    df_farm = datasets["farmacias_master"]
    df_imp = datasets["importaciones_master"]
    df_fusion = datasets["fusion_mensual"]
    df_geo = datasets["farmacias_geo"]

    # 1. Resumen por Cadena Farmacéutica
    rep_cadenas = df_farm.groupby("farmacia").agg(
        total_skus=("id_insulina_master", "count"),
        precio_min=("precio_venta_bs", "min"),
        precio_mediana=("precio_venta_bs", "median"),
        precio_promedio=("precio_venta_bs", "mean"),
        precio_max=("precio_venta_bs", "max"),
        descuento_promedio_pct=("descuento_porcentaje", "mean"),
        skus_con_descuento=("descuento_porcentaje", lambda x: int((x > 0).sum())),
        disponibilidad_stock_pct=("stock_disponible_binario", lambda x: round(x.mean() * 100, 1)),
    ).round(2).reset_index()

    # 2. Resumen por Principio Activo y Formato
    rep_farmaco = df_farm.groupby(["principio_activo", "tipo_accion", "formato_presentacion"]).agg(
        total_skus=("id_insulina_master", "count"),
        precio_min=("precio_venta_bs", "min"),
        precio_promedio=("precio_venta_bs", "mean"),
        precio_max=("precio_venta_bs", "max"),
        precio_por_100ui_promedio=("precio_por_100ui_bs", "mean"),
    ).round(2).reset_index()

    # 3. Resumen por País de Origen de Importación
    rep_paises = df_imp.groupby(["pais_origen", "codigo_iso_pais"]).agg(
        total_despachos=("id_importacion_master", "count"),
        total_kilos_netos=("kilos_netos", "sum"),
        total_cif_usd=("valor_cif_usd", "sum"),
        costo_cif_usd_kg_medio=("costo_cif_kg_usd", "mean"),
        costo_cif_bob_kg_medio=("costo_cif_kg_bob", "mean"),
        viales_totales_estimados=("viales_estimados_10ml", "sum"),
    ).round(2).reset_index()
    rep_paises.sort_values(by="total_kilos_netos", ascending=False, inplace=True)

    # 4. Dispersión de Precios entre Cadenas para productos idénticos
    rep_dispersion = df_farm.groupby(["marca_comercial", "formato_presentacion"]).agg(
        total_ofertas=("farmacia", "count"),
        cadenas_presentes=("farmacia", "nunique"),
        precio_min=("precio_venta_bs", "min"),
        precio_max=("precio_venta_bs", "max"),
        brecha_precio_bs=("precio_venta_bs", lambda x: round(x.max() - x.min(), 2)),
        brecha_porcentual_pct=(
            "precio_venta_bs",
            lambda x: round(((x.max() - x.min()) / x.min()) * 100, 1) if x.min() > 0 else 0.0,
        ),
    ).reset_index()
    rep_dispersion.sort_values(by="brecha_porcentual_pct", ascending=False, inplace=True)

    # 5. Métricas de la Fusión Importaciones-Stock (US-27)
    rep_fusion = df_fusion.groupby("fecha_periodo").agg(
        observaciones_retail=("productos_observados", "sum"),
        productos_disponibles=("productos_disponibles", "sum"),
        tasa_disponibilidad_media=("tasa_disponibilidad", "mean"),
        cif_usd_arribado=("valor_cif_usd_lag_0m", "first"),
        cif_usd_lag_1m=("valor_cif_usd_lag_1m", "first"),
        kilos_lag_0m=("kilos_netos_lag_0m", "first"),
        kilos_lag_1m=("kilos_netos_lag_1m", "first"),
        semaforo_upstream=("semaforo_abastecimiento_upstream", "first"),
    ).reset_index()

    # 6. Métricas de Cobertura Territorial por Anillos (US-03)
    rep_anillos = df_geo.groupby(["anillo_asignado", "estado_anillo"]).agg(
        sucursales_conteo=("id_sucursal", "count"),
        farmacias_presentes=("farmacia", "nunique"),
    ).reset_index()

    # Exportación
    rep_cadenas.to_csv(PROCESSED_DIR / "eda_metricas_resumen_farmacias.csv", index=False, encoding="utf-8-sig")
    rep_farmaco.to_csv(PROCESSED_DIR / "eda_metricas_por_principio_activo.csv", index=False, encoding="utf-8-sig")
    rep_paises.to_csv(PROCESSED_DIR / "eda_metricas_resumen_importaciones.csv", index=False, encoding="utf-8-sig")
    rep_dispersion.to_csv(PROCESSED_DIR / "eda_dispersion_marcas_cadenas.csv", index=False, encoding="utf-8-sig")
    rep_fusion.to_csv(PROCESSED_DIR / "eda_metricas_fusion_importaciones_stock.csv", index=False, encoding="utf-8-sig")
    rep_anillos.to_csv(PROCESSED_DIR / "eda_metricas_cobertura_anillos.csv", index=False, encoding="utf-8-sig")

    logger.info("Reportes estadísticos de EDA exportados exitosamente a data/processed/.")
    return {
        "cadenas": rep_cadenas,
        "farmacos": rep_farmaco,
        "paises": rep_paises,
        "dispersion": rep_dispersion,
        "fusion": rep_fusion,
        "anillos": rep_anillos,
    }


def run_multivariable_eda() -> Dict[str, Any]:
    """Orquesta la ejecución completa del EDA y auditoría de calidad de US-16."""
    logger.info("=== INICIANDO ANÁLISIS EXPLORATORIO DE DATOS MULTIVARIABLE (US-16) ===")
    datasets = load_all_fused_datasets()

    quality = audit_multisource_data_quality(datasets)
    generate_eda_figures(datasets)
    reports = generate_eda_statistical_reports(datasets)

    logger.info("=== PROCESO EDA Y AUDITORÍA DE CALIDAD COMPLETADO CON ÉXITO ===")
    return {"quality": quality, "reports": reports}


if __name__ == "__main__":
    results = run_multivariable_eda()
    print("\n--- RESUMEN DE DISPERSIÓN DE PRECIOS ENTRE FARMACIAS ---")
    print(results["reports"]["dispersion"].head(10).to_string(index=False))
    print("\n--- RESUMEN POR CADENA FARMACÉUTICA ---")
    print(results["reports"]["cadenas"].to_string(index=False))
    print("\n--- RESUMEN FUSIÓN IMPORTACIONES-STOCK (US-27) ---")
    print(results["reports"]["fusion"].to_string(index=False))
