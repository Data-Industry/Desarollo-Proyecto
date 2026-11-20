import os
import re
import asyncio
import shutil
import markdown
from playwright.async_api import async_playwright

MD_PATH = r"c:\Users\USUARIO\Desktop\Proyecto Integrador\docs\DOCUMENTACION_MAESTRA_SISTEMA_INSULINA.md"
PDF_PATH = r"c:\Users\USUARIO\Desktop\Proyecto Integrador\docs\DOCUMENTACION_MAESTRA_SISTEMA_INSULINA.pdf"
ARTIFACT_DIR = r"C:\Users\USUARIO\.gemini\antigravity\brain\ccf30eb7-9b28-48ca-8301-f6996c594ed6"
ARTIFACT_PDF_PATH = os.path.join(ARTIFACT_DIR, "DOCUMENTACION_MAESTRA_SISTEMA_INSULINA.pdf")

def parse_markdown_to_html(md_text: str) -> str:
    # Pre-process callouts > [!NOTE], > [!TIP], etc.
    def replace_callout(match):
        kind = match.group(1).upper()
        content = match.group(2).strip()
        color_map = {
            'NOTE': ('#0284c7', '#f0f9ff', 'ℹ️ NOTA INFORMATIVA'),
            'TIP': ('#16a34a', '#f0fdf4', '💡 CONSEJO / BUENA PRÁCTICA'),
            'IMPORTANT': ('#d97706', '#fffbeb', '⚠️ IMPORTANTE'),
            'WARNING': ('#dc2626', '#fef2f2', '🚨 ADVERTENCIA'),
            'CAUTION': ('#b91c1c', '#fef2f2', '🛑 PRECAUCIÓN')
        }
        border_col, bg_col, title = color_map.get(kind, ('#0f766e', '#f0fdfa', kind))
        return f'<div class="callout" style="border-left: 4px solid {border_col}; background: {bg_col}; padding: 12px 16px; margin: 14px 0; border-radius: 4px;"><div style="font-weight: 700; font-size: 8.5pt; color: {border_col}; margin-bottom: 4px;">{title}</div><div style="font-size: 9.5pt; color: #1e293b;">{content}</div></div>'

    md_text = re.sub(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*\n((?:>.*(?:\n|$))*)', 
                     lambda m: replace_callout(re.match(r'>\s*\[!(.*?)\]\s*\n(.*)', m.group(0), re.DOTALL)), 
                     md_text)

    # Convert remaining blockquotes
    # Convert markdown with extensions
    html_content = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'toc', 'nl2br', 'sane_lists']
    )

    # Convert ```mermaid to <div class="mermaid">
    html_content = re.sub(
        r'<pre><code class="language-mermaid">([\s\S]*?)</code></pre>',
        r'<div class="mermaid">\1</div>',
        html_content
    )

    full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Documentación Maestra del Sistema - Insulinas Bolivia</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({{ 
        startOnLoad: true, 
        theme: 'neutral',
        flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }}
    }});
</script>
<style>
    @page {{
        size: A4;
        margin: 20mm 16mm 20mm 16mm;
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        font-size: 9.5pt;
        line-height: 1.55;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}
    .document-cover {{
        background: linear-gradient(135deg, #0f766e 0%, #134e4a 100%);
        color: #ffffff;
        padding: 28px 24px;
        border-radius: 8px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(15, 118, 110, 0.15);
    }}
    .document-cover h1 {{
        font-size: 19pt;
        font-weight: 800;
        margin: 0 0 8px 0;
        color: #ffffff;
        border: none;
        padding: 0;
        line-height: 1.25;
    }}
    .document-cover .subtitle {{
        font-size: 11pt;
        color: #ccfbf1;
        margin-bottom: 16px;
        font-weight: 400;
    }}
    .document-cover .meta-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        font-size: 8.5pt;
        background: rgba(255, 255, 255, 0.12);
        padding: 10px 14px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .document-cover .meta-item strong {{
        display: block;
        color: #99f6e4;
        font-size: 7.5pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    h1 {{
        font-size: 15pt;
        color: #0f766e;
        border-bottom: 2px solid #0f766e;
        padding-bottom: 4px;
        margin-top: 24px;
        margin-bottom: 12px;
        font-weight: 700;
        page-break-after: avoid;
    }}
    h2 {{
        font-size: 12pt;
        color: #1e293b;
        border-left: 4px solid #0f766e;
        padding-left: 8px;
        margin-top: 18px;
        margin-bottom: 8px;
        font-weight: 700;
        page-break-after: avoid;
    }}
    h3 {{
        font-size: 10pt;
        color: #334155;
        margin-top: 14px;
        margin-bottom: 6px;
        font-weight: 600;
        page-break-after: avoid;
    }}
    p {{
        margin: 0 0 10px 0;
        text-align: justify;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0 16px 0;
        font-size: 8.5pt;
        page-break-inside: avoid;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    th {{
        background-color: #0f766e;
        color: #ffffff;
        font-weight: 600;
        padding: 6px 8px;
        text-align: left;
        border: 1px solid #0d9488;
    }}
    td {{
        padding: 5px 8px;
        border: 1px solid #e2e8f0;
        vertical-align: top;
    }}
    tr:nth-child(even) td {{
        background-color: #f8fafc;
    }}
    pre {{
        background-color: #1e293b;
        color: #f8fafc;
        padding: 10px 12px;
        border-radius: 6px;
        font-family: 'Consolas', 'Menlo', 'Courier New', monospace;
        font-size: 8pt;
        overflow-x: auto;
        page-break-inside: avoid;
        margin: 10px 0;
        line-height: 1.4;
    }}
    code {{
        font-family: 'Consolas', 'Menlo', 'Courier New', monospace;
        font-size: 8pt;
        background-color: #f1f5f9;
        color: #0f766e;
        padding: 1px 4px;
        border-radius: 3px;
    }}
    pre code {{
        background: transparent;
        color: inherit;
        padding: 0;
    }}
    .mermaid {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 14px;
        margin: 14px auto;
        text-align: center;
        page-break-inside: avoid;
    }}
    .mermaid svg {{
        max-width: 95% !important;
        height: auto !important;
    }}
    blockquote {{
        border-left: 4px solid #0f766e;
        background: #f0fdfa;
        margin: 10px 0;
        padding: 8px 14px;
        border-radius: 0 4px 4px 0;
        font-style: normal;
        color: #134e4a;
    }}
    ul, ol {{
        margin: 6px 0 10px 0;
        padding-left: 20px;
    }}
    li {{
        margin-bottom: 4px;
    }}
    hr {{
        border: 0;
        border-top: 1px solid #cbd5e1;
        margin: 18px 0;
    }}
    .badge {{
        display: inline-block;
        padding: 2px 7px;
        font-size: 7.5pt;
        font-weight: 700;
        border-radius: 10px;
        background-color: #ccfbf1;
        color: #0f766e;
    }}
</style>
</head>
<body>
<div class="document-cover">
    <div style="text-transform: uppercase; letter-spacing: 1.5px; font-size: 7.5pt; color: #99f6e4; font-weight: 700; margin-bottom: 4px;">Proyecto Integrador de Ciencia de Datos &amp; Salud Pública</div>
    <h1>Sistema de Monitoreo, Predicción y Comparación de Precios de Insulinas en Bolivia</h1>
    <div class="subtitle">Documentación Maestra de Arquitectura, Pipeline de Datos, Modelado Machine Learning y Plataforma Web Ciudadana para Adultos Mayores</div>
    <div class="meta-grid">
        <div class="meta-item">
            <strong>Estado del Sistema</strong>
            Producción Activa (V1.0)
        </div>
        <div class="meta-item">
            <strong>Metodología</strong>
            CRISP-DM + SCRUM (Sprint 6)
        </div>
        <div class="meta-item">
            <strong>Fecha de Emisión</strong>
            20 de Noviembre, 2026
        </div>
        <div class="meta-item">
            <strong>Población Objetivo</strong>
            Jubilados / Pacientes DM
        </div>
    </div>
</div>

{html_content}

</body>
</html>
"""
    return full_html

async def main():
    print(f"Leyendo Markdown desde: {MD_PATH}")
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_text = parse_markdown_to_html(md_text)
    temp_html_path = os.path.join(ARTIFACT_DIR, "scratch", "temp_maestra.html")
    os.makedirs(os.path.dirname(temp_html_path), exist_ok=True)
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_text)

    print("Iniciando Playwright para renderizar PDF...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set viewport
        await page.set_viewport_size({"width": 1280, "height": 1024})
        await page.goto(f"file:///{temp_html_path.replace(os.sep, '/')}", wait_until="networkidle")
        # Give Mermaid time to finish rendering all SVGs
        await asyncio.sleep(2.5)

        header_template = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 7pt; color: #64748b; width: 100%; padding: 0 16mm; display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">
            <span>Sistema de Monitoreo y Predicción de Insulinas en Bolivia</span>
            <span style="font-weight: 600; color: #0f766e;">DOCUMENTACIÓN MAESTRA DEL SISTEMA (SPRINTS 1 AL 6)</span>
        </div>
        """
        footer_template = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 7pt; color: #64748b; width: 100%; padding: 0 16mm; display: flex; justify-content: space-between; border-top: 1px solid #e2e8f0; padding-top: 4px;">
            <span>Santa Cruz de la Sierra - Noviembre 2026 | Universidad / Proyecto Integrador</span>
            <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
        </div>
        """

        print(f"Generando PDF en: {PDF_PATH}")
        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template=header_template,
            footer_template=footer_template,
            margin={"top": "20mm", "bottom": "20mm", "left": "16mm", "right": "16mm"}
        )
        
        with open(PDF_PATH, "wb") as f:
            f.write(pdf_bytes)

        # Copy to artifact directory
        shutil.copy2(PDF_PATH, ARTIFACT_PDF_PATH)
        print(f"PDF copiado exitosamente a: {ARTIFACT_PDF_PATH}")
        print(f"Tamaño del PDF generado: {len(pdf_bytes) / 1024:.1f} KB")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
