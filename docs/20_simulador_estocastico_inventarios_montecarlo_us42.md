# SCRUM-56 (US-42) — Simulación Estocástica de Inventarios de Insulina (Monte Carlo) y Controles Ergonómicos de Audio

**Fase CRISP-DM:** Fase 5 — Evaluación y Optimización Prescriptiva  
**Historia de Usuario:** `US-42` (`SCRUM-56`)  
**Story Points:** 5 SP  
**Asignado a:** Daniel Molina & Mía Arteaga  
**Sprint:** Sprint 6 (Sprint de Cierre y Preparación para Feria Universitaria)  
**Estado:** Finalizada  
**Fundamentación Bibliográfica Académica:**  
* García Dunna, E., García Reyes, H., & Cárdenas Barrón, L. E. (2013). *Simulación y análisis de sistemas con ProModel* (2.ª ed.). Pearson Educación.  
  - **Capítulo 4.3.3:** *Modelo de un sistema de inventarios* (págs. 142–146).  
  - **Capítulo 5.5:** *Arribos cíclicos y cuellos de botella temporales* (págs. 186–190).  
**URL Pública Oficial:** [https://data-industry.github.io/Desarollo-Proyecto/](https://data-industry.github.io/Desarollo-Proyecto/)  
**Módulos Desarrollados:**  
1. `src/optimization/simulador_montecarlo_paciente.py` (Motor estocástico en Python, 1.000 réplicas, IC 95%).  
2. `src/optimization/test_simulador_montecarlo.py` (8/8 pruebas unitarias).  
3. `src/models/test_07_audio_y_simulacion_web.py` (6/6 pruebas unitarias de integración web).  
4. `src/ui/generar_mvp_interactivo.py` y HTMLs (`index.html`, `docs/index.html`, `mvp_comparador_jubilados.html`).  
**Cobertura Global del Proyecto:** 141/141 pruebas unitarias aprobadas (100% de éxito).

---

## 1. Justificación y Planteamiento del Problema

En la defensa académica y en la validación con adultos mayores, el cálculo de inventario de medicamentos crónicos no puede tratarse como un modelo determinista estático ($Duración = Capacidad / Dosis$). En la práctica clínica y geriátrica real:
1. **Consumo estocástico variable:** Los pacientes con diabetes insulinodependiente ajustan sus unidades diarias según su glucemia capilar, ingesta de carbohidratos, episodios de estrés o infecciones intercurrentes, presentando variabilidad $\sigma_D > 0$.
2. **Riesgo crítico de desabastecimiento personal:** Quedarse sin insulina una noche o fin de semana representa una emergencia médica de cetoacidosis diabética o hiperglucemia severa.
3. **El cuello de botella de cobro de pensiones en Santa Cruz:** Los jubilados cobran su pensión de vejez en el Banco Unión entre los días 1 y 5 de cada mes. Ir a la farmacia en esos días implica colas masivas, agotamiento físico y desabastecimiento puntual en sucursales céntricas. Por otro lado, comprar a fin de mes conlleva riesgo de falta de stock en importaciones.

Para aportar un **valor científico y de ingeniería genuino**, se implementó un **Simulador Estocástico de Monte Carlo para Inventario de Paciente**, complementado con **controles ergonómicos de voz accesibles** (botón de parada inmediata y regulador de velocidad de audio).

---

## 2. Formulación Ágil de la Historia de Usuario

### Formulación (US-42 / SCRUM-56)
* **Como** Adulto mayor jubilado o cuidador en Santa Cruz de la Sierra,
* **Quiero** simular con qué probabilidad y en qué fecha exacta se me agotará mi frasco de insulina considerando variaciones en mi dosis diaria, y contar con controles para detener el audio o acelerarlo (x1, x1.5, x2),
* **Para** saber el día óptimo para reabastecerme sin hacer colas bancarias ni quedarme sin medicamento, teniendo una experiencia auditiva cómoda sin lecturas molestas accidentales.

### Criterios de Aceptación Cumplidos:
- [x] **CA-1 (Motor Monte Carlo):** Ejecutar al menos 1.000 iteraciones estocásticas con distribución normal truncada ($Box-Muller$) y calcular media, desviación estándar e intervalo de confianza al 95%.
- [x] **CA-2 (Punto de Reorden y Día Óptimo):** Determinar el nivel de reserva de seguridad ($s$) y recomendar un día calendario de compra que evite los días 1–5 (colas de cobro en Banco Unión) y los días 28–31 (quiebre de inventario mensual).
- [x] **CA-3 (Botón Detener Audio):** Al lado de cada botón de escucha de audio (en cabecera, tarjetas de fármacos y chatbot), habilitar un botón de parada inmediata (`⏹️ Detener`) que cancele `speechSynthesis`.
- [x] **CA-4 (Velocidad de Reproducción):** Añadir botones selectores de velocidad (`1x`, `1.5x`, `2x`) accesibles visualmente.
- [x] **CA-5 (Rendimiento Client-Side):** La simulación de 1.000 réplicas en JavaScript en el navegador del jubilado se ejecuta en menos de 15 milisegundos sin consumir datos ni depender de servidores backend.

---

## 3. Modelo Matemático y Metodología (García Dunna et al., 2013)

```mermaid
flowchart TD
    subgraph Parámetros del Paciente
        Cap["Capacidad Frasco (ej. 1000 UI)"]
        Dosis["Dosis Diaria Media μ (ej. 30 UI)"]
        Var["Variabilidad Diaria σ (ej. 3 UI)"]
    end

    subgraph Generador Estocástico Box-Muller
        RND["Variables Uniformes U1, U2 ~ U(0,1)"]
        Z0["Z0 = sqrt(-2 ln U1) * cos(2π U2)"]
        Dt["Consumo Diario: Dt = max(0.5, μ + Z0 * σ)"]
    end

    subgraph Simulación Monte Carlo (R = 1000)
        Loop["Bucle Diario: Inv(t) = Inv(t-1) - Dt"]
        Stockout["Condición de Agotamiento: Inv(t) <= 0 -> Registrar Día T_r"]
    end

    subgraph Estadísticos de Decisión
        Media["Duración Esperada: T_prom = Σ T_r / 1000"]
        IC["Intervalo de Confianza 95%: [T - 1.96*SE, T + 1.96*SE]"]
        Reorden["Punto de Reorden de Seguridad: s = μ * L + 1.645 * σ_L"]
        DiaOptimo["Día Óptimo de Compra (Evita Días 1-5 de Banco Unión)"]
    end

    Cap & Dosis & Var --> RND
    RND --> Z0 --> Dt
    Dt --> Loop --> Stockout
    Stockout --> Media & IC & Reorden --> DiaOptimo
```

### 3.1. Ecuaciones del Sistema de Inventario
Sea $I_t$ el inventario remanente de insulina en unidades internacionales (UI) en el día $t$, con $I_0 = C$ (capacidad inicial del frasco, típicamente 1.000 UI en viales de 10 ml o 300 UI en plumas tipo Solostar/KwikPen).

El consumo diario $D_t$ se modela estocásticamente como una variable aleatoria normal truncada en $D_{min} = 0.5 \text{ UI}$:
$$D_t \sim \max\left(0.5, \; \mu_D + \sigma_D \cdot Z\right), \quad Z \sim \mathcal{N}(0, 1)$$

Donde $Z$ se genera computacionalmente mediante la transformación de Box-Muller:
$$Z = \sqrt{-2 \ln(U_1)} \cos(2\pi U_2), \quad U_1, U_2 \sim \mathcal{U}(0, 1)$$

La ecuación de transición de estado es:
$$I_t = \max(0, \; I_{t-1} - D_t)$$

El tiempo de agotamiento del frasco $T$ para la réplica $r$ es:
$$T_r = \min \{ t \in \mathbb{N} : I_t = 0 \}$$

### 3.2. Estimación Puntual y por Intervalo (1.000 Réplicas)
Para $R = 1.000$ réplicas independientes:
- **Media muestral:** $\bar{T} = \frac{1}{R} \sum_{r=1}^{R} T_r$
- **Varianza muestral:** $S^2 = \frac{1}{R - 1} \sum_{r=1}^{R} (T_r - \bar{T})^2$
- **Error estándar:** $SE = \frac{S}{\sqrt{R}}$
- **Intervalo de confianza al 95%:** 
  $$IC_{95\%}(T) = \left[ \bar{T} - 1.96 \cdot SE, \; \bar{T} + 1.96 \cdot SE \right]$$

### 3.3. Determinación del Punto de Reorden y Política de Compra
Siguiendo el modelo de inventarios con demanda estocástica y tiempo de entrega ($L = 3 \text{ días}$ promedio de reposición):
$$s = \mu_D \cdot L + z_{0.95} \cdot \sigma_D \sqrt{L}$$

Donde $z_{0.95} \approx 1.645$ garantiza un 95% de nivel de servicio (probabilidad de desabastecimiento $\le 5\%$).

Para la fecha de compra, el algoritmo cruza la fecha crítica de alerta con el calendario mensual de Santa Cruz:
- Si el día de reorden coincide con el rango crítico de cobro de pensiones en el Banco Unión (días 1 a 5 de mes), el sistema adelanta la recomendación de compra al día 28 del mes anterior o la posterga con reserva de seguridad al día 6, protegiendo al jubilado del esfuerzo físico de las aglomeraciones.

---

## 4. Mejoras Ergonómicas de Accesibilidad en Audio

Para resolver las observaciones de usabilidad donde un clic involuntario forzaba al usuario a escuchar la locución completa:
1. **Botón `⏹️ Detener`:** Integrado con `window.speechSynthesis.cancel()` en:
   - Cabecera principal (`#btnDetenerAudioHeader`).
   - Cabecera del Chatbot flotante (`#btnDetenerChatHeader`).
   - Cada tarjeta de medicamento comparado (`.btn-card-audio-stop`).
   - Cada mensaje emitido por el bot conversacional.
2. **Píldoras de Velocidad (`1x`, `1.5x`, `2x`):** Modifican dinámicamente `utterance.rate`, guardando el estado en `window.velocidadAudioActual` con realce visual del botón activo.

---

## 5. Resultados de Validación y Suites de Pruebas

```
----------------------------------------------------------------------
Ran 8 tests in 0.099s (src/optimization/test_simulador_montecarlo.py) -> OK
Ran 6 tests in 0.006s (src/models/test_07_audio_y_simulacion_web.py)  -> OK
Ran 141 tests in 9.422s (Suite Integral del Proyecto)                -> OK (100%)
----------------------------------------------------------------------
```

| Componente | Métrica / Resultado | Estado |
| :--- | :--- | :---: |
| **Tiempo de Simulación (1.000 corridas)** | < 12 ms en navegador cliente | Cumplido |
| **Consumo de Ancho de Banda** | 0 KB adicionales (cálculo en JavaScript local) | Cumplido |
| **Control de Detención de Voz** | Cancelación instantánea en < 50 ms | Cumplido |
| **Protección Banco Unión** | Sugiere día seguro evitando días 1-5 | Cumplido |
| **Trazabilidad Git** | `Libro optimización/` 100% excluido por `.gitignore` | Verificado |

---

## 6. Conclusión y Valor para la Defensa Académica

Esta implementación demuestra la capacidad del equipo para articular conceptos de **Modelos y Optimización / Teoría de Colas y Simulación de Sistemas** directamente con el producto tecnológico interactivo. No se limitó a un cálculo académico aislado, sino que se integró de forma transparente y accesible en la interfaz web pública a costo cero.
