"""Suite de pruebas unitarias para el motor de simulación estocástica Monte Carlo.

Verifica la formulación matemática y el comportamiento del modelo de inventarios
de García Dunna, García Reyes & Cárdenas Barrón (2013).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.optimization.simulador_montecarlo_paciente import (
    SimuladorInventarioPaciente,
    ResultadoSimulacion,
    simular_cobertura_insulina,
)


class TestSimuladorMonteCarloPaciente(unittest.TestCase):
    """Pruebas unitarias para la simulación estocástica de inventarios de insulina."""

    def setUp(self) -> None:
        """Configura un escenario clínico típico: 25 UI/día con vial de 1.000 UI."""
        self.simulador = SimuladorInventarioPaciente(
            dosis_media_ui=25.0,
            variabilidad_sigma_ui=3.0,
            presentacion_total_ui=1000.0,
            dias_margen_seguridad=5,
            random_seed=42,
        )

    def test_01_validacion_parametros_invalidos(self) -> None:
        """Verifica que se rechacen dosis nulas, negativas o capacidades inválidas."""
        with self.assertRaises(ValueError):
            SimuladorInventarioPaciente(dosis_media_ui=0.0)

        with self.assertRaises(ValueError):
            SimuladorInventarioPaciente(dosis_media_ui=-10.0)

        with self.assertRaises(ValueError):
            SimuladorInventarioPaciente(dosis_media_ui=20.0, presentacion_total_ui=0.0)

        with self.assertRaises(ValueError):
            SimuladorInventarioPaciente(dosis_media_ui=20.0, variabilidad_sigma_ui=-1.0)

    def test_02_caso_determinista_sin_variabilidad(self) -> None:
        """Con sigma=0, la duración debe coincidir exactamente con Capacidad / Dosis."""
        sim_det = SimuladorInventarioPaciente(
            dosis_media_ui=25.0,
            variabilidad_sigma_ui=0.0,
            presentacion_total_ui=1000.0,
            random_seed=42,
        )
        res = sim_det.ejecutar_montecarlo(num_replicas=100)
        # 1000 / 25 = 40 días exactos
        self.assertEqual(res.dias_duracion_media, 40.0)
        self.assertEqual(res.desviacion_estandar_dias, 0.0)
        self.assertEqual(res.percentil_5_dias, 40.0)
        self.assertEqual(res.percentil_95_dias, 40.0)

    def test_03_ejecucion_montecarlo_1000_replicas(self) -> None:
        """Verifica que la simulación con 1.000 réplicas converja alrededor de la media teórica."""
        res = self.simulador.ejecutar_montecarlo(num_replicas=1000)
        self.assertEqual(res.num_replicas, 1000)
        # La media debe estar muy cercana a 40 días (entre 38 y 42 días)
        self.assertGreater(res.dias_duracion_media, 38.0)
        self.assertLess(res.dias_duracion_media, 42.0)
        self.assertGreater(res.desviacion_estandar_dias, 0.0)

    def test_04_coherencia_intervalo_confianza_95(self) -> None:
        """Verifica que el intervalo de confianza al 95% sea consistente (IC_inf <= Media <= IC_sup)."""
        res = self.simulador.ejecutar_montecarlo(num_replicas=1000)
        self.assertLessEqual(res.ic_95_inferior_dias, res.dias_duracion_media)
        self.assertGreaterEqual(res.ic_95_superior_dias, res.dias_duracion_media)
        # Con N=1000, el semiancho del IC de la media debe ser inferior a 0.5 días
        semi_ancho = res.ic_95_superior_dias - res.dias_duracion_media
        self.assertLess(semi_ancho, 0.5)

    def test_05_monotonia_de_percentiles(self) -> None:
        """Verifica que los percentiles empíricos cumplan P5 <= P50 <= P95."""
        res = self.simulador.ejecutar_montecarlo(num_replicas=1000)
        self.assertLessEqual(res.percentil_5_dias, res.percentil_50_dias)
        self.assertLessEqual(res.percentil_50_dias, res.percentil_95_dias)

    def test_06_punto_de_reorden_seguro(self) -> None:
        """Verifica el cálculo del punto de reorden (dosis * días de seguridad)."""
        res = self.simulador.ejecutar_montecarlo(num_replicas=500)
        # 25 UI/día * 5 días = 125 UI
        self.assertEqual(res.punto_reorden_seguro_ui, 125.0)
        self.assertGreater(res.dia_inicio_reorden, 0)
        self.assertLess(res.dia_inicio_reorden, res.dias_duracion_media)

    def test_07_optimizacion_dia_compra(self) -> None:
        """Verifica la asignación del día óptimo evitando los días críticos de cobro de renta."""
        res = self.simulador.ejecutar_montecarlo(num_replicas=500)
        self.assertIn(res.dia_optimo_compra_mes, [12, 22])
        # La probabilidad de quiebre en el día óptimo debe ser significativamente menor que a fin de mes
        self.assertLess(res.probabilidad_quiebre_dia_optimo_pct, res.probabilidad_quiebre_fin_mes_pct)

    def test_08_interfaz_alto_nivel_json(self) -> None:
        """Verifica que simular_cobertura_insulina devuelva el diccionario esperado para la UI."""
        datos = simular_cobertura_insulina(
            dosis_diaria_ui=30.0,
            variabilidad_ui=4.0,
            presentacion_ui=300.0,  # Cartucho de 3 ml
        )
        self.assertIn("dias_duracion_media", datos)
        self.assertIn("ic_95_inferior_dias", datos)
        self.assertIn("ic_95_superior_dias", datos)
        self.assertIn("dia_optimo_compra_mes", datos)
        self.assertIn("mensaje_clinico", datos)
        self.assertIn("histograma_dias", datos)
        # Cartucho de 300 UI con 30 UI/día dura aproximadamente 10 días
        self.assertGreater(datos["dias_duracion_media"], 8.0)
        self.assertLess(datos["dias_duracion_media"], 12.0)


if __name__ == "__main__":
    unittest.main()
