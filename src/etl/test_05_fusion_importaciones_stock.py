"""Pruebas de preparación de datos para US-27 / SCRUM-42 (Fusión e Importaciones-Stock)."""

from pathlib import Path
import sys
import tempfile
import unittest
import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import importlib
try:
    _fusion_mod = importlib.import_module("src.etl.05_fusion_importaciones_stock")
except ImportError:
    _fusion_mod = importlib.import_module("05_fusion_importaciones_stock")

RAW_DIR = _fusion_mod.RAW_DIR
build_import_retail_mapping = _fusion_mod.build_import_retail_mapping
build_monthly_import_retail_fusion = _fusion_mod.build_monthly_import_retail_fusion
build_monthly_retail_summary = _fusion_mod.build_monthly_retail_summary
build_prepared_import_lags = _fusion_mod.build_prepared_import_lags
build_retail_history = _fusion_mod.build_retail_history
build_santa_cruz_import_monthly = _fusion_mod.build_santa_cruz_import_monthly
normalize_stock_status = _fusion_mod.normalize_stock_status


class TestFusionImportacionesStock(unittest.TestCase):
    """Pruebas de validación de la fusión sin estimación estadística de lags."""

    def test_snapshots_historicos_detectados(self):
        history, metrics = build_retail_history()
        self.assertGreaterEqual(metrics["snapshots_detectados"], 1)
        self.assertGreaterEqual(metrics["snapshots_unicos"], 1)
        self.assertGreaterEqual(len(history), 1)

    def test_snapshots_identicos_se_deduplican(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            snapshot = "id_origen,farmacia,nombre_comercial,timestamp,estado_stock\n1,F,Lantus,2026-10-19T00:00:00Z,Disponible\n"
            (tmp_path / "insulina_precios_stock_a.csv").write_text(snapshot)
            (tmp_path / "insulina_precios_stock_b.csv").write_text(snapshot)
            history, metrics = build_retail_history(tmp_path)
            self.assertEqual(metrics["snapshots_detectados"], 2)
            self.assertEqual(metrics["snapshots_unicos"], 1)
            self.assertEqual(len(history), 1)

    def test_fecha_periodo_y_disponibilidad_se_normalizan(self):
        history, _ = build_retail_history()
        self.assertEqual(set(history["fecha_periodo"]), {"2026-10"})
        self.assertEqual(normalize_stock_status("Agotado"), ("AGOTADO", 0))
        self.assertEqual(normalize_stock_status("Últimas unidades"), ("ULTIMAS_UNIDADES", 1))
        self.assertEqual(normalize_stock_status("Disponible"), ("DISPONIBLE", 1))

    def test_resumen_tasa_disponibilidad_valida(self):
        history, _ = build_retail_history()
        summary = build_monthly_retail_summary(history)
        self.assertTrue(summary["tasa_disponibilidad"].between(0, 1).all())
        self.assertEqual(set(summary["fecha_periodo"]), {"2026-10"})
        self.assertIn("marca_comercial", summary.columns)
        self.assertTrue((summary["productos_disponibles"] <= summary["productos_observados"]).all())

    def test_no_mapeable_y_muchos_a_muchos_se_explicitan(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            history = pd.DataFrame({"nombre_comercial": ["Lantus Solostar", "Toujeo SoloStar"]})
            imports = pd.DataFrame({"descripcion_comercial": ["Lantus / Toujeo", "Marca inexistente"]})
            import_path = tmp_path / "importaciones.csv"
            imports.to_csv(import_path, index=False)
            mapping = build_import_retail_mapping(history, import_path)
            multiple = mapping[mapping["descripcion_importacion_original"] == "Lantus / Toujeo"]
            self.assertTrue((multiple["cardinalidad"] == "MUCHOS_A_MUCHOS").all())
            unmapped = mapping[mapping["descripcion_importacion_original"] == "Marca inexistente"].iloc[0]
            self.assertEqual(unmapped["tipo_match"], "NO_MAPEABLE")
            self.assertTrue(bool(unmapped["requiere_revision"]))

    def test_lags_preparados_de_2026_10_corresponden_a_meses_anteriores(self):
        prepared = build_prepared_import_lags(build_santa_cruz_import_monthly())
        october = prepared.loc[prepared["fecha_periodo"] == "2026-10"].iloc[0]
        for months, period in [(1, "2026-09"), (2, "2026-08"), (3, "2026-07")]:
            source = prepared.loc[prepared["fecha_periodo"] == period].iloc[0]
            self.assertEqual(october[f"kilos_netos_lag_{months}m"], source["total_kilos_netos"])
            self.assertEqual(october[f"valor_cif_usd_lag_{months}m"], source["total_valor_cif_usd"])

    def test_fusion_conserva_unicamente_retail_existente_y_calidad(self):
        history, _ = build_retail_history()
        retail = build_monthly_retail_summary(history)
        prepared = build_prepared_import_lags(build_santa_cruz_import_monthly())
        fusion = build_monthly_import_retail_fusion(retail, prepared)
        self.assertEqual(len(fusion), len(retail[retail["fecha_periodo"] == "2026-10"]))
        self.assertEqual(set(fusion["fecha_periodo"]), {"2026-10"})
        self.assertTrue((fusion["cobertura_retail_meses"] == 1).all())
        self.assertFalse(fusion["lag_estimado_estadisticamente"].any())


if __name__ == "__main__":
    unittest.main()
