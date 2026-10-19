# Investigación inicial: acceso a insulina para pacientes jubilados con diabetes

## 1. Contexto del problema

El planteamiento preliminar describe a un paciente jubilado con diabetes que debe recorrer varias farmacias durante días consecutivos para encontrar insulina importada. Cuando finalmente la consigue, puede pagar hasta el triple de su precio habitual. Esta situación reduce de forma importante el presupuesto disponible para comprar alimentos y convierte el acceso al tratamiento en un problema de salud, abastecimiento y vulnerabilidad económica.

El material inicial identifica como factores relacionados la escasez de medicamentos, la dependencia de productos importados, la insuficiencia de las pensiones, la especulación de precios y el impacto de la falta de dólares en la importación farmacéutica. También señala un posible daño colateral: la reducción de la capacidad de compra de alimentos y el endeudamiento de los hogares.

## 2. Pregunta orientadora

¿Cómo puede un sistema de información sobre disponibilidad y precios, complementado con alternativas de compra y entrega, mejorar el acceso oportuno y económicamente sostenible a la insulina para pacientes jubilados con diabetes?

Esta pregunta será afinada después de validar la disponibilidad y calidad de los datos.

## 3. Personas y actores afectados

- **Pacientes jubilados con diabetes:** necesitan continuidad en su tratamiento, tienen ingresos relativamente fijos y pueden presentar limitaciones de movilidad.
- **Familiares y cuidadores:** apoyan la búsqueda, compra, transporte y administración del medicamento.
- **Farmacias y distribuidores:** disponen de inventarios y precios que pueden variar por establecimiento y fecha.
- **Importadores y laboratorios:** intervienen en el abastecimiento, la disponibilidad de divisas y los tiempos de reposición.
- **Instituciones públicas, aseguradoras y organizaciones de pacientes:** pueden facilitar compras institucionales, subsidios, seguimiento y priorización de casos.

## 4. Hallazgos iniciales e hipótesis de trabajo

1. La disponibilidad de insulina no es uniforme entre farmacias ni entre periodos.
2. La dependencia de importaciones puede aumentar la probabilidad de quiebres de stock y variaciones de precio.
3. Los pacientes jubilados son especialmente vulnerables porque sus ingresos y su movilidad son limitados.
4. La falta de información consolidada obliga a realizar búsquedas presenciales o repetidas.
5. Un inventario georreferenciado y actualizado podría reducir el tiempo de búsqueda.
6. La compra institucional o subsidiada y la entrega programada podrían disminuir el costo total de acceso, pero requieren validación financiera, legal y operativa.

Estas hipótesis no se consideran conclusiones: deberán contrastarse con datos de farmacias, pacientes y fuentes oficiales.

## 5. Alternativas de abordaje consideradas

### 5.1. Plataforma de inventario farmacéutico

Consolidar disponibilidad, presentación, precio, fecha de actualización y ubicación de la insulina por farmacia. El sistema debería mostrar la antigüedad del dato para evitar que una existencia desactualizada se interprete como confirmación.

### 5.2. Entrega a domicilio para pacientes priorizados

Permitir la reserva y entrega programada a personas con limitaciones de movilidad o con tratamiento continuo. Para implementarla se necesitarían reglas de priorización, trazabilidad y controles de temperatura cuando correspondan.

### 5.3. Compra institucional o subsidio

Analizar compras agrupadas, convenios con farmacias, apoyo de instituciones y mecanismos de subsidio. Esta alternativa debe evaluarse con el costo final para el paciente, la sostenibilidad presupuestaria y la normativa aplicable.

## 6. Alcance inicial de la investigación

### Incluye

- Describir la disponibilidad, el precio y la variación temporal de las presentaciones de insulina seleccionadas.
- Identificar zonas, farmacias o periodos con mayor riesgo de desabastecimiento.
- Estimar el impacto del precio del tratamiento sobre el presupuesto mensual del paciente.
- Analizar el tiempo y la distancia asociados a la búsqueda del medicamento.
- Diseñar indicadores y visualizaciones para apoyar decisiones de abastecimiento y atención.
- Comparar escenarios de compra directa, compra institucional, subsidio y entrega programada.

### No incluye en la primera etapa

- Prescribir, sustituir o modificar tratamientos médicos.
- Recomendar dosis, marcas o cambios terapéuticos a pacientes.
- Confirmar diagnósticos clínicos individuales.
- Operar ventas, pagos, distribución ni logística de medicamentos.
- Afirmar causalidad entre una variable económica y un resultado clínico sin evidencia longitudinal.

## 7. Datos previstos a utilizarse

| Grupo de datos | Variables o campos previstos | Uso analítico | Fuente posible |
|---|---|---|---|
| Inventario | Fecha y hora, farmacia, municipio/zona, producto, presentación, unidades disponibles, estado de disponibilidad | Medir quiebres de stock y disponibilidad por ubicación | Farmacias, distribuidores o reportes institucionales |
| Precios | Producto, presentación, precio, moneda, fecha, canal de compra, precio subsidiado/no subsidiado | Comparar precios y detectar variaciones o sobrecostos | Farmacias, observatorios de precios y registros de compra |
| Demanda | Fecha, unidades solicitadas/vendidas, recetas atendidas, solicitudes no atendidas | Estimar demanda y anticipar faltantes | Farmacias, centros de salud u organizaciones participantes |
| Pacientes y hogares | Rango de edad, condición de jubilación, zona, frecuencia mensual, ingreso o pensión por rangos, gasto en alimentos y medicamentos | Medir vulnerabilidad y carga financiera | Encuestas anonimizadas y voluntarias |
| Acceso | Distancia, tiempo de traslado, número de farmacias consultadas, disponibilidad de transporte y entrega | Evaluar barreras de acceso | Encuestas, geolocalización agregada y registros de entrega |
| Abastecimiento | Proveedor, país de origen, fecha de pedido, fecha de llegada, tiempo de reposición, unidades importadas | Analizar dependencia importadora y tiempos de reposición | Importadores, distribuidores y fuentes oficiales |
| Contexto económico | Tipo de cambio de referencia, inflación, costo de transporte y evolución de precios | Interpretar cambios de precio y costo total | Fuentes estadísticas y financieras oficiales |
| Resultados del servicio | Reservas atendidas, entregas exitosas, tiempo de respuesta, cancelaciones y satisfacción | Evaluar las alternativas de solución | Prototipo, farmacias participantes y encuestas |

## 8. Indicadores iniciales

- **Disponibilidad:** porcentaje de farmacias con existencia por producto y zona.
- **Días de desabastecimiento:** número de días sin unidades disponibles en un periodo.
- **Variación de precio:** diferencia porcentual entre el precio mínimo, máximo y mediano.
- **Sobrecosto relativo:** precio observado frente a un precio de referencia.
- **Carga financiera:** gasto mensual estimado en insulina como porcentaje de la pensión o ingreso del hogar.
- **Esfuerzo de búsqueda:** número de farmacias visitadas y tiempo invertido antes de obtener el medicamento.
- **Cobertura de atención:** proporción de solicitudes atendidas y entregas exitosas.
- **Tiempo de reposición:** días entre el pedido y la disponibilidad para el paciente.

## 9. Calidad, privacidad y riesgos de los datos

- Registrar la fecha y hora de cada observación para distinguir datos actuales de datos históricos.
- Estandarizar nombres de productos, presentaciones, unidades, monedas y ubicaciones.
- Separar precio publicado, precio pagado y subsidio aplicado.
- Documentar datos faltantes, duplicados, cambios de fuente y reglas de limpieza.
- No almacenar nombres, documentos, teléfonos ni direcciones exactas de pacientes en el análisis.
- Usar rangos para edad e ingresos y publicar resultados agregados para evitar reidentificación.
- Obtener consentimiento informado para encuestas y limitar el acceso a datos sensibles.
- Validar con personal de salud cualquier interpretación relacionada con continuidad del tratamiento.

## 10. Próximos pasos

1. Delimitar la ciudad o zona geográfica y las presentaciones de insulina que se estudiarán.
2. Definir las fuentes que pueden entregar datos periódicos y sus responsables.
3. Diseñar un diccionario de datos y un formato común de captura.
4. Realizar una prueba piloto con un conjunto pequeño de farmacias y pacientes voluntarios.
5. Validar los indicadores con actores del sistema de salud y organizaciones de pacientes.
6. Construir un tablero exploratorio y comparar escenarios de acceso.
7. Documentar limitaciones, supuestos y criterios para una eventual implementación.

## 11. Estado de la investigación

Este documento es una línea base de investigación y diseño. Resume el objetivo preliminar y los elementos observados en el material inicial del proyecto; no reemplaza una revisión bibliográfica, una validación con actores ni una evaluación médica o regulatoria. Las cifras, relaciones causales y alternativas deberán confirmarse con datos verificables antes de usarse para tomar decisiones.
