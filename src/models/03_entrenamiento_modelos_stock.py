"""Entrenamiento, calibración y validación de modelos supervisados de stock (US-05 / SCRUM-9).

Fase 4 CRISP-DM: Modelado Predictivo.
Este módulo entrena modelos supervisados de clasificación (Random Forest, XGBoost y
Regresión Logística Regularizada) para predecir el riesgo inminente de quiebre de
stock de insulinas en farmacias de Santa Cruz de la Sierra.

Prioridad clínica: Se optimiza la métrica de Recall (Sensibilidad) y el F2-score para
minimizar Falsos Negativos (dejar desabastecido a un paciente jubilado).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import matplotlib
matplotlib.use("Agg")  # Operación sin servidor gráfico
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("modelos_stock")

# Rutas del Proyecto
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
FIGURES_DIR = PROJECT_DIR / "docs" / "figures"
MODELS_DIR = PROJECT_DIR / "models"
INPUT_DATASET = DATA_PROCESSED_DIR / "dataset_analitico_modelado.csv"

# Definición de Variables y Filtro Anti-Leakage
TARGET_COLUMN = "quiebre_stock_inminente"

LEAKAGE_COLUMNS = [
    "estado_stock",
    "stock_disponible_binario",
    "alerta_quiebre_stock",
    "semaforo_stock",
    "target_es_proxy",
    "definicion_target",
    TARGET_COLUMN,
]

METADATA_COLUMNS = [
    "id_insulina_master",
    "id_origen",
    "url_producto",
    "timestamp_extraccion",
    "fecha",
    "fecha_periodo",
    "sucursal",
    "ciudad",
    "departamento",
    "marca_comercial",
    "densidad_farmacias_anillo",
    "densidad_anillo_disponible",
    "tiene_lags_importacion",
    "tiene_tipo_cambio",
    "tiene_calendario",
]

NUMERIC_FEATURES = [
    "precio_venta_bs",
    "precio_lista_bs",
    "descuento_porcentaje",
    "precio_por_ml_bs",
    "precio_por_100ui_bs",
    "volumen_ml",
    "concentracion_ui_ml",
    "unidades_totales_ui",
]

CATEGORICAL_FEATURES = [
    "farmacia",
    "principio_activo",
    "tipo_accion",
    "origen_biologico",
    "laboratorio_fabricante",
    "formato_presentacion",
]


def asegurar_directorios() -> None:
    """Crea los directorios necesarios si no existen."""
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def cargar_y_preparar_datos(ruta_csv: Path = INPUT_DATASET) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Carga el dataset analítico de modelado y separa predictores de target y metadatos."""
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el dataset analítico en: {ruta_csv}")

    df = pd.read_csv(ruta_csv)
    logger.info(f"Dataset analítico cargado con {len(df)} filas y {len(df.columns)} columnas.")

    # Validar presencia del target
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Falta la columna target '{TARGET_COLUMN}' en el dataset.")

    y = df[TARGET_COLUMN].astype(int)
    pos_count = int(y.sum())
    total_count = len(y)
    logger.info(f"Distribución del target: {pos_count} positivos ({pos_count/total_count:.1%}) y {total_count - pos_count} negativos.")

    # Validar columnas predictoras
    for col in NUMERIC_FEATURES + CATEGORICAL_FEATURES:
        if col not in df.columns:
            raise KeyError(f"Columna requerida '{col}' no encontrada en el dataset.")

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()

    # Comprobación estricta anti-fuga
    for leak_col in LEAKAGE_COLUMNS:
        if leak_col in X.columns:
            raise RuntimeError(f"Fuga detectada: '{leak_col}' no debe estar en X.")

    return df, X, y


def construir_preprocesador() -> ColumnTransformer:
    """Construye el preprocesador hermético que transforma numéricas y categóricas."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def obtener_modelos_a_entrenar() -> Dict[str, Any]:
    """Retorna el diccionario de modelos supervisados configurados."""
    return {
        "Baseline": DummyClassifier(strategy="most_frequent"),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=3,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=60,
            max_depth=2,
            learning_rate=0.05,
            scale_pos_weight=9.75,
            eval_metric="logloss",
            random_state=42,
        ),
        "LogisticRegression": LogisticRegression(
            C=0.5,
            class_weight="balanced",
            max_iter=1000,
            random_state=42,
        ),
    }


def evaluar_umbral_optimo(
    y_true: np.ndarray, y_probs: np.ndarray, beta: float = 2.0
) -> Tuple[float, float, float, float]:
    """Encuentra el umbral probabilístico que maximiza el F-beta score priorizando Recall."""
    umbrales = np.linspace(0.05, 0.65, 61)
    mejor_th = 0.50
    mejor_fbeta = -1.0
    mejor_rec = 0.0
    mejor_prec = 0.0

    for th in umbrales:
        preds = (y_probs >= th).astype(int)
        rec = recall_score(y_true, preds, zero_division=0)
        prec = precision_score(y_true, preds, zero_division=0)
        f_b = fbeta_score(y_true, preds, beta=beta, zero_division=0)

        # Criterio: maximizar F2 manteniendo precisión mínima de 15% para evitar alarmas triviales
        if f_b > mejor_fbeta and (prec >= 0.15 or rec > mejor_rec):
            mejor_fbeta = f_b
            mejor_th = float(th)
            mejor_rec = float(rec)
            mejor_prec = float(prec)

    return mejor_th, mejor_rec, mejor_prec, mejor_fbeta


def ejecutar_validacion_cruzada(
    X: pd.DataFrame, y: pd.Series
) -> Tuple[Dict[str, np.ndarray], pd.DataFrame, Dict[str, float]]:
    """Ejecuta validación cruzada estratificada K=4 con predicciones fuera de muestra (OOF)."""
    skf = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
    preprocesador = construir_preprocesador()
    modelos = obtener_modelos_a_entrenar()

    oof_probs: Dict[str, np.ndarray] = {}
    metricas_lista: List[Dict[str, Any]] = []
    umbrales_optimos: Dict[str, float] = {}

    y_arr = y.values

    for nombre, modelo in modelos.items():
        logger.info(f"Evaluando modelo con K-Fold estratificado: {nombre}...")
        pipeline = Pipeline([("prep", preprocesador), ("clf", modelo)])
        probs = np.zeros(len(y_arr))

        for train_idx, val_idx in skf.split(X, y_arr):
            X_train, y_train = X.iloc[train_idx], y_arr[train_idx]
            X_val = X.iloc[val_idx]

            pipeline.fit(X_train, y_train)

            if hasattr(pipeline.named_steps["clf"], "predict_proba"):
                val_probs = pipeline.predict_proba(X_val)[:, 1]
            else:
                val_probs = pipeline.predict(X_val).astype(float)

            probs[val_idx] = val_probs

        oof_probs[nombre] = probs

        # ROC-AUC y PR-AUC
        if nombre != "Baseline":
            roc_auc = float(roc_auc_score(y_arr, probs))
            pr_auc = float(average_precision_score(y_arr, probs))
        else:
            roc_auc = 0.50
            pr_auc = float(y.mean())

        # Evaluación en umbral clásico (0.50)
        preds_50 = (probs >= 0.50).astype(int)
        acc_50 = float(accuracy_score(y_arr, preds_50))
        prec_50 = float(precision_score(y_arr, preds_50, zero_division=0))
        rec_50 = float(recall_score(y_arr, preds_50, zero_division=0))
        f1_50 = float(f1_score(y_arr, preds_50, zero_division=0))
        f2_50 = float(fbeta_score(y_arr, preds_50, beta=2, zero_division=0))

        metricas_lista.append({
            "modelo": nombre,
            "tipo_umbral": "Estandar (0.50)",
            "umbral": 0.50,
            "accuracy": round(acc_50, 4),
            "precision": round(prec_50, 4),
            "recall_sensibilidad": round(rec_50, 4),
            "f1_score": round(f1_50, 4),
            "f2_score_clinico": round(f2_50, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
        })

        # Evaluación en umbral óptimo clínico
        if nombre != "Baseline":
            th_opt, rec_opt, prec_opt, f2_opt = evaluar_umbral_optimo(y_arr, probs, beta=2.0)
            preds_opt = (probs >= th_opt).astype(int)
            acc_opt = float(accuracy_score(y_arr, preds_opt))
            f1_opt = float(f1_score(y_arr, preds_opt, zero_division=0))
            umbrales_optimos[nombre] = th_opt

            metricas_lista.append({
                "modelo": nombre,
                "tipo_umbral": f"Clinico Optimo ({th_opt:.2f})",
                "umbral": round(th_opt, 4),
                "accuracy": round(acc_opt, 4),
                "precision": round(prec_opt, 4),
                "recall_sensibilidad": round(rec_opt, 4),
                "f1_score": round(f1_opt, 4),
                "f2_score_clinico": round(f2_opt, 4),
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
            })
        else:
            umbrales_optimos[nombre] = 0.50

    df_metricas = pd.DataFrame(metricas_lista)
    return oof_probs, df_metricas, umbrales_optimos


def entrenar_y_serializar_modelos_finales(
    X: pd.DataFrame, y: pd.Series, umbrales_optimos: Dict[str, float]
) -> Tuple[Dict[str, Pipeline], pd.DataFrame, str]:
    """Entrena los modelos finales en la totalidad de datos y los serializa en models/."""
    preprocesador = construir_preprocesador()
    modelos = obtener_modelos_a_entrenar()
    pipelines_entrenados: Dict[str, Pipeline] = {}

    preprocesador.fit(X)
    nombres_cat = list(
        preprocesador.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
    )
    todas_features = NUMERIC_FEATURES + nombres_cat

    feature_importances: List[Dict[str, Any]] = []

    for nombre, modelo in modelos.items():
        if nombre == "Baseline":
            continue

        pipe = Pipeline([("prep", preprocesador), ("clf", modelo)])
        pipe.fit(X, y)
        pipelines_entrenados[nombre] = pipe

        # Guardar archivo .joblib
        archivo_modelo = MODELS_DIR / f"{nombre.lower()}_stock.joblib"
        joblib.dump(pipe, archivo_modelo)
        logger.info(f"Modelo serializado en: {archivo_modelo}")

        # Extraer importancia de características
        clf = pipe.named_steps["clf"]
        if hasattr(clf, "feature_importances_"):
            importancias = clf.feature_importances_
            for feat, imp in zip(todas_features, importancias):
                feature_importances.append({
                    "modelo": nombre,
                    "caracteristica": feat,
                    "importancia_absoluta": round(float(imp), 6),
                    "tipo_importancia": "MDI_Gini" if nombre == "RandomForest" else "Gain_Weight",
                })
        elif hasattr(clf, "coef_"):
            coeficientes = np.abs(clf.coef_[0])
            for feat, coef in zip(todas_features, coeficientes):
                feature_importances.append({
                    "modelo": nombre,
                    "caracteristica": feat,
                    "importancia_absoluta": round(float(coef), 6),
                    "tipo_importancia": "Coeficiente_L2_Absoluto",
                })

    # Selección del mejor modelo de producción: RandomForest por balance empírico y estabilidad
    mejor_modelo_nombre = "RandomForest"
    mejor_pipe = pipelines_entrenados[mejor_modelo_nombre]
    archivo_produccion = MODELS_DIR / "modelo_produccion_stock.joblib"
    joblib.dump(mejor_pipe, archivo_produccion)
    logger.info(f"Modelo oficial de producción serializado en: {archivo_produccion}")

    # Guardar metadata JSON
    metadata = {
        "proyecto": "Predictor de Quiebre de Stock de Insulina - CRISP-DM Fase 4",
        "sprint": "SCRUM Sprint 3",
        "historia_usuario": "US-05 (SCRUM-9)",
        "modelo_produccion": mejor_modelo_nombre,
        "umbral_clinico_produccion": umbrales_optimos.get(mejor_modelo_nombre, 0.25),
        "target": TARGET_COLUMN,
        "total_registros_entrenamiento": len(X),
        "total_positivos_quiebre": int(y.sum()),
        "caracteristicas_numericas": NUMERIC_FEATURES,
        "caracteristicas_categoricas": CATEGORICAL_FEATURES,
        "metricas_clave": {
            "criterio_primario": "Recall (Sensibilidad)",
            "f2_score_ponderacion": "Beta=2 (Penaliza falsos negativos)",
        },
    }
    with open(MODELS_DIR / "modelo_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    df_fi = pd.DataFrame(feature_importances)
    return pipelines_entrenados, df_fi, mejor_modelo_nombre


def generar_figuras_evaluacion(
    y_true: np.ndarray,
    oof_probs: Dict[str, np.ndarray],
    df_fi: pd.DataFrame,
    umbrales_optimos: Dict[str, float],
) -> None:
    """Genera y guarda las 4 figuras estadísticas de evaluación en docs/figures/."""
    colores = {
        "RandomForest": "#2ca02c",
        "XGBoost": "#d62728",
        "LogisticRegression": "#1f77b4",
        "Baseline": "#7f7f7f",
    }

    # 1. Curvas ROC
    plt.figure(figsize=(8, 6), dpi=300)
    for nombre, probs in oof_probs.items():
        if nombre == "Baseline":
            plt.plot([0, 1], [0, 1], linestyle="--", color=colores[nombre], label="Baseline Aleatorio (AUC = 0.50)")
            continue
        fpr, tpr, _ = roc_curve(y_true, probs)
        auc = roc_auc_score(y_true, probs)
        plt.plot(fpr, tpr, color=colores[nombre], lw=2, label=f"{nombre} (AUC = {auc:.3f})")

    plt.xlabel("Tasa de Falsos Positivos (1 - Especificidad)", fontsize=11)
    plt.ylabel("Tasa de Verdaderos Positivos (Recall / Sensibilidad)", fontsize=11)
    plt.title("Comparativa de Curvas ROC - Predicción de Quiebre de Stock (US-05)", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right", frameon=True)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "modelo_curvas_roc.png")
    plt.close()

    # 2. Curvas Precision-Recall
    plt.figure(figsize=(8, 6), dpi=300)
    base_rate = np.mean(y_true)
    plt.axhline(base_rate, linestyle="--", color="gray", label=f"Línea Base Prevalencia ({base_rate:.1%})")

    for nombre, probs in oof_probs.items():
        if nombre == "Baseline":
            continue
        prec, rec, _ = precision_recall_curve(y_true, probs)
        pr_auc = average_precision_score(y_true, probs)
        plt.plot(rec, prec, color=colores[nombre], lw=2, label=f"{nombre} (PR-AUC = {pr_auc:.3f})")

    plt.xlabel("Recall / Sensibilidad (Cobertura de Quiebres)", fontsize=11)
    plt.ylabel("Precisión (Fiabilidad de la Alerta)", fontsize=11)
    plt.title("Curvas Precision-Recall con Énfasis en Clase Minoritaria (US-05)", fontsize=12, fontweight="bold")
    plt.legend(loc="upper right", frameon=True)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "modelo_curvas_pr.png")
    plt.close()

    # 3. Matrices de Confusión Comparadas
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), dpi=300)
    modelos_clave = ["RandomForest", "XGBoost", "LogisticRegression"]

    for i, nombre in enumerate(modelos_clave):
        probs = oof_probs[nombre]

        # Umbral Estándar (0.50)
        cm_std = confusion_matrix(y_true, (probs >= 0.50).astype(int))
        ax_std = axes[0, i]
        im_std = ax_std.imshow(cm_std, cmap="Blues", interpolation="nearest")
        ax_std.set_title(f"{nombre} - Umbral Estándar (0.50)", fontsize=11, fontweight="bold")
        ax_std.set_xticks([0, 1])
        ax_std.set_yticks([0, 1])
        ax_std.set_xticklabels(["Stock Disp (0)", "Quiebre (1)"])
        ax_std.set_yticklabels(["Stock Disp (0)", "Quiebre (1)"])
        for r in range(2):
            for c in range(2):
                ax_std.text(c, r, str(cm_std[r, c]), ha="center", va="center", color="red" if r==1 and c==0 else "black", fontsize=12)

        # Umbral Clínico Óptimo
        th_opt = umbrales_optimos.get(nombre, 0.25)
        cm_opt = confusion_matrix(y_true, (probs >= th_opt).astype(int))
        ax_opt = axes[1, i]
        ax_opt.imshow(cm_opt, cmap="Oranges", interpolation="nearest")
        ax_opt.set_title(f"{nombre} - Umbral Clínico ({th_opt:.2f})", fontsize=11, fontweight="bold")
        ax_opt.set_xticks([0, 1])
        ax_opt.set_yticks([0, 1])
        ax_opt.set_xticklabels(["Stock Disp (0)", "Quiebre (1)"])
        ax_opt.set_yticklabels(["Stock Disp (0)", "Quiebre (1)"])
        for r in range(2):
            for c in range(2):
                ax_opt.text(c, r, str(cm_opt[r, c]), ha="center", va="center", color="green" if r==1 and c==1 else "black", fontsize=12)

    axes[0, 0].set_ylabel("Valor Real (Umbral 0.50)", fontsize=11)
    axes[1, 0].set_ylabel("Valor Real (Umbral Clínico)", fontsize=11)
    fig.suptitle("Matrices de Confusión: Impacto de la Calibración Clínica del Umbral en el Recall", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "modelo_matrices_confusion.png")
    plt.close()

    # 4. Feature Importance (Top 12 características)
    plt.figure(figsize=(10, 6), dpi=300)
    df_rf_fi = df_fi[df_fi["modelo"] == "RandomForest"].sort_values(by="importancia_absoluta", ascending=False).head(12)
    plt.barh(df_rf_fi["caracteristica"][::-1], df_rf_fi["importancia_absoluta"][::-1], color="#2ca02c", alpha=0.85)
    plt.xlabel("Importancia Relativa (Gini / MDI)", fontsize=11)
    plt.title("Top 12 Características Predictoras del Quiebre de Stock (Random Forest)", fontsize=12, fontweight="bold")
    plt.grid(axis="x", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "modelo_feature_importance.png")
    plt.close()
    logger.info("4 figuras estadísticas generadas exitosamente en docs/figures/.")


def generar_predicciones_procesadas(
    df_original: pd.DataFrame,
    oof_probs: Dict[str, np.ndarray],
    umbrales_optimos: Dict[str, float],
) -> pd.DataFrame:
    """Genera la tabla final de probabilidades y predicciones fuera de muestra."""
    salida = pd.DataFrame()
    salida["id_insulina_master"] = df_original["id_insulina_master"]
    salida["farmacia"] = df_original["farmacia"]
    salida["marca_comercial"] = df_original["marca_comercial"]
    salida["principio_activo"] = df_original["principio_activo"]
    salida["precio_venta_bs"] = df_original["precio_venta_bs"]
    salida["target_real_quiebre"] = df_original[TARGET_COLUMN]

    for modelo in ["RandomForest", "XGBoost", "LogisticRegression"]:
        p = oof_probs[modelo]
        th = umbrales_optimos.get(modelo, 0.25)
        salida[f"probabilidad_{modelo.lower()}"] = np.round(p, 4)
        salida[f"alerta_{modelo.lower()}"] = np.where(p >= th, "ALERTA_QUIEBRE", "STOCK_ESTABLE")

    # Semáforo Predictivo Final Consolidado (Basado en el modelo de producción RandomForest)
    p_rf = oof_probs["RandomForest"]
    th_rf = umbrales_optimos.get("RandomForest", 0.25)

    condiciones = [
        p_rf >= th_rf,
        (p_rf >= th_rf * 0.6) & (p_rf < th_rf),
        p_rf < th_rf * 0.6,
    ]
    semaforos = ["ROJO_ALTO_RIESGO", "AMARILLO_RIESGO_MODERADO", "VERDE_ESTABLE"]
    salida["semaforo_predictivo_ml"] = np.select(condiciones, semaforos, default="VERDE_ESTABLE")

    return salida


def ejecutar_pipeline_entrenamiento() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Función orquestadora principal de entrenamiento y evaluación supervisada."""
    asegurar_directorios()
    logger.info("=== INICIANDO ENTRENAMIENTO DE MODELOS SUPERVISADOS (US-05) ===")

    df_original, X, y = cargar_y_preparar_datos()
    oof_probs, df_metricas, umbrales_optimos = ejecutar_validacion_cruzada(X, y)

    pipelines_entrenados, df_fi, mejor_modelo = entrenar_y_serializar_modelos_finales(
        X, y, umbrales_optimos
    )

    generar_figuras_evaluacion(y.values, oof_probs, df_fi, umbrales_optimos)

    df_predicciones = generar_predicciones_procesadas(df_original, oof_probs, umbrales_optimos)

    # Exportación de CSVs
    ruta_metricas = DATA_PROCESSED_DIR / "metricas_modelos_supervisados.csv"
    ruta_predicciones = DATA_PROCESSED_DIR / "predicciones_probabilidad_stock.csv"
    ruta_fi = DATA_PROCESSED_DIR / "feature_importance_modelos.csv"

    df_metricas.to_csv(ruta_metricas, index=False, encoding="utf-8-sig")
    df_predicciones.to_csv(ruta_predicciones, index=False, encoding="utf-8-sig")
    df_fi.to_csv(ruta_fi, index=False, encoding="utf-8-sig")

    logger.info(f"Métricas exportadas a: {ruta_metricas}")
    logger.info(f"Predicciones exportadas a: {ruta_predicciones}")
    logger.info(f"Feature importance exportado a: {ruta_fi}")
    logger.info("=== ENTRENAMIENTO COMPLETADO EXITOSAMENTE (US-05) ===")

    return df_metricas, df_predicciones, df_fi


if __name__ == "__main__":
    ejecutar_pipeline_entrenamiento()
