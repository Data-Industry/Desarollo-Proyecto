# Reestructuración del Backlog en Jira (Proyecto Insulina CRISP-DM)

**Objetivo:** Mantener el Product Backlog en Jira Cloud (`SCRUM`, 18 Historias de Usuario, 96 Story Points en total) alineado con las 6 fases de la metodología **CRISP-DM** y la estrategia analítica de doble flujo (Web Scraping de Farmacias Retail + Ingesta Aduanera de Importaciones).

---

## Resumen de Cuadratura del Backlog (18 Historias / 96 SP)

| Épica (Fase CRISP-DM) | Historias Incluidas | Cantidad | Suma de Story Points |
| :--- | :--- | :---: | :---: |
| **Fase 1: Comprensión del Negocio** | `US-19` (7), `US-11` (3), `US-14` (5) | 3 | **15 SP** |
| **Fase 2: Comprensión de los Datos** | `US-20` (7), `US-21` (7), `US-16` (5), `US-03` (5) | 4 | **24 SP** |
| **Fase 3: Preparación de los Datos** | `US-22` (5), `US-27` (5), `US-23` (5), `US-02` (3) | 4 | **18 SP** |
| **Fase 4: Modelado** | `US-04` (5), `US-05` (8) | 2 | **13 SP** |
| **Fase 5: Evaluación** | `US-24` (5), `US-25` (3) | 2 | **8 SP** |
| **Fase 6: Despliegue** | `US-06` (5), `US-26` (8), `US-10` (5) | 3 | **18 SP** |
| **TOTAL PROYECTO** | **18 Historias de Usuario** | **18** | **96 SP** |

---

## Distribución por Sprints

- **Sprint 1 (Cerrado - 22 SP):**
  - `US-19` (7 SP): Integración y estructuración CRISP-DM en GitHub.
  - `US-11` (3 SP): Comprensión del negocio, causas raíz y actor validado.
  - `US-20` (7 SP): Scraping automatizado de farmacias locales (Farmacorp, Chávez, Telchi).
  - `US-22` (5 SP): Pipeline ETL de limpieza, normalización y dataset maestro `insulinas_master.csv`.

- **Sprint 2 (Activo - 22 SP):**
  - `US-21` (7 SP): Ingesta, limpieza y normalización de importaciones públicas de insulina (Partida NANDINA `3004.31.00.00`).
  - `US-16` (5 SP): Auditoría de calidad de datos y análisis exploratorio (EDA) multivariable.
  - `US-03` (5 SP): Script de georreferenciación de sucursales y clasificación por anillos urbanos (1 al 8).
  - `US-27` (5 SP): Fusión de fuentes (Scraping + Importaciones) y modelado de desfase temporal (Lag) de abastecimiento.

- **Sprints Posteriores (52 SP):** Modelado predictivo, evaluación de Recall, chatbot conversacional y despliegue final.

---

## Detalle Técnico de Historias de Usuario

### Fase 1: Comprensión del Negocio (15 SP)
- **`US-19` (7 SP) [Sprint 1]:** Conexión de directorio local con GitHub y arquitectura de carpetas CRISP-DM.
- **`US-11` (3 SP) [Sprint 1]:** Formalización en `docs/01_comprension_negocio.md` del problema, actores y preguntas analíticas.
- **`US-14` (5 SP):** Definición formal de metas de minería, priorización de métrica de Recall, ética y plan de contingencia.

### Fase 2: Comprensión de los Datos (24 SP)
- **`US-20` (7 SP) [Sprint 1]:** Web scraping automatizado multicanal de portales farmacéuticos en Santa Cruz.
- **`US-21` (7 SP) [Sprint 2]:** Ingesta, filtrado y normalización de importaciones aduaneras de insulina (INE / Aduana Nacional, subpartida `3004.31.00.00`).
- **`US-16` (5 SP) [Sprint 2]:** Perfilado, evaluación de completitud, dispersión de precios y EDA de datasets.
- **`US-03` (5 SP) [Sprint 2]:** Geocodificación y mapeo territorial de sucursales en los 8 anillos de Santa Cruz de la Sierra.

### Fase 3: Preparación de los Datos (18 SP)
- **`US-22` (5 SP) [Sprint 1]:** Pipeline ETL en Python, descarte de descartables y generación de `insulinas_master.csv` con 25 campos.
- **`US-27` (5 SP) [Sprint 2]:** Fusión de series temporales de importación con inventarios retail de farmacias y cálculo de lags logísticos de reposición.
- **`US-23` (5 SP):** Imputación zonal de faltantes en anillos periféricos y cruce con calendario de pago de pensiones (Banco Unión).
- **`US-02` (3 SP):** Feature Engineering y cálculo de matriz de correlación temporal y espacial.

### Fase 4: Modelado (13 SP)
- **`US-04` (5 SP):** Análisis espacial de densidad, proximidad y cobertura de farmacias con stock en los anillos 1 al 8.
- **`US-05` (8 SP):** Entrenamiento y serialización de modelos supervisados (Árboles de Decisión, Regresión Logística) para clasificar probabilidad de existencia de stock ($P \ge 70\%$).

### Fase 5: Evaluación (8 SP)
- **`US-24` (5 SP):** Evaluación rigurosa con optimización estricta de Recall (Sensibilidad) para erradicar falsos positivos de stock para adultos mayores.
- **`US-25` (3 SP):** Generación automatizada de reportes de desempeño, curvas ROC y análisis de importancia de variables (SHAP / Feature Importance).

### Fase 6: Despliegue (18 SP)
- **`US-06` (5 SP):** Motor lógico del semáforo predictivo preventivo (`VERDE`, `AMARILLO`, `ROJO`) en tiempo real.
- **`US-26` (8 SP):** Chatbot conversacional accesible en lenguaje natural para consultas de stock, precios y farmacias cercanas.
- **`US-10` (5 SP):** Sistema automatizado de alertas preventivas en el chatbot (5 a 7 días antes de agotar el frasco de insulina).
