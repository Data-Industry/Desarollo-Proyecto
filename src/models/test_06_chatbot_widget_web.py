"""Pruebas unitarias para el Despliegue e Integración del Chatbot Widget y Puente WhatsApp (US-39 / SCRUM-54).

Valida la integración accesible en el MVP web, presencia de controles senior-friendly,
atajos de consulta rápida, botón de compartir en WhatsApp (wa.me), lectura por voz,
cero tecnicismos de Machine Learning y seguridad estricta HTTPS a costo $0.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class TestChatbotWidgetWeb(unittest.TestCase):
    """Suite de validación de la interfaz conversacional ciudadana en la web pública."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.html_path = PROJECT_DIR / "mvp_comparador_jubilados.html"
        cls.docs_index = PROJECT_DIR / "docs" / "index.html"
        cls.root_index = PROJECT_DIR / "index.html"

        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.contenido = f.read()

    def test_01_widget_flotante_componentes_html(self) -> None:
        """Verifica la existencia de los elementos estructurales del widget conversacional."""
        self.assertIn('id="contenedorChatbotFlotante"', self.contenido)
        self.assertIn('id="btnToggleChatbot"', self.contenido)
        self.assertIn('id="modalChatbot"', self.contenido)
        self.assertIn('id="chatMessages"', self.contenido)
        self.assertIn('id="inputMensajeChat"', self.contenido)
        self.assertIn('id="formChatbot"', self.contenido)
        self.assertIn('id="btnAudioChatHeader"', self.contenido)

    def test_02_pildoras_rapidas_senior_friendly(self) -> None:
        """Verifica que existan preguntas rápidas preconfiguradas para evitar que el jubilado deba tipear."""
        self.assertIn("¿Lantus más barata?", self.contenido)
        self.assertIn("¿Stock de Novolin N?", self.contenido)
        self.assertIn("2do Anillo", self.contenido)
        self.assertIn("Gasto 30 UI/día", self.contenido)

    def test_03_puente_compartir_whatsapp(self) -> None:
        """Verifica que el widget cuente con el puente directo para compartir reportes a WhatsApp."""
        self.assertIn("api.whatsapp.com/send?text=", self.contenido)
        self.assertIn("Enviar a WhatsApp", self.contenido)

    def test_04_motor_js_triage_medico_y_calculadora(self) -> None:
        """Comprueba que la lógica client-side incluya desvío médico ético y cálculo presupuestario."""
        self.assertIn("function procesarConsultaChatbot", self.contenido)
        self.assertIn("Aviso de Salud Importante", self.contenido)
        self.assertIn("no puedo indicar dosis", self.contenido)
        self.assertIn("Presupuesto Mensual Estimado", self.contenido)

    def test_05_accesibilidad_y_atributos_aria(self) -> None:
        """Verifica los atributos de accesibilidad WCAG senior."""
        self.assertIn('role="dialog"', self.contenido)
        self.assertIn('aria-modal="true"', self.contenido)
        self.assertIn('aria-expanded="false"', self.contenido)
        self.assertIn('aria-label="Abrir asistente de consulta"', self.contenido)

    def test_06_sincronizacion_archivos_produccion(self) -> None:
        """Comprueba que el widget esté sincronizado en raíz, docs/ e index.html para GitHub Pages."""
        self.assertTrue(self.docs_index.exists())
        self.assertTrue(self.root_index.exists())

        with open(self.docs_index, "r", encoding="utf-8") as f:
            contenido_docs = f.read()
        with open(self.root_index, "r", encoding="utf-8") as f:
            contenido_root = f.read()

        self.assertIn('id="btnToggleChatbot"', contenido_docs)
        self.assertIn('id="btnToggleChatbot"', contenido_root)
        self.assertEqual(len(self.contenido), len(contenido_docs))

    def test_07_ausencia_tecnicismos_y_seguridad_https(self) -> None:
        """Asegura cero jerga de Machine Learning y cero dependencias de localhost."""
        self.assertNotIn("localhost:", self.contenido)
        self.assertNotIn("127.0.0.1:", self.contenido)
        self.assertNotIn("file:///", self.contenido)
        self.assertNotIn("Machine Learning", self.contenido)
        self.assertNotIn("Random Forest", self.contenido)
        self.assertNotIn("Lag de importaciones", self.contenido)


if __name__ == "__main__":
    unittest.main()
