# Reestructuración del Backlog en Jira (Proyecto Insulina CRISP-DM)

**Tablero Oficial Jira Cloud:** [https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog](https://danielmerengue0.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)  
**Estado:** 100% Auditado y Sincronizado (19 Historias de Usuario, 99 Story Points en total).

---

## Resumen de Cuadratura del Backlog (19 Historias / 99 SP)

| Épica (Fase CRISP-DM) | Clave Épica | Historias Incluidas | Cantidad | Story Points |
| :--- | :---: | :--- | :---: | :---: |
| **Fase 1: Comprensión del Negocio** | `SCRUM-29` | `SCRUM-28` (US-19: 7), `SCRUM-15` (US-11: 3), `SCRUM-18` (US-14: 5) | 3 | **15 SP** |
| **Fase 2: Comprensión de los Datos** | `SCRUM-30` | `SCRUM-27` (US-20: 7), `SCRUM-23` (US-21: 7), `SCRUM-20` (US-16: 5), `SCRUM-7` (US-03: 5), `SCRUM-43` (US-28: 3) | 5 | **27 SP** |
| **Fase 3: Preparación de los Datos** | `SCRUM-31` | `SCRUM-36` (US-22: 5), `SCRUM-42` (US-27: 5), `SCRUM-37` (US-23: 5), `SCRUM-24` (US-02: 3) | 4 | **18 SP** |
| **Fase 4: Modelado** | `SCRUM-33` | `SCRUM-8` (US-04: 5), `SCRUM-9` (US-05: 8) | 2 | **13 SP** |
| **Fase 5: Evaluación** | `SCRUM-34` | `SCRUM-38` (US-24: 5), `SCRUM-39` (US-25: 3) | 2 | **8 SP** |
| **Fase 6: Despliegue** | `SCRUM-35` | `SCRUM-10` (US-06: 5), `SCRUM-41` (US-26: 8), `SCRUM-40` (US-10: 5) | 3 | **18 SP** |
| **TOTAL PROYECTO** | | **19 Historias de Usuario** | **19** | **99 SP** |

---

## Distribución por Sprints en Jira

### SCRUM Sprint 1 (Cerrado - 22 SP)
- **`SCRUM-28` (US-19 - 7 SP):** Integración y automatización de repositorio GitHub con directorio local.
- **`SCRUM-15` (US-11 - 3 SP):** Definición del problema de negocio, perfil de actores y pregunta de investigación (`docs/01_comprension_negocio.md`).
- **`SCRUM-27` (US-20 - 7 SP):** Extracción automatizada (Web Scraping) de stock y precios en portales de farmacias (Farmacorp, Chávez, Telchi).
- **`SCRUM-36` (US-22 - 5 SP):** Pipeline ETL de limpieza, estandarización de precios y normalización de insulinas (`insulinas_master.csv`).

### SCRUM Sprint 2 (Activo / En Cierre - 25 SP)
- **`SCRUM-23` (US-21 - 7 SP):** Ingesta y normalización de importaciones aduaneras de insulina (Partida NANDINA `3004.31.00.00`) con Tipo de Cambio Oficial del BCB. **[Completada]**
- **`SCRUM-20` (US-16 - 5 SP):** Auditoría automatizada de calidad de datos y análisis exploratorio (EDA) multivariable integrando la fusión de US-27 y geolocalización de US-03. **[Completada]**
- **`SCRUM-7` (US-03 - 5 SP):** Script de geolocalización de sucursales farmacéuticas y mapeo por anillos urbanos (1 al 8) en Santa Cruz. **[Completada - Mía Wayar]**
- **`SCRUM-42` (US-27 - 5 SP):** Fusión de fuentes (Scraping + Importaciones) y preparación de variables de rezago temporal de abastecimiento. **[Completada - Mía Wayar]**
- **`SCRUM-43` (US-28 - 3 SP):** Ingesta automatizada del tipo de cambio oficial del BCB (`https://www.bcb.gob.bo/grafico_evolutivo/`) y serie histórica diaria (`Tipo_de_cambio.csv`). **[Completada]**

### Product Backlog Priorizado (52 SP)
- `SCRUM-18` (US-14 - 5 SP): Metas de minería, métricas de éxito (Recall) y cronograma.
- `SCRUM-37` (US-23 - 5 SP): Imputación zonal de faltantes y cruce con calendario bancario Banco Unión.
- `SCRUM-24` (US-02 - 3 SP): Feature Engineering y matriz de correlación temporal y espacial.
- `SCRUM-8` (US-04 - 5 SP): Análisis espacial de cobertura y densidad por anillos urbanos.
- `SCRUM-9` (US-05 - 8 SP): Entrenamiento de modelos supervisados de disponibilidad de stock.
- `SCRUM-38` (US-24 - 5 SP): Evaluación con optimización de Recall para minimizar falsos positivos.
- `SCRUM-39` (US-25 - 3 SP): Generación automatizada de reportes de desempeño y Feature Importance.
- `SCRUM-10` (US-06 - 5 SP): Motor lógico del semáforo predictivo preventivo.
- `SCRUM-41` (US-26 - 8 SP): Chatbot conversacional accesible para adultos mayores y cuidadores.
- `SCRUM-40` (US-10 - 5 SP): Sistema de alertas preventivas tempranas (5 a 7 días antes de agotar).
