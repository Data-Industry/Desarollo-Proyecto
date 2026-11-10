"""
Pipeline Analítico y Estadístico de Validación Empírica con Usuarios (US-33 / SCRUM-48)
Fase 5 CRISP-DM: Evaluación

Este script carga los datos tabulados de la validación empírica en Santa Cruz de la Sierra
(14 participantes: 10 adultos mayores jubilados y 4 cuidadores familiares), ejecuta el
análisis psicométrico de la Escala de Usabilidad del Sistema (SUS - Brooke 1996, Bangor et al. 2008),
analiza la efectividad/eficiencia de las tareas guiadas (Task Testing), evalúa la comprensión
del semáforo predictivo y directorio territorial, y genera figuras estadísticas de alta resolución.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuración de estilos visuales profesionales
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

DATA_PATH = os.path.join("data", "processed", "validacion_usuarios_tabulacion.csv")
CUALI_PATH = os.path.join("data", "processed", "validacion_usuarios_cualitativo.csv")
FIGURES_DIR = os.path.join("docs", "figures")
SUMMARY_OUTPUT = os.path.join("data", "processed", "validacion_metricas_resumen.csv")


def cargar_datos():
    """Carga y valida los datasets de validación de campo."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"No se encontró el dataset cuantitativo en: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    df_cuali = None
    if os.path.exists(CUALI_PATH):
        df_cuali = pd.read_csv(CUALI_PATH)
        
    return df, df_cuali


def calcular_estadisticas_sus(df):
    """
    Calcula estadísticas descriptivas e inferenciales del puntaje SUS
    conforme a los estándares de Brooke (1996) y Lewis & Sauro (2009).
    """
    resumen = {}
    
    # 1. Muestra completa
    sus_total = df["sus_score"]
    n_total = len(sus_total)
    mean_total = sus_total.mean()
    median_total = sus_total.median()
    std_total = sus_total.std(ddof=1)
    se_total = std_total / np.sqrt(n_total)
    ci95_total = stats.t.interval(0.95, df=n_total-1, loc=mean_total, scale=se_total)
    
    resumen["total"] = {
        "n": n_total,
        "media": round(mean_total, 2),
        "mediana": round(median_total, 2),
        "desv_std": round(std_total, 2),
        "iqr": round(sus_total.quantile(0.75) - sus_total.quantile(0.25), 2),
        "min": round(sus_total.min(), 2),
        "max": round(sus_total.max(), 2),
        "ci95_inf": round(ci95_total[0], 2),
        "ci95_sup": round(ci95_total[1], 2),
        "sub_usabilidad": round(df["sus_sub_usabilidad"].mean(), 2),
        "sub_aprendizaje": round(df["sus_sub_aprendizaje"].mean(), 2)
    }
    
    # 2. Por grupo
    for grupo in ["Jubilado", "Cuidador"]:
        sub = df[df["grupo"] == grupo]["sus_score"]
        n_g = len(sub)
        mean_g = sub.mean()
        median_g = sub.median()
        std_g = sub.std(ddof=1)
        se_g = std_g / np.sqrt(n_g)
        ci95_g = stats.t.interval(0.95, df=n_g-1, loc=mean_g, scale=se_g)
        
        resumen[grupo.lower()] = {
            "n": n_g,
            "media": round(mean_g, 2),
            "mediana": round(median_g, 2),
            "desv_std": round(std_g, 2),
            "iqr": round(sub.quantile(0.75) - sub.quantile(0.25), 2),
            "min": round(sub.min(), 2),
            "max": round(sub.max(), 2),
            "ci95_inf": round(ci95_g[0], 2),
            "ci95_sup": round(ci95_g[1], 2),
            "sub_usabilidad": round(df[df["grupo"] == grupo]["sus_sub_usabilidad"].mean(), 2),
            "sub_aprendizaje": round(df[df["grupo"] == grupo]["sus_sub_aprendizaje"].mean(), 2)
        }
        
    return resumen


def calcular_metricas_tareas(df):
    """
    Calcula tasas de éxito, finalización independiente, tiempos y errores por tarea.
    """
    tareas = ["t1", "t2", "t3a", "t3b"]
    nombres_tareas = {
        "t1": "T1: Búsqueda Insulina",
        "t2": "T2: Menor Precio y Ahorro",
        "t3a": "T3A: Semáforo Predictivo",
        "t3b": "T3B: Directorio por Anillo"
    }
    
    metricas = {}
    for t in tareas:
        evaluables = df[df[f"{t}_evaluable"] == 1]
        n_eval = len(evaluables)
        
        exitos = evaluables[evaluables[f"{t}_resultado"].isin(["Completo_Solo", "Completo_Ayuda"])]
        n_exito = len(exitos)
        tasa_exito = (n_exito / n_eval) * 100.0 if n_eval > 0 else 0.0
        
        independientes = evaluables[evaluables[f"{t}_resultado"] == "Completo_Solo"]
        n_indep = len(independientes)
        tasa_indep = (n_indep / n_eval) * 100.0 if n_eval > 0 else 0.0
        
        tiempos = evaluables[f"{t}_tiempo_segundos"]
        errores = evaluables[f"{t}_errores"]
        
        metricas[t] = {
            "nombre": nombres_tareas[t],
            "n_evaluable": n_eval,
            "tasa_exito_pct": round(tasa_exito, 1),
            "tasa_indep_pct": round(tasa_indep, 1),
            "tiempo_mediana_s": round(tiempos.median(), 1),
            "tiempo_media_s": round(tiempos.mean(), 1),
            "tiempo_std_s": round(tiempos.std(), 1),
            "tiempo_min_s": int(tiempos.min()),
            "tiempo_max_s": int(tiempos.max()),
            "errores_total": int(errores.sum()),
            "errores_promedio": round(errores.mean(), 2)
        }
        
    return metricas


def calcular_metricas_negocio(df):
    """
    Calcula métricas clave de contexto de compra, desabastecimiento e intención de uso.
    """
    total = len(df)
    desabastecidos = int(df["episodio_desabastecimiento_previo"].sum())
    pct_desabastecimiento = round((desabastecidos / total) * 100.0, 1)
    
    farmacias_media = round(df["farmacias_visitadas_promedio"].mean(), 2)
    transporte_media = round(df["gasto_transporte_bs"].mean(), 1)
    tiempo_horas_media = round(df["tiempo_busqueda_horas"].mean(), 2)
    
    # Intención de uso positiva (4 o 5)
    intencion_alta = len(df[df["intencion_uso"] >= 4])
    pct_intencion_alta = round((intencion_alta / total) * 100.0, 1)
    
    # Canal preferido
    canal_counts = df["canal_preferido"].value_counts().to_dict()
    
    # Comprensión del semáforo (2=Completa, 1=Parcial, 0=Incorrecta)
    semaforo_completa = len(df[df["t3a_comprension"] == 2])
    semaforo_parcial = len(df[df["t3a_comprension"] == 1])
    semaforo_error = len(df[df["t3a_comprension"] == 0])
    
    # Comprensión directorio territorial
    anillo_completa = len(df[df["t3b_comprension_directorio"] == 2])
    anillo_parcial = len(df[df["t3b_comprension_directorio"] == 1])
    anillo_error = len(df[df["t3b_comprension_directorio"] == 0])
    
    return {
        "pct_desabastecimiento_previo": pct_desabastecimiento,
        "farmacias_visitadas_media": farmacias_media,
        "gasto_transporte_media_bs": transporte_media,
        "tiempo_busqueda_horas_media": tiempo_horas_media,
        "pct_intencion_uso_positiva": pct_intencion_alta,
        "canales_preferidos": canal_counts,
        "semaforo_comprension": {
            "completa_pct": round((semaforo_completa / total) * 100.0, 1),
            "parcial_pct": round((semaforo_parcial / total) * 100.0, 1),
            "error_pct": round((semaforo_error / total) * 100.0, 1)
        },
        "anillos_comprension": {
            "directorio_puro_pct": round((anillo_completa / total) * 100.0, 1),
            "duda_stock_pct": round((anillo_parcial / total) * 100.0, 1),
            "creyo_stock_confirmado_pct": round((anillo_error / total) * 100.0, 1)
        }
    }


def generar_figuras_validacion(df, sus_res, tareas_res, negocio_res):
    """
    Genera y guarda las 4 figuras estadísticas de alta resolución en docs/figures/.
    """
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # FIGURA 1: Distribución SUS y Benchmarking (Bangor et al. 2008/2009)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    grupos_orden = ["Jubilado", "Cuidador"]
    palette = {"Jubilado": "#1565C0", "Cuidador": "#2E7D32"}
    
    sns.boxplot(x="grupo", y="sus_score", hue="grupo", data=df, order=grupos_orden, palette=palette, 
                width=0.45, ax=ax, boxprops=dict(alpha=0.7), showmeans=True, legend=False,
                meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black", "markersize": 8})
    sns.stripplot(x="grupo", y="sus_score", data=df, order=grupos_orden, color="#212121", 
                  size=8, jitter=0.15, alpha=0.8, ax=ax)
    
    # Líneas de referencia estándar SUS
    ax.axhline(68.0, color="#E65100", linestyle="--", linewidth=1.5, label="Promedio Internacional SUS (68.0 = 'OK')")
    ax.axhline(70.0, color="#1B5E20", linestyle=":", linewidth=1.5, label="Umbral 'Good' / Grado B (70.0)")
    ax.axhline(85.0, color="#4A148C", linestyle="-.", linewidth=1.5, label="Umbral 'Excellent' / Grado A (85.0)")
    
    # Anotaciones de medias
    media_jub = sus_res["jubilado"]["media"]
    media_cuid = sus_res["cuidador"]["media"]
    ax.text(0, media_jub + 2, f"Media: {media_jub:.1f}\n(Mediana: {sus_res['jubilado']['mediana']:.1f})", 
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#0D47A1",
            bbox=dict(boxstyle="round,pad=0.3", fc="#E3F2FD", ec="#1565C0", alpha=0.9))
    ax.text(1, media_cuid + 2, f"Media: {media_cuid:.1f}\n(Mediana: {sus_res['cuidador']['mediana']:.1f})", 
            ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1B5E20",
            bbox=dict(boxstyle="round,pad=0.3", fc="#E8F5E9", ec="#2E7D32", alpha=0.9))
    
    ax.set_title("Validación Empírica SUS v3.0 por Grupo de Usuario (N=14 en Santa Cruz)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Puntuación SUS (0 - 100)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Segmento de Usuario", fontsize=11, fontweight="bold")
    ax.set_ylim(45, 100)
    ax.legend(loc="lower right", frameon=True, fontsize=9)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "validacion_fig1_distribucion_sus_benchmarking.png")
    fig.savefig(fig1_path, dpi=300)
    plt.close(fig)
    print(f"Figura 1 generada en: {fig1_path}")
    
    # FIGURA 2: Rendimiento de Tareas (Tasa de Éxito, Independencia y Tiempos)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    
    keys_t = ["t1", "t2", "t3a", "t3b"]
    labels_t = ["T1: Búsqueda\nInsulina", "T2: Comparar\nPrecio y Ahorro", "T3A: Semáforo\nPreventivo", "T3B: Directorio\npor Anillo"]
    exito_vals = [tareas_res[k]["tasa_exito_pct"] for k in keys_t]
    indep_vals = [tareas_res[k]["tasa_indep_pct"] for k in keys_t]
    tiempos_med = [tareas_res[k]["tiempo_mediana_s"] for k in keys_t]
    
    x = np.arange(len(keys_t))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, exito_vals, width, label="Tasa de Éxito Total (%)", color="#1976D2")
    rects2 = ax1.bar(x + width/2, indep_vals, width, label="Finalización Independiente (%)", color="#43A047")
    
    ax1.set_ylabel("Porcentaje de Participantes (%)", fontsize=10, fontweight="bold")
    ax1.set_title("Eficacia: Éxito vs Finalización Independiente", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels_t, fontsize=9)
    ax1.set_ylim(0, 115)
    ax1.legend(loc="lower right", fontsize=9)
    
    for r in rects1:
        h = r.get_height()
        ax1.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
    for r in rects2:
        h = r.get_height()
        ax1.annotate(f"{h:.1f}%", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
        
    # Eficiencia: Tiempos medianos
    colors_time = ["#3949AB", "#5E35B1", "#00897B", "#D81B60"]
    bars_t = ax2.bar(labels_t, tiempos_med, color=colors_time, width=0.5, alpha=0.85)
    ax2.set_ylabel("Tiempo Mediano de Ejecución (segundos)", fontsize=10, fontweight="bold")
    ax2.set_title("Eficiencia: Tiempo Mediano por Tarea", fontsize=11, fontweight="bold")
    ax2.set_ylim(0, max(tiempos_med) * 1.3)
    
    for b in bars_t:
        h = b.get_height()
        ax2.annotate(f"{h:.0f}s", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
                     
    plt.suptitle("Evaluación de Eficacia y Eficiencia en Pruebas de Tareas (Task Testing)", fontsize=13, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "validacion_fig2_rendimiento_tareas_tiempos.png")
    fig.savefig(fig2_path, dpi=300)
    plt.close(fig)
    print(f"Figura 2 generada en: {fig2_path}")
    
    # FIGURA 3: Comprensión del Semáforo Preventivo y Directorio Espacial
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8))
    
    # Semáforo
    labels_sem = ["Comprensión Plena\n(Riesgo Coherente)", "Comprensión Parcial\n(Duda Stock)", "Error Conceptual\n(Diagnóstico/Certeza)"]
    vals_sem = [negocio_res["semaforo_comprension"]["completa_pct"], 
                negocio_res["semaforo_comprension"]["parcial_pct"], 
                negocio_res["semaforo_comprension"]["error_pct"]]
    colors_sem = ["#2E7D32", "#F9A825", "#C62828"]
    
    wedges1, texts1, autotexts1 = ax1.pie(vals_sem, labels=labels_sem, autopct="%1.1f%%", 
                                          startangle=140, colors=colors_sem, 
                                          textprops=dict(fontsize=9, fontweight="bold"))
    ax1.set_title("Comprensión del Semáforo Preventivo v3.0\n(12 Verdes / 11 Amarillos / 1 Rojo)", fontsize=11, fontweight="bold")
    
    # Directorio Territorial
    labels_dir = ["Directorio Sucursales\n(Comprensión Exacta)", "Duda sobre Stock\nLocal", "Asumió Stock Físico\nConfirmado"]
    vals_dir = [negocio_res["anillos_comprension"]["directorio_puro_pct"], 
                negocio_res["anillos_comprension"]["duda_stock_pct"], 
                negocio_res["anillos_comprension"]["creyo_stock_confirmado_pct"]]
    colors_dir = ["#1565C0", "#FB8C00", "#D32F2F"]
    
    wedges2, texts2, autotexts2 = ax2.pie(vals_dir, labels=labels_dir, autopct="%1.1f%%", 
                                          startangle=140, colors=colors_dir, 
                                          textprops=dict(fontsize=9, fontweight="bold"))
    ax2.set_title("Comprensión del Filtro Territorial\n(Directorio de Farmacias por Anillo)", fontsize=11, fontweight="bold")
    
    plt.suptitle("Validación Cognitiva de la Interfaz: Semáforo de Riesgo y Cobertura Territorial", fontsize=12, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "validacion_fig3_comprension_semaforo_anillos.png")
    fig.savefig(fig3_path, dpi=300)
    plt.close(fig)
    print(f"Figura 3 generada en: {fig3_path}")
    
    # FIGURA 4: Matriz de Fricción vs Prioridad y Preferencia de Canal
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))
    
    # Canal preferido
    canales = list(negocio_res["canales_preferidos"].keys())
    conteo_canales = list(negocio_res["canales_preferidos"].values())
    pct_canales = [(c / len(df)) * 100.0 for c in conteo_canales]
    
    bars_c = ax1.bar(canales, pct_canales, color=["#25D366", "#0288D1"], width=0.45)
    ax1.set_ylabel("Preferencia declarada (%)", fontsize=10, fontweight="bold")
    ax1.set_title("Canal Preferido para Consultas de Stock", fontsize=11, fontweight="bold")
    ax1.set_ylim(0, 115)
    for b in bars_c:
        h = b.get_height()
        ax1.annotate(f"{h:.1f}%", xy=(b.get_x() + b.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")
        
    # Puntos de fricción
    fricciones = [
        ("Falsa expectativa stock sucursal", 28.6, 9.0, "P04, P06"),
        ("Toque táctil en móviles pequeños", 21.4, 6.5, "P06"),
        ("Demanda fecha actualización", 21.4, 5.0, "C02"),
        ("Alerta preventiva renta Banco Unión", 85.7, 8.5, "C03, P02")
    ]
    
    for label, freq, impact, parts in fricciones:
        c_point = "#D32F2F" if impact >= 8.0 else "#F57C00"
        ax2.scatter(freq, impact, s=250, color=c_point, alpha=0.85, edgecolors="black")
        ax2.annotate(f"{label}\n({parts})", xy=(freq, impact), xytext=(5, 5), textcoords="offset points",
                     fontsize=8, fontweight="bold")
                     
    ax2.set_xlabel("Frecuencia en la Muestra (%)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Impacto Operativo / Riesgo de Decisión (1-10)", fontsize=10, fontweight="bold")
    ax2.set_title("Matriz de Fricciones Identificadas y Prioridades", fontsize=11, fontweight="bold")
    ax2.set_xlim(10, 95)
    ax2.set_ylim(4, 10.5)
    ax2.axvline(25, color="gray", linestyle=":", alpha=0.6)
    ax2.axhline(7.5, color="gray", linestyle=":", alpha=0.6)
    ax2.text(80, 10, "PRIORIDAD 1\n(Chatbot + Alertas)", fontsize=8, color="#B71C1C", fontweight="bold", ha="center")
    
    plt.suptitle("Implicaciones de Negocio para el Roadmap Final: Canal WhatsApp y Fricciones Críticas", fontsize=12, fontweight="bold", y=0.98)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "validacion_fig4_matriz_friccion_adopcion_canal.png")
    fig.savefig(fig4_path, dpi=300)
    plt.close(fig)
    print(f"Figura 4 generada en: {fig4_path}")


def exportar_resumen_tabulado(sus_res, tareas_res, negocio_res):
    """
    Exporta un archivo CSV con el resumen de métricas clave para trazabilidad de negocio.
    """
    rows = [
        {"categoria": "SUS_Global", "metrica": "Media_Total", "valor": sus_res["total"]["media"], "unidad": "puntos_0_100"},
        {"categoria": "SUS_Global", "metrica": "Mediana_Total", "valor": sus_res["total"]["mediana"], "unidad": "puntos_0_100"},
        {"categoria": "SUS_Global", "metrica": "Desv_Std_Total", "valor": sus_res["total"]["desv_std"], "unidad": "puntos"},
        {"categoria": "SUS_Jubilados", "metrica": "Media_Jubilados", "valor": sus_res["jubilado"]["media"], "unidad": "puntos_0_100"},
        {"categoria": "SUS_Jubilados", "metrica": "Mediana_Jubilados", "valor": sus_res["jubilado"]["mediana"], "unidad": "puntos_0_100"},
        {"categoria": "SUS_Cuidadores", "metrica": "Media_Cuidadores", "valor": sus_res["cuidador"]["media"], "unidad": "puntos_0_100"},
        {"categoria": "SUS_Subescala", "metrica": "Usabilidad_Promedio", "valor": sus_res["total"]["sub_usabilidad"], "unidad": "base_100"},
        {"categoria": "SUS_Subescala", "metrica": "Aprendizaje_Promedio", "valor": sus_res["total"]["sub_aprendizaje"], "unidad": "base_100"},
        {"categoria": "Tareas_Eficacia", "metrica": "T1_Exito_Pct", "valor": tareas_res["t1"]["tasa_exito_pct"], "unidad": "porcentaje"},
        {"categoria": "Tareas_Eficacia", "metrica": "T2_Exito_Pct", "valor": tareas_res["t2"]["tasa_exito_pct"], "unidad": "porcentaje"},
        {"categoria": "Tareas_Eficacia", "metrica": "T3A_Exito_Pct", "valor": tareas_res["t3a"]["tasa_exito_pct"], "unidad": "porcentaje"},
        {"categoria": "Tareas_Eficacia", "metrica": "T3B_Exito_Pct", "valor": tareas_res["t3b"]["tasa_exito_pct"], "unidad": "porcentaje"},
        {"categoria": "Tareas_Eficiencia", "metrica": "T1_Tiempo_Mediana", "valor": tareas_res["t1"]["tiempo_mediana_s"], "unidad": "segundos"},
        {"categoria": "Tareas_Eficiencia", "metrica": "T2_Tiempo_Mediana", "valor": tareas_res["t2"]["tiempo_mediana_s"], "unidad": "segundos"},
        {"categoria": "Tareas_Eficiencia", "metrica": "T3A_Tiempo_Mediana", "valor": tareas_res["t3a"]["tiempo_mediana_s"], "unidad": "segundos"},
        {"categoria": "Tareas_Eficiencia", "metrica": "T3B_Tiempo_Mediana", "valor": tareas_res["t3b"]["tiempo_mediana_s"], "unidad": "segundos"},
        {"categoria": "Negocio_Contexto", "metrica": "Desabastecimiento_Previo_Pct", "valor": negocio_res["pct_desabastecimiento_previo"], "unidad": "porcentaje"},
        {"categoria": "Negocio_Contexto", "metrica": "Farmacias_Visitadas_Media", "valor": negocio_res["farmacias_visitadas_media"], "unidad": "farmacias"},
        {"categoria": "Negocio_Contexto", "metrica": "Gasto_Transporte_Media_Bs", "valor": negocio_res["gasto_transporte_media_bs"], "unidad": "bob"},
        {"categoria": "Negocio_Adopcion", "metrica": "Intencion_Uso_Alta_Pct", "valor": negocio_res["pct_intencion_uso_positiva"], "unidad": "porcentaje"},
        {"categoria": "Negocio_Canal", "metrica": "Preferencia_WhatsApp_Pct", "valor": round((negocio_res["canales_preferidos"].get("WhatsApp Chatbot", 0) / 14) * 100.0, 1), "unidad": "porcentaje"}
    ]
    df_res = pd.DataFrame(rows)
    df_res.to_csv(SUMMARY_OUTPUT, index=False)
    print(f"Resumen de métricas exportado exitosamente en: {SUMMARY_OUTPUT}")


def main():
    print("=== INICIANDO ANÁLISIS DE VALIDACIÓN EMPÍRICA CON USUARIOS (US-33 / SCRUM-48) ===")
    df, df_cuali = cargar_datos()
    print(f"Dataset cuantitativo cargado: {len(df)} participantes ({len(df[df['grupo']=='Jubilado'])} Jubilados, {len(df[df['grupo']=='Cuidador'])} Cuidadores).")
    
    sus_res = calcular_estadisticas_sus(df)
    tareas_res = calcular_metricas_tareas(df)
    negocio_res = calcular_metricas_negocio(df)
    
    print("\n--- RESUMEN SUS (Brooke 1996 / Bangor 2008) ---")
    print(f"Muestra Global (N=14): Media = {sus_res['total']['media']} | Mediana = {sus_res['total']['mediana']} | Desv.Std = {sus_res['total']['desv_std']}")
    print(f"Jubilados (N=10): Media = {sus_res['jubilado']['media']} | Mediana = {sus_res['jubilado']['mediana']} | Usabilidad = {sus_res['jubilado']['sub_usabilidad']}% | Aprendizaje = {sus_res['jubilado']['sub_aprendizaje']}%")
    print(f"Cuidadores (N=4): Media = {sus_res['cuidador']['media']} | Mediana = {sus_res['cuidador']['mediana']} | Usabilidad = {sus_res['cuidador']['sub_usabilidad']}% | Aprendizaje = {sus_res['cuidador']['sub_aprendizaje']}%")
    
    print("\n--- RENDIMIENTO DE TAREAS GUIADAS (TASK TESTING) ---")
    for t_id, data in tareas_res.items():
        print(f"{data['nombre']}: Éxito = {data['tasa_exito_pct']}% | Independiente = {data['tasa_indep_pct']}% | Tiempo Mediano = {data['tiempo_mediana_s']}s | Errores = {data['errores_total']}")
        
    print("\n--- VALIDACIÓN DE NEGOCIO Y CONTEXTO EMPÍRICO ---")
    print(f"Participantes con historial de desabastecimiento: {negocio_res['pct_desabastecimiento_previo']}%")
    print(f"Promedio de farmacias recorridas en búsqueda: {negocio_res['farmacias_visitadas_media']} farmacias")
    print(f"Gasto promedio en transporte por búsqueda: Bs {negocio_res['gasto_transporte_media_bs']}")
    print(f"Intención de uso positiva (Probablemente / Definitivamente): {negocio_res['pct_intencion_uso_positiva']}%")
    print(f"Canales preferidos: {negocio_res['canales_preferidos']}")
    
    print("\n--- GENERANDO FIGURAS ESTADÍSTICAS Y TABLAS DE RESUMEN ---")
    generar_figuras_validacion(df, sus_res, tareas_res, negocio_res)
    exportar_resumen_tabulado(sus_res, tareas_res, negocio_res)
    print("=== PROCESAMIENTO ANALÍTICO COMPLETADO EXITOSAMENTE ===")


if __name__ == "__main__":
    main()
