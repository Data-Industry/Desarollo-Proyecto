# SCRUM-46 (US-31) — Pulido Didáctico, Lenguaje Ciudadano y Semáforo Coherente del MVP (Versión 3.0)

**Fase CRISP-DM:** Fase 6 — Despliegue  
**Historia de Usuario:** `US-31` (`SCRUM-46`)  
**Story Points:** 5 SP  
**Estado:** Finalizada  
**Datasets Integrados:** `data/processed/insulinas_master.csv`, `data/processed/predicciones_probabilidad_stock.csv`, `data/processed/farmacias_geolocalizadas.csv`  
**Archivos Ejecutables Generados:**  
- `mvp_comparador_jubilados.html` (en la raíz del proyecto para acceso directo)  
- `src/ui/mvp_comparador_jubilados.html`  
- `docs/mvp_jubilados_comparador.html` (copia documental requerida por criterios de aceptación)  
- `ARTIFACT_HTML` oficial de la sesión  
**Script Generador:** `src/ui/generar_mvp_interactivo.py`  
**Suite de Pruebas Unitarias:** `src/models/test_04_mvp_jubilados.py` (7/7 pruebas aprobadas)  

---

## 1. Contexto de la Historia de Usuario y Feedback de Defensa

Durante la defensa del Sprint 3 y la evaluación del prototipo v2.0, se identificaron dos áreas de mejora críticas para la adopción real por parte de jubilados insulinodependientes y cuidadores en Santa Cruz de la Sierra:

1. **Brecha de Comprensión (Lenguaje excesivamente técnico):**  
   El visualizador incluía términos de ciencia de datos como *"Machine Learning"*, *"Modelo IA"*, *"Random Forest"* y *"Lag de importaciones"*, los cuales generaban confusión y desconfianza en adultos mayores jubilados sin formación informática.
2. **Incoherencia Semafórica en Casos con Stock Disponible:**  
   Debido a un umbral de alerta hiper-sensible optimizado para minimizar falsos negativos en salud pública, medicamentos que se encontraban físicamente disponibles en 2 cadenas farmacéuticas (ej. *Farmacorp* y *Farmacias Chávez*) figuraban con semáforo **ROJO (Alerta de Quiebre)** en la vista general. Esto contradecía la realidad del catálogo y desorientaba al usuario.

---

## 2. Mejoras Implementadas en la Versión 3.0

### 2.1. Eliminación de Tecnicismos y Lenguaje Ciudadano Accesible
- Se removieron por completo las referencias a *"Machine Learning"*, *"Random Forest"*, *"Variables Analíticas"* y *"Lag"* en la vista interactiva.
- Se adaptaron los títulos y descripciones a conceptos cotidianos y empáticos:
  - *Antes:* *"Semáforo de Abastecimiento Preventivo (Modelo IA)"*.
  - *Ahora:* *"Semáforo Preventivo de Disponibilidad en Farmacias"*.
  - *Antes:* *"Predicción basada en Machine Learning para anticipar quiebres y compras antes del pago de rentas"*.
  - *Ahora:* *"Monitoreo diario de existencias en farmacias para avisarte con anticipación si conviene comprar antes del cobro de rentas"*.

### 2.2. Nuevo Módulo: Glosario Ciudadano Interactivo
Se integró una sección destacada con 4 tarjetas didácticas explicativas:
1. **¿Qué es el "Quiebre de Stock"?:** Explicado de forma sencilla como la situación donde las farmacias agotan sus existencias y no pueden despachar de inmediato, justificando la importancia de comprar con días de anticipación.
2. **¿Cómo funciona el Semáforo?:** Aclaración explícita de que **si hay stock en al menos una farmacia, nunca marcará rojo**.
3. **¿Cómo se calcula el Ahorro?:** Explicación matemática clara: se resta el precio más caro menos el más barato para el mismo medicamento, mostrando el dinero que el jubilado conserva en su bolsillo.
4. **¿Qué significa "U-100"?:** Definición clínica de 100 Unidades Internacionales por mililitro y la recomendación de usar jeringas graduadas correspondientes.

### 2.3. Algoritmo Estricto de Coherencia Semafórica
Se rediseñó la lógica determinista del semáforo general por medicamento:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EVALUACIÓN DE DISPONIBILIDAD                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ¿Existen farmacias con stock activo?
                  (DISPONIBLE o ULTIMAS_UNIDADES)
                                    │
                   ┌────────────────┴────────────────┐
                   │ NO                              │ SÍ
                   ▼                                 ▼
      ┌─────────────────────────┐       ┌────────────────────────┐
      │          ROJO           │       │ ¿Hay señales de riesgo?│
      │   (Agotado General)     │       └───────────┬────────────┘
      │ Únicamente si el 100%   │                   │
      │ de farmacias está en    │         ┌─────────┴─────────┐
      │ AGOTADO (0 activas).    │         │ SÍ                │ NO
      └─────────────────────────┘         ▼                   ▼
                            ┌────────────────────────┐  ┌─────────────────────┐
                            │        AMARILLO        │  │        VERDE        │
                            │      (Precaución)      │  │ (Stock Asegurado)   │
                            │ • Pocas unidades       │  │ • Múltiples cadenas │
                            │ • Cadena única         │  │   con stock normal  │
                            │ • Agotado en una pero  │  │ • Sin alertas de    │
                            │   disponible en otra   │  │   escasez inmediata │
                            │ • Alta demanda de mes  │  └─────────────────────┘
                            └────────────────────────┘
```

#### Regla de Oro Implementada:
> **Bajo ninguna circunstancia un medicamento con una o más farmacias disponibles marcará ROJO.** El color rojo queda reservado estrictamente para medicamentos con stock agotado en la totalidad de las cadenas consultadas.

---

## 3. Distribución Resultante del Catálogo (24 Formulaciones Únicas)

Tras la aplicación de las reglas semafóricas coherentes, la distribución en Santa Cruz de la Sierra refleja fielmente la realidad del mercado:

| Semáforo | Total Formulaciones | Porcentaje | Comportamiento en Farmacias |
| :---: | :---: | :---: | :--- |
| **🟢 VERDE** | **12** | **50.0%** | Abastecimiento normal asegurado en múltiples cadenas (Novolin R, Novolin 70/30, Lantus vial, Lantus pluma, Humodar NPH, Humodar R, Humodar C25, Densulin N, Densulin R, Glaritus, Apidra pluma, Insugen regular). |
| **🟡 AMARILLO** | **11** | **45.8%** | Disponibles para compra, pero con advertencia preventiva: últimas unidades (Novolin N, Basalog, Toujeo vial), disponibilidad en una sola cadena (Densulent, Glinux N, Toujeo cartucho, Apidra vial/cartucho) o asimetría (Asparpen agotado en Farmacorp pero disponible en Chávez). |
| **🔴 ROJO** | **1** | **4.2%** | Únicamente **Insugen NPH (Vial 10 ml)** en Farmacorp, la cual se encuentra 100% agotada en catálogo sin stock activo reportado. |

---

## 4. Verificación y Pruebas Unitarias Automatizadas

La suite `src/models/test_04_mvp_jubilados.py` fue ampliada a **7 pruebas unitarias** que validan:
1. `test_01_compilacion_datos_reales_agrupados`: 24 formulaciones, 43 registros y 16 sucursales.
2. `test_02_estructura_comparativa_3_cadenas_y_metricas`: Precios, cadenas y atributos de cada fármaco.
3. `test_03_regla_estricta_semaforo_coherente_us31`: Comprobación matemática de que **ningún** medicamento disponible tiene semáforo rojo, que el rojo es exactamente 1 y que los verdes y amarillos tienen existencias activas.
4. `test_04_sucursales_geolocalizadas_y_anillos`: Integridad territorial por anillos (2, 3, 4, 7 y Centro).
5. `test_05_archivos_html_generados_y_sincronizados`: Existencia y peso (>20 kB) en las 4 rutas requeridas (`src/ui/`, raíz, `docs/` y artefacto).
6. `test_06_glosario_ciudadano_y_ausencia_tecnicismos`: Presencia de las 4 tarjetas del glosario y ausencia de cadenas crudas de *Machine Learning* o *Random Forest*.
7. `test_07_criterios_interactivos_y_accesibilidad_senior`: Controles de filtro, ordenamiento, calculadora de dosis, zoom de letra (`A-`/`A+`) y lectura por voz.

**Resultado de Ejecución:** `7/7 pruebas aprobadas (100% OK)` en 0.091 segundos.
