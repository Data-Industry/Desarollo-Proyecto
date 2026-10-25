"""
Suite de Pruebas Automatizadas para US-16 (SCRUM-20): Auditoría de Calidad y EDA Multivariable
"""

import os
import unittest
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
FIGURES_DIR = os.path.join(PROJECT_DIR, "docs", "figures")

class TestEDAMultivariable(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fig_paths = [
            os.path.join(FIGURES_DIR, "eda_fig1_distribucion_precios_farmacias.png"),
            os.path.join(FIGURES_DIR, "eda_fig2_evolucion_costo_importacion_tc.png"),
            os.path.join(FIGURES_DIR, "eda_fig3_comparativa_cadenas_farmacias.png"),
            os.path.join(FIGURES_DIR, "eda_fig4_participacion_paises_origen.png"),
            os.path.join(FIGURES_DIR, "eda_fig5_matriz_correlacion_multifuente.png")
        ]
        cls.table_cadenas = os.path.join(PROCESSED_DIR, "eda_metricas_resumen_farmacias.csv")
        cls.table_farmaco = os.path.join(PROCESSED_DIR, "eda_metricas_por_principio_activo.csv")
        cls.table_paises = os.path.join(PROCESSED_DIR, "eda_metricas_resumen_importaciones.csv")
        cls.table_dispersion = os.path.join(PROCESSED_DIR, "eda_dispersion_marcas_cadenas.csv")

    def test_01_figuras_generadas(self):
        """Verifica que las 5 figuras estadísticas del EDA existan y pesen más de 50 KB."""
        for p in self.fig_paths:
            self.assertTrue(os.path.exists(p), f"No existe la figura: {p}")
            self.assertGreater(os.path.getsize(p), 50000, f"Figura demasiado pequeña: {p}")

    def test_02_tablas_resumen_existencia(self):
        """Verifica que las 4 tablas analíticas del EDA se hayan exportado a data/processed/."""
        for p in [self.table_cadenas, self.table_farmaco, self.table_paises, self.table_dispersion]:
            self.assertTrue(os.path.exists(p), f"No existe la tabla: {p}")
            self.assertGreater(os.path.getsize(p), 0, f"Tabla vacía: {p}")

    def test_03_auditoria_calidad_cadenas(self):
        """Verifica métricas de las 3 farmacias (Chávez, Farmacorp, Telchi)."""
        df = pd.read_csv(self.table_cadenas)
        self.assertEqual(len(df), 3, "Deben figurar exactamente 3 cadenas farmacéuticas")
        cadenas = set(df["farmacia"].unique())
        self.assertTrue({"Farmacias Chávez", "Farmacorp", "Farmacias Telchi"}.issubset(cadenas))
        self.assertTrue((df["precio_min"] > 0).all())
        self.assertTrue((df["disponibilidad_stock_pct"] > 80).all())

    def test_04_analisis_dispersion_brechas(self):
        """Verifica que se detecten brechas de precios para medicamentos idénticos entre cadenas."""
        df = pd.read_csv(self.table_dispersion)
        self.assertGreater(len(df), 0)
        # Novolin debe presentar brecha de precios positiva
        novolin_row = df[df["marca_comercial"] == "Novolin R"]
        self.assertFalse(novolin_row.empty)
        self.assertGreater(float(novolin_row["brecha_precio_bs"].values[0]), 0)

    def test_05_cuota_paises_importacion(self):
        """Verifica agregación por país de origen en las importaciones."""
        df = pd.read_csv(self.table_paises)
        paises_clave = {"Alemania", "Francia", "Dinamarca", "India"}
        paises_presentes = set(df["pais_origen"].unique())
        self.assertTrue(paises_clave.issubset(paises_presentes))
        self.assertTrue((df["total_kilos_netos"] > 0).all())
        self.assertTrue((df["costo_cif_usd_kg_medio"] > 150).all())

if __name__ == "__main__":
    unittest.main()
