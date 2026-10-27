# SCRUM-42 — Fusión de Importaciones y Stock Retail

## Objetivo

Preparar una base auditable para relacionar importaciones de la partida 3004.31.00.00 con disponibilidad retail de insulinas. Esta etapa consolida snapshots, resume disponibilidad categórica y genera candidatos de correspondencia; no estima un lag estadístico.

## Fuentes utilizadas

### Importaciones

`data/processed/importaciones_insulina_bolivia.csv` y su resumen mensual contienen 70 períodos consecutivos, desde 2021-01 hasta 2026-10. Incluyen fecha de período, descripción comercial, origen, aduana, destino, kilos netos y brutos, valores CIF/FOB, costos derivados, viales/UI estimados y alertas upstream.

Advertencia de trazabilidad: el dataset actual de importaciones fue generado internamente por `src/etl/etl_importaciones.py`. Debe validarse o reemplazarse posteriormente por una fuente oficial trazable de INE/Aduana antes de utilizarlo para conclusiones operativas o estadísticas. En los artefactos de SCRUM-42 esto se declara con `fuente_importacion_estado = NO_VALIDADA_OFICIALMENTE` y `fuente_importacion_tipo = DATASET_GENERADO_POR_ETL`.

Los valores numéricos actuales no deben citarse como estadísticas oficiales de importación de Bolivia. En particular, `viales_estimados` y `ui_estimadas` son variables derivadas por el ETL a partir de supuestos de conversión; no son inventario físico observado ni unidades confirmadas por una fuente aduanera oficial.

### Retail

Se consolidan cuatro snapshots históricos reales: todos pertenecen al 19 de octubre de 2026. `insulina_precios_stock_latest.csv` es un alias/duplicado del último snapshot y se excluye mediante hash de contenido. El stock disponible es categórico (`DISPONIBLE`, `ULTIMAS_UNIDADES`, `AGOTADO`); no es inventario cuantitativo.

## Consolidación histórica retail

`src/etl/fusion_importaciones_stock.py` descubre todos los archivos `data/raw/insulina_precios_stock_*.csv`, deduplica archivos idénticos por SHA-256 y conserva `archivo_origen` y `snapshot_id` en `data/processed/retail_stock_historico_consolidado.csv`.

El resumen `data/processed/retail_stock_mensual_resumen.csv` se agrupa por período, farmacia, principio activo y, cuando existe, marca canónica. Cada fila de snapshot es una observación: `productos_observados` es su conteo total. Las categorías mutuamente excluyentes son `productos_stock_normal` (`DISPONIBLE`), `productos_ultimas_unidades` (`ULTIMAS_UNIDADES`) y `productos_agotados` (`AGOTADO`), por lo que su suma equivale a `productos_observados`.

`productos_disponibles` significa **disponibilidad efectiva**, no exclusivamente stock normal: incluye `productos_stock_normal + productos_ultimas_unidades`, porque ambos estados permiten adquirir el producto. La `tasa_disponibilidad` es `productos_disponibles / productos_observados`. Estas métricas representan observaciones categóricas de los snapshots, no unidades de inventario ni ventas.

## Mapeo importación-retail

`data/processed/mapeo_productos_importacion_retail.csv` registra correspondencias candidatas con texto original y normalizado, marca, principio activo, laboratorio, presentación, cardinalidad, confianza y revisión requerida. Las descripciones con varias marcas preservan la relación muchos-a-muchos. La similitud textual no se usa como unión automática definitiva: los candidatos ambiguos requieren revisión humana.

## Relación territorial

SCRUM-7 aporta sucursales físicas geolocalizadas y algunos anillos asignados en `farmacias_geolocalizadas.csv`. Sin embargo, el scraping actual registra etiquetas generales de cobertura de red, no una sucursal física verificable por producto. Por ello no existe todavía una relación verificable producto → sucursal física → anillo y esta etapa no la infiere.

## Preparación de variables temporales

`data/processed/importaciones_santa_cruz_mensual.csv` agrega los despachos cuyo `departamento_destino` es `Santa Cruz`. El calendario conserva los 70 meses disponibles de la fuente nacional; si no existen despachos a Santa Cruz para un mes, los totales agregados son cero y el costo por kilo queda sin definir (`NaN`).

`data/processed/importaciones_stock_lags_preparados.csv` incorpora para kilos netos, CIF USD, viales estimados y UI estimadas:

- `lag_0m`: valor de importación del mismo mes.
- `lag_1m`: valor del mes calendario anterior.
- `lag_2m`: valor de dos meses calendario anteriores.
- `lag_3m`: valor de tres meses calendario anteriores.

Las primeras filas conservan valores ausentes cuando no hay historia previa suficiente.

## Diferencia entre lag preparado y lag estimado

Las variables `lag_1m`, `lag_2m` y `lag_3m` representan desplazamientos temporales de variables de importación y se preparan como posibles predictores. No constituyen una estimación estadística del tiempo logístico de reposición ni representan días o meses reales de demora logística.

Por ello, los artefactos incluyen `lag_preparado = True` y `lag_estimado_estadisticamente = False`. No se calcula correlación cruzada, lag óptimo ni causalidad.

## Fusión mensual

`data/processed/importaciones_stock_fusion_mensual.csv` realiza una unión por `fecha_periodo`, sin forzar una unión por producto. El retail de 2026-10 se enriquece con la importación Santa Cruz de 2026-10 y sus valores preparados de 2026-09, 2026-08 y 2026-07. No se fabrican meses retail históricos.

## Limitaciones temporales

Con los datos disponibles actualmente no es estadísticamente defendible estimar un desfase temporal real entre importaciones y disponibilidad retail. Tampoco existe historia retail suficiente para calcular un lag óptimo.

Las importaciones son mensuales, mientras el retail disponible solo cubre cuatro lecturas intradía de un único día de octubre de 2026. No hay serie retail mensual suficiente para correlación cruzada, selección de desfase, intervalos de confianza o atribución causal.

Otras limitaciones: stock categórico sin cantidades físicas; ausencia de fecha de nacionalización y de fecha de reposición; falta de una relación verificable producto–sucursal–anillo; y fuente importadora actual generada internamente que requiere validación oficial trazable.

## Condición para estimar lag real

Solo podrá evaluarse una relación temporal estadística cuando exista una serie retail periódica suficiente, con cobertura y calidad documentadas, y una fuente importadora oficial trazable. Hasta entonces, los desplazamientos son únicamente predictores preparados.

## Próxima etapa

La próxima etapa podrá ampliar la cobertura retail y revisar el mapeo canónico. Las variables ya construidas seguirán tratándose como predictores preparados, no como lags estadísticos estimados, hasta acumular suficientes snapshots retail periódicos y una fuente importadora oficial trazable.
