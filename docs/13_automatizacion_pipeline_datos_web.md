# SCRUM-52 / US-37 — Automatización del Pipeline de Datos Frescos para la Web Pública

## 1. Objetivo

SCRUM-52 incorpora un comando único y seguro para validar un snapshot retail local, aplicar el modelo de producción existente, consolidar precios, stock, riesgo y sucursales, generar el HTML candidato y publicarlo solamente si supera todos los controles.

El pipeline no ejecuta scraping, no reentrena modelos y no regenera EDA, figuras ni datasets analíticos.

## 2. Problema anterior

La actualización requería ejecutar manualmente varios scripts en un orden no protegido. El generador escribía directamente dos HTML, admitía predicciones faltantes mediante valores verdes por defecto, trataba presencia en Telchi como stock disponible y convertía sucursales sin anillo en anillo central. Tampoco existían freshness gates ni manifest de trazabilidad.

## 3. Arquitectura del refresh

El orquestador es `src/pipeline/refresh_production_web.py`. Usa transformaciones farmacológicas ya definidas por el ETL, pero las ejecuta en memoria para no sobrescribir artefactos intermedios. La inferencia usa `models/modelo_produccion_stock.joblib` y su umbral se obtiene exclusivamente de `models/modelo_metadata.json`.

El HTML se construye mediante `src/ui/generar_mvp_interactivo.py`, ahora capaz de recibir DataFrames preparados en staging.

## 4. Flujo

```text
snapshot local
  → resolución por timestamp real
  → validación de precios, farmacia, URL, timestamp y freshness
  → normalización conservadora de stock y evidencia
  → preparación de features existentes
  → validación BCB
  → validación de sucursales y anillos
  → inferencia con joblib de producción
  → stock observado + riesgo predictivo
  → HTML y manifest en staging
  → gates de integridad
  → publicación atómica; HTML raíz al final
```

## 5. Entradas

- `data/raw/insulina_precios_stock_latest.csv` y snapshots fechados.
- `data/processed/tipo_cambio_diario_bcb.csv`.
- `data/processed/farmacias_geolocalizadas.csv`.
- `models/modelo_produccion_stock.joblib`.
- `models/modelo_metadata.json`.

`--input` permite señalar un snapshot local concreto. Sin esa opción se comparan `latest` y los snapshots fechados usando primero el timestamp interno y el nombre solo como respaldo. `ctime` no interviene como criterio principal.

## 6. Salidas

- `mvp_comparador_jubilados.html`: artefacto público canónico.
- `src/ui/mvp_comparador_jubilados.html`: copia mantenida por compatibilidad.
- `data/processed/web_bundle_manifest.json`: manifest publicado únicamente tras una ejecución válida.

## 7. Validaciones de precios

La publicación se bloquea ante precio actual nulo, no numérico, no finito o menor/igual a cero. Si existe precio regular, debe ser numérico, finito y mayor o igual al actual. También se validan farmacia, URL HTTP/HTTPS, timestamp y unicidad de `farmacia + id_origen`.

Los duplicados exactos pueden eliminarse con warning. Dos registros con la misma clave y contenido incompatible constituyen un error. El pipeline no corrige precios silenciosamente.

## 8. Validaciones de stock

Estados permitidos:

- `DISPONIBLE`
- `ULTIMAS_UNIDADES`
- `AGOTADO`
- `NO_VERIFICADO`

La evidencia se conserva por separado. Farmacias Telchi queda como `NO_VERIFICADO / CATALOG_ONLY`, porque el scraper actual prueba presencia en catálogo, no inventario. Un valor desconocido se convierte en `NO_VERIFICADO / UNKNOWN`, nunca en disponible.

`NO_VERIFICADO` no se convierte en stock positivo. El modelo actual tampoco recibe stock como feature.

## 9. Stock actual vs riesgo predictivo

El bundle contiene explícitamente:

- `stock_actual`
- `stock_evidence`
- `riesgo_predictivo`
- `probabilidad_riesgo`

Es válido observar stock disponible y riesgo predictivo rojo al mismo tiempo: describen conceptos distintos. El pipeline emite `RISK_STOCK_DISAGREEMENT` pero no modifica ninguno de los dos valores. El HTML presenta el riesgo como una estimación, no como inventario.

## 10. Cotización BCB

La serie debe contener fecha, valor positivo y finito, y fuente identificable. El manifest declara la dirección `BOB_PER_USD`. El pipeline no llama a funciones con fallbacks numéricos ni inventa una cotización cuando el archivo falta.

## 11. Freshness

Constantes iniciales:

| Fuente | Warning | Error |
|---|---:|---:|
| Retail | más de 24 horas | más de 72 horas |
| BCB | más de 3 días | más de 7 días |

Una fecha futura también es error. Estos límites no deben flexibilizarse para hacer pasar datos antiguos.

## 12. Manifest

El manifest incluye generación, fecha efectiva de datos, nombre y SHA-256 del snapshot, nombre/hash/umbral/tipo de target del modelo, moneda, fecha y fuente BCB, conteos, warnings, versión de esquema y fingerprint de inputs. Si Git está disponible se incorpora `pipeline_version`; si no, el campo se omite.

## 13. Staging

El candidato se genera dentro de un directorio temporal del proyecto. Allí se escriben y vuelven a leer el HTML y el manifest para validar el artefacto real, sin tocar producción.

## 14. Publicación atómica

La copia de `src/ui` y el manifest se publican antes del HTML raíz. Cada archivo usa un temporal en su mismo directorio y `os.replace()`. El HTML raíz se reemplaza al final. Si una sustitución previa falla, se restauran la copia y el manifest anteriores; el HTML público permanece intacto.

## 15. Idempotencia

El fingerprint combina hashes de snapshot, BCB, sucursales, modelo, metadata, código del pipeline, generador MVP y configuración de freshness. Los registros y el JSON se ordenan de forma determinista.

Si fingerprint, manifest y HTML coinciden con producción, el comando muestra `NO_CHANGES` y no reescribe archivos. Se conserva el `generated_at` original.

## 16. CLI

```bash
python src/pipeline/refresh_production_web.py
python src/pipeline/refresh_production_web.py --dry-run
python src/pipeline/refresh_production_web.py --verbose
python src/pipeline/refresh_production_web.py --input data/raw/insulina_precios_stock_YYYYMMDD_HHMMSS.csv
```

`--dry-run` resuelve, valida, prepara e inspecciona el candidato, pero no publica HTML ni manifest.

## 17. Exit codes

| Código | Significado |
|---:|---|
| 0 | Publicación exitosa, dry-run válido o `NO_CHANGES` |
| 2 | Input o validación de datos |
| 3 | Preparación de features, metadata o modelo |
| 4 | Integridad del manifest/HTML candidato |
| 5 | Publicación o rollback |

## 18. Tests

La suite se ejecuta con:

```bash
python -m unittest src.pipeline.test_refresh_production_web
```

Usa directorios temporales, snapshots y BCB frescos, sucursales fixture y un modelo serializado de prueba. No lee ni modifica los artefactos reales. Cubre precios, timestamps, farmacias, URLs, stock, Telchi, predicciones, umbral, BCB, anillos, bundle, manifest, placeholders, preservación ante fallos e idempotencia.

## 19. Limitaciones

- El pipeline consolida snapshots locales; la obtención de datos sigue siendo un proceso separado.
- Las features farmacológicas se derivan del nombre usando las reglas existentes del ETL.
- El modelo representa un proxy de stock actual y no un evento futuro longitudinal.
- Un semáforo uniforme genera warning, pero no se altera automáticamente.
- El HTML todavía carga Tailwind desde un recurso externo.
- No existe relación verificable producto–sucursal ni cálculo de distancia.

## 20. Cómo explicar este SCRUM

Antes, publicar datos nuevos dependía de una secuencia manual y podía dejar información parcial o engañosa. Ahora un comando selecciona el snapshot correcto, comprueba precios y vigencia, distingue presencia en catálogo de stock confirmado, valida la cotización BCB, ejecuta el modelo ya aprobado y construye una versión candidata de la web. La versión pública solo cambia después de superar todos los controles; si algo falla, se conserva la versión anterior y se informa la causa con un código de salida claro.
