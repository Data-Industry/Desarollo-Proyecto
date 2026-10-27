# SCRUM-43 / US-28 — Ingesta Automatizada del Tipo de Cambio Oficial del BCB

**Fase CRISP-DM:** Fase 2: Comprensión de los Datos  
**Historia de Usuario:** `US-28` (`SCRUM-43`)  
**Story Points:** 3 SP  
**Sprint:** Sprint 2 (Activo)  

---

## 1. Justificación y Necesidad de Negocio

Para proyectar con precisión la disponibilidad y el precio de medicamentos esenciales importados como la insulina, resulta indispensable contar con una fuente oficial, auditable y reproducible del tipo de cambio en Bolivia (BOB/USD).

En etapas preliminares se implementó un modelo referencial fluctuante que proyectaba cotizaciones superiores a 16 Bs/USD para 2026. No obstante, las estadísticas de comercio exterior y la realidad del mercado farmacéutico indican que la cotización oficial rara vez superó los 12.00–12.50 Bs/USD durante dicho periodo.

Con el fin de erradicar discrepancias y cumplir con los criterios de auditoría de CRISP-DM, se incorpora la **Historia de Usuario US-28** para la ingesta directa, validación y procesamiento de las cotizaciones oficiales publicadas por el **Banco Central de Bolivia (BCB)** a través de su plataforma de **Gráfico Evolutivo de Cotizaciones**.

---

## 2. Fuente Oficial y Endpoints Web del BCB

- **Portal Web Oficial:** [https://www.bcb.gob.bo/grafico_evolutivo/](https://www.bcb.gob.bo/grafico_evolutivo/)
- **Datos Crudos en Repositorio:** `data/raw/Tipo_de_cambio.csv` (delimitado con `;`, 2,126 registros diarios desde el 01/01/2021 hasta el 27/10/2026).
- **Mecanismos de Consulta e Ingesta:**
  1. **Tramo Base Histórico (2021 al 28/06/2026):** Extraído desde el endpoint script `https://www.bcb.gob.bo/grafico_evolutivo/assets/datos-grafico-evolutivo.js`, el cual expone la variable JSON `DATOS_GRAFICO_EVOLUTIVO["tipo_de_cambio"]["datos"]`.
  2. **Tramo Dinámico Diario (desde 29/06/2026 a la fecha):** Obtenido de forma reactiva desde `https://www.bcb.gob.bo/grafico_evolutivo/tco-runtime.php`, el cual alimenta `window.BCB_TCO_DB` directamente desde la base de datos oficial del BCB.

---

## 3. Arquitectura del Pipeline ETL (`src/etl/02_ingesta_tipo_cambio_bcb.py`)

El pipeline ejecuta las siguientes etapas automáticas:
1. **Doble Mecanismo de Ingesta (Online / Offline):**
   - Si existe conectividad, consulta los endpoints oficiales del BCB y actualiza `data/raw/Tipo_de_cambio.csv` respetando el delimitador `;`.
   - Si opera sin conexión o ante excepciones de red, carga de forma inmediata el archivo local de respaldo `data/raw/Tipo_de_cambio.csv`.
2. **Normalización Diaria:**
   - Estandariza fechas en formato ISO (`YYYY-MM-DD`).
   - Extrae `gestion`, `mes`, `dia` y `fecha_periodo`.
   - Clasifica el régimen cambiario formal (paridad fija 6.86/6.96 hasta 2022, transición 2023, fluctuación interbancaria 2024–2025, cotización fluctuante diaria BCB 2026).
   - Exporta: [`data/processed/tipo_cambio_diario_bcb.csv`](file:///c:/Users/USUARIO/Desktop/Proyecto%20Integrador/data/processed/tipo_cambio_diario_bcb.csv).
3. **Agregación Mensual para Series Temporales:**
   - Calcula el promedio mensual ponderado, valor de cierre de mes, mínimos, máximos y variación intermensual porcentual.
   - Exporta: [`data/processed/tipo_cambio_mensual_bcb.csv`](file:///c:/Users/USUARIO/Desktop/Proyecto%20Integrador/data/processed/tipo_cambio_mensual_bcb.csv) y [`data/processed/tipo_cambio_historico_bolivia.csv`](file:///c:/Users/USUARIO/Desktop/Proyecto%20Integrador/data/processed/tipo_cambio_historico_bolivia.csv) (70 periodos continuos).

---

## 4. Validación de Criterios de Aceptación (DoD)

- [x] **Criterio 1 (Formato y Delimitador):** Ingesta exitosa del archivo delimitado por punto y coma (`;`) sin errores de parseo numérico ni de fechas.
- [x] **Criterio 2 (Rango Oficial en 2026):** Verificación de que en la gestión 2026 las cotizaciones se mantengan entre 8.78 y 12.02 Bs/USD, garantizando coherencia con el mercado cambiario oficial.
- [x] **Criterio 3 (Integración con Importaciones US-21):** Sustitución del cálculo empírico en `src/etl/etl_importaciones.py` por las cotizaciones oficiales del BCB, recalculando el valor CIF en BOB y costos por kilogramo.
- [x] **Criterio 4 (Pruebas Automatizadas):** Suite de pruebas unitarias aprobada en [`src/etl/test_tipo_cambio_bcb.py`](file:///c:/Users/USUARIO/Desktop/Proyecto%20Integrador/src/etl/test_tipo_cambio_bcb.py) (4/4 tests aprobados).
