"""Pruebas de aceptación de SCRUM-38 / US-41."""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold


module = importlib.import_module("src.models.04_evaluacion_formal_calibracion")
PROJECT_DIR = Path(__file__).resolve().parents[2]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestEvaluacionFormalCalibracion(unittest.TestCase):
    """Valida separación anidada, métricas, outputs y seguridad productiva."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.data, cls.X, cls.y = module.load_dataset()
        cls.production_artifacts = sorted((PROJECT_DIR / "models").glob("*.joblib"))
        cls.hashes_before = {path.name: file_hash(path) for path in cls.production_artifacts}
        cls.config = module.EvaluationConfig(
            outer_seeds=(42,),
            thresholds=(0.10, 0.30, 0.50, 0.70, 0.90),
        )
        cls.results = module.run_evaluation(
            config=cls.config,
            model_filter=["Dummy"],
        )
        cls.hashes_after = {path.name: file_hash(path) for path in cls.production_artifacts}

    def test_01_target_correcto(self) -> None:
        expected = self.data["estado_stock"].isin(["AGOTADO", "ULTIMAS_UNIDADES"]).astype(int)
        pd.testing.assert_series_equal(
            self.y.reset_index(drop=True), expected.reset_index(drop=True), check_names=False
        )
        self.assertEqual(self.y.value_counts().sort_index().to_dict(), expected.value_counts().sort_index().to_dict())

    def test_02_exclusion_de_leakage(self) -> None:
        self.assertTrue(module.LEAKAGE_COLUMNS.isdisjoint(module.FEATURES))
        self.assertEqual(list(self.X.columns), module.FEATURES)

    def test_03_folds_estratificados(self) -> None:
        cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
        validation_counts = []
        total_pos = int(self.y.sum())
        for train_idx, validation_idx in cv.split(self.X, self.y):
            v_count = int(self.y.iloc[validation_idx].sum())
            t_count = int(self.y.iloc[train_idx].sum())
            validation_counts.append(v_count)
            self.assertEqual(t_count + v_count, total_pos)
        self.assertEqual(sum(validation_counts), total_pos)

    def test_04_outer_validation_nunca_entra_al_entrenamiento(self) -> None:
        module.validate_fold_boundaries([0, 1, 2], [3], [0, 1], [0, 1, 2])
        with self.assertRaisesRegex(RuntimeError, "Outer-validation|Fuga|threshold"):
            module.validate_fold_boundaries([0, 1, 2], [3], [0, 3], [0, 1])

    def test_05_calibrador_solo_usa_outer_train(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "calibración|Fuga"):
            module.validate_fold_boundaries([0, 1, 2], [3], [0, 1], [1, 3])
        evaluated = self.results.fold[self.results.fold["estado_modelo"] == "EVALUADO"]
        self.assertFalse(evaluated["outer_validation_usado_en_calibracion"].any())

    def test_06_threshold_solo_usa_inner_train(self) -> None:
        evaluated = self.results.fold[self.results.fold["estado_modelo"] == "EVALUADO"]
        self.assertFalse(evaluated["outer_validation_usado_en_threshold"].any())
        for row in evaluated.itertuples(index=False):
            train = set(json.loads(row.indices_outer_train))
            validation = set(json.loads(row.indices_outer_validation))
            self.assertTrue(train.isdisjoint(validation))

    def test_07_matriz_de_costos(self) -> None:
        metrics = module.safe_classification_metrics(
            [0, 0, 1, 1], [0.10, 0.80, 0.40, 0.90], threshold=0.50
        )
        self.assertEqual((metrics["tn"], metrics["fp"], metrics["fn"], metrics["tp"]), (1, 1, 1, 1))
        self.assertEqual(5 * metrics["fn"] + metrics["fp"], 6)

    def test_08_tn_fp_fn_tp_correctos(self) -> None:
        metrics = module.safe_classification_metrics(
            [0, 0, 0, 1, 1], [0.10, 0.20, 0.90, 0.40, 0.80], threshold=0.50
        )
        self.assertEqual(metrics["tn"], 2)
        self.assertEqual(metrics["fp"], 1)
        self.assertEqual(metrics["fn"], 1)
        self.assertEqual(metrics["tp"], 1)

    def test_09_deteccion_politica_degenerada(self) -> None:
        curve = module.evaluate_threshold_grid(
            [0, 0, 0, 1], [0.80, 0.70, 0.60, 0.90], [0.50], 0.90, 0.80
        )
        self.assertTrue(bool(curve.iloc[0]["politica_degenerada"]))
        self.assertEqual(float(curve.iloc[0]["proporcion_alertada"]), 1.0)

    def test_10_determinismo_mismas_semillas(self) -> None:
        probabilities = np.asarray([0.1, 0.2, 0.3, 0.8, 0.9])
        labels = np.asarray([0, 0, 1, 1, 1])
        curve_a = module.evaluate_threshold_grid(labels, probabilities, [0.2, 0.5, 0.8], 0.9, 0.8)
        curve_b = module.evaluate_threshold_grid(labels, probabilities, [0.2, 0.5, 0.8], 0.9, 0.8)
        selected_a, reason_a = module.select_threshold(curve_a, 0.9, 0.8)
        selected_b, reason_b = module.select_threshold(curve_b, 0.9, 0.8)
        pd.testing.assert_series_equal(selected_a, selected_b)
        self.assertEqual(reason_a, reason_b)

    def test_11_esquema_y_exportacion_de_outputs(self) -> None:
        required_fold = {
            "modelo", "calibracion", "outer_seed", "outer_fold", "recall",
            "precision", "roc_auc", "pr_auc_average_precision", "brier_score",
            "log_loss", "threshold_seleccionado", "politica_degenerada",
        }
        self.assertTrue(required_fold.issubset(self.results.fold.columns))
        self.assertIn("estado_objetivo_recall_90", self.results.summary.columns)
        self.assertIn("probabilidad_outer_oof", self.results.predictions.columns)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module.export_results(
                self.results,
                output_dir=root / "data",
                figures_dir=root / "figures",
                document_path=root / "docs" / "evaluacion.md",
            )
            for filename in module.OUTPUT_FILENAMES.values():
                self.assertTrue((root / "data" / filename).is_file(), filename)
            for filename in module.FIGURE_FILENAMES:
                self.assertTrue((root / "figures" / filename).is_file(), filename)
            self.assertTrue((root / "docs" / "evaluacion.md").is_file())

    def test_12_xgboost_ausente_no_rompe_pipeline(self) -> None:
        with mock.patch.object(module, "XGBOOST_AVAILABLE", False), mock.patch.object(
            module, "XGBOOST_IMPORT_ERROR", "ModuleNotFoundError simulado"
        ):
            results = module.run_evaluation(
                config=self.config,
                model_filter=["XGBoost"],
            )
        self.assertEqual(results.fold.iloc[0]["estado_modelo"], "NO_DISPONIBLE_ENTORNO")
        self.assertEqual(results.summary.iloc[0]["estado_modelo"], "NO_DISPONIBLE_ENTORNO")

    def test_13_joblibs_productivos_intactos(self) -> None:
        self.assertTrue(self.production_artifacts)
        self.assertEqual(self.hashes_before, self.hashes_after)


if __name__ == "__main__":
    unittest.main()
