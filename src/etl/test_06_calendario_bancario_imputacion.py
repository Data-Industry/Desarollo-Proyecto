"""Pruebas unitarias de SCRUM-37: calendario e imputación conservadora."""

import importlib
from pathlib import Path
import sys
import unittest

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    module = importlib.import_module("src.etl.06_calendario_bancario_imputacion")
except ImportError:
    module = importlib.import_module("06_calendario_bancario_imputacion")


class TestCalendarioBancarioImputacion(unittest.TestCase):
    """Valida reglas explícitas sin inventar observaciones retail."""

    @classmethod
    def setUpClass(cls):
        """Construye un calendario reutilizable para las pruebas."""
        cls.calendar = module.add_payment_variables(module.build_calendar(2026))

    def test_calendario_tiene_365_dias(self):
        """Comprueba que 2026 no bisiesto tiene una fila por día."""
        self.assertEqual(len(self.calendar), 365)

    def test_dias_uno_a_cinco_y_fin_de_mes_son_pago_jira(self):
        """Comprueba la regla operativa solicitada en Jira."""
        january = self.calendar[self.calendar["mes"].eq(1)]
        self.assertTrue(january.loc[january["dia"].between(1, 5), "dia_pago_renta"].eq(1).all())
        self.assertEqual(int(january.loc[january["dia"].eq(31), "dia_pago_renta"].iloc[0]), 1)

    def test_dias_uno_a_siete_son_ventana_oficial(self):
        """Comprueba la ventana normativa de disponibilidad de pensiones."""
        february = self.calendar[self.calendar["mes"].eq(2)]
        self.assertTrue(february.loc[february["dia"].between(1, 7), "dia_pago_pension_oficial"].eq(1).all())
        self.assertEqual(int(february.loc[february["dia"].eq(8), "dia_pago_pension_oficial"].iloc[0]), 0)

    def test_ventana_y_distancia_funcionan_antes_y_despues(self):
        """Comprueba distancias firmadas alrededor de un pago operativo."""
        cases = {"2026-01-04": 0, "2026-01-08": 3, "2026-01-28": -3}
        for fecha, distance in cases.items():
            row = self.calendar[self.calendar["fecha"].eq(pd.Timestamp(fecha))].iloc[0]
            self.assertEqual(int(row["distancia_dias_pago_renta"]), distance)
            self.assertEqual(int(row["ventana_pago_renta_3d"]), 1)

    def test_sin_faltantes_no_se_modifican(self):
        """Comprueba que una observación completa conserva sus valores."""
        retail = pd.DataFrame({
            "farmacia": ["A"], "marca_comercial": ["M"], "principio_activo": ["P"],
            "precio_bs": [10.0], "estado_stock": ["DISPONIBLE"],
            "stock_disponible_binario": [1],
        })
        result = module.apply_conservative_imputation(retail)
        self.assertEqual(result.loc[0, "precio_bs_imputado"], 10.0)
        self.assertEqual(result.loc[0, "estado_stock_imputado"], "DISPONIBLE")
        self.assertFalse(bool(result.loc[0, "precio_fue_imputado"]))
        self.assertFalse(bool(result.loc[0, "stock_fue_imputado"]))

    def test_retail_actual_completo_no_recibe_imputaciones(self):
        """Comprueba directamente que el retail actual conserva sus valores."""
        retail = pd.read_csv(
            PROJECT_DIR / "data" / "processed" / "retail_stock_historico_consolidado.csv"
        )
        result = module.apply_conservative_imputation(retail)
        self.assertTrue(result["precio_bs"].equals(result["precio_bs_imputado"]))
        self.assertTrue(result["estado_stock"].equals(result["estado_stock_imputado"]))
        self.assertFalse(result["precio_fue_imputado"].any())
        self.assertFalse(result["stock_fue_imputado"].any())

    def test_mediana_se_aplica_en_grupo_suficiente(self):
        """Comprueba la mediana de precio sin usar un promedio global."""
        retail = pd.DataFrame({
            "farmacia": ["A"] * 4, "marca_comercial": ["M"] * 4,
            "principio_activo": ["P"] * 4, "precio_bs": [10.0, 20.0, 30.0, None],
            "estado_stock": ["DISPONIBLE"] * 4, "stock_disponible_binario": [1] * 4,
        })
        result = module.impute_prices(retail, minimum_observations=3)
        self.assertEqual(result.loc[3, "precio_bs_imputado"], 20.0)
        self.assertTrue(bool(result.loc[3, "precio_fue_imputado"]))

    def test_moda_se_aplica_en_grupo_suficiente(self):
        """Comprueba una moda única para completar estado de stock."""
        retail = pd.DataFrame({
            "farmacia": ["A"] * 4, "marca_comercial": ["M"] * 4,
            "principio_activo": ["P"] * 4, "precio_bs": [10.0] * 4,
            "estado_stock": ["DISPONIBLE", "DISPONIBLE", "AGOTADO", None],
            "stock_disponible_binario": [1, 1, 0, None],
        })
        result = module.impute_stock_status(retail, minimum_observations=3)
        self.assertEqual(result.loc[3, "estado_stock_imputado"], "DISPONIBLE")
        self.assertTrue(bool(result.loc[3, "stock_fue_imputado"]))

    def test_grupos_pequenos_no_se_imputan(self):
        """Comprueba que sin mínimo de evidencia se mantiene el faltante."""
        retail = pd.DataFrame({
            "farmacia": ["A", "A", "A"], "marca_comercial": ["M"] * 3,
            "principio_activo": ["P"] * 3, "precio_bs": [10.0, 20.0, None],
            "estado_stock": ["DISPONIBLE", "AGOTADO", None],
            "stock_disponible_binario": [1, 0, None],
        })
        result = module.apply_conservative_imputation(retail, minimum_observations=3)
        self.assertTrue(pd.isna(result.loc[2, "precio_bs_imputado"]))
        self.assertTrue(pd.isna(result.loc[2, "estado_stock_imputado"]))

    def test_anillos_no_se_imputan(self):
        """Comprueba que el proceso no crea una clasificación territorial."""
        retail = pd.DataFrame({
            "farmacia": ["A"], "marca_comercial": ["M"], "principio_activo": ["P"],
            "precio_bs": [10.0], "estado_stock": ["DISPONIBLE"],
            "stock_disponible_binario": [1], "anillo_asignado": [None],
        })
        result = module.apply_conservative_imputation(retail)
        self.assertTrue(pd.isna(result.loc[0, "anillo_asignado"]))

    def test_union_no_crea_observaciones_adicionales(self):
        """Comprueba que el cruce conserva exactamente las filas retail."""
        retail = pd.DataFrame({
            "timestamp": ["2026-10-19T10:00:00+00:00", "2026-10-19T11:00:00+00:00"],
            "farmacia": ["A", "A"], "marca_comercial": ["M", "M"],
            "principio_activo": ["P", "P"], "precio_bs": [1.0, 2.0],
            "estado_stock": ["DISPONIBLE", "AGOTADO"], "stock_disponible_binario": [1, 0],
        })
        result = module.merge_retail_with_calendar(retail, self.calendar)
        self.assertEqual(len(result), len(retail))
        self.assertTrue(result["dia_pago_renta"].notna().all())


if __name__ == "__main__":
    unittest.main()
