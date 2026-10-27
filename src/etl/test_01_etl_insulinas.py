"""Pruebas unitarias para el pipeline ETL de Insulinas Retail (US-22 / SCRUM-36)."""

from pathlib import Path
import unittest
import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


class TestETLInsulinas(unittest.TestCase):
    """Verifica la calidad y criterios de aceptación del dataset maestro de insulinas."""

    @classmethod
    def setUpClass(cls):
        cls.master_file = PROCESSED_DIR / "insulinas_master.csv"
        cls.discard_file = PROCESSED_DIR / "descartes_insumos_desechables.csv"
        cls.json_file = PROCESSED_DIR / "insulinas_master.json"

    def test_archivos_generados(self):
        """Verifica que existan el maestro CSV, JSON y la bitácora de descartes."""
        self.assertTrue(self.master_file.exists(), f"Falta {self.master_file}")
        self.assertTrue(self.discard_file.exists(), f"Falta {self.discard_file}")
        self.assertTrue(self.json_file.exists(), f"Falta {self.json_file}")

    def test_cuadratura_y_pureza_insulinas(self):
        """Verifica que el maestro contenga 43 insulinas puras y 9 descartes auditados."""
        df_m = pd.read_csv(self.master_file)
        df_d = pd.read_csv(self.discard_file)
        self.assertEqual(len(df_m), 43, "El catálogo maestro debe contener exactamente 43 insulinas puras.")
        self.assertEqual(len(df_d), 9, "Deben existir exactamente 9 descartes de insumos desechables/fármacos no insulina.")

    def test_columnas_requeridas(self):
        """Verifica que el dataset maestro contenga los 25 atributos clínicos y económicos."""
        df_m = pd.read_csv(self.master_file)
        self.assertGreaterEqual(len(df_m.columns), 25, "El maestro debe tener al menos 25 columnas.")
        self.assertIn("precio_venta_bs", df_m.columns)
        self.assertIn("precio_por_100ui_bs", df_m.columns)
        self.assertIn("tipo_accion", df_m.columns)
        self.assertIn("semaforo_stock", df_m.columns)


if __name__ == "__main__":
    unittest.main()
