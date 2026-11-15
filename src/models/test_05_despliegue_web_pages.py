"""Pruebas unitarias para Despliegue Continuo (CI/CD) y Hosting Web Gratuito (US-35 / SCRUM-50).

Verifica la existencia, sincronización e integridad de los archivos de entrada para GitHub Pages
(index.html en raíz y docs/), la configuración del workflow de GitHub Actions, la ausencia de rutas
locales inseguras y el cumplimiento estricto de HTTPS y metadatos SEO/OpenGraph.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_DIR = Path(__file__).resolve().parents[2]
CURRENT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))


class TestDespliegueWebPages(unittest.TestCase):
    """Suite de validación de entrega continua y hosting gratuito a costo $0 para US-35."""

    @classmethod
    def setUpClass(cls) -> None:
        """Inicializa rutas del proyecto."""
        cls.project_dir = Path(__file__).resolve().parents[2]
        cls.root_index = cls.project_dir / "index.html"
        cls.docs_index = cls.project_dir / "docs" / "index.html"
        cls.root_mvp = cls.project_dir / "mvp_comparador_jubilados.html"
        cls.workflow_file = cls.project_dir / ".github" / "workflows" / "deploy_pages.yml"

    def test_01_archivos_index_html_generados_y_sincronizados(self) -> None:
        """Comprueba que index.html exista en raíz y docs/ y supere los 25 KB de contenido interactivo."""
        self.assertTrue(self.root_index.exists(), "Falta index.html en la raíz del proyecto para GitHub Pages")
        self.assertTrue(self.docs_index.exists(), "Falta docs/index.html para publicación desde rama /docs")

        size_root = self.root_index.stat().st_size
        size_docs = self.docs_index.stat().st_size
        self.assertGreater(size_root, 25000, f"index.html raíz es muy pequeño ({size_root} bytes)")
        self.assertGreater(size_docs, 25000, f"docs/index.html es muy pequeño ({size_docs} bytes)")

        with open(self.root_index, "r", encoding="utf-8") as f:
            contenido_root = f.read()
        with open(self.docs_index, "r", encoding="utf-8") as f:
            contenido_docs = f.read()

        self.assertEqual(
            contenido_root,
            contenido_docs,
            "El archivo index.html en raíz y en docs/ deben ser exactamente idénticos y sincronizados.",
        )

    def test_02_workflow_github_actions_ci_cd(self) -> None:
        """Verifica la sintaxis, permisos y acciones oficiales del pipeline CI/CD de GitHub Pages."""
        self.assertTrue(self.workflow_file.exists(), "Falta .github/workflows/deploy_pages.yml")

        with open(self.workflow_file, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Permisos obligatorios para GitHub Pages
        self.assertIn("pages: write", yaml_content)
        self.assertIn("id-token: write", yaml_content)
        self.assertIn("contents: read", yaml_content)

        # Triggers
        self.assertIn("branches: [ main ]", yaml_content)
        self.assertIn("workflow_dispatch:", yaml_content)

        # Acciones oficiales de GitHub Pages
        self.assertIn("actions/checkout@v4", yaml_content)
        self.assertIn("actions/setup-python@v5", yaml_content)
        self.assertIn("actions/configure-pages@v5", yaml_content)
        self.assertIn("actions/upload-pages-artifact@v3", yaml_content)
        self.assertIn("actions/deploy-pages@v4", yaml_content)

        # Pasos de validación antes del despliegue
        self.assertIn("test_*.py", yaml_content)
        self.assertIn("generar_mvp_interactivo.py", yaml_content)

    def test_03_enlaces_seguros_https_y_cero_localhost(self) -> None:
        """Verifica que el HTML no dependa de servidores locales ni protocolos inseguros."""
        with open(self.docs_index, "r", encoding="utf-8") as f:
            contenido = f.read()

        # No debe haber referencias a localhost, loopback o rutas absolutas de desarrollo
        self.assertNotIn("localhost:", contenido)
        self.assertNotIn("127.0.0.1:", contenido)
        self.assertNotIn("file:///", contenido)
        self.assertNotIn("C:\\Users\\", contenido)

        # Recursos externos deben cargarse estrictamente por HTTPS
        self.assertIn("https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js", contenido)
        self.assertIn("https://fonts.googleapis.com", contenido)

    def test_04_compatibilidad_responsive_y_metadatos_seo_opengraph(self) -> None:
        """Verifica etiquetas responsive, metadatos SEO y componentes interactivos para usuarios senior."""
        with open(self.docs_index, "r", encoding="utf-8") as f:
            contenido = f.read()

        # Metadatos web obligatorios
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1.0">', contenido)
        self.assertIn('property="og:title"', contenido)
        self.assertIn('property="og:description"', contenido)
        self.assertIn('property="og:url"', contenido)
        self.assertIn('rel="canonical"', contenido)
        self.assertIn("https://data-industry.github.io/Desarollo-Proyecto/", contenido)

        # Componentes funcionales del MVP
        self.assertIn('id="btnFontMinus"', contenido)
        self.assertIn('id="btnFontPlus"', contenido)
        self.assertIn('id="sec-glosario"', contenido)
        self.assertIn('id="sec-calculadora"', contenido)
        self.assertIn('id="sec-filtros"', contenido)
        self.assertIn('id="sec-catalogo"', contenido)
        self.assertIn('id="sec-anillos"', contenido)


if __name__ == "__main__":
    unittest.main()
