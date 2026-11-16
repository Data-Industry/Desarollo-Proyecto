"""Pruebas aisladas del refresh de producción web (SCRUM-52 / US-37)."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.pipeline import refresh_production_web as pipeline


class FixtureModel:
    """Modelo mínimo serializable para probar inferencia sin tocar los joblib reales."""

    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        probabilities = np.linspace(0.2, 0.8, len(features))
        return np.column_stack([1.0 - probabilities, probabilities])


class TestRefreshProductionWeb(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.raw_dir = self.root / "data" / "raw"
        self.processed_dir = self.root / "data" / "processed"
        self.model_dir = self.root / "models"
        self.ui_dir = self.root / "src" / "ui"
        for directory in (self.raw_dir, self.processed_dir, self.model_dir, self.ui_dir):
            directory.mkdir(parents=True, exist_ok=True)

        self.now = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)
        self.snapshot_path = self.raw_dir / "insulina_precios_stock_20261115_110000.csv"
        self.snapshot = pd.DataFrame([
            {
                "id_origen": "FARMACORP-1",
                "farmacia": "Farmacorp",
                "nombre_comercial": "Lantus Insulina Glargina 100 UI 10 ml",
                "precio_bs": 100.0,
                "precio_regular_bs": 110.0,
                "estado_stock": "Disponible",
                "url_producto": "https://farmacorp.example/producto/1",
                "timestamp": (self.now - timedelta(hours=1)).isoformat(),
            },
            {
                "id_origen": "TELCHI-2",
                "farmacia": "Farmacias Telchi",
                "nombre_comercial": "Novolin N Insulina 100 UI 10 ml",
                "precio_bs": 200.0,
                "precio_regular_bs": 200.0,
                "estado_stock": "Disponible",
                "url_producto": "https://telchi.example/producto/2",
                "timestamp": (self.now - timedelta(hours=2)).isoformat(),
            },
        ])
        self._write_snapshot(self.snapshot)

        self.bcb_path = self.processed_dir / "tipo_cambio_diario_bcb.csv"
        self._write_bcb(self.now - timedelta(days=1))

        self.branches_path = self.processed_dir / "farmacias_geolocalizadas.csv"
        self.branches = pd.DataFrame([
            {
                "farmacia": "Farmacorp",
                "id_sucursal": "SC-1",
                "nombre_sucursal": "Sucursal Piraí",
                "direccion": "Av. Piraí esq. 2do Anillo",
                "ciudad": "Santa Cruz de la Sierra",
                "anillo_asignado": 2,
                "estado_anillo": "ASIGNADO",
                "fuente": "https://farmacorp.example/sucursales",
                "fecha_verificacion": "2026-11-14",
                "advertencias": "",
            }
        ])
        self.branches.to_csv(self.branches_path, index=False)

        self.model_path = self.model_dir / "modelo_produccion_stock.joblib"
        joblib.dump(FixtureModel(), self.model_path)
        self.metadata_path = self.model_dir / "modelo_metadata.json"
        self.metadata = {
            "modelo_produccion": "FixtureModel",
            "umbral_clinico_produccion": 0.5,
            "caracteristicas_numericas": ["precio_venta_bs"],
            "caracteristicas_categoricas": ["farmacia"],
        }
        self.metadata_path.write_text(json.dumps(self.metadata), encoding="utf-8")

        self.paths = pipeline.RefreshPaths(
            raw_dir=self.raw_dir,
            bcb_path=self.bcb_path,
            branches_path=self.branches_path,
            model_path=self.model_path,
            model_metadata_path=self.metadata_path,
            root_html=self.root / "mvp_comparador_jubilados.html",
            ui_html=self.ui_dir / "mvp_comparador_jubilados.html",
            manifest_path=self.processed_dir / "web_bundle_manifest.json",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_snapshot(self, frame: pd.DataFrame) -> Path:
        frame.to_csv(self.snapshot_path, index=False)
        return self.snapshot_path

    def _write_bcb(self, date: datetime, value: float = 12.09, source: str = "Banco Central de Bolivia") -> None:
        pd.DataFrame([{
            "fecha_iso": date.date().isoformat(),
            "tipo_cambio_oficial_bob_usd": value,
            "fuente_oficial": source,
        }]).to_csv(self.bcb_path, index=False)

    def _validated_products(self) -> tuple[pipeline.SnapshotSelection, pd.DataFrame]:
        selection = pipeline.resolve_snapshot(self.raw_dir)
        raw, _ = pipeline.validate_snapshot(selection, now=self.now)
        return selection, pipeline.prepare_products(raw)

    def _candidate(self) -> tuple[str, dict, pd.DataFrame, pd.DataFrame]:
        selection, products = self._validated_products()
        products, metadata, model_hash = pipeline.run_model_inference(
            products, self.model_path, self.metadata_path
        )
        bcb, _ = pipeline.validate_bcb(self.bcb_path, now=self.now)
        branches = pipeline.prepare_branches(self.branches_path)
        fingerprint = pipeline.calculate_input_fingerprint(
            selection, bcb, self.branches_path, model_hash, self.metadata_path
        )
        manifest = pipeline.build_manifest(
            selection, products, branches, bcb, metadata, model_hash,
            pipeline.risk_stock_warnings(products), fingerprint, self.now,
        )
        html = pipeline.build_candidate_html(products, branches, manifest)
        return html, manifest, products, branches

    def test_01_snapshot_existe_y_se_resuelve(self) -> None:
        older_latest = self.snapshot.copy()
        older_latest["timestamp"] = (self.now - timedelta(days=1)).isoformat()
        older_latest.to_csv(self.raw_dir / "insulina_precios_stock_latest.csv", index=False)
        selection = pipeline.resolve_snapshot(self.raw_dir)
        self.assertTrue(selection.path.exists())
        self.assertEqual(selection.path, self.snapshot_path)

    def test_02_snapshot_no_vacio(self) -> None:
        selection = pipeline.resolve_snapshot(self.raw_dir)
        validated, _ = pipeline.validate_snapshot(selection, now=self.now)
        self.assertFalse(validated.empty)

    def test_03_existe_al_menos_un_producto_valido(self) -> None:
        _, products = self._validated_products()
        self.assertGreater(len(products), 0)

    def test_04_precio_actual_debe_ser_positivo(self) -> None:
        invalid = self.snapshot.copy()
        invalid.loc[0, "precio_bs"] = 0
        self._write_snapshot(invalid)
        with self.assertRaisesRegex(pipeline.InputValidationError, "INVALID_PRICE"):
            pipeline.validate_snapshot(pipeline.resolve_snapshot(self.raw_dir), now=self.now)

    def test_05_precio_regular_debe_ser_coherente(self) -> None:
        invalid = self.snapshot.copy()
        invalid.loc[0, "precio_regular_bs"] = 50
        self._write_snapshot(invalid)
        with self.assertRaisesRegex(pipeline.InputValidationError, "INVALID_REGULAR_PRICE"):
            pipeline.validate_snapshot(pipeline.resolve_snapshot(self.raw_dir), now=self.now)

    def test_06_timestamp_debe_ser_valido(self) -> None:
        invalid = self.snapshot.copy()
        invalid.loc[0, "timestamp"] = "fecha-imposible"
        self._write_snapshot(invalid)
        selection = pipeline.SnapshotSelection(self.snapshot_path, pipeline.sha256_file(self.snapshot_path), self.now)
        with self.assertRaisesRegex(pipeline.InputValidationError, "INVALID_TIMESTAMP"):
            pipeline.validate_snapshot(selection, now=self.now)

    def test_07_farmacia_debe_estar_permitida(self) -> None:
        invalid = self.snapshot.copy()
        invalid.loc[0, "farmacia"] = "Farmacia Inventada"
        self._write_snapshot(invalid)
        with self.assertRaisesRegex(pipeline.InputValidationError, "UNKNOWN_PHARMACY"):
            pipeline.validate_snapshot(pipeline.resolve_snapshot(self.raw_dir), now=self.now)

    def test_08_url_debe_ser_valida(self) -> None:
        invalid = self.snapshot.copy()
        invalid.loc[0, "url_producto"] = ""
        self._write_snapshot(invalid)
        with self.assertRaisesRegex(pipeline.InputValidationError, "INVALID_URL"):
            pipeline.validate_snapshot(pipeline.resolve_snapshot(self.raw_dir), now=self.now)

    def test_09_estado_normalizado_pertenece_al_catalogo(self) -> None:
        selection = pipeline.resolve_snapshot(self.raw_dir)
        validated, _ = pipeline.validate_snapshot(selection, now=self.now)
        self.assertTrue(set(validated["stock_actual"]).issubset(pipeline.ALLOWED_STOCK_STATES))

    def test_10_estado_desconocido_no_se_vuelve_disponible(self) -> None:
        unknown = self.snapshot.copy()
        unknown.loc[0, "estado_stock"] = "estado raro"
        self._write_snapshot(unknown)
        validated, _ = pipeline.validate_snapshot(pipeline.resolve_snapshot(self.raw_dir), now=self.now)
        row = validated.loc[validated["id_origen"].eq("FARMACORP-1")].iloc[0]
        self.assertEqual(row["stock_actual"], "NO_VERIFICADO")
        self.assertNotEqual(row["stock_actual"], "DISPONIBLE")

    def test_11_telchi_catalogo_es_no_verificado(self) -> None:
        validated, warnings = pipeline.validate_snapshot(pipeline.resolve_snapshot(self.raw_dir), now=self.now)
        row = validated.loc[validated["farmacia"].eq("Farmacias Telchi")].iloc[0]
        self.assertEqual(row["stock_actual"], "NO_VERIFICADO")
        self.assertEqual(row["stock_evidence"], "CATALOG_ONLY")
        self.assertTrue(any("STOCK_UNVERIFIED" in warning for warning in warnings))

    def test_12_probabilidad_debe_estar_entre_cero_y_uno(self) -> None:
        predictions = pd.DataFrame([{
            "id_insulina_master": "A", "probabilidad_riesgo": 1.2,
            "riesgo_predictivo": "ROJO_ALTO_RIESGO", "model_threshold": 0.5,
        }])
        with self.assertRaisesRegex(pipeline.ProcessingError, "INVALID_PROBABILITY"):
            pipeline.validate_prediction_frame(predictions, ["A"], 0.5)

    def test_13_prediccion_faltante_es_error(self) -> None:
        predictions = pd.DataFrame([{
            "id_insulina_master": "A", "probabilidad_riesgo": 0.2,
            "riesgo_predictivo": "VERDE_ESTABLE", "model_threshold": 0.5,
        }])
        with self.assertRaisesRegex(pipeline.ProcessingError, "PREDICTION_MISSING"):
            pipeline.validate_prediction_frame(predictions, ["A", "B"], 0.5)

    def test_14_semaforo_debe_estar_permitido(self) -> None:
        predictions = pd.DataFrame([{
            "id_insulina_master": "A", "probabilidad_riesgo": 0.2,
            "riesgo_predictivo": "AZUL", "model_threshold": 0.5,
        }])
        with self.assertRaisesRegex(pipeline.ProcessingError, "INVALID_RISK_STATE"):
            pipeline.validate_prediction_frame(predictions, ["A"], 0.5)

    def test_15_umbral_debe_coincidir_con_metadata(self) -> None:
        predictions = pd.DataFrame([{
            "id_insulina_master": "A", "probabilidad_riesgo": 0.2,
            "riesgo_predictivo": "VERDE_ESTABLE", "model_threshold": 0.4,
        }])
        with self.assertRaisesRegex(pipeline.ProcessingError, "THRESHOLD_MISMATCH"):
            pipeline.validate_prediction_frame(predictions, ["A"], 0.5)

    def test_16_bcb_valido_declara_bob_por_usd(self) -> None:
        bcb, warnings = pipeline.validate_bcb(self.bcb_path, now=self.now)
        self.assertGreater(bcb["value"], 0)
        self.assertEqual(bcb["direction"], "BOB_PER_USD")
        self.assertEqual(warnings, [])

    def test_17_bcb_antiguo_es_error(self) -> None:
        self._write_bcb(self.now - timedelta(days=pipeline.BCB_ERROR_DAYS + 1))
        with self.assertRaisesRegex(pipeline.InputValidationError, "BCB_STALE"):
            pipeline.validate_bcb(self.bcb_path, now=self.now)

    def test_18_sin_evidencia_conserva_anillo_nulo(self) -> None:
        branches = self.branches.copy()
        branches.loc[0, ["estado_anillo", "anillo_asignado"]] = ["SIN_EVIDENCIA", np.nan]
        branches.to_csv(self.branches_path, index=False)
        prepared = pipeline.prepare_branches(self.branches_path)
        self.assertTrue(pd.isna(prepared.loc[0, "anillo_asignado"]))
        self.assertEqual(prepared.loc[0, "estado_anillo"], "SIN_EVIDENCIA")

    def test_19_ambiguo_conserva_anillo_nulo(self) -> None:
        branches = self.branches.copy()
        branches.loc[0, ["estado_anillo", "anillo_asignado"]] = ["AMBIGUO_EN_BORDE", np.nan]
        branches.to_csv(self.branches_path, index=False)
        prepared = pipeline.prepare_branches(self.branches_path)
        self.assertTrue(pd.isna(prepared.loc[0, "anillo_asignado"]))
        self.assertEqual(prepared.loc[0, "estado_anillo"], "AMBIGUO_EN_BORDE")

    def test_20_bundle_candidato_no_esta_vacio(self) -> None:
        html, manifest, _, _ = self._candidate()
        pipeline.validate_candidate_html(html, manifest)
        self.assertGreater(len(html), 1000)

    def test_21_manifest_contiene_metadata_obligatoria(self) -> None:
        _, manifest, _, _ = self._candidate()
        pipeline.validate_manifest(manifest)
        self.assertEqual(manifest["bundle_schema_version"], 1)
        self.assertIn("source_snapshot", manifest)
        self.assertIn("model", manifest)

    def test_22_html_contiene_datos_del_candidato(self) -> None:
        html, manifest, products, _ = self._candidate()
        self.assertIn(manifest["source_snapshot"]["filename"], html)
        self.assertIn(products.iloc[0]["marca_comercial"], html)
        self.assertIn("stock_actual", html)
        self.assertIn("riesgo_predictivo", html)

    def test_23_html_no_contiene_placeholders_criticos(self) -> None:
        html, manifest, _, _ = self._candidate()
        pipeline.validate_candidate_html(html, manifest)
        self.assertNotRegex(html, r"\bTODO\b|\bPLACEHOLDER\b|__BUNDLE_[A-Z_]+__|\bNaN\b")

    def test_24_fallo_no_modifica_produccion(self) -> None:
        self.paths.root_html.write_text("HTML_ANTERIOR", encoding="utf-8")
        self.paths.ui_html.write_text("UI_ANTERIOR", encoding="utf-8")
        self.paths.manifest_path.write_text('{"anterior": true}', encoding="utf-8")
        invalid = self.snapshot.copy()
        invalid.loc[0, "precio_bs"] = 0
        self._write_snapshot(invalid)
        with self.assertRaises(pipeline.InputValidationError):
            pipeline.run_refresh(paths=self.paths, now=self.now)
        self.assertEqual(self.paths.root_html.read_text(encoding="utf-8"), "HTML_ANTERIOR")
        self.assertEqual(self.paths.ui_html.read_text(encoding="utf-8"), "UI_ANTERIOR")
        self.assertEqual(self.paths.manifest_path.read_text(encoding="utf-8"), '{"anterior": true}')

    def test_25_ejecucion_repetida_es_idempotente(self) -> None:
        first = pipeline.run_refresh(paths=self.paths, now=self.now)
        first_html_hash = pipeline.sha256_file(self.paths.root_html)
        first_manifest = self.paths.manifest_path.read_bytes()
        second = pipeline.run_refresh(paths=self.paths, now=self.now + timedelta(minutes=1))
        self.assertEqual(first["status"], "PUBLISHED")
        self.assertEqual(second["status"], "NO_CHANGES")
        self.assertEqual(pipeline.sha256_file(self.paths.root_html), first_html_hash)
        self.assertEqual(self.paths.manifest_path.read_bytes(), first_manifest)


if __name__ == "__main__":
    unittest.main()
