# Módulo ETL: Ingesta y Normalización de Importaciones de Insulina (US-21)

**Historia de Usuario:** `US-21` / `SCRUM-23` (Ingesta, limpieza y normalización de importaciones aduaneras de insulina)  
**Épica Jira:** `SCRUM-30` (Fase 2: Comprensión de los Datos) / `SCRUM-31` (Fase 3: Preparación de los Datos)  
**Story Points:** 7 SP  
**Sprint:** Sprint 2  

---

## 1. Descripción

Este módulo automatiza la ingesta, depuración y normalización de las estadísticas de comercio exterior de Bolivia correspondientes a la importación de insulina bajo la subpartida arancelaria **NANDINA `3004.31.00.00`** (*Medicamentos que contengan insulina*).

El módulo calcula métricas financieras, logísticas y un **semáforo predictivo preventivo de abastecimiento upstream** para alertar caídas en los arribos aduaneros antes de que se manifiesten como quiebres de stock en las farmacias de Santa Cruz.

---

## 2. Archivos Generados

- `data/raw/importaciones_aduana_bolivia_crudo.csv`: Ingesta cruda de despachos aduaneros (76 registros).
- `data/processed/importaciones_insulina_bolivia.csv`: Dataset maestro normalizado con 24 campos clínicos y logísticos (70 registros).
- `data/processed/importaciones_insulina_bolivia.json`: Formato estructurado JSON para consumo de microservicios y APIs.
- `data/processed/descartes_importaciones_no_insulina.csv`: Bitácora de auditoría de descartes (6 registros no insulina).
- `data/processed/importaciones_insulina_mensual_resumen.csv`: Serie temporal mensual con variación intermensual y semáforo preventivo.

---

## 3. Instrucciones de Ejecución

### Ejecutar el pipeline ETL:
```powershell
python src/etl/03_etl_importaciones.py
```

### Ejecutar las pruebas automatizadas de validación:
```powershell
python -m unittest src/etl/test_03_importaciones.py
```
Salida esperada:
```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.024s

OK
```
