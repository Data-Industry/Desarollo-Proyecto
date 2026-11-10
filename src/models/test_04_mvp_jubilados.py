"""Pruebas unitarias para el MVP Visualizador Didáctico de Insulina para Jubilados (US-31 / SCRUM-46).

Verifica la compilación de datos reales agrupados por medicamento, la comparación directa
de las 3 cadenas de farmacias (Farmacorp, Farmacias Chávez, Farmacias Telchi), la generación
de archivos HTML autocontenidos (incluyendo docs/mvp_jubilados_comparador.html), el glosario
ciudadano amigable, la ausencia de tecnicismos y la regla estricta de semáforos coherentes.
"""

from __future__ import annotations

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
    """Suite de pruebas unitarias para US-31 versión 3.0 (Lenguaje Ciudadano y Semáforo Coherente)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Configura rutas y compila datos reales del MVP."""
        cls.project_dir = Path(__file__).resolve().parents[2]
        cls.src_ui_html = cls.project_dir / "src" / "ui" / "mvp_comparador_jubilados.html"
        cls.root_html = cls.project_dir / "mvp_comparador_jubilados.html"
        cls.docs_html = cls.project_dir / "docs" / "mvp_jubilados_comparador.html"
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

    def test_02_estructura_comparativa_3_cadenas_y_metricas(self) -> None:
        """Comprueba que cada medicamento contenga desglose de precios de cadenas y métricas comparativas."""
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
                self.assertIn("disponible", datos)
                self.assertGreater(datos["precio_venta_bs"], 0)

    def test_03_regla_estricta_semaforo_coherente_us31(self) -> None:
        """Verifica que NINGUNA insulina disponible marque ROJO y que el semáforo sea 100% coherente."""
        total_verde = 0
        total_amarillo = 0
        total_rojo = 0

        for med in self.medicamentos:
            sem = med["semaforo_general"]
            activas = med["total_farmacias_activas"]

            # Regla 1: Si hay farmacias activas, BAJO NINGUNA CIRCUNSTANCIA puede ser ROJO
            if activas > 0:
                self.assertNotEqual(
                    sem,
                    "ROJO",
                    f"Incoherencia semafórica: {med['marca']} tiene {activas} farmacia(s) disponible(s) pero marca ROJO.",
                )
                self.assertIn(sem, {"VERDE", "AMARILLO"})

            # Regla 2: El ROJO se reserva estrictamente cuando activas == 0
            if sem == "ROJO":
                self.assertEqual(
                    activas,
                    0,
                    f"El semáforo ROJO solo se permite cuando no hay stock activo, pero {med['marca']} tiene {activas}.",
                )
                total_rojo += 1
            elif sem == "VERDE":
                total_verde += 1
                self.assertGreaterEqual(activas, 2, "El verde requiere al menos 2 farmacias con stock estable.")
            elif sem == "AMARILLO":
                total_amarillo += 1
                self.assertGreater(activas, 0, "El amarillo requiere al menos 1 farmacia con existencias.")

        self.assertEqual(self.resumen["total_verde"], total_verde)
        self.assertEqual(self.resumen["total_amarillo"], total_amarillo)
        self.assertEqual(self.resumen["total_rojo"], total_rojo)
        self.assertGreater(total_verde, 0, "Debe haber medicamentos con stock verde asegurado.")
        self.assertGreater(total_amarillo, 0, "Debe haber medicamentos con semáforo amarillo de precaución.")
        self.assertEqual(total_rojo, 1, "Debe haber exactamente 1 presentación totalmente agotada (Insugen NPH).")

    def test_04_sucursales_geolocalizadas_y_anillos(self) -> None:
        """Comprueba que las sucursales tengan dirección, ciudad y anillo identificado."""
        anillos_encontrados = {s["anillo_num"] for s in self.sucursales}
        self.assertTrue({2.0, 3.0, 4.0, 7.0}.issubset(anillos_encontrados))
        for suc in self.sucursales:
            self.assertTrue(len(suc["nombre"]) > 0)
            self.assertTrue(len(suc["direccion"]) > 0)
            self.assertIn("anillo_etiqueta", suc)
            self.assertEqual(suc["ciudad"], "Santa Cruz de la Sierra")

    def test_05_archivos_html_generados_y_sincronizados(self) -> None:
        """Verifica que los 4 archivos HTML existan y tengan un tamaño válido (>20KB)."""
        self.assertTrue(self.src_ui_html.exists(), "Falta src/ui/mvp_comparador_jubilados.html")
        self.assertTrue(self.root_html.exists(), "Falta mvp_comparador_jubilados.html en la raíz")
        self.assertTrue(self.docs_html.exists(), "Falta docs/mvp_jubilados_comparador.html (Criterio US-31)")
        self.assertTrue(self.artifact_html.exists(), "Falta el artefacto oficial en brain/")

        self.assertGreater(self.src_ui_html.stat().st_size, 20000)
        self.assertGreater(self.root_html.stat().st_size, 20000)
        self.assertGreater(self.docs_html.stat().st_size, 20000)
        self.assertGreater(self.artifact_html.stat().st_size, 20000)

    def test_06_glosario_ciudadano_y_ausencia_tecnicismos(self) -> None:
        """Verifica que el glosario accesible esté presente y que no existan tecnicismos en la vista."""
        with open(self.src_ui_html, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Glosario ciudadano interactivo obligatorio (Criterio de Aceptación US-31)
        self.assertIn('id="sec-glosario"', contenido)
        self.assertIn('¿Qué es "Quiebre de stock"?', contenido)
        self.assertIn('¿Cómo funciona el Semáforo?', contenido)
        self.assertIn('¿Cómo se calcula tu Ahorro?', contenido)
        self.assertIn('¿Qué significa "U-100"?', contenido)

        # Ausencia de tecnicismos complejos en el texto visible al jubilado
        self.assertNotIn("Machine Learning", contenido, "No debe incluirse el término 'Machine Learning'")
        self.assertNotIn("Random Forest", contenido, "No debe incluirse el término 'Random Forest'")
        self.assertNotIn("Lag de importaciones", contenido, "No debe incluirse 'Lag de importaciones'")

        # Semáforo de lenguaje amigable
        self.assertIn("VERDE (Disponibilidad Segura)", contenido)
        self.assertIn("AMARILLO (Precaución)", contenido)
        self.assertIn("ROJO (Agotado General)", contenido)

    def test_07_criterios_interactivos_y_accesibilidad_senior(self) -> None:
        """Verifica controles de búsqueda, ordenamiento, calculadora y accesibilidad senior."""
        with open(self.src_ui_html, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Paso 1: Filtros de catálogo y botones explícitos
        self.assertIn('id="filtroPrincipio"', contenido)
        self.assertIn('id="filtroFormato"', contenido)
        self.assertIn('id="filtroFarmacia"', contenido)
        self.assertIn('id="inputBusqueda"', contenido)
        self.assertIn('id="btnAplicarFiltros"', contenido)
        self.assertIn('id="btnLimpiarFiltros"', contenido)

        # Comparador con desglose de 3 cadenas por tarjeta
        self.assertIn("⭐ Mejor Precio", contenido)
        self.assertIn("Comparativa por Farmacia:", contenido)
        self.assertIn("Ahorro Máximo en tu Compra:", contenido)

        # Paso 2: Buscador Territorial por Anillos
        self.assertIn('id="selectAnilloFiltro"', contenido)
        self.assertIn('id="tbodySucursales"', contenido)

        # Paso 3: Calculadora de Presupuesto Mensual
        self.assertIn('id="inputDosisDiaria"', contenido)
        self.assertIn('id="selectTipoInsulinaCalc"', contenido)
        self.assertIn('id="calcResumenAhorro"', contenido)

        # Accesibilidad Senior: Escalado real de letra y voz
        self.assertIn('id="btnFontMinus"', contenido)
        self.assertIn('id="btnFontPlus"', contenido)
        self.assertIn('id="lblFontScale"', contenido)
        self.assertIn("document.documentElement.style.fontSize", contenido)
        self.assertIn("leerResumenVoz", contenido)
        self.assertIn("speechSynthesis", contenido)


if __name__ == "__main__":
    unittest.main()
