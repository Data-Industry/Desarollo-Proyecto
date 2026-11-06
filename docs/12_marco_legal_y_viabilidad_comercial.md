# SCRUM-45 (US-30) — Marco legal, regulatorio y viabilidad comercial

**Historia de Usuario:** `US-30`

**Clave Jira:** `SCRUM-45`

**Fase CRISP-DM:** Comprensión del negocio / evaluación de viabilidad

**Ámbito territorial:** Estado Plurinacional de Bolivia

**Fecha de consulta de normas, políticas y sitios:** **6 de noviembre de 2026**

> **Naturaleza del documento:** análisis jurídico-documental académico y recomendaciones de cumplimiento. No constituye dictamen legal, patrocinio jurídico ni sustituye la revisión de un abogado habilitado en Bolivia.

## 1. Objetivo y alcance

Este SCRUM analiza el marco legal y de políticas privadas que puede afectar al comparador académico de precios y disponibilidad de insulina para personas jubiladas de Santa Cruz de la Sierra. Su propósito es orientar decisiones sobre:

- extracción automatizada de precios y estados publicados en sitios de farmacias;
- presentación de precios, fuentes, fechas y disponibilidad;
- mención de marcas de insulina y nombres de farmacias;
- tratamiento presente o futuro de datos personales y datos relacionados con salud;
- delimitación entre información comercial y consejo médico;
- posible uso futuro de WhatsApp Business;
- transición desde un MVP académico hacia un producto público o comercial.

El análisis se limita al sistema que existe en el repositorio al 6 de noviembre de 2026. No atribuye al proyecto funciones planificadas que todavía no han sido implementadas. En particular, no supone que exista un chatbot funcional, una integración con WhatsApp, una plataforma de ventas o un inventario en tiempo real.

Para evitar conclusiones más amplias que las fuentes, el documento utiliza cuatro categorías:

| Categoría | Significado en este documento |
|---|---|
| **Texto legal verificable** | Contenido que puede contrastarse con una norma, política o documento oficial citado. |
| **Interpretación razonable** | Aplicación prudente del texto al sistema analizado; no equivale a decisión judicial ni administrativa. |
| **Recomendación de cumplimiento** | Medida preventiva para reducir riesgo técnico, jurídico o de comunicación. |
| **Revisión jurídica profesional** | Punto cuyo resultado depende de hechos, contratos, registros, jurisprudencia o criterios de autoridad que deben ser examinados por un abogado. |

El documento **no constituye un dictamen legal profesional**. La viabilidad académica descrita aquí tampoco significa que el proyecto cumpla automáticamente toda norma aplicable ni que pueda lanzarse comercialmente sin trabajo adicional.

## 2. Descripción técnica del sistema analizado

El sistema operativo actual es un **visualizador HTML local** generado a partir de datasets procesados. Agrupa productos de insulina, compara precios observados en tres cadenas, presenta estados de catálogo y señales experimentales de un modelo, contiene un directorio estático de sucursales por anillo y ofrece una calculadora local de frascos y presupuesto.

Los datos se encuentran embebidos en el HTML. Al abrir el archivo, el usuario no consulta en vivo a las farmacias. La interfaz no vende, reserva, cobra ni confirma pedidos.

Los scrapers consultan:

- **Farmacorp:** buscador público y fichas JSON de productos mediante `requests`;
- **Farmacias Chávez:** sitio público mediante Playwright y un navegador Chromium sin interfaz gráfica;
- **Farmacias Telchi:** resultados públicos de búsqueda de WooCommerce mediante `requests` y BeautifulSoup.

Los campos brutos incluyen identificador de origen, cadena, nombre comercial, clasificación de principio activo, marca o laboratorio, precio actual, precio regular, descuento, estado de stock, sucursal genérica, ciudad, URL de producto y fecha/hora de extracción. Los archivos de salida son CSV y JSON estructurados; además, se conservan snapshots CSV con fecha en el nombre. No se guarda el HTML completo de las páginas.

No se encontraron cuentas propias del comparador, registro de usuarios, GPS, backend de conversaciones ni almacenamiento de historiales personales. El campo de dosis de la calculadora se procesa en el navegador y no se encontró código que lo envíe o persista. Aun así, una dosis es información relacionada con salud y su tratamiento futuro debe mantenerse minimizado.

| Componente | Estado actual | Riesgo jurídico relevante |
|---|---|---|
| Visualizador | HTML local con datos embebidos | Vigencia, exactitud, atribución y posible interpretación como información comercial actual. |
| Scraper Farmacorp | `requests` sobre búsqueda y fichas JSON públicas | Instrucciones actuales para agentes, términos del sitio, carga y reutilización automatizada. |
| Scraper Chávez | Playwright headless sobre buscador público | Automatización de navegador, carga, términos no localizados y estabilidad del DOM. |
| Scraper Telchi | `requests` + BeautifulSoup sobre WooCommerce público | Estado “Disponible” inferido sin comprobación específica y términos generales no localizados. |
| Dataset bruto | CSV/JSON con productos, precios, estado, fuente y timestamp | Retención, errores de clasificación y necesidad de conservar trazabilidad. |
| ETL analítico | Depura insumos y normaliza insulinas | Un error de origen o clasificación puede trasladarse a la interfaz. |
| Chatbot | No existe implementación funcional | Riesgo futuro, no capacidad actual. |
| WhatsApp | No existe integración | Su adopción futura está condicionada por políticas de Meta sobre productos médicos. |
| Datos de usuarios | No hay cuentas ni perfiles | Riesgo actual bajo; aumentaría si se agregan teléfono, historial o ubicación. |
| Ubicación | Directorio estático por anillos; sin GPS | Puede inducir a creer que calcula cercanía o stock por zona si no se explica. |
| Calculadora | Cálculo local a partir de una dosis introducida | Posible confusión entre cálculo económico y recomendación clínica. |
| Modelo predictivo | Señal experimental embebida | Riesgo de presentar probabilidad como certeza de stock o recomendación de compra. |

## 3. Marco normativo boliviano

El análisis se apoya en las siguientes fuentes:

| Instrumento | Función relevante para el proyecto |
|---|---|
| Constitución Política del Estado | Privacidad, intimidad, comunicaciones privadas, acceso a información y Acción de Protección de Privacidad. |
| Ley N.º 453 | Información al consumidor, precios, ofertas, publicidad engañosa y confidencialidad. |
| Decreto Supremo N.º 2130 | Desarrollo de la Ley 453, incluida la exhibición del precio final y cumplimiento de ofertas. |
| Ley N.º 164 | Derechos de usuarios TIC, privacidad de comunicaciones, datos personales, seguridad y comercio electrónico. |
| Decreto Supremo N.º 1793 | Definición y reglas de tratamiento de datos personales, consentimiento, finalidad y seguridad. |
| Ley N.º 3131 | Ejercicio profesional médico, acto médico, confidencialidad y derechos del paciente. |
| Decisión 486 de la Comunidad Andina | Derechos sobre marcas y límites para usos informativos de buena fe. |
| Políticas privadas de Meta y farmacias | Condiciones contractuales o de plataforma adicionales a la legislación estatal. |

### Texto legal verificable

La Constitución reconoce la privacidad y permite pedir conocimiento, rectificación o eliminación de datos mediante la Acción de Protección de Privacidad. La Ley 453 regula la información proporcionada en relaciones de consumo. La Ley 164 y su reglamento contienen protecciones de comunicaciones y datos personales. La Ley 3131 delimita el ejercicio profesional médico. La Decisión 486 integra el régimen andino de propiedad industrial aplicable en Bolivia.

Según la verificación realizada en fuentes legislativas oficiales, **Bolivia no contaba al 6 de noviembre de 2026 con una ley general integral de protección de datos personales promulgada y vigente**. La Cámara de Diputados publicaba un proyecto de “Ley de Protección de Datos Personales”, PL N.º 538/2025-2026, dentro de los proyectos en tratamiento. Un proyecto legislativo no debe citarse como obligación vigente.

### Interpretación razonable

La ausencia de una ley general integral no significa ausencia de protección. La Constitución, la normativa TIC, el derecho civil, la normativa médica y reglas sectoriales siguen siendo relevantes. Además, las políticas de plataformas pueden ser más restrictivas que la legislación y condicionar el acceso a sus servicios.

### Recomendación de cumplimiento

El proyecto debería adoptar desde ahora principios de finalidad, minimización, consentimiento, transparencia, seguridad y retención limitada, incluso antes de un producto público. Esto reduce retrabajo y prepara al sistema para posibles cambios legislativos.

### Revisión jurídica profesional

Antes de comercializar, un abogado deberá confirmar el conjunto completo de normas sectoriales, civiles, comerciales, sanitarias, publicitarias, tributarias y de competencia que corresponda al modelo de negocio concreto.

## 4. Protección al consumidor — Ley 453

### Texto legal verificable

- El **artículo 13** reconoce el derecho de usuarias, usuarios, consumidoras y consumidores a recibir información fidedigna, veraz, completa, adecuada, gratuita y oportuna sobre productos y servicios.
- El **artículo 14** obliga al proveedor, conforme a normativa específica, a proporcionar información accesible sobre características, uso, conservación y riesgos; consignar el precio total en moneda nacional; informar rangos de precios; ofrecer alternativas en medicamentos con el mismo principio activo o denominación genérica; e informar las condiciones de rebajas y promociones.
- El **artículo 18** exige cumplir las modalidades y términos ofertados o convenidos.
- El **artículo 25** prohíbe publicidad engañosa o abusiva y la información u omisión que provoque error o daño económico respecto de naturaleza, características, calidad, cantidad, seguridad, desempeño, durabilidad, precio o garantía.
- El **artículo 40.6** exige a los proveedores adoptar mecanismos de seguridad apropiados y confiables para proteger secreto, confidencialidad e intimidad de la información de los usuarios y consumidores.
- El **artículo 14.II del DS N.º 2130** exige que los proveedores exhiban o anuncien de forma clara, precisa y visible el precio final; si un producto tiene más de un precio marcado por el proveedor, prevalece el menor.

Fuentes: [Ley N.º 453 — Cámara de Diputados](https://diputados.gob.bo/wp-content/uploads/Leyes/Ley_N_0453.pdf) y [Reglamento aprobado por DS N.º 2130 — Servicio Estatal de Autonomías](https://sea.gob.bo/digesto/CompendioII/J/79_REG.pdf).

### Interpretación razonable

Si el comparador se presenta públicamente como fuente de precios o disponibilidad, debe evitar que datos históricos o inferidos parezcan ofertas vigentes garantizadas. Una etiqueta “precio referencial observado” y la fecha de captura permiten comunicar con mayor precisión lo que realmente se conoce.

La obligación de ofrecer alternativas de medicamentos corresponde al proveedor en el contexto previsto por la Ley 453. No autoriza al comparador a recomendar sustituciones terapéuticas ni a concluir que dos presentaciones son clínicamente intercambiables.

### Qué NO dice la Ley 453

- La Ley 453 **no autoriza expresamente el scraping**.
- La Ley 453 **no prohíbe expresamente el scraping**.
- El derecho del consumidor a recibir información no equivale automáticamente a una licencia para extracción automatizada, reproducción, republicación o explotación comercial de información de un sitio privado.
- La visibilidad pública de un precio no elimina por sí sola términos contractuales, instrucciones técnicas, derechos de propiedad intelectual o deberes de competencia leal.

### Recomendaciones de cumplimiento

- Mostrar cadena, URL fuente, fecha y hora de extracción junto a cada dato.
- Indicar por cuánto tiempo se considera vigente una captura dentro del comparador.
- Presentar el precio como **referencial** y no como precio garantizado.
- Distinguir “publicado en catálogo”, “disponibilidad reportada” y “stock confirmado”.
- Evitar expresiones como “abastecimiento asegurado”, “precio garantizado” o “acudir con confianza”.
- Incluir un canal para que farmacias o usuarios reporten errores y solicitar corrección.
- Registrar la rectificación sin borrar la trazabilidad de la fuente original.

### Revisión jurídica profesional

Debe determinarse si un futuro servicio comercial califica como proveedor frente a sus propios usuarios y qué obligaciones de contratos de adhesión, reclamos, publicidad y responsabilidad le resultarían directamente aplicables.

## 5. Telecomunicaciones y privacidad — Ley 164

### Texto legal verificable

La Ley N.º 164 establece el principio de inviolabilidad de comunicaciones privadas. El artículo 54 reconoce, entre otros, los derechos de las usuarias y usuarios a:

- información clara, precisa, cierta, completa, oportuna y gratuita sobre servicios TIC;
- respeto a la privacidad e inviolabilidad de comunicaciones;
- decidir qué datos personales aparecen en guías y solicitar su corrección o supresión;
- protección de datos personales frente a publicidad no autorizada.

El artículo 55 obliga a no causar daño a instalaciones, redes y equipos ni interferencias perjudiciales. El artículo 56 obliga a operadores y proveedores a garantizar inviolabilidad y secreto de las comunicaciones, protección de datos personales e intimidad. El artículo 72 promueve la protección de usuarios y la seguridad informática y de redes. El artículo 85 exige un ambiente técnicamente confiable para la oferta electrónica de bienes y servicios. Fuente: [Ley N.º 164 — Ministerio de Justicia](https://www.justicia.gob.bo/cms/files/LEY%20N%C2%BA%20164%20Gaceta%20Oficial_gs7rr7i4.pdf).

El DS N.º 1793 define:

- **dato personal:** información concerniente a una persona natural o jurídica que la identifica o la hace identificable;
- **tratamiento:** cualquier operación o conjunto de operaciones como recolección, almacenamiento, uso, circulación o supresión.

Su artículo 56 dispone que el tratamiento técnico en los sectores público y privado requiere conocimiento previo y consentimiento expreso del titular; información sobre finalidad, destinatarios, responsable y derechos; limitación de uso a la finalidad informada; consentimiento u orden judicial para comunicar a terceros; y medidas técnicas y organizativas de seguridad. El artículo 57 regula comunicaciones comerciales digitales, identificación del remitente y mecanismos para aceptar o rechazar mensajes futuros. Fuente: [DS N.º 1793 — CTIC-EPB](https://www.ctic.gob.bo/wp-content/uploads/2016/03/DS-N%C2%B0-1793-Reglamento-a-la-Ley-N%C2%B0164-para-el-Desarrollo-de-Tecnolog%C3%ADas-de-la-Informaci%C3%B3n-y-Comunicaci%C3%B3n.pdf).

### Interpretación razonable

La Ley 164 no contiene una disposición que autorice o prohíba expresamente el scraping. Consultar una ficha pública sin credenciales no equivale automáticamente a interceptar una comunicación privada. Sin embargo, una página pública tampoco equivale automáticamente a autorización de reutilización automatizada o comercial.

El análisis cambia si se accede a sesiones privadas, cuentas, cookies de terceros, endpoints protegidos, información no destinada al público o si se afecta la disponibilidad del sistema.

### Recomendaciones de cumplimiento

Para una futura corrección técnica de los scrapers se recomienda:

- limitar solicitudes por dominio y unidad de tiempo;
- usar cache para no repetir consultas sin necesidad;
- aplicar backoff creciente ante fallos transitorios;
- detenerse ante respuestas `403`, `429`, CAPTCHA o nuevos mecanismos de protección;
- no intentar resolver, eludir ni automatizar CAPTCHA;
- no acceder a sesiones privadas, cuentas o APIs que requieran credenciales sin convenio;
- registrar fecha, dominio, endpoint, código de respuesta, volumen y motivo de cada ejecución;
- revisar `robots.txt` y términos antes de cada despliegue o cuando cambie el sitio;
- definir una frecuencia máxima, responsable y procedimiento de suspensión.

Estas son recomendaciones para trabajo futuro; este SCRUM no modifica los scrapers.

### Revisión jurídica profesional

La Ley 164 no debe analizarse aislada. El alcance de acceso no autorizado, responsabilidad por daño, obligaciones contractuales y aplicación del DS 1793 a un chatbot privado comercial requiere revisión profesional con la arquitectura final disponible.

## 6. Constitución y protección de privacidad

### Texto legal verificable

- El **artículo 21.2** reconoce privacidad, intimidad, honra, honor, propia imagen y dignidad.
- El **artículo 21.6** reconoce acceso, interpretación, análisis y comunicación libre de información.
- El **artículo 25** protege domicilio y comunicaciones privadas; prohíbe interceptar conversaciones o comunicaciones privadas fuera de las condiciones constitucionales y legales.
- El **artículo 130** permite interponer la Acción de Protección de Privacidad para conocer, objetar, eliminar o rectificar datos registrados en medios físicos o electrónicos, archivos o bancos de datos públicos o privados, cuando exista impedimento indebido o afectación de intimidad, privacidad, imagen, honra o reputación.
- El **artículo 131** permite que el juez ordene revelación, eliminación o rectificación de los datos impugnados.

Fuente: [Constitución Política del Estado — Órgano Electoral Plurinacional](https://web.oep.org.bo/wp-content/uploads/2016/12/constitucion_politica_estado.pdf).

### Definiciones sencillas

| Concepto | Explicación aplicable al proyecto |
|---|---|
| Privacidad | Capacidad de la persona para mantener aspectos de su vida personal fuera de usos o divulgaciones no autorizadas. |
| Dato personal | Información que, sola o combinada, identifica o hace identificable a una persona. |
| Dato relacionado con salud | Información que revela o permite inferir enfermedad, tratamiento, medicamento, dosis, receta o situación clínica. |
| Dato anónimo | Información respecto de la cual no existe una posibilidad razonable de identificar nuevamente a la persona. |
| Dato agregado | Resultado estadístico de varias personas presentado sin individualización; puede dejar de ser seguro si el grupo es muy pequeño. |
| Acción de Protección de Privacidad | Garantía constitucional para conocer, objetar, rectificar o eliminar datos y proteger intimidad, imagen, honra y reputación. |

### Interpretación razonable

El número de teléfono identifica directamente a una persona. El medicamento consultado puede revelar un tratamiento. Un historial muestra patrones. Una ubicación o GPS revela desplazamientos y lugares frecuentes. En conjunto, **teléfono + medicamento + historial + ubicación** puede formar un perfil personal relacionado con salud, aunque el usuario nunca escriba expresamente su diagnóstico.

Sustituir el nombre por un código no vuelve anónimos los datos si siguen asociados a teléfono, voz, GPS, fechas precisas u otros atributos reidentificadores.

El derecho de acceso a información del artículo 21.6 tampoco constituye por sí solo una autorización para incumplir términos privados, eludir controles o reutilizar comercialmente cualquier contenido accesible.

### Recomendación de cumplimiento

Recopilar únicamente lo imprescindible, explicar la finalidad antes de la recolección, separar datos de contacto de resultados de investigación y habilitar mecanismos de acceso, corrección y eliminación.

## 7. Web scraping

### Descripción técnica verificada

**Farmacorp:** ejecuta búsquedas con 16 términos mediante `requests` contra `search/suggest.json`. Para productos únicos intenta consultar una ficha `.json`. Usa un encabezado que se presenta como Chrome 120. No se autentica y no conserva HTML.

**Farmacias Chávez:** abre el sitio principal con Chromium headless mediante Playwright, busca “insulina”, espera resultados y extrae enlaces `/p/` del DOM. Usa pausas fijas de aproximadamente 2, 1 y 5 segundos en distintas etapas.

**Farmacias Telchi:** realiza seis búsquedas públicas de WooCommerce con `requests`, analiza HTML con BeautifulSoup y asigna “Disponible” a todos los resultados aceptados, sin una comprobación diferenciada de inventario.

No existe en el repositorio un scheduler que permita establecer una frecuencia operativa automática. La documentación habla de extracción periódica, pero la ejecución real disponible es manual. Tampoco existen reintentos con backoff, control central de tasa o lectura de `robots.txt`.

| Riesgo | Situación actual | Nivel | Medida recomendada |
|---|---|---:|---|
| Farmacorp: política técnica | El scraper usa endpoints de búsqueda y producto sin implementar instrucciones actuales para agentes | Alto | Revisar arquitectura y solicitar contacto/autorización antes de escalar. |
| Chávez: automatización | Playwright carga el sitio y ejecuta una búsqueda pública | Medio | Definir tasa, revisar términos y detenerse ante barreras. |
| Telchi: exactitud | Todo resultado aceptado se marca “Disponible” | Alto | Usar “publicado; disponibilidad no verificada” hasta contar con evidencia. |
| Autenticación | Ningún scraper usa login o credenciales | Bajo actual | No incorporar autenticación sin autorización formal. |
| CAPTCHA | No existe solver ni evasión | Bajo actual | Mantener prohibición de evasión y detener la ejecución si aparece. |
| Mecanismos técnicos | No hay bypass explícito de tokens o bloqueos | Bajo actual | No introducir bypass; registrar y respetar bloqueos. |
| User-Agent | Se presenta como navegador Chrome y no identifica al proyecto | Medio | Usar identificación transparente y contacto cuando la fuente lo admita. |
| `robots.txt` | El código no lo consulta | Alto en Farmacorp | Comprobar y registrar instrucciones antes de cada ejecución. |
| Frecuencia | No hay scheduler ni límite documentado | Medio | Establecer frecuencia máxima y presupuesto de solicitudes. |
| Pausas | Solo Chávez tiene pausas fijas; Farmacorp y Telchi no | Medio | Incorporar rate limiting y pausas prudentes. |
| Reintentos | No hay estrategia explícita | Medio | Reintentos limitados con backoff solo para fallos transitorios. |
| Carga | Farmacorp combina múltiples búsquedas y fichas; Chávez carga navegador completo | Medio | Cache, deduplicación y consultas incrementales. |
| HTML | No se guarda HTML completo | Bajo | Mantener almacenamiento mínimo y auditable. |
| Datos estructurados | Se guardan CSV, JSON y snapshots históricos | Medio | Política de retención, deduplicación y control de acceso. |
| Timestamps | Cada registro tiene fecha/hora UTC y los snapshots tienen fecha | Favorable | Conservar y mostrar la fecha al usuario. |
| URLs | Se conserva URL del producto | Favorable | Mostrar enlace fuente y vigilar enlaces rotos. |
| Stock | Farmacorp y Chávez interpretan señales del catálogo; Telchi presume disponibilidad | Alto | Diferenciar catálogo, disponibilidad reportada y stock confirmado. |
| Clasificación | El bruto incluye jeringas, agujas y falsos positivos | Medio | Validar antes de publicar y mantener bitácora de descartes. |
| Propiedad intelectual | Se reutilizan nombres y hechos; no se copian imágenes en el scraper | Medio | Minimizar contenido y no copiar descripciones, logos o fotografías. |
| Vigencia | El HTML mantiene una captura sin actualización durante su uso | Alto público | Fecha visible, expiración y confirmación con farmacia. |
| APIs/convenios | No hay integración autorizada | Alto al escalar | Transición a UCP, API, feed o convenio. |

### Farmacorp: `robots.txt` e instrucciones para agentes

Al 6 de noviembre de 2026, el [`robots.txt` de Farmacorp](https://farmacorp.com/robots.txt):

- permite el rastreo de muchas páginas públicas del escaparate;
- bloquea rutas privadas, transaccionales o internas;
- publica instrucciones específicas para agentes;
- exige que las solicitudes iniciadas por agentes se identifiquen mediante los mecanismos requeridos por la integración;
- orienta a utilizar interfaces UCP y herramientas WebMCP soportadas;
- indica que no se utilicen atajos scriptados para acciones de compra.

### Interpretación razonable

`robots.txt` es una señal técnica y de política, no una sentencia ni una norma estatal que determine por sí sola la licitud. Que una ruta esté permitida para rastreo tampoco concede automáticamente derechos de republicación o explotación comercial. A la inversa, una instrucción de rastreo no reemplaza el análisis de términos, contrato, carga, propiedad intelectual y finalidad.

El scraper actual de Farmacorp no implementa identificación de agente ni UCP/WebMCP. Por ello **requiere revisión técnica y, preferentemente, contacto formal antes de escalar o utilizarse en un producto público/comercial**.

### Términos públicos de las farmacias

- **Farmacorp:** publica términos generales. Indica que precios y existencias pueden cambiar sin previo aviso, que la disponibilidad depende del movimiento diario y que precios web pueden no aplicar a otros canales. No se localizó en esos términos una cláusula que use expresamente “bot”, “robot”, “scraping” o “extracción automatizada”. Fuente: [Términos de Farmacorp](https://farmacorp.com/policies/terms-of-service) y [Preguntas frecuentes](https://farmacorp.com/pages/preguntas-frecuentes).
- **Farmacias Chávez:** no se localizó mediante navegación y búsqueda pública una política general verificable sobre bots, scraping, reproducción o uso comercial. “No localizada” no significa “inexistente” ni implica autorización.
- **Farmacias Telchi:** el sitio enlazaba condiciones de campañas específicas, pero no se localizó una política general verificable aplicable al catálogo completo sobre bots o scraping. Las condiciones de una campaña no deben extenderse al sitio entero sin fundamento.

### Revisión jurídica profesional

Antes del uso comercial debe analizarse la formación y alcance de contratos por navegación, derechos de autor sobre contenidos o selección, competencia desleal, eventual protección de bases de datos, atribución y responsabilidad por republicación.

## 8. Propiedad intelectual y marcas — Decisión 486

### Texto legal verificable

- El **artículo 154** establece que el derecho al uso exclusivo de una marca se adquiere por registro ante la oficina nacional competente.
- El **artículo 155** permite al titular impedir actos de terceros, incluidos usos que puedan causar confusión, riesgo de asociación, dilución o aprovechamiento injusto.
- El **artículo 156** identifica actos que pueden constituir uso de un signo en el comercio.
- El **artículo 157** permite ciertos usos sin consentimiento cuando se realizan de buena fe, no a título de marca, con propósito de identificación o información y sin capacidad de inducir a confusión sobre la procedencia. También contempla anunciar, incluso en publicidad comparativa, ofrecer o indicar existencia o disponibilidad de productos legítimamente marcados bajo esas condiciones.

Fuentes: [Decisión 486 — Gaceta Oficial de la Comunidad Andina/TJCA](https://www.tribunalandino.org.ec/decisiones/normativa/DEC486-sentencia.pdf) e [Interpretación Prejudicial 367-IP-2017](https://www.tribunalandino.org.ec/decisiones/IP/367-IP-2017.pdf).

### Interpretación razonable aplicada al MVP

Mencionar **Lantus, Novolin, Apidra, Toujeo** y otras marcas en texto para identificar el producto observado puede encajar en una finalidad nominativa e informativa si el uso es necesario, exacto, de buena fe y no crea confusión. Esto no concede al proyecto derechos sobre esas marcas.

| Uso | Evaluación prudente |
|---|---|
| A. Nombre de marca en texto | Menor riesgo cuando identifica el producto y se acompaña de principio activo, presentación y fuente. |
| B. Logo | Mayor riesgo; puede sugerir identidad, afiliación o patrocinio. Requiere autorización o análisis específico. |
| C. Empaque | Puede incorporar marca, diseño, imagen comercial y otros derechos. Evitar sin permiso. |
| D. Fotografías | Pueden estar protegidas por derecho de autor además de mostrar marcas. No reutilizar sin licencia. |
| E. Diseño que parezca patrocinio | Riesgo alto de asociación o confusión; debe evitarse. |

### Recomendaciones de cumplimiento

- Usar nombres de marca en texto plano y solo para identificar el producto.
- Presentar principio activo, concentración, formato y laboratorio junto a la marca.
- No usar logos, empaques, tipografías, colores corporativos o fotografías como decoración.
- No denominar al comparador con una marca ajena.
- No afirmar que una farmacia o laboratorio recomienda, patrocina o autoriza el proyecto sin convenio escrito.
- Mantener neutralidad entre cadenas y productos.

Texto recomendado:

> **Las marcas mencionadas pertenecen a sus respectivos titulares. Este proyecto no mantiene afiliación, patrocinio ni autorización de los laboratorios o farmacias mencionados, salvo que se indique expresamente.**

### Revisión jurídica profesional

La aplicación del artículo 157 depende del contexto visual y comercial, la buena fe, los registros concretos y la posible notoriedad de cada marca. Un producto comercial necesita auditoría marcaria antes de publicarse.

## 9. Datos personales y datos relacionados con salud

### Principio de minimización

El proyecto debe recopilar únicamente los datos estrictamente necesarios para una función definida. Que un dato sea útil para análisis no significa que sea necesario. Si el comparador puede funcionar sin identificar a la persona, debe preferirse esa arquitectura.

| Dato | Necesidad | Riesgo | Recomendación |
|---|---|---:|---|
| Nombre | **Evitar** | Medio | No pedirlo para buscar o comparar. |
| Teléfono | **Necesario solo si se usa WhatsApp** | Alto | Utilizarlo únicamente para mensajería consentida; no convertirlo en identificador analítico. |
| Edad exacta | **Evitar** | Medio | Para investigación, usar rango opcional y separado de identidad. |
| Ubicación aproximada | **Opcional** | Medio | Permitir selección manual de zona; no asociar a identidad sin necesidad. |
| Anillo | **Opcional** | Bajo/medio | Usarlo como filtro temporal, no como historial personal. |
| GPS | **Evitar** | Muy alto | No solicitarlo para el MVP; usar anillo o zona seleccionada. |
| Medicamento consultado | **Necesario para la búsqueda actual** | Alto si se vincula | Procesar la consulta sin historial por defecto. |
| Historial de búsquedas | **Evitar** | Alto | No crear perfiles longitudinales de medicamentos. |
| Dosis | **Opcional para calculadora** | Alto | Procesar localmente, sin transmisión ni persistencia; evaluar si el beneficio justifica pedirla. |
| Receta | **Evitar** | Muy alto | No pedir fotografías ni contenido de recetas. |
| Diagnóstico/enfermedad | **Evitar** | Muy alto | No solicitar; no es necesario para comparar precios. |
| Mensajes | **Necesario solo durante un chat** | Alto | Retención mínima, finalidad limitada y acceso restringido. |
| Cuidador | **Opcional** | Medio | Registrar solo el rol si es necesario; no identidad completa. |
| Audio | **Evitar** | Alto | No grabar; en investigación requerir consentimiento separado y plazo de eliminación. |

### Recomendaciones de cumplimiento

- No crear historial por defecto.
- Procesar localmente cuando sea posible, como ocurre actualmente con la calculadora.
- Separar la lista de contacto para coordinar una investigación de las respuestas y resultados.
- Usar códigos aleatorios, no iniciales ni fechas de nacimiento.
- Definir plazos de retención y eliminación antes de recopilar.
- Restringir accesos por rol y mantener registro de accesos administrativos.
- Informar finalidad, responsable, destinatarios, plazo y derechos antes de obtener consentimiento.
- Solicitar consentimientos separados para mensajes, investigación y grabaciones.
- No reutilizar datos para marketing, perfilado o entrenamiento sin nueva evaluación y consentimiento compatible.

### Interpretación razonable

El medicamento, dosis o conversación pueden ser datos relacionados con salud porque permiten inferir tratamiento o enfermedad. Su riesgo aumenta al vincularlos con teléfono, ubicación, cuidador o historial.

### Revisión jurídica profesional

El alcance exacto del DS 1793 sobre cada arquitectura privada y las transferencias a proveedores extranjeros debe confirmarse antes de contratar nube, analítica, chatbot o mensajería.

## 10. WhatsApp Business / Meta

### Texto de política verificable

La [Política de Mensajes de WhatsApp Business](https://business.whatsapp.com/policy/preview?lang=es_LA), consultada el 6 de noviembre de 2026, prohíbe utilizar los Servicios de WhatsApp Business para **comprar, vender, promocionar o facilitar el intercambio** de determinados bienes o servicios regulados o restringidos. La lista incluye drogas —recetadas, recreativas o de otro tipo— y productos médicos y de salud. La política señala que estas prohibiciones se aplican independientemente de licencias o registros locales.

La misma política exige, entre otros elementos:

- que la persona entregue su número y otorgue consentimiento explícito para recibir mensajes posteriores;
- identificación clara de la empresa;
- respeto a solicitudes de baja o bloqueo;
- avisos, permisos y consentimientos para recopilar, usar y compartir información;
- política de privacidad publicada;
- plantillas aprobadas para conversaciones iniciadas por la empresa fuera de la ventana aplicable;
- vías claras de escalamiento desde respuestas automáticas hacia atención humana u otro soporte;
- cumplimiento de requisitos aplicables al tratamiento de información de salud.

### Evaluación por caso

| Caso | Actividad | Evaluación prudente |
|---|---|---|
| A | Información general no comercial sobre cómo funciona el proyecto o dónde confirmar datos | Menor riesgo, siempre que no promocione productos ni simule atención médica. |
| B | Comparador de precios y disponibilidad de insulina | Zona de riesgo: puede interpretarse como promoción o facilitación del intercambio de productos médicos. No debe asumirse permitido. |
| C | Venta, reserva, carrito, pago o confirmación de medicamentos | Incompatible con la restricción identificada; no debe implementarse dentro del canal. |
| D | Recomendación médica, de marca, dosis, equivalencia o sustitución | Riesgo alto de telemedicina/acto clínico y de daño; debe evitarse. |
| E | Recopilación de diagnóstico, receta, dosis, síntomas o historial | Riesgo muy alto; exige evaluación jurídica, seguridad reforzada y compatibilidad con políticas. Para este proyecto debe evitarse. |

### Interpretación razonable

Informar no es necesariamente lo mismo que vender. Sin embargo, la amplitud de las expresiones “promocionar” y “facilitar el intercambio” impide afirmar que un comparador de insulina puede implementarse libremente en WhatsApp. El caso B debe tratarse como una incertidumbre de plataforma, no como una autorización implícita.

### Recomendaciones de cumplimiento

- Obtener validación formal y documentada de Meta o de un Business Solution Provider antes de adoptar WhatsApp.
- Volver a revisar políticas inmediatamente antes del piloto y del lanzamiento.
- No vender, reservar, cobrar ni confirmar pedidos de medicamentos dentro del canal.
- Mantener un enfoque informativo y remitir la confirmación de precio/stock a la farmacia.
- Implementar opt-in específico, registro de consentimiento y mecanismo de baja.
- Publicar política de privacidad antes de captar números o conversaciones.
- Mantener retención mínima y no reenviar chats a otros clientes.
- Proporcionar escalamiento humano claro.
- Diseñar un canal alternativo si Meta rechaza el caso de uso.

### Revisión jurídica profesional

La aprobación de una plantilla o cuenta no equivale a dictamen sobre legislación boliviana. Deben cumplirse simultáneamente política de plataforma y derecho aplicable.

## 11. Responsabilidad médica

### Texto legal verificable

La [Ley N.º 3131 del Ejercicio Profesional Médico](https://www.minsalud.gob.bo/component/jdownloads/?Itemid=465&catid=12&id=142%3Aley-no-3131&task=download.send) regula el ejercicio profesional médico. Define el acto médico como intervención profesional del médico respaldada por protocolos y normativa. Protege secreto médico, confidencialidad, intimidad e información del paciente. Exige matrícula para el ejercicio profesional y reconoce documentos médicos oficiales, incluida la receta.

El [Reglamento de la Ley N.º 3131, DS N.º 28562](https://www.lexivox.org/norms/BO-DS-28562.html), utilizado como fuente normativa complementaria, define la receta médica y vincula la prescripción a requisitos profesionales.

### Delimitación del producto

El proyecto debe presentarse como:

- herramienta informativa;
- comparador de precios observados;
- comparador de disponibilidad publicada o reportada;
- apoyo para localizar opciones y confirmar con la farmacia.

No debe presentarse como:

- diagnóstico;
- prescripción;
- recomendación de dosis;
- confirmación de equivalencia;
- sustitución terapéutica;
- recomendación de cambiar de insulina, presentación o laboratorio;
- consejo médico personalizado.

### Riesgos actuales de comunicación

| Expresión o función | Riesgo |
|---|---|
| “Dosis habitual frecuente: 20 a 40 UI” | Puede interpretarse como referencia clínica o dosis sugerida. |
| “Abastecimiento asegurado” | Convierte una señal experimental en garantía. |
| “Acudir con confianza” | Puede inducir desplazamiento o compra sin confirmación. |
| “Comprar con 5 días de anticipación” | Puede parecer consejo general de tratamiento o compra no respaldado para cada paciente. |
| Calculadora basada en dosis | Puede confundirse con cálculo terapéutico aunque use una dosis prescrita. |
| Semáforo predictivo | Puede confundirse con certeza de stock, recomendación de compra o alerta clínica. |

### Interpretación razonable

La calculadora actual no prescribe una dosis: utiliza el valor introducido para un cálculo económico local. No obstante, la interfaz debe explicar con claridad que no valida la dosis, frecuencia, presentación ni producto. Tampoco debe normalizar una cifra como “habitual”.

### Recomendación de cumplimiento

Eliminar o reformular las expresiones anteriores, separar visualmente stock observado de probabilidad experimental y mostrar el disclaimer clínico antes o junto a cualquier calculadora.

Un disclaimer **no compensa** una funcionalidad que materialmente diagnostique, prescriba, recomiende dosis, sugiera equivalencias o induzca cambios de tratamiento. La conducta real del producto prevalece sobre su etiqueta.

### Revisión jurídica profesional

Si se incorporan personalización clínica, reglas por diagnóstico, interpretación de recetas o recomendaciones, debe realizarse una evaluación sanitaria completa antes de desarrollar o desplegar la función.

## 12. Matriz general de riesgos legales

Prioridades utilizadas:

- **P0:** antes de publicación.
- **P1:** antes de escalar o comercializar.
- **P2:** mejora recomendada.

| Tema | Norma/política | Situación actual | Riesgo | Recomendación | Prioridad | Fuente |
|---|---|---|---:|---|:---:|---|
| Scraping | Leyes 453/164, términos y `robots.txt` | Automatización de tres sitios sin convenio | Alto en Farmacorp; medio en otras fuentes | Revisar Farmacorp y planificar autorización/API | P0/P1 | Leyes citadas; sitios oficiales |
| Precios | Ley 453 arts. 13, 14 y 25; DS 2130 | Datos embebidos sin fecha visible al usuario | Alto público | Mostrar fuente, captura, vigencia y carácter referencial | P0 | Cámara de Diputados/SEA |
| Consumidor | Ley 453 | Existen mensajes que pueden parecer garantías | Alto | Eliminar afirmaciones absolutas y habilitar corrección | P0 | Cámara de Diputados |
| Marcas | Decisión 486 arts. 154–157 | Nombres de marcas en texto, sin logos | Medio | Uso nominativo, no afiliación y auditoría antes de comercializar | P0/P1 | CAN/TJCA |
| Propiedad intelectual | Régimen aplicable y términos | No se copian imágenes, pero se reutilizan nombres y hechos | Medio | No copiar descripciones, fotos, logos o diseño | P1 | Sitios/TJCA; revisión profesional |
| Privacidad | CPE arts. 21, 25, 130–131; DS 1793 | Sin cuentas ni backend de usuario | Bajo actual; alto con chatbot | Minimización, consentimiento y seguridad desde el diseño | P0 futuro | OEP/CTIC |
| Datos de salud | CPE, DS 1793, Ley 3131 | Dosis transitoria y medicamento consultado | Medio | No persistir, no perfilar y evitar diagnóstico/receta | P0 | OEP/CTIC/Salud |
| WhatsApp | Política de WhatsApp Business | No implementado | Alto futuro | Validación Meta/BSP y canal alternativo | P1 | Meta |
| Responsabilidad médica | Ley 3131 y reglamento | Calculadora y textos ambiguos | Alto público | Delimitar función, retirar consejos y añadir disclaimer | P0 | Ministerio de Salud |
| Actualización | Ley 453; términos de Farmacorp | HTML estático y stock no confirmado | Alto | Fecha, expiración y confirmación directa | P0 | Ley 453/Farmacorp |
| API/convenios | Políticas y contratos | No existen acuerdos estructurados | Alto al escalar | Contacto, convenio, API/feed/UCP | P1 | Farmacias |
| Uso comercial | Conjunto normativo | Proyecto académico, sin modelo contractual final | Alto antes de monetizar | Revisión legal integral y acuerdos | P1 | Fuentes múltiples |
| Seguridad | Ley 164 y DS 1793 | No hay backend personal actual | Bajo actual | Plan de roles, cifrado, incidentes y retención | P1 | Justicia/CTIC |
| Reclamos | Ley 453 | No existe canal propio formal en el MVP | Medio público | Canal de corrección y respuesta documentada | P0/P2 | Cámara de Diputados |

## 13. Proyecto académico vs producto comercial

| Dimensión | A. MVP académico/piloto | B. Producto público | C. Producto comercial |
|---|---|---|---|
| Scraping | Baja frecuencia, datos públicos, sin evasión | Controles técnicos y transparencia obligatorios | Convenio/API preferente y revisión contractual |
| Usuarios | Prueba pequeña con códigos | Público indeterminado | Clientes, soporte y potencial relación de consumo |
| Privacidad | Datos de investigación mínimos y separados | Aviso de privacidad y derechos | Gobierno formal de datos, proveedores y transferencias |
| Consentimiento | Consentimiento informado del piloto | Consentimiento por finalidad si se recopilan datos | Evidencia de consentimiento, bajas y gestión de derechos |
| Marcas | Texto mínimo para identificar | Disclaimer y diseño sin confusión | Auditoría marcaria y acuerdos cuando correspondan |
| Precios | Captura exploratoria | Fecha, fuente y carácter referencial | Mecanismo fiable de actualización y rectificación |
| Disponibilidad | No se presenta como inventario real | Etiqueta de no verificación | Feed autorizado o confirmación por sucursal |
| WhatsApp | No necesario | No adoptar sin validación | Validación Meta/BSP y cumplimiento continuo; sin ventas médicas |
| Seguridad | Archivos bajo control del equipo | Controles básicos, mínima telemetría | Cifrado, roles, logs, incidentes y evaluación de terceros |
| Responsabilidad | Exposición controlada y moderada | Mayor confianza y posibilidad de daño | Responsabilidad contractual, comercial y reputacional superior |
| Documentación | Protocolo, consentimiento y limitaciones | Privacidad, disclaimers y canal de corrección | Términos, privacidad, retención, seguridad, reclamos y contratos |
| Acuerdos | Deseables, no siempre disponibles en piloto cerrado | Recomendables antes de escalar | Necesarios para un suministro estable y defendible |

### Interpretación razonable

La finalidad académica reduce exposición y escala, pero no elimina derechos de terceros ni deberes hacia participantes. Publicar el sistema cambia el público, la confianza y el impacto. Comercializarlo agrega incentivos económicos, relación de consumo, publicidad y dependencia operacional de datos de terceros.

## 14. Hoja de ruta de cumplimiento

### P0 — Antes de publicación

- Eliminar “abastecimiento asegurado”, “garantizado”, “acudir con confianza” y expresiones equivalentes.
- Mostrar fuente, URL, fecha/hora y carácter referencial de precios.
- Aclarar que la presencia en Telchi no demuestra stock y que ningún estado equivale a inventario por sucursal.
- Incorporar disclaimer clínico, de marcas, precios e independencia.
- No presentar el semáforo como certeza ni recomendación médica.
- No recopilar datos personales o clínicos que el comparador no necesita.
- Revisar el scraper de Farmacorp frente a sus instrucciones actuales antes de nuevas ejecuciones a escala.
- Habilitar un canal de corrección de información.

### P1 — Antes de escalar

- Implementar rate limiting por dominio.
- Incorporar cache y consultas incrementales.
- Aplicar backoff limitado ante fallos transitorios.
- Detenerse ante `403`, `429`, CAPTCHA o bloqueo.
- Consultar y registrar `robots.txt` y términos.
- Definir frecuencia máxima, responsable y bitácora de ejecuciones.
- Documentar política de privacidad, consentimiento y retención si aparecen cuentas o mensajes.
- Contactar formalmente a Farmacorp, Chávez y Telchi.
- Solicitar feed, API, UCP o acceso estructurado.
- Definir proceso de respuesta a correcciones y reclamos.

### P2 — Antes de comercializar

- Formalizar convenios con las fuentes.
- Migrar a API, feed o mecanismo oficial.
- Publicar términos y condiciones propios.
- Implementar programa formal de privacidad y seguridad.
- Definir política de retención y eliminación.
- Realizar auditoría marcaria y de contenidos.
- Obtener revisión legal profesional en Bolivia.
- Revisar competencia, publicidad, consumo, salud y contratación.
- Volver a revisar políticas de Meta y obtener validación formal si se considera WhatsApp.
- Preparar plan de incidentes, continuidad y retiro/corrección de datos erróneos.

## 15. Transición scraping → API / convenios

### Fase 1 — MVP académico

- Scraping de baja frecuencia sobre datos visibles sin login.
- Sin CAPTCHA, evasión, credenciales ni rutas privadas.
- Almacenamiento estructurado mínimo con URL y timestamp.
- Resultados presentados como captura académica, no inventario garantizado.

### Fase 2 — Contacto formal

- Presentar el objetivo social y académico.
- Informar los campos, frecuencia y forma de atribución.
- Solicitar autorización de acceso, uso y republicación.
- Consultar condiciones para una eventual fase comercial.

### Fase 3 — Convenio

- Definir datos permitidos, frecuencia, finalidad y responsables.
- Acordar significado de stock y alcance por sucursal.
- Fijar seguridad, correcciones, vigencia, soporte y terminación.
- Regular uso de nombres, marcas, logos y enlaces.

### Fase 4 — API o feed oficial

- Autenticación autorizada y límites de tasa conocidos.
- Esquema versionado y documentación técnica.
- Timestamps de origen y estados definidos.
- Menor dependencia de estructura HTML.

### Fase 5 — Producto comercial

- Acuerdos vigentes con fuentes críticas.
- Auditoría de privacidad, seguridad, consumidor y marcas.
- Procesos de soporte, reclamos y corrección.
- Revisión jurídica profesional previa al lanzamiento.

### Ventajas de la transición

| Ventaja | Efecto esperado |
|---|---|
| Datos más confiables | Menos inferencias y errores de extracción. |
| Stock por sucursal | Evita presentar cobertura de red como inventario local. |
| Menor riesgo contractual | La autorización define usos y límites. |
| Menor carga | El feed evita recorrer múltiples páginas. |
| Timestamps de origen | Permiten mostrar vigencia real. |
| Estabilidad | Menos roturas por cambios de HTML o selectores. |
| Mejor soporte | Existe un canal formal para correcciones. |
| Escalabilidad | La frecuencia y volumen quedan acordados. |

## 16. Disclaimer recomendado

### Disclaimer clínico

> **Información referencial basada en datos publicados por las farmacias y capturas realizadas en una fecha determinada. Este comparador no brinda diagnóstico, prescripción ni recomendaciones de dosis o cambios de tratamiento y no sustituye la atención de un profesional de salud. No cambie de insulina, presentación ni dosis sin indicación médica. Confirme precio, presentación y disponibilidad directamente con la farmacia antes de comprar.**

### Disclaimer de marcas

> **Las marcas mencionadas pertenecen a sus respectivos titulares. Su inclusión tiene finalidad identificativa e informativa. El proyecto no adquiere derechos sobre ellas.**

### Disclaimer de precios y disponibilidad

> **Los precios y estados corresponden a la fuente y fecha indicadas, pueden cambiar sin aviso y no garantizan inventario, precio final ni disponibilidad en una sucursal. Verifique la información directamente con la farmacia.**

### Disclaimer de independencia

> **Este proyecto académico es independiente y no mantiene afiliación, patrocinio ni autorización de los laboratorios o farmacias mencionados, salvo que se indique expresamente mediante un acuerdo verificable.**

Los disclaimers deben mostrarse de forma legible y cercana a la decisión correspondiente. No deben quedar ocultos en términos extensos ni utilizarse para contradecir afirmaciones principales más categóricas.

## 17. Limitaciones jurídicas

- Este documento no es dictamen legal ni determina responsabilidad en un caso concreto.
- Normas, términos, `robots.txt` y políticas de Meta pueden cambiar después de la fecha de consulta.
- No localizar una política pública de Chávez o Telchi no demuestra que no exista ni implica autorización.
- La aceptación y alcance contractual de términos por navegación o automatización depende de hechos y criterios jurídicos.
- El análisis de competencia desleal requiere conocer modelo de negocio, presentación comparativa, mercado y efectos.
- La protección por derecho de autor de textos, fotografías, selección, organización o interfaces debe evaluarse por contenido concreto.
- La visibilidad pública de hechos comerciales no concede automáticamente derecho a reproducir todos los elementos de una página.
- La aplicación precisa del DS 1793 a arquitecturas privadas, transferencias internacionales y proveedores futuros requiere revisión.
- Las políticas de Meta son privadas, pueden ser más restrictivas que el derecho local y admiten decisiones de aplicación propias.
- Una autorización de plataforma no sustituye cumplimiento legal; cumplimiento legal tampoco garantiza aceptación de plataforma.
- Un disclaimer no elimina responsabilidad si el diseño real induce a error, prescribe o causa daño.
- Un producto comercial requiere analizar además contratos, publicidad, reclamos, licencias, tributación, seguridad y estructura empresarial.
- El proyecto de ley integral de datos puede cambiar o ser promulgado en el futuro; debe vigilarse su evolución sin tratarlo hoy como ley vigente.

## 18. Conclusión de viabilidad

La conclusión no es que el proyecto “sea legal” o “ilegal”. La viabilidad depende del escenario, la escala, las fuentes, el diseño y las medidas adoptadas.

| Escenario | Estado | Condiciones mínimas | Riesgo residual |
|---|---|---|---|
| Académico | **Viable con condiciones** | Baja frecuencia, datos públicos, sin evasión, muestra cerrada, fuentes y limitaciones documentadas, sin consejo médico | Medio: términos, exactitud y uso de terceros siguen requiriendo cautela. |
| Público | **Viable después de cambios técnicos y de transparencia** | Fecha/fuente visibles, stock no garantizado, disclaimers, minimización, canal de corrección y revisión de Farmacorp | Medio/alto: mayor confianza y potencial de daño por datos vencidos. |
| Comercial | **Requiere convenios/API y revisión jurídica profesional** | Acuerdos, acceso estructurado, términos propios, privacidad, seguridad, auditoría marcaria, revisión sanitaria y de plataforma | Medio incluso con controles: políticas, mercado y datos pueden cambiar. |

### Académico

El MVP puede continuar como ejercicio académico si mantiene una escala controlada, no elude mecanismos, explica las limitaciones y evita presentar datos o predicciones como garantías o consejo médico.

### Público

La publicación requiere corregir comunicación, mostrar trazabilidad, aclarar vigencia y stock, aplicar minimización y revisar técnicamente la fuente Farmacorp antes de escalar.

### Comercial

La comercialización no debería depender indefinidamente de scraping no autorizado. Requiere convenios o APIs, documentación contractual propia, programa de privacidad y seguridad, auditoría de marcas y revisión jurídica profesional previa.

## 19. Fuentes

| Fuente | Institución | Artículo/sección | URL | Fecha de consulta |
|---|---|---|---|---|
| Constitución Política del Estado | Órgano Electoral Plurinacional | Arts. 21, 25, 130 y 131 | [PDF oficial](https://web.oep.org.bo/wp-content/uploads/2016/12/constitucion_politica_estado.pdf) | 6/11/2026 |
| Ley N.º 453 | Cámara de Diputados | Arts. 13, 14, 18, 25 y 40 | [PDF](https://diputados.gob.bo/wp-content/uploads/Leyes/Ley_N_0453.pdf) | 6/11/2026 |
| Reglamento de la Ley 453, DS N.º 2130 | Servicio Estatal de Autonomías | Art. 14 y cumplimiento de ofertas | [PDF](https://sea.gob.bo/digesto/CompendioII/J/79_REG.pdf) | 6/11/2026 |
| Ley N.º 164 | Ministerio de Justicia | Arts. 54, 55, 56, 72 y 85 | [PDF](https://www.justicia.gob.bo/cms/files/LEY%20N%C2%BA%20164%20Gaceta%20Oficial_gs7rr7i4.pdf) | 6/11/2026 |
| Reglamento TIC, DS N.º 1793 | CTIC-EPB | Definiciones; arts. 56 y 57 | [PDF](https://www.ctic.gob.bo/wp-content/uploads/2016/03/DS-N%C2%B0-1793-Reglamento-a-la-Ley-N%C2%B0164-para-el-Desarrollo-de-Tecnolog%C3%ADas-de-la-Informaci%C3%B3n-y-Comunicaci%C3%B3n.pdf) | 6/11/2026 |
| Proyecto de Ley de Protección de Datos Personales | Cámara de Diputados | PL N.º 538/2025-2026, proyecto en tratamiento | [Listado oficial](https://diputados.gob.bo/proyectos-de-ley-en-tratamiento/) | 6/11/2026 |
| Decisión 486 | Comunidad Andina / Tribunal de Justicia de la Comunidad Andina | Arts. 154–157 | [Gaceta oficial](https://www.tribunalandino.org.ec/decisiones/normativa/DEC486-sentencia.pdf) | 6/11/2026 |
| Interpretación Prejudicial 367-IP-2017 | Tribunal de Justicia de la Comunidad Andina | Buena fe y límites del art. 157 | [PDF](https://www.tribunalandino.org.ec/decisiones/IP/367-IP-2017.pdf) | 6/11/2026 |
| Ley N.º 3131 del Ejercicio Profesional Médico | Ministerio de Salud y Deportes | Arts. 1, 3, 4, 7, 10, 12 y 13 | [Documento oficial](https://www.minsalud.gob.bo/component/jdownloads/?Itemid=465&catid=12&id=142%3Aley-no-3131&task=download.send) | 6/11/2026 |
| Reglamento de la Ley 3131, DS N.º 28562 | Compilación normativa boliviana | Definición de receta y prescripción | [Texto](https://www.lexivox.org/norms/BO-DS-28562.html) | 6/11/2026 |
| Política de Mensajes de WhatsApp Business | WhatsApp / Meta | Opt-in, automatización, datos, salud y productos restringidos | [Política oficial](https://business.whatsapp.com/policy/preview?lang=es_LA) | 6/11/2026 |
| Sitio y términos de Farmacorp | Farmacorp S.A. | Términos de uso, precios y disponibilidad | [Términos](https://farmacorp.com/policies/terms-of-service) | 6/11/2026 |
| Preguntas frecuentes | Farmacorp S.A. | Precios web, stock y otros canales | [FAQ](https://farmacorp.com/pages/preguntas-frecuentes) | 6/11/2026 |
| `robots.txt` e instrucciones para agentes | Farmacorp / plataforma Shopify | Rutas, identificación y UCP/WebMCP | [`robots.txt`](https://farmacorp.com/robots.txt) | 6/11/2026 |
| Catálogo público | Farmacias Chávez | Sitio consultado; términos generales no localizados | [Sitio oficial](https://www.farmaciaschavez.com.bo/) | 6/11/2026 |
| Catálogo público | Farmacias Telchi | Sitio consultado; enlaces de campañas específicas | [Sitio oficial](https://farmaciastelchi.com/) | 6/11/2026 |

Las fuentes no oficiales o compilaciones se utilizan únicamente como complemento cuando se identifica expresamente su naturaleza. Las conclusiones principales se apoyan prioritariamente en Constitución, órganos públicos, Comunidad Andina, TJCA, Meta y sitios oficiales de las farmacias.

## 20. Cómo explicar este SCRUM

### ¿Qué problema aborda?

El proyecto necesita comparar información pública de farmacias y hacerla accesible para adultos mayores, pero debe evitar convertir una herramienta académica en una fuente que aparente garantizar stock, recomendar tratamientos o utilizar datos y marcas sin límites claros.

### ¿Qué investigamos?

Revisamos qué hace realmente el código, qué datos extrae, cómo funciona el MVP, qué dicen la Constitución y las leyes bolivianas sobre información, privacidad y ejercicio médico, cómo puede usarse una marca con finalidad informativa y qué restricciones impone WhatsApp Business.

### ¿Qué encontramos?

- El sistema actual es un HTML local, no un chatbot.
- No hay WhatsApp, cuentas, GPS ni backend de conversaciones.
- Los scrapers consultan páginas públicas sin login ni CAPTCHA.
- Las normas de consumidor exigen información veraz y precios claros, pero no conceden una licencia de scraping.
- La privacidad se protege aunque todavía no exista una ley general integral promulgada.
- Las marcas pueden mencionarse informativamente bajo condiciones de buena fe y ausencia de confusión.
- WhatsApp restringe promoción o facilitación de productos médicos.
- El producto debe mantenerse fuera de diagnóstico, prescripción y sustitución terapéutica.

### ¿El scraping es legal?

**No existe una respuesta absoluta. La legislación revisada no autoriza ni prohíbe expresamente el scraping, por lo que deben considerarse acceso, términos, mecanismos técnicos, propiedad intelectual, consumidor y uso comercial.**

El riesgo es menor cuando se consultan datos públicos con baja frecuencia, sin autenticación ni evasión y con atribución. Aumenta cuando se ignoran instrucciones, se sobrecargan sistemas, se copian contenidos protegidos, se eluden controles o se explota comercialmente sin acuerdo.

### ¿Podemos mostrar marcas?

Puede ser razonable mencionar una marca en texto para identificar un producto legítimo si el uso es exacto, de buena fe, informativo y no genera confusión sobre patrocinio. No deben usarse logos, empaques o fotografías sin autorización o revisión específica.

### ¿Podemos usar WhatsApp?

No debe asumirse. La política actual restringe comprar, vender, promocionar o facilitar productos médicos y de salud. Un comparador de precios puede caer en una zona de riesgo. Se necesita validación formal de Meta o un BSP y un canal alternativo. No se deben vender ni reservar medicamentos dentro de WhatsApp.

### ¿Qué cambia si comercializamos?

Aumentan la escala, confianza del usuario, responsabilidad por errores, obligaciones de privacidad, publicidad y soporte. La dependencia de scraping se vuelve más difícil de justificar y se necesitan convenios, API o feeds oficiales, términos propios y revisión jurídica profesional.

### ¿Cuál es la recomendación final?

Mantener el proyecto como MVP académico con condiciones; corregir transparencia y mensajes antes de publicarlo; y no avanzar a un producto comercial hasta contar con acceso estructurado o convenios, privacidad y seguridad formales, auditoría de marcas, revisión de Meta si corresponde y revisión jurídica boliviana.
