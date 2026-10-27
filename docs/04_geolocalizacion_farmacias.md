# Geolocalización de sucursales farmacéuticas — SCRUM-7

## Objetivo

Construir un catálogo auditable de sucursales físicas de farmacias de Santa Cruz de la Sierra y asignar un anillo urbano solo cuando exista evidencia suficiente. El proceso no infiere direcciones, coordenadas ni anillos.

## Fuente de sucursales

El catálogo maestro es `data/raw/sucursales_farmacias_scz.csv`. A la fecha de
verificación (25 de octubre de 2026) contiene 16 sucursales físicas de Santa
Cruz de la Sierra: 12 de Farmacorp, 3 de Farmacias Chávez y 1 de Farmacias
Telchi.

Las 12 filas de Farmacorp usan el listado público oficial de la cadena:

<https://farmacorp.com/pages/bases-de-la-promocion-hay-bebe>

Las tres filas de Farmacias Chávez fueron incorporadas exclusivamente a partir
de registros nominados de sucursal, dirección y coordenadas publicados por la
Guía Urbana GAMSC. La fila de Farmacias Telchi combina su listado oficial de
sucursales con la coincidencia de nombre y ubicación de la Guía Urbana GAMSC.
Las URLs de ambas fuentes se conservan por fila en `fuente` y
`fuente_geocodificacion`.

Cada fila identifica una sucursal física con `id_sucursal`; no se usan las
etiquetas generales de cobertura de los datasets de productos.

## Estrategia híbrida

`src/etl/04_geolocalizar_farmacias.py` crea `data/processed/farmacias_geolocalizadas.csv` y aplica el siguiente orden:

1. **Dirección explícita.** Reconoce únicamente expresiones de anillo del 1 al 8 escritas en la dirección oficial. Una sola referencia se registra como `ASIGNADO` con método `DIRECCION_EXPLICITA`.
2. **Ambigüedad.** Si una dirección contiene dos anillos, como “entre 2do y 3er Anillo”, no asigna ningún valor y registra `AMBIGUO_EN_BORDE`.
3. **Geocodificación opcional.** Con `--geocodificar`, consulta Nominatim para direcciones sin coordenadas. Se limita a una consulta por segundo, usa un User-Agent identificable y guarda la consulta, respuesta y fecha. Un único resultado razonable queda como `CANDIDATO_VALIDACION`, nunca como ubicación validada automáticamente.
4. **GIS futuro.** La función `asignar_anillo_por_geometria()` reserva el punto de integración para una capa oficial de polígonos. No crea polígonos ni usa estimaciones mientras el archivo `data/raw/cartografia/gamsc_anillos_1_8.geojson` no exista y sea validado.

## Por qué no se usa distancia radial

Los anillos son infraestructura vial y no círculos concéntricos perfectos. Clasificar una sucursal por distancia al centro sería una aproximación no verificable y puede contradecir su ubicación real frente a una avenida de anillo. Por esa razón, el pipeline no usa distancia radial.

## Hallazgos de la Guía Urbana GAMSC

La Guía Urbana Municipal publica un visor Leaflet, un WMS y un WFS de GeoServer bajo el dominio municipal. El WFS expone, entre otras, las capas `calles_vias`, `calles_vias_principales`, `distritos_wgs84` y `unidades_vecinales_wgs84`. También dispone de puntos de farmacia y búsquedas de vías.

No se identificó una capa pública completa de polígonos oficiales para los anillos 1–8. Las vías verificables no sustituyen una zonificación completa: antes de hacer point-in-polygon debe obtenerse o validarse una capa oficial que tenga un atributo `anillo` con valores 1–8.

## Validaciones

- `id_sucursal` es único dentro de cada cadena.
- Latitud y longitud son obligatoriamente un par.
- Latitud válida: -90 a 90; longitud válida: -180 a 180.
- Todo anillo asignado está entre 1 y 8.
- Ningún registro `AMBIGUO_EN_BORDE` puede recibir anillo.
- Registros sin coordenadas quedan visibles como pendientes de geocodificación.

## Dependencias

La ejecución base usa la biblioteca estándar de Python. La opción
`--geocodificar` requiere `geopy`; las pruebas automatizadas requieren `pytest`.
No se instala GeoPandas ni Shapely hasta disponer de una capa oficial de
polígonos que deba procesarse.

## Resultados actuales

La ejecución sin `--geocodificar` no realiza llamadas externas. El catálogo
actual tiene 16 sucursales: 12 Farmacorp, 3 Farmacias Chávez y 1 Farmacias
Telchi. Cinco sucursales tienen coordenadas `VALIDADA`: Farmacorp SC-31, las
tres de Chávez y la de Telchi. Las cinco provienen de evidencia municipal
verificable de la Guía Urbana GAMSC; las once restantes continúan pendientes de
validación geográfica para evitar inferencias no sustentadas.

Los anillos asignados proceden exclusivamente de referencias explícitas e
inequívocas de las direcciones de origen. No representan una inferencia por
distancia ni por las coordenadas disponibles. Con las filas actuales hay ocho
anillos asignados: cuatro en el anillo 2, dos en el 3, uno en el 4 y uno en el
7. Tres registros se encuentran `AMBIGUO_EN_BORDE`: Farmacorp SC-18, Chávez
CH-02 y Chávez CH-03.

### Ejecución de geocodificación con Nominatim

El 25 de octubre de 2026 se ejecutó el modo `--geocodificar` con las doce
consultas completas de dirección, ciudad y país. Se respetó una consulta por
segundo y se guardó en la salida cada consulta y la respuesta textual recibida.

| Resultado | Cantidad |
|---|---:|
| Sucursales con coordenadas devueltas | 0 |
| Coordenadas `VALIDADA` | 0 |
| `CANDIDATO_VALIDACION` | 0 |
| `AMBIGUA` | 1 |
| `NO_ENCONTRADA` | 11 |

La única respuesta con candidatos fue `SC-07 IRALA FG`: Nominatim devolvió
tres alternativas de avenidas y no una coincidencia identificable para la
sucursal `Av. Irala #564`; por ello no se guardaron coordenadas. Las otras once
consultas no devolvieron resultado. Ningún estado `NO_ENCONTRADA` significa que
la sucursal no exista: únicamente que Nominatim no entregó una coincidencia
confiable para la consulta oficial utilizada.

Las coordenadas y el anillo son variables distintas. La incorporación de
coordenadas validadas no modifica un anillo: cada anillo actual sigue siendo
una referencia explícita e inequívoca de la dirección de origen.

## Candidatos pendientes de validación

Se mantienen fuera del catálogo maestro diez candidatos identificados durante
la revisión de fuentes públicas, porque todavía no hay evidencia suficiente
para identificar inequívocamente una sucursal física con un ID propio.

- **Farmacias Chávez (7, confianza MEDIA):** referencias municipales de Av.
  Paurito; Av. Principal 1ro de Mayo con Calle 12 Este; Av. Principal 1ro de
  Mayo con Calle 8 Este; Av. Bush; 2do Anillo en zona El Pari; Av. Paraguá; y
  Virgen de Cotoca. Aunque la Guía Urbana publica puntos y coordenadas, no
  publica un nombre de sucursal que permita distinguirlos sin ambigüedad.
- **Farmacias Telchi (3, confianza MEDIA):** Sucursal Roca y Coronado,
  Sucursal 2do Anillo y Sucursal Centro, listadas en la fuente oficial de la
  cadena. La fuente consultada no publica dirección detallada ni coordenadas,
  y no se obtuvo una coincidencia municipal inequívoca.

Estos candidatos requieren una fuente oficial adicional, validación manual o
una coincidencia municipal que identifique la sucursal antes de incorporarse al
catálogo.

## Limitaciones y evolución

- Las coordenadas obtenidas desde Nominatim son candidatas y requieren contraste con una fuente oficial.
- Nominatim puede no indexar direcciones locales, esquinas, abreviaturas o datos recientes; un resultado vacío no invalida la dirección oficial.
- La Guía Urbana puede contener nombres o direcciones genéricas, por lo que no se debe unir automáticamente un punto municipal a un ID de sucursal sin validación.
- La clasificación espacial definitiva requiere un GeoJSON/GeoPackage oficial completo de anillos 1–8.
- Cuando exista esa capa, se implementará point-in-polygon en `asignar_anillo_por_geometria()` y se documentará la versión, CRS, licencia y fecha de extracción.
