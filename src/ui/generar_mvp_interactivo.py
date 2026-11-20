"""Generador del MVP Visualizador Didáctico e Interactivo Local para Jubilados (US-31 / US-34 / SCRUM-49).

Versión 3.1 (Refinamiento Ergonómico y Estética Farmacéutica Pastel):
- Controles accesibles explícitos con texto legible: "Achicar letra" y "Agrandar letra" (reemplazo de A- y A+).
- Glosario ciudadano interactivo compacto y no invasivo: botón desplegable con definiciones claras al pasar el mouse o hacer clic.
- Reubicación de la Calculadora de Dosis y Presupuesto Mensual a la parte superior antes del catálogo.
- Filtrado por catálogo y búsqueda con acción explícita mediante botón 'Filtrar Catálogo' o tecla Enter.
- Estética pastel farmacéutica limpia, humana y natural (Anti-IA): verdes salvia, menta suave y blanco clínico.
- Semáforo general de disponibilidad observada, separado del riesgo predictivo por farmacia.
- Comparador económico transparente entre Farmacorp, Farmacias Chávez y Farmacias Telchi.
- Exportación automática sincronizada a la raíz, src/ui/, docs/ y directorio de artefactos.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generador_mvp")

# Rutas del Proyecto
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
SRC_UI_DIR = PROJECT_DIR / "src" / "ui"
DOCS_DIR = PROJECT_DIR / "docs"

ROOT_HTML = PROJECT_DIR / "mvp_comparador_jubilados.html"
ROOT_INDEX_HTML = PROJECT_DIR / "index.html"
UI_HTML = SRC_UI_DIR / "mvp_comparador_jubilados.html"
DOCS_HTML = DOCS_DIR / "mvp_jubilados_comparador.html"
DOCS_INDEX_HTML = DOCS_DIR / "index.html"
ARTIFACT_HTML = Path(
    r"C:\Users\USUARIO\.gemini\antigravity\brain\ccf30eb7-9b28-48ca-8301-f6996c594ed6\mvp_jubilados_comparador.html"
)


def compilar_datos_reales(
    *,
    df_master: Optional[pd.DataFrame] = None,
    df_preds: Optional[pd.DataFrame] = None,
    df_geo: Optional[pd.DataFrame] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Compila el MVP desde archivos existentes o DataFrames preparados en staging.

    Las predicciones son obligatorias: nunca se sustituyen valores faltantes por
    un supuesto verde. El stock observado y el riesgo predictivo se conservan
    en campos separados.
    """
    master_path = DATA_PROCESSED_DIR / "insulinas_master.csv"
    preds_path = DATA_PROCESSED_DIR / "predicciones_probabilidad_stock.csv"
    geo_path = DATA_PROCESSED_DIR / "farmacias_geolocalizadas.csv"

    if df_master is None and not master_path.exists():
        raise FileNotFoundError(f"Falta el dataset maestro en: {master_path}")
    if df_preds is None and not preds_path.exists():
        raise FileNotFoundError(f"Falta el dataset de predicciones en: {preds_path}")
    if df_geo is None and not geo_path.exists():
        raise FileNotFoundError(f"Falta el dataset geolocalizado en: {geo_path}")

    df_master = pd.read_csv(master_path) if df_master is None else df_master.copy()
    df_preds = pd.read_csv(preds_path) if df_preds is None else df_preds.copy()
    df_geo = pd.read_csv(geo_path) if df_geo is None else df_geo.copy()

    if {"probabilidad_riesgo", "riesgo_predictivo"}.issubset(df_preds.columns):
        prediction_columns = ["id_insulina_master", "probabilidad_riesgo", "riesgo_predictivo"]
    elif {"probabilidad_randomforest", "semaforo_predictivo_ml"}.issubset(df_preds.columns):
        df_preds = df_preds.rename(columns={
            "probabilidad_randomforest": "probabilidad_riesgo",
            "semaforo_predictivo_ml": "riesgo_predictivo",
        })
        prediction_columns = ["id_insulina_master", "probabilidad_riesgo", "riesgo_predictivo"]
    else:
        raise ValueError("Faltan las columnas obligatorias de predicción del bundle.")

    if df_preds["id_insulina_master"].duplicated().any():
        raise ValueError("Existe más de una predicción para el mismo producto.")

    # Merge de insulinas con predicciones ML
    master_base = df_master.drop(
        columns=["probabilidad_riesgo", "riesgo_predictivo", "probabilidad_randomforest", "semaforo_predictivo_ml"],
        errors="ignore",
    )
    df_merged = master_base.merge(
        df_preds[prediction_columns],
        on="id_insulina_master",
        how="left",
        validate="one_to_one",
    )
    if df_merged[["probabilidad_riesgo", "riesgo_predictivo"]].isna().any().any():
        missing_ids = df_merged.loc[
            df_merged[["probabilidad_riesgo", "riesgo_predictivo"]].isna().any(axis=1),
            "id_insulina_master",
        ].tolist()
        raise ValueError(f"Predicción faltante para: {missing_ids}")

    # AGRUPACIÓN POR MEDICAMENTO / FORMULACIÓN
    medicamentos_dict: Dict[Tuple[str, str, str, float], Dict[str, Any]] = {}

    for _, row in df_merged.iterrows():
        key = (
            str(row["marca_comercial"]),
            str(row["principio_activo"]),
            str(row["formato_presentacion"]),
            float(row["volumen_ml"]),
        )

        if key not in medicamentos_dict:
            medicamentos_dict[key] = {
                "id": f"MED-{len(medicamentos_dict) + 1:02d}",
                "marca": str(row["marca_comercial"]),
                "principio_activo": str(row["principio_activo"]),
                "tipo_accion": str(row["tipo_accion"]),
                "formato": str(row["formato_presentacion"]),
                "volumen_ml": float(row["volumen_ml"]),
                "concentracion_ui_ml": int(row["concentracion_ui_ml"]),
                "unidades_totales": int(row["unidades_totales_ui"]),
                "laboratorio": str(row["laboratorio_fabricante"]),
                "origen_biologico": str(row["origen_biologico"]),
                "precios": {},
            }

        farmacia = str(row["farmacia"])
        precio_venta = float(row["precio_venta_bs"])
        precio_lista = float(row["precio_lista_bs"])
        precio_100ui = float(row["precio_por_100ui_bs"])
        descuento = float(row["descuento_porcentaje"])
        estado_stock = str(row.get("stock_actual", row.get("estado_stock", "NO_VERIFICADO")))
        stock_evidence = str(row.get("stock_evidence", "SOURCE_REPORTED"))
        if farmacia == "Farmacias Telchi" and stock_evidence == "SOURCE_REPORTED":
            estado_stock = "NO_VERIFICADO"
            stock_evidence = "CATALOG_ONLY"
        semaforo_ml = str(row["riesgo_predictivo"])
        prob_quiebre = float(row["probabilidad_riesgo"])
        stock_warning = (
            "Producto encontrado en catálogo; stock no confirmado"
            if estado_stock == "NO_VERIFICADO"
            else ""
        )

        medicamentos_dict[key]["precios"][farmacia] = {
            "disponible": estado_stock in {"DISPONIBLE", "ULTIMAS_UNIDADES"},
            "precio_venta_bs": precio_venta,
            "precio_lista_bs": precio_lista,
            "precio_por_100ui_bs": precio_100ui,
            "descuento_porcentaje": descuento,
            "stock_actual": estado_stock,
            "stock_evidence": stock_evidence,
            "stock_advertencia": stock_warning,
            "riesgo_predictivo": semaforo_ml,
            "probabilidad_riesgo": prob_quiebre,
            "fuente": str(row.get("url_producto", "")),
            "fecha_datos": str(row.get("timestamp_extraccion", "")),
            # Alias conservados para compatibilidad con consumidores existentes.
            "estado_stock": estado_stock,
            "semaforo_ml": semaforo_ml,
            "prob_quiebre_ml": prob_quiebre,
        }

    # Procesar métricas comparativas y SEMÁFORO COHERENTE CON LENGUAJE CIUDADANO (US-31)
    medicamentos_lista = []
    for key, med in medicamentos_dict.items():
        # Farmacias con stock físico activo (DISPONIBLE o ULTIMAS_UNIDADES)
        cadenas_activas = [
            (c, d["precio_venta_bs"], d["precio_por_100ui_bs"])
            for c, d in med["precios"].items()
            if d["disponible"] and d["estado_stock"] in ["DISPONIBLE", "ULTIMAS_UNIDADES"]
        ]
        cadenas_agotadas = [
            c for c, d in med["precios"].items()
            if d["estado_stock"] == "AGOTADO"
        ]
        cadenas_no_verificadas = [
            c for c, d in med["precios"].items()
            if d["estado_stock"] == "NO_VERIFICADO"
        ]
        hay_ultimas_unidades = any(
            d["estado_stock"] == "ULTIMAS_UNIDADES" for d in med["precios"].values()
        )

        # Cálculo de mejores precios y ahorro
        if cadenas_activas:
            cadenas_activas.sort(key=lambda x: x[1])
            mejor_cadena, mejor_precio, mejor_100ui = cadenas_activas[0]
            peor_cadena, peor_precio, _ = cadenas_activas[-1]
            ahorro_max = round(peor_precio - mejor_precio, 2)
        else:
            todos_precios = [
                (c, d["precio_venta_bs"], d["precio_por_100ui_bs"])
                for c, d in med["precios"].items()
            ]
            todos_precios.sort(key=lambda x: x[1])
            mejor_cadena, mejor_precio, mejor_100ui = todos_precios[0]
            peor_cadena, peor_precio, ahorro_max = todos_precios[-1][0], todos_precios[-1][1], 0.0

        # El semáforo general resume únicamente disponibilidad observada. El
        # riesgo del modelo permanece separado en cada registro de farmacia.
        if not cadenas_activas and cadenas_agotadas and not cadenas_no_verificadas:
            semaforo_general = "ROJO"
            motivo_semaforo = "No se observó disponibilidad en las farmacias consultadas"
            etiqueta_semaforo = "🔴 Sin disponibilidad observada"
        elif not cadenas_activas:
            semaforo_general = "AMARILLO"
            motivo_semaforo = "No hay disponibilidad confirmada; existen registros sin verificar"
            etiqueta_semaforo = "🟡 Disponibilidad no confirmada"
        elif hay_ultimas_unidades:
            semaforo_general = "AMARILLO"
            motivo_semaforo = "Se observaron últimas unidades; confirma antes de acudir"
            etiqueta_semaforo = "🟡 Pocas Unidades"
        elif cadenas_agotadas:
            semaforo_general = "AMARILLO"
            motivo_semaforo = f"Sin disponibilidad observada en {', '.join(cadenas_agotadas)}, con disponibilidad en otra farmacia"
            etiqueta_semaforo = "🟡 Disponibilidad Parcial"
        elif cadenas_no_verificadas:
            semaforo_general = "AMARILLO"
            motivo_semaforo = "Hay disponibilidad observada y también registros de stock no verificado"
            etiqueta_semaforo = "🟡 Verificación Parcial"
        elif len(med["precios"]) == 1:
            semaforo_general = "AMARILLO"
            motivo_semaforo = "Disponibilidad observada en una sola cadena farmacéutica"
            etiqueta_semaforo = "🟡 Oferta Única"
        else:
            semaforo_general = "VERDE"
            motivo_semaforo = "Disponible según datos observados en múltiples farmacias"
            etiqueta_semaforo = "🟢 Disponibilidad observada"

        med["mejor_cadena"] = mejor_cadena
        med["mejor_precio_bs"] = mejor_precio
        med["precio_max_bs"] = peor_precio
        med["ahorro_max_bs"] = ahorro_max
        med["mejor_precio_100ui_bs"] = mejor_100ui
        med["semaforo_general"] = semaforo_general
        med["motivo_semaforo"] = motivo_semaforo
        med["etiqueta_semaforo"] = etiqueta_semaforo
        med["total_farmacias_disp"] = len(med["precios"])
        med["total_farmacias_activas"] = len(cadenas_activas)

        medicamentos_lista.append(med)

    # Ordenar medicamentos por precio más económico por defecto
    medicamentos_lista.sort(key=lambda m: m["mejor_precio_bs"])

    # Consolidar sucursales geolocalizadas
    sucursales_lista = []
    for _, row in df_geo.iterrows():
        estado_anillo = str(row["estado_anillo"])
        anillo = row["anillo_asignado"]
        if estado_anillo == "ASIGNADO" and pd.notnull(anillo):
            anillo_num: Optional[float] = float(anillo)
            anillo_str = f"Anillo {int(anillo)}"
        else:
            anillo_num = None
            anillo_str = "Sin anillo confirmado"
        sucursales_lista.append({
            "id": str(row["id_sucursal"]),
            "farmacia": str(row["farmacia"]),
            "nombre": str(row["nombre_sucursal"]),
            "direccion": str(row["direccion"]),
            "ciudad": str(row["ciudad"]),
            "anillo_num": anillo_num,
            "anillo_etiqueta": anillo_str,
            "estado_anillo": estado_anillo,
            "estado_actividad": "NO_VERIFICADO",
            "fuente": str(row.get("fuente", "")),
            "fecha_verificacion": str(row.get("fecha_verificacion", "")),
            "advertencias": str(row.get("advertencias", "")) if pd.notna(row.get("advertencias", "")) else "",
        })

    # Resumen macro accesible
    resumen_macro = {
        "total_medicamentos": len(medicamentos_lista),
        "total_registros_crudos": len(df_master),
        "total_sucursales": len(sucursales_lista),
        "precio_min_bs": float(min(m["mejor_precio_bs"] for m in medicamentos_lista if m["mejor_precio_bs"] > 0)),
        "precio_max_bs": float(max(m["precio_max_bs"] for m in medicamentos_lista)),
        "total_verde": sum(1 for m in medicamentos_lista if m["semaforo_general"] == "VERDE"),
        "total_amarillo": sum(1 for m in medicamentos_lista if m["semaforo_general"] == "AMARILLO"),
        "total_rojo": sum(1 for m in medicamentos_lista if m["semaforo_general"] == "ROJO"),
        "metadata": metadata or {},
    }

    return medicamentos_lista, sucursales_lista, resumen_macro


def construir_html_mvp(
    medicamentos: List[Dict[str, Any]],
    sucursales: List[Dict[str, Any]],
    resumen: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Genera HTML5 accesible con estética pastel, trazabilidad y datos separados."""
    metadata = metadata or resumen.get("metadata", {})
    meds_json = json.dumps(medicamentos, ensure_ascii=False, sort_keys=True)
    sucursales_json = json.dumps(sucursales, ensure_ascii=False, sort_keys=True)
    resumen_json = json.dumps(resumen, ensure_ascii=False, sort_keys=True)
    metadata_json = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
    generated_at = str(metadata.get("generated_at", "No disponible"))
    data_as_of = str(metadata.get("data_as_of", "No disponible"))
    source_name = str(metadata.get("source_snapshot", {}).get("filename", "No disponible"))

    return f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth" style="font-size: 16px;">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Asistente de Insulina para Jubilados - Santa Cruz de la Sierra</title>
  <meta name="description" content="Comparador interactivo de precios, disponibilidad observada y riesgo predictivo de insulina en Santa Cruz de la Sierra (Farmacorp, Chávez, Telchi).">
  <meta property="og:title" content="Asistente de Insulina para Jubilados - Santa Cruz de la Sierra">
  <meta property="og:description" content="Compara precios entre farmacias, calcula tu presupuesto mensual y consulta por separado disponibilidad observada y riesgo predictivo.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://data-industry.github.io/Desarollo-Proyecto/">
  <link rel="canonical" href="https://data-industry.github.io/Desarollo-Proyecto/">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    body {{
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      background-color: #f7faf8;
      color: #1e293b;
    }}

    .focus-ring:focus {{
      outline: 3px solid #2d6a4f !important;
      outline-offset: 2px !important;
    }}

    /* Paleta Pastel Farmacéutica Natural y Limpia (Anti-IA) */
    .badge-verde {{
      background-color: #ebf7ee;
      color: #1b5e20;
      border: 1px solid #c3e6cb;
    }}
    .badge-amarillo {{
      background-color: #fef9e8;
      color: #855b0a;
      border: 1px solid #fbe59d;
    }}
    .badge-rojo {{
      background-color: #fdf2f2;
      color: #991b1b;
      border: 1px solid #f8c8c8;
    }}

    .card-pastel {{
      background-color: #ffffff;
      border: 1px solid #e3eae5;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03), 0 1px 2px rgba(0, 0, 0, 0.02);
      transition: all 0.2s ease-in-out;
    }}
    .card-pastel:hover {{
      border-color: #a3cfbb;
      box-shadow: 0 4px 12px rgba(45, 106, 79, 0.07);
    }}

    .transition-scale {{
      transition: transform 0.15s ease-in-out, background-color 0.15s ease;
    }}
    .transition-scale:active {{
      transform: scale(0.97);
    }}

    @keyframes fadeInSlide {{
      from {{ opacity: 0; transform: translateY(-6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .animate-fadeIn {{
      animation: fadeInSlide 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
  </style>
</head>
<body class="bg-[#f7faf8] text-slate-800 antialiased font-sans min-h-screen">

  <!-- ENCABEZADO ACCESIBLE CON BOTONES EXPLÍCITOS DE TAMAÑO DE LETRA (US-34) -->
  <header class="bg-[#1b4332] text-white shadow-sm sticky top-0 z-50 border-b border-[#2d6a4f]">
    <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <span class="text-3xl" aria-hidden="true">🩺</span>
        <div>
          <h1 class="text-xl md:text-2xl font-black tracking-tight text-white">Comparador de Insulina para Jubilados</h1>
          <p class="text-emerald-100/90 text-xs md:text-sm font-medium">Santa Cruz de la Sierra • Precios publicados por Farmacorp, Chávez y Telchi</p>
        </div>
      </div>

      <!-- CONTROLES DE ACCESIBILIDAD SENIOR: ACHICAR / AGRANDAR LETRA CON TEXTO EXPLÍCITO -->
      <div class="flex items-center gap-1.5 sm:gap-2 bg-[#2d6a4f]/70 p-1.5 rounded-xl border border-emerald-500/40">
        <span class="text-xs font-bold uppercase tracking-wider text-emerald-100 hidden lg:inline">Tamaño de letra:</span>
        <button id="btnFontMinus" onclick="ajustarFuente(-0.1)" class="px-2.5 py-1.5 rounded-lg bg-emerald-50 text-emerald-950 font-bold text-xs md:text-sm hover:bg-white focus-ring transition-scale flex items-center gap-1" title="Achicar tamaño de letra" aria-label="Achicar tamaño de letra">
          <span>🔍➖</span> Achicar letra
        </button>
        <span id="lblFontScale" class="text-xs font-extrabold text-white px-1.5 min-w-[42px] text-center">100%</span>
        <button id="btnFontPlus" onclick="ajustarFuente(0.1)" class="px-2.5 py-1.5 rounded-lg bg-emerald-50 text-emerald-950 font-bold text-xs md:text-sm hover:bg-white focus-ring transition-scale flex items-center gap-1" title="Agrandar tamaño de letra" aria-label="Agrandar tamaño de letra">
          <span>🔍➕</span> Agrandar letra
        </button>
        <button onclick="leerResumenVoz()" class="ml-1 sm:ml-2 px-3 py-1.5 rounded-lg bg-[#fef3c7] text-[#78350f] border border-[#fde68a] font-extrabold text-xs md:text-sm flex items-center gap-1.5 hover:bg-[#fde68a] focus-ring transition-scale" title="Escuchar resumen en audio">
          <span>🔊</span> <span class="hidden md:inline">Léeme en voz alta</span>
        </button>
      </div>
    </div>
  </header>

  <!-- CONTENEDOR PRINCIPAL -->
  <main class="max-w-6xl mx-auto px-4 py-6 space-y-6">

    <!-- BANNER DE BIENVENIDA LIMPIO Y EMPÁTICO -->
    <section class="card-pastel rounded-2xl p-5 md:p-6 border border-emerald-200/90 bg-[#f4f9f5] flex flex-col md:flex-row gap-5 items-center justify-between" aria-labelledby="sec-resumen">
      <div class="space-y-1.5">
        <h2 id="sec-resumen" class="text-lg md:text-2xl font-black text-[#1b4332] flex items-center gap-2">
          <span>👋</span> ¡Bienvenido! Compara precios y ahorra en tu insulina
        </h2>
        <p class="text-slate-600 text-sm md:text-base leading-relaxed">
          Cada tarjeta agrupa un medicamento y te lista los precios de <strong class="text-slate-900">Farmacorp, Farmacias Chávez y Farmacias Telchi</strong>, destacando la opción más económica para proteger tu pensión.
        </p>
      </div>
      <div class="flex flex-row md:flex-col gap-2.5 shrink-0">
        <div class="bg-white border border-emerald-200 rounded-xl px-4 py-2 text-center shadow-xs">
          <span class="block text-[11px] uppercase font-bold text-emerald-800">Precios desde</span>
          <span class="text-xl md:text-2xl font-black text-emerald-900" id="resumenPrecioMin">Bs {resumen['precio_min_bs']:.2f}</span>
        </div>
        <div class="bg-white border border-emerald-200 rounded-xl px-4 py-2 text-center shadow-xs">
          <span class="block text-[11px] uppercase font-bold text-emerald-800">Presentaciones comparadas</span>
          <span class="text-xl md:text-2xl font-black text-[#1b4332]">{resumen['total_medicamentos']} tipos</span>
        </div>
      </div>
    </section>

    <section class="card-pastel rounded-xl p-4 border border-blue-200 bg-blue-50 text-sm text-blue-950" aria-label="Trazabilidad de los datos">
      <p><strong>Fecha efectiva de los datos:</strong> {data_as_of} • <strong>Fecha de generación del bundle:</strong> {generated_at}</p>
      <p><strong>Snapshot fuente:</strong> {source_name}. Los precios y estados pueden cambiar; confirma precio y disponibilidad directamente con la farmacia antes de acudir.</p>
    </section>

    <!-- SEMÁFORO GENERAL DE DISPONIBILIDAD OBSERVADA (US-31/US-34) -->
    <section class="card-pastel rounded-2xl p-5 md:p-6 border border-[#e3eae5] space-y-4" aria-labelledby="sec-semaforo">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-[#e9f0eb] pb-3">
        <div>
          <h2 id="sec-semaforo" class="text-lg md:text-xl font-black text-slate-900 flex items-center gap-2">
            <span>🚦</span> Disponibilidad Observada en Farmacias
          </h2>
          <p class="text-slate-600 text-xs md:text-sm mt-0.5">
            Resumen de los estados observados en las fuentes consultadas. El riesgo predictivo se muestra por separado en cada farmacia.
          </p>
        </div>
        <div id="badgeSemaforoGlobal" class="px-3.5 py-1.5 rounded-xl text-xs md:text-sm font-extrabold flex items-center gap-1.5 badge-verde shadow-xs">
          <span>ℹ️</span> <span>DISPONIBILIDAD OBSERVADA: {resumen['total_verde']} VERDE • {resumen['total_amarillo']} AMARILLO • {resumen['total_rojo']} ROJO</span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-1">
        <div class="p-4 rounded-xl border border-[#c3e6cb] bg-[#ebf7ee] space-y-1">
          <div class="flex items-center gap-2 font-bold text-[#1b5e20] text-sm md:text-base">
            <span class="text-xl">🟢</span> VERDE (Disponibilidad Segura)
          </div>
          <p class="text-[#2e6f40] text-xs md:text-sm leading-relaxed">
            {resumen['total_verde']} presentaciones con disponibilidad observada en múltiples farmacias. Confirma antes de acudir.
          </p>
        </div>

        <div class="p-4 rounded-xl border border-[#fbe59d] bg-[#fef9e8] space-y-1">
          <div class="flex items-center gap-2 font-bold text-[#855b0a] text-sm md:text-base">
            <span class="text-xl">🟡</span> AMARILLO (Precaución)
          </div>
          <p class="text-[#8c6b1b] text-xs md:text-sm leading-relaxed">
            {resumen['total_amarillo']} presentaciones con disponibilidad parcial, últimas unidades o datos sin verificar. Confirma con la farmacia.
          </p>
        </div>

        <div class="p-4 rounded-xl border border-[#f8c8c8] bg-[#fdf2f2] space-y-1">
          <div class="flex items-center gap-2 font-bold text-[#991b1b] text-sm md:text-base">
            <span class="text-xl">🔴</span> ROJO (Agotado General)
          </div>
          <p class="text-[#a83232] text-xs md:text-sm leading-relaxed">
            {resumen['total_rojo']} presentaciones sin disponibilidad observada en las fuentes consultadas. Confirma con la farmacia.
          </p>
        </div>
      </div>
    </section>

    <!-- GLOSARIO CIUDADANO COMPACTO Y NO INVASIVO (US-34) -->
    <section id="sec-glosario" class="card-pastel rounded-xl p-3 border border-emerald-200/80 bg-emerald-50/40" aria-label="Glosario Ciudadano">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <span class="text-xl">📖</span>
          <div>
            <h2 class="text-sm md:text-base font-bold text-emerald-950 inline">Glosario de Términos Amigables:</h2>
            <span class="text-xs text-slate-500 ml-1 hidden sm:inline">Pasa el mouse o presiona el botón para consultar definiciones sencillas</span>
          </div>
        </div>
        <button id="btnToggleGlosario" onclick="toggleGlosario()" onmouseenter="mostrarGlosario(true)" class="px-3 py-1.5 bg-white hover:bg-emerald-50 text-emerald-900 border border-emerald-300 rounded-lg text-xs md:text-sm font-bold flex items-center gap-1.5 shadow-xs focus-ring transition-scale" aria-expanded="false" aria-controls="glosarioContenido">
          <span>📖 Glosario de Términos</span>
          <span id="iconoGlosario" class="text-xs">▼</span>
        </button>
      </div>

      <!-- Contenedor desplegable (no ocupa espacio en pantalla cuando está recogido) -->
      <div id="glosarioContenido" class="hidden mt-3 pt-3 border-t border-emerald-200/70 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 animate-fadeIn">
        <!-- Tarjeta 1: Quiebre de stock -->
        <div class="bg-white p-3.5 rounded-xl border border-emerald-100 shadow-xs space-y-1">
          <div class="flex items-center gap-1.5 text-emerald-900 font-extrabold text-xs md:text-sm">
            <span>📦</span> ¿Qué es "Quiebre de stock"?
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            Situación en la que una farmacia reporta que agotó sus existencias de una insulina y no puede reponerla de inmediato. El reporte debe confirmarse directamente con la farmacia.
          </p>
        </div>

        <!-- Tarjeta 2: Disponibilidad observada y riesgo predictivo -->
        <div class="bg-white p-3.5 rounded-xl border border-emerald-100 shadow-xs space-y-1">
          <div class="flex items-center gap-1.5 text-emerald-900 font-extrabold text-xs md:text-sm">
            <span>🚦</span> ¿Cómo funciona el Semáforo?
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            La <strong>disponibilidad observada</strong> describe el stock reportado por la fuente (Verde: segura, Amarillo: precaución, Rojo: agotada). El <strong>riesgo predictivo</strong> es una estimación del modelo y se muestra por separado; no confirma inventario ni convierte un producto disponible en agotado. Confirma con la farmacia antes de acudir.
          </p>
        </div>

        <!-- Tarjeta 3: Cálculo del Ahorro -->
        <div class="bg-white p-3.5 rounded-xl border border-emerald-100 shadow-xs space-y-1">
          <div class="flex items-center gap-1.5 text-emerald-900 font-extrabold text-xs md:text-sm">
            <span>💰</span> ¿Cómo se calcula tu Ahorro?
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            Restamos el precio de la farmacia más cara menos el de la más barata para el <strong>mismo medicamento exacto</strong>. La diferencia es el dinero en Bolivianos que te queda en el bolsillo al elegir bien.
          </p>
        </div>

        <!-- Tarjeta 4: Concentración U-100 -->
        <div class="bg-white p-3.5 rounded-xl border border-emerald-100 shadow-xs space-y-1">
          <div class="flex items-center gap-1.5 text-emerald-900 font-extrabold text-xs md:text-sm">
            <span>💉</span> ¿Qué significa "U-100"?
          </div>
          <p class="text-slate-600 text-xs leading-relaxed">
            Significa que cada mililitro contiene <strong>100 Unidades Internacionales</strong> de insulina. Es la presentación estándar en Bolivia. Asegúrate de usar siempre jeringas graduadas para U-100.
          </p>
        </div>
      </div>
    </section>

    <!-- CALCULADORA DE DOSIS Y PRESUPUESTO MENSUAL DEL JUBILADO (REUBICADA ANTES DEL CATÁLOGO - US-34) -->
    <section class="card-pastel rounded-2xl p-5 md:p-6 border border-amber-200/90 bg-[#fffdf7] space-y-5" aria-labelledby="sec-calculadora">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200/70 pb-3">
        <div>
          <h2 id="sec-calculadora" class="text-lg md:text-xl font-extrabold text-amber-950 flex items-center gap-2">
            <span>🧮</span> Calculadora de Ahorro y Presupuesto Mensual para tu Pensión
          </h2>
          <p class="text-amber-900/80 text-xs md:text-sm mt-0.5">
            Ingresa la dosis diaria recetada por tu médico para saber cuántos frascos necesitas y cuánto dinero ahorras al mes comprando en la farmacia más económica.
          </p>
        </div>
        <span class="text-xs font-bold text-amber-800 bg-amber-100/80 px-2.5 py-1 rounded-full border border-amber-200">
          Herramienta de Ahorro
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 items-center">
        <div class="space-y-1.5">
          <label for="inputDosisDiaria" class="block font-bold text-slate-800 text-sm">¿Cuántas Unidades (UI) usas al día?</label>
          <div class="flex items-center gap-2.5">
            <input type="number" id="inputDosisDiaria" min="1" max="150" placeholder="Tu dosis" onchange="calcularPresupuesto()" class="w-28 p-2.5 bg-white border border-amber-300 rounded-xl font-black text-xl text-center text-slate-900 focus-ring">
            <span class="font-bold text-slate-600 text-sm">UI / día</span>
          </div>
          <span class="text-xs text-slate-500 block">Ingresa únicamente la dosis indicada por tu profesional de salud.</span>
        </div>

        <div class="space-y-1.5">
          <label for="selectTipoInsulinaCalc" class="block font-bold text-slate-800 text-sm">Insulina que utilizas:</label>
          <select id="selectTipoInsulinaCalc" onchange="calcularPresupuesto()" class="w-full p-2.5 bg-white border border-amber-300 rounded-xl font-bold text-slate-800 text-sm focus-ring">
            <option value="Novolin N">Novolin N (NPH 10 ml Vial)</option>
            <option value="Novolin R">Novolin R (Regular 10 ml Vial)</option>
            <option value="Novolin 70/30">Novolin 70/30 (Mixta 10 ml Vial)</option>
            <option value="Lantus">Lantus (Glargina 10 ml Vial)</option>
            <option value="Basalog">Basalog (Glargina 10 ml Vial)</option>
            <option value="Apidra">Apidra (Glulisina 3 ml Pluma)</option>
          </select>
          <span class="text-xs text-slate-500 block">Calcula automáticamente frascos y ahorro al mes.</span>
        </div>

        <div class="bg-white p-4 rounded-xl border border-amber-300/80 shadow-xs space-y-1.5 text-center md:text-left">
          <span class="block text-xs uppercase font-extrabold text-amber-800 tracking-wider">Resultado Estimado al Mes (30 días)</span>
          <div class="text-xl md:text-2xl font-black text-emerald-800" id="calcResumenAhorro">Calculando ahorro...</div>
          <p class="text-slate-600 text-xs leading-relaxed" id="calcDetalleFrascos">Cálculo de frascos y presupuesto en curso.</p>
        </div>
      </div>
    </section>

    <!-- PASO 1: PANEL DE FILTROS RÁPIDOS CON BOTÓN FILTRAR FUNCIONAL Y COHERENTE (US-34) -->
    <section class="card-pastel rounded-2xl p-5 md:p-6 border border-[#e3eae5] space-y-4" aria-labelledby="sec-filtros">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-[#e9f0eb] pb-3">
        <div>
          <h2 id="sec-filtros" class="text-lg md:text-xl font-black text-slate-900 flex items-center gap-2">
            <span>🔍</span> Paso 1: Busca tu Medicamento
          </h2>
          <span class="text-xs md:text-sm text-slate-500">Ajusta los filtros deseados y presiona "Filtrar Catálogo" para actualizar</span>
        </div>
        <div id="lblFiltroEstado" class="text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
          ✓ Catálogo cargado
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Filtro Principio Activo -->
        <div class="space-y-1.5">
          <label for="filtroPrincipio" class="block font-bold text-slate-800 text-sm">Tipo de Insulina / Principio Activo:</label>
          <select id="filtroPrincipio" onchange="marcarFiltrosPendientes()" class="w-full p-2.5 bg-white border border-[#cbd5e1] rounded-xl font-medium text-slate-800 text-sm focus-ring">
            <option value="TODOS">Todas las insulinas</option>
            <option value="Glargina">Insulina Glargina (Lantus, Basalog, Glaripen, Toujeo)</option>
            <option value="Regular">Insulina Regular / Rápida (Novolin R, Densulin R)</option>
            <option value="NPH">Insulina NPH / Intermedia (Novolin N, Humodar NPH)</option>
            <option value="Mixta">Insulina Mixta / 70/30 (Novolin 70/30)</option>
            <option value="Glulisina">Insulina Glulisina (Apidra)</option>
            <option value="Asparta">Insulina Asparta (Asparpen)</option>
          </select>
        </div>

        <!-- Filtro Formato -->
        <div class="space-y-1.5">
          <label for="filtroFormato" class="block font-bold text-slate-800 text-sm">Presentación / Envase:</label>
          <select id="filtroFormato" onchange="marcarFiltrosPendientes()" class="w-full p-2.5 bg-white border border-[#cbd5e1] rounded-xl font-medium text-slate-800 text-sm focus-ring">
            <option value="TODOS">Todos los envases</option>
            <option value="Vial">Frasco Ampolla / Vial (10 ml)</option>
            <option value="Cartucho">Cartucho para Pluma (3 ml)</option>
            <option value="Lapicero">Pluma Descartable Prellenada</option>
          </select>
        </div>

        <!-- Filtro Cadena de Farmacia -->
        <div class="space-y-1.5">
          <label for="filtroFarmacia" class="block font-bold text-slate-800 text-sm">Cadena de Farmacias:</label>
          <select id="filtroFarmacia" onchange="marcarFiltrosPendientes()" class="w-full p-2.5 bg-white border border-[#cbd5e1] rounded-xl font-medium text-slate-800 text-sm focus-ring">
            <option value="TODAS">Todas las cadenas (Comparar las 3)</option>
            <option value="Farmacorp">Disponible en Farmacorp</option>
            <option value="Chávez">Disponible en Farmacias Chávez</option>
            <option value="Telchi">Disponible en Farmacias Telchi</option>
          </select>
        </div>
      </div>

      <!-- Buscador por texto -->
      <div class="space-y-1.5">
        <label for="inputBusqueda" class="block font-bold text-slate-800 text-sm">O escribe el nombre comercial (presiona Enter o el botón para buscar):</label>
        <div class="relative">
          <input type="text" id="inputBusqueda" oninput="marcarFiltrosPendientes()" onkeydown="if(event.key==='Enter') aplicarFiltros()" placeholder="Ejemplo: Lantus, Novolin, Basalog, Apidra..." class="w-full p-2.5 pl-10 bg-white border border-[#cbd5e1] rounded-xl font-medium text-slate-800 text-sm focus-ring">
          <span class="absolute left-3 top-2.5 text-base text-slate-400" aria-hidden="true">🔎</span>
        </div>
      </div>

      <!-- BOTONES DE ACCIÓN: FILTRAR EXPLÍCITO Y LIMPIAR (US-34) -->
      <div class="flex flex-wrap items-center gap-3 pt-1">
        <button id="btnAplicarFiltros" onclick="aplicarFiltros()" class="px-5 py-2.5 bg-[#2d6a4f] hover:bg-[#1b4332] text-white font-black text-sm md:text-base rounded-xl flex items-center justify-center gap-2 shadow-xs transition-scale focus-ring">
          <span>🔍</span> Filtrar Catálogo
        </button>
        <button id="btnLimpiarFiltros" onclick="limpiarFiltros()" class="px-4 py-2.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 font-bold text-xs md:text-sm rounded-xl flex items-center justify-center gap-1.5 transition-scale focus-ring">
          <span>↺</span> Ver Todos los Medicamentos
        </button>
      </div>
    </section>

    <!-- CATÁLOGO AGRUPADO: CADA MEDICAMENTO CON COMPARATIVA PASTEL DE LAS 3 CADENAS -->
    <section class="space-y-4" aria-labelledby="sec-catalogo">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 id="sec-catalogo" class="text-lg md:text-xl font-black text-slate-900 flex items-center gap-2">
            <span>🏷️</span> Comparativa de Precios entre las 3 Cadenas
          </h2>
          <p class="text-slate-600 text-xs md:text-sm" id="lblResultadosConteo">
            Mostrando {resumen['total_medicamentos']} medicamentos. Cada tarjeta lista los precios de Farmacorp, Chávez y Telchi.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs font-bold text-slate-600">Ordenar por:</span>
          <select id="selectOrden" onchange="aplicarFiltros()" class="p-2 border border-slate-300 rounded-lg font-bold text-xs bg-white text-slate-800 focus-ring">
            <option value="precio_asc">Precio más bajo primero (Mayor ahorro)</option>
            <option value="precio_desc">Precio más alto primero</option>
            <option value="ahorro_desc">Mayor ahorro entre farmacias</option>
            <option value="nombre_asc">Nombre alfabético (A-Z)</option>
          </select>
        </div>
      </div>

      <!-- Contenedor dinámico de tarjetas agrupadas -->
      <div id="contenedorMedicamentos" class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- Renderizado dinámico vía JavaScript -->
      </div>
    </section>

    <!-- BUSCADOR TERRITORIAL POR ANILLOS (1 AL 8 EN SANTA CRUZ) -->
    <section class="card-pastel rounded-2xl p-5 md:p-6 border border-[#e3eae5] space-y-4" aria-labelledby="sec-anillos">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-[#e9f0eb] pb-3">
        <div>
          <h2 id="sec-anillos" class="text-lg md:text-xl font-black text-slate-900 flex items-center gap-2">
            <span>📍</span> Paso 2: Consulta Sucursales por Anillo
          </h2>
          <p class="text-slate-600 text-xs md:text-sm mt-0.5">
            Listado de sucursales y evidencia territorial disponible. No se calcula distancia ni cercanía.
          </p>
        </div>

        <!-- Selector de Anillo -->
        <div class="flex items-center gap-2">
          <label for="selectAnilloFiltro" class="font-bold text-slate-700 text-xs">Filtrar por Anillo:</label>
          <select id="selectAnilloFiltro" onchange="filtrarSucursales()" class="p-2 bg-white border border-slate-300 rounded-lg font-bold text-slate-800 text-xs focus-ring">
            <option value="TODOS">Todas las sucursales</option>
            <option value="2">2do Anillo (Piraí, Trinidad, Cotoca, Charcas)</option>
            <option value="3">3er Anillo (Santos Dumont, Mutualista)</option>
            <option value="4">4to Anillo (Paraguá)</option>
            <option value="7">7mo Anillo (Av. Banzer)</option>
            <option value="SIN_EVIDENCIA">Sin anillo verificado</option>
          </select>
        </div>
      </div>

      <!-- Tabla de sucursales con paleta pastel limpia -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse" id="tablaSucursales">
          <thead>
            <tr class="bg-[#f4f8f5] text-slate-700 font-extrabold text-xs border-b border-[#dce6df]">
              <th class="p-3">Cadena</th>
              <th class="p-3">Nombre de Sucursal</th>
              <th class="p-3">Anillo Urbano</th>
              <th class="p-3">Dirección Confirmada</th>
              <th class="p-3">Estado de Sucursal</th>
            </tr>
          </thead>
          <tbody id="tbodySucursales" class="divide-y divide-[#edf2ee] text-xs md:text-sm">
            <!-- Renderizado dinámico vía JavaScript -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- CONSEJOS PRÁCTICOS PARA EL ADULTO MAYOR EN PALETA PASTEL DE FARMACIA -->
    <section class="card-pastel rounded-2xl p-5 md:p-6 border border-emerald-200/90 bg-[#f4f9f5] space-y-2.5">
      <h3 class="text-base md:text-lg font-extrabold text-[#1b4332] flex items-center gap-2">
        <span>💡</span> Consejos Importantes para el Jubilado y su Familia
      </h3>
      <ul class="list-disc list-inside space-y-1.5 text-slate-700 text-xs md:text-sm font-medium leading-relaxed">
        <li><strong>Conserva la cadena de frío:</strong> Al retirar tu insulina en la farmacia, llévala siempre en bolsa térmica o con un gel refrigerante sin congelar directamente el frasco.</li>
        <li><strong>Verifica la concentración:</strong> En Bolivia la mayoría de insulinas son U-100 (100 Unidades por mililitro). Usa siempre jeringas graduadas para U-100.</li>
        <li><strong>Confirma antes de acudir:</strong> Verifica directamente con la farmacia el precio y la disponibilidad actuales.</li>
      </ul>
    </section>

  </main>

  <!-- PIE DE PÁGINA ACCESIBLE -->
  <footer class="bg-[#1b4332] text-emerald-100/80 py-6 text-center text-xs border-t border-[#2d6a4f] mt-10">
    <div class="max-w-6xl mx-auto px-4 space-y-1">
      <p class="font-bold text-white">Asistente Ciudadano de Precios y Disponibilidad de Insulina • Santa Cruz de la Sierra</p>
      <p>Desarrollado para el Proyecto Integrador • Datos provenientes de fuentes de Farmacorp, Chávez y Telchi.</p>
    </div>
  </footer>

  <!-- DATOS REALES EMBEBIDOS Y LÓGICA INTERACTIVA -->
  <script>
    // Inyección de datos reales compilados
    const DATA_MEDICAMENTOS = {meds_json};
    const DATA_SUCURSALES = {sucursales_json};
    const DATA_RESUMEN = {resumen_json};
    const DATA_METADATA = {metadata_json};

    let escalaFuenteActual = 1.0;

    // 1. CONTROL DE ZOOM DE FUENTE (Afecta a todo el documento via root font-size)
    function ajustarFuente(delta) {{
      escalaFuenteActual = Math.max(0.85, Math.min(1.5, escalaFuenteActual + delta));
      document.documentElement.style.fontSize = (16 * escalaFuenteActual) + 'px';
      const lblScale = document.getElementById('lblFontScale');
      if (lblScale) {{
        lblScale.textContent = Math.round(escalaFuenteActual * 100) + '%';
      }}
    }}

    // 2. TOGGLE Y VISIBILIDAD DEL GLOSARIO COMPACTO (US-34)
    function toggleGlosario() {{
      const panel = document.getElementById('glosarioContenido');
      const icono = document.getElementById('iconoGlosario');
      const btn = document.getElementById('btnToggleGlosario');
      if (!panel) return;
      const estaOculto = panel.classList.contains('hidden');
      if (estaOculto) {{
        panel.classList.remove('hidden');
        if (icono) icono.textContent = '▲';
        if (btn) btn.setAttribute('aria-expanded', 'true');
      }} else {{
        panel.classList.add('hidden');
        if (icono) icono.textContent = '▼';
        if (btn) btn.setAttribute('aria-expanded', 'false');
      }}
    }}

    function mostrarGlosario(abrir) {{
      const panel = document.getElementById('glosarioContenido');
      const icono = document.getElementById('iconoGlosario');
      const btn = document.getElementById('btnToggleGlosario');
      if (!panel) return;
      if (abrir) {{
        panel.classList.remove('hidden');
        if (icono) icono.textContent = '▲';
        if (btn) btn.setAttribute('aria-expanded', 'true');
      }}
    }}

    // 3. ESTADOS PENDIENTES DEL FILTRADO (US-34)
    function marcarFiltrosPendientes() {{
      const lbl = document.getElementById('lblFiltroEstado');
      const btn = document.getElementById('btnAplicarFiltros');
      if (lbl) {{
        lbl.className = 'text-xs font-bold text-amber-800 bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200 animate-pulse';
        lbl.textContent = '● Presiona "Filtrar Catálogo" para ver cambios';
      }}
      if (btn) {{
        btn.classList.add('ring-2', 'ring-emerald-400');
      }}
    }}

    // 4. RENDERIZADO DE TARJETAS AGRUPADAS CON COMPARATIVA PASTEL DE LAS 3 CADENAS
    function renderizarMedicamentos(medicamentos) {{
      const contenedor = document.getElementById('contenedorMedicamentos');
      const lblConteo = document.getElementById('lblResultadosConteo');
      contenedor.innerHTML = '';

      lblConteo.textContent = `Mostrando ${{medicamentos.length}} medicamentos. Cada tarjeta compara los precios de Farmacorp, Chávez y Telchi.`;

      if (medicamentos.length === 0) {{
        contenedor.innerHTML = `
          <div class="col-span-full bg-white p-8 rounded-2xl border border-dashed border-slate-300 text-center space-y-3">
            <span class="text-4xl block">🔍</span>
            <p class="text-lg font-bold text-slate-800">No encontramos medicamentos con los filtros seleccionados.</p>
            <p class="text-slate-500 text-sm">Prueba cambiando el tipo de insulina o presiona "Ver Todos los Medicamentos".</p>
            <button onclick="limpiarFiltros()" class="mt-2 px-5 py-2.5 bg-[#2d6a4f] text-white font-bold rounded-xl shadow-xs hover:bg-[#1b4332] transition-scale">
              Mostrar Todo el Catálogo
            </button>
          </div>
        `;
        return;
      }}

      const cadenas = ["Farmacias Chávez", "Farmacorp", "Farmacias Telchi"];

      medicamentos.forEach(med => {{
        const card = document.createElement('article');
        card.className = "card-pastel rounded-2xl p-5 border border-[#e3eae5] flex flex-col justify-between space-y-4 hover:border-emerald-300 transition-all";

        // Badge del semáforo general: disponibilidad observada, no predicción.
        let semaforoBadge = '';
        if (med.semaforo_general === 'VERDE') {{
          semaforoBadge = `<span class="px-2.5 py-1 rounded-lg text-xs font-black badge-verde" title="${{med.motivo_semaforo}}">🟢 Disponibilidad observada</span>`;
        }} else if (med.semaforo_general === 'AMARILLO') {{
          semaforoBadge = `<span class="px-2.5 py-1 rounded-lg text-xs font-black badge-amarillo" title="${{med.motivo_semaforo}}">🟡 Disponibilidad parcial</span>`;
        }} else {{
          semaforoBadge = `<span class="px-2.5 py-1 rounded-lg text-xs font-black badge-rojo" title="${{med.motivo_semaforo}}">🔴 Sin disponibilidad observada</span>`;
        }}

        // Construir filas de la comparativa de farmacias con estética pastel
        let filasFarmaciasHTML = '';
        cadenas.forEach(cadena => {{
          const info = med.precios[cadena];
          if (info) {{
            const tieneStock = info.disponible && info.estado_stock !== 'AGOTADO';
            const esElMejor = (cadena === med.mejor_cadena && med.total_farmacias_activas > 1 && tieneStock);

            filasFarmaciasHTML += `
              <div class="p-3 rounded-xl border ${{esElMejor ? 'bg-[#f0f9f3] border-[#bfe5cd] ring-1 ring-[#cdeade]' : 'bg-[#fafcfb] border-[#eaf0eb]'}} flex items-center justify-between gap-2">
                <div class="space-y-0.5">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-slate-800 text-sm md:text-base">${{cadena}}</span>
                    ${{esElMejor ? '<span class="px-2 py-0.5 rounded-full text-[11px] font-black bg-[#2d6a4f] text-white uppercase tracking-wider">⭐ Mejor Precio</span>' : ''}}
                  </div>
                  <span class="text-xs text-slate-500 block">
                    Por 100 UI: <strong>Bs ${{info.precio_por_100ui_bs.toFixed(2)}}</strong> • 
                    <span class="${{info.stock_actual === 'AGOTADO' ? 'text-rose-600 font-bold' : (info.stock_actual === 'ULTIMAS_UNIDADES' ? 'text-amber-600 font-bold' : (info.stock_actual === 'NO_VERIFICADO' ? 'text-slate-600 font-bold' : 'text-emerald-700'))}}">
                      Stock actual: ${{info.stock_actual}}
                    </span>
                  </span>
                  <span class="text-xs text-slate-500 block">Riesgo predictivo: <strong>${{info.riesgo_predictivo}}</strong> (${{(info.probabilidad_riesgo * 100).toFixed(1)}}%)</span>
                  ${{info.stock_advertencia ? `<span class="text-xs text-amber-700 font-bold block">${{info.stock_advertencia}}</span>` : ''}}
                  <span class="text-xs text-slate-500 block">Datos: ${{info.fecha_datos}} • <a class="underline" href="${{info.fuente}}" target="_blank" rel="noopener noreferrer">Ver fuente</a></span>
                </div>
                <div class="text-right">
                  <span class="text-xl font-black text-slate-900 block">Bs ${{info.precio_venta_bs.toFixed(2)}}</span>
                </div>
              </div>
            `;
          }} else {{
            // No disponible en esta cadena
            filasFarmaciasHTML += `
              <div class="p-2.5 rounded-xl border border-dashed border-[#e2e8f0] bg-[#fafbfc] flex items-center justify-between opacity-60">
                <span class="font-medium text-slate-500 text-xs">${{cadena}}</span>
                <span class="text-xs text-slate-400 italic">No disponible en catálogo</span>
              </div>
            `;
          }}
        }});

        card.innerHTML = `
          <div class="space-y-3">
            <!-- Encabezado de la tarjeta -->
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="text-lg md:text-xl font-black text-slate-900 leading-snug">${{med.marca}}</h3>
                <p class="text-sm font-bold text-emerald-800">${{med.principio_activo}}</p>
                <p class="text-xs text-slate-500">${{med.formato}} • ${{med.volumen_ml}} ml (${{med.unidades_totales}} UI) • Lab. ${{med.laboratorio}}</p>
              </div>
              <div class="shrink-0 flex flex-col items-end gap-1">
                ${{semaforoBadge}}
                <span class="text-[10px] text-slate-500 text-right max-w-[130px] leading-tight">${{med.motivo_semaforo}}</span>
              </div>
            </div>

            <!-- Resumen de Ahorro Destacado en Paleta Pastel -->
            ${{med.ahorro_max_bs > 0 && med.total_farmacias_activas > 1 ? `
              <div class="bg-[#ebf7ee] border border-[#bfe5cd] p-3 rounded-xl flex items-center justify-between gap-2">
                <div class="flex items-center gap-2">
                  <span class="text-xl">💵</span>
                  <div>
                    <span class="text-xs uppercase font-extrabold text-[#1b5e20] block">Ahorro Máximo en tu Compra:</span>
                    <span class="text-sm md:text-base font-black text-[#1b4332]">Ahorras Bs ${{med.ahorro_max_bs.toFixed(2)}} comprando en ${{med.mejor_cadena}}</span>
                  </div>
                </div>
                <span class="text-xs font-bold bg-white text-[#1b5e20] px-2.5 py-1 rounded-lg border border-[#c3e6cb] shrink-0">
                  Mejor opción
                </span>
              </div>
            ` : (med.total_farmacias_activas === 1 ? `
              <div class="bg-[#f8faf9] border border-[#e2e8f0] p-2.5 rounded-xl text-xs text-slate-600 font-medium">
                Disponibilidad observada a Bs ${{med.mejor_precio_bs.toFixed(2)}} en ${{med.mejor_cadena}} (única farmacia con existencias observadas).
              </div>
            ` : (med.total_farmacias_activas === 0 && med.semaforo_general === 'ROJO' ? `
              <div class="bg-[#fdf2f2] border border-[#f8c8c8] p-2.5 rounded-xl text-xs text-[#991b1b] font-medium">
                Sin disponibilidad observada en las fuentes consultadas. Confirma con la farmacia.
              </div>
            ` : (med.total_farmacias_activas === 0 ? `
              <div class="bg-[#fef9e8] border border-[#fbe59d] p-2.5 rounded-xl text-xs text-[#855b0a] font-medium">
                No hay disponibilidad confirmada; existen registros sin verificar. Confirma con la farmacia.
              </div>
            ` : `
              <div class="bg-[#f8faf9] border border-[#e2e8f0] p-2.5 rounded-xl text-xs text-slate-600 font-medium">
                Disponibilidad observada a Bs ${{med.mejor_precio_bs.toFixed(2)}} en ${{med.mejor_cadena}}.
              </div>
            `)))}}

            <!-- Lista comparativa de las 3 farmacias -->
            <div class="space-y-2 pt-1">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500 block">Comparativa por Farmacia:</span>
              ${{filasFarmaciasHTML}}
            </div>
          </div>
        `;
        contenedor.appendChild(card);
      }});
    }}

    // 5. LÓGICA DE FILTRADO ROBUSTA CON BOTÓN EXPLÍCITO (US-34)
    function aplicarFiltros() {{
      const principioSel = document.getElementById('filtroPrincipio').value;
      const formatoSel = document.getElementById('filtroFormato').value;
      const farmaciaSel = document.getElementById('filtroFarmacia').value;
      const busqueda = document.getElementById('inputBusqueda').value.toLowerCase().trim();
      const orden = document.getElementById('selectOrden').value;

      let filtrados = DATA_MEDICAMENTOS.filter(med => {{
        // Filtro principio activo
        let matchPrincipio = true;
        if (principioSel !== 'TODOS') {{
          matchPrincipio = med.principio_activo.toLowerCase().includes(principioSel.toLowerCase()) ||
                           med.marca.toLowerCase().includes(principioSel.toLowerCase());
        }}

        // Filtro formato
        let matchFormato = true;
        if (formatoSel !== 'TODOS') {{
          matchFormato = med.formato.toLowerCase().includes(formatoSel.toLowerCase());
        }}

        // Filtro farmacia
        let matchFarmacia = true;
        if (farmaciaSel !== 'TODAS') {{
          matchFarmacia = Object.keys(med.precios).some(cad => cad.toLowerCase().includes(farmaciaSel.toLowerCase()));
        }}

        // Filtro texto libre
        let matchTexto = true;
        if (busqueda) {{
          matchTexto = med.marca.toLowerCase().includes(busqueda) ||
                       med.principio_activo.toLowerCase().includes(busqueda) ||
                       med.laboratorio.toLowerCase().includes(busqueda);
        }}

        return matchPrincipio && matchFormato && matchFarmacia && matchTexto;
      }});

      // Ordenamiento
      if (orden === 'precio_asc') {{
        filtrados.sort((a, b) => a.mejor_precio_bs - b.mejor_precio_bs);
      }} else if (orden === 'precio_desc') {{
        filtrados.sort((a, b) => b.mejor_precio_bs - a.mejor_precio_bs);
      }} else if (orden === 'ahorro_desc') {{
        filtrados.sort((a, b) => b.ahorro_max_bs - a.ahorro_max_bs);
      }} else if (orden === 'nombre_asc') {{
        filtrados.sort((a, b) => a.marca.localeCompare(b.marca));
      }}

      renderizarMedicamentos(filtrados);

      // Feedback visual del estado de filtrado
      const lbl = document.getElementById('lblFiltroEstado');
      const btn = document.getElementById('btnAplicarFiltros');
      if (lbl) {{
        lbl.className = 'text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200';
        lbl.textContent = `✓ Catálogo filtrado (${{filtrados.length}} encontrados)`;
      }}
      if (btn) {{
        btn.classList.remove('ring-2', 'ring-emerald-400');
      }}
    }}

    // 6. LIMPIAR FILTROS
    function limpiarFiltros() {{
      document.getElementById('filtroPrincipio').value = 'TODOS';
      document.getElementById('filtroFormato').value = 'TODOS';
      document.getElementById('filtroFarmacia').value = 'TODAS';
      document.getElementById('inputBusqueda').value = '';
      document.getElementById('selectOrden').value = 'precio_asc';
      aplicarFiltros();
    }}

    // 7. FILTRAR SUCURSALES POR ANILLO
    function filtrarSucursales() {{
      const anilloSel = document.getElementById('selectAnilloFiltro').value;
      const tbody = document.getElementById('tbodySucursales');
      tbody.innerHTML = '';

      let filtradas = DATA_SUCURSALES.filter(s => {{
        if (anilloSel === 'TODOS') return true;
        if (anilloSel === 'SIN_EVIDENCIA') return s.anillo_num === null;
        return (s.anillo_num === parseFloat(anilloSel));
      }});

      filtradas.forEach(s => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-[#f9fbf9] transition-colors';
        tr.innerHTML = `
          <td class="p-3 font-bold text-slate-800">${{s.farmacia}}</td>
          <td class="p-3 font-semibold text-emerald-950">${{s.nombre}}</td>
          <td class="p-3">
            <span class="px-2.5 py-1 rounded-md text-xs font-extrabold ${{s.anillo_num !== null && s.anillo_num <= 2 ? 'bg-[#ebf3f7] text-[#1e4a62]' : 'bg-[#edf2ee] text-slate-700'}}">
              ${{s.anillo_etiqueta}}
            </span>
          </td>
          <td class="p-3 text-slate-600 text-xs md:text-sm">${{s.direccion}}</td>
          <td class="p-3">
            <span class="text-xs font-bold text-slate-700 bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200">
              Estado no verificado
            </span>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // 8. CALCULADORA DE PRESUPUESTO Y AHORRO
    function calcularPresupuesto() {{
      const dosis = parseFloat(document.getElementById('inputDosisDiaria').value);
      const marca = document.getElementById('selectTipoInsulinaCalc').value;
      const lblAhorro = document.getElementById('calcResumenAhorro');
      const lblDetalle = document.getElementById('calcDetalleFrascos');
      if (!Number.isFinite(dosis) || dosis <= 0) {{
        lblAhorro.textContent = 'Ingresa tu dosis indicada';
        lblDetalle.textContent = 'Usa únicamente la dosis indicada por tu profesional de salud.';
        return;
      }}
      const dosisMensual = dosis * 30;

      // Buscar en medicamentos
      const med = DATA_MEDICAMENTOS.find(m => m.marca.toLowerCase().includes(marca.toLowerCase()));
      if (!med) return;

      const volumenPorFrasco = med.unidades_totales || 1000;
      const frascosNecesarios = Math.ceil(dosisMensual / volumenPorFrasco);

      const precios = Object.values(med.precios)
        .filter(p => p.disponible)
        .map(p => p.precio_venta_bs);
      if (precios.length === 0) {{
        lblAhorro.textContent = 'Sin disponibilidad confirmada';
        lblDetalle.textContent = 'Confirma precio y disponibilidad directamente con la farmacia.';
        return;
      }}
      const minPrecio = Math.min(...precios);
      const maxPrecio = Math.max(...precios);
      const ahorroTotal = ((maxPrecio - minPrecio) * frascosNecesarios).toFixed(2);

      if (minPrecio === maxPrecio || precios.length <= 1) {{
        lblAhorro.textContent = `Gasto estimado al mes: Bs ${{(minPrecio * frascosNecesarios).toFixed(2)}}`;
      }} else {{
        lblAhorro.textContent = `Ahorras Bs ${{ahorroTotal}} al mes`;
      }}

      lblDetalle.textContent = `Con la dosis ingresada de ${{dosis}} UI/día, el cálculo estima ${{frascosNecesarios}} frasco(s) de ${{volumenPorFrasco}} UI para 30 días (${{dosisMensual}} UI). Menor precio con disponibilidad observada: Bs ${{minPrecio.toFixed(2)}} en ${{med.mejor_cadena}}.`;
    }}

    // 9. LECTURA POR VOZ DIDÁCTICA
    function leerResumenVoz() {{
      if (!('speechSynthesis' in window)) {{
        alert('Tu navegador no soporta lectura por voz.');
        return;
      }}
      const texto = `Hola. En este momento el sistema compara ${{DATA_RESUMEN.total_medicamentos}} presentaciones de insulina en Santa Cruz de la Sierra. Cada tarjeta separa el stock observado del riesgo predictivo. Confirma precio y disponibilidad directamente con la farmacia antes de acudir.`;
      const utterance = new SpeechSynthesisUtterance(texto);
      utterance.lang = 'es-BO';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }}

    // 10. INICIALIZACIÓN
    window.addEventListener('DOMContentLoaded', () => {{
      // Carga inicial directa
      aplicarFiltros();
      filtrarSucursales();
      calcularPresupuesto();
    }});
  </script>
</body>
</html>
"""


def exportar_mvp() -> None:
    """Genera y guarda el HTML interactivo sincronizado en las 6 ubicaciones clave (incluyendo GitHub Pages)."""
    SRC_UI_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_HTML.parent.mkdir(parents=True, exist_ok=True)

    medicamentos, sucursales, resumen = compilar_datos_reales()
    html_content = construir_html_mvp(medicamentos, sucursales, resumen)

    # 1. Guardar en src/ui/
    with open(UI_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"MVP interactivo actualizado en: {UI_HTML}")

    # 2. Guardar en raíz del proyecto (nombre histórico y index.html para GitHub Pages raíz)
    with open(ROOT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(ROOT_INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Copia accesible actualizada en raíz (mvp y index.html): {ROOT_HTML}")

    # 3. Guardar en docs/ (Criterio de Aceptación US-31 y US-35 para GitHub Pages /docs)
    with open(DOCS_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(DOCS_INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Copias de producción actualizadas en docs/ (mvp y index.html): {DOCS_INDEX_HTML}")

    # 4. Guardar como Artefacto de Antigravity
    with open(ARTIFACT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Artefacto oficial actualizado en: {ARTIFACT_HTML}")


if __name__ == "__main__":
    exportar_mvp()
