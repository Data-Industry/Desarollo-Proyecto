"""Pruebas unitarias para el pipeline de ingesta del Tipo de Cambio Oficial del BCB (US-28)."""

from pathlib import Path
import unittest
import pandas as pd

import importlib
try:
    _mod_bcb = importlib.import_module("src.etl.02_ingesta_tipo_cambio_bcb")
except ImportError:
    _mod_bcb = importlib.import_module("02_ingesta_tipo_cambio_bcb")

BCB_DAILY_PROCESSED_CSV = _mod_bcb.BCB_DAILY_PROCESSED_CSV
BCB_MONTHLY_PROCESSED_CSV = _mod_bcb.BCB_MONTHLY_PROCESSED_CSV
BCB_RAW_CSV = _mod_bcb.BCB_RAW_CSV
get_official_exchange_rate = _mod_bcb.get_official_exchange_rate
load_raw_bcb_exchange_rate = _mod_bcb.load_raw_bcb_exchange_rate
process_bcb_exchange_rates = _mod_bcb.process_bcb_exchange_rates
run_bcb_pipeline = _mod_bcb.run_bcb_pipeline


class TestIngestaTipoCambioBCB(unittest.TestCase):
    """Conjunto de pruebas para la ingesta y normalización del tipo de cambio oficial."""

    def test_load_raw_bcb_exchange_rate(self):
        """Verifica que el archivo raw de BCB se cargue correctamente con columnas Fecha y Valor."""
        self.assertTrue(BCB_RAW_CSV.exists(), "El archivo data/raw/Tipo_de_cambio.csv debe existir.")
        df = load_raw_bcb_exchange_rate(BCB_RAW_CSV)
        self.assertFalse(df.empty)
        self.assertIn("Fecha", df.columns)
        self.assertIn("Valor", df.columns)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["Fecha"]))
        self.assertTrue(pd.api.types.is_float_dtype(df["Valor"]))

    def test_process_bcb_exchange_rates(self):
        """Verifica la agregación diaria y mensual y los rangos de valores realistas."""
        raw_df = load_raw_bcb_exchange_rate(BCB_RAW_CSV)
        daily, monthly = process_bcb_exchange_rates(raw_df)

        self.assertEqual(len(daily), len(raw_df))
        self.assertGreaterEqual(len(monthly), 70, "Deben existir al menos 70 periodos mensuales (2021-2026).")
        
        # Validar que para 2026 los valores estén entre 8 y 13 Bs/USD (según datos oficiales, no > 16)
        m_2026 = monthly[monthly["gestion"] == 2026]
        self.assertFalse(m_2026.empty)
        self.assertTrue((m_2026["tipo_cambio_promedio_bob_usd"] <= 13.0).all(), "En 2026 los valores no deben exceder 13 Bs.")
        self.assertTrue((m_2026["tipo_cambio_promedio_bob_usd"] >= 8.0).all(), "En 2026 los valores no deben ser menores a 8 Bs.")

    def test_get_official_exchange_rate(self):
        """Verifica que las consultas de tipo de cambio retornen los valores oficiales esperados."""
        # En 2021-01 el tipo de cambio oficial del BCB era 6.86
        tc_2021_1 = get_official_exchange_rate(2021, 1)
        self.assertAlmostEqual(tc_2021_1, 6.86, places=2)

        # En 2026-10 debe estar alrededor de 11.82 (media mensual oficial del archivo)
        tc_2026_10 = get_official_exchange_rate(2026, 10)
        self.assertAlmostEqual(tc_2026_10, 11.8237, places=1)
        self.assertLess(tc_2026_10, 13.0)

    def test_pipeline_execution_and_artifacts(self):
        """Verifica que run_bcb_pipeline genere los artefactos esperados en data/processed/."""
        daily, monthly = run_bcb_pipeline()
        self.assertTrue(BCB_DAILY_PROCESSED_CSV.exists())
        self.assertTrue(BCB_MONTHLY_PROCESSED_CSV.exists())
        self.assertGreater(len(daily), 2000)
        self.assertGreaterEqual(len(monthly), 70)


if __name__ == "__main__":
    unittest.main()
