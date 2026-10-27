"""Pruebas de preparación de datos para SCRUM-42; no prueba ni calcula lags."""

from pathlib import Path

import pandas as pd

from fusion_importaciones_stock import (
    RAW_DIR,
    build_import_retail_mapping,
    build_monthly_import_retail_fusion,
    build_monthly_retail_summary,
    build_prepared_import_lags,
    build_retail_history,
    build_santa_cruz_import_monthly,
    normalize_stock_status,
)


def test_latest_no_duplica_snapshot_historico():
    history, metrics = build_retail_history()
    assert metrics["snapshots_detectados"] == 5
    assert metrics["snapshots_unicos"] == 4
    assert "insulina_precios_stock_latest.csv" not in set(history["archivo_origen"])


def test_snapshots_identicos_se_deduplican(tmp_path: Path):
    snapshot = "id_origen,farmacia,nombre_comercial,timestamp,estado_stock\n1,F,Lantus,2026-10-19T00:00:00Z,Disponible\n"
    (tmp_path / "insulina_precios_stock_a.csv").write_text(snapshot)
    (tmp_path / "insulina_precios_stock_b.csv").write_text(snapshot)
    history, metrics = build_retail_history(tmp_path)
    assert metrics["snapshots_detectados"] == 2
    assert metrics["snapshots_unicos"] == 1
    assert len(history) == 1


def test_fecha_periodo_y_disponibilidad_se_normalizan():
    history, _ = build_retail_history()
    assert set(history["fecha_periodo"]) == {"2026-10"}
    assert normalize_stock_status("Agotado") == ("AGOTADO", 0)
    assert normalize_stock_status("Últimas unidades") == ("ULTIMAS_UNIDADES", 1)
    assert normalize_stock_status("Disponible") == ("DISPONIBLE", 1)


def test_resumen_tasa_disponibilidad_valida():
    history, _ = build_retail_history()
    summary = build_monthly_retail_summary(history)
    assert summary["tasa_disponibilidad"].between(0, 1).all()
    assert set(summary["fecha_periodo"]) == {"2026-10"}
    assert "marca_comercial" in summary.columns
    assert (summary["productos_disponibles"] <= summary["productos_observados"]).all()
    assert (
        summary["productos_observados"]
        == summary["productos_stock_normal"]
        + summary["productos_ultimas_unidades"]
        + summary["productos_agotados"]
    ).all()
    assert (
        summary["productos_disponibles"]
        == summary["productos_stock_normal"] + summary["productos_ultimas_unidades"]
    ).all()


def test_no_mapeable_y_muchos_a_muchos_se_explicitan(tmp_path: Path):
    history = pd.DataFrame({"nombre_comercial": ["Lantus Solostar", "Toujeo SoloStar"]})
    imports = pd.DataFrame({"descripcion_comercial": ["Lantus / Toujeo", "Marca inexistente"]})
    import_path = tmp_path / "importaciones.csv"
    imports.to_csv(import_path, index=False)
    mapping = build_import_retail_mapping(history, import_path)
    multiple = mapping[mapping["descripcion_importacion_original"] == "Lantus / Toujeo"]
    assert (multiple["cardinalidad"] == "MUCHOS_A_MUCHOS").all()
    unmapped = mapping[mapping["descripcion_importacion_original"] == "Marca inexistente"].iloc[0]
    assert unmapped["tipo_match"] == "NO_MAPEABLE"
    assert bool(unmapped["requiere_revision"])


def test_resumen_retail_no_contiene_lags():
    history, _ = build_retail_history()
    summary = build_monthly_retail_summary(history)
    assert not any("lag" in column.lower() for column in summary.columns)


def test_lags_preparados_de_2026_10_corresponden_a_meses_anteriores():
    prepared = build_prepared_import_lags(build_santa_cruz_import_monthly())
    october = prepared.loc[prepared["fecha_periodo"] == "2026-10"].iloc[0]
    for months, period in [(1, "2026-09"), (2, "2026-08"), (3, "2026-07")]:
        source = prepared.loc[prepared["fecha_periodo"] == period].iloc[0]
        assert october[f"kilos_netos_lag_{months}m"] == source["total_kilos_netos"]
        assert october[f"valor_cif_usd_lag_{months}m"] == source["total_valor_cif_usd"]
        assert october[f"viales_estimados_lag_{months}m"] == source["total_viales_estimados"]
        assert october[f"ui_estimadas_lag_{months}m"] == source["total_ui_estimadas"]


def test_primeros_lags_y_metadatos_no_estiman_lag():
    prepared = build_prepared_import_lags(build_santa_cruz_import_monthly())
    first = prepared.iloc[0]
    assert pd.isna(first["kilos_netos_lag_1m"])
    assert pd.isna(first["kilos_netos_lag_2m"])
    assert pd.isna(first["kilos_netos_lag_3m"])
    assert prepared["lag_preparado"].all()
    assert not prepared["lag_estimado_estadisticamente"].any()
    assert set(prepared["fuente_importacion_estado"]) == {"NO_VALIDADA_OFICIALMENTE"}
    assert set(prepared["fuente_importacion_tipo"]) == {"DATASET_GENERADO_POR_ETL"}


def test_fusion_conserva_unicamente_retail_existente_y_calidad():
    history, _ = build_retail_history()
    retail = build_monthly_retail_summary(history)
    prepared = build_prepared_import_lags(build_santa_cruz_import_monthly())
    fusion = build_monthly_import_retail_fusion(retail, prepared)
    assert len(fusion) == len(retail[retail["fecha_periodo"] == "2026-10"])
    assert set(fusion["fecha_periodo"]) == {"2026-10"}
    assert (fusion["cobertura_retail_meses"] == 1).all()
    assert not fusion["suficiente_para_estimacion_lag"].any()
    assert not fusion["lag_estimado_estadisticamente"].any()
    assert set(fusion["fuente_importacion_estado"]) == {"NO_VALIDADA_OFICIALMENTE"}
    assert set(fusion["fuente_importacion_tipo"]) == {"DATASET_GENERADO_POR_ETL"}
    assert fusion["tasa_disponibilidad"].between(0, 1).all()
