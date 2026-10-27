"""Suite de Pruebas Automatizadas para US-16 (SCRUM-20): Auditoría de Calidad y EDA Multifuente."""

from pathlib import Path
import unittest
import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
FIGURES_DIR = PROJECT_DIR / "docs" / "figures"


class TestEDAMultivariable(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fig_paths = [
            FIGURES_DIR / "eda_fig1_distribucion_precios_farmacias.png",
            FIGURES_DIR / "eda_fig2_evolucion_costo_importacion_tc.png",
            FIGURES_DIR / "eda_fig3_comparativa_cadenas_farmacias.png",
            FIGURES_DIR / "eda_fig4_participacion_paises_origen.png",
            FIGURES_DIR / "eda_fig5_matriz_correlacion_multifuente.png",
            FIGURES_DIR / "eda_fig6_geolocalizacion_anillos_scz.png",
        ]
        cls.table_cadenas = PROCESSED_DIR / "eda_metricas_resumen_farmacias.csv"
        cls.table_farmaco = PROCESSED_DIR / "eda_metricas_por_principio_activo.csv"
        cls.table_paises = PROCESSED_DIR / "eda_metricas_resumen_importaciones.csv"
        cls.table_dispersion = PROCESSED_DIR / "eda_dispersion_marcas_cadenas.csv"
        cls.table_fusion = PROCESSED_DIR / "eda_metricas_fusion_importaciones_stock.csv"
        cls.table_anillos = PROCESSED_DIR / "eda_metricas_cobertura_anillos.csv"
        cls.audit_json = PROCESSED_DIR / "eda_calidad_auditoria_completa.json"

    def test_01_figuras_generadas(self):
        """Verifica que las 6 figuras estadísticas del EDA existan y pesen más de 40 KB."""
        for p in self.fig_paths:
            self.assertTrue(p.exists(), f"No existe la figura: {p}")
            self.assertGreater(p.stat().st_size, 40000, f"Figura demasiado pequeña: {p}")

    def test_02_tablas_resumen_existencia(self):
        """Verifica que las tablas analíticas del EDA se hayan exportado a data/processed/."""
        for p in [self.table_cadenas, self.table_farmaco, self.table_paises, self.table_dispersion, self.table_fusion, self.table_anillos]:
            self.assertTrue(p.exists(), f"No existe la tabla: {p}")
            self.assertGreater(p.stat().st_size, 0, f"Tabla vacía: {p}")
        self.assertTrue(self.audit_json.exists(), "No existe el archivo de auditoría JSON.")

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
        novolin_row = df[df["marca_comercial"] == "Novolin R"]
        self.assertFalse(novolin_row.empty)
        self.assertGreater(float(novolin_row["brecha_precio_bs"].values[0]), 0)

    def test_05_integracion_fusion_us27(self):
        """Verifica que las métricas de la fusión mensual incorporen el resumen de US-27."""
        df = pd.read_csv(self.table_fusion)
        self.assertFalse(df.empty)
        self.assertIn("tasa_disponibilidad_media", df.columns)
        self.assertIn("cif_usd_lag_1m", df.columns)
        self.assertTrue((df["tasa_disponibilidad_media"] > 0.8).all())

    def test_06_integracion_anillos_us03(self):
        """Verifica que el EDA incorpore la distribución territorial de sucursales por anillo."""
        df = pd.read_csv(self.table_anillos)
        self.assertFalse(df.empty)
        self.assertIn("anillo_asignado", df.columns)
        self.assertIn("sucursales_conteo", df.columns)


if __name__ == "__main__":
    unittest.main()
