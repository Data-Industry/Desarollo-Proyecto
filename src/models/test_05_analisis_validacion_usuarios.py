"""
Suite de Pruebas Unitarias Automatizadas para Validación Empírica con Usuarios (US-33 / SCRUM-48)
Fase 5 CRISP-DM: Evaluación

Verifica la integridad de datos, consistencia matemática de la fórmula SUS (Brooke 1996),
métricas de tareas guiadas, resguardo de privacidad y generación de artefactos analíticos.
"""

import os
import sys
import unittest
import importlib
import pandas as pd
import numpy as np

# Configuración universal de ruta de importación
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

TABULACION_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "validacion_usuarios_tabulacion.csv")
CUALITATIVO_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "validacion_usuarios_cualitativo.csv")
RESUMEN_CSV = os.path.join(PROJECT_ROOT, "data", "processed", "validacion_metricas_resumen.csv")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "docs", "figures")


class TestAnalisisValidacionUsuarios(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Carga los datasets de validación y ejecuta el pipeline de análisis si es necesario."""
        cls.mod_analisis = importlib.import_module("src.models.04_analisis_validacion_usuarios")
        if not os.path.exists(TABULACION_CSV) or not os.path.exists(RESUMEN_CSV):
            cls.mod_analisis.main()
        cls.df = pd.read_csv(TABULACION_CSV)
        cls.df_cuali = pd.read_csv(CUALITATIVO_CSV)
        cls.df_res = pd.read_csv(RESUMEN_CSV)

    def test_01_existencia_y_dimensiones_datasets(self):
        """Valida que los datasets requeridos existan y contengan la muestra aprobada (N=14)."""
        self.assertTrue(os.path.exists(TABULACION_CSV), "El archivo tabulacion.csv debe existir")
        self.assertTrue(os.path.exists(CUALITATIVO_CSV), "El archivo cualitativo.csv debe existir")
        self.assertEqual(len(self.df), 14, "La muestra debe tener exactamente 14 participantes")
        self.assertEqual(len(self.df[self.df["grupo"] == "Jubilado"]), 10, "Deben existir 10 participantes Jubilados")
        self.assertEqual(len(self.df[self.df["grupo"] == "Cuidador"]), 4, "Deben existir 4 participantes Cuidadores")
        self.assertGreaterEqual(len(self.df_cuali), 10, "Deben existir al menos 10 registros cualitativos")

    def test_02_resguardo_privacidad_datos_sensibles(self):
        """Verifica cumplimiento ético y ausencia total de datos de identidad o clínicos sensibles."""
        columnas = [c.lower() for c in self.df.columns]
        prohibidos = ["nombre", "apellido", "cedula", "ci", "telefono", "email", "direccion", "historia_clinica"]
        for p in prohibidos:
            self.assertNotIn(p, columnas, f"No debe existir la columna prohibida '{p}' en tabulación")

    def test_03_calculo_matematico_estricto_sus(self):
        """Valida que la fórmula de Brooke (1996) coincida exactamente en el 100% de los registros."""
        for idx, row in self.df.iterrows():
            # Impares: 1, 3, 5, 7, 9
            c_impares = (row["sus_i1"] - 1) + (row["sus_i3"] - 1) + (row["sus_i5"] - 1) + (row["sus_i7"] - 1) + (row["sus_i9"] - 1)
            # Pares: 2, 4, 6, 8, 10
            c_pares = (5 - row["sus_i2"]) + (5 - row["sus_i4"]) + (5 - row["sus_i6"]) + (5 - row["sus_i8"]) + (5 - row["sus_i10"])
            
            suma = c_impares + c_pares
            esperado = round(suma * 2.5, 2)
            
            self.assertEqual(row["sus_suma_transformada"], suma, f"Error en suma transformada para {row['codigo_participante']}")
            self.assertEqual(row["sus_score"], esperado, f"Error en puntaje SUS para {row['codigo_participante']}")
            self.assertGreaterEqual(row["sus_score"], 0.0)
            self.assertLessEqual(row["sus_score"], 100.0)

    def test_04_subescalas_usabilidad_aprendizaje(self):
        """Valida el cálculo de subescalas conforme a Lewis & Sauro (2009)."""
        for idx, row in self.df.iterrows():
            c_usab = ((row["sus_i1"] - 1) + (5 - row["sus_i2"]) + (row["sus_i3"] - 1) + 
                      (row["sus_i5"] - 1) + (5 - row["sus_i6"]) + (row["sus_i7"] - 1) + 
                      (5 - row["sus_i8"]) + (row["sus_i9"] - 1))
            c_learn = (5 - row["sus_i4"]) + (5 - row["sus_i10"])
            
            exp_usab = round((c_usab / 32.0) * 100.0, 2)
            exp_learn = round((c_learn / 8.0) * 100.0, 2)
            
            self.assertEqual(row["sus_sub_usabilidad"], exp_usab)
            self.assertEqual(row["sus_sub_aprendizaje"], exp_learn)
            self.assertTrue(0 <= row["sus_sub_usabilidad"] <= 100)
            self.assertTrue(0 <= row["sus_sub_aprendizaje"] <= 100)

    def test_05_metricas_tareas_guiadas(self):
        """Valida coherencia en resultados de tareas: tiempos positivos, ayudas en rango 0-4 y resultados válidos."""
        resultados_validos = {"Completo_Solo", "Completo_Ayuda", "No_Completo", "No_Evaluable"}
        for t in ["t1", "t2", "t3a", "t3b"]:
            for res in self.df[f"{t}_resultado"]:
                self.assertIn(res, resultados_validos)
            for t_seg in self.df[f"{t}_tiempo_segundos"]:
                self.assertGreater(t_seg, 0, "El tiempo de tarea debe ser positivo")
        for ay in self.df["t1_nivel_ayuda"]:
            self.assertTrue(0 <= ay <= 4, "Nivel de ayuda debe estar entre 0 y 4")

    def test_06_figuras_estadisticas_generadas(self):
        """Verifica la generación de las 4 figuras de alta resolución en docs/figures/."""
        figuras = [
            "validacion_fig1_distribucion_sus_benchmarking.png",
            "validacion_fig2_rendimiento_tareas_tiempos.png",
            "validacion_fig3_comprension_semaforo_anillos.png",
            "validacion_fig4_matriz_friccion_adopcion_canal.png"
        ]
        for f in figuras:
            path_f = os.path.join(FIGURES_DIR, f)
            self.assertTrue(os.path.exists(path_f), f"La figura {f} debe existir")
            self.assertGreater(os.path.getsize(path_f), 10000, f"La figura {f} debe tener un tamaño válido (>10KB)")

    def test_07_resumen_tabulado_metricas(self):
        """Verifica la presencia y consistencia de la tabla resumen de métricas."""
        self.assertTrue(os.path.exists(RESUMEN_CSV))
        metricas = self.df_res["metrica"].tolist()
        self.assertIn("Media_Total", metricas)
        self.assertIn("Media_Jubilados", metricas)
        self.assertIn("Media_Cuidadores", metricas)
        self.assertIn("Preferencia_WhatsApp_Pct", metricas)


if __name__ == "__main__":
    unittest.main()
