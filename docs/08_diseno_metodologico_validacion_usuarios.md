# SCRUM-47 (US-32) — Diseño metodológico de validación con usuarios

**Fase CRISP-DM:** Evaluación

**Historia de usuario:** `US-32` (`SCRUM-47`)

**Tipo de entrega:** Diseño de instrumentos y protocolo de aplicación

**MVP de referencia:** `mvp_comparador_jubilados.html` y su copia idéntica en `src/ui/mvp_comparador_jubilados.html`

**Estado de la validación:** Diseñada, todavía no aplicada

> Este documento define cómo se realizará una futura validación con usuarios. No presenta resultados, participantes reclutados, entrevistas realizadas ni puntuaciones SUS obtenidas. La aplicación, tabulación y elaboración de conclusiones corresponderán a `SCRUM-48` (`US-33`).

## 1. Objetivo

### 1.1 Objetivo general

Diseñar un protocolo claro, ético y repetible para evaluar con adultos mayores jubilados insulinodependientes de Santa Cruz de la Sierra la usabilidad percibida y la comprensión del MVP comparador de insulinas que existe actualmente.

La evaluación propuesta se concentra en:

- facilidad para buscar una insulina;
- comprensión de los filtros y resultados;
- interpretación de precios y ahorro;
- diferenciación entre estado de stock y semáforo predictivo;
- uso del directorio de sucursales por anillo, sin atribuirle disponibilidad de productos;
- usabilidad percibida mediante la Escala de Usabilidad del Sistema (SUS);
- confianza, barreras e intención declarada de volver a usar el MVP.

### 1.2 Preguntas de validación

1. ¿Puede el participante encontrar una insulina y su presentación dentro del catálogo sin ayuda?
2. ¿Comprende los filtros por tipo, presentación y cadena farmacéutica?
3. ¿Puede identificar el menor precio y el ahorro mostrado cuando existen registros comparables?
4. ¿Distingue el precio total del precio normalizado por 100 UI?
5. ¿Distingue el estado actual de catálogo (`DISPONIBLE`, `ULTIMAS_UNIDADES` o `AGOTADO`) del semáforo predictivo?
6. ¿Qué significado atribuye a los colores verde, amarillo y rojo?
7. ¿Comprende que el filtro por anillo muestra sucursales, pero no confirma stock de una insulina en esas sucursales?
8. ¿Puede usar los controles de tamaño de fuente y, si lo desea, la lectura por voz?
9. ¿Qué elementos aumentan o reducen la confianza en la información presentada?
10. ¿Usaría el MVP nuevamente y en qué situación?

### 1.3 Alcance y exclusiones

El protocolo evalúa usabilidad, comprensión, facilidad de búsqueda, interpretación de precios, comprensión del semáforo e intención de uso. Las métricas se interpretarán junto con las observaciones y respuestas abiertas; ninguna métrica aislada determinará por sí sola la aceptación del MVP.

Este estudio **no evalúa**:

- precisión médica, seguridad clínica o eficacia terapéutica;
- adecuación de dosis, número de aplicaciones o cambios de tratamiento;
- exactitud real o en tiempo real del inventario de una farmacia;
- vigencia comercial garantizada de los precios;
- precisión estadística, calibración o desempeño predictivo del modelo;
- impacto clínico, adherencia al tratamiento o resultados de salud;
- representatividad estadística de la población de jubilados de Santa Cruz;
- disponibilidad de una insulina por sucursal o por anillo.

## 2. Usuario objetivo

### 2.1 Usuario principal

El usuario principal definido por el proyecto es el adulto mayor jubilado con diabetes insulinodependiente, residente en Santa Cruz de la Sierra, que necesita adquirir insulina de forma periódica.

Esta definición identifica el segmento al que se dirige el MVP. No implica que todas las personas del segmento tengan las mismas capacidades, hábitos, barreras o experiencias de compra.

### 2.2 Usuario secundario

El usuario secundario es el familiar o cuidador que consulta información o participa en la compra de insulina para un adulto mayor. Si se incluye en la prueba piloto, sus resultados se analizarán como un grupo separado y no se mezclarán automáticamente con los del usuario principal.

### 2.3 Características definidas por el proyecto

Los documentos del proyecto establecen que el usuario principal:

- reside en Santa Cruz de la Sierra;
- utiliza insulina y necesita conseguirla periódicamente;
- enfrenta incertidumbre sobre qué farmacia puede tener el producto;
- puede consultar o visitar más de una farmacia;
- puede recibir apoyo de familiares o cuidadores;
- podría beneficiarse de información consolidada sobre precios, estados de stock y sucursales;
- forma parte de un segmento para el cual se busca una interfaz clara, con letra ajustable y lenguaje comprensible.

El proyecto también plantea como posibles barreras la movilidad reducida y la dificultad para usar portales digitales complejos. Estas características no deben generalizarse a todos los adultos mayores.

### 2.4 Supuestos que todavía deben validarse

La prueba deberá explorar, sin tratarlos previamente como hechos:

- frecuencia real de compra y de desabastecimiento;
- cantidad de farmacias consultadas o visitadas;
- tiempo y costos dedicados a buscar insulina;
- persona que realiza habitualmente la compra;
- acceso a teléfono, computadora e Internet;
- nivel de familiaridad con buscadores, filtros y formularios;
- posibles barreras visuales, auditivas o motoras;
- reconocimiento de marca, principio activo y presentación;
- familiaridad con los anillos urbanos;
- grado de confianza en precios y estados obtenidos de sitios web;
- necesidad de ayuda para utilizar el comparador;
- intención de incorporar el MVP a una compra real.

## 3. Qué se evalúa del MVP

La prueba se realizará sobre una copia identificada y congelada del MVP. Antes de cada sesión se registrarán nombre del archivo, fecha de modificación, navegador, dispositivo, tamaño de pantalla y fecha de aplicación. Si el MVP cambia después de diseñado este protocolo, se revisarán las tareas antes de continuar con el trabajo de campo.

### 3.1 Funcionalidades y significado real

| Funcionalidad | Qué hace realmente | Qué NO significa |
|---|---|---|
| Buscador por texto | Filtra las 24 formulaciones embebidas por coincidencia parcial de marca, principio activo o laboratorio. | No busca fuera del catálogo, no corrige errores de escritura y no consulta farmacias en vivo. |
| Filtro por tipo de insulina | Reduce las tarjetas mediante coincidencias con el principio activo o marca. | No recomienda una insulina ni verifica que sea equivalente a la prescrita. |
| Filtro por presentación | Filtra por vial, cartucho o lapicero, según el texto almacenado. | No confirma compatibilidad con dispositivos ni indicación médica. |
| Filtro por cadena | Conserva productos que tienen un registro de catálogo para la cadena elegida. | No garantiza que el producto esté disponible; puede existir un registro cuyo estado sea `AGOTADO`. |
| Comparación de precios | Muestra registros de hasta tres cadenas y calcula el menor precio, el mayor y su diferencia. | No garantiza vigencia del precio ni que el menor precio corresponda a stock comprable. |
| Precio por 100 UI | Presenta una normalización económica para facilitar comparación. | No representa una dosis recomendada ni el costo clínico del tratamiento. |
| Estado de stock | Muestra categorías embebidas: `DISPONIBLE`, `ULTIMAS_UNIDADES` o `AGOTADO`. | No indica cantidad física, sucursal específica ni inventario en tiempo real. |
| Semáforo por medicamento | Resume señales predictivas asociadas a los registros agrupados. | No es diagnóstico, garantía de stock ni sustituto del estado actual de catálogo. |
| Semáforo global y textos explicativos | Presenta un estado general y tarjetas informativas verde, amarilla y roja. | Sus conteos y mensajes actuales son textos estáticos; no deben interpretarse como recálculo en tiempo real. |
| Directorio por anillos | Filtra una lista embebida de 16 sucursales por Centro o por los anillos 2, 3, 4 y 7. | No relaciona producto con sucursal o anillo, no muestra stock por anillo y no calcula distancia real. |
| “Farmacia más cercana” | Permite visualizar sucursales agrupadas por la etiqueta de anillo. | No usa la ubicación del participante, no calcula rutas y no demuestra cuál es la farmacia más cercana. |
| Calculadora | Estima frascos para 30 días y diferencia mensual de precios a partir de una dosis introducida y seis opciones de insulina. | No prescribe dosis, no valida tratamiento y no asegura que los productos usados en el cálculo estén disponibles. |
| Tamaño de fuente | Aumenta o reduce proporcionalmente el tamaño base del documento dentro de un rango. | No resuelve todas las necesidades de accesibilidad ni sustituye una evaluación visual individual. |
| Lectura por voz | Lee un resumen predeterminado si el navegador admite síntesis de voz. | No lee todo el contenido, no verifica comprensión y depende del navegador. |
| Reserva o compra | No existe. | El MVP no reserva, vende, paga ni confirma pedidos. |

### 3.2 Limitaciones que condicionan la prueba

- Los datos están embebidos en el HTML y no se actualizan durante la sesión.
- No existe inventario en tiempo real ni stock cuantitativo.
- No existe una relación verificable `producto → sucursal → anillo`.
- La presencia de una cadena en una tarjeta no equivale necesariamente a disponibilidad.
- El cálculo de ahorro considera los precios registrados aunque alguno corresponda a un estado agotado.
- El semáforo predictivo es experimental y puede diferir del estado actual de stock.
- La regla actual puede producir una alerta roja para un medicamento que figura disponible en una o más cadenas.
- El estado global, los conteos por color y algunos mensajes preventivos son estáticos y pueden no coincidir con las tarjetas.
- Algunas sucursales sin evidencia suficiente o con ubicación ambigua se presentan dentro de la categoría Centro.
- El estado visual “Activa” de las sucursales es fijo y no constituye verificación operativa en tiempo real.
- El diseño visual carga Tailwind CSS desde un recurso externo; por ello, la presentación completa puede depender de Internet aunque los datos estén embebidos.
- La interfaz no muestra al usuario la fecha de extracción de precios y stock.
- Frases como “abastecimiento asegurado”, “garantizado” o “acudir con confianza” no deben repetirse por el moderador como afirmaciones verificadas.

Estas limitaciones no se corregirán dentro de `SCRUM-47`; se registrarán para evitar interpretaciones incorrectas y para atribuir adecuadamente los problemas observados al MVP, al protocolo o al contexto.

## 4. Diseño de la prueba

### 4.1 Enfoque metodológico

Se propone una evaluación moderada de métodos mixtos:

- **Cuantitativa exploratoria:** éxito, finalización independiente, tiempo, errores, ayudas, respuestas SUS, comprensión e intención de uso.
- **Cualitativa:** observación de dificultades, comentarios espontáneos y entrevista semiestructurada.

La combinación permite saber no solo si una tarea se completa, sino también por qué resulta clara o difícil. El diseño es exploratorio y no experimental: no asigna tratamientos, no compara grupos al azar y no permite atribuir causalidad.

### 4.2 Orden de una sesión

1. Bienvenida y explicación general.
2. Lectura y aceptación del consentimiento informado.
3. Preguntas iniciales de perfil y contexto de compra.
4. Tareas guiadas de búsqueda, comparación, semáforo y anillos.
5. Aplicación completa de SUS.
6. Entrevista final sobre comprensión, confianza e intención de uso.
7. Cierre, agradecimiento y recordatorio de los límites del MVP.

### 4.3 Duración y condiciones

La duración estimada por sesión es de **25 a 35 minutos**, sin contar descansos. La sesión puede extenderse si el participante necesita leer con calma o solicitar una pausa; la velocidad no debe imponerse como condición de participación.

Se procurará:

- un lugar tranquilo, iluminado y con asiento cómodo;
- el dispositivo previsto para el uso real o, si no se conoce, el mismo dispositivo para todos los participantes de una ronda;
- navegador y versión registrados;
- notificaciones desactivadas;
- una copia del MVP sin datos personales;
- hoja de registro preparada antes de comenzar;
- cronómetro silencioso no visible como mecanismo de presión.

### 4.4 Rol del moderador y mínima intervención

El moderador deberá leer instrucciones estandarizadas, observar, registrar y cuidar el bienestar del participante. No deberá enseñar la solución, mover el cursor, señalar el control correcto ni reformular una pregunta de modo que revele la respuesta.

Cuando el participante se detenga, se utilizará esta secuencia:

1. esperar unos segundos sin intervenir;
2. usar una invitación neutral: “Cuénteme qué está buscando”;
3. repetir literalmente la instrucción;
4. ofrecer una orientación general, sin nombrar el control;
5. si es necesario para continuar, indicar el control concreto y registrar una ayuda directa.

Toda intervención posterior a la instrucción se contabilizará según el esquema de ayudas de la sección 7. La sesión debe comenzar con la frase: **“Estamos evaluando el comparador, no a usted. Si algo resulta difícil, esa dificultad nos ayuda a mejorar el producto.”**

## 5. Escala de Usabilidad del Sistema (SUS)

### 5.1 Propósito e instrucciones

SUS es un cuestionario de diez afirmaciones que produce una medida global de usabilidad percibida. Se aplicará inmediatamente después de las tareas, cuando la experiencia de uso todavía sea reciente. No mide precisión médica, calidad del inventario ni exactitud predictiva.

El moderador dirá:

> A continuación leeré diez afirmaciones sobre el comparador. Para cada una, indique cuánto está de acuerdo o en desacuerdo. Responda pensando en lo que acaba de usar. No hay respuestas correctas o incorrectas.

Si el participante solicita lectura, el moderador podrá leer cada reactivo y las cinco opciones exactamente como están escritas, sin explicar su polaridad ni sugerir una respuesta. Deben contestarse los diez reactivos. Ante duda, puede elegirse la opción central.

### 5.2 Escala de respuesta

| Valor | Respuesta |
|---:|---|
| 1 | Totalmente en desacuerdo |
| 2 | En desacuerdo |
| 3 | Ni de acuerdo ni en desacuerdo |
| 4 | De acuerdo |
| 5 | Totalmente de acuerdo |

### 5.3 Reactivos adaptados

La adaptación conserva el concepto y la alternancia positiva/negativa de SUS. Se sustituye “sistema” por “comparador” y se simplifica el vocabulario sin cambiar el sentido metodológico.

| N.º | Polaridad | Concepto original | Reactivo para aplicar |
|---:|---|---|---|
| 1 | Positiva | Uso frecuente | Creo que usaría este comparador cada vez que necesite buscar insulina. |
| 2 | Negativa | Complejidad innecesaria | Este comparador me pareció más complicado de lo que debería ser. |
| 3 | Positiva | Facilidad de uso | Me resultó fácil usar este comparador. |
| 4 | Negativa | Necesidad de apoyo | Necesitaría ayuda de alguien que sepa usar tecnología para utilizar este comparador. |
| 5 | Positiva | Integración de funciones | La búsqueda, los precios y la información de farmacias están bien organizados entre sí. |
| 6 | Negativa | Inconsistencia | Encontré información o controles que no parecían concordar entre sí. |
| 7 | Positiva | Facilidad de aprendizaje | Creo que la mayoría de las personas aprendería a usar este comparador rápidamente. |
| 8 | Negativa | Uso engorroso | Me resultó incómodo o difícil avanzar dentro del comparador. |
| 9 | Positiva | Confianza durante el uso | Me sentí seguro de saber qué hacer mientras usaba el comparador. |
| 10 | Negativa | Aprendizaje previo | Necesitaría aprender muchas cosas antes de poder usar bien este comparador. |

Los ítems positivos son 1, 3, 5, 7 y 9. Los negativos son 2, 4, 6, 8 y 10. No se cambiará el orden ni se eliminarán reactivos durante la aplicación.

### 5.4 Cálculo

Para cada participante:

1. En los ítems positivos 1, 3, 5, 7 y 9, calcular `respuesta − 1`.
2. En los ítems negativos 2, 4, 6, 8 y 10, calcular `5 − respuesta`.
3. Sumar las diez contribuciones transformadas. El resultado estará entre 0 y 40.
4. Multiplicar la suma por `2,5`.

La fórmula puede expresarse como:

`SUS = 2,5 × [Σ(respuesta impar − 1) + Σ(5 − respuesta par)]`

El puntaje final estará entre 0 y 100. No es un porcentaje de tareas correctas.

### 5.5 Ejemplo numérico ficticio de cálculo

El siguiente ejemplo solo explica el procedimiento; no representa a un participante real:

| Ítem | Respuesta ficticia | Transformación | Contribución |
|---:|---:|---|---:|
| 1 | 4 | 4 − 1 | 3 |
| 2 | 2 | 5 − 2 | 3 |
| 3 | 4 | 4 − 1 | 3 |
| 4 | 3 | 5 − 3 | 2 |
| 5 | 4 | 4 − 1 | 3 |
| 6 | 2 | 5 − 2 | 3 |
| 7 | 4 | 4 − 1 | 3 |
| 8 | 2 | 5 − 2 | 3 |
| 9 | 4 | 4 − 1 | 3 |
| 10 | 3 | 5 − 3 | 2 |
| **Total** |  |  | **28** |

`28 × 2,5 = 70`.

### 5.6 Interpretación prudente

Un puntaje mayor indica una percepción global de mayor usabilidad, pero no explica por sí solo qué parte del MVP funcionó o falló. Se interpretará junto con tareas, errores, ayudas y entrevistas.

En una muestra piloto pequeña se reportarán los puntajes individuales, la mediana, el promedio, el rango y, cuando sea útil, la desviación estándar. Los valores de referencia publicados pueden servir como contexto descriptivo, pero no como umbral automático de aprobación. No se crearán subescalas de “usabilidad” y “aprendizaje” ni se afirmará validación psicométrica de la adaptación con esta muestra.

## 6. Entrevista semiestructurada

Las preguntas se formularán de manera abierta y neutral. El moderador no asumirá que el participante sufrió desabastecimiento, que tiene baja habilidad digital ni que el MVP le resultó útil.

### A. Perfil y contexto de compra

1. Cuénteme cómo consigue normalmente la insulina que necesita.
2. ¿Cada cuánto tiempo suele necesitar conseguirla?
3. ¿Quién suele buscar información y quién suele realizar la compra?
4. ¿Cómo decide a qué farmacia consultar o ir?
5. En una compra habitual, ¿cuántas farmacias suele consultar o visitar?
6. ¿Qué dificultades, si alguna, encuentra durante la compra?
7. ¿Qué medio utiliza para buscar información antes de salir de casa?
8. ¿Suele usar teléfono, computadora u otro medio para estas consultas? ¿Cómo le resulta?

### B. Experiencias de desabastecimiento

1. ¿Le ha ocurrido alguna vez que no encuentra la insulina que busca? Si desea, cuénteme qué pasó.
2. ¿Con qué frecuencia recuerda que ocurre?
3. ¿Qué hace cuando la primera farmacia consultada no tiene el producto?
4. ¿Cuánto tiempo suele dedicar a buscarlo?
5. ¿Qué gastos o dificultades prácticas le genera la búsqueda?
6. ¿Recibe ayuda de otra persona cuando no encuentra el producto? ¿Cómo es esa ayuda?
7. ¿Qué información habría sido útil en esa situación?

No se solicitarán detalles clínicos sobre interrupciones, síntomas o consecuencias médicas, salvo que el participante los mencione espontáneamente. El moderador no profundizará en información clínica innecesaria.

### C. Uso del MVP

1. ¿Cómo decidió dónde buscar la insulina dentro del comparador?
2. ¿Qué parte de la búsqueda le resultó clara y qué parte no?
3. ¿Cómo interpretó los precios que aparecieron en la tarjeta?
4. ¿Qué entiende por “precio por 100 UI”?
5. ¿Qué entiende por “ahorro máximo”?
6. Con sus propias palabras, ¿qué cree que significa el semáforo?
7. ¿Qué diferencia observa entre el semáforo y las palabras “disponible”, “últimas unidades” o “agotado”?
8. ¿Qué entendió cuando seleccionó un anillo?
9. ¿Qué información necesitaría antes de decidir ir a una farmacia?
10. ¿Qué elementos le hacen confiar o desconfiar de la información mostrada?
11. ¿Cómo le resultaron el tamaño de letra y la organización de la página?
12. Si probó la lectura por voz, ¿cómo le resultó?

### D. Disposición de uso

1. ¿En qué situación, si alguna, usaría este comparador?
2. ¿Lo usaría nuevamente? ¿Por qué?
3. ¿Preferiría usarlo solo o con ayuda? ¿Por qué?
4. ¿En qué dispositivo le resultaría más cómodo?
5. ¿Qué sería lo primero que cambiaría?
6. ¿Qué información le faltó?
7. ¿Qué podría hacerle desconfiar o dejar de usarlo?

### E. Preguntas neutrales de profundización

Estas preguntas pueden utilizarse sin sugerir una respuesta:

- ¿Podría contarme un poco más?
- ¿Qué quiso decir con eso?
- ¿Qué esperaba que ocurriera?
- ¿Qué fue lo que observó en la pantalla?
- ¿Cómo llegó a esa conclusión?
- ¿Qué palabra o elemento le hizo pensar eso?
- ¿Hay otra cosa que le haya llamado la atención?

Se evitarán preguntas inductivas como “¿Le pareció fácil?”, “¿Verdad que el semáforo ayuda?” o “¿Usaría esta útil aplicación?”.

## 7. Prueba de tareas guiadas (*Task Testing*)

### 7.1 Reglas generales de registro

- El cronómetro comienza al terminar de leer la instrucción y se detiene cuando el participante comunica la respuesta, abandona o alcanza el cierre operativo.
- Los tiempos sugeridos son referencias para cuidar la duración, no criterios públicos de presión ni umbrales de calidad.
- Si el producto habitual no existe o una tarea requiere datos que el MVP no ofrece, se registra `causa_no_evaluable`; no se cuenta como fallo del participante.
- Un error inducido por información contradictoria del MVP se registra como problema de interfaz, no como incapacidad del participante.
- Las citas textuales se anotan sin nombre ni otro identificador.

Escala de ayudas:

| Nivel | Tipo de ayuda | Ejemplo |
|---:|---|---|
| 0 | Sin ayuda | El participante continúa por cuenta propia. |
| 1 | Invitación neutral | “Cuénteme qué está buscando.” |
| 2 | Repetición | Se repite literalmente la instrucción. |
| 3 | Orientación general | “Puede revisar los controles de esta sección.” |
| 4 | Ayuda directa | Se indica el control o paso concreto. |

Resultado de tarea: `completó solo`, `completó con ayuda`, `no completó` o `no evaluable`.

### 7.2 Matriz de tareas

| Campo | Tarea 1 — Buscar una insulina habitual | Tarea 2 — Identificar menor precio y ahorro | Tarea 3A — Interpretar semáforo | Tarea 3B — Filtrar sucursales por anillo |
|---|---|---|---|---|
| Objetivo | Evaluar búsqueda y reconocimiento de marca y presentación. | Evaluar lectura comparativa de cadena, precio y ahorro. | Evaluar el significado atribuido al color y su diferenciación respecto al stock actual. | Evaluar el uso del filtro territorial como directorio de sucursales. |
| Instrucción exacta | “Busque la insulina que utiliza habitualmente y muéstreme la presentación que compraría.” | “En esta tarjeta, indíqueme qué farmacia muestra el precio más bajo, cuánto cuesta y cuánto dice que ahorraría frente al precio más alto.” | “Observe el semáforo de esta insulina. ¿Qué cree que significa y qué haría con esa información?” | “Seleccione el anillo que le indicaré y muéstreme qué sucursales aparecen.” |
| Escenario alternativo | Si el producto no está en el catálogo: “Ahora busque Novolin N en frasco de 10 ml.” | Si el producto anterior solo tiene una cadena o no permite ahorro, usar la tarjeta de Novolin N como escenario común. | Si no hay una tarjeta seleccionada, utilizar la tarjeta empleada en la tarea 2. | Si el participante no conoce su anillo o este no figura, asignar el “3er Anillo” como escenario común. |
| Criterio de éxito | Localiza la marca y presentación solicitadas y muestra la tarjeta correspondiente. | Indica correctamente la cadena, el precio menor y el ahorro mostrado cuando existe. | Explica que el color comunica riesgo o alerta y no constituye garantía de disponibilidad ni diagnóstico. | Aplica el filtro indicado y localiza al menos una sucursal listada. |
| Criterio de fallo | Selecciona otra formulación, no encuentra la tarjeta o abandona pese a las ayudas. La ausencia del producto no es fallo. | Informa una cadena, precio o ahorro distinto del mostrado, o no logra responder pese a las ayudas. Una recomendación agotada es problema del MVP. | Interpreta el color como certeza de que todas las farmacias tienen o no tienen stock, o como recomendación médica, y mantiene esa respuesta tras solicitar que la explique. | No logra aplicar el filtro o identificar una sucursal. No es fallo señalar que la pantalla no demuestra stock por anillo. |
| Tiempo de referencia | Hasta 3 minutos antes de ofrecer cierre o ayuda directa. | Hasta 3 minutos. | Hasta 2 minutos. | Hasta 2 minutos. |
| Errores a registrar | Uso de filtro no relacionado; confusión marca/principio; presentación incorrecta; resultado perdido; búsqueda sin coincidencia. | Confusión entre precio total y 100 UI; selección del precio mayor; ahorro confundido con descuento; elección de un registro agotado inducida por el sistema. | Confusión riesgo/stock; rojo entendido como agotado en todas las cadenas; verde entendido como garantía; uso médico del color. | Confusión entre anillo y disponibilidad; selección distinta; Centro entendido como ubicación validada; “más cercana” entendida como distancia calculada. |
| Ayudas | Registrar nivel máximo y cantidad total. | Registrar nivel máximo y cantidad total. | Solo preguntas neutrales; no explicar el color antes de obtener la respuesta. | No señalar el selector salvo ayuda directa registrada. |
| Resultado | Solo / con ayuda / no completó / no evaluable. | Solo / con ayuda / no completó / no evaluable. | Comprensión completa / parcial / incorrecta / no evaluable. | Solo / con ayuda / no completó / no evaluable. |
| Observaciones | Ruta usada, términos escritos, dudas y citas. | Elementos leídos, comparación realizada y fuente de confusión. | Explicación textual y acción que dice que tomaría. | Anillo elegido, sucursales encontradas y significado atribuido. |
| `causa_no_evaluable` | Producto habitual fuera del catálogo; fallo técnico de la sesión. | Menos de dos precios; ausencia de ahorro; fallo técnico. | Semáforo no visible o fallo técnico. | Anillo requerido no ofrecido; lista vacía por fallo técnico. |

### 7.3 Aclaración obligatoria sobre la tarea 3B

La tarea 3B solo evalúa la capacidad de filtrar un **directorio de sucursales**. No evalúa ni demuestra disponibilidad de insulina por anillo. Después de registrar la interpretación espontánea, el moderador aclarará:

> Esta lista muestra sucursales asociadas a un anillo. La versión actual no confirma si una insulina está disponible en esas sucursales.

## 8. Métricas

### 8.1 Tasa de éxito por tarea

`Tasa de éxito = participantes que completan correctamente / participantes con tarea evaluable × 100`

Mide la proporción que alcanzó el objetivo, con o sin ayuda según se reporte. Las tareas no evaluables se excluyen del denominador y sus causas se informan por separado.

### 8.2 Finalización independiente

`Finalización independiente = participantes que completan sin ayuda / participantes con tarea evaluable × 100`

Permite diferenciar una tarea finalmente resuelta de una tarea que requirió intervención. Se reportará junto con la distribución de niveles de ayuda.

### 8.3 Tiempo por tarea

Se registrará en segundos desde el final de la instrucción hasta la respuesta, abandono o cierre. El tiempo ayuda a detectar fricción, pero no debe interpretarse aisladamente: una lectura cuidadosa puede ser apropiada.

- Usar **mediana** como resumen principal cuando haya pocos casos, valores extremos o distribución asimétrica.
- Usar **promedio** como complemento cuando se informe también dispersión y no oculte casos extremos.
- Reportar rango mínimo–máximo; si la muestra lo permite, añadir rango intercuartílico.

### 8.4 Errores

`Errores por tarea = suma de acciones o interpretaciones definidas como error durante la tarea`

Se separarán:

- error de interacción;
- error de comprensión;
- contradicción o problema inducido por el MVP;
- fallo técnico.

No todos los errores tienen la misma gravedad. Se describirá su efecto sobre el objetivo, sin crear una puntuación ponderada no validada.

### 8.5 Ayudas

Se registrarán cantidad total y nivel máximo de ayuda. Una tarea completada después de ayuda directa no se contará como finalización independiente.

### 8.6 Puntaje SUS

Se calculará conforme a la sección 5. Se reportará como percepción global de usabilidad, no como porcentaje de precisión. Para el piloto se presentarán resultados individuales anonimizados, mediana, promedio, rango y dispersión pertinente.

### 8.7 Comprensión del semáforo

| Puntuación | Criterio |
|---:|---|
| 0 | Interpretación incorrecta: lo trata como certeza de stock, diagnóstico o recomendación médica. |
| 1 | Comprensión parcial: reconoce una alerta, pero la confunde en parte con stock actual o garantía. |
| 2 | Comprensión completa para el alcance del MVP: reconoce riesgo/alerta y distingue que no garantiza stock ni reemplaza el estado actual. |

Se conservará además la explicación textual, porque la puntuación no muestra por qué ocurrió la confusión.

### 8.8 Comprensión del anillo

| Puntuación | Criterio |
|---:|---|
| 0 | Cree que el filtro confirma stock de la insulina o calcula la farmacia más cercana. |
| 1 | Reconoce que muestra sucursales, pero mantiene alguna duda sobre disponibilidad o distancia. |
| 2 | Explica que solo filtra un directorio y que no confirma disponibilidad del producto. |

### 8.9 Intención de uso

Pregunta cerrada posterior a la entrevista:

> Si este comparador estuviera disponible, ¿qué tan probable sería que lo usara en una futura búsqueda de insulina?

| Valor | Respuesta |
|---:|---|
| 1 | Definitivamente no lo usaría |
| 2 | Probablemente no lo usaría |
| 3 | No estoy seguro |
| 4 | Probablemente lo usaría |
| 5 | Definitivamente lo usaría |

Siempre se acompañará con “¿Por qué?”. Esta medida expresa intención declarada, no uso real futuro.

## 9. Consentimiento informado

### 9.1 Texto propuesto

> **Invitación a participar**
>
> Le invitamos a participar en una prueba académica de un comparador de información sobre insulinas y farmacias de Santa Cruz de la Sierra. El propósito es conocer si la página es clara, comprensible y fácil de usar.
>
> La actividad durará aproximadamente entre 25 y 35 minutos. Primero le haremos algunas preguntas generales sobre cómo busca insulina. Después le pediremos realizar tareas sencillas en la página, responder diez afirmaciones sobre su facilidad de uso y comentar qué le resultó claro o confuso.
>
> Estamos evaluando la página, no sus conocimientos ni sus capacidades. No hay respuestas correctas o incorrectas en las preguntas de opinión.
>
> Su participación es voluntaria. Puede no responder una pregunta, pedir una pausa o retirarse en cualquier momento, sin tener que explicar el motivo y sin ninguna consecuencia.
>
> Esta prueba no es una consulta médica. No se le pedirá cambiar su tratamiento, su insulina ni su dosis. La página no sustituye la orientación de un médico o farmacéutico. Los precios, estados de stock y semáforos mostrados forman parte de un MVP y no garantizan disponibilidad en una farmacia.
>
> Registraremos sus respuestas con un código, sin incluir su nombre en la hoja de resultados. La información se usará con fines académicos y se presentará de forma agrupada o anónima. Solo el equipo autorizado del proyecto tendrá acceso a los registros de la prueba.
>
> Tomar notas forma parte de la actividad. Cualquier grabación de audio, video o pantalla requiere una autorización separada. Puede participar aunque no autorice una grabación.
>
> Antes de decidir, puede hacer todas las preguntas que desee.
>
> **Declaración:** He recibido una explicación clara, tuve oportunidad de preguntar y acepto participar voluntariamente.
>
> Código del participante: __________ — Fecha: __________
> Aceptación de participación: Sí ☐  No ☐

### 9.2 Autorizaciones separadas

Cada opción debe poder rechazarse sin impedir la participación:

- Autorizo notas escritas anonimizadas: Sí ☐ No ☐
- Autorizo grabación de audio: Sí ☐ No ☐
- Autorizo grabación de pantalla: Sí ☐ No ☐
- Autorizo grabación de video: Sí ☐ No ☐

Si se realiza alguna grabación, el equipo deberá informar finalidad, ubicación de almacenamiento, personas con acceso y fecha o condición de eliminación.

### 9.3 Datos que no deben recopilarse

No se solicitarán ni registrarán, salvo justificación ética y metodológica posterior independiente:

- nombre completo, número de cédula o fotografía identificable;
- número de seguro, afiliación o historia clínica;
- dirección domiciliaria exacta;
- credenciales, contraseñas o datos bancarios;
- resultados de glucosa, diagnósticos adicionales o complicaciones médicas;
- fotografías de recetas, envases con datos personales o documentos clínicos;
- dosis detallada vinculada con la identidad;
- teléfono, correo u otro contacto dentro de la hoja de respuestas;
- información clínica de familiares;
- cualquier dato que no sea necesario para comprender el uso del MVP.

Si se requiere contacto para coordinar una sesión, se mantendrá en una lista separada de los resultados y se eliminará cuando deje de ser necesario. El nombre de la insulina habitual puede revelar información de salud; si se usa para la tarea, no se asociará con la identidad del participante.

## 10. Pautas éticas

1. Tratar a cada participante como adulto autónomo y evitar diminutivos o expresiones paternalistas como “abuelito”.
2. Usar frases breves, vocabulario cotidiano y ritmo pausado, sin infantilizar.
3. Preguntar si desea que se aumente la letra, se lea una instrucción o se ajuste el entorno.
4. Permitir pausas y finalizar la sesión si existe cansancio, incomodidad o deseo de retirarse.
5. No presionar para terminar rápido ni mostrar desaprobación ante errores.
6. Mantener la mínima intervención y registrar toda ayuda.
7. No inducir respuestas con palabras, gestos, tono de voz o señalamiento visual.
8. Verificar comprensión pidiendo que la persona explique con sus propias palabras.
9. Proteger notas, grabaciones y pantallas frente a personas no autorizadas.
10. No solicitar información médica innecesaria.
11. No recomendar marcas, dosis, sustituciones, compras anticipadas ni cambios de tratamiento.
12. No prometer disponibilidad, precio, ahorro ni actividad de una sucursal.
13. No presentar el semáforo como diagnóstico, certeza o recomendación médica.
14. No corregir una interpretación mientras todavía se está midiendo; aclarar los límites después de registrar la respuesta.
15. Ante una pregunta médica, indicar que debe consultarse a un profesional de salud o farmacéutico.
16. Reportar citas de manera anónima y evitar detalles que permitan reconocer a la persona.

## 11. Propuesta de muestra piloto

### 11.1 Composición propuesta

- **Grupo principal:** 8 a 12 adultos mayores jubilados insulinodependientes residentes en Santa Cruz de la Sierra.
- **Grupo opcional separado:** 3 a 5 familiares o cuidadores que participen habitualmente en la búsqueda o compra.

Los resultados de cuidadores se reportarán por separado. No se mezclarán en una única puntuación SUS con los usuarios principales salvo que se justifique y se muestre también cada grupo de forma independiente.

### 11.2 Selección intencional y diversidad

Se propone selección intencional, no probabilística, procurando variación en:

- uso autónomo o apoyo de cuidador;
- experiencia declarada con teléfono o computadora;
- dispositivo habitual;
- zona o anillo de residencia, registrado de forma amplia y no como dirección;
- experiencia previa buscando información de farmacias;
- necesidades de accesibilidad comunicadas voluntariamente;
- marca o presentación habitual, sin registrar detalles clínicos adicionales.

La inclusión no dependerá de demostrar alta habilidad digital. Debe evitarse reclutar únicamente personas cercanas al equipo o con experiencia tecnológica, porque reduciría la diversidad de problemas observables.

### 11.3 Propósito exploratorio

La muestra piloto sirve para:

- comprobar que el protocolo se entiende y puede repetirse;
- detectar problemas recurrentes de navegación y comprensión;
- observar si las tareas corresponden al MVP real;
- identificar lenguaje confuso o interpretaciones riesgosas;
- estimar duración y carga para el participante;
- priorizar mejoras para una iteración posterior.

Puede concluir qué problemas aparecieron en las sesiones realizadas, con qué frecuencia dentro del piloto y qué evidencia cuantitativa y cualitativa los acompaña.

No puede concluir:

- que los resultados representan a todos los jubilados de Santa Cruz;
- prevalencia poblacional de una barrera;
- aceptación general del producto;
- impacto clínico o económico real;
- precisión del modelo o del inventario;
- causalidad entre una característica personal y un resultado;
- validez psicométrica definitiva de la adaptación de SUS.

Una muestra estadísticamente representativa requeriría un marco muestral definido, cálculo formal de tamaño, estrategia probabilística, control de no respuesta y análisis inferencial. Este piloto no cumple ni pretende cumplir esas condiciones. La literatura de usabilidad muestra que grupos pequeños pueden descubrir problemas relevantes con rendimientos decrecientes, pero eso no convierte sus porcentajes en estimaciones poblacionales.

## 12. Procedimiento de aplicación

### 12.1 Preparación de la ronda

1. Confirmar que se evaluará la versión aprobada del MVP y no modificarla durante una ronda.
2. Registrar hash o fecha del archivo, navegador, versión, dispositivo, pantalla, conectividad y responsable.
3. Abrir el MVP y verificar buscador, filtros, tarjetas, selector de anillos, tamaño de fuente y voz.
4. Preparar consentimiento, hoja de tareas, SUS, entrevista y cronómetro.
5. Asignar un código anónimo, por ejemplo `P01`, sin usar iniciales ni fecha de nacimiento.
6. Definir el escenario alternativo de tareas y verificar que aparezca en la versión evaluada.
7. Comprobar privacidad del espacio y almacenamiento autorizado de los registros.

### 12.2 Inicio de la sesión

1. Recibir al participante y presentarse.
2. Explicar que se evalúa el comparador, no a la persona.
3. Informar duración, derecho a pausa y retiro.
4. Leer el consentimiento y resolver preguntas.
5. Registrar aceptación y autorizaciones separadas.
6. Preguntar si necesita ajuste de letra, lectura o descanso antes de comenzar.

### 12.3 Preguntas iniciales

1. Aplicar únicamente el bloque A de entrevista y las preguntas generales necesarias del bloque B.
2. No registrar información clínica adicional.
3. Determinar si la insulina habitual está en el catálogo sin convertir su ausencia en fallo.
4. No enseñar todavía cómo utilizar filtros, precios, semáforo o anillos.

### 12.4 Tareas guiadas

1. Leer una tarea por vez, exactamente como está escrita.
2. Iniciar el cronómetro al terminar la instrucción.
3. Observar sin intervenir y registrar ruta, errores y comentarios.
4. Aplicar la secuencia de mínima intervención cuando sea necesario.
5. Detener el tiempo al completar, abandonar o cerrar la tarea.
6. Registrar resultado, ayudas, causa no evaluable y problemas del MVP.
7. No corregir la comprensión del semáforo antes de completar la tarea 3A.
8. Tras la tarea 3B, aclarar que no existe disponibilidad por anillo.

### 12.5 Aplicación de SUS

1. Entregar o leer la escala completa en su orden original.
2. Usar siempre las mismas cinco opciones.
3. No explicar qué ítems son positivos o negativos.
4. Revisar que haya una respuesta en cada reactivo, sin cambiar respuestas por el participante.
5. Calcular el puntaje después de la sesión o fuera de la vista del participante.

### 12.6 Entrevista final

1. Aplicar los bloques C y D.
2. Utilizar las profundizaciones neutrales cuando sea necesario.
3. Formular la escala de intención de uso y preguntar el motivo.
4. Registrar citas textuales breves sin datos identificables.
5. Preguntar si desea agregar algo.

### 12.7 Cierre y resguardo

1. Agradecer la participación.
2. Recordar que el MVP no garantiza precios, stock o disponibilidad por sucursal.
3. Recordar que el semáforo no sustituye orientación profesional.
4. Guardar los registros con el código anónimo.
5. Separar consentimientos y datos de contacto de las respuestas.
6. Documentar fallos técnicos y desviaciones del protocolo.
7. Revisar la hoja antes de iniciar otra sesión, sin modificar el protocolo a mitad de una ronda salvo por seguridad.

## 13. Plantillas de registro

### A. Datos generales anónimos del participante

| Campo | Registro |
|---|---|
| Código anónimo | |
| Fecha de sesión | |
| Grupo | Usuario principal / cuidador |
| Rango de edad opcional | 60–69 / 70–79 / 80 o más / prefiere no responder |
| Compra normalmente | Solo / con ayuda / otra persona / prefiere no responder |
| Dispositivo habitual | Teléfono / computadora / tableta / ninguno / otro |
| Familiaridad digital declarada | Baja / media / alta / prefiere no responder |
| Zona amplia o anillo, si lo conoce | |
| Necesidad de accesibilidad comunicada voluntariamente | Ninguna / letra / lectura / movilidad / otra / prefiere no responder |
| Navegador y dispositivo de prueba | |
| Versión o fecha del MVP | |
| Grabaciones autorizadas | Ninguna / audio / pantalla / video |

No registrar nombre, documento, dirección exacta, historia clínica, teléfono o correo en esta tabla.

### B. Registro por tarea

| Código | Tarea | Producto/escenario | Evaluable | Inicio | Fin | Tiempo (s) | Resultado | Nivel máximo de ayuda | N.º de ayudas | N.º de errores | `causa_no_evaluable` | Observaciones | Comentario textual |
|---|---|---|---|---|---|---:|---|---:|---:|---:|---|---|---|
| | 1 | | Sí / No | | | | | | | | | | |
| | 2 | | Sí / No | | | | | | | | | | |
| | 3A | | Sí / No | | | | | | | | | | |
| | 3B | | Sí / No | | | | | | | | | | |

### C. Registro SUS

| Código | I1 | I2 | I3 | I4 | I5 | I6 | I7 | I8 | I9 | I10 | Suma transformada | SUS 0–100 | Observaciones de aplicación |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| | | | | | | | | | | | | | |

Lista de comprobación del cálculo:

- [ ] Ítems impares: respuesta − 1.
- [ ] Ítems pares: 5 − respuesta.
- [ ] Diez contribuciones entre 0 y 4.
- [ ] Suma entre 0 y 40.
- [ ] Suma multiplicada por 2,5.
- [ ] Puntaje final entre 0 y 100.

### D. Registro de entrevista

| Código | Bloque | Pregunta | Resumen de respuesta | Cita textual anónima | Nota del moderador |
|---|---|---|---|---|---|
| | A | | | | |
| | B | | | | |
| | C | | | | |
| | D | | | | |
| | E | | | | |

### E. Hallazgos cualitativos

| ID hallazgo | Evidencia o patrón | Participantes en que apareció | Tarea/sección | Impacto observado | Interpretación provisional | Evidencia adicional necesaria |
|---|---|---|---|---|---|---|
| H-01 | | | | | | |

No convertir automáticamente una opinión aislada en patrón. Conservar también casos discrepantes.

### F. Problemas observados

| ID problema | Descripción observable | Tipo | Frecuencia en el piloto | Consecuencia para la tarea | Evidencia | Prioridad propuesta | Recomendación pendiente |
|---|---|---|---:|---|---|---|---|
| P-01 | | Datos / modelo / interfaz / contenido / protocolo / técnico | | | | | |

La prioridad será una propuesta basada en frecuencia, impacto y riesgo de interpretación; no una conclusión estadística poblacional.

## 14. Limitaciones

### 14.1 Limitaciones de los datos

- El catálogo contiene 43 registros agrupados en 24 formulaciones, no todo el mercado.
- Los estados son categóricos y no contienen cantidades físicas.
- Los precios y estados proceden de capturas embebidas y no se actualizan durante la prueba.
- La interfaz no muestra fecha de actualización al participante.
- Solo tres formulaciones tienen registros de las tres cadenas; otras comparaciones incluyen una o dos.
- Un producto ausente puede significar falta de registro, no agotamiento.
- No existe trazabilidad producto–sucursal–anillo.
- Parte de la clasificación territorial carece de evidencia suficiente o es ambigua.

### 14.2 Limitaciones del modelo y semáforo

- El modelo se construyó con 43 observaciones de un corte transversal y un número reducido de casos positivos.
- El objetivo es un proxy de riesgo presente o inminente, no seguimiento longitudinal hasta un quiebre real.
- En la versión diagnosticada, las 24 tarjetas agrupadas resultan rojas aunque la mayoría de los registros de stock están disponibles.
- La regla del medicamento toma rojo si cualquiera de sus registros contiene una señal roja.
- Puede coexistir `DISPONIBLE` con “Alerta de Quiebre”; la interfaz no explica suficientemente la diferencia temporal.
- El semáforo global amarillo y los textos fijos de 20 verdes y 4 rojos no coinciden con el resultado actual de las tarjetas.
- SUS y el *task testing* evalúan comprensión y usabilidad; no validan el rendimiento predictivo.

### 14.3 Limitaciones de interfaz y contenido

- El filtro por cadena está rotulado como disponibilidad, pero verifica presencia de un registro de catálogo.
- Todos los registros reciben internamente una marca `disponible: true`, incluso si el estado es `AGOTADO`.
- El menor precio y el ahorro pueden calcularse incluyendo registros agotados.
- “No disponible en catálogo” no equivale a agotado.
- “Farmacia más cercana” no se basa en ubicación ni distancia.
- Las sucursales muestran “Activa” mediante texto fijo.
- Registros territoriales sin evidencia pueden presentarse como Centro.
- Algunos mensajes usan afirmaciones fuertes como abastecimiento asegurado o garantizado.
- La locución predeterminada usa “abuelito”, lenguaje que puede percibirse como paternalista.
- La calculadora usa supuestos de 30 días y un subconjunto de productos; no es una herramienta clínica.
- La apariencia completa puede depender de un recurso externo de Tailwind CSS.

### 14.4 Limitaciones de la prueba piloto

- Selección intencional y tamaño pequeño.
- Posible sesgo de voluntariado y de reclutamiento por conveniencia.
- Efecto del moderador y del entorno de prueba.
- Intención declarada distinta del uso real sostenido.
- Posible aprendizaje entre tareas.
- SUS adaptado lingüísticamente, pero sin validación psicométrica local previa.
- Diferencias de dispositivo o conectividad si no se estandarizan.
- Los porcentajes describen el piloto y no estiman la población.

## 15. Interpretación de resultados

### 15.1 Triangulación

Los resultados se interpretarán combinando:

1. **SUS:** percepción global posterior al uso.
2. **Tareas:** capacidad observable de alcanzar objetivos concretos.
3. **Tiempo, errores y ayudas:** fricción durante la interacción.
4. **Comprensión del semáforo y anillo:** riesgo de interpretación incorrecta.
5. **Entrevistas:** motivos, expectativas, confianza y necesidades.
6. **Intención de uso:** disposición declarada y explicación asociada.

Ejemplos de triangulación:

- SUS favorable con errores repetidos puede indicar satisfacción subjetiva pese a problemas objetivos.
- Tareas completadas solo con ayuda pueden elevar la tasa de éxito, pero reducir la finalización independiente.
- Intención de uso alta con desconfianza en la vigencia del stock señala valor percibido condicionado a mejores datos.
- Confusión compartida sobre rojo y disponibilidad debe tratarse como problema del diseño, aunque el tiempo de tarea sea corto.

### 15.2 Resumen cuantitativo

- Informar numeradores y denominadores, no solo porcentajes: por ejemplo, `5 de 8 tareas evaluables`.
- Separar `no evaluable` de `no completó`.
- Usar mediana para tiempos y SUS cuando la muestra sea pequeña o asimétrica; complementar con promedio, rango y dispersión.
- Mostrar resultados de usuarios principales y cuidadores por separado.
- No establecer a posteriori umbrales arbitrarios de “éxito” para declarar aprobado el MVP.
- Si se utiliza un referente publicado de SUS, presentarlo como comparación contextual, no como corte clínico o estadístico.

### 15.3 Síntesis cualitativa y priorización

Un hallazgo se apoyará en evidencia observable: tarea, cita, error o patrón. Se distinguirán:

- problema del dato;
- problema del modelo;
- problema de interfaz o contenido;
- barrera contextual;
- desviación del protocolo;
- preferencia individual.

La priorización considerará frecuencia dentro del piloto, impacto sobre la tarea y riesgo de interpretación. Se conservarán opiniones minoritarias o contradictorias para no forzar consenso.

### 15.4 Conclusiones permitidas y no permitidas

La futura aplicación podrá concluir, de forma exploratoria, qué tareas fueron más difíciles, qué mensajes generaron confusión, qué problemas se repitieron y cómo percibieron el MVP las personas participantes.

No permitirá afirmar causalidad, precisión del modelo, efectividad clínica, disponibilidad real, aceptación poblacional ni representatividad estadística. Tampoco permitirá afirmar que una mejora específica resolverá un problema hasta volver a evaluarla.

## 16. Cómo explicar este SCRUM

### 16.1 Qué problema resolvemos

El proyecto necesita saber si el MVP real puede ser utilizado y comprendido por su público objetivo antes de continuar hacia una validación de campo. Sin un protocolo común, cada integrante podría hacer preguntas diferentes, ayudar de forma desigual o interpretar el semáforo y los anillos de manera incorrecta.

### 16.2 Qué hicimos

En `SCRUM-47` se diseñó un método repetible para evaluar la versión actual del comparador respetando sus capacidades y limitaciones. Se definieron el orden de la sesión, instrucciones, criterios de observación, métricas, consentimiento y resguardo ético.

### 16.3 Qué instrumentos se diseñaron

- Escala SUS de diez reactivos en lenguaje claro, con cálculo estándar.
- Entrevista semiestructurada sobre compra, desabastecimiento, uso y disposición.
- Cuatro tareas: búsqueda, comparación, interpretación del semáforo y filtro por anillo.
- Métricas de éxito, independencia, tiempo, errores, ayudas y comprensión.
- Consentimiento informado y pautas éticas.
- Plantillas listas para registrar datos anónimos, tareas, SUS, entrevistas y problemas.

### 16.4 Qué se medirá

Se medirá usabilidad percibida, capacidad para completar tareas, comprensión de precios, semáforo y directorio territorial, necesidad de ayuda e intención declarada de uso.

### 16.5 Qué no hicimos todavía

No se reclutaron participantes, no se realizaron entrevistas o tareas, no se calcularon puntajes reales y no se validó el modelo. Por ello, este SCRUM no demuestra que el MVP sea usable, aceptado o preciso.

### 16.6 Conexión con SCRUM-48

`SCRUM-48` deberá aplicar estos instrumentos a la muestra aprobada, tabular los datos, calcular SUS, analizar hallazgos y elaborar conclusiones de negocio. Antes del trabajo de campo deberá confirmar que la versión del MVP no cambió; si cambió, tendrá que revisar escenarios y criterios sin alterar la lógica original de SUS.

## Referencias metodológicas

- Brooke, J. (1996). *SUS: A “Quick and Dirty” Usability Scale*. En P. W. Jordan, B. Thomas, B. A. Weerdmeester e I. L. McClelland (Eds.), *Usability Evaluation in Industry* (pp. 189–194). Taylor & Francis. [Texto del capítulo](https://hci-studies.org/methods-and-measures/downloads/SUS_Brooke1996.pdf).
- Bangor, A., Kortum, P. T., & Miller, J. T. (2008). An Empirical Evaluation of the System Usability Scale. *International Journal of Human–Computer Interaction, 24*(6), 574–594. [https://doi.org/10.1080/10447310802205776](https://doi.org/10.1080/10447310802205776).
- Bangor, A., Kortum, P., & Miller, J. (2009). Determining What Individual SUS Scores Mean: Adding an Adjective Rating Scale. *Journal of Usability Studies, 4*(3), 114–123. [Artículo en PDF](https://uxpajournal.org/wp-content/uploads/sites/7/pdf/JUS_Bangor_May2009.pdf).
- Virzi, R. A. (1992). Refining the Test Phase of Usability Evaluation: How Many Subjects Is Enough? *Human Factors, 34*(4), 457–468. [https://doi.org/10.1177/001872089203400407](https://doi.org/10.1177/001872089203400407).
- Lewis, J. R. (1994). Sample Sizes for Usability Studies: Additional Considerations. *Human Factors, 36*(2), 368–378. [https://doi.org/10.1177/001872089403600215](https://doi.org/10.1177/001872089403600215).

## Lista de verificación previa a SCRUM-48

- [ ] La versión del MVP quedó identificada y congelada para la ronda.
- [ ] El equipo entiende que este documento no contiene resultados.
- [ ] Los moderadores practicaron la mínima intervención.
- [ ] El consentimiento y las autorizaciones están separados.
- [ ] Se evita recopilar información médica innecesaria.
- [ ] La ausencia de una insulina se registra como no evaluable, no como fallo.
- [ ] El ahorro no se interpreta sin revisar el estado de stock mostrado.
- [ ] El semáforo no se presenta como disponibilidad actual, diagnóstico o garantía.
- [ ] El filtro por anillo no se presenta como stock por sucursal.
- [ ] Los cuidadores se analizan como grupo separado.
- [ ] SUS conserva diez reactivos, orden, polaridad y cálculo estándar.
- [ ] No se inventan subescalas SUS.
- [ ] Las conclusiones se limitan al carácter exploratorio del piloto.
