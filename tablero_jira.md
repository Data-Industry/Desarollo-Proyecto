# Reestructuración del Backlog en Jira (Proyecto Insulina CRISP-DM)

**Tablero Oficial Jira Cloud:** [https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog](https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)  
**Estado:** 100% Auditado y Sincronizado bajo Formato Ágil Oficial (25 Historias de Usuario, 131 Story Points en total en 6 Sprints).

---

## Resumen de Cuadratura del Backlog (25 Historias / 131 SP)

| Épica (Fase CRISP-DM) | Clave Épica | Historias Incluidas | Cantidad | Story Points |
| :--- | :---: | :--- | :---: | :---: |
| **Fase 1: Comprensión del Negocio** | `SCRUM-29` | `SCRUM-28` (US-19: 7), `SCRUM-15` (US-11: 3), `SCRUM-45` (US-30: 3 SP) | 3 | **13 SP** |
| **Fase 2: Comprensión de los Datos** | `SCRUM-30` | `SCRUM-27` (US-20: 7), `SCRUM-23` (US-21: 7), `SCRUM-20` (US-16: 5), `SCRUM-7` (US-03: 5), `SCRUM-43` (US-28: 3) | 5 | **27 SP** |
| **Fase 3: Preparación de los Datos** | `SCRUM-31` | `SCRUM-36` (US-22: 5), `SCRUM-42` (US-27: 5), `SCRUM-37` (US-23: 5), `SCRUM-24` (US-02: 3), `SCRUM-52` (US-37: 3) | 5 | **21 SP** |
| **Fase 4: Modelado** | `SCRUM-33` | `SCRUM-9` (US-05: 8) | 1 | **8 SP** |
| **Fase 5: Evaluación** | `SCRUM-34` | `SCRUM-47` (US-32: 5), `SCRUM-48` (US-33: 8), `SCRUM-51` (US-36: 8), `SCRUM-55` (US-40: 5), `SCRUM-38` (US-41: 3) | 5 | **29 SP** |
| **Fase 6: Despliegue** | `SCRUM-35` | `SCRUM-44` (US-29: 5), `SCRUM-46` (US-31: 5), `SCRUM-49` (US-34: 5), `SCRUM-50` (US-35: 5), `SCRUM-53` (US-38: 8), `SCRUM-54` (US-39: 5) | 6 | **33 SP** |
| **TOTAL PROYECTO** | | **25 Historias de Usuario Activas** | **25** | **131 SP** |

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
- **`SCRUM-43` (US-28 - 3 SP):** Ingesta automatizada del tipo de cambio oficial del BCB (`Tipo_de_cambio.csv`). **[Finalizada]**

### SCRUM Sprint 3 (Cerrado al 100% - 21 SP)
- **`SCRUM-37` (US-23 - 5 SP):** Script de imputación zonal de valores faltantes y cruce con calendario bancario Banco Unión. **[Finalizada - Mía Wayar]**
- **`SCRUM-24` (US-02 - 3 SP):** Feature Engineering y matriz correlacional ampliada de variables predictivas. **[Finalizada - Mía Wayar]**
- **`SCRUM-9` (US-05 - 8 SP):** Entrenamiento de modelos supervisados de clasificación de disponibilidad y quiebre de stock. **[Finalizada]**
- **`SCRUM-44` (US-29 - 5 SP):** MVP Visualizador Didáctico e Interactivo Local de Precios, Stock y Farmacias por Anillo para Jubilados. **[Finalizada]**

### SCRUM Sprint 4 (Cerrado al 100% — 21/21 SP Completados)
- **`SCRUM-45` (US-30 - 3 SP):** Marco Legal, Regulatorio y Viabilidad Comercial de Scraping y Chatbot en Bolivia. **[Finalizada - Mía Wayar]**
- **`SCRUM-46` (US-31 - 5 SP):** Pulido Didáctico, Lenguaje Ciudadano y Semáforo Coherente del MVP (v3.0). **[Finalizada - Daniel Molina]**
- **`SCRUM-47` (US-32 - 5 SP):** Diseño Metodológico de Instrumentos de Validación Empírica con Usuarios (SUS y Entrevistas). **[Finalizada - Mía Wayar]**
- **`SCRUM-48` (US-33 - 8 SP):** Trabajo de Validación de Campo, Tabulación de Datos e Informe de Conclusiones de Negocio. **[Finalizada - Daniel Molina]**

### SCRUM Sprint 5 (ACTIVO / EN CURSO — 21 SP)
*Período: 15 nov – 29 nov 2026 • Meta: Pulido visual pastel, Despliegue en Producción a Costo $0 e Informe Metodológico Parte 1.*
- **`SCRUM-49` (US-34 - 5 SP):** Refinamiento Ergonómico, Estética Farmacéutica Pastel y Pulido UI/UX. **[Finalizada - Daniel Molina]**
- **`SCRUM-50` (US-35 - 5 SP):** Despliegue Continuo (CI/CD) y Hosting Web Gratuito en Producción (GitHub Pages). **[Finalizada - Daniel Molina]**
- **`SCRUM-51` (US-36 - 8 SP):** Documento Metodológico y Validación del Emprendimiento (Capítulos 1.1 al 3.4). **[Por hacer - Mía Wayar]**
- **`SCRUM-52` (US-37 - 3 SP):** Automatización del Pipeline de Datos Frescos para la Web Pública. **[Finalizada - Mía Wayar]**

### SCRUM Sprint 6 (PLANIFICADO EN BACKLOG — 21 SP)
*Meta: Chatbot Funcional, Integración a Producción, Documento Metodológico Parte 2 y Evaluación Formal de Recall.*
- **`SCRUM-53` (US-38 - 8 SP):** Desarrollo del Asistente Conversacional (Chatbot) en Lenguaje Natural. **[Planificada - Daniel Molina]**
- **`SCRUM-54` (US-39 - 5 SP):** Despliegue e Integración del Chatbot a Costo $0 (Widget Web + Canal Mensajería). **[Planificada - Daniel Molina]**
- **`SCRUM-55` (US-40 - 5 SP):** Documento Metodológico y Modelo de Negocio (Capítulos 3.5 al 5.4 - Integrado). **[Planificada - Mía Wayar]**
- **`SCRUM-38` (US-41 - 3 SP):** Evaluación Formal de Modelos Predictivos y Calibración de Recall (>= 90%). **[Planificada - Mía Wayar]**

---

## Detalle de Historias de los Sprints 5 y 6 bajo Formato Ágil Oficial

### SPRINT 5 (En Curso)

#### 1. `SCRUM-49` (`US-34` - 5 SP): Refinamiento Ergonómico, Estética Farmacéutica Pastel y Pulido UI/UX
* **Como** Adulto mayor jubilado o familiar cuidador en Santa Cruz de la Sierra,
* **Quiero** una interfaz visualmente limpia con botones explícitos de "Agrandar letra" y "Achicar letra", un glosario flotante compacto que no ocupe espacio innecesario, la calculadora de ahorro en la parte superior y una paleta farmacéutica pastel amigable y natural,
* **Para** encontrar y comparar mi insulina con total comodidad visual y rapidez sin perderme en la página ni sentir que uso una herramienta artificial.
* **Criterios de Aceptación / Validación:**
  - [ ] Reemplazo de botones A-/A+ por botones visibles de texto "Agrandar letra" y "Achicar letra".
  - [ ] Glosario ciudadano compacto tipo botón flotante/modal accesible que no ocupe espacio vertical excesivo.
  - [ ] Calculadora de dosis y ahorro mensual reubicada en la parte superior junto a los filtros principales.
  - [ ] Corrección de redundancia entre búsqueda interactiva y botón de filtrado de catálogo.
  - [ ] Rediseño visual con paleta farmacéutica pastel limpia (menta suave, salvia, tonos claros, sin sombras ni estilos artificiales de IA).

#### 2. `SCRUM-50` (`US-35` - 5 SP): Despliegue Continuo (CI/CD) y Hosting Web Gratuito en Producción
* **Como** Usuario y evaluador del proyecto,
* **Quiero** acceder al comparador interactivo mediante una URL pública segura en internet a costo cero,
* **Para** utilizar la herramienta desde cualquier celular o computadora sin depender de un entorno local de ejecución.
* **Criterios de Aceptación / Validación:**
  - [ ] Publicación del sitio web en GitHub Pages con URL pública y soporte HTTPS activo.
  - [ ] Configuración de GitHub Actions para despliegue continuo automático ante cambios en main.
  - [ ] Verificación de funcionamiento multiplataforma (móvil y escritorio) a costo $0 permanente.

#### 3. `SCRUM-51` (`US-36` - 8 SP): Documento Metodológico y Validación del Emprendimiento (Capítulos 1.1 al 3.4)
* **Como** Equipo emprendedor y postulante académico,
* **Queremos** consolidar el informe integral de la materia Programa Emprendedor cubriendo desde el punto 1.1 hasta el 3.4 con la evidencia recolectada en campo,
* **Para** formalizar la fundamentación metodológica, contextual, competitiva y empírica del modelo de solución.
* **Criterios de Aceptación / Validación:**
  - [ ] Carátula y autoría oficial con los 4 integrantes: Daniel Molina, Mía Wayar, Carlos Hugo Suárez y Kessia Cuellar.
  - [ ] Capítulo 1 (1.1-1.10) completo, con 1.3 identificando al Dueño del Problema con nombre, cargo institucional y cita textual literal de la entrevista de campo.
  - [ ] Capítulo 2 (2.1-2.4) completo, con 2.4 detallando el Benchmarking de 3 casos internacionales parecidos a la solución.
  - [ ] Capítulo 3 (3.1-3.4) completo, con 3.4 registrando la bitácora de campo con fechas, lugares y personas entrevistadas en Santa Cruz.

#### 4. `SCRUM-52` (`US-37` - 3 SP): Automatización del Pipeline de Datos Frescos para la Web Pública
* **Como** Mantenedor del sistema,
* **Quiero** un script de un solo paso que compile y refresque los datos de precios, farmacias y semáforo preventivo en el archivo de producción web,
* **Para** asegurar que la web pública siempre muestre información actualizada sin intervención manual propensa a fallos.
* **Criterios de Aceptación / Validación:**
  - [ ] Script automatizado de consolidación de datos frescos para producción web.
  - [ ] Validación de consistencia de stock, precios y cotización cambiaria BCB.
  - [ ] Tests de integridad de datos en el bundle web.

---

### SPRINT 6 (Planificado)

#### 5. `SCRUM-53` (`US-38` - 8 SP): Desarrollo del Asistente Conversacional (Chatbot) en Lenguaje Natural
* **Como** Adulto mayor con diabetes o familiar cuidador,
* **Quiero** consultar por mensaje de texto o voz simple la disponibilidad, el mejor precio y la farmacia más cercana para mi tipo de insulina,
* **Para** recibir una respuesta inmediata, comprensible y sin tener que explorar tablas ni menús complejos.
* **Criterios de Aceptación / Validación:**
  - [ ] Motor conversacional en src/chatbot/ que reconozca marcas comerciales, formatos y ubicación por anillos en Santa Cruz.
  - [ ] Respuestas empáticas con lenguaje ciudadano, sin tecnicismos y con semáforo preventivo.
  - [ ] Integración con la base analítica de stock y precios de farmacias.

#### 6. `SCRUM-54` (`US-39` - 5 SP): Despliegue e Integración del Chatbot a Costo $0 (Widget Web + Canal Mensajería)
* **Como** Jubilado que navega la página web o utiliza mensajería,
* **Quiero** interactuar directamente con el asistente a través de un botón de chat flotante y un canal directo de mensajería (WhatsApp / Telegram),
* **Para** resolver mis dudas desde cualquier dispositivo sin pagar nada.
* **Criterios de Aceptación / Validación:**
  - [ ] Widget flotante interactivo de chat incrustado en la página web pública.
  - [ ] Conector a canal de mensajería gratuito (WhatsApp Cloud API / Bot de Telegram a costo $0).
  - [ ] Backend serverless desplegado a costo $0 permanente.

#### 7. `SCRUM-55` (`US-40` - 5 SP): Documento Metodológico y Modelo de Negocio (Capítulos 3.5 al 5.4 - Integrado)
* **Como** Equipo emprendedor,
* **Queremos** completar la segunda parte del documento maestro de Programa Emprendedor desde el punto 3.5 hasta el 5.4 sobre el mismo archivo unificado,
* **Para** definir con rigor el perfil del cliente, el diseño de la solución y el modelo de negocio.
* **Criterios de Aceptación / Validación:**
  - [ ] Capítulo 3 (3.5-3.9): Procesamiento, resultados, perfil del cliente, segmentación y análisis de competidores.
  - [ ] Capítulo 4 (4.1-4.6): Proceso de ideación, criterios de selección, descripción de la solución, funcionamiento, propuesta de valor y prototipo.
  - [ ] Capítulo 5 (5.1-5.4): Business Model Canvas, plan operativo, modelo de ingresos/precios y estructura de costos.
  - [ ] Integración continua en el mismo documento maestro sin archivos separados.

#### 8. `SCRUM-38` (`US-41` - 3 SP): Evaluación Formal de Modelos Predictivos y Calibración de Recall (>= 90%)
* **Como** Científico de datos del proyecto,
* **Quiero** evaluar formalmente los modelos supervisados optimizando el Recall (>= 90%) con validación cruzada y calibración de probabilidades,
* **Para** garantizar que el sistema minimice los falsos negativos y nunca reporte stock seguro cuando existe un riesgo real de quiebre.
* **Criterios de Aceptación / Validación:**
  - [ ] Evaluación Stratified K-Fold de PR-AUC, ROC-AUC y matriz de costos con penalización a falsos negativos.
  - [ ] Calibración de probabilidades (Isotonic / Sigmoid).
  - [ ] Documentación técnica de evaluación formal en docs/.
