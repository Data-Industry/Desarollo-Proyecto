"""Pruebas unitarias para el MVP Visualizador Didáctico de Insulina para Jubilados (US-29 / SCRUM-44).

Verifica la compilación de datos reales agrupados por medicamento, la comparación directa
de las 3 cadenas de farmacias (Farmacorp, Farmacias Chávez, Farmacias Telchi), la generación
de archivos HTML autocontenidos y los estándares de accesibilidad para adultos mayores.
"""

import importlib
from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[2]
CURRENT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    gen_mvp = importlib.import_module("src.ui.generar_mvp_interactivo")
except ImportError:
    gen_mvp = importlib.import_module("generar_mvp_interactivo")


class TestMVPJubilados(unittest.TestCase):
    """Suite de pruebas unitarias para US-29 versión 2.0 (Agrupada y Accesible)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configura rutas y compila datos reales del MVP."""
        cls.project_dir = Path(__file__).resolve().parents[2]
        cls.src_ui_html = cls.project_dir / "src" / "ui" / "mvp_comparador_jubilados.html"
        cls.root_html = cls.project_dir / "mvp_comparador_jubilados.html"
        cls.artifact_html = gen_mvp.ARTIFACT_HTML

        cls.medicamentos, cls.sucursales, cls.resumen = gen_mvp.compilar_datos_reales()

    def test_01_compilacion_datos_reales_agrupados(self) -> None:
        """Verifica que se compilen 24 formulaciones únicas a partir de 43 registros y 16 sucursales."""
        self.assertEqual(len(self.medicamentos), 24, "Deben existir exactamente 24 formulaciones únicas agrupadas")
        self.assertEqual(len(self.sucursales), 16, "Deben existir 16 sucursales geolocalizadas")
        self.assertEqual(self.resumen["total_medicamentos"], 24)
        self.assertEqual(self.resumen["total_registros_crudos"], 43)
        self.assertEqual(self.resumen["total_sucursales"], 16)
        self.assertGreater(self.resumen["precio_min_bs"], 0)
        self.assertGreater(self.resumen["precio_max_bs"], self.resumen["precio_min_bs"])

    def test_02_estructura_comparativa_3_cadenas_y_ml(self) -> None:
        """Comprueba que cada medicamento contenga desglose de precios de cadenas y métricas predictivas."""
        cadenas_validas = {"Farmacorp", "Farmacias Chávez", "Farmacias Telchi"}
        for med in self.medicamentos:
            self.assertIn("id", med)
            self.assertIn("marca", med)
            self.assertIn("principio_activo", med)
            self.assertIn("tipo_accion", med)
            self.assertIn("formato", med)
            self.assertIn("precios", med)
            self.assertGreater(len(med["precios"]), 0, "Cada medicamento debe tener al menos una cadena con precio")
            self.assertIn(med["mejor_cadena"], cadenas_validas)
            self.assertGreater(med["mejor_precio_bs"], 0)
            self.assertIn(med["semaforo_general"], {"VERDE", "AMARILLO", "ROJO"})

            # Validar estructura interna de cada cadena dentro del medicamento
            for cadena_nombre, datos in med["precios"].items():
                self.assertIn(cadena_nombre, cadenas_validas)
                self.assertIn("precio_venta_bs", datos)
                self.assertIn("precio_por_100ui_bs", datos)
                self.assertIn("estado_stock", datos)
                self.assertIn("semaforo_ml", datos)
                self.assertIn("prob_quiebre_ml", datos)
                self.assertGreater(datos["precio_venta_bs"], 0)
                self.assertGreaterEqual(datos["prob_quiebre_ml"], 0.0)
                self.assertLessEqual(datos["prob_quiebre_ml"], 1.0)

    def test_03_sucursales_geolocalizadas_y_anillos(self) -> None:
        """Comprueba que las sucursales tengan dirección, ciudad y anillo identificado."""
        anillos_encontrados = {s["anillo_num"] for s in self.sucursales}
        self.assertTrue({2.0, 3.0, 4.0, 7.0}.issubset(anillos_encontrados))
        for suc in self.sucursales:
            self.assertTrue(len(suc["nombre"]) > 0)
            self.assertTrue(len(suc["direccion"]) > 0)
            self.assertIn("anillo_etiqueta", suc)
            self.assertEqual(suc["ciudad"], "Santa Cruz de la Sierra")

    def test_04_archivos_html_generados(self) -> None:
        """Verifica que los archivos HTML existan y tengan un tamaño válido (>20KB)."""
        self.assertTrue(self.src_ui_html.exists(), "Falta src/ui/mvp_comparador_jubilados.html")
        self.assertTrue(self.root_html.exists(), "Falta mvp_comparador_jubilados.html en la raíz")
        self.assertTrue(self.artifact_html.exists(), "Falta el artefacto oficial en brain/")

        self.assertGreater(self.src_ui_html.stat().st_size, 20000)
        self.assertGreater(self.root_html.stat().st_size, 20000)
        self.assertGreater(self.artifact_html.stat().st_size, 20000)

    def test_05_criterios_aceptacion_y_nuevos_botones(self) -> None:
        """Verifica los criterios de aceptación y los nuevos controles solicitados por el usuario."""
        with open(self.src_ui_html, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Paso 1: Filtros de catálogo y botones explícitos
        self.assertIn('id="filtroPrincipio"', contenido)
        self.assertIn('id="filtroFormato"', contenido)
        self.assertIn('id="filtroFarmacia"', contenido)
        self.assertIn('id="inputBusqueda"', contenido)
        self.assertIn('id="btnAplicarFiltros"', contenido, "Debe existir el botón explícito de Filtrar Catálogo")
        self.assertIn('id="btnLimpiarFiltros"', contenido, "Debe existir el botón de restablecer filtros")
        self.assertIn(f"Bs {self.resumen['precio_min_bs']:.2f}", contenido, "El precio mínimo del banner debe ser dinámico")

        # Comparador con desglose de 3 cadenas por tarjeta
        self.assertIn("⭐ Mejor Precio", contenido)
        self.assertIn("Comparativa por Farmacia:", contenido)
        self.assertIn("Ahorras Bs", contenido)
        self.assertIn("Farmacias Chávez", contenido)
        self.assertIn("Farmacorp", contenido)
        self.assertIn("Farmacias Telchi", contenido)

        # Paso 2: Buscador Territorial por Anillos
        self.assertIn('id="selectAnilloFiltro"', contenido)
        self.assertIn('id="tbodySucursales"', contenido)
        self.assertIn("2do Anillo", contenido)
        self.assertIn("3er Anillo", contenido)

        # Semáforo Preventivo Upstream & ML
        self.assertIn('id="badgeSemaforoGlobal"', contenido)
        self.assertIn("VERDE (Stock Estable)", contenido)
        self.assertIn("AMARILLO (Pocas Unidades)", contenido)
        self.assertIn("ROJO (Alerta de Quiebre)", contenido)

        # Paso 3: Calculadora de Presupuesto Mensual
        self.assertIn('id="inputDosisDiaria"', contenido)
        self.assertIn('id="selectTipoInsulinaCalc"', contenido)
        self.assertIn('id="calcResumenAhorro"', contenido)

    def test_06_accesibilidad_senior_y_zoom_escalable(self) -> None:
        """Comprueba controles de accesibilidad senior y escalado de fuente del documento completo."""
        with open(self.src_ui_html, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Controles de tamaño de letra que escalan el elemento raíz (document.documentElement)
        self.assertIn('id="btnFontMinus"', contenido)
        self.assertIn('id="btnFontPlus"', contenido)
        self.assertIn('id="lblFontScale"', contenido)
        self.assertIn("document.documentElement.style.fontSize", contenido)

        # Asistente de lectura por voz nativo
        self.assertIn("leerResumenVoz", contenido)
        self.assertIn("speechSynthesis", contenido)

        # Semáforos de contraste accesible
        self.assertIn("badge-verde", contenido)
        self.assertIn("badge-amarillo", contenido)
        self.assertIn("badge-rojo", contenido)


if __name__ == "__main__":
    unittest.main()
