"""Pruebas Unitarias para el Asistente Conversacional en Lenguaje Natural (US-38 / SCRUM-53).

Verifica la extracción de entidades, clasificación de intenciones, cálculo de comparativas
y presupuestos, ausencia de tecnicismos de Machine Learning y cumplimiento ético de desvío
médico para adultos mayores y familiares cuidadores.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from src.chatbot.asistente_insulina import AsistenteInsulina, normalizar_texto


class TestAsistenteConversacional(unittest.TestCase):
    """Suite de validación de la experiencia conversacional del usuario senior."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.asistente = AsistenteInsulina()

    def test_01_normalizar_texto(self) -> None:
        """Verifica la eliminación de acentos y normalización a minúsculas."""
        self.assertEqual(normalizar_texto("¡LÁNTUS 100 UI!"), "¡lantus 100 ui!")
        self.assertEqual(normalizar_texto("Farmacias Chávez"), "farmacias chavez")
        self.assertEqual(normalizar_texto("Acción Rápida"), "accion rapida")

    def test_02_extraccion_marcas_y_principios(self) -> None:
        """Comprueba el reconocimiento de marcas y principios activos comerciales."""
        e1 = self.asistente.extraer_entidades("¿Cuánto cuesta la insulina Lantus en frasco?")
        self.assertEqual(e1["marca"], "Lantus")
        self.assertEqual(e1["formato"], "Vial / Frasco Ampolla")

        e2 = self.asistente.extraer_entidades("Tienen Novolin N o alguna NPH intermedia")
        self.assertEqual(e2["marca"], "Novolin N")
        self.assertEqual(e2["principio_activo"], "Insulina Humana NPH (N)")

        e3 = self.asistente.extraer_entidades("Busco Basalog en lapicero prellenado")
        self.assertEqual(e3["marca"], "Basalog")
        self.assertEqual(e3["formato"], "Lapicero Prellenado (Pluma)")

    def test_03_extraccion_anillos_urbanos_santa_cruz(self) -> None:
        """Verifica la detección de anillos (1 al 8) y alias céntricos en Santa Cruz."""
        e1 = self.asistente.extraer_entidades("Sucursales de Farmacorp en el 2do anillo")
        self.assertEqual(e1["anillo"], 2)
        self.assertEqual(e1["cadena_farmacia"], "Farmacorp")

        e2 = self.asistente.extraer_entidades("Farmacias por el 4to anillo")
        self.assertEqual(e2["anillo"], 4)

        e3 = self.asistente.extraer_entidades("Dónde hay farmacia en el centro o casco viejo")
        self.assertEqual(e3["anillo"], 1)

    def test_04_deteccion_intenciones(self) -> None:
        """Verifica la clasificación adecuada de intenciones ciudadanas."""
        # Precios
        res_precio = self.asistente.responder("¿Dónde está más barata la insulina Lantus?")
        self.assertEqual(res_precio["intencion"], "CONSULTAR_PRECIO_COMPARATIVO")

        # Stock
        res_stock = self.asistente.responder("¿Hay stock disponible de Novolin R hoy?")
        self.assertEqual(res_stock["intencion"], "CONSULTAR_DISPONIBILIDAD_STOCK")

        # Sucursales
        res_suc = self.asistente.responder("Sucursales de farmacias en el 3er anillo")
        self.assertEqual(res_suc["intencion"], "CONSULTAR_SUCURSALES_ANILLO")

        # Presupuesto
        res_calc = self.asistente.responder("Uso 30 UI al día de Lantus, cuánto gasto al mes")
        self.assertEqual(res_calc["intencion"], "CALCULAR_PRESUPUESTO_DOSIS")

        # Saludo
        res_saludo = self.asistente.responder("Hola buenas tardes, qué puedes hacer")
        self.assertEqual(res_saludo["intencion"], "SALUDO_Y_AYUDA")

        # Desvío médico
        res_med = self.asistente.responder("¿Cuánta dosis me debo poner si tengo 200 de glucosa?")
        self.assertEqual(res_med["intencion"], "CONSULTA_MEDICA_DESVIO")

    def test_05_comparativa_precios_y_ahorro_monetario(self) -> None:
        """Comprueba que la respuesta de precios calcule el ahorro en Bs y la mejor farmacia."""
        resp = self.asistente.responder("Precio de Lantus en Santa Cruz")
        self.assertEqual(resp["intencion"], "CONSULTAR_PRECIO_COMPARATIVO")
        self.assertIn("Lantus", resp["respuesta_texto"])
        self.assertIn("Farmacorp", resp["respuesta_texto"])
        self.assertIn("Bs", resp["respuesta_texto"])
        self.assertIn(resp["semaforo"], ["VERDE", "AMARILLO", "ROJO"])

        mejor = resp.get("mejor_opcion", {})
        self.assertTrue(mejor.get("farmacia"))
        self.assertGreater(mejor.get("precio_bs", 0), 0)
        self.assertGreaterEqual(mejor.get("ahorro_bs", 0), 0)

    def test_06_calculadora_presupuesto_dosis(self) -> None:
        """Verifica el cálculo de frascos y presupuesto mensual para 30 días."""
        resp = self.asistente.responder("Presupuesto para Lantus con 30 UI al día")
        self.assertEqual(resp["intencion"], "CALCULAR_PRESUPUESTO_DOSIS")
        self.assertIn("30 UI al día", resp["respuesta_texto"])
        self.assertIn("900 UI", resp["respuesta_texto"])  # 30 * 30 = 900
        self.assertIn("unidad(es)", resp["respuesta_texto"])

        calc = resp.get("mejor_opcion", {})
        self.assertGreaterEqual(calc.get("frascos_mes", 0), 1)
        self.assertGreater(calc.get("gasto_mensual_min_bs", 0), 0)

    def test_07_ausencia_tecnicismos_ml_y_empatia_senior(self) -> None:
        """Verifica que las respuestas no contengan jerga de Machine Learning y mantengan calidez."""
        consultas = [
            "Hola",
            "Precio de Lantus",
            "Hay stock de Novolin N",
            "Farmacias en el 2do anillo",
            "Gasto para 40 UI al día",
        ]
        for c in consultas:
            resp = self.asistente.responder(c)
            texto = resp["respuesta_texto"]

            # Ausencia de jerga técnica compleja
            self.assertNotIn("Machine Learning", texto)
            self.assertNotIn("Random Forest", texto)
            self.assertNotIn("XGBoost", texto)
            self.assertNotIn("F1-Score", texto)
            self.assertNotIn("AUC-ROC", texto)
            self.assertNotIn("Lag", texto)
            self.assertNotIn("Overfitting", texto)

            # Presencia de tono respetuoso y claro
            self.assertTrue(len(texto) > 40)

    def test_08_desvio_etico_consultas_medicas(self) -> None:
        """Verifica que cualquier consulta de dosificación médica derive éticamente al médico."""
        consultas_medicas = [
            "¿Puedo cambiar mi Novolin por Lantus?",
            "¿Qué dosis me pongo hoy?",
            "Recétame una insulina para la diabetes",
        ]
        for q in consultas_medicas:
            resp = self.asistente.responder(q)
            self.assertEqual(resp["intencion"], "CONSULTA_MEDICA_DESVIO")
            self.assertEqual(resp["semaforo"], "ALERTA_SALUD")
            self.assertIn("médico", resp["respuesta_texto"].lower())
            self.assertIn("no puedo", resp["respuesta_texto"].lower())


if __name__ == "__main__":
    unittest.main()
