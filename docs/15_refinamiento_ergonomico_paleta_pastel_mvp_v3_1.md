# SCRUM-49 (US-34) — Refinamiento Ergonómico, Estética Farmacéutica Pastel y Pulido UI/UX (Versión 3.1)

**Fase CRISP-DM:** Fase 6 — Despliegue  
**Historia de Usuario:** `US-34` (`SCRUM-49`)  
**Story Points:** 5 SP  
**Asignado a:** Daniel Molina  
**Estado:** Finalizada  
**Datasets Integrados:** `data/processed/insulinas_master.csv`, `data/processed/predicciones_probabilidad_stock.csv`, `data/processed/farmacias_geolocalizadas.csv`  
**Archivos Ejecutables Generados:**  
- `mvp_comparador_jubilados.html` (raíz del proyecto para acceso directo)  
- `src/ui/mvp_comparador_jubilados.html`  
- `docs/mvp_jubilados_comparador.html` (copia documental requerida por criterios de aceptación)  
- `ARTIFACT_HTML` oficial de la sesión en `brain/`  
**Script Generador:** `src/ui/generar_mvp_interactivo.py`  
**Suite de Pruebas Unitarias:** `src/models/test_04_mvp_jubilados.py` (8/8 pruebas aprobadas)  

---

## 1. Contexto de la Historia de Usuario y Retroalimentación de Usuario

A partir de las pruebas de usabilidad y la retroalimentación cualitativa recabada en el Sprint 4 con adultos mayores y cuidadores en Santa Cruz de la Sierra, se identificaron oportunidades clave para perfeccionar la ergonomía cognitiva y visual del visualizador interactivo:

1. **Ambigüedad en los Botones de Zoom:**  
   Los botones rotulados como `A-` y `A+` resultaban abstractos para ciertos adultos mayores con escasa familiaridad digital, quienes dudaban de su función. Se solicitó explícitamente sustituirlos por términos directos en lenguaje natural: **"Achicar letra"** y **"Agrandar letra"**.
2. **Invasividad Espacial del Glosario:**  
   El módulo de glosario ciudadano ocupaba un bloque vertical muy grande en la pantalla (4 tarjetas completas fijas), desplazando hacia abajo las herramientas principales de consulta y compra.
3. **Pérdida de Relevancia de la Calculadora de Presupuesto:**  
   La calculadora de dosis y ahorro mensual se encontraba situada al pie de la página, por debajo de las 24 tarjetas del catálogo. Esto reducía su visibilidad y utilidad práctica para el jubilado.
4. **Redundancia del Botón de Filtrado:**  
   Dado que el catálogo realizaba un filtrado reactivo parcial en tiempo real, el botón *"Filtrar Catálogo"* parecía redundante o inoperante. Se solicitó que el botón tenga un propósito concreto y que se requiera presionar el botón o la tecla Enter para ejecutar el filtrado de forma deliberada.
5. **Estética Artificial ("Estilo IA"):**  
   El diseño previo empleaba sombras pesadas, bordes oscuros de alto contraste y gradientes saturados característicos de plantillas generadas por IA. El usuario solicitó una apariencia más limpia, humana, acogedora y profesional, con una **paleta pastel inspirada en farmacias modernas y salud**.

---

## 2. Soluciones Técnicas Implementadas en la Versión 3.1

### 2.1. Controles Accesibles de Zoom con Texto Explícito
Se reemplazaron los glifos minimalistas por botones accesibles con microiconografía y texto visible completo:
```html
<button id="btnFontMinus" onclick="ajustarFuente(-0.1)" title="Achicar tamaño de letra" aria-label="Achicar tamaño de letra">
  <span>🔍➖</span> Achicar letra
</button>
<span id="lblFontScale">100%</span>
<button id="btnFontPlus" onclick="ajustarFuente(0.1)" title="Agrandar tamaño de letra" aria-label="Agrandar tamaño de letra">
  <span>🔍➕</span> Agrandar letra
</button>
```
Se preservó el escalado real sobre `document.documentElement.style.fontSize`, permitiendo que todos los textos, espaciados y componentes de la aplicación crezcan proporcionalmente entre el 85% y el 150%.

### 2.2. Glosario Ciudadano Compacto y Desplegable (`#sec-glosario`)
Se transformó el contenedor estático en una barra delgada y elegante (~42px de alto en estado pasivo):
- Incluye el botón interactivo `📖 Glosario de Términos` (`id="btnToggleGlosario"`).
- Se activa al pasar el mouse (`onmouseenter`) o al hacer clic (`onclick="toggleGlosario()"`).
- Al desplegarse, muestra suavemente (`animate-fadeIn`) las 4 definiciones requeridas:
  1. *¿Qué es "Quiebre de stock"?*
  2. *¿Cómo funciona el Semáforo?*
  3. *¿Cómo se calcula tu Ahorro?*
  4. *¿Qué significa "U-100"?*
- Al cerrarse, libera el espacio visual inmediatamente para facilitar la navegación.

### 2.3. Reubicación Estratégica de la Calculadora de Ahorro (`#sec-calculadora`)
La Calculadora de Dosis Diaria y Presupuesto Mensual se trasladó a la parte superior de la página, **ubicándose inmediatamente antes del panel de búsqueda y catálogo de medicamentos**.
- Permite al jubilado calcular cuántos frascos o viales requerirá en el mes en base a su prescripción médica (ej. 30 UI/día) antes de revisar el catálogo.
- Calcula el ahorro mensual en Bolivianos entre cadenas de forma inmediata.

### 2.4. Coherencia en la Acción de Filtrado y Búsqueda
Se estableció un flujo deliberado de interacción:
1. Al modificar los selectores (`filtroPrincipio`, `filtroFormato`, `filtroFarmacia`) o escribir en `inputBusqueda`, el indicador de estado muestra:  
   `● Presiona "Filtrar Catálogo" para ver cambios` (animado y con resalte visual en el botón).
2. Presionar el botón `btnAplicarFiltros` o la tecla **Enter** en la barra de búsqueda aplica los criterios y actualiza el conteo y las tarjetas.
3. El botón `btnLimpiarFiltros` restablece instantáneamente todos los controles al catálogo general.

### 2.5. Paleta Farmacéutica Pastel y Diseño Limpio ("Anti-IA")
Se eliminaron las sombras excesivas y los gradientes oscuros, sustituyéndolos por colores suaves, naturales y clínicos:
- **Verde Salvia y Botánico:** Cabecera en `#1b4332`, acentos en `#2d6a4f` y bordes sutiles en `#e3eae5`.
- **Fondo Clínico Suave:** `#f7faf8`, reduciendo la fatiga ocular del adulto mayor.
- **Semáforo Pastel Suave:**
  - *Verde (Stock Seguro):* Fondo pastel menta `#ebf7ee`, texto `#1b5e20`, borde `#c3e6cb`.
  - *Amarillo (Precaución):* Fondo pastel manteca `#fef9e8`, texto `#855b0a`, borde `#fbe59d`.
  - *Rojo (Agotado General):* Fondo pastel rosáceo `#fdf2f2`, texto `#991b1b`, borde `#f8c8c8`.
- **Tarjetas Pastel:** Fondo blanco puro (`#ffffff`), borde delgado de 1px (`#e3eae5`) y micro-sombras naturales (`0 1px 3px rgba(0,0,0,0.03)`).

---

## 3. Matriz de Validación de Criterios de Aceptación

| Criterio de Aceptación (US-34) | Componente / Elemento | Estado de Verificación |
| :--- | :--- | :---: |
| **Texto explícito de zoom** | `btnFontMinus` ("Achicar letra"), `btnFontPlus` ("Agrandar letra") | ✅ Verificado en pruebas unitarias y DOM |
| **Glosario compacto interactivo** | `sec-glosario`, `btnToggleGlosario`, `toggleGlosario()`, 4 definiciones | ✅ Verificado en pruebas unitarias y DOM |
| **Calculadora previa al catálogo** | `pos_calculadora < pos_catalogo` en el documento HTML | ✅ Verificado (`test_08_refinamiento_ergonomico_paleta_pastel_us34`) |
| **Filtrado activo y coherente** | `btnAplicarFiltros`, `marcarFiltrosPendientes()`, Enter handler | ✅ Verificado en pruebas unitarias e interactividad |
| **Estética Pastel Farmacéutica** | Clases `card-pastel`, paleta salvia `#1b4332`, sin sombras pesadas | ✅ Verificado visualmente y en pruebas unitarias |
| **Sincronización de 4 archivos** | `src/ui/`, raíz, `docs/`, artefacto en `brain/` | ✅ Sincronizados y auditados (>20 KB cada uno) |
| **Compatibilidad con suites previas** | 83 pruebas unitarias (45 models + 38 ETL) | ✅ 83/83 pruebas aprobadas (100% OK) |

---

## 4. Conclusiones y Próximos Pasos

Con la culminación de `US-34` (`SCRUM-49`), el visualizador interactivo alcanza una madurez visual y ergonómica óptima para la población de adultos mayores en Santa Cruz de la Sierra.  
El siguiente paso en el **SCRUM Sprint 5** es `US-35` (`SCRUM-50`): **Despliegue Continuo (CI/CD) y Hosting Web Gratuito en Producción** para publicar la herramienta en la web pública a costo \$0.
