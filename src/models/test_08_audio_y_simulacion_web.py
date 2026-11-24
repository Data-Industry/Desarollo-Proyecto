"""Pruebas unitarias para Controles Ergonómicos de Audio y Simulación Monte Carlo Web (US-42 / SCRUM-56).

Valida:
1. Botones de detención inmediata de audio (detenerAudio) en cabecera, tarjetas de fármacos y chatbot.
2. Selector de velocidades de reproducción (1x, 1.5x, 2x).
3. Integración del panel de simulación estocástica Monte Carlo en el comparador web interactivo.
4. Consistencia en los puntos de distribución web (raíz, docs y src/ui).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class TestAudioYSimulacionWeb(unittest.TestCase):
    """Suite de verificación para controles ergonómicos de voz y simulación Monte Carlo en la UI."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.html_root = PROJECT_DIR / "mvp_comparador_jubilados.html"
        cls.html_index = PROJECT_DIR / "index.html"
        cls.html_docs = PROJECT_DIR / "docs" / "index.html"

        with open(cls.html_root, "r", encoding="utf-8") as f:
            cls.contenido_root = f.read()

        with open(cls.html_index, "r", encoding="utf-8") as f:
            cls.contenido_index = f.read()

        with open(cls.html_docs, "r", encoding="utf-8") as f:
            cls.contenido_docs = f.read()

    def test_01_botones_detener_audio_presentes(self) -> None:
        """Verifica la existencia del botón de detener audio en cabecera, tarjetas y chatbot."""
        # Cabecera general
        self.assertIn('id="btnDetenerAudioHeader"', self.contenido_root)
        self.assertIn("detenerAudio()", self.contenido_root)
        self.assertIn("Detener", self.contenido_root)

        # Chatbot
        self.assertIn('id="btnDetenerChatHeader"', self.contenido_root)
        self.assertIn("window.speechSynthesis.cancel()", self.contenido_root)

    def test_02_controles_velocidad_audio(self) -> None:
        """Verifica la presencia de los botones selectores de velocidad x1, x1.5 y x2."""
        self.assertIn("cambiarVelocidadAudio(1.0, this)", self.contenido_root)
        self.assertIn("cambiarVelocidadAudio(1.5, this)", self.contenido_root)
        self.assertIn("cambiarVelocidadAudio(2.0, this)", self.contenido_root)
        self.assertIn("btn-vel-audio", self.contenido_root)
        self.assertIn("window.velocidadAudioActual", self.contenido_root)

    def test_03_panel_montecarlo_calculadora(self) -> None:
        """Verifica los elementos interactivos del simulador estocástico en la calculadora."""
        self.assertIn('id="inputVariabilidadDosis"', self.contenido_root)
        self.assertIn('id="btnEjecutarMonteCarlo"', self.contenido_root)
        self.assertIn('id="panelResultadosMonteCarlo"', self.contenido_root)
        self.assertIn("ejecutarSimulacionMonteCarloUI", self.contenido_root)

    def test_04_logica_montecarlo_en_cliente(self) -> None:
        """Verifica que el motor JS implemente 1000 réplicas y evite cuellos de botella de cobro."""
        self.assertIn("const R = 1000;", self.contenido_root)
        self.assertIn("Banco Unión", self.contenido_root)
        self.assertIn("Box-Muller", self.contenido_root)
        self.assertIn("Cuándo comprar", self.contenido_root)

    def test_05_botones_audio_en_tarjetas_medicamentos(self) -> None:
        """Verifica que las tarjetas de medicamentos tengan botón dedicado de escuchar y detener."""
        self.assertIn("leerRecomendacionTarjeta", self.contenido_root)
        self.assertIn("detenerAudio()", self.contenido_root)

    def test_06_consistencia_entre_archivos_distribucion(self) -> None:
        """Asegura que index.html y docs/index.html tengan idénticos controles y capacidades."""
        for path_name, content in [("index.html", self.contenido_index), ("docs/index.html", self.contenido_docs)]:
            self.assertIn('id="btnDetenerAudioHeader"', content, f"Falta detener en {path_name}")
            self.assertIn('cambiarVelocidadAudio(1.5, this)', content, f"Falta vel 1.5 en {path_name}")
            self.assertIn('id="panelResultadosMonteCarlo"', content, f"Falta panel Monte Carlo en {path_name}")
            self.assertIn('id="btnDetenerChatHeader"', content, f"Falta detener chat en {path_name}")

    def test_07_audio_bienvenida_y_lenguaje_humano(self) -> None:
        """Verifica que el botón de bienvenida de voz esté presente y con lenguaje empático para el jubilado."""
        self.assertIn('id="btnAudioBienvenida"', self.contenido_root)
        self.assertIn("leerResumenVoz()", self.contenido_root)
        self.assertIn("¡Hola abuelito o familiar cuidador!", self.contenido_root)
        self.assertIn("Tu Plan de Duración y Compra Tranquila", self.contenido_root)
        self.assertIn("¿Cuánto te durará tu frasco?", self.contenido_root)
        self.assertIn("¿Cuándo se acabará tu frasco y qué día te conviene comprar?", self.contenido_root)

    def test_08_panel_trazabilidad_en_footer_y_sin_indisponible(self) -> None:
        """Verifica que la trazabilidad esté en el footer y que no muestre texto crudo 'No disponible'."""
        self.assertIn('aria-label="Trazabilidad de los datos"', self.contenido_root)
        self.assertIn('insulina_precios_stock_', self.contenido_root)
        self.assertNotIn("Fecha efectiva de los datos: No disponible", self.contenido_root)
        self.assertNotIn("Snapshot fuente: No disponible", self.contenido_root)
        self.assertNotIn("Fecha de generación del bundle: No disponible", self.contenido_root)


if __name__ == "__main__":
    unittest.main()
