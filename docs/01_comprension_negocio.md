# 1. Comprensión del Negocio

## 1.1 Problema de negocio

Los pacientes jubilados insulinodependientes en Santa Cruz de la Sierra enfrentan dificultades para acceder oportunamente a insulina importada debido a la falta de visibilidad sobre el stock disponible en las farmacias.

Esta situación se agrava porque los inventarios se gestionan de forma aislada entre establecimientos y muchos pacientes presentan una brecha digital que limita su acceso a información previa sobre disponibilidad.

Como consecuencia, los pacientes deben recorrer varias farmacias, invertir mayor tiempo en la búsqueda y enfrentar un mayor riesgo de interrupción de su tratamiento.

## 1.2 Problema principal

Incertidumbre sobre la disponibilidad de insulina importada para pacientes jubilados insulinodependientes en Santa Cruz de la Sierra.

## 1.3 Causa raíz

La causa raíz del problema se relaciona principalmente con dos factores:

### Inventarios aislados

Las farmacias gestionan sus existencias de forma independiente y no existe una fuente consolidada de información que permita conocer la disponibilidad de insulina entre diferentes establecimientos.

Esto dificulta identificar previamente dónde existe stock y genera que el paciente deba realizar consultas o desplazamientos a diferentes farmacias.

### Brecha digital

Parte de los pacientes jubilados presenta dificultades para acceder o utilizar canales digitales complejos para consultar información sobre disponibilidad de medicamentos.

Factores como edad, conocimientos tecnológicos, acceso a dispositivos o dificultades de uso pueden limitar su capacidad para consultar información antes de desplazarse.

## 1.4 Actor principal validado

El actor principal del proyecto está conformado por:

Pacientes jubilados con diabetes insulinodependientes residentes en Santa Cruz de la Sierra.

Características principales:

- Necesitan adquirir insulina de manera periódica para mantener la continuidad de su tratamiento.
- Enfrentan incertidumbre sobre qué farmacias cuentan con disponibilidad.
- Pueden presentar movilidad reducida asociada a la edad.
- Algunos dependen del apoyo de familiares o cuidadores para realizar consultas o compras.
- La interrupción del tratamiento representa un riesgo para su salud.
- Parte del segmento puede presentar dificultades en el uso de herramientas digitales complejas.

## 1.5 Pregunta de investigación

¿Cuáles son los factores que permiten predecir la disponibilidad de insulina importada para los pacientes jubilados con diabetes en Santa Cruz de la Sierra durante el segundo semestre de 2026?

## 1.6 Objetivo general

Determinar los factores que permiten predecir la disponibilidad de insulina importada para los pacientes jubilados con diabetes en Santa Cruz de la Sierra durante el segundo semestre de 2026.

## 1.7 Pregunta analítica

¿Qué variables temporales, territoriales y de abastecimiento permiten predecir si una farmacia tendrá disponibilidad de insulina importada en un periodo determinado?

## 1.8 Objetivo analítico

Identificar las variables con mayor capacidad predictiva sobre la disponibilidad de insulina importada y utilizarlas posteriormente en un modelo de clasificación que permita estimar la probabilidad de existencia de stock.

## 1.9 Relación con el modelo predictivo

La definición del problema y de la pregunta analítica permite orientar el desarrollo posterior del modelo predictivo.

El modelo deberá analizar variables relacionadas con factores temporales, ubicación geográfica, características de las farmacias, reposición y demanda, con el objetivo de identificar patrones asociados a la disponibilidad de insulina.

La variable objetivo podrá representarse inicialmente como:

- 1 = Stock disponible.
- 0 = Stock no disponible.

## 1.10 Relación con el chatbot

Los resultados generados por el modelo predictivo podrán ser utilizados posteriormente por un chatbot de consulta simplificada.

El chatbot permitirá presentar al paciente jubilado o a su familiar información comprensible sobre la probabilidad de disponibilidad de insulina, reduciendo la necesidad de consultar o recorrer múltiples farmacias sin información previa.

El chatbot no sustituye al modelo predictivo, sino que funciona como un canal de acceso a los resultados generados por el componente analítico.

## 1.11 Relación con CRISP-DM

Este documento corresponde a la primera fase de CRISP-DM: Comprensión del Negocio.

En esta fase se define:

- El problema que se desea resolver.
- El actor afectado.
- Las causas principales del problema.
- La pregunta de investigación.
- El objetivo general.
- La pregunta analítica.
- La orientación del futuro modelo predictivo.

Esta definición permitirá avanzar posteriormente hacia la fase de Comprensión de los Datos.

## 1.12 Resultado esperado de la fase

Al finalizar esta fase, el proyecto debe contar con:

- Problema de negocio delimitado.
- Causa raíz identificada.
- Actor principal validado.
- Pregunta de investigación definida.
- Objetivo general alineado con el problema.
- Pregunta analítica orientada al análisis de datos.
- Base conceptual para el desarrollo del modelo predictivo.
- Relación definida entre el modelo predictivo y el futuro chatbot.
