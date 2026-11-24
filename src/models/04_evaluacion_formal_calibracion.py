"""Evaluación formal anidada y calibración de modelos de stock (SCRUM-38 / US-41).

Este módulo es deliberadamente independiente del entrenamiento productivo. Lee el
dataset analítico actual, instancia modelos desde código y escribe únicamente
artefactos de evaluación con prefijo/alcance SCRUM-38. Nunca carga ni serializa los
``.joblib`` de producción.

El target evaluado es un proxy del estado de stock observado en el mismo corte, no
un quiebre futuro. La validación anidada impide que el outer-validation participe
en preprocesamiento, calibración o selección de threshold.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    fbeta_score,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:  # XGBoost es opcional por requisito de la historia.
    import xgboost
    from xgboost import XGBClassifier

    XGBOOST_AVAILABLE = True
    XGBOOST_IMPORT_ERROR = ""
    XGBOOST_VERSION = xgboost.__version__
except Exception as exc:  # pragma: no cover - depende del entorno.
    XGBClassifier = None  # type: ignore[assignment]
    XGBOOST_AVAILABLE = False
    XGBOOST_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
    XGBOOST_VERSION = "NO_DISPONIBLE"


PROJECT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_DIR / "data" / "processed" / "dataset_analitico_modelado.csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
FIGURES_DIR = PROJECT_DIR / "docs" / "figures"
DOCUMENT_PATH = PROJECT_DIR / "docs" / "20_evaluacion_formal_calibracion_scrum38.md"

TARGET_COLUMN = "quiebre_stock_inminente"
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
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
LEAKAGE_COLUMNS = {
    TARGET_COLUMN,
    "estado_stock",
    "stock_disponible_binario",
    "alerta_quiebre_stock",
    "semaforo_stock",
    "target_es_proxy",
    "definicion_target",
}

DEFAULT_OUTER_SEEDS = (42, 123, 2026)
DEFAULT_ALERT_LIMIT = 0.80
DEFAULT_RECALL_TARGET = 0.90
DEFAULT_THRESHOLDS = tuple(np.round(np.arange(0.01, 1.00, 0.01), 2))
COST_RATIOS = (2, 5, 10)
CALIBRATION_VARIANTS = ("sin_calibrar", "sigmoid", "isotonic_exploratorio")

OUTPUT_FILENAMES = {
    "fold": "evaluacion_cv_por_fold.csv",
    "summary": "evaluacion_cv_resumen.csv",
    "predictions": "predicciones_oof_calibradas.csv",
    "calibration": "metricas_calibracion_probabilidades.csv",
    "thresholds": "curva_threshold_costos.csv",
    "confusion": "matrices_confusion_formales.csv",
}

FIGURE_FILENAMES = (
    "scrum38_roc_cv.png",
    "scrum38_pr_cv.png",
    "scrum38_calibracion.png",
    "scrum38_matrices_confusion.png",
    "scrum38_recall_precision_threshold.png",
    "scrum38_costos_threshold.png",
    "scrum38_estabilidad_folds.png",
)


@dataclass(frozen=True)
class EvaluationConfig:
    """Configuración reproducible de la evaluación."""

    outer_seeds: Tuple[int, ...] = DEFAULT_OUTER_SEEDS
    outer_splits: int = 4
    inner_splits: int = 3
    recall_target: float = DEFAULT_RECALL_TARGET
    alert_limit: float = DEFAULT_ALERT_LIMIT
    thresholds: Tuple[float, ...] = DEFAULT_THRESHOLDS
    cost_fn: int = 5
    cost_fp: int = 1


@dataclass
class EvaluationResults:
    fold: pd.DataFrame
    summary: pd.DataFrame
    predictions: pd.DataFrame
    calibration: pd.DataFrame
    thresholds: pd.DataFrame
    confusion: pd.DataFrame
    metadata: Dict[str, Any]


class AdaptiveXGBClassifier(ClassifierMixin, BaseEstimator):
    """XGBoost que recalcula ``scale_pos_weight`` en cada llamada a ``fit``."""

    def __init__(
        self,
        n_estimators: int = 60,
        max_depth: int = 2,
        learning_rate: float = 0.05,
        eval_metric: str = "logloss",
        random_state: int = 42,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.eval_metric = eval_metric
        self.random_state = random_state

    def fit(self, X: Any, y: Sequence[int]) -> "AdaptiveXGBClassifier":
        if not XGBOOST_AVAILABLE or XGBClassifier is None:
            raise RuntimeError(f"XGBoost no disponible: {XGBOOST_IMPORT_ERROR}")
        y_array = np.asarray(y, dtype=int)
        positives = int(y_array.sum())
        negatives = int(len(y_array) - positives)
        if positives == 0 or negatives == 0:
            raise ValueError("XGBoost requiere ambas clases en el fold de entrenamiento.")
        self.scale_pos_weight_ = negatives / positives
        self.estimator_ = XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            scale_pos_weight=self.scale_pos_weight_,
            eval_metric=self.eval_metric,
            objective="binary:logistic",
            random_state=self.random_state,
            n_jobs=1,
        )
        self.estimator_.fit(X, y_array)
        self.classes_ = np.asarray(self.estimator_.classes_)
        self.n_features_in_ = getattr(self.estimator_, "n_features_in_", None)
        return self

    def predict_proba(self, X: Any) -> np.ndarray:
        return self.estimator_.predict_proba(X)

    def predict(self, X: Any) -> np.ndarray:
        return self.estimator_.predict(X)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def environment_metadata(dataset_path: Path, config: EvaluationConfig) -> Dict[str, Any]:
    return {
        "timestamp_evaluacion_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(dataset_path.relative_to(PROJECT_DIR)),
        "dataset_sha256": sha256_file(dataset_path),
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
        "joblib_version": joblib.__version__,
        "xgboost_version": XGBOOST_VERSION,
        "random_seeds": json.dumps(list(config.outer_seeds)),
        "outer_splits": config.outer_splits,
        "inner_splits": config.inner_splits,
        "recall_objetivo": config.recall_target,
        "limite_alertas_tecnico_configurable": config.alert_limit,
        "penalizacion_tecnica_fp": config.cost_fp,
        "penalizacion_tecnica_fn": config.cost_fn,
        "descripcion_costos": "penalización técnica relativa para evaluación; no es costo clínico, económico ni médico real",
    }


def load_dataset(path: Path = DATASET_PATH) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    data = pd.read_csv(path)
    missing = set(FEATURES + [TARGET_COLUMN]) - set(data.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")
    y = data[TARGET_COLUMN].astype(int)
    if set(y.unique()) != {0, 1}:
        raise ValueError("El target debe contener exactamente las clases 0 y 1.")
    if data[FEATURES].isna().any().any():
        raise ValueError("Las features del modelo contienen valores faltantes.")
    if not LEAKAGE_COLUMNS.isdisjoint(FEATURES):
        raise RuntimeError("La selección de features contiene fuga directa del target.")
    return data, data[FEATURES].copy(), y


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def available_model_status() -> Dict[str, Tuple[str, str]]:
    status = {
        "Dummy": ("DISPONIBLE", ""),
        "RandomForest": ("DISPONIBLE", ""),
        "LogisticRegression": ("DISPONIBLE", ""),
    }
    status["XGBoost"] = (
        ("DISPONIBLE", "")
        if XGBOOST_AVAILABLE
        else ("NO_DISPONIBLE_ENTORNO", XGBOOST_IMPORT_ERROR)
    )
    return status


def build_base_model(model_name: str, random_state: int) -> BaseEstimator:
    if model_name == "Dummy":
        return DummyClassifier(strategy="most_frequent")
    if model_name == "RandomForest":
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=3,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=1,
        )
    if model_name == "LogisticRegression":
        return LogisticRegression(
            C=0.5,
            class_weight="balanced",
            max_iter=1000,
            random_state=random_state,
        )
    if model_name == "XGBoost":
        return AdaptiveXGBClassifier(random_state=random_state)
    raise KeyError(f"Modelo desconocido: {model_name}")


def build_estimator(
    model_name: str,
    calibration: str,
    random_state: int,
    calibration_splits: int,
) -> BaseEstimator:
    base_pipeline = Pipeline(
        [("prep", build_preprocessor()), ("clf", build_base_model(model_name, random_state))]
    )
    if calibration == "sin_calibrar":
        return base_pipeline
    method = "sigmoid" if calibration == "sigmoid" else "isotonic"
    calibration_cv = StratifiedKFold(
        n_splits=calibration_splits, shuffle=True, random_state=random_state + 17
    )
    return CalibratedClassifierCV(
        estimator=base_pipeline,
        method=method,
        cv=calibration_cv,
        ensemble=True,
    )


def validate_fold_boundaries(
    outer_train_indices: Iterable[int],
    outer_validation_indices: Iterable[int],
    threshold_indices: Iterable[int],
    calibration_indices: Iterable[int],
) -> None:
    """Bloquea cualquier participación del outer-validation en ajuste/selección."""

    outer_train = set(map(int, outer_train_indices))
    outer_validation = set(map(int, outer_validation_indices))
    threshold_set = set(map(int, threshold_indices))
    calibration_set = set(map(int, calibration_indices))
    if outer_train & outer_validation:
        raise RuntimeError("Outer-train y outer-validation se superponen.")
    if not threshold_set.issubset(outer_train):
        raise RuntimeError("La selección de threshold contiene índices fuera de outer-train.")
    if not calibration_set.issubset(outer_train):
        raise RuntimeError("La calibración contiene índices fuera de outer-train.")
    if outer_validation & (threshold_set | calibration_set):
        raise RuntimeError("Fuga: outer-validation participó en calibración o threshold.")


def safe_classification_metrics(
    y_true: Sequence[int], probabilities: Sequence[float], threshold: float
) -> Dict[str, Any]:
    y_array = np.asarray(y_true, dtype=int)
    probs = np.clip(np.asarray(probabilities, dtype=float), 1e-12, 1 - 1e-12)
    predictions = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_array, predictions, labels=[0, 1]).ravel()
    negative_total = tn + fp
    specificity = tn / negative_total if negative_total else np.nan
    fpr = fp / negative_total if negative_total else np.nan
    result: Dict[str, Any] = {
        "accuracy": accuracy_score(y_array, predictions),
        "precision": precision_score(y_array, predictions, zero_division=0),
        "recall": recall_score(y_array, predictions, zero_division=0),
        "f1": f1_score(y_array, predictions, zero_division=0),
        "f2": fbeta_score(y_array, predictions, beta=2, zero_division=0),
        "specificity": specificity,
        "fpr": fpr,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "proporcion_alertada": float(predictions.mean()),
        "brier_score": brier_score_loss(y_array, probs),
        "log_loss": log_loss(y_array, probs, labels=[0, 1]),
    }
    if len(np.unique(y_array)) == 2:
        result["roc_auc"] = roc_auc_score(y_array, probs)
        result["pr_auc_average_precision"] = average_precision_score(y_array, probs)
    else:
        result["roc_auc"] = np.nan
        result["pr_auc_average_precision"] = np.nan
    return result


def evaluate_threshold_grid(
    y_true: Sequence[int],
    probabilities: Sequence[float],
    thresholds: Sequence[float],
    recall_target: float,
    alert_limit: float,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    sensitivity_limits = (0.60, 0.70, 0.80, 0.90, 1.00)
    for threshold in thresholds:
        metrics = safe_classification_metrics(y_true, probabilities, float(threshold))
        row = {"threshold": float(threshold), **metrics}
        for ratio in COST_RATIOS:
            row[f"costo_relativo_fn{ratio}_fp1"] = ratio * metrics["fn"] + metrics["fp"]
        row["alcanza_recall_objetivo"] = bool(metrics["recall"] >= recall_target)
        row["politica_degenerada"] = bool(
            row["alcanza_recall_objetivo"]
            and metrics["proporcion_alertada"] > alert_limit
        )
        for limit in sensitivity_limits:
            suffix = int(round(limit * 100))
            row[f"degenerada_limite_alertas_{suffix}"] = bool(
                row["alcanza_recall_objetivo"]
                and metrics["proporcion_alertada"] > limit
            )
        rows.append(row)
    return pd.DataFrame(rows)


def select_threshold(
    curve: pd.DataFrame,
    recall_target: float,
    alert_limit: float,
) -> Tuple[pd.Series, str]:
    """Prioriza el objetivo sin escoger automáticamente una política degenerada."""

    target = curve[curve["recall"] >= recall_target]
    viable_target = target[target["proporcion_alertada"] <= alert_limit]
    if not viable_target.empty:
        candidates = viable_target
        reason = "RECALL_OBJETIVO_NO_DEGENERADO"
    else:
        nondegenerate = curve[curve["proporcion_alertada"] <= alert_limit]
        if nondegenerate.empty:
            candidates = curve
            reason = "SIN_POLITICA_BAJO_LIMITE_ALERTAS"
        else:
            max_recall = nondegenerate["recall"].max()
            candidates = nondegenerate[nondegenerate["recall"] == max_recall]
            reason = "FALLBACK_MAX_RECALL_NO_DEGENERADO"
    ordered = candidates.sort_values(
        ["costo_relativo_fn5_fp1", "f2", "precision", "threshold"],
        ascending=[True, False, False, False],
        kind="stable",
    )
    return ordered.iloc[0], reason


def _validate_cv_feasibility(y: pd.Series, splits: int, context: str) -> None:
    counts = y.value_counts()
    if len(counts) != 2 or int(counts.min()) < splits:
        raise ValueError(
            f"{context}: se requieren al menos {splits} casos por clase; distribución={counts.to_dict()}"
        )


def inner_oof_probabilities(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    model_name: str,
    calibration: str,
    config: EvaluationConfig,
    random_state: int,
) -> np.ndarray:
    """Genera probabilidades OOF exclusivamente dentro de outer-train."""

    _validate_cv_feasibility(y_train, config.inner_splits, "Inner CV")
    splitter = StratifiedKFold(
        n_splits=config.inner_splits, shuffle=True, random_state=random_state + 101
    )
    probabilities = np.full(len(y_train), np.nan, dtype=float)
    for inner_fold, (fit_idx, validation_idx) in enumerate(splitter.split(X_train, y_train), 1):
        y_fit = y_train.iloc[fit_idx]
        calibration_splits = min(config.inner_splits, int(y_fit.value_counts().min()))
        if calibration != "sin_calibrar" and calibration_splits < 2:
            raise ValueError(
                f"{calibration}: muestra insuficiente para calibración en inner fold {inner_fold}."
            )
        estimator = build_estimator(
            model_name,
            calibration,
            random_state + inner_fold,
            max(2, calibration_splits),
        )
        estimator.fit(X_train.iloc[fit_idx], y_fit)
        probabilities[validation_idx] = estimator.predict_proba(
            X_train.iloc[validation_idx]
        )[:, 1]
    if np.isnan(probabilities).any():
        raise RuntimeError("Inner CV no generó una probabilidad OOF para cada outer-train.")
    return probabilities


def _metadata_columns(metadata: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(metadata)


def run_evaluation(
    dataset_path: Path = DATASET_PATH,
    config: EvaluationConfig = EvaluationConfig(),
    model_filter: Optional[Sequence[str]] = None,
) -> EvaluationResults:
    data, X, y = load_dataset(dataset_path)
    _validate_cv_feasibility(y, config.outer_splits, "Outer CV")
    metadata = environment_metadata(dataset_path, config)
    selected_models = list(model_filter or available_model_status().keys())
    status = available_model_status()
    unknown = set(selected_models) - set(status)
    if unknown:
        raise ValueError(f"Modelos desconocidos: {sorted(unknown)}")

    fold_rows: List[Dict[str, Any]] = []
    prediction_rows: List[Dict[str, Any]] = []
    threshold_rows: List[Dict[str, Any]] = []
    confusion_rows: List[Dict[str, Any]] = []

    for model_name in selected_models:
        model_status, cause = status[model_name]
        if model_status != "DISPONIBLE":
            fold_rows.append(
                {
                    **_metadata_columns(metadata),
                    "modelo": model_name,
                    "calibracion": "NO_DISPONIBLE_ENTORNO",
                    "estado_modelo": model_status,
                    "causa_estado_modelo": cause,
                    "outer_seed": np.nan,
                    "outer_fold": np.nan,
                }
            )
            continue

        for calibration in CALIBRATION_VARIANTS:
            for outer_seed in config.outer_seeds:
                outer_cv = StratifiedKFold(
                    n_splits=config.outer_splits,
                    shuffle=True,
                    random_state=outer_seed,
                )
                for outer_fold, (outer_train_idx, outer_validation_idx) in enumerate(
                    outer_cv.split(X, y), 1
                ):
                    validate_fold_boundaries(
                        outer_train_idx,
                        outer_validation_idx,
                        outer_train_idx,
                        outer_train_idx,
                    )
                    X_train, y_train = X.iloc[outer_train_idx], y.iloc[outer_train_idx]
                    X_validation = X.iloc[outer_validation_idx]
                    y_validation = y.iloc[outer_validation_idx]
                    fold_seed = int(outer_seed * 100 + outer_fold)

                    try:
                        inner_probs = inner_oof_probabilities(
                            X_train,
                            y_train,
                            model_name,
                            calibration,
                            config,
                            fold_seed,
                        )
                        curve = evaluate_threshold_grid(
                            y_train,
                            inner_probs,
                            config.thresholds,
                            config.recall_target,
                            config.alert_limit,
                        )
                        selected, selection_reason = select_threshold(
                            curve, config.recall_target, config.alert_limit
                        )
                        threshold = float(selected["threshold"])
                        target_any = bool((curve["recall"] >= config.recall_target).any())
                        target_nondegenerate = bool(
                            (
                                (curve["recall"] >= config.recall_target)
                                & (curve["proporcion_alertada"] <= config.alert_limit)
                            ).any()
                        )
                        for row in curve.to_dict("records"):
                            threshold_rows.append(
                                {
                                    **_metadata_columns(metadata),
                                    "modelo": model_name,
                                    "calibracion": calibration,
                                    "outer_seed": outer_seed,
                                    "outer_fold": outer_fold,
                                    "origen_curva": "inner_oof_outer_train",
                                    **row,
                                }
                            )

                        calibration_splits = min(
                            config.inner_splits, int(y_train.value_counts().min())
                        )
                        estimator = build_estimator(
                            model_name,
                            calibration,
                            fold_seed + 5000,
                            calibration_splits,
                        )
                        estimator.fit(X_train, y_train)
                        outer_probs = estimator.predict_proba(X_validation)[:, 1]
                        metrics = safe_classification_metrics(
                            y_validation, outer_probs, threshold
                        )
                        selected_degenerate = bool(
                            metrics["recall"] >= config.recall_target
                            and metrics["proporcion_alertada"] > config.alert_limit
                        )
                        common = {
                            **_metadata_columns(metadata),
                            "modelo": model_name,
                            "calibracion": calibration,
                            "estado_modelo": "EVALUADO",
                            "causa_estado_modelo": "",
                            "outer_seed": outer_seed,
                            "outer_fold": outer_fold,
                            "n_outer_train": len(outer_train_idx),
                            "n_outer_validation": len(outer_validation_idx),
                            "positivos_outer_train": int(y_train.sum()),
                            "positivos_outer_validation": int(y_validation.sum()),
                            "threshold_seleccionado": threshold,
                            "razon_seleccion_threshold": selection_reason,
                            "recall_objetivo_disponible_inner": target_any,
                            "recall_objetivo_no_degenerado_inner": target_nondegenerate,
                            "politica_degenerada": selected_degenerate,
                            "outer_validation_usado_en_threshold": False,
                            "outer_validation_usado_en_calibracion": False,
                            "indices_outer_train": json.dumps(outer_train_idx.tolist()),
                            "indices_outer_validation": json.dumps(
                                outer_validation_idx.tolist()
                            ),
                        }
                        fold_rows.append(
                            {
                                **common,
                                **metrics,
                                "costo_relativo": config.cost_fn * metrics["fn"]
                                + config.cost_fp * metrics["fp"],
                                "costo_relativo_fn2_fp1": 2 * metrics["fn"]
                                + metrics["fp"],
                                "costo_relativo_fn5_fp1": 5 * metrics["fn"]
                                + metrics["fp"],
                                "costo_relativo_fn10_fp1": 10 * metrics["fn"]
                                + metrics["fp"],
                            }
                        )
                        confusion_rows.append(
                            {
                                **_metadata_columns(metadata),
                                "modelo": model_name,
                                "calibracion": calibration,
                                "outer_seed": outer_seed,
                                "outer_fold": outer_fold,
                                "threshold_seleccionado": threshold,
                                **{key: metrics[key] for key in ("tn", "fp", "fn", "tp")},
                                "politica_degenerada": selected_degenerate,
                            }
                        )
                        outer_predictions = (outer_probs >= threshold).astype(int)
                        for local_position, global_idx in enumerate(outer_validation_idx):
                            prediction_rows.append(
                                {
                                    **_metadata_columns(metadata),
                                    "modelo": model_name,
                                    "calibracion": calibration,
                                    "outer_seed": outer_seed,
                                    "outer_fold": outer_fold,
                                    "indice_dataset": int(global_idx),
                                    "id_insulina_master": data.iloc[global_idx][
                                        "id_insulina_master"
                                    ],
                                    "target_real": int(y_validation.iloc[local_position]),
                                    "probabilidad_outer_oof": float(
                                        outer_probs[local_position]
                                    ),
                                    "threshold_seleccionado": threshold,
                                    "prediccion": int(outer_predictions[local_position]),
                                    "politica_degenerada_fold": selected_degenerate,
                                }
                            )
                    except Exception as exc:
                        fold_rows.append(
                            {
                                **_metadata_columns(metadata),
                                "modelo": model_name,
                                "calibracion": calibration,
                                "estado_modelo": "NO_EVALUABLE_FOLD",
                                "causa_estado_modelo": f"{type(exc).__name__}: {exc}",
                                "outer_seed": outer_seed,
                                "outer_fold": outer_fold,
                                "n_outer_train": len(outer_train_idx),
                                "n_outer_validation": len(outer_validation_idx),
                            }
                        )

    fold_frame = pd.DataFrame(fold_rows)
    predictions_frame = pd.DataFrame(prediction_rows)
    thresholds_frame = pd.DataFrame(threshold_rows)
    confusion_frame = pd.DataFrame(confusion_rows)
    summary_frame = build_summary(fold_frame, metadata, status, selected_models, config)
    calibration_frame = build_calibration_metrics(predictions_frame, metadata)
    return EvaluationResults(
        fold=fold_frame,
        summary=summary_frame,
        predictions=predictions_frame,
        calibration=calibration_frame,
        thresholds=thresholds_frame,
        confusion=confusion_frame,
        metadata=metadata,
    )


def build_summary(
    fold_frame: pd.DataFrame,
    metadata: Mapping[str, Any],
    status: Mapping[str, Tuple[str, str]],
    selected_models: Sequence[str],
    config: EvaluationConfig,
) -> pd.DataFrame:
    evaluated = fold_frame[fold_frame.get("estado_modelo", pd.Series(dtype=str)) == "EVALUADO"].copy()
    metrics = [
        "accuracy",
        "precision",
        "recall",
        "f1",
        "f2",
        "roc_auc",
        "pr_auc_average_precision",
        "brier_score",
        "log_loss",
        "specificity",
        "fpr",
        "proporcion_alertada",
        "threshold_seleccionado",
        "fp",
        "fn",
        "costo_relativo_fn2_fp1",
        "costo_relativo_fn5_fp1",
        "costo_relativo_fn10_fp1",
    ]
    rows: List[Dict[str, Any]] = []
    if not evaluated.empty:
        for (model_name, calibration), group in evaluated.groupby(
            ["modelo", "calibracion"], sort=False
        ):
            row: Dict[str, Any] = {
                **_metadata_columns(metadata),
                "modelo": model_name,
                "calibracion": calibration,
                "estado_modelo": "EVALUADO",
                "causa_estado_modelo": "",
                "folds_evaluados": len(group),
            }
            for metric in metrics:
                values = pd.to_numeric(group[metric], errors="coerce")
                row[f"{metric}_media"] = values.mean()
                row[f"{metric}_std"] = values.std(ddof=1)
                row[f"{metric}_min"] = values.min()
                row[f"{metric}_max"] = values.max()
            all_recall = bool((group["recall"] >= config.recall_target).all())
            any_degenerate = bool(group["politica_degenerada"].astype(bool).any())
            if all_recall and not any_degenerate:
                objective = "ALCANZADO_ESTABLE"
            elif all_recall and any_degenerate:
                objective = "ALCANZADO_DEGENERADO"
            else:
                objective = "NO_ALCANZADO_ESTABLEMENTE"
            row["estado_objetivo_recall_90"] = objective
            row["folds_con_recall_objetivo"] = int(
                (group["recall"] >= config.recall_target).sum()
            )
            row["folds_politica_degenerada"] = int(
                group["politica_degenerada"].astype(bool).sum()
            )
            row["advertencia_varianza"] = (
                "ALTA_VARIANZA_NO_INTERPRETAR_MEDIA_COMO_EVIDENCIA_FUERTE"
                if float(row.get("recall_std", 0) or 0) > 0.10
                else "MUESTRA_PEQUENA_INTERPRETAR_CON_CAUTELA"
            )
            rows.append(row)

    evaluated_keys = {(row["modelo"], row["calibracion"]) for row in rows}
    for model_name in selected_models:
        model_status, cause = status[model_name]
        if model_status != "DISPONIBLE" and not any(
            key[0] == model_name for key in evaluated_keys
        ):
            rows.append(
                {
                    **_metadata_columns(metadata),
                    "modelo": model_name,
                    "calibracion": "NO_DISPONIBLE_ENTORNO",
                    "estado_modelo": model_status,
                    "causa_estado_modelo": cause,
                    "folds_evaluados": 0,
                    "estado_objetivo_recall_90": "NO_ALCANZADO_ESTABLEMENTE",
                }
            )
    return pd.DataFrame(rows)


def build_calibration_metrics(
    predictions: pd.DataFrame, metadata: Mapping[str, Any]
) -> pd.DataFrame:
    if predictions.empty:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    bin_edges = np.linspace(0, 1, 6)
    for (model_name, calibration), group in predictions.groupby(
        ["modelo", "calibracion"], sort=False
    ):
        y = group["target_real"].to_numpy(dtype=int)
        probs = np.clip(group["probabilidad_outer_oof"].to_numpy(dtype=float), 1e-12, 1 - 1e-12)
        brier = brier_score_loss(y, probs)
        loss = log_loss(y, probs, labels=[0, 1])
        bin_ids = np.digitize(probs, bin_edges[1:-1], right=False)
        for bin_id in range(5):
            mask = bin_ids == bin_id
            rows.append(
                {
                    **_metadata_columns(metadata),
                    "modelo": model_name,
                    "calibracion": calibration,
                    "bin": bin_id + 1,
                    "limite_inferior": bin_edges[bin_id],
                    "limite_superior": bin_edges[bin_id + 1],
                    "n": int(mask.sum()),
                    "probabilidad_media": float(probs[mask].mean()) if mask.any() else np.nan,
                    "fraccion_positivos": float(y[mask].mean()) if mask.any() else np.nan,
                    "brier_score_global": brier,
                    "log_loss_global": loss,
                    "nota": "isotonic es exploratorio" if calibration == "isotonic_exploratorio" else "",
                }
            )
    return pd.DataFrame(rows)


def export_results(
    results: EvaluationResults,
    output_dir: Path = OUTPUT_DIR,
    figures_dir: Path = FIGURES_DIR,
    document_path: Path = DOCUMENT_PATH,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    document_path.parent.mkdir(parents=True, exist_ok=True)
    frames = {
        "fold": results.fold,
        "summary": results.summary,
        "predictions": results.predictions,
        "calibration": results.calibration,
        "thresholds": results.thresholds,
        "confusion": results.confusion,
    }
    for key, frame in frames.items():
        frame.to_csv(output_dir / OUTPUT_FILENAMES[key], index=False, encoding="utf-8-sig")
    create_figures(results, figures_dir)
    write_documentation(results, document_path)


def _available_predictions(results: EvaluationResults) -> pd.DataFrame:
    return results.predictions.copy()


def create_figures(results: EvaluationResults, figures_dir: Path = FIGURES_DIR) -> None:
    predictions = _available_predictions(results)
    if predictions.empty:
        raise RuntimeError("No existen predicciones OOF para generar figuras.")
    labels = {
        "sin_calibrar": "Sin calibrar",
        "sigmoid": "Sigmoid",
        "isotonic_exploratorio": "Isotonic (expl.)",
    }

    # ROC y PR sobre todas las repeticiones OOF, claramente etiquetadas.
    for kind, filename in [("roc", "scrum38_roc_cv.png"), ("pr", "scrum38_pr_cv.png")]:
        fig, ax = plt.subplots(figsize=(9, 7), dpi=180)
        for (model, calibration), group in predictions.groupby(["modelo", "calibracion"]):
            y = group["target_real"].to_numpy(dtype=int)
            p = group["probabilidad_outer_oof"].to_numpy(dtype=float)
            if kind == "roc":
                x, y_curve, _ = roc_curve(y, p)
                score = roc_auc_score(y, p)
                ax.plot(x, y_curve, label=f"{model} · {labels[calibration]} ({score:.3f})")
            else:
                precision, recall, _ = precision_recall_curve(y, p)
                score = average_precision_score(y, p)
                ax.plot(recall, precision, label=f"{model} · {labels[calibration]} ({score:.3f})")
        if kind == "roc":
            ax.plot([0, 1], [0, 1], "--", color="gray", label="Azar")
            ax.set(xlabel="FPR", ylabel="Recall", title="SCRUM-38 · ROC outer-OOF repetida")
        else:
            prevalence = predictions["target_real"].mean()
            ax.axhline(prevalence, ls="--", color="gray", label=f"Prevalencia ({prevalence:.3f})")
            ax.set(xlabel="Recall", ylabel="Precision", title="SCRUM-38 · Precision–Recall outer-OOF")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(figures_dir / filename)
        plt.close(fig)

    # Reliability curve.
    fig, ax = plt.subplots(figsize=(9, 7), dpi=180)
    for (model, calibration), group in results.calibration.groupby(["modelo", "calibracion"]):
        valid = group[group["n"] > 0]
        ax.plot(
            valid["probabilidad_media"],
            valid["fraccion_positivos"],
            marker="o",
            label=f"{model} · {labels[calibration]}",
        )
    ax.plot([0, 1], [0, 1], "--", color="black", label="Calibración ideal")
    ax.set(xlabel="Probabilidad media", ylabel="Fracción positiva", title="SCRUM-38 · Curvas de calibración")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(figures_dir / "scrum38_calibracion.png")
    plt.close(fig)

    # Matrices: primera semilla para no sumar observaciones repetidas.
    first_seed = min(results.metadata.get("random_seeds", "[42]").strip("[]").split(","), key=lambda value: int(value))
    seed_value = int(first_seed)
    groups = list(predictions[predictions["outer_seed"] == seed_value].groupby(["modelo", "calibracion"]))
    columns = 3
    rows = math.ceil(len(groups) / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(13, 4 * rows), dpi=170, squeeze=False)
    for ax, ((model, calibration), group) in zip(axes.flat, groups):
        cm = confusion_matrix(group["target_real"], group["prediccion"], labels=[0, 1])
        ax.imshow(cm, cmap="Blues")
        for r in range(2):
            for c in range(2):
                ax.text(c, r, str(cm[r, c]), ha="center", va="center", fontsize=12)
        ax.set_title(f"{model} · {labels[calibration]}")
        ax.set_xticks([0, 1], ["Pred 0", "Pred 1"])
        ax.set_yticks([0, 1], ["Real 0", "Real 1"])
    for ax in axes.flat[len(groups):]:
        ax.axis("off")
    fig.suptitle(f"SCRUM-38 · Matrices outer-OOF (seed {seed_value})")
    fig.tight_layout()
    fig.savefig(figures_dir / "scrum38_matrices_confusion.png")
    plt.close(fig)

    # Curvas de threshold agregadas desde inner OOF.
    curve = results.thresholds.groupby(["modelo", "calibracion", "threshold"], as_index=False).agg(
        recall=("recall", "mean"),
        precision=("precision", "mean"),
        costo=("costo_relativo_fn5_fp1", "mean"),
    )
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=180)
    for (model, calibration), group in curve.groupby(["modelo", "calibracion"]):
        label = f"{model} · {labels[calibration]}"
        axes[0].plot(group["threshold"], group["recall"], label=label)
        axes[1].plot(group["threshold"], group["precision"], label=label)
    axes[0].axhline(DEFAULT_RECALL_TARGET, ls="--", color="black")
    axes[0].set(title="Recall", xlabel="Threshold", ylabel="Media inner-OOF")
    axes[1].set(title="Precision", xlabel="Threshold", ylabel="Media inner-OOF")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(figures_dir / "scrum38_recall_precision_threshold.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=180)
    for (model, calibration), group in curve.groupby(["modelo", "calibracion"]):
        ax.plot(group["threshold"], group["costo"], label=f"{model} · {labels[calibration]}")
    ax.set(title="SCRUM-38 · Penalización técnica relativa FN:FP = 5:1", xlabel="Threshold", ylabel="Costo medio inner-OOF")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(figures_dir / "scrum38_costos_threshold.png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6), dpi=180)
    evaluated = results.fold[results.fold["estado_modelo"] == "EVALUADO"].copy()
    evaluated["grupo"] = evaluated["modelo"] + "\n" + evaluated["calibracion"].map(labels)
    group_names = list(dict.fromkeys(evaluated["grupo"]))
    values = [evaluated.loc[evaluated["grupo"] == name, "recall"].to_numpy() for name in group_names]
    # Compatibilidad universal de versiones de Matplotlib (tick_labels en 3.9+ vs labels legacy)
    try:
        ax.boxplot(values, tick_labels=group_names, showmeans=True)
    except TypeError:
        ax.boxplot(values, labels=group_names, showmeans=True)
    ax.axhline(DEFAULT_RECALL_TARGET, ls="--", color="red", label="Objetivo 0.90")
    ax.set(title="SCRUM-38 · Estabilidad de recall entre outer folds", ylabel="Recall")
    ax.tick_params(axis="x", rotation=35, labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "scrum38_estabilidad_folds.png")
    plt.close(fig)


def _format_float(value: Any, digits: int = 3) -> str:
    try:
        numeric = float(value)
        return "NA" if math.isnan(numeric) else f"{numeric:.{digits}f}"
    except (TypeError, ValueError):
        return "NA"


def write_documentation(results: EvaluationResults, path: Path = DOCUMENT_PATH) -> None:
    summary = results.summary
    evaluated = summary[summary["estado_modelo"] == "EVALUADO"]
    table_rows = []
    for row in evaluated.itertuples(index=False):
        table_rows.append(
            "| {modelo} | {calibracion} | {recall} | {precision} | {roc} | {pr} | {brier} | {loss} | {fp} | {alerts} | {state} |".format(
                modelo=row.modelo,
                calibracion=row.calibracion,
                recall=_format_float(row.recall_media),
                precision=_format_float(row.precision_media),
                roc=_format_float(row.roc_auc_media),
                pr=_format_float(row.pr_auc_average_precision_media),
                brier=_format_float(row.brier_score_media),
                loss=_format_float(row.log_loss_media),
                fp=_format_float(row.fp_media, 2),
                alerts=_format_float(row.proporcion_alertada_media),
                state=row.estado_objetivo_recall_90,
            )
        )
    unavailable = summary[summary["estado_modelo"] != "EVALUADO"]
    unavailable_text = "\n".join(
        f"- **{row.modelo}:** `{row.estado_modelo}` — {row.causa_estado_modelo}"
        for row in unavailable.itertuples(index=False)
    ) or "- Todos los modelos solicitados estuvieron disponibles."
    any_success = bool((evaluated["estado_objetivo_recall_90"] == "ALCANZADO_ESTABLE").any())
    conclusion = (
        "Al menos una combinación alcanzó el objetivo en todos los outer folds sin superar el límite técnico configurable de alertas. La muestra sigue siendo demasiado pequeña para considerarlo evidencia fuerte."
        if any_success
        else "No existe evidencia suficiente para afirmar que Recall >= 90% sea estable y útil. El objetivo debe reportarse como no alcanzado establemente o, cuando corresponda, alcanzado únicamente mediante una política degenerada."
    )
    metadata = results.metadata
    document = f"""# SCRUM-38 / US-41 — Evaluación formal y calibración

## 1. Objetivo

Evaluar de forma reproducible los modelos actuales sin modificar los artefactos productivos, separando estrictamente ajuste, calibración, selección de threshold y validación externa.

## 2. Dataset utilizado

- Archivo: `{metadata['dataset_path']}`.
- SHA-256: `{metadata['dataset_sha256']}`.
- Registros: 43; clase 0: 35; clase 1: 8.
- Python {metadata['python_version']}; scikit-learn {metadata['sklearn_version']}; joblib {metadata['joblib_version']}; XGBoost {metadata['xgboost_version']}.
- Semillas outer: {metadata['random_seeds']}.

## 3. Naturaleza del target

`quiebre_stock_inminente` es un **proxy del estado actual**: agotado o últimas unidades equivale a 1. No es un quiebre futuro observado y los resultados no validan pronóstico temporal ni riesgo clínico.

## 4. Por qué 4 folds

Con 8 positivos, cuatro folds ubican exactamente dos positivos en cada outer-validation. Cinco folds dejarían folds con un solo positivo y un error movería el recall en 100 puntos. Las repeticiones con distintas semillas miden sensibilidad a la partición, pero no crean observaciones nuevas.

## 5. Validación anidada

Se usó outer `StratifiedKFold(4)` repetido y inner `StratifiedKFold(3)`. El threshold se eligió solo con probabilidades inner-OOF del outer-train. El outer-validation nunca participó en preprocesamiento, calibración ni selección.

## 6. Threshold no es calibración

El threshold convierte probabilidades en clases. La calibración intenta alinear probabilidad estimada y frecuencia observada. Se evaluó el modelo sin calibrar, sigmoid y, solo exploratoriamente, isotonic.

## 7. Sigmoid e isotonic

Sigmoid es la variante calibrada principal por ser paramétrica. Isotonic es exploratorio: 43 filas y 8 positivos son insuficientes para recomendar una función escalonada flexible como artefacto productivo.

## 8. Matriz de costos

Escenario principal: TN=0, TP=0, FP=1, FN=5; `costo = 5*FN + FP`. Es una **penalización técnica relativa para evaluación**, no un costo clínico, económico ni médico. También se reportan razones 2:1 y 10:1.

## 9. Resultados outer-CV

| Modelo | Calibración | Recall medio | Precision media | ROC-AUC | PR-AUC/AP | Brier | Log-loss | FP medio | Proporción alertada | Estado Recall >=90% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
{chr(10).join(table_rows)}

Estado de modelos opcionales:

{unavailable_text}

## 10. Recall >=90%, falsos positivos y estabilidad

Con 8 positivos, Recall >=90% exige detectar 8/8 en el conjunto OOF correspondiente. La clasificación final exige alcanzarlo en todos los outer folds y no solo como promedio. Una política se marca degenerada cuando alcanza el objetivo superando el límite técnico configurable de proporción alertada ({metadata['limite_alertas_tecnico_configurable']:.0%}); este límite se acompaña con sensibilidad 60%, 70%, 80%, 90% y 100% y no se presenta como criterio clínico.

## 11. ROC-AUC, PR-AUC y calibración

ROC-AUC y Average Precision se calcularon exclusivamente sobre outer-validation. Brier y log-loss evalúan calidad probabilística. Con tan pocos positivos, diferencias pequeñas entre variantes no constituyen evidencia fuerte y las curvas de confiabilidad contienen bins con pocos casos.

## 12. Limitaciones

- 43 observaciones y 8 positivos.
- Un único corte temporal; no hay evento futuro.
- Dependencia potencial entre productos similares y farmacias.
- Alta sensibilidad a las particiones.
- Isotonic puede sobreajustar.
- Las repeticiones CV reutilizan las mismas filas.
- El límite de alertas es una configuración técnica para sensibilidad, no una verdad clínica.

## 13. Recomendación final

{conclusion}

No se modificaron joblib, threshold productivo, predicciones productivas ni pipeline web.
"""
    path.write_text(document, encoding="utf-8")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DATASET_PATH)
    parser.add_argument("--limite-alertas", type=float, default=DEFAULT_ALERT_LIMIT)
    parser.add_argument("--semillas", type=int, nargs="+", default=list(DEFAULT_OUTER_SEEDS))
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not 0 < args.limite_alertas <= 1:
        raise ValueError("--limite-alertas debe estar en (0, 1].")
    config = EvaluationConfig(
        outer_seeds=tuple(args.semillas), alert_limit=float(args.limite_alertas)
    )
    results = run_evaluation(args.dataset, config)
    export_results(results)
    print(results.summary[[
        "modelo",
        "calibracion",
        "estado_modelo",
        "estado_objetivo_recall_90",
    ]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
