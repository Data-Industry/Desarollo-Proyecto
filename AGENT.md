# Guía y Contexto Operativo para Agentes de Inteligencia Artificial (AGENT.md)

> **AVISO PARA EL AGENTE DE IA / COPILOTO:**  
> Este documento contiene el contexto integral del proyecto, la arquitectura metodológica, las reglas de negocio, el backlog de historias de usuario y el **Protocolo Obligatorio de Commits y Trazabilidad**.  
> **Cualquier agente de IA o colaborador debe leer y respetar este archivo antes y durante el desarrollo de cualquier tarea.**

---

## 1. Visión del Proyecto y Contexto de Negocio

### 1.1. Título y Alcance
- **Proyecto:** Sistema Predictivo de Disponibilidad y Precios de Insulina con Asistente Conversacional (Chatbot) para Pacientes Insulinodependientes.
- **Ubicación Geográfica:** Santa Cruz de la Sierra, Bolivia (anillos urbanos 1 al 8).
- **Marco Temporal de Análisis:** Segundo semestre de 2026.
- **Repositorio Remoto Oficial:** [https://github.com/Data-Industry/Desarollo-Proyecto](https://github.com/Data-Industry/Desarollo-Proyecto)

### 1.2. El Problema y Causas Raíz
Los pacientes jubilados con diabetes insulinodependientes en Santa Cruz de la Sierra enfrentan dificultades críticas para acceder oportunamente a insulina importada debido a la falta de visibilidad del stock disponible en farmacias.
- **Inventarios aislados:** Las farmacias gestionan sus existencias de manera independiente sin una plataforma consolidada.
- **Brecha digital y movilidad reducida:** La población de adultos mayores presenta barreras para navegar portales web complejos, obligándolos a peregrinar físicamente bajo condiciones climáticas adversas (calor extremo) con alto riesgo de interrumpir su tratamiento médico.

### 1.3. Preguntas Clave
- **Pregunta de Investigación:** ¿Cuáles son los factores que permiten predecir la disponibilidad de insulina importada para los pacientes jubilados con diabetes en Santa Cruz de la Sierra durante el segundo semestre de 2026?
- **Pregunta Analítica:** ¿Qué variables temporales, territoriales y de abastecimiento permiten predecir si una farmacia tendrá disponibilidad de insulina importada en un periodo determinado?

### 1.4. Solución Integral y Arquitectura Analítica
1. **Pipeline de Ingesta Dual (Oferta y Demanda):**
   - **Demanda / Stock Inmediato:** Web scraping automatizado periódico de portales de farmacias en Santa Cruz (Farmacorp, Farmacias Chávez, Farmacias Telchi).
   - **Oferta Macro / Importaciones Upstream:** Ingesta y normalización de registros oficiales de comercio exterior (INE / Aduana Nacional de Bolivia) bajo la partida arancelaria NANDINA `3004.31.00.00` (*Medicamentos que contengan insulina*).
2. **Dataset Maestro Analítico:** Normalización estricta de medicamentos de insulina pura en `insulinas_master.csv`, excluyendo descartables (jeringas/agujas) y fármacos ajenos hacia bitácoras de auditoría.
3. **Modelos Predictivos y Semáforo de Alerta Preventiva:**
   - Modelado de desfase temporal (*Lag logístico* entre arribo aduanero y distribución en farmacia).
   - Clasificación supervisada de probabilidad de stock ($P \ge 70\%$) y semaforización predictiva (`VERDE`, `AMARILLO`, `ROJO`).
   - Detección estadística de dispersión y anomalías de precios por 100 UI.
   - Análisis espacial de densidad y cobertura territorial por anillos urbanos (1 al 8).
4. **Chatbot Conversacional Accesible:** Interfaz simple en lenguaje natural para que el adulto mayor o su familiar consulte disponibilidad inmediata, precios y alternativas cercanas sin navegar en sitios web complejos.
5. **Dashboard Analítico:** Visualización interactiva para monitoreo preventivo y tomadores de decisión.

---

## 2. Metodología de Trabajo y Tablero de Control

El proyecto sigue el estándar **CRISP-DM** en 6 fases, gestionado en **Jira Cloud** (Clave `SCRUM`, 18 Historias de Usuario, 96 Story Points en total).

### 2.1. Matriz Refactorizada del Product Backlog (18 Historias de Usuario)

| Épica (Fase CRISP-DM) | Clave | Historia de Usuario | SP | Estado / Asignación |
| :--- | :--- | :--- | :---: | :--- |
| **Fase 1: Comprensión del Negocio** | `US-19` | Integración y estructuración del repositorio GitHub según CRISP-DM | 7 | **Completada (Sprint 1)** |
| **Fase 1: Comprensión del Negocio** | `US-11` | Definición del problema, causas raíz, perfil de actores y preguntas de investigación | 3 | **Completada (Sprint 1)** |
| **Fase 1: Comprensión del Negocio** | `US-14` | Metas de minería de datos, métricas de éxito (Recall), ética y cronograma CRISP-DM | 5 | Backlog (Fase 1) |
| **Fase 2: Comprensión de los Datos** | `US-20` | Extracción automatizada (Web Scraping) de stock y precios de insulinas | 7 | **Completada (Sprint 1)** |
| **Fase 2: Comprensión de los Datos** | `US-21` | Ingesta, limpieza y normalización de importaciones públicas de insulinas (Partida NANDINA 3004.31.00.00) | 7 | **Sprint 2 (Activo)** |
| **Fase 2: Comprensión de los Datos** | `US-16` | Auditoría de calidad de datos y análisis exploratorio (EDA) multivariable | 5 | **Sprint 2 (Activo)** |
| **Fase 2: Comprensión de los Datos** | `US-03` | Script de geolocalización de sucursales y clasificación por anillos urbanos (1 al 8) | 5 | **Sprint 2 (Activo)** |
| **Fase 3: Preparación de los Datos** | `US-22` | Pipeline ETL de limpieza, estandarización de precios y normalización de insulinas | 5 | **Completada (Sprint 1)** |
| **Fase 3: Preparación de los Datos** | `US-27` | Fusión de fuentes (Scraping + Importaciones) y modelado de desfase temporal (Lag) de abastecimiento | 5 | **Sprint 2 (Activo)** |
| **Fase 3: Preparación de los Datos** | `US-23` | Script de imputación zonal de faltantes y cruce con calendario de pensiones (Banco Unión) | 5 | Backlog (Fase 3) |
| **Fase 3: Preparación de los Datos** | `US-02` | Feature Engineering y matriz de correlación temporal-espacial | 3 | Backlog (Fase 3) |
| **Fase 4: Modelado** | `US-04` | Análisis espacial de densidad, proximidad y cobertura de farmacias por anillos (1 al 8) | 5 | Backlog (Fase 4) |
| **Fase 4: Modelado** | `US-05` | Entrenamiento de modelos supervisados de clasificación de stock (Árbol, Reg. Logística) | 8 | Backlog (Fase 4) |
| **Fase 5: Evaluación** | `US-24` | Evaluación rigurosa priorizando métrica de Recall (minimización de traslados inútiles) | 5 | Backlog (Fase 5) |
| **Fase 5: Evaluación** | `US-25` | Script automatizado de reportes de desempeño, curvas ROC y Feature Importance | 3 | Backlog (Fase 5) |
| **Fase 6: Despliegue** | `US-06` | Motor lógico del semáforo predictivo preventivo conectado a la salida de los modelos | 5 | Backlog (Fase 6) |
| **Fase 6: Despliegue** | `US-26` | Desarrollo e integración del Chatbot conversacional para consulta en lenguaje natural | 8 | Backlog (Fase 6) |
| **Fase 6: Despliegue** | `US-10` | Sistema de alertas preventivas de compra anticipada (5 a 7 días antes de agotar) | 5 | Backlog (Fase 6) |

### 2.2. Distribución y Capacidad por Sprints
- **Sprint 1 (Cerrado):** `US-19` (7 SP) + `US-11` (3 SP) + `US-20` (7 SP) + `US-22` (5 SP) = **22 Story Points**.
- **Sprint 2 (Activo):** `US-21` (7 SP) + `US-16` (5 SP) + `US-03` (5 SP) + `US-27` (5 SP) = **22 Story Points**.
- **Sprints Restantes (Modelado, Evaluación y Chatbot):** 52 Story Points.
- **Total Proyecto:** 18 Historias | **96 Story Points**.

---

## 3. Arquitectura del Repositorio y Estándares Técnicos

### 3.1. Estructura de Directorios (CRISP-DM)
```
Proyecto Integrador/
├── data/
│   ├── raw/                  # Datasets crudos (scraping web e importaciones aduaneras INE)
│   └── processed/            # Datasets maestros normalizados (insulinas_master.csv, importaciones_insulina.csv, descartes)
├── docs/                     # Documentación formal por fase CRISP-DM (01_comprension_negocio.md, etc.)
├── src/
│   ├── scraping/             # Scrapers de farmacias (Farmacorp, Chávez, Telchi)
│   ├── etl/                  # Pipelines ETL de insulinas e importaciones aduaneras
│   ├── models/               # Scripts de entrenamiento, inferencia y evaluación ML
│   └── chatbot/              # Backend conversacional y conectores de chat
├── AGENT.md                  # Este documento (Contexto, lineamientos y bitácora obligatoria)
├── tablero_jira.md           # Resumen detallado del backlog de Jira
└── .gitignore                # Reglas de exclusión de git
```

### 3.2. Reglas de Negocio y Calidad de Datos
1. **Foco Estricto en Insulinas Puras:** En `data/processed/insulinas_master.csv` solo deben residir medicamentos de insulina (viales, frascos ampolla, cartuchos, lapiceras). Los descartables (jeringas, agujas) y fármacos ajenos se excluyen y se registran en `descartes_insumos_desechables.csv`.
2. **Partida Arancelaria Oficial de Insulina:** Toda ingesta aduanera debe filtrar y validar exclusivamente la subpartida NANDINA `3004.31.00.00` (*Que contengan insulina*), depurando otras partidas.
3. **Manejo de Errores en Windows:** Siempre considerar que si un archivo `.csv` está abierto en Microsoft Excel, lanzará `PermissionError`. Los scripts deben manejar excepciones y no interrumpir el flujo.
4. **Codificación:** Utilizar siempre `utf-8-sig` en exportaciones `.csv` para compatibilidad universal con Excel y caracteres latinos (acentos, ñ).

---

## 4. PROTOCOLO OBLIGATORIO DE DESARROLLO Y COMMITS PARA EL AGENTE IA

A partir de ahora, **cada agente de IA que colabore en el proyecto debe ejecutar de forma obligatoria el siguiente ciclo de 6 pasos para cada tarea o Historia de Usuario asignada**:

```mermaid
flowchart TD
    P1["1. Lectura de la US y Criterios de Aceptación"] --> P2["2. Desarrollo e Implementación Técnica"]
    P2 --> P3["3. Ejecución y Validación de Criterios"]
    P3 --> P4["4. Git Commit (Conventional Commits)"]
    P4 --> P5["5. Registro Obligatorio en la Bitácora de AGENT.md con N° Ascendente (#001, #002...)"]
    P5 --> P6["6. Sincronización Remota (git push origin main)"]
```

### Detalle de los Pasos:

1. **Lectura de Requisitos:** Identificar la Historia de Usuario (`US-XX`), su Épica y sus Criterios de Aceptación especificados en este documento o en Jira.
2. **Implementación:** Crear o modificar el código, scripts o documentación respetando la estructura CRISP-DM.
3. **Validación Técnica:** Ejecutar los scripts en el entorno local y comprobar de forma explícita que se satisfacen todos los criterios de aceptación sin errores.
4. **Git Commit:** Crear el commit en la rama `main` siguiendo la convención:
   - Formato: `<tipo>(<alcance>): <descripción concisa>` (e.g. `feat(etl): complete US-22 insulin data cleaning and master dataset generation`).
   - Tipos válidos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
5. **Registro Obligatorio en la Bitácora de `AGENT.md`:**  
   Inmediatamente después de realizar el commit, el agente **DEBE** agregar una fila a la **Tabla de Trazabilidad de Commits** (Sección 5 de este archivo), documentando:
   - **N° Commit:** Número secuencial incremental en orden ascendente (`#001`, `#002`, `#003`, ..., `#009`, etc.).
   - **Hash Git:** Short hash de 7 caracteres del commit generado.
   - **Historia de Usuario / Tarea asociada.**
   - **Sprint y Fecha.**
   - **Descripción técnica de lo realizado.**
   - **Confirmación explícita de criterios de validación alcanzados.**
6. **Sincronización:** Ejecutar `git push origin main` para asegurar que el repositorio remoto en GitHub quede actualizado y disponible para el resto del equipo.
7. **Reporte al Usuario:** Comunicar en el mensaje final el N° de commit, el hash, los criterios validados y el estado actualizado del proyecto.

---

## 5. Bitácora Oficial de Commits y Trazabilidad de Historias de Usuario

*Esta tabla se mantiene estrictamente en **orden ascendente por N° de commit secuencial**:*

| N° Commit | Hash Git | Historia / Tarea | Sprint | Fecha | Resumen de lo Desarrollado | Criterios de Validación Alcanzados |
| :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **#001** | `962fe0c` | `US-11` (Inicial) | Sprint 1 | 2026-10-18 | Carga de investigación inicial del problema de desabastecimiento de insulina. | Documento base de contextualización de pacientes con diabetes en Santa Cruz. |
| **#002** | `b74749f` | `US-20` | Sprint 1 | 2026-10-19 | Scrapers automatizados para Farmacorp, Farmacias Chávez (Playwright) y Telchi (WooCommerce). | Extracción exitosa de 52 registros brutos en `data/raw/insulina_precios_stock_latest.csv` con precios, stock y URL. |
| **#003** | `e9e863a` | `US-19` | Sprint 1 | 2026-10-19 | Limpieza de archivos obsoletos (`investigacion-inicial.md`) y preparación para estandarización. | Repositorio limpio de archivos no conformes a la estructura CRISP-DM. |
| **#004** | `09744b5` | `US-19` | Sprint 1 | 2026-10-19 | Creación de directorios estándar CRISP-DM (`data/raw`, `data/processed`, `src/scraping`, `src/etl`, `src/models`, `src/chatbot`, `docs`). | Estructura de carpetas creada, versionada con `.gitkeep` y sincronizada con GitHub `origin/main`. |
| **#005** | `b112494` | `US-11` | Sprint 1 | 2026-10-19 | Documentación formal de la Fase 1 CRISP-DM (`docs/01_comprension_negocio.md`). | Problema de negocio, causa raíz (inventarios aislados y brecha digital), actor validado y pregunta analítica delimitados. |
| **#006** | `25a6a4a` | `US-22` | Sprint 1 | 2026-10-19 | Pipeline ETL en `src/etl/etl_insulinas.py`, generación de dataset maestro y bitácora de descartes. | 9 descartables/fármacos no insulina excluidos (`descartes_insumos_desechables.csv`); 43 medicamentos de insulina pura normalizados con 25 campos en `insulinas_master.csv` y `.json`. |
| **#007** | `22c8056` | `US-19` / Ops | Sprint 1 | 2026-10-21 | Creación inicial de `AGENT.md` con contexto operativo del proyecto y reglas de trazabilidad. | Guía para agentes de IA integrada y documentada en la raíz del repositorio. |
| **#008** | `addfab6` | `US-19` / Ops | Sprint 1 | 2026-10-21 | Sincronización y ajuste inicial de referencias en la bitácora de `AGENT.md`. | Bitácora alineada con el árbol git y remotos. |
| **#009** | `7b0c494` | Ops / Refactor | Sprint 1 | 2026-10-21 | Numeración ascendente secuencial (#001-#009), adición de `US-21` (7 SP) y `US-27` (5 SP) al Sprint 2 (22 SP), eliminación de US-08 redundante. | Backlog cuadra en 96 SP (18 US), Sprint 2 configurado con 22 SP y protocolo de commits ordenado secuencialmente. |

---

## 6. Próximo Paso en el Flujo de Trabajo

- **Sprint Activo:** **Sprint 2 (22 Story Points)**.
- **Historias a Desarrollar:**
  1. `US-21` (7 SP): Ingesta, limpieza y normalización de importaciones aduaneras de insulina (Partida NANDINA `3004.31.00.00`).
  2. `US-16` (5 SP): Auditoría de calidad de datos y análisis exploratorio (EDA) multivariable.
  3. `US-03` (5 SP): Script de georreferenciación de sucursales y clasificación por anillos urbanos (1 al 8).
  4. `US-27` (5 SP): Fusión de fuentes (Scraping + Importaciones) y modelado de desfase temporal (Lag) de abastecimiento.
