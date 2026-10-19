# Módulo de Web Scraping — Catálogos de Farmacias (Bolivia)

**Historia de Usuario Asociada:** `US-20: Extracción automatizada (Web Scraping) de stock y precios en portales de farmacias` (`SCRUM-27`)  
**Metodología:** CRISP-DM — **Fase 2: Comprensión de los Datos**  
**Área Geográfica:** Santa Cruz de la Sierra, Bolivia.

---

## 1. Descripción
Este módulo implementa scripts automatizados y resilientes para la extracción periódica de disponibilidad de stock, precios en bolivianos (Bs.), descuentos y presentaciones de insulinas (Glargina, NPH, Rápida, Mixta, etc.) en los catálogos en línea de las principales cadenas farmacéuticas en Bolivia:

1. **Farmacorp** (`https://farmacorp.com`): Extracción mediante motor de consultas de catálogo y API de productos en Shopify.
2. **Farmacias Chávez** (`https://www.farmaciaschavez.com.bo`): Extracción headless mediante **Playwright** sobre la plataforma Next.js / Instaleap, navegando el catálogo zonal de Santa Cruz de la Sierra.

---

## 2. Estructura de Archivos

```text
src/scraping/
├── scraper_farmacorp.py    # Scraper especializado para la cadena Farmacorp
├── scraper_chavez.py       # Scraper automatizado con Playwright para Farmacias Chávez
├── main_scraper.py         # Orquestador del pipeline, consolidación y exportación
└── README.md               # Documentación técnica del módulo
```

---

## 3. Campos del Dataset Extraído (`data/raw/`)

Los datos se exportan automáticamente en formato CSV y JSON estructurado:

| Campo | Tipo | Descripción |
| :--- | :---: | :--- |
| `id_origen` | string | Identificador único del producto en el catálogo de la farmacia. |
| `farmacia` | string | Cadena farmacéutica (`Farmacorp`, `Farmacias Chávez`). |
| `nombre_comercial` | string | Nombre y presentación comercial completa del fármaco. |
| `principio_activo` | string | Clasificación farmacológica (ej. *Insulina Glargina*, *Insulina Humana NPH*). |
| `marca_laboratorio` | string | Marca o laboratorio fabricante. |
| `precio_bs` | float | Precio final vigente en bolivianos (Bs.). |
| `precio_regular_bs`| float | Precio de lista sin descuento en bolivianos (Bs.). |
| `descuento_aplicado`| bool | Indicador booleano de descuento o promoción activa. |
| `estado_stock` | string | Estado de disponibilidad (`Disponible`, `Últimas unidades`, `Agotado`). |
| `sucursal` | string | Sucursal o red zonal de distribución en Santa Cruz. |
| `ciudad` | string | Ciudad objetivo (`Santa Cruz de la Sierra`). |
| `url_producto` | string | Enlace directo a la ficha del producto en la tienda virtual. |
| `timestamp` | datetime | Marca temporal de extracción (UTC / ISO 8601). |

---

## 4. Instrucciones de Ejecución

Para ejecutar la extracción completa de forma manual o programada:

```powershell
python src/scraping/main_scraper.py
```

Los resultados consolidados se almacenan en:
- `data/raw/insulina_precios_stock_latest.csv`
- `data/raw/insulina_precios_stock_latest.json`
- `data/raw/insulina_precios_stock_<YYYYMMDD_HHMMSS>.csv` (archivo histórico versionado)
