# Instrucciones de Reestructuración del Backlog en Jira (Proyecto Insulina CRISP-DM)

**Objetivo para el Agente (Antigravity):** Ejecutar la refactorización completa del Product Backlog en Jira Cloud (`projectId=10000`, clave `SCRUM`) para alinear el proyecto con un enfoque técnico de Ingeniería de Datos, Machine Learning y despliegue de un Chatbot conversacional, manteniendo la trazabilidad con las 6 fases de la metodología **CRISP-DM**.

**Resumen del Estado Objetivo:**
- **Total de Épicas:** 6 (Fases 1 a 6 de CRISP-DM).
- **Total de Historias de Usuario Activas:** 18 Historias.
- **Peso Total del Backlog:** 96 Story Points (SP).
- **Historias a Eliminar (absorbidas por fusión o descartadas por alcance):** 7 Historias (`SCRUM-25`, `SCRUM-17`, `SCRUM-26`, `SCRUM-21`, `SCRUM-22`, `SCRUM-11`, `SCRUM-13`).

---

## PASO 1: Verificar / Crear las 6 Épicas (Fases CRISP-DM)

Asegurar que existan exactamente estas 6 Épicas en el proyecto:
1. **Fase 1: Comprensión del Negocio**
2. **Fase 2: Comprensión de los Datos**
3. **Fase 3: Preparación de los Datos**
4. **Fase 4: Modelado**
5. **Fase 5: Evaluación**
6. **Fase 6: Despliegue**

---

## PASO 2: Eliminar Historias Redundantes o Absorbidas (7 Issues)

Eliminar del tablero las siguientes actividades cuyos contenidos han sido fusionados o reemplazados por procesos automatizados:

| Issue Key | Resumen Original | Story Points | Motivo de Baja |
| :--- | :--- | :---: | :--- |
| `SCRUM-25` | US-12: Identificación de actores y necesidades | 3 | Fusionada dentro de `SCRUM-15` (`US-11`). |
| `SCRUM-17` | US-13: Formalización de la pregunta y objetivos de investigación | 3 | Fusionada dentro de `SCRUM-15` (`US-11`). |
| `SCRUM-26` | US-15: Definición de criterios de éxito | 5 | Fusionada dentro de `SCRUM-18` (`US-14`). |
| `SCRUM-21` | US-17: Evaluación de riesgos, ética y privacidad | 5 | Fusionada dentro de `SCRUM-18` (`US-14`). |
| `SCRUM-22` | US-18: Plan de proyecto CRISP-DM | 5 | Fusionada dentro de `SCRUM-18` (`US-14`). |
| `SCRUM-11` | US-07: Comparador de precios entre farmacias de cadena e independientes | 3 | Absorbida por el scraper (`SCRUM-27` / `US-20`) y el pipeline ETL (`US-22`). |
| `SCRUM-13` | US-09: Evaluación de interrupción terapéutica por desabastecimiento | 2 | Descartada (se prioriza el desarrollo de la herramienta sobre encuestas clínicas manuales). |

---

## PASO 3: Actualizar Historias Existentes (13 Issues)

Modificar los campos (`Summary`, `Description`, `Epic Link`, `Priority`, `Story Points`) de los siguientes issues existentes:

### Épica: Fase 1: Comprensión del Negocio (Subtotal: 15 SP)

#### 1. `SCRUM-28`
- **Summary:** `US-19: Integración y automatización de repositorio GitHub con directorio local`
- **Epic:** Fase 1: Comprensión del Negocio
- **Priority:** Highest
- **Story Points:** `7`
- **Description:**
  > **Como** equipo de desarrollo y ciencia de datos, **quiero** conectar el directorio local del proyecto con un repositorio en GitHub mediante flujos automatizados de sincronización y estructura de carpetas estándar CRISP-DM, **para** garantizar el control de versiones, la reproducibilidad de los scripts y el trabajo continuo con Antigravity.
  > **Criterios de Aceptación:**
  > - Estructura de directorios creada (`data/raw`, `data/processed`, `src/scraping`, `src/etl`, `src/models`, `src/chatbot`, `docs`).
  > - Sincronización automatizada con GitHub configurada y operativa.

#### 2. `SCRUM-15` *(Fusión de US-11 + US-12 + US-13)*
- **Summary:** `US-11: Definición del problema de negocio, perfil de actores y pregunta de investigación`
- **Epic:** Fase 1: Comprensión del Negocio
- **Priority:** High
- **Story Points:** `3`
- **Description:**
  > **Como** equipo analítico, **quiero** consolidar en un único documento técnico la delimitación del problema de desabastecimiento de insulina en Santa Cruz de la Sierra, el perfil del usuario objetivo (jubilado insulinodependiente) y la pregunta de investigación para el segundo semestre de 2026, **para** alinear el desarrollo del modelo predictivo y del chatbot.
  > **Criterios de Aceptación:**
  > - Documento `docs/01_comprension_negocio.md` versionado en el repositorio con problema, causa raíz (inventarios aislados y brecha digital), actor validado y pregunta analítica.

#### 3. `SCRUM-18` *(Fusión de US-14 + US-15 + US-17 + US-18)*
- **Summary:** `US-14: Objetivos de minería de datos, criterios de éxito, ética y plan CRISP-DM`
- **Epic:** Fase 1: Comprensión del Negocio
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** científico de datos, **quiero** establecer las metas matemáticas de minería de datos (umbral de probabilidad de stock zonal $P \ge 70\%$), las métricas técnicas de éxito (priorización de Recall/Sensibilidad), los lineamientos de privacidad y el cronograma iterativo CRISP-DM/PDCA, **para** regir el entrenamiento de algoritmos y el diseño del chatbot.

---

### Épica: Fase 2: Comprensión de los Datos (Subtotal: 22 SP)

#### 4. `SCRUM-27`
- **Summary:** `US-20: Extracción automatizada (Web Scraping) de stock y precios en portales de farmacias`
- **Epic:** Fase 2: Comprensión de los Datos
- **Priority:** Highest
- **Story Points:** `7`
- **Description:**
  > **Como** ingeniero de datos, **quiero** desarrollar scripts automatizados de web scraping sobre los catálogos web activos de las cadenas de farmacias en Santa Cruz, **para** extraer periódicamente disponibilidad de insulina (Lantus, Basaglar, Glargina), precios en bolivianos (Bs.) por frasco y sucursales activas.
  > **Criterios de Aceptación:**
  > - Scripts en `src/scraping/` funcionales.
  > - Exportación estructurada en `data/raw/` con nombre comercial, precio, estado de stock, sucursal y timestamp.

#### 5. `SCRUM-20`
- **Summary:** `US-16: Auditoría automatizada de calidad de datos y análisis exploratorio (EDA)`
- **Epic:** Fase 2: Comprensión de los Datos
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** analista de datos, **quiero** ejecutar un script de perfilado y Análisis Exploratorio de Datos (EDA) sobre los registros extraídos de las farmacias web, **para** cuantificar valores nulos, dispersión de precios, cobertura geográfica y restricciones de subregistro en tiempo real.

#### 6. `SCRUM-7`
- **Summary:** `US-03: Script de geolocalización de sucursales farmacéuticas y mapeo por anillos urbanos (1 al 8)`
- **Epic:** Fase 2: Comprensión de los Datos
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** ingeniero de datos, **quiero** geocodificar las sucursales de farmacias extraídas y clasificarlas automáticamente según su ubicación dentro de los anillos urbanos (1 al 8) de Santa Cruz de la Sierra, **para** alimentar las variables espaciales de los modelos y orientar las consultas zonales del chatbot.

#### 7. `SCRUM-23` *(Transformada de US-01 a US-21)*
- **Summary:** `US-21: Extracción de datos de importación aduanera y simulación de demanda zonal`
- **Epic:** Fase 2: Comprensión de los Datos
- **Priority:** Medium
- **Story Points:** `5`
- **Description:**
  > **Como** científico de datos, **quiero** extraer registros históricos de importación aduanera de insulina en Bolivia y generar series sintéticas/simuladas de demanda y tiempos de reposición por anillo urbano, **para** complementar el dataset de scraping web y permitir el entrenamiento robusto de los modelos supervisados.

---

### Épica: Fase 3: Preparación de los Datos (Subtotal parcial: 3 SP + 10 SP nuevos = 13 SP)

#### 8. `SCRUM-24`
- **Summary:** `US-02: Ingeniería de características (Feature Engineering) y matriz correlacional de variables`
- **Epic:** Fase 3: Preparación de los Datos
- **Priority:** Medium
- **Story Points:** `3`
- **Description:**
  > **Como** científico de datos, **quiero** construir las variables predictoras temporales y espaciales (semana del mes, proximidad a días de pago de pensiones en Banco Unión, retrasos de importación, anillo urbano) y calcular su matriz de correlación, **para** seleccionar los predictores de mayor impacto en los algoritmos.

---

### Épica: Fase 4: Modelado (Subtotal: 20 SP)

#### 9. `SCRUM-8`
- **Summary:** `US-04: Algoritmo de Clustering (K-Means) de vulnerabilidad logística y matriz de probabilidad zonal`
- **Epic:** Fase 4: Modelado
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** científico de datos, **quiero** implementar un modelo no supervisado (K-Means / Clustering Jerárquico) y una matriz probabilística por anillos (1 al 8), **para** segmentar las farmacias según su perfil de abastecimiento e identificar "islas de escasez" críticas fuera del 4to anillo.

#### 10. `SCRUM-9`
- **Summary:** `US-05: Entrenamiento de modelo supervisado de clasificación de disponibilidad de stock`
- **Epic:** Fase 4: Modelado
- **Priority:** Highest
- **Story Points:** `8`
- **Description:**
  > **Como** científico de datos, **quiero** entrenar y serializar algoritmos de clasificación supervisada (Árbol de Decisión y Regresión Logística con partición 80/20), **para** estimar la probabilidad de existencia de stock zonal y clasificarla en las 3 categorías del semáforo: Verde ($P \ge 75\%$), Amarillo ($40\% \le P < 75\%$) y Rojo ($P < 40\%$).

#### 11. `SCRUM-12`
- **Summary:** `US-08: Modelo de regresión para predicción de curva de sobreprecios en bolivianos`
- **Epic:** Fase 4: Modelado
- **Priority:** Medium
- **Story Points:** `7`
- **Description:**
  > **Como** científico de datos, **quiero** entrenar un modelo de regresión supervisada continua (Regresión Lineal Regularizada / Random Forest Regressor), **para** estimar el precio del frasco de insulina en bolivianos (Bs.) y detectar semanas con incrementos mayores al 20% sobre la media.

---

### Épica: Fase 6: Despliegue (Subtotal parcial: 10 SP + 8 SP nuevos = 18 SP)

#### 12. `SCRUM-10`
- **Summary:** `US-06: Motor lógico del semáforo predictivo conectado a las salidas de los modelos`
- **Epic:** Fase 6: Despliegue
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** desarrollador backend, **quiero** programar el módulo de inferencia que traduce las probabilidades del modelo `US-05` y los datos del scraper en un estado de semáforo zonal (Verde/Amarillo/Rojo) en tiempo real, **para** exponer respuestas claras que consuman el chatbot y el calendario visual.

#### 13. `SCRUM-14` *(Restaurar / Asegurar en Backlog de Fase 6)*
- **Summary:** `US-10: Sistema automatizado de alertas preventivas de compra anticipada vía Chatbot`
- **Epic:** Fase 6: Despliegue
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** paciente jubilado o familiar cuidador, **quiero** recibir notificaciones preventivas automatizadas en el chatbot (entre 5 y 7 días antes de agotar el frasco o ante alertas de quiebre/sobreprecio zonal), **para** realizar una compra programada oportuna y evitar la interrupción del tratamiento.

---

## PASO 4: Crear Nuevas Historias de Usuario Técnicas (5 Issues Nuevos)

Crear los siguientes 5 issues tipo `Story` para completar las Fases 3 (Preparación), 5 (Evaluación) y 6 (Despliegue del Chatbot):

#### 14. Nueva Historia — `US-22` (Fase 3)
- **Issue Type:** Story
- **Summary:** `US-22: Pipeline ETL de limpieza, estandarización de precios y normalización de insulinas`
- **Epic:** Fase 3: Preparación de los Datos
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** ingeniero de datos, **quiero** construir un pipeline ETL en Python que limpie los datos crudos del web scraping, estandarice formatos de precios en Bs. y normalice las denominaciones comerciales y concentraciones de insulina (Lantus, Basaglar, Glargina), **para** generar un dataset maestro consistente en `data/processed/`.

#### 15. Nueva Historia — `US-23` (Fase 3)
- **Issue Type:** Story
- **Summary:** `US-23: Script de imputación zonal de valores faltantes y cruce con calendario bancario`
- **Epic:** Fase 3: Preparación de los Datos
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** ingeniero de datos, **quiero** implementar técnicas de imputación zonal para subsanar valores faltantes en sucursales periféricas (fuera del 4to anillo) e integrar el calendario de fechas de pago de pensiones (Banco Unión), **para** entregar la tabla analítica final lista para el entrenamiento (`ABT - Analytical Base Table`).

#### 16. Nueva Historia — `US-24` (Fase 5)
- **Issue Type:** Story
- **Summary:** `US-24: Evaluación de modelos con optimización de Recall (Sensibilidad) y validación cruzada`
- **Epic:** Fase 5: Evaluación
- **Priority:** High
- **Story Points:** `5`
- **Description:**
  > **Como** científico de datos, **quiero** evaluar rigurosamente los modelos entrenados (`US-04`, `US-05`, `US-08`) mediante validación cruzada, matrices de confusión y priorización estricta de la métrica de Recall/Sensibilidad, **para** minimizar falsos positivos de stock que provoquen traslados físicos inútiles del adulto mayor bajo calor extremo.

#### 17. Nueva Historia — `US-25` (Fase 5)
- **Issue Type:** Story
- **Summary:** `US-25: Script de generación automatizada de reportes de desempeño y Feature Importance`
- **Epic:** Fase 5: Evaluación
- **Priority:** Medium
- **Story Points:** `3`
- **Description:**
  > **Como** analista de datos, **quiero** programar un script que genere automáticamente las gráficas de importancia de variables (Feature Importance), curvas ROC/Precisión-Recall y métricas de error de regresión (RMSE/MAE), **para** documentar los hallazgos empíricos del proyecto y validar las hipótesis de negocio.

#### 18. Nueva Historia — `US-26` (Fase 6)
- **Issue Type:** Story
- **Summary:** `US-26: Desarrollo e integración del Chatbot conversacional para consulta de stock y precios`
- **Epic:** Fase 6: Despliegue
- **Priority:** Highest
- **Story Points:** `8`
- **Description:**
  > **Como** paciente jubilado o cuidador, **quiero** interactuar con un chatbot conversacional accesible (vía mensajería simple sin requerir navegación en portales web complejos), **para** preguntar en lenguaje natural en qué farmacias cercanas a mi anillo urbano hay insulina disponible hoy, a qué precio y cuál es el estado del semáforo de abastecimiento.

---

## PASO 5: Verificación de Cuadratura del Backlog (Checklist para el Agente)

Al finalizar las operaciones en Jira, verificar que el tablero refleje exactamente esta distribución:

| Épica (Fase CRISP-DM) | Historias Incluidas | Cantidad | Suma de Story Points |
| :--- | :--- | :---: | :---: |
| **Fase 1: Comprensión del Negocio** | `US-19` (7), `US-11` (3), `US-14` (5) | 3 | **15 SP** |
| **Fase 2: Comprensión de los Datos** | `US-20` (7), `US-16` (5), `US-03` (5), `US-21` (5) | 4 | **22 SP** |
| **Fase 3: Preparación de los Datos** | `US-22` (5), `US-23` (5), `US-02` (3) | 3 | **13 SP** |
| **Fase 4: Modelado** | `US-04` (5), `US-05` (8), `US-08` (7) | 3 | **20 SP** |
| **Fase 5: Evaluación** | `US-24` (5), `US-25` (3) | 2 | **8 SP** |
| **Fase 6: Despliegue** | `US-06` (5), `US-26` (8), `US-10` (5) | 3 | **18 SP** |
| **TOTAL PROYECTO** | **18 Historias de Usuario** | **18** | **96 SP** |