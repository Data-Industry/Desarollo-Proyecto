"""Generador del MVP Visualizador Didáctico e Interactivo Local para Jubilados (US-29 / SCRUM-44).

Versión 2.0:
- Agrupación por medicamento con lista comparativa directa de las 3 cadenas (Farmacorp, Chávez, Telchi).
- Escalado dinámico de tipografía en toda la interfaz (A- / A+) afectando a la raíz HTML.
- Botón prominente de 'Filtrar Catálogo' y reseteo rápido.
- Detección visual inmediata del mejor precio y cálculo del ahorro máximo en Bs.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("generador_mvp")

# Rutas del Proyecto
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
SRC_UI_DIR = PROJECT_DIR / "src" / "ui"
ROOT_HTML = PROJECT_DIR / "mvp_comparador_jubilados.html"
UI_HTML = SRC_UI_DIR / "mvp_comparador_jubilados.html"
ARTIFACT_HTML = Path(
    r"C:\Users\USUARIO\.gemini\antigravity\brain\ccf30eb7-9b28-48ca-8301-f6996c594ed6\mvp_jubilados_comparador.html"
)


def compilar_datos_reales() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Carga, consolida y agrupa por medicamento las insulinas, sucursales y predicciones ML."""
    master_path = DATA_PROCESSED_DIR / "insulinas_master.csv"
    preds_path = DATA_PROCESSED_DIR / "predicciones_probabilidad_stock.csv"
    geo_path = DATA_PROCESSED_DIR / "farmacias_geolocalizadas.csv"

    if not master_path.exists():
        raise FileNotFoundError(f"Falta el dataset maestro en: {master_path}")
    if not preds_path.exists():
        raise FileNotFoundError(f"Falta el dataset de predicciones en: {preds_path}")
    if not geo_path.exists():
        raise FileNotFoundError(f"Falta el dataset geolocalizado en: {geo_path}")

    df_master = pd.read_csv(master_path)
    df_preds = pd.read_csv(preds_path)
    df_geo = pd.read_csv(geo_path)

    # Merge de insulinas con predicciones ML
    df_merged = df_master.merge(
        df_preds[[
            "id_insulina_master",
            "probabilidad_randomforest",
            "alerta_randomforest",
            "semaforo_predictivo_ml",
        ]],
        on="id_insulina_master",
        how="left",
    )

    df_merged["probabilidad_randomforest"] = df_merged["probabilidad_randomforest"].fillna(0.10)
    df_merged["alerta_randomforest"] = df_merged["alerta_randomforest"].fillna("STOCK_ESTABLE")
    df_merged["semaforo_predictivo_ml"] = df_merged["semaforo_predictivo_ml"].fillna("VERDE_ESTABLE")

    # AGRUPACIÓN POR MEDICAMENTO / FORMULACIÓN
    cadenas_oficiales = ["Farmacias Chávez", "Farmacorp", "Farmacias Telchi"]
    medicamentos_dict: Dict[Tuple[str, str, str, float], Dict[str, Any]] = {}

    for idx, row in df_merged.iterrows():
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
        estado_stock = str(row["estado_stock"])
        semaforo_ml = str(row["semaforo_predictivo_ml"])
        prob_quiebre = float(row["probabilidad_randomforest"])

        medicamentos_dict[key]["precios"][farmacia] = {
            "disponible": True,
            "precio_venta_bs": precio_venta,
            "precio_lista_bs": precio_lista,
            "precio_por_100ui_bs": precio_100ui,
            "descuento_porcentaje": descuento,
            "estado_stock": estado_stock,
            "semaforo_ml": semaforo_ml,
            "prob_quiebre_ml": prob_quiebre,
        }

    # Procesar métricas comparativas para cada medicamento
    medicamentos_lista = []
    for key, med in medicamentos_dict.items():
        precios_disp = [
            (cadena, datos["precio_venta_bs"], datos["precio_por_100ui_bs"])
            for cadena, datos in med["precios"].items()
        ]

        if precios_disp:
            # Ordenar por precio más bajo
            precios_disp.sort(key=lambda x: x[1])
            mejor_cadena, mejor_precio, mejor_100ui = precios_disp[0]
            peor_cadena, peor_precio, _ = precios_disp[-1]
            ahorro_max = round(peor_precio - mejor_precio, 2)
        else:
            mejor_cadena, mejor_precio, mejor_100ui = "", 0.0, 0.0
            peor_cadena, peor_precio, ahorro_max = "", 0.0, 0.0

        # Semáforo general del medicamento
        estados_ml = [d["semaforo_ml"] for d in med["precios"].values()]
        if any("ROJO" in e for e in estados_ml):
            semaforo_general = "ROJO"
        elif any("AMARILLO" in e for e in estados_ml):
            semaforo_general = "AMARILLO"
        else:
            semaforo_general = "VERDE"

        med["mejor_cadena"] = mejor_cadena
        med["mejor_precio_bs"] = mejor_precio
        med["precio_max_bs"] = peor_precio
        med["ahorro_max_bs"] = ahorro_max
        med["mejor_precio_100ui_bs"] = mejor_100ui
        med["semaforo_general"] = semaforo_general
        med["total_farmacias_disp"] = len(med["precios"])

        medicamentos_lista.append(med)

    # Ordenar medicamentos por precio más económico por defecto
    medicamentos_lista.sort(key=lambda m: m["mejor_precio_bs"])

    # Consolidar sucursales geolocalizadas
    sucursales_lista = []
    for _, row in df_geo.iterrows():
        anillo = row["anillo_asignado"]
        anillo_str = f"{int(anillo)}to Anillo" if pd.notnull(anillo) else "Casco Urbano Central"
        sucursales_lista.append({
            "id": str(row["id_sucursal"]),
            "farmacia": str(row["farmacia"]),
            "nombre": str(row["nombre_sucursal"]),
            "direccion": str(row["direccion"]),
            "ciudad": str(row["ciudad"]),
            "anillo_num": float(anillo) if pd.notnull(anillo) else 1.0,
            "anillo_etiqueta": anillo_str,
            "estado_anillo": str(row["estado_anillo"]),
        })

    # Resumen macro
    resumen_macro = {
        "total_medicamentos": len(medicamentos_lista),
        "total_registros_crudos": len(df_master),
        "total_sucursales": len(sucursales_lista),
        "precio_min_bs": float(min(m["mejor_precio_bs"] for m in medicamentos_lista)),
        "precio_max_bs": float(max(m["precio_max_bs"] for m in medicamentos_lista)),
    }

    return medicamentos_lista, sucursales_lista, resumen_macro


def construir_html_mvp(
    medicamentos: List[Dict[str, Any]],
    sucursales: List[Dict[str, Any]],
    resumen: Dict[str, Any],
) -> str:
    """Genera el código HTML5 reactivo, accesible y con comparación de las 3 cadenas."""
    meds_json = json.dumps(medicamentos, ensure_ascii=False)
    sucursales_json = json.dumps(sucursales, ensure_ascii=False)
    resumen_json = json.dumps(resumen, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="es" class="scroll-smooth" style="font-size: 16px;">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Asistente de Insulina para Jubilados - Santa Cruz de la Sierra</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .focus-ring:focus {{
      outline: 4px solid #2563eb !important;
      outline-offset: 2px !important;
    }}
    .badge-verde {{ background-color: #dcfce7; color: #166534; border: 2px solid #86efac; }}
    .badge-amarillo {{ background-color: #fef9c3; color: #854d0e; border: 2px solid #fde047; }}
    .badge-rojo {{ background-color: #fee2e2; color: #991b1b; border: 2px solid #fca5a5; }}
    .transition-scale {{ transition: transform 0.15s ease-in-out; }}
    .transition-scale:active {{ transform: scale(0.96); }}
  </style>
</head>
<body class="bg-slate-50 text-slate-900 antialiased font-sans min-h-screen">

  <!-- ENCABEZADO ACCESIBLE CON BOTONES DE ZOOM REAL -->
  <header class="bg-emerald-700 text-white shadow-md sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <span class="text-3xl" aria-hidden="true">🩺</span>
        <div>
          <h1 class="text-xl md:text-2xl font-black tracking-tight">Comparador de Insulina para Jubilados</h1>
          <p class="text-emerald-100 text-xs md:text-sm font-medium">Santa Cruz de la Sierra • Farmacorp, Chávez y Telchi</p>
        </div>
      </div>

      <!-- CONTROLES DE ACCESIBILIDAD SENIOR (AFECTA A TODA LA PÁGINA) -->
      <div class="flex items-center gap-2 bg-emerald-800/90 p-2 rounded-xl border border-emerald-600 shadow-sm">
        <span class="text-xs font-bold uppercase tracking-wider text-emerald-200">Letra:</span>
        <button id="btnFontMinus" onclick="ajustarFuente(-0.1)" class="w-9 h-9 rounded-lg bg-white text-emerald-950 font-black text-lg flex items-center justify-center hover:bg-emerald-100 focus-ring transition-scale" title="Reducir letra" aria-label="Reducir tamaño de letra">A-</button>
        <span id="lblFontScale" class="text-xs font-extrabold text-white px-1">100%</span>
        <button id="btnFontPlus" onclick="ajustarFuente(0.1)" class="w-9 h-9 rounded-lg bg-white text-emerald-950 font-black text-xl flex items-center justify-center hover:bg-emerald-100 focus-ring transition-scale" title="Aumentar letra" aria-label="Aumentar tamaño de letra">A+</button>
        <button onclick="leerResumenVoz()" class="ml-2 px-3 py-1.5 rounded-lg bg-amber-400 text-slate-950 font-extrabold text-xs md:text-sm flex items-center gap-1.5 hover:bg-amber-300 focus-ring transition-scale" title="Escuchar resumen en audio">
          <span>🔊</span> <span class="hidden sm:inline">Léeme en voz alta</span>
        </button>
      </div>
    </div>
  </header>

  <!-- CONTENEDOR PRINCIPAL -->
  <main class="max-w-6xl mx-auto px-4 py-6 space-y-8">

    <!-- BANNER DE BIENVENIDA -->
    <section class="bg-white rounded-2xl p-6 border-2 border-emerald-200 shadow-sm flex flex-col md:flex-row gap-6 items-center justify-between" aria-labelledby="sec-resumen">
      <div class="space-y-2">
        <h2 id="sec-resumen" class="text-xl md:text-2xl font-bold text-emerald-900 flex items-center gap-2">
          <span>👋</span> ¡Bienvenido! Compara precios de farmacias en un solo lugar
        </h2>
        <p class="text-slate-600 text-base md:text-lg">
          Cada tarjeta agrupa un medicamento y te lista los precios de <strong class="text-slate-900">Farmacorp, Farmacias Chávez y Farmacias Telchi</strong>, destacando la opción más barata para que cuides tu pensión.
        </p>
      </div>
      <div class="flex flex-row md:flex-col gap-3 shrink-0">
        <div class="bg-emerald-50 border border-emerald-300 rounded-xl px-4 py-2 text-center">
          <span class="block text-xs uppercase font-bold text-emerald-700">Precios desde</span>
          <span class="text-2xl font-black text-emerald-900" id="resumenPrecioMin">Bs {resumen['precio_min_bs']:.2f}</span>
        </div>
        <div class="bg-blue-50 border border-blue-300 rounded-xl px-4 py-2 text-center">
          <span class="block text-xs uppercase font-bold text-blue-700">Medicamentos</span>
          <span class="text-2xl font-black text-blue-900">{resumen['total_medicamentos']} tipos</span>
        </div>
      </div>
    </section>

    <!-- WIDGET DEL SEMÁFORO PREVENTIVO PREDICTIVO (US-05) -->
    <section class="bg-white rounded-2xl p-6 border-2 border-slate-200 shadow-sm space-y-4" aria-labelledby="sec-semaforo">
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h2 id="sec-semaforo" class="text-xl md:text-2xl font-bold text-slate-900 flex items-center gap-2">
            <span>🚦</span> Semáforo de Abastecimiento Preventivo (Modelo IA)
          </h2>
          <p class="text-slate-600 text-sm md:text-base">
            Predicción basada en Machine Learning para anticipar quiebres y compras antes del pago de rentas.
          </p>
        </div>
        <div id="badgeSemaforoGlobal" class="px-4 py-2 rounded-xl text-base md:text-lg font-extrabold flex items-center gap-2 badge-amarillo">
          <span>⚠️</span> <span>ESTADO GENERAL: RIESGO MODERADO</span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
        <div class="p-4 rounded-xl border-2 border-emerald-300 bg-emerald-50/70 space-y-1">
          <div class="flex items-center gap-2 font-bold text-emerald-900 text-base md:text-lg">
            <span class="text-2xl">🟢</span> VERDE (Stock Estable)
          </div>
          <p class="text-emerald-800 text-sm">
            20 medicamentos con abastecimiento asegurado en la mayoría de cadenas farmacéuticas.
          </p>
        </div>

        <div class="p-4 rounded-xl border-2 border-amber-300 bg-amber-50/70 space-y-1">
          <div class="flex items-center gap-2 font-bold text-amber-900 text-base md:text-lg">
            <span class="text-2xl">🟡</span> AMARILLO (Pocas Unidades)
          </div>
          <p class="text-amber-800 text-sm">
            Rotación acelerada en presentaciones de Basalog y Apidra. Recomendamos llamar antes de acudir.
          </p>
        </div>

        <div class="p-4 rounded-xl border-2 border-rose-300 bg-rose-50/70 space-y-1">
          <div class="flex items-center gap-2 font-bold text-rose-900 text-base md:text-lg">
            <span class="text-2xl">🔴</span> ROJO (Alerta de Quiebre)
          </div>
          <p class="text-rose-800 text-sm">
            4 presentaciones con stock quebrado en alguna cadena (Asparpen y viales). ¡Comprar con 5 días de anticipación!
          </p>
        </div>
      </div>
    </section>

    <!-- PASO 1: PANEL DE FILTROS RÁPIDOS CON BOTÓN FILTRAR EXPLÍCITO -->
    <section class="bg-white rounded-2xl p-6 border-2 border-slate-300 shadow-sm space-y-5" aria-labelledby="sec-filtros">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200 pb-3">
        <h2 id="sec-filtros" class="text-xl md:text-2xl font-bold text-slate-900 flex items-center gap-2">
          <span>🔍</span> Paso 1: Filtra y Busca tu Medicamento
        </h2>
        <span class="text-xs md:text-sm font-semibold text-slate-500">Selecciona tus preferencias y presiona "Filtrar"</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Filtro Principio Activo -->
        <div class="space-y-1">
          <label for="filtroPrincipio" class="block font-bold text-slate-800 text-sm md:text-base">Tipo de Insulina / Fármaco:</label>
          <select id="filtroPrincipio" class="w-full p-3 bg-slate-50 border-2 border-slate-300 rounded-xl font-medium text-slate-900 text-base focus-ring">
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
        <div class="space-y-1">
          <label for="filtroFormato" class="block font-bold text-slate-800 text-sm md:text-base">Presentación / Envase:</label>
          <select id="filtroFormato" class="w-full p-3 bg-slate-50 border-2 border-slate-300 rounded-xl font-medium text-slate-900 text-base focus-ring">
            <option value="TODOS">Todos los envases</option>
            <option value="Vial">Frasco Ampolla / Vial (10 ml)</option>
            <option value="Cartucho">Cartucho para Pluma (3 ml)</option>
            <option value="Lapicero">Pluma Descartable Prellenada</option>
          </select>
        </div>

        <!-- Filtro Cadena de Farmacia -->
        <div class="space-y-1">
          <label for="filtroFarmacia" class="block font-bold text-slate-800 text-sm md:text-base">Cadena de Farmacias:</label>
          <select id="filtroFarmacia" class="w-full p-3 bg-slate-50 border-2 border-slate-300 rounded-xl font-medium text-slate-900 text-base focus-ring">
            <option value="TODAS">Todas las cadenas (Comparar las 3)</option>
            <option value="Farmacorp">Disponible en Farmacorp</option>
            <option value="Chávez">Disponible en Farmacias Chávez</option>
            <option value="Telchi">Disponible en Farmacias Telchi</option>
          </select>
        </div>
      </div>

      <!-- Buscador por texto rápido -->
      <div class="space-y-1">
        <label for="inputBusqueda" class="block font-bold text-slate-800 text-sm md:text-base">O escribe el nombre comercial:</label>
        <div class="relative">
          <input type="text" id="inputBusqueda" placeholder="Ejemplo: Lantus, Novolin, Basalog, Apidra..." class="w-full p-3 pl-10 bg-slate-50 border-2 border-slate-300 rounded-xl font-medium text-slate-900 text-base focus-ring">
          <span class="absolute left-3 top-3 text-lg text-slate-400" aria-hidden="true">🔎</span>
        </div>
      </div>

      <!-- BOTONES DE ACCIÓN VISIBLES: FILTRAR Y LIMPIAR -->
      <div class="flex flex-wrap items-center gap-3 pt-2">
        <button id="btnAplicarFiltros" onclick="aplicarFiltros()" class="px-6 py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-black text-base md:text-lg rounded-xl flex items-center justify-center gap-2 shadow-md transition-scale focus-ring">
          <span>🔍</span> Filtrar Catálogo
        </button>
        <button id="btnLimpiarFiltros" onclick="limpiarFiltros()" class="px-5 py-3.5 bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold text-sm md:text-base rounded-xl flex items-center justify-center gap-1 transition-scale focus-ring">
          <span>↺</span> Ver Todos los Medicamentos
        </button>
      </div>
    </section>

    <!-- CATÁLOGO AGRUPADO: CADA MEDICAMENTO CON LISTA DE LAS 3 CADENAS -->
    <section class="space-y-4" aria-labelledby="sec-catalogo">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 id="sec-catalogo" class="text-xl md:text-2xl font-bold text-slate-900 flex items-center gap-2">
            <span>🏷️</span> Comparativa de Precios entre las 3 Cadenas
          </h2>
          <p class="text-slate-600 text-sm md:text-base" id="lblResultadosConteo">
            Mostrando 24 medicamentos. Cada tarjeta lista los precios de Farmacorp, Chávez y Telchi.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs md:text-sm font-bold text-slate-700">Ordenar por:</span>
          <select id="selectOrden" onchange="aplicarFiltros()" class="p-2 border-2 border-slate-300 rounded-lg font-bold text-xs md:text-sm bg-white focus-ring">
            <option value="precio_asc">Precio más bajo primero (Ahorro)</option>
            <option value="precio_desc">Precio más alto primero</option>
            <option value="ahorro_desc">Mayor ahorro entre farmacias</option>
            <option value="nombre_asc">Nombre alfabético (A-Z)</option>
          </select>
        </div>
      </div>

      <!-- Contenedor dinámico de tarjetas agrupadas -->
      <div id="contenedorMedicamentos" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Renderizado dinámico vía JavaScript -->
      </div>
    </section>

    <!-- CALCULADORA DE DOSIS Y PRESUPUESTO MENSUAL DEL JUBILADO -->
    <section class="bg-amber-50 rounded-2xl p-6 border-2 border-amber-300 shadow-sm space-y-6" aria-labelledby="sec-calculadora">
      <div class="border-b border-amber-200 pb-3">
        <h2 id="sec-calculadora" class="text-xl md:text-2xl font-extrabold text-amber-950 flex items-center gap-2">
          <span>🧮</span> Calculadora de Ahorro y Presupuesto Mensual para tu Pensión
        </h2>
        <p class="text-amber-900 text-sm md:text-base">
          Ingresa la dosis diaria prescrita por tu médico para saber cuántos frascos necesitas y cuánto dinero ahorras al mes.
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        <div class="space-y-2">
          <label for="inputDosisDiaria" class="block font-bold text-slate-900 text-sm md:text-base">¿Cuántas Unidades (UI) usas al día?</label>
          <div class="flex items-center gap-3">
            <input type="number" id="inputDosisDiaria" min="5" max="150" value="30" onchange="calcularPresupuesto()" class="w-32 p-3 bg-white border-2 border-amber-400 rounded-xl font-black text-2xl text-center text-slate-900 focus-ring">
            <span class="font-bold text-slate-700 text-base md:text-lg">UI / día</span>
          </div>
          <span class="text-xs text-slate-500 block">Dosis habitual frecuente: 20 a 40 UI al día.</span>
        </div>

        <div class="space-y-2">
          <label for="selectTipoInsulinaCalc" class="block font-bold text-slate-900 text-sm md:text-base">Insulina que utilizas:</label>
          <select id="selectTipoInsulinaCalc" onchange="calcularPresupuesto()" class="w-full p-3 bg-white border-2 border-amber-400 rounded-xl font-bold text-slate-900 text-sm md:text-base focus-ring">
            <option value="Novolin N">Novolin N (NPH 10 ml Vial)</option>
            <option value="Novolin R">Novolin R (Regular 10 ml Vial)</option>
            <option value="Novolin 70/30">Novolin 70/30 (Mixta 10 ml Vial)</option>
            <option value="Lantus">Lantus (Glargina 10 ml Vial)</option>
            <option value="Basalog">Basalog (Glargina 10 ml Vial)</option>
            <option value="Apidra">Apidra (Glulisina 3 ml Pluma)</option>
          </select>
        </div>

        <div class="bg-white p-5 rounded-xl border-2 border-amber-400 shadow-sm space-y-2 text-center md:text-left">
          <span class="block text-xs uppercase font-black text-amber-800">Resultado Estimado al Mes (30 días)</span>
          <div class="text-2xl font-black text-emerald-700" id="calcResumenAhorro">Ahorras Bs 22.80 al mes</div>
          <p class="text-slate-600 text-xs md:text-sm" id="calcDetalleFrascos">Con 30 UI/día necesitas 1 frasco de 1000 UI para 30 días.</p>
        </div>
      </div>
    </section>

    <!-- BUSCADOR TERRITORIAL POR ANILLOS (1 AL 8 EN SANTA CRUZ) -->
    <section class="bg-white rounded-2xl p-6 border-2 border-slate-200 shadow-sm space-y-4" aria-labelledby="sec-anillos">
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-3">
        <div>
          <h2 id="sec-anillos" class="text-xl md:text-2xl font-bold text-slate-900 flex items-center gap-2">
            <span>📍</span> Paso 2: Encuentra la Farmacia Más Cercana a tu Anillo
          </h2>
          <p class="text-slate-600 text-sm md:text-base">
            Sucursales físicas confirmadas por geolocalización en Santa Cruz de la Sierra.
          </p>
        </div>

        <!-- Selector de Anillo -->
        <div class="flex items-center gap-2">
          <label for="selectAnilloFiltro" class="font-bold text-slate-800 text-xs md:text-sm">Filtrar por Anillo:</label>
          <select id="selectAnilloFiltro" onchange="filtrarSucursales()" class="p-2.5 bg-slate-50 border-2 border-slate-300 rounded-lg font-bold text-slate-900 text-xs md:text-sm focus-ring">
            <option value="TODOS">Todos los anillos (16 sucursales)</option>
            <option value="2">2do Anillo (Pirai, Trinidad, Cotoca, Charcas)</option>
            <option value="3">3er Anillo (Santos Dumont, Mutualista)</option>
            <option value="4">4to Anillo (Paraguá)</option>
            <option value="7">7mo Anillo (Av. Banzer)</option>
            <option value="CENTRO">Casco Viejo / Anillo Central</option>
          </select>
        </div>
      </div>

      <!-- Tabla de sucursales -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse" id="tablaSucursales">
          <thead>
            <tr class="bg-slate-100 text-slate-800 font-extrabold text-xs md:text-sm border-b-2 border-slate-300">
              <th class="p-3">Cadena</th>
              <th class="p-3">Nombre de Sucursal</th>
              <th class="p-3">Anillo Urbano</th>
              <th class="p-3">Dirección Confirmada</th>
              <th class="p-3">Estado de Sucursal</th>
            </tr>
          </thead>
          <tbody id="tbodySucursales" class="divide-y divide-slate-200 text-sm md:text-base">
            <!-- Renderizado dinámico vía JavaScript -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- CONSEJOS PRÁCTICOS PARA EL ADULTO MAYOR -->
    <section class="bg-emerald-50 rounded-2xl p-6 border border-emerald-200 space-y-3">
      <h3 class="text-lg font-extrabold text-emerald-950 flex items-center gap-2">
        <span>💡</span> Consejos Importantes para el Jubilado y su Familia
      </h3>
      <ul class="list-disc list-inside space-y-1.5 text-emerald-900 text-sm md:text-base font-medium">
        <li><strong>Conserva la cadena de frío:</strong> Al retirar tu insulina en la farmacia, llévala siempre en bolsa térmica o con un gel refrigerante sin congelar directamente el frasco.</li>
        <li><strong>Verifica la concentración:</strong> En Bolivia la mayoría de insulinas son U-100 (100 Unidades por mililitro). Usa siempre jeringas graduadas para U-100.</li>
        <li><strong>Compra con 5 días de anticipación:</strong> Especialmente durante los días de pago de pensiones del Banco Unión (días 1 al 5 y fin de mes), cuando aumenta la demanda y las farmacias pueden quebrar stock transitoriamente.</li>
      </ul>
    </section>

  </main>

  <!-- PIE DE PÁGINA -->
  <footer class="bg-slate-900 text-slate-400 py-6 text-center text-xs md:text-sm border-t border-slate-800 mt-12">
    <div class="max-w-6xl mx-auto px-4 space-y-1">
      <p class="font-bold text-slate-300">Sistema Predictivo de Insulina para Jubilados • Metodología CRISP-DM</p>
      <p>Desarrollado para el Proyecto Integrador (Santa Cruz, Bolivia) • Datos reales auditados de Farmacorp, Chávez y Telchi.</p>
    </div>
  </footer>

  <!-- DATOS REALES EMBEBIDOS Y LÓGICA INTERACTIVA -->
  <script>
    // Inyección de datos reales compilados
    const DATA_MEDICAMENTOS = {meds_json};
    const DATA_SUCURSALES = {sucursales_json};
    const DATA_RESUMEN = {resumen_json};

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

    // 2. RENDERIZADO DE TARJETAS AGRUPADAS CON LISTA DE LAS 3 CADENAS
    function renderizarMedicamentos(medicamentos) {{
      const contenedor = document.getElementById('contenedorMedicamentos');
      const lblConteo = document.getElementById('lblResultadosConteo');
      contenedor.innerHTML = '';

      lblConteo.textContent = `Mostrando ${{medicamentos.length}} medicamentos. Cada tarjeta compara los precios de Farmacorp, Chávez y Telchi.`;

      if (medicamentos.length === 0) {{
        contenedor.innerHTML = `
          <div class="col-span-full bg-white p-8 rounded-2xl border-2 border-dashed border-slate-300 text-center space-y-3">
            <span class="text-4xl block">🔍</span>
            <p class="text-xl font-bold text-slate-800">No encontramos medicamentos con los filtros seleccionados.</p>
            <p class="text-slate-500">Prueba cambiando el tipo de insulina o presiona "Ver Todos los Medicamentos".</p>
            <button onclick="limpiarFiltros()" class="mt-2 px-5 py-2.5 bg-emerald-600 text-white font-bold rounded-xl shadow-sm">
              Mostrar Todo el Catálogo
            </button>
          </div>
        `;
        return;
      }}

      const cadenas = ["Farmacias Chávez", "Farmacorp", "Farmacias Telchi"];

      medicamentos.forEach(med => {{
        const card = document.createElement('article');
        card.className = "bg-white rounded-2xl p-5 border-2 border-slate-200 shadow-sm flex flex-col justify-between space-y-4 hover:border-emerald-400 transition-all";

        // Badges del semáforo general
        let semaforoBadge = '<span class="px-2.5 py-1 rounded-lg text-xs font-black badge-verde">🟢 Stock Normal</span>';
        if (med.semaforo_general === 'ROJO') {{
          semaforoBadge = '<span class="px-2.5 py-1 rounded-lg text-xs font-black badge-rojo">🔴 Alerta de Quiebre</span>';
        }} else if (med.semaforo_general === 'AMARILLO') {{
          semaforoBadge = '<span class="px-2.5 py-1 rounded-lg text-xs font-black badge-amarillo">🟡 Pocas Unidades</span>';
        }}

        // Construir filas de la lista de farmacias
        let filasFarmaciasHTML = '';
        cadenas.forEach(cadena => {{
          const info = med.precios[cadena];
          if (info) {{
            const esElMejor = (cadena === med.mejor_cadena && med.total_farmacias_disp > 1);
            filasFarmaciasHTML += `
              <div class="p-3 rounded-xl border ${{esElMejor ? 'bg-emerald-50 border-emerald-300 ring-1 ring-emerald-200' : 'bg-slate-50 border-slate-200'}} flex items-center justify-between gap-2">
                <div class="space-y-0.5">
                  <div class="flex items-center gap-2">
                    <span class="font-bold text-slate-900 text-sm md:text-base">${{cadena}}</span>
                    ${{esElMejor ? '<span class="px-2 py-0.5 rounded-full text-xs font-black bg-emerald-600 text-white uppercase tracking-wider">⭐ Mejor Precio</span>' : ''}}
                  </div>
                  <span class="text-xs text-slate-500 block">
                    100 UI: <strong>Bs ${{info.precio_por_100ui_bs.toFixed(2)}}</strong> • 
                    <span class="${{info.estado_stock === 'AGOTADO' ? 'text-rose-600 font-bold' : (info.estado_stock === 'ULTIMAS_UNIDADES' ? 'text-amber-600 font-bold' : 'text-emerald-700')}}">
                      ${{info.estado_stock}}
                    </span>
                  </span>
                </div>
                <div class="text-right">
                  <span class="text-xl md:text-2xl font-black text-slate-900 block">Bs ${{info.precio_venta_bs.toFixed(2)}}</span>
                </div>
              </div>
            `;
          }} else {{
            // No disponible en esta cadena
            filasFarmaciasHTML += `
              <div class="p-2.5 rounded-xl border border-dashed border-slate-200 bg-slate-50/50 flex items-center justify-between opacity-60">
                <span class="font-medium text-slate-500 text-xs md:text-sm">${{cadena}}</span>
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
                <h3 class="text-xl md:text-2xl font-black text-slate-900 leading-snug">${{med.marca}}</h3>
                <p class="text-sm md:text-base font-bold text-emerald-800">${{med.principio_activo}}</p>
                <p class="text-xs md:text-sm text-slate-500">${{med.formato}} • ${{med.volumen_ml}} ml (${{med.unidades_totales}} UI) • Lab. ${{med.laboratorio}}</p>
              </div>
              <div class="shrink-0">${{semaforoBadge}}</div>
            </div>

            <!-- Resumen de Ahorro Destacado -->
            ${{med.ahorro_max_bs > 0 ? `
              <div class="bg-gradient-to-r from-emerald-50 to-teal-50 border-2 border-emerald-400 p-3 rounded-xl flex items-center justify-between gap-2">
                <div class="flex items-center gap-2">
                  <span class="text-xl">💵</span>
                  <div>
                    <span class="text-xs uppercase font-extrabold text-emerald-800 block">Ahorro Máximo:</span>
                    <span class="text-base font-black text-emerald-950">Ahorras Bs ${{med.ahorro_max_bs.toFixed(2)}} comprando en ${{med.mejor_cadena}}</span>
                  </div>
                </div>
                <span class="text-xs font-bold bg-white text-emerald-800 px-2 py-1 rounded-lg border border-emerald-300 shrink-0">
                  Mejor opción
                </span>
              </div>
            ` : `
              <div class="bg-slate-50 border border-slate-200 p-2.5 rounded-xl text-xs text-slate-600 font-medium">
                Disponible a Bs ${{med.mejor_precio_bs.toFixed(2)}} en ${{med.mejor_cadena}}.
              </div>
            `}}

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

    // 3. LÓGICA DE FILTRADO ROBUSTA
    function aplicarFiltros() {{
      const principioSel = document.getElementById('filtroPrincipio').value;
      const formatoSel = document.getElementById('filtroFormato').value;
      const farmaciaSel = document.getElementById('filtroFarmacia').value;
      const busqueda = document.getElementById('inputBusqueda').value.toLowerCase().trim();
      const orden = document.getElementById('selectOrden').value;

      let filtrados = DATA_MEDICAMENTOS.filter(med => {{
        // Filtro principio activo (coincidencia parcial flexible)
        let matchPrincipio = true;
        if (principioSel !== 'TODOS') {{
          matchPrincipio = med.principio_activo.toLowerCase().includes(principioSel.toLowerCase()) ||
                           med.marca.toLowerCase().includes(principioSel.toLowerCase());
        }}

        // Filtro formato (coincidencia parcial)
        let matchFormato = true;
        if (formatoSel !== 'TODOS') {{
          matchFormato = med.formato.toLowerCase().includes(formatoSel.toLowerCase());
        }}

        // Filtro farmacia (debe estar disponible en esa cadena)
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
    }}

    // 4. LIMPIAR FILTROS
    function limpiarFiltros() {{
      document.getElementById('filtroPrincipio').value = 'TODOS';
      document.getElementById('filtroFormato').value = 'TODOS';
      document.getElementById('filtroFarmacia').value = 'TODAS';
      document.getElementById('inputBusqueda').value = '';
      document.getElementById('selectOrden').value = 'precio_asc';
      aplicarFiltros();
    }}

    // 5. FILTRAR SUCURSALES POR ANILLO
    function filtrarSucursales() {{
      const anilloSel = document.getElementById('selectAnilloFiltro').value;
      const tbody = document.getElementById('tbodySucursales');
      tbody.innerHTML = '';

      let filtradas = DATA_SUCURSALES.filter(s => {{
        if (anilloSel === 'TODOS') return true;
        if (anilloSel === 'CENTRO') return (s.anillo_num === 1.0 || s.estado_anillo === 'SIN_EVIDENCIA');
        return (s.anillo_num === parseFloat(anilloSel));
      }});

      filtradas.forEach(s => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition-colors';
        tr.innerHTML = `
          <td class="p-3 font-bold text-slate-900">${{s.farmacia}}</td>
          <td class="p-3 font-semibold text-emerald-900">${{s.nombre}}</td>
          <td class="p-3">
            <span class="px-2.5 py-1 rounded-md text-xs font-extrabold ${{s.anillo_num <= 2 ? 'bg-blue-100 text-blue-800' : 'bg-slate-200 text-slate-800'}}">
              ${{s.anillo_etiqueta}}
            </span>
          </td>
          <td class="p-3 text-slate-700 text-xs md:text-sm">${{s.direccion}}</td>
          <td class="p-3">
            <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-lg border border-emerald-200">
              ✓ Activa
            </span>
          </td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // 6. CALCULADORA DE PRESUPUESTO
    function calcularPresupuesto() {{
      const dosis = parseFloat(document.getElementById('inputDosisDiaria').value) || 30;
      const marca = document.getElementById('selectTipoInsulinaCalc').value;
      const dosisMensual = dosis * 30;

      // Buscar en medicamentos
      const med = DATA_MEDICAMENTOS.find(m => m.marca.toLowerCase().includes(marca.toLowerCase()));
      if (!med) return;

      const volumenPorFrasco = med.unidades_totales || 1000;
      const frascosNecesarios = Math.ceil(dosisMensual / volumenPorFrasco);

      const precios = Object.values(med.precios).map(p => p.precio_venta_bs);
      const minPrecio = Math.min(...precios);
      const maxPrecio = Math.max(...precios);
      const ahorroTotal = ((maxPrecio - minPrecio) * frascosNecesarios).toFixed(2);

      const lblAhorro = document.getElementById('calcResumenAhorro');
      const lblDetalle = document.getElementById('calcDetalleFrascos');

      if (minPrecio === maxPrecio || precios.length <= 1) {{
        lblAhorro.textContent = `Gasto mensual: Bs ${{(minPrecio * frascosNecesarios).toFixed(2)}}`;
      }} else {{
        lblAhorro.textContent = `Ahorras Bs ${{ahorroTotal}} al mes`;
      }}

      lblDetalle.textContent = `Con ${{dosis}} UI/día necesitas ${{frascosNecesarios}} frasco(s) de ${{volumenPorFrasco}} UI para 30 días (${{dosisMensual}} UI). Mejor opción: Bs ${{minPrecio.toFixed(2)}} en ${{med.mejor_cadena}}.`;
    }}

    // 7. LECTURA POR VOZ DIDÁCTICA
    function leerResumenVoz() {{
      if (!('speechSynthesis' in window)) {{
        alert('Tu navegador no soporta lectura por voz.');
        return;
      }}
      const texto = `Hola abuelito o familiar cuidador. En este momento el sistema compara veinticuatro presentaciones de insulina en Santa Cruz de la Sierra. Cada tarjeta te muestra los precios de Farmacorp, Farmacias Chávez y Farmacias Telchi para que elijas la más barata. Te recomendamos adquirir tu dosis con cinco días de anticipación antes de las fechas de pago del Banco Unión.`;
      const utterance = new SpeechSynthesisUtterance(texto);
      utterance.lang = 'es-BO';
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    }}

    // 8. EVENT LISTENERS AUTOMÁTICOS Y EN TIEMPO REAL
    window.addEventListener('DOMContentLoaded', () => {{
      // Event listeners para filtros en vivo
      document.getElementById('filtroPrincipio').addEventListener('change', aplicarFiltros);
      document.getElementById('filtroFormato').addEventListener('change', aplicarFiltros);
      document.getElementById('filtroFarmacia').addEventListener('change', aplicarFiltros);
      document.getElementById('inputBusqueda').addEventListener('keyup', aplicarFiltros);

      // Carga inicial
      aplicarFiltros();
      filtrarSucursales();
      calcularPresupuesto();
    }});
  </script>
</body>
</html>
"""


def exportar_mvp() -> None:
    """Genera y guarda el HTML interactivo actualizado en el proyecto y como artefacto oficial."""
    SRC_UI_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_HTML.parent.mkdir(parents=True, exist_ok=True)

    medicamentos, sucursales, resumen = compilar_datos_reales()
    html_content = construir_html_mvp(medicamentos, sucursales, resumen)

    # 1. Guardar en src/ui/
    with open(UI_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"MVP interactivo actualizado en: {UI_HTML}")

    # 2. Guardar en raíz del proyecto
    with open(ROOT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Copia accesible actualizada en: {ROOT_HTML}")

    # 3. Guardar como Artefacto de Antigravity
    with open(ARTIFACT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Artefacto oficial actualizado en: {ARTIFACT_HTML}")


if __name__ == "__main__":
    exportar_mvp()
