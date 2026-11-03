"""Pruebas unitarias para el módulo de entrenamiento de modelos supervisados (US-05 / SCRUM-9).

Verifica la integridad de la preparación de datos, la prevención estricta de fuga
de información (anti-leakage), la serialización de modelos, las métricas y la
generación de figuras analíticas.
"""

import importlib
import json
from pathlib import Path
import unittest

import joblib
import numpy as np
import pandas as pd

mod_stock = importlib.import_module("src.models.03_entrenamiento_modelos_stock")


class TestEntrenamientoModelosStock(unittest.TestCase):
    """Suite de validación formal para US-05."""

    @classmethod
    def setUpClass(cls) -> None:
        """Carga datos y ejecuta validaciones preliminares."""
        cls.project_dir = Path(__file__).resolve().parents[2]
        cls.data_processed = cls.project_dir / "data" / "processed"
        cls.models_dir = cls.project_dir / "models"
        cls.figures_dir = cls.project_dir / "docs" / "figures"

        cls.df_orig, cls.X, cls.y = mod_stock.cargar_y_preparar_datos()

    def test_01_cargar_datos_y_dimensiones(self) -> None:
        """Verifica que el dataset analítico se cargue con la dimensionalidad esperada."""
        self.assertEqual(len(self.df_orig), 43)
        self.assertEqual(len(self.X), 43)
        self.assertEqual(len(self.y), 43)
        self.assertEqual(int(self.y.sum()), 4)

    def test_02_blindaje_estricto_anti_leakage(self) -> None:
        """Verifica que ninguna columna que delate el target esté presente en las predictoras."""
        for leak_col in mod_stock.LEAKAGE_COLUMNS:
            self.assertNotIn(
                leak_col,
                self.X.columns,
                f"Fuga crítica detectada: {leak_col} está presente en la matriz predictora X",
            )

    def test_03_features_predictoras_definidas(self) -> None:
        """Verifica que X contenga exactamente las 14 variables predictoras seleccionadas."""
        expected_cols = mod_stock.NUMERIC_FEATURES + mod_stock.CATEGORICAL_FEATURES
        self.assertEqual(list(self.X.columns), expected_cols)
        self.assertEqual(len(self.X.columns), 14)

    def test_04_preprocesador_ajuste_y_transformacion(self) -> None:
        """Comprueba que el ColumnTransformer escale numéricas y codifique categóricas."""
        prep = mod_stock.construir_preprocesador()
        X_trans = prep.fit_transform(self.X)

        self.assertEqual(X_trans.shape[0], 43)
        self.assertGreater(X_trans.shape[1], 14)
        self.assertFalse(np.isnan(X_trans).any())

    def test_05_configuracion_de_modelos(self) -> None:
        """Comprueba que se instancien los 4 modelos requeridos con sus parámetros."""
        modelos = mod_stock.obtener_modelos_a_entrenar()
        self.assertIn("Baseline", modelos)
        self.assertIn("RandomForest", modelos)
        self.assertIn("XGBoost", modelos)
        self.assertIn("LogisticRegression", modelos)

    def test_06_evaluacion_umbral_optimo(self) -> None:
        """Comprueba la lógica de cálculo del umbral óptimo orientado al Recall."""
        y_dummy = np.array([0, 0, 0, 0, 1, 1])
        probs_dummy = np.array([0.1, 0.2, 0.3, 0.4, 0.7, 0.8])
        th_opt, rec, prec, f2 = mod_stock.evaluar_umbral_optimo(y_dummy, probs_dummy, beta=2.0)

        self.assertGreaterEqual(th_opt, 0.05)
        self.assertLessEqual(th_opt, 0.65)
        self.assertGreaterEqual(rec, 0.0)
        self.assertGreaterEqual(prec, 0.0)
        self.assertGreaterEqual(f2, 0.0)

    def test_07_modelos_serializados_existencia_y_carga(self) -> None:
        """Verifica que todos los archivos .joblib y metadata JSON existan y sean legibles."""
        archivos_esperados = [
            "randomforest_stock.joblib",
            "xgboost_stock.joblib",
            "logisticregression_stock.joblib",
            "modelo_produccion_stock.joblib",
            "modelo_metadata.json",
        ]
        for nombre_archivo in archivos_esperados:
            ruta = self.models_dir / nombre_archivo
            self.assertTrue(ruta.exists(), f"Falta el artefacto de modelo: {ruta}")

        # Probar carga del modelo de producción
        prod_model = joblib.load(self.models_dir / "modelo_produccion_stock.joblib")
        preds = prod_model.predict(self.X)
        probs = prod_model.predict_proba(self.X)[:, 1]
        self.assertEqual(len(preds), 43)
        self.assertEqual(len(probs), 43)

        # Probar carga de metadata
        with open(self.models_dir / "modelo_metadata.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["historia_usuario"], "US-05 (SCRUM-9)")
        self.assertEqual(meta["total_positivos_quiebre"], 4)

    def test_08_tablas_analiticas_procesadas(self) -> None:
        """Verifica la validez y estructura de los CSVs analíticos generados."""
        ruta_metricas = self.data_processed / "metricas_modelos_supervisados.csv"
        ruta_preds = self.data_processed / "predicciones_probabilidad_stock.csv"
        ruta_fi = self.data_processed / "feature_importance_modelos.csv"

        self.assertTrue(ruta_metricas.exists())
        self.assertTrue(ruta_preds.exists())
        self.assertTrue(ruta_fi.exists())

        df_m = pd.read_csv(ruta_metricas)
        df_p = pd.read_csv(ruta_preds)
        df_f = pd.read_csv(ruta_fi)

        # Validar métricas
        self.assertGreater(len(df_m), 4)
        self.assertIn("recall_sensibilidad", df_m.columns)
        self.assertIn("f2_score_clinico", df_m.columns)

        # Validar predicciones
        self.assertEqual(len(df_p), 43)
        self.assertIn("probabilidad_randomforest", df_p.columns)
        self.assertIn("semaforo_predictivo_ml", df_p.columns)
        self.assertTrue(df_p["probabilidad_randomforest"].between(0.0, 1.0).all())

        # Validar semáforos permitidos
        semaforos_validos = {"ROJO_ALTO_RIESGO", "AMARILLO_RIESGO_MODERADO", "VERDE_ESTABLE"}
        self.assertTrue(set(df_p["semaforo_predictivo_ml"]).issubset(semaforos_validos))

        # Validar feature importance
        self.assertGreater(len(df_f), 10)
        self.assertIn("importancia_absoluta", df_f.columns)

    def test_09_figuras_estadisticas_generadas(self) -> None:
        """Comprueba que las 4 figuras analíticas se hayan generado con tamaño válido."""
        figuras = [
            "modelo_curvas_roc.png",
            "modelo_curvas_pr.png",
            "modelo_matrices_confusion.png",
            "modelo_feature_importance.png",
        ]
        for fig in figuras:
            ruta = self.figures_dir / fig
            self.assertTrue(ruta.exists(), f"Falta la figura generada: {ruta}")
            self.assertGreater(ruta.stat().st_size, 10000, f"Figura {fig} demasiado pequeña o corrupta")


if __name__ == "__main__":
    unittest.main()
