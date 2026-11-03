"""Pruebas de aceptación para SCRUM-24 / US-02."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
module = importlib.import_module("src.models.02_feature_engineering")


class TestFeatureEngineering(unittest.TestCase):
    """Comprueba reglas de negocio, joins seguros y correlaciones válidas."""

    @classmethod
    def setUpClass(cls):
        cls.summary = module.run_pipeline()
        cls.data = pd.read_csv(module.OUTPUT_PATH)
        cls.pearson = pd.read_csv(module.PEARSON_PATH, index_col=0)
        cls.spearman = pd.read_csv(module.SPEARMAN_PATH, index_col=0)
        cls.master = pd.read_csv(module.MASTER_PATH)

    def test_01_dataset_final_no_esta_vacio(self):
        """La matriz final debe contener observaciones retail."""
        self.assertFalse(self.data.empty)

    def test_02_joins_no_aumentan_filas(self):
        """Los joins uno-a-muchos accidentales no pueden duplicar productos."""
        self.assertEqual(len(self.data), len(self.master))

    def test_03_target_es_binario(self):
        """El proxy solo debe tomar los valores 0 y 1."""
        self.assertEqual(set(self.data["quiebre_stock_inminente"].unique()), {0, 1})

    def test_04_regla_del_target(self):
        """Valida los tres estados que definen el proxy de riesgo actual."""
        expected = {"AGOTADO": 1, "ULTIMAS_UNIDADES": 1, "DISPONIBLE": 0}
        for state, target in expected.items():
            rows = self.data[self.data["estado_stock"] == state]
            if not rows.empty:
                self.assertTrue(rows["quiebre_stock_inminente"].eq(target).all())

    def test_05_fuga_no_es_predictor(self):
        """Variables que revelan el target no pueden ser predictores."""
        predictors = module.get_predictor_columns(self.data)
        self.assertTrue(module.LEAKAGE_COLUMNS.isdisjoint(predictors))

    def test_06_precio_por_100ui_respeta_formula(self):
        """Comprueba el precio comparable cuando hay unidades totales válidas."""
        valid = self.data[self.data["unidades_totales_ui"].gt(0)]
        # El ETL guarda el valor monetario redondeado a dos decimales.
        expected = (valid["precio_venta_bs"] * 100 / valid["unidades_totales_ui"]).round(2)
        # Algunas fuentes de origen redondean el precio de venta antes del ETL;
        # se acepta una diferencia máxima de un centavo monetario.
        np.testing.assert_allclose(valid["precio_por_100ui_bs"], expected, rtol=0, atol=0.011)

    def test_07_lags_se_unen_por_periodo(self):
        """Una fila retail toma los lags de su mismo mes, no de otro mes."""
        lags = pd.read_csv(module.LAGS_PATH).set_index("fecha_periodo")
        column = next(c for c in module.LAG_COLUMNS if c in self.data.columns)
        for _, row in self.data.iterrows():
            if row["fecha_periodo"] in lags.index:
                self.assertEqual(row[column], lags.loc[row["fecha_periodo"], column])

    def test_08_tipo_cambio_se_une_por_periodo(self):
        """La cotización aplicada debe ser la del período mensual retail."""
        exchange = pd.read_csv(module.EXCHANGE_PATH).set_index("fecha_periodo")
        column = next(c for c in module.EXCHANGE_COLUMNS if c in self.data.columns)
        for _, row in self.data.iterrows():
            if row["fecha_periodo"] in exchange.index:
                self.assertEqual(row[column], exchange.loc[row["fecha_periodo"], column])

    def test_09_calendario_no_duplica_y_coincide(self):
        """El calendario se deduplica de forma segura antes del join."""
        calendar = module.prepare_calendar(pd.read_csv(module.CALENDAR_PATH))
        self.assertFalse(calendar.duplicated(["id_origen", "fecha"]).any())
        self.assertEqual(len(self.data), len(self.master))

    def test_10_densidad_solo_anillos_confirmados(self):
        """La tabla territorial no puede incluir anillos ambiguos o sin evidencia."""
        density = pd.read_csv(module.DENSITY_PATH)
        geo = pd.read_csv(module.GEO_PATH)
        expected = geo[geo["estado_anillo"].eq("ASIGNADO") & geo["anillo_asignado"].notna()]
        self.assertEqual(density["cantidad_farmacias"].sum(), len(expected))
        self.assertTrue(self.data["densidad_farmacias_anillo"].isna().all())
        self.assertTrue(self.data["densidad_anillo_disponible"].eq(False).all())

    def test_11_z_score_tiene_media_cercana_a_cero(self):
        """Cada Z-score creado queda centrado cerca de cero."""
        z_columns = [c for c in self.data.columns if c.startswith("z_")]
        self.assertIn("z_precio_por_100ui_bs", z_columns)
        for column in z_columns:
            self.assertAlmostEqual(float(self.data[column].mean()), 0.0, places=10)

    def test_12_no_hay_z_score_de_constantes(self):
        """Una variable constante se conserva, pero no se normaliza."""
        predictors = module.get_predictor_columns(self.data)
        constants = [c for c in predictors if self.data[c].dropna().nunique() < 2]
        for column in constants:
            self.assertNotIn(f"z_{column}", self.data.columns)

    def test_13_correlaciones_solo_numericas_elegibles(self):
        """Pearson y Spearman contienen exactamente variables elegibles."""
        expected = module.eligible_correlation_columns(self.data)
        self.assertEqual(self.pearson.columns.tolist(), expected)
        self.assertEqual(self.spearman.columns.tolist(), expected)
        self.assertTrue(module.LEAKAGE_COLUMNS.isdisjoint(expected))

    def test_14_correlaciones_en_rango(self):
        """Los coeficientes definidos deben permanecer entre -1 y 1."""
        for matrix in [self.pearson, self.spearman]:
            values = matrix.to_numpy(dtype=float)
            finite = values[np.isfinite(values)]
            self.assertTrue(((finite >= -1) & (finite <= 1)).all())

    def test_15_target_declara_que_es_proxy(self):
        """La matriz debe conservar la advertencia metodológica del target."""
        self.assertTrue(self.data["target_es_proxy"].eq(True).all())
        self.assertTrue(self.data["definicion_target"].eq("AGOTADO_O_ULTIMAS_UNIDADES").all())


if __name__ == "__main__":
    unittest.main()
