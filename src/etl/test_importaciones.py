"""
Script de Pruebas Automatizadas y Validación de Criterios de Aceptación para US-21
Historia de Usuario: US-21 (SCRUM-23) - Ingesta y Normalización de Importaciones de Insulina
"""

import os
import unittest
import pandas as pd
import numpy as np
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
PROCESSED_DIR = os.path.join(PROJECT_DIR, "data", "processed")
RAW_DIR = os.path.join(PROJECT_DIR, "data", "raw")

class TestImportacionesETL(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.raw_file = os.path.join(RAW_DIR, "importaciones_aduana_bolivia_crudo.csv")
        cls.master_file = os.path.join(PROCESSED_DIR, "importaciones_insulina_bolivia.csv")
        cls.json_file = os.path.join(PROCESSED_DIR, "importaciones_insulina_bolivia.json")
        cls.discard_file = os.path.join(PROCESSED_DIR, "descartes_importaciones_no_insulina.csv")
        cls.summary_file = os.path.join(PROCESSED_DIR, "importaciones_insulina_mensual_resumen.csv")
        cls.tc_file = os.path.join(PROCESSED_DIR, "tipo_cambio_historico_bolivia.csv")

        # Cargar datasets
        cls.df_raw = pd.read_csv(cls.raw_file)
        cls.df_master = pd.read_csv(cls.master_file)
        cls.df_discard = pd.read_csv(cls.discard_file)
        cls.df_summary = pd.read_csv(cls.summary_file)
        cls.df_tc = pd.read_csv(cls.tc_file)

    def test_01_archivos_generados_y_no_vacios(self):
        """Verifica que todos los archivos requeridos existan y tengan contenido."""
        for path in [self.raw_file, self.master_file, self.json_file, self.discard_file, self.summary_file, self.tc_file]:
            self.assertTrue(os.path.exists(path), f"El archivo no existe: {path}")
            self.assertGreater(os.path.getsize(path), 0, f"El archivo está vacío: {path}")

    def test_02_filtro_estricto_subpartida_nandina(self):
        """Verifica que el dataset maestro contenga EXCLUSIVAMENTE la partida 3004.31.00.00."""
        partidas_unicas = self.df_master["subpartida_nandina"].unique()
        self.assertEqual(len(partidas_unicas), 1, "Existen múltiples partidas en el dataset maestro")
        self.assertEqual(partidas_unicas[0], "3004.31.00.00", "La partida no es 3004.31.00.00")

    def test_03_auditoria_de_descartes(self):
        """Verifica que los registros no insulina se encuentren en la bitácora de descartes con motivo válido."""
        self.assertGreater(len(self.df_discard), 0, "No se registraron descartes")
        self.assertNotIn("3004.31.00.00", self.df_discard["subpartida_nandina"].values)
        self.assertTrue(self.df_discard["motivo_descarte"].notna().all(), "Existen descartes sin motivo")

    def test_04_cuadratura_de_registros(self):
        """Verifica que total crudo = total limpio + total descartado."""
        total_crudo = len(self.df_raw)
        total_limpio = len(self.df_master)
        total_descartes = len(self.df_discard)
        self.assertEqual(total_crudo, total_limpio + total_descartes, "La suma de registros no cuadra")

    def test_05_integridad_de_campos_master(self):
        """Verifica la presencia de las variables clínicas, geográficas y financieras en el dataset maestro."""
        campos_esperados = [
            "id_importacion_master", "gestion", "mes", "fecha_periodo",
            "subpartida_nandina", "descripcion_arancelaria", "descripcion_comercial",
            "pais_origen", "codigo_iso_pais", "aduana_ingreso", "via_transporte",
            "departamento_destino", "kilos_brutos", "kilos_netos",
            "valor_cif_usd", "valor_fob_usd", "tipo_cambio_bob_usd", "regimen_cambiario",
            "valor_cif_bob", "costo_cif_kg_usd", "costo_cif_kg_bob",
            "viales_estimados_10ml", "unidades_internacionales_ui_estimadas",
            "gravamen_arancelario_pct", "autorizacion_previa_minsalud", "fuente_datos"
        ]
        for col in campos_esperados:
            self.assertIn(col, self.df_master.columns, f"Falta la columna {col} en master")

    def test_06_tipo_de_cambio_fluctuante_y_consistencia_financiera(self):
        """Verifica que el tipo de cambio sea dinámico/fluctuante y consistente con CIF BOB."""
        # Verificar que el tipo de cambio NO sea estático
        tcs_unicos = self.df_master["tipo_cambio_bob_usd"].unique()
        self.assertGreater(len(tcs_unicos), 5, "El tipo de cambio debe ser fluctuante/dinámico, no estático")
        
        # Verificar cálculo exacto de CIF BOB con el tipo de cambio fluctuante correspondiente
        cif_esperado = self.df_master["valor_cif_usd"] * self.df_master["tipo_cambio_bob_usd"]
        self.assertTrue(np.allclose(self.df_master["valor_cif_bob"], cif_esperado, atol=0.05),
                        "El cálculo de CIF BOB no coincide con el tipo de cambio fluctuante")
        
        # Verificar que en 2026 el TC sea significativamente mayor a 6.96
        tc_2026 = self.df_master[self.df_master["gestion"] == 2026]["tipo_cambio_bob_usd"].mean()
        self.assertGreater(tc_2026, 14.0, "El tipo de cambio en 2026 debe reflejar el mercado fluctuante (>14)")

    def test_07_semaforo_preventivo_en_resumen_mensual(self):
        """Verifica la presencia y validez de la clasificación del semáforo preventivo."""
        self.assertIn("semaforo_abastecimiento_upstream", self.df_summary.columns)
        self.assertIn("alerta_quiebre_importacion_binaria", self.df_summary.columns)
        self.assertIn("tipo_cambio_promedio_bob_usd", self.df_summary.columns)
        semaforos_validos = {"VERDE", "AMARILLO", "ROJO"}
        semaforos_presentes = set(self.df_summary["semaforo_abastecimiento_upstream"].unique())
        self.assertTrue(semaforos_presentes.issubset(semaforos_validos), "Existen semáforos no válidos")

    def test_08_integridad_json(self):
        """Verifica que el archivo JSON estructurado sea parseable y contenga los mismos registros."""
        with open(self.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), len(self.df_master), "El JSON no coincide en tamaño con el CSV master")

if __name__ == "__main__":
    unittest.main()
