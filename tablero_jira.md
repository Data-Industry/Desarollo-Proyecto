# Reestructuración del Backlog en Jira (Proyecto Insulina CRISP-DM)

**Tablero Oficial Jira Cloud:** [https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog](https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)  
**Estado:** 100% Auditado y Sincronizado bajo Formato Ágil Oficial (18 Historias de Usuario, 94 Story Points en total).

---

## Resumen de Cuadratura del Backlog (18 Historias / 94 SP)

| Épica (Fase CRISP-DM) | Clave Épica | Historias Incluidas | Cantidad | Story Points |
| :--- | :---: | :--- | :---: | :---: |
| **Fase 1: Comprensión del Negocio** | `SCRUM-29` | `SCRUM-28` (US-19: 7), `SCRUM-15` (US-11: 3) *(SCRUM-18 depurada)* | 2 | **10 SP** |
| **Fase 2: Comprensión de los Datos** | `SCRUM-30` | `SCRUM-27` (US-20: 7), `SCRUM-23` (US-21: 7), `SCRUM-20` (US-16: 5), `SCRUM-7` (US-03: 5), `SCRUM-43` (US-28: 3) | 5 | **27 SP** |
| **Fase 3: Preparación de los Datos** | `SCRUM-31` | `SCRUM-36` (US-22: 5), `SCRUM-42` (US-27: 5), `SCRUM-37` (US-23: 5), `SCRUM-24` (US-02: 3) | 4 | **18 SP** |
| **Fase 4: Modelado** | `SCRUM-33` | `SCRUM-9` (US-05: 8) *(SCRUM-8 sustituida por MVP)* | 1 | **8 SP** |
| **Fase 5: Evaluación** | `SCRUM-34` | `SCRUM-38` (US-24: 5), `SCRUM-39` (US-25: 3) | 2 | **8 SP** |
| **Fase 6: Despliegue** | `SCRUM-35` | `SCRUM-44` (US-29 MVP: 5), `SCRUM-10` (US-06: 5), `SCRUM-41` (US-26: 8), `SCRUM-40` (US-10: 5) | 4 | **23 SP** |
| **TOTAL PROYECTO** | | **18 Historias de Usuario** | **18** | **94 SP** |

---

## Distribución por Sprints en Jira

### SCRUM Sprint 1 (Cerrado - 22 SP)
- **`SCRUM-28` (US-19 - 7 SP):** Integración y automatización de repositorio GitHub con directorio local. **[Finalizada]**
- **`SCRUM-15` (US-11 - 3 SP):** Definición del problema de negocio, perfil de actores y pregunta de investigación (`docs/01_comprension_negocio.md`). **[Finalizada]**
- **`SCRUM-27` (US-20 - 7 SP):** Extracción automatizada (Web Scraping) de stock y precios en portales de farmacias (Farmacorp, Chávez, Telchi). **[Finalizada]**
- **`SCRUM-36` (US-22 - 5 SP):** Pipeline ETL de limpieza, estandarización de precios y normalización de insulinas (`insulinas_master.csv`). **[Finalizada]**

### SCRUM Sprint 2 (Cerrado al 100% - 25 SP)
- **`SCRUM-23` (US-21 - 7 SP):** Ingesta y normalización de importaciones aduaneras de insulina (Partida NANDINA `3004.31.00.00`) con Tipo de Cambio Oficial del BCB. **[Finalizada]**
- **`SCRUM-20` (US-16 - 5 SP):** Auditoría automatizada de calidad de datos y análisis exploratorio (EDA) multivariable integrando la fusión de US-27 y geolocalización de US-03. **[Finalizada]**
- **`SCRUM-7` (US-03 - 5 SP):** Script de geolocalización de sucursales farmacéuticas y mapeo por anillos urbanos (1 al 8) en Santa Cruz. **[Finalizada - Mía Wayar]**
- **`SCRUM-42` (US-27 - 5 SP):** Fusión de fuentes (Scraping + Importaciones) y preparación de variables de rezago temporal de abastecimiento. **[Finalizada - Mía Wayar]**
- **`SCRUM-43` (US-28 - 3 SP):** Ingesta automatizada del tipo de cambio oficial del BCB (`https://www.bcb.gob.bo/grafico_evolutivo/`) y serie histórica diaria (`Tipo_de_cambio.csv`). **[Finalizada]**

### SCRUM Sprint 3 (Cerrado al 100% - 21 SP)
- **`SCRUM-37` (US-23 - 5 SP):** Script de imputación zonal de valores faltantes y cruce con calendario bancario Banco Unión. **[Finalizada - Mía Wayar]**
- **`SCRUM-24` (US-02 - 3 SP):** Feature Engineering y matriz correlacional ampliada de variables predictivas. **[Finalizada - Mía Wayar]**
- **`SCRUM-9` (US-05 - 8 SP):** Entrenamiento de modelos supervisados de clasificación de disponibilidad y quiebre de stock. **[Finalizada]**
- **`SCRUM-44` (US-29 - 5 SP):** MVP Visualizador Didáctico e Interactivo Local de Precios, Stock y Farmacias por Anillo para Jubilados. **[Finalizada]**

### Product Backlog Priorizado (Sprint 4: Evaluación y Despliegue - 26 SP)
- `SCRUM-38` (US-24 - 5 SP): Evaluación de modelos con optimización estricta de Recall (Sensibilidad).
- `SCRUM-39` (US-25 - 3 SP): Generación automatizada de reportes de desempeño, curvas ROC y Feature Importance.
- `SCRUM-10` (US-06 - 5 SP): Motor lógico del semáforo predictivo preventivo (`VERDE`, `AMARILLO`, `ROJO`).
- `SCRUM-41` (US-26 - 8 SP): Chatbot conversacional accesible para adultos mayores y cuidadores.
- `SCRUM-40` (US-10 - 5 SP): Sistema de alertas preventivas tempranas (5 a 7 días antes de agotar).

---

## Detalle de Historias del Sprint 3 bajo Formato Ágil Oficial

### 1. `SCRUM-37` (`US-23` - 5 SP): Cruce con Calendario Bancario e Imputación Zonal
* **Como** Científico de Datos del proyecto,
* **Quiero** construir un script que impute valores faltantes por zona y cruce las fechas de inventario con el cronograma oficial de pago de rentas del Banco Unión (días 1 al 5 y fin de mes),
* **Para** incorporar el efecto estacional de cobro de pensiones como predictor del aumento súbito en la demanda y del riesgo de desabastecimiento en farmacias cercanas.
* **Criterios de Aceptación / Validación:**
  - Script reproducible en `src/etl/06_calendario_bancario_imputacion.py`.
  - Matriz de calendario con variables binarias `dia_pago_renta` y ventana de impacto (±3 días).
  - Reglas reproducibles de imputación para precios y disponibilidad sin distorsionar la varianza original.
  - Tests unitarios con 100% de aprobación.

### 2. `SCRUM-24` (`US-02` - 3 SP): Feature Engineering y Matriz Analítica
* **Como** Científico de Datos del proyecto,
* **Quiero** transformar y sintetizar variables multivariables (ratios precio/100 UI, rezagos combinados de importaciones `Lag_1m` a `Lag_3m`, variaciones cambiarias y densidad de farmacias por anillo),
* **Para** generar la matriz analítica final normalizada que servirá de entrenamiento a los algoritmos de Machine Learning.
* **Criterios de Aceptación / Validación:**
  - Script en `src/models/02_feature_engineering.py`.
  - Generación de `data/processed/dataset_analitico_modelado.csv` con variables predictivas y target binario `quiebre_stock_inminente`.
  - Matriz de correlación de Pearson y Spearman exportada para auditoría.
  - Tests unitarios con 100% de aprobación.

### 3. `SCRUM-9` (`US-05` - 8 SP): Modelos Supervisados de Clasificación de Stock
* **Como** Científico de Datos del proyecto,
* **Quiero** entrenar y validar modelos supervisados de clasificación (Random Forest, XGBoost y Regresión Logística regularizada),
* **Para** predecir con una ventana de 5 a 15 días si una determinada insulina entrará en quiebre de stock en una zona/anillo de Santa Cruz.
* **Criterios de Aceptación / Validación:**
  - Script en `src/models/03_entrenamiento_modelos_stock.py`.
  - Validación cruzada estratificada (*Stratified K-Fold* temporal) evitando fuga de datos (*data leakage*).
  - Métrica de evaluación primaria optimizada hacia el **Recall / Sensibilidad** (minimizar falsos negativos).
  - Exportación de métricas de precisión, curvas ROC y modelos serializados en `models/`.

### 4. `SCRUM-44` (`US-29` - 5 SP): MVP Interactivo Local para Jubilados
* **Como** Adulto mayor jubilado con diabetes (o familiar cuidador) en Santa Cruz de la Sierra,
* **Quiero** acceder a una aplicación web interactiva local intuitiva, de tipografía accesible y alto contraste,
* **Para** comparar al instante los precios de mi insulina entre Farmacorp, Chávez y Telchi, verificar en qué anillo urbano hay stock disponible y consultar el semáforo preventivo antes de salir de casa.
* **Criterios de Aceptación / Validación:**
  - Interfaz web interactiva ejecutable localmente (HTML5 / Tailwind accesible / JS) alimentada directamente por los datos reales de `insulinas_master.csv` y `farmacias_geolocalizadas.csv`.
  - **Filtro Rápido:** Selección por principio activo (Glargina, NPH, Rápida, Mezcla) y presentación.
  - **Comparador Económico:** Destaca de forma visible la farmacia con el precio más bajo y el ahorro en Bs.
  - **Buscador Territorial por Anillos:** Identifica sucursales con stock físico en los anillos 1 al 8.
  - **Semáforo Preventivo:** Widget visual (`VERDE`, `AMARILLO`, `ROJO`) que indica el estado general del abastecimiento upstream.
