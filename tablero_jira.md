# Reestructuración del Backlog en Jira (Proyecto Insulina CRISP-DM)

**Tablero Oficial Jira Cloud:** [https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog](https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)  
**Estado:** 100% Auditado y Sincronizado bajo Formato Ágil Oficial (18 Historias de Usuario, 94 Story Points en total).

---

## Resumen de Cuadratura del Backlog (18 Historias / 94 SP)

| Épica (Fase CRISP-DM) | Clave Épica | Historias Incluidas | Cantidad | Story Points |
| :--- | :---: | :--- | :---: | :---: |
| **Fase 1: Comprensión del Negocio** | `SCRUM-29` | `SCRUM-28` (US-19: 7), `SCRUM-15` (US-11: 3), `SCRUM-45` (US-30: 3 SP) *(SCRUM-18 depurada)* | 3 | **13 SP** |
| **Fase 2: Comprensión de los Datos** | `SCRUM-30` | `SCRUM-27` (US-20: 7), `SCRUM-23` (US-21: 7), `SCRUM-20` (US-16: 5), `SCRUM-7` (US-03: 5), `SCRUM-43` (US-28: 3) | 5 | **27 SP** |
| **Fase 3: Preparación de los Datos** | `SCRUM-31` | `SCRUM-36` (US-22: 5), `SCRUM-42` (US-27: 5), `SCRUM-37` (US-23: 5), `SCRUM-24` (US-02: 3) | 4 | **18 SP** |
| **Fase 4: Modelado** | `SCRUM-33` | `SCRUM-9` (US-05: 8) *(SCRUM-8 sustituida por MVP)* | 1 | **8 SP** |
| **Fase 5: Evaluación** | `SCRUM-34` | `SCRUM-47` (US-32: 5 SP), `SCRUM-48` (US-33: 8 SP), `SCRUM-38` (US-24: 5 SP en Backlog) *(SCRUM-39 depurada)* | 3 | **18 SP** |
| **Fase 6: Despliegue** | `SCRUM-35` | `SCRUM-44` (US-29 MVP: 5), `SCRUM-46` (US-31: 5 SP) *(SCRUM-41, SCRUM-40 y SCRUM-10 depuradas)* | 2 | **10 SP** |
| **TOTAL PROYECTO** | | **18 Historias de Usuario Activas** | **18** | **94 SP** |

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

### SCRUM Sprint 4 (En Ejecución — 13/21 SP Completados)
- **`SCRUM-45` (US-30 - 3 SP):** Marco Legal, Regulatorio y Viabilidad Comercial de Scraping y Chatbot en Bolivia. **[Finalizada - Mía Wayar]**
- **`SCRUM-46` (US-31 - 5 SP):** Pulido Didáctico, Lenguaje Ciudadano y Semáforo Coherente del MVP (v3.0). **[Finalizada - Daniel Molina]**
- **`SCRUM-47` (US-32 - 5 SP):** Diseño Metodológico de Instrumentos de Validación Empírica con Usuarios (SUS y Entrevistas). **[Finalizada - Mía Wayar]**
- **`SCRUM-48` (US-33 - 8 SP):** Trabajo de Validación de Campo, Tabulación de Datos e Informe de Conclusiones de Negocio. **[En Curso - Daniel Molina]**

### Product Backlog Priorizado (Sprint 5: Evaluación Formal y Cierre - 5 SP)
- **`SCRUM-38` (US-24 - 5 SP):** Evaluación formal de modelos supervisados con optimización estricta de Recall (Sensibilidad) y calibración probabilística. **[Backlog]**

---

## Detalle de Historias del Sprint 4 bajo Formato Ágil Oficial

### 1. `SCRUM-45` (`US-30` - 3 SP): Marco Legal, Regulatorio y Viabilidad Comercial de Scraping y Chatbot en Bolivia
* **Como** Equipo de Ciencia de Datos y Emprendimiento Tecnológico,
* **Quiero** realizar un análisis exhaustivo del marco legal boliviano e internacional sobre web scraping de precios públicos (Ley N° 453 de Protección al Consumidor, Ley N° 164 de Telecomunicaciones, Decisión 486 de la CAN sobre marcas) y las consideraciones regulatorias, de privacidad (Habeas Data) y responsabilidad médica para un eventual lanzamiento público y comercial del chatbot,
* **Para** garantizar la viabilidad jurídica del proyecto, mitigar riesgos legales de propiedad intelectual y fijar la hoja de ruta de cumplimiento normativo previo al despliegue comercial.
* **Criterios de Aceptación / Validación:**
  - [ ] Documento técnico-legal estructurado en `docs/07_marco_legal_y_viabilidad_comercial.md`.
  - [ ] Análisis de legitimidad del web scraping de datos públicos de farmacias bajo la Ley N° 453 (acceso a información y transparencia de precios) y Ley N° 164 (delitos informáticos y ética de scraping sin vulneración de accesos).
  - [ ] Evaluación del uso nominativo de marcas comerciales de insulinas bajo la Decisión 486 de la Comisión de la Comunidad Andina (uso de marcas de terceros con fines meramente informativos y comparativos).
  - [ ] Matriz de consideraciones legales y regulatorias para un eventual lanzamiento público y comercial del chatbot:
    - Términos de Servicio y políticas de Meta para WhatsApp Business API en el sector salud/farmacia.
    - Protección de datos personales de salud (Habeas Data, Art. 21 y 130 de la Constitución Política del Estado de Bolivia).
    - Deslindes de responsabilidad médica (*Medical Disclaimers* y límites entre recomendación clínica vs. reporte de existencias comerciales).
    - Plan de transición desde web scraping hacia convenios oficiales de interoperabilidad y APIs de farmacias asociadas.

### 2. `SCRUM-46` (`US-31` - 5 SP): Pulido Didáctico, Lenguaje Ciudadano y Semáforo Coherente del MVP (v3.0)
* **Como** Adulto mayor jubilado o ciudadano sin conocimientos técnicos de Machine Learning,
* **Quiero** una versión refinada y clara del MVP con lenguaje 100% amigable y accesible, que incluya definiciones comprensibles de términos como "quiebre de stock" y un semáforo predictivo cuya lógica sea completamente coherente con la disponibilidad inmediata en farmacias,
* **Para** entender con claridad el estado de mi insulina sin confundirme con jerga técnica y confiar en el semáforo para saber cuándo debo comprar anticipadamente o cuándo hay stock suficiente garantizado.
* **Criterios de Aceptación / Validación:**
  - [ ] Eliminación de tecnicismos como "Machine Learning", "Random Forest", "Variables Analíticas" y "Lag de importaciones" en la vista principal del usuario en `src/mvp/generar_mvp_interactivo.py`.
  - [ ] Incorporación de un glosario visual accesible y tarjetas explicativas con lenguaje ciudadano (ej. *"Quiebre de stock: Situación en la que las farmacias agotan por completo sus existencias y no pueden reponer de inmediato"*).
  - [ ] Corrección algorítmica estricta del Semáforo de Riesgo: Ninguna insulina marcará ROJO si se encuentra disponible en una o más cadenas farmacéuticas; el ROJO se reserva únicamente si todas las farmacias están agotadas. El AMARILLO refleja riesgo moderado por pocas unidades o proximidad al cobro de pensiones Banco Unión (días 1 al 5). El VERDE refleja abastecimiento estable y suficiente.
  - [ ] Generación automática del visualizador v3.0 (`docs/mvp_jubilados_comparador.html`) con diseño responsivo, alto contraste y tipografía apta para jubilados.
  - [ ] Tests unitarios automatizados que verifiquen las reglas semafóricas y la no presencia de rojo en medicamentos con stock activo.

### 3. `SCRUM-47` (`US-32` - 5 SP): Diseño Metodológico de Instrumentos de Validación Empírica con Usuarios (SUS y Entrevistas)
* **Como** Diseñador UX e Investigador de Validación de Negocio,
* **Quiero** diseñar y protocolizar los instrumentos de validación empírica con usuarios (escala de usabilidad SUS adaptada al adulto mayor boliviano, guía de entrevistas semiestructuradas y matriz de prueba de tareas guiadas),
* **Para** contar con un marco metodológico estandarizado, riguroso y replicable que permita cuantificar la aceptación, facilidad de uso y valor percibido del MVP antes del producto final.
* **Criterios de Aceptación / Validación:**
  - [ ] Documento metodológico completo en `docs/08_diseno_metodologico_validacion_usuarios.md`.
  - [ ] Formulario de Escala de Usabilidad del Sistema (SUS - System Usability Scale) de 10 reactivos adaptado a lenguaje neutro y comprensible para adultos mayores de Santa Cruz.
  - [ ] Protocolo y guía de entrevista cualitativa semiestructurada enfocada en: hábitos de compra, frecuencia de desabastecimiento, comprensión del semáforo y disposición de uso.
  - [ ] Matriz de pruebas de tareas guiadas (*Task Testing*): Tarea 1 (Buscar su insulina habitual), Tarea 2 (Identificar la farmacia más barata y el ahorro), Tarea 3 (Interpretar el semáforo y disponibilidad en su anillo).
  - [ ] Consentimiento informado y pautas éticas para interacción con adultos mayores jubilados.

### 4. `SCRUM-48` (`US-33` - 8 SP): Trabajo de Validación de Campo, Tabulación de Datos e Informe de Conclusiones de Negocio
* **Como** Product Owner y Analista de Negocio,
* **Quiero** aplicar los instrumentos de validación a una muestra representativa de jubilados diabéticos y familiares cuidadores en Santa Cruz de la Sierra, tabular cuantitativamente los resultados SUS y generar un informe gerencial de conclusiones y aprendizajes de negocio,
* **Para** validar empíricamente la hipótesis de valor de la solución, cuantificar la usabilidad del prototipo y orientar las decisiones estratégicas de la siguiente iteración con evidencia real.
* **Criterios de Aceptación / Validación:**
  - [ ] Aplicación y tabulación de la muestra empírica en `data/processed/validacion_usuarios_tabulacion.csv`.
  - [ ] Cálculo estadístico del puntaje global SUS (escala 0-100) y desglose por dimensiones de usabilidad y aprendizaje.
  - [ ] Matriz cualitativa de hallazgos, barreras identificadas (*friction points*) y cotizaciones verbales de los entrevistados.
  - [ ] Informe formal de conclusiones de negocio y recomendaciones en `docs/09_informe_validacion_campo_y_negocio.md`.
  - [ ] Conclusiones cuantitativas y cualitativas que respondan a la viabilidad del MVP y prioricen las mejoras para el release final.
