<!-- Generado automáticamente por convertir_docx_a_markdown.py -->
<!-- Origen  : AvanceProductoFinal_Zurita.docx -->
<!-- Fecha   : 2026-06-22 10:59 -->

**ESTRUCTURA PARA LA PRESENTACIÓN DE TRABAJO DE TITULACIÓN MODALIDAD PROYECTO DE INTEGRACIÓN CURRICULAR**

**PÁGINAS PRELIMINARES**

**Título: "**SISTEMA DE MONITOREO PASIVO DE INFORMACIÓN PARA LA PRESENTACIÓN DE RESULTADOS DE LA HUELLA DE CARBONO USANDO DATOS DE PRODUCCIÓN TEXTIL EN UNA INDUSTRIA DE JEANS EN PELILEO**"**

**Abstract**

La industria textil es uno de los principales pilares económicos del Ecuador, pero también es una de las industrias que más contaminación genera y a nivel mundial también lo es. En el cantón Pelileo que es el centro del país de la industria textil, específicamente en la empresa Faditex la cual enfrenta un desafío crítico, que es la falta de datos precisos sobre los desperdicios generados de tela. Actualmente los registros no presentan una precisión y son tomados de forma manual, lo que se convierte en el grave problema de no conocer la huella de carbono generada por la la zona de producción y debilita la toma de decisiones frente al impacto ambiental que este genera.

Este proyecto investigativo propone una implementación de un sistema inteligente de monitoreo y control. La solución propuesta abarca avanzadas tecnologías como Internet de las Cosas (IoT), esto se cumplirá con la instalación de sensores de alta precisión controlados por el microcontrolador ESP32 para capturar de manera automática los datos. Estos datos serán enviados de manera inalámbrica a nuestro Adafruit IO para el almacenamiento de los datos, y posteriormente se verán procesados en el algoritmo de Machine Learning “Random Forest”. Este modelo destaca por procesar volúmenes amplios de datos y entregas predicciones de contaminación de 90% de certeza o superior, ayudando a identificar exactamente puntos críticos con los datos capturados.

Para que la información sea útil y visible en el día a día de la empresa, se desarrollara un panel visual (dashboard) usando el frameword de Streamlit. A través de esta herramienta el encargado del departamento ambiental y desechos visualizara alertas sobre picos anormales de contaminación, visualizar data histórica y compara reportes de contaminación.

**Palabras claves:** Huella de Carbono, IoT, Machine Learning, Random Forest, Industria Textil, Sostenibilidad Digital.

**CAPÍTULO I**

**INTRODUCCIÓN**

* 1. **Contextualización**
* **Nivel Macro (Mundial)**

La crisis de sostenibilidad que atraviesa la manufactura textil a escala global ha alcanzado magnitudes alarmantes, generando actualmente cerca de 92 millones de toneladas de desechos al año[1]. Esta dinámica, exacerbada por la aceleración del consumo de la "moda rápida", provoca que cada segundo se incinera o entierre en vertederos el equivalente a un camión de basura lleno de ropa[2]. El impacto atmosférico no es menor, ya que el sector es responsable de entre el 8% y el 10% de las emisiones mundiales de gases de efecto invernadero, una huella que supera la contribución del transporte marítimo y aéreo internacional combinados.[3] De mantenerse la tendencia actual, se estima que para el año 2050 esta industria podría agotar una cuarta parte del presupuesto de carbono disponible para el planeta.[4]

* **Meso (Nacional/Sector Industria Ecuador)**

En el ámbito nacional, la industria textil ecuatoriana se posiciona como un pilar económico que aporta el 7% al PIB industrial.[5] Sin embargo, la gestión de sus residuos sólidos enfrenta desafíos críticos de infraestructura. Según el Registro de Gestión de Residuos Sólidos del INEC (2024), el 59,7% de los municipios disponen sus desechos en rellenos sanitarios, mientras que un 15,8% todavía recurre a botaderos a cielo abierto[6], sitios donde la descomposición de los textiles libera metano, un gas con un potencial de calentamiento 28 veces mayor que el $CO\_{2}$. Para contrarrestar esta problemática, el Ministerio del Ambiente, Agua y Transición Ecológica (MAATE) ha declarado como emblemático al proyecto "GRECI"[7], enfocado en instaurar modelos de economía circular. A pesar de estos esfuerzos, la adopción de tecnologías sostenibles en la Zona Central del País sigue limitada por barreras económicas y un acceso restringido a financiamiento.

* **Micro (Sector Industrial Pelileo)**

A nivel local, los talleres textiles del cantón Pelileo, como es el caso de Faditex dedicados mayormente al denim, operan bajo un esquema tradicional donde la falta de precisión técnica deriva en pérdidas de tejido durante la fase de corte. Las limitaciones son evidentes: según estadísticas el 43% de los productores locales identifica la falta de recursos financieros y el 30% la capacitación insuficiente como los principales obstáculos para modernizar su manufactura[8], [9]. Actualmente, la gestión de estos sobrantes es reactiva y carece de una separación técnica en la fuente, lo que impide cuantificar la huella de carbono real de la operación. Esta ausencia de datos objetivos hace imperativa la implementación de un plan de mejora que permitan diagnosticar la eficiencia productiva y fundamentar estrategias de control ambiental alineadas con las normativas cantonales.

**(Estado del arte quitar tabla y mandar al final)- citas reordenar en caso de ser necesario para que mantenga un orden numérico con el inicio de cada párrafo.**

* 1. **Estado del Arte**

La gestión integral de residuos y la mitigación de la huella de carbono provocada por la industria textil presenta una transición por medio de las Industrias 4.0 la cual impulsa estos objetivos. Tenemos 3 aspectos importantes que pudimos obtener tras una revisión literaria exhaustiva.

**Sistemas de telemetría IoT y sistemas ciber – físicos:**

Sistemas telemetría y gemelos digitales para la visualización de los datos en tiempo real es la tecnología usada en las industrias 4.0 [16], también se identifica específicamente a los Sistemas Ciber-Físicos como los catalizadores con mayor impacto en la identificación de anomalías y la reducción de desperdicios en tiempo real dentro de la industria textil. Es la base de tu infraestructura de datos.[11]

**Algoritmos Machine Learning “Random Forest”:**

Estudios recientes validan que el Random Forest es superior a otros modelos (como la regresión lineal o incluso redes LSTM en ciertos contextos) para la predicción de recursos y emisiones industriales, alcanzando precisiones en ($R^{2}$) que sustentan la eficiencia de este modelo matemático [13],[10].

**Modelos de Sostenibilidad Digital para la Eficiencia de Materiales:**

Un sistema de control y monitoreo de datos en tiempo real[16], [13], que se integre a rol de funciones del responsable en la toma de decisiones para la mitigación ambiental, estos recientes estudios con tecnologías emergentes presentan resultados positivos al enfrentar el principal nodo del problema de emisiones de CO2.[15]

* 1. **Planteamiento del Problema**

**Problema central:**

**“Deficiente procesamiento de datos en la contaminación de la Huella de Carbono”**

El desarrollo de la industria textil en Pelileo ha priorizado históricamente el volumen de producción sobre la eficiencia ambiental, lo que ha generado una brecha tecnológica en la cuantificación de sus emisiones. El desconocimiento técnico sobre el impacto real de los desperdicios de tela y la ausencia de herramientas digitales para su monitoreo impiden que las organizaciones locales realicen una gestión proactiva de su sostenibilidad.

Efecto 3: Problema por decisiones reactivas y tardías por desconocimiento del volumen de producción y desechos generados.

Efecto 2: Aumento de la vulnerabilidad en la salud ocupacional por exposición prolongada a emisiones gaseosas y ruido

Efecto 1: Presencia de picos críticos no controlados que elevan el riesgo de incumplir el reglamento cantonal de medición de contaminación

PROBLEMA CENTRAL

“Inexistencia de herramientas para el procesamiento de datos de residuos textiles”

Causa 3: Dificultad para relacionar la cantidad de producción con el nivel de desperdicios generados.

Causa 2: Uso de registros manuales o cálculos observados que no reflejan la realidad de los sobrantes textiles.

Causa 1: Inexistencia de equipos automáticos para medir cuánto desperdicio se genera diariamente.

El problema central se origina a partir de tres causas fundamentales: la inexistencia de equipos automáticos o sistemas de telemetría IoT que cuantifiquen el desperdicio en tiempo real; la dependencia de registros manuales y esporádicos que no reflejan la realidad de los sobrantes textiles; y la dificultad técnica para relacionar los volúmenes de producción con el nivel de desperdicio mediante métodos de estimación tradicionales. La persistencia de estas causas deriva en demoras en los informes ambientales solicitados por el GAD de Pelileo y en la imposibilidad de cuantificar la huella de carbono asociada a dichos residuos.

Este conflicto se originó a partir de tres puntos claves; en primer lugar, la inexistencia de equipos automáticos o sistemas de telemetría IoT esto limita la captura precisa de datos, como consecuencia de este déficit de hardware en la organización, esta presenta una dependencia crítica en el uso de registros manuales o cálculos observados, que no reflejan en realidad una data más precisa. La dificultad técnica para relacionar los volúmenes de producción con el nivel de los desperdicios generados, es una tarea muy compleja debido a interacciones no lineales entre variables que métodos tradicionales de cálculo lineal no logran capturar.

Estas deficiencias operativas y tecnológicas comprometen la competitividad y sostenibilidad de la organización, el impacto inmediato reconocible es la exposición a picos críticos de contaminación no controlados, lo que potencialmente elevan el riesgo de incumplir el reglamento cantonal vigente. De igual manera el no tener un monitoreo genera un aumento en la vulnerabilidad de salud ocupacional, que se exponen a emisiones gaseosas, ruido industrial derivado de procesos ineficientes. Finalmente, el punto central de esta ineficiencia se manifiesta por medio de la incapacidad para cuantificar la huella de carbono, al no poder trazar el impacto que genera cada pantalón, la empresa no tiene la capacidad de procesar datos crudos y pierde la oportunidad de implementar una economía circular a micro-nivel con una finalidad de sustentabilidad y rentabilidad.

* 1. **Justificación**

Frente al crecimiento desmedido del modelo de "moda rápida", surge la necesidad imperativa de adoptar estrategias que mitiguen el impacto ambiental en el sector textil. En el contexto de Pelileo, esta iniciativa se vincula con el Proyecto Emblemático GRECI del Ministerio del Ambiente, Agua y Transición Ecológica (MAATE), impulsando una transición real hacia la economía circular. Al fundamentar la gestión de residuos en datos técnicos precisos, la propuesta se convierte en un motor que impulsa las metas de sostenibilidad establecidas en el Plan Nacional de Desarrollo 2024-2025.

La modernización de la planta se alcanza mediante la sustitución de métodos de monitoreo tradicionales y reactivos por una arquitectura de telemetría IoT de alta precisión. La integración de sensores de peso y microcontroladores automatiza la recolección de información, eliminando el sesgo del error humano presente en los registros manuales. Esta infraestructura tecnológica, potenciada por modelos de Machine Learning, permite anticipar anomalías en la producción y maximizar el rendimiento de la materia prima en cada etapa del proceso.

La capacidad de convertir datos crudos en indicadores estratégicos otorga a la gerencia una herramienta de control sin precedentes. A través de un dashboard, es posible visualizar en tiempo real la huella de carbono generada y localizar los puntos críticos de desperdicio durante el corte y la confección. Más allá de la eficiencia interna, esta solución garantiza que la empresa opere bajo el estricto cumplimiento de las ordenanzas ambientales de Pelileo, generando reportes técnicos automáticos que blindan a la organización ante posibles auditorías o sanciones.

El éxito de la implementación se traduce en beneficios tangibles para diversos sectores; los propietarios de los talleres logran una reducción de costos mediante el ahorro de tejido y la optimización de sus flujos operativos. Simultáneamente, se genera un impacto social positivo al mejorar el entorno laboral de los operarios, reduciendo riesgos a la salud derivados de una gestión deficiente. A largo plazo, esta reducción de la carga contaminante se extiende a la comunidad de Pelileo, promoviendo un equilibrio saludable entre la actividad industrial y la calidad de vida de sus habitantes.

La ejecución de la propuesta se respalda en el uso de hardware de bajo costo y plataformas de código abierto, lo que minimiza la barrera de inversión económica inicial. El empleo de placas y sensores accesibles en el mercado local no solo facilita el mantenimiento del sistema, sino que permite que el modelo sea replicable y escalable para otras empresas del sector. Al apoyarse en herramientas digitales flexibles, el sistema posee la capacidad de evolucionar y expandirse al ritmo de crecimiento de la propia fábrica, asegurando la vigencia tecnológica de la inversión.

* 1. **Objetivos**
     1. **Objetivo General**

Implementar un dashboard para el monitoreo y control de datos de contaminación por residuos textiles en la empresa Faditex, usando un modelo de Machine Learning, con la finalidad de reducir la cantidad de residuos textiles en el área de producción.

* + 1. **Objetivos Específicos**

1. Analizar la situación actual de generación de residuos textiles y la precisión en sus registros manuales, para establecer una línea base de impacto ambiental.
2. Diseñar una arquitectura sólida que integra hardware de sensorización, protocolos de comunicación para el análisis de datos.
3. Desarrollar e implementar un pipeline de procesamiento de datos en Python y el modelo predictivo Random Forest para una estimación de desperdicios generados.
4. Validar el funcionamiento del pipeline y el modelo predictivo mediante comparaciones de datos históricos.
   1. **Alcance del Proyecto**

**1.6.1 Elementos incluidos en el proyecto**

* **Módulos del sistema:**
  + Módulo para adquisición de datos (hardware en el Edge).
  + Módulo de comunicación y almacenamiento temporal (Middleware y broker “Adafruit IO”)
  + Módulo de procesamiento de datos (Algoritmo de Machine Learning)
  + Módulo visual (Dashboard)
* **Rol de usuario:** Se indica un único rol correspondiente al “Jefe /Administrador Ambiental”, el cual incluirá en sus funciones la visualización de los datos en tiempo real, la data histórica y los resultados de la huella de carbono.
* **Entorno de despliegue:**
  + **Físico:** Prototipo para la recolección de datos instalado en una zona estratégica del área de producción de Faditex.
  + **Lógico:** Una ingesta de datos que operará sobre la nube de Adafruit IO, el dashboard analítico lo desplegaremos en un entorno local o una aplicación de alojamiento ágil (Streamlit).
* **Tipos de datos:** El sistema procesará de manera exclusiva datos temporales de: peso y fecha para armar una data histórica, pero usaremos datos extras para el cálculo de la huella de carbono, datos obtenidos de Faditex.
* **Tecnologías, plataformas y protocolo:**
  + **Hardware:** ESP32 Azure IoT aplicado a sensores de peso HX711.
  + **Transmisión:** Implementación del protocolo de mensajería MQTT y el uso de Adafruit IO como Middleware y broker para la recepción, visualización y almacenamiento de los datos.
  + **Software y Analítica:** Uso de Adafruit IO y su API REST correspondiente. El procesamiento analítico se ejecutará en un pipeline de Python y se usará la herramienta correspondiente para la visualización del dashboard.

**1.6.2 Elementos excluidos del proyecto**

**Acción de automatización o mitigación:** El sistema cumple con un rol predictivo netamente informático no da alertas o envía informes automáticos. No se incluirán funciones de automatización o alertas tempranas a la persona responsable de la toma de decisiones de contaminación.

**Integración a sistemas externos:** El dashboard que se presentará no se conectará a APIS externas o sistemas de bases datos existentes, tampoco se darán accesos a administrativos por motivos de licencias gratuitas del software usado para esto.

**Mantenimiento y soporte post-entrega:** El compromiso finaliza con la entrega funcional tanto del hardware como del dashboard. No se brindará servicio de soporte técnico que incluyan modificaciones en codificación o hardware y los componentes que este integra.

**Implementación masiva:** La implementación en su totalidad del equipo funcional se limita a un único lugar ya establecido de forma estratégica dentro de la empresa.

**Capacitación laboral:** No se visualiza una capacitación masiva de usuarios pues el sistema es autónomo, la información esencial para el manejo de la herramienta se dara por medio de un manual de usuario a la persona responsable.

* 1. **Fundamentación Teórica**

**Sistemas Ciber-Físicos (CPS) y Telemetría IoT:**

Integración de sensores, procesadores y actuadores monitoreados por computadoras para el censado y monitoreo real de procesos físicos[11], en este apartado tratamos de los sensores y su placa que vamos a colocar para la toma de los datos, como es: “ESP32 Azure IoT, sensores de peso”.

**Plataformas de Sostenibilidad Digital:**

La digitalización industrial es lo que nos permite la transformación hacia procesos de baja emisión de carbono [16].

**Random Forest Regressor:**

Modelo matemático más adecuado para problemas de regresión no lineal en entornos industriales complejos [10], es un método de aprendizaje automático que se basa en múltiple árboles para la toma de una decisión más precisa y robusta, este motor analítico es el modulo central para el análisis de todo y ha demostrado alta validez en la industria textil por presentar coeficientes de determinación $R^{2}$ por encima de 0.98 superando modelos de regresión lineal tradicionales.

**Análisis de importancia de variables:**

Dentro de modelos de ensamble esta técnica es usada para identificar factores a futuro que podrían ejercer una influencia o afectar la variable principal, como es la huella de carbono o el volumen de los desperdicios [15].

**Economía Circular a Micro-Nivel:**

Se enfoca en un nivel micro y se centra en acciones preventivas de manera individual para las empresas con la finalidad de optimizar procesos y reducir el volumen de desperdicios antes que se conviertan en pasivos ambientales [12].

**CAPÍTULO II**

**METODOLOGÍA**

* 1. **Diagnóstico de la Situación Actual**

Actualmente Faditex, presenta un Departamento de Desechos y Medio Ambiente el cual se encarga de verificar el cumplimiento de la normativa Ambiental impuesta por el GAD Municipal de Pelileo, en lo que respecta a esta gestión de control y recolección de datos, observamos resultados negativos. La empresa no presenta rutinas de medición frecuentes, el registro de mermas de tela se lo hace de manera manual, pero cumpliendo las necesidades mínimas solicitadas por inspectores del GAD Municipal de Pelileo.

Durante la jornada operativa diaria, el departamento no presente herramientas para el procesamiento y la visualización de los datos relacionados a la huella del carbono en tiempo real, laborando bajo una data histórica que no presenta un monitoreo o control constante de desperdicios textiles.

* + Desconocimiento operativo: El no disponer de herramientas en donde visualizar los datos, la empresa presenta inconsistencias por lapsos temporales, hasta conocer con los que se manejaran en ese momento.
  + Respuesta reactiva y tardía: La falta de monitoreo de la cantidad de desperdicios emitidos imposibilita un tiempo de reacción prudente ante picos críticos de contaminación. El equipo tarda en generar una respuesta pues no disponen de herramientas en donde visualizar y prevenir infracciones por parte del GAD Municipal.
  1. **Metodología de Desarrollo o Implementación**

Acorde a que el núcleo tecnológico del presente proyecto se centra en la ingeniería de datos y el modelo analítico para la mitigación del impacto ambiental, se ha seleccionado la metodología de Ciencia de Datos OSEMN (Obtain, Scrub, Explore, Model, iNterpret).

La elección de OSEMN se fundamenta por presentar un enfoque táctico y secuencial sobre el ciclo de vida del dato, su diseño es clave para estructuras donde usamos Machine Learning. Esta metodología en nuestro presenta puntos fuertes como el trabajar ya con una guía de flujo de datos desde la ingesta de telemetría IoT, pasando por valores atípicos, ruidos hasta un entrenamiento del algoritmo de Random Forest y la interpretación de los resultados directamente con indicadores de la huella de carnbono.

**Procedimiento y Actividades a realizar:**

El desarrollo del modelo matemático escogido para el análisis y la visualización del dashboard presentarán 5 pasos esenciales que se tratan en la metodología OSEMN, adaptadas a la finalidad de nuestro proyecto:

1. Obtener (Obtain):
   * Descripción: Fase de captura y centralización de las fuentes de datos primarias.
   * Actividad dentro del proyecto: Configuración de la captura de datos automatizada usando el protocolo de comunicación MQTT y usaremos librerías de Python para visualizar el flujo de datos en tiempo real.
2. Limpiar (Scrub):
   * Descripción: Garantizar la integridad de los datos
   * Actividad dentro del proyecto: Ejecutar un EDA y ETL para una limpieza de datos los cuales usaremos para alimentar nuestro algoritmo de Machine Learning.
3. Explorar (Explore):
   * Descripción: Hallazgo de patrones y tendencias presentes en los datos.
   * Actividad dentro del proyecto: Realizar un análisis exploratorio de datos (EDA) para detección de irregularidades, verificando la relación entre los datos y reflejando una realidad operativa.
4. Modelar (Model):
   * Descripción: Implementar un modelo matemático para la predicción o clasificación.
   * Actividad dentro del proyecto: Seleccionar y entrenar el modelo, en esta fase los datos se dividirán en entrenamiento y prueba.
5. Interpretar (iNterpret):
   * Descripción: Transformación de las métricas a valores estratégicos visuales.
   * Actividad dentro del proyecto: Validar el éxito del modelo mediante métricas, y los datos se presentarán mediante un dashboard para el entendimiento de los mismos.
   1. **Técnicas e Instrumentos de Recolección de Información**

**2.3.1 Fase de Análisis y levantamiento de la información inicial.**

**Identificar requerimientos técnicos y normativos de la empresa Faditex:**

Diálogo formal con el responsable de la fábrica textil, aplicando una entrevista con un enfoque para acoger los protocolos actuales de medio ambiente evidenciando una inexistencia de herramientas para el monitoreo de contaminación por huella de carbono.

**Observación Directa:**

Para una validación del modelo matemático y el dashboard, se emplearán técnicas específicas, enfocadas en el rendimiento tanto del dashboard como del modelo matemático y su enfoque en la solución requerida para la empresa, aplicamos técnicas de Telemetría para la obtención, extracción y visualización de los datos de manera autónoma, esta captura de información por parte de los instrumentos de medición se podrá visualizar en tiempo real, se usarán diferentes herramientas para cumplir con estas métricas como Adafruit IO, sensores HX711 para el peso de los desperdicios textiles, y una codificación para observas la fecha de la medición tomada, de esta manera toda la información armara nuestra data que usaremos para el modelo algorítmico.

**Modelo Algorítmico aplicado:**

Para el modelo de Random Forest la técnica que usaremos será Validación cruzada o el uso de Hold-out para la división de datos en entrenamiento o prueba, durante el desarrollo del modelo aplicaremos varios parámetros como; Reset para evaluar el tiempo de recuperación del modelo para la siguiente predicción, una matriz de confusión que se complementará con un Recall de todos los eventos ocurridos y la aplicación de F1-Score para asegurar de la armonía del modelo entre alarmista y permisivo al momento de la predicción frente a los valores indicados por la entidad ambiental.

**Observación de funcionabilidad y pruebas de latencia:**

Se ejecutarán pruebas visuales frente a la latencia de la captura de datos por parte de los sensores una vez estos se reflejen en el dashboard con un tiempo establecido por código de 5 segundos y la respuesta dependerá directamente de la calidad de internet.

* 1. **Requerimientos del Proyecto**

**Requerimientos Funcionales:**

|  |  |  |
| --- | --- | --- |
| ID | Descripción | Prioridad |
| RF-01 | La herramienta permitirá la captura de automatizada de datos peso relacionados a la contaminación, al igual que fecha de la captura de los mismos, todo usando la API de Adafruit IO. | CRÍTICA/ALTA |
| RF-02 | Para la alimentación del algoritmo matemático se ejecutara un EDA para el análisis de los datos y un ETL para la transformación de los mismos. | ALTA |
| RF-03 | Para el evalúo de los datos procesados usaremos el modelo “Random Forest” para la clasificación de los datos que serán destinados al entrenamiento o prueba del algoritmo. | ALTA |
| RF-04 | El dashboard presentara en tiempo real los datos pertenecientes a la huella de carbono que genera la empresa con sus desperdicios, detectando picos altos y por medio de esto el encargado podrá tomar decisiones claves. | ALTA |
| RF-05 | La herramienta visual ayudará a cumplir con los protocolos ambientales del GAD de Pelileo y facilitara acciones para evitar incumplimientos con la contaminación de la huella de carbono que genera la empresa | MEDIA |
| RF-06 | Al encargado del Departamento de Desechos y Medio Ambiente se le facilitara la visualización histórica para auditorias o toma de decisiones por parte de administración. | MEDIA |

**Requerimientos No Funcionales:**

|  |  |  |
| --- | --- | --- |
| ID | Categoría | Descripción |
| RNF-01 | Rendimiento | El dashboard capturara los datos para evidenciar alerta o picos anormales por parte del encargado en tiempos establecidos de <= 5 segundos tras el censo por parte del dispositivo especializado HX711. |
| RNF-02 | Precisión | El modelo algorítmico Random Forest permanecerá dentro de rangos presentados que son superiores a 90% para la correcta predicción de anomalías en contaminación por huella de carbono. |
| RNF-03 | Disponibilidad | La herramienta de visualización operará y capturará los datos en su totalidad durante las jornadas laborales, pues será el evento clave de generación de desperdicios. |
| RNF-04 | Seguridad | El acceso a la visualización de los datos tendrá solo la persona encargada, pues el uso de licencias que efectuaremos permiten una mínima creación de usuarios que |

Cada requerimiento funcional o no funcional se desglosa y se hace una pequeña documentación con una pequeña imagen, cuidado que la imagen no redunde con la imagen

* 1. **Diseño de la Solución**

**2.5.1 Arquitectura General**

El diseño tendrá una serie de pasos a seguir empezando con el diseño del hardware que usaremos para la captura de datos, un apartado independiente para el proceso de estos y la alimentación del algoritmo matemático.

**2.5.2 Diseño de la Capa Perimetral**

* **Unidad de Procesamiento:** Se aplicará un microcontrolador específicamente un ESP32 Azure IoT muy especifica para proyectos de captura de datos con sensores, presenta bajo consumos de energía.
* **Componentes:** El hardware presenta una configuración para sensores de peso y la captura de los datos mediante el protocolo MQTT. El sensor HX711 en la versión de 10kg nos brinda un amplio rango para medir desperdicios que generan la empresa.

**2.5.3 Flujo de datos y diseño lógico**

Para un manejo más eficiente de los datos optaremos por el broker Adafruit IO el cual permite la captura en tiempo real y facilitara acciones frente a picos anormales de datos correspondientes a la contaminación generada.

* **Fase de procesamiento de datos (ETL):** Los datos capturados se someterán a técnicas especializadas para transformación a datos útiles pues los datos capturados son crudos y por medio de un Z-SCORE obtendremos datos útiles para alimentar nuestro algoritmo matemático.
* **Motor de implementación:** Utilizaremos scikit-learn de Python para implementar el modelo supervisado de Random Forest. El modelo procesará los datos obtenidos por los sensores de peso y lo ajustaremos para la predicción de anomalías que podrá observar el encargado en el Departamento de Desechos y Medio Ambiente.

**2.5.4 Visualización de los datos:**

La herramienta de entrega será un dashboard para la visualización de los datos en tiempo real manteniendo una arquitectura limpia y comprensible de los datos.

* **Componente Visual:** Desarrollado mediante el framework de Streamlit, el dashboard integrara una captura en tiempo real del microcontrolador ESP32 y centralizados en el broker Adafruit IO. Junto a el algoritmo predictivo de Random Forest que categorizará el nivel del impacto medio ambiental provocado por los desperdicios generados de la empresa. El dashboard mostrará la importancia la importancia relativa de las variables que interviene para el cálculo de la huella de carbono.
  1. **Justificación Técnica**

1. **Hardware Perimetral (ESP32 y Sensores Analíticos):** Para la captura de los datos de la industria Faditex se tomó la decisión de usar el microcontrolador ESP32 Azure IoT, el uso de esta placa está ampliamente justificado para proyectos con monitoreo y control de datos en tiempo real[17]**,** al integrar funciones de wifi y facilidades en el uso de protocolos de transmisión de datos como MQTT, AMQP y HTTPS, ratifica la importancia de este tipo de placa en el proyecto, esta selección tecnológica permite una adaptación a Industrias 4.0.
2. **Transmisión de datos:** De los posibles protocolos de transmisión de datos hemos seleccionado MQTT sobre protocolos tradicionales como HTPP, el bajo consumo de recursos son características esenciales para el constante trabajo del microcontrolador en la captura de datos, la huella de carbono requiere un constante flujo de datos y parámetros que se van a enviar, MQTT presenta paquetes con cabeceras mínimas, lo que evita la saturación del ancho de banda y fluctuaciones de la red.
3. **Análisis de datos:** El modelo matemático se desarrollará en Python utilizando librerías específicas como scikit-learn para la implementación del algoritmo “Random Forest”, esta decisión del modelo se fundamenta en papers en los cuales son aplicados para predicciones de contaminación [10], el modelo trabaja con varios multi-árboles antes de tomar una decisión lo que nos indica que el modelo no presentara un sobreajuste, el uso de este modelo es fundamental para la sostenibilidad del proyecto, ya que ofrece una alta interpretabilidad del cálculo realizado.
4. **Visualización:** Para el dashboard interactivo, hemos descartado toda posibilidad de en la cual intervenga construir el mismo, pues sería un consumo innecesario de recursos, justificamos el uso de Streamlit el cual es un framework que pertenece a Python el cual nos ayuda observar la data. Este framework nos permite integrar el modelo algorítmico pues es diseñada para ciencia de datos y aprendizajes automáticos, mantiene una compatibilidad con las principales librerías que usaremos.

**CAPÍTULO III**

**IMPLEMENTACIÓN, PRUEBAS Y RESULTADOS**

* 1. **Descripción de la Solución**

La solución desarrollada se concibe como un ecosistema integral y vanguardista de monitoreo ambiental y analítica predictiva, diseñado específicamente para promover la sostenibilidad, la reducción de mermas y la toma de decisiones preventivas en la línea productiva de la empresa Faditex Denim. El sistema representa un salto tecnológico significativo respecto a las metodologías convencionales de supervisión de residuos, las cuales son manuales, reactivas y carecen de capacidad prospectiva para cuantificar el impacto ambiental en tiempo real. En su lugar, esta propuesta implementa una arquitectura robusta de cinco capas funcionales:

1. Adquisición en el Borde
2. Transmisión IoT
3. Procesamiento ETL
4. Predicción Analítica
5. Visualización

Que permite la captura pasiva y la interpretación de variables críticas de producción, tales como el peso de los residuos textiles, la eficiencia del tejido y la generación de emisiones de Dióxido de Carbono Equivalente (CO₂eq) en la etapa de manufactura.

Esta infraestructura no solo automatiza la vigilancia constante del proceso operativo, sino que integra armónicamente el hardware de adquisición de bajo costo (Edge Computing) desplegado directamente en la planta, con un motor de Inteligencia Artificial de alta precisión basado en el algoritmo Random Forest. Al fundamentarse metodológicamente en el Análisis de Ciclo de Vida (LCA) para aislar y extrapolar la proporción exacta de la huella de carbono generada exclusivamente durante la confección del denim, la solución garantiza una transición fluida desde la lectura física de las celdas de carga hasta la generación de inteligencia operativa en un dashboard interactivo. De este modo, la herramienta se posiciona como un instrumento estratégico de gestión ambiental, capaz de proyectar escenarios de desperdicio futuro y visibilizar ineficiencias imperceptibles en la métrica tradicional, asegurando un entorno productivo resiliente, altamente eficiente y plenamente alineado con los principios de economía circular dictados por la Industria 4.0.

# **3.1.1 Arquitectura del Sistema y Flujo de Datos**

La arquitectura del sistema se estructuró en cuatro capas funcionales claramente diferenciadas, de modo que el diseño del software y del hardware refleje de manera fiel el recorrido de la información a lo largo de su ciclo de vida. Este enfoque por capas desacopladas permite trazar el flujo del dato desde el entorno físico de la planta de corte hasta la generación de indicadores de gestión, convirtiendo una magnitud física, el peso de los residuos textiles, en inteligencia operativa y ambiental. Cada capa cumple una responsabilidad específica y se comunica con la siguiente a través de una interfaz bien definida, lo que garantiza la trazabilidad completa del dato y la posibilidad de mantener o sustituir cualquier componente sin afectar al resto del sistema.

1. Capa de Ingesta y Comunicación:

Corresponde a la obtención ininterrumpida del dato crudo. A nivel perimetral (Edge), se utiliza un microcontrolador ESP32 encargado de gobernar los amplificadores HX711 conectados a las celdas de carga, sobre las cuales se depositan los retazos de tela generados en el proceso de corte y confección. La señal del conversor analógico-digital de 24 bits es convertida a una magnitud de peso, en gramos, mediante un factor de calibración, y cada lectura es empaquetada y transmitida, con una cadencia de cinco segundos, mediante el protocolo ligero MQTT hacia el broker en la nube Adafruit IO, el cual opera como el middleware de recepción y almacenamiento de la serie temporal en el feed denominado peso.

1. Capa de Procesamiento y Limpieza.

El motor analítico, implementado en Python, consume el histórico de mediciones exportado desde la nube en formatos CSV y XLSX, incorporando automáticamente todo archivo nuevo a partir de patrones de nombre, sin requerir modificaciones en el código. Los datos crudos atraviesan un proceso de depuración que corrige las taras negativas mediante valor absoluto, descarta lecturas nulas o no numéricas y aplica un filtro de ruido que conserva exclusivamente el rango válido comprendido entre 50 y 2000 gramos, mitigando así tanto el ruido de tara del sensor vacío como los picos anómalos de saturación. Un aspecto central de esta capa es la agregación temporal: dado que el sensor realiza una medición de estado, el peso presente sobre la báscula, y no un conteo incremental, las múltiples lecturas de cada jornada se sintetizan en su máximo diario, valor que representa el mayor volumen de residuo acumulado antes del vaciado de la báscula. Sobre esta base se construyen las variables predictoras mediante ingeniería de características: rezagos del peso de uno a tres días y una media móvil de tres días calculada exclusivamente sobre días previos, a fin de evitar la fuga de información hacia el modelo. Asimismo, el motor de Pandas genera resúmenes estadísticos, distribuciones de frecuencia y una matriz de correlación entre las variables del modelo, que permiten comprender el comportamiento del proceso.

1. Capa de Modelado Predictivo:

Constituye el núcleo predictivo de la arquitectura. A diferencia de los algoritmos basados en distancia, el modelo Random Forest no requiere una estandarización previa de las magnitudes, por ejemplo, mediante Z-Score, ya que su naturaleza basada en particiones sucesivas de árboles de decisión es invariante a la escala de las variables; esta propiedad simplifica el pre procesamiento sin sacrificar rigurosidad. El conjunto depurado se divide cronológicamente, sin aleatorización, condición obligatoria en las series de tiempo, en subconjuntos de entrenamiento y prueba, y se entrena un regresor Random Forest con la profundidad de los árboles y el tamaño mínimo de hoja controlados, a fin de prevenir el sobreajuste dado el reducido número de jornadas disponibles. El modelo, entrenado sobre el comportamiento histórico, estima el desperdicio esperado, en kilogramos, para el siguiente ciclo de producción.

1. Capa de Presentación e Interfaz Web:

El conocimiento generado por el modelo es transformado en inteligencia operativa de fácil interpretación. Utilizando el framework Streamlit y los motores de graficación Matplotlib y Seaborn, el sistema traduce las predicciones y los datos depurados en indicadores de gestión, como la producción estimada, la eficiencia del proceso frente al referente industrial y la huella de carbono expresada en kilogramos de CO2 equivalente, distribuidos en cinco páginas interactivas. Entre los recursos de visualización destaca una gráfica dinámica de CO2 filtrable por rango de fechas, que permite analizar la evolución de las emisiones para un día o una semana específica. Esta capa culmina con la generación automática de un reporte ejecutivo en formato PDF mediante la librería ReportLab, facilitando al responsable de producción la interpretación inmediata del estado ambiental y productivo del proceso.

![C:\Users\Chris\Downloads\arquitectura_cuatro_capas.png](data:image/png;base64...)

*Figura 3.1 Arquitectura en cuatro capas y flujo de datos del sistema. Elaboración propia.*

La Figura 3.1 sintetiza la arquitectura descrita y evidencia el carácter unidireccional y trazable del flujo de datos: el dato avanza de forma secuencial desde el dispositivo físico de captura, pasa por la nube, el procesamiento y el modelo predictivo, y culmina en la interfaz que consume el usuario. Su importancia radica en que permite comprobar, de un solo vistazo, que un único dato físico, el peso de los residuos, se propaga a través de las cuatro capas sin puntos de quiebre ni transformaciones opacas, desde su obtención en el sensor hasta su interpretación como indicador de decisión. De esta manera, el esquema demuestra el cumplimiento del objetivo del sistema, cuantificar y visualizar la cantidad de residuos textiles generados en el área de producción y su impacto ambiental asociado, y respalda la confiabilidad de los indicadores entregados al responsable de producción

# **3.1.2 Stack Tecnológico**

El desarrollo del sistema integró un conjunto de tecnologías de código abierto, seleccionadas por su madurez, su interoperabilidad y su amplia adopción en los ámbitos de la ciencia de datos y el Internet de las Cosas. Con el fin de garantizar la reproducibilidad de la investigación, la Tabla 3.1 presenta el stack tecnológico completo empleado en cada capa del sistema, especificando la versión exacta de cada herramienta y la justificación técnica que motivó su elección. Estas versiones corresponden al entorno virtual con el que se desarrolló y validó la solución, registradas en el archivo requirements.txt, lo que permite a cualquier investigador recrear el entorno de ejecución de manera idéntica y obtener resultados equivalentes.

|  |  |  |  |
| --- | --- | --- | --- |
| **Componente** | **Tecnología** | **Versión** | **Justificación Técnica** |
| Lenguaje | Python | 3.14.4 | Estándar de la industria para ciencia de datos y robustez en librerías de ML. |
| Interfaz Web | Streamlit | 1.58.0 | Integración nativa con Python y manejo de estados de sesión para tiempo real. |
| Procesamiento | Pandas | 3.0.3 | Manipulación de series temporales y remuestreo (agregación diaria). |
| Cálculo numérico | NumPy | 2.4.6 | Operaciones vectoriales que sustentan el procesamiento y las métricas. |
| Machine Learning | Scikit-learn | 1.9.0 | Implementación del **Random Forest Regressor** para predicción del desperdicio. |
| Visualización | Matplotlib | 3.10.9 | Gráficos estáticos: series de tiempo, histogramas, mapa de calor. |
| Visualización | Seaborn | 0.13.2 | Estilización estadística de los gráficos (histograma con KDE, heatmap). |
| Reportes | ReportLab | 4.5.1 | Generación programática del reporte ejecutivo en PDF. |
| Broker IoT | Adafruit IO | 3.0.0 | Gestión de feeds MQTT con integración vía API REST. |
| Credenciales | python-dotenv | 1.2.2 | Carga de credenciales desde variables de entorno (seguridad). |
| Lectura Excel | openpyxl | 3.1.5 | Lectura de los archivos de datos históricos en formato XLSX. |

*Tabla 3.1. Stack tecnológico del sistema, con la versión y la justificación técnica de cada componente.*

# **3.1.3 Justificación de la Arquitectura**

El diseño y la selección de la arquitectura del sistema se justifican bajo tres pilares de ingeniería: la idoneidad del modelo predictivo frente a la naturaleza de los datos, la resiliencia ante entornos de red industriales inestables y la eficiencia en el ciclo de vida del software. Estos criterios responden, además, a la problemática operativa identificada en Faditex durante el levantamiento de requisitos, en el cual se evidenció que el registro de los residuos textiles se realizaba de forma manual y esporádica: el depósito de retazos se controlaba únicamente cuando se encontraba lleno, sin una toma de datos diaria, lo que ocasionaba demoras en la elaboración de los informes ambientales mensuales solicitados por el GAD de Pelileo. La arquitectura propuesta sustituye ese proceso manual por un flujo de datos automatizado, continuo y trazable.

En primer lugar, la adopción del algoritmo Random Forest como núcleo predictivo responde a la naturaleza no lineal y temporal del desperdicio textil. El volumen de retazos generado en la planta no presenta un comportamiento constante, sino que varía en función del día de la semana, del ritmo de producción reciente y de patrones históricos. Frente a los modelos lineales clásicos, que asumen una relación fija entre las variables, Random Forest captura estas relaciones complejas sin necesidad de especificar una forma matemática previa. Asimismo, al fundamentarse en la combinación de múltiples árboles de decisión, resulta robusto frente al sobreajuste y ofrece una elevada interpretabilidad a través de la importancia de las variables, una ventaja decisiva dado el reducido número de jornadas disponibles para el entrenamiento; a diferencia de los algoritmos basados en distancia, tampoco requiere la estandarización previa de las magnitudes. La pertinencia de esta elección se sustenta, además, en antecedentes de la industria textil donde algoritmos de aprendizaje automático, y en particular Random Forest, han demostrado un buen desempeño en la predicción de variables de producción y de huella de carbono, los cuales se desarrollan en el marco teórico de la presente investigación.

Desde la perspectiva de la infraestructura de telecomunicaciones, la integración de una topología perimetral (Edge) acoplada a un broker MQTT en la nube (Adafruit IO) resuelve los desafíos de conectividad propios de las zonas industriales. El protocolo MQTT, al ser un estándar de mensajería asíncrona y de estructura ultraligera, garantiza una transmisión eficiente de la telemetría incluso en condiciones de bajo ancho de banda o latencia elevada. Como mecanismo de resiliencia, el firmware del microcontrolador ESP32 supervisa en cada ciclo el estado de la conexión Wi-Fi y del enlace MQTT, y los restablece de forma automática ante una caída temporal de la red, evitando la interrupción del servicio de medición; además, la lectura de cada celda de carga se ejecuta únicamente cuando el amplificador HX711 confirma la disponibilidad del dato, lo que previene el bloqueo del dispositivo ante una eventual desconexión del sensor. De manera complementaria, la arquitectura contempla una doble fuente de datos, la lectura en tiempo real desde la nube y el histórico exportado en archivos locales en formatos CSV y XLSX, lo que aporta resiliencia al análisis al permitir reconstruir la serie temporal aun cuando el enlace en vivo no esté disponible.

Finalmente, el despliegue de la capa de presentación y del motor de inferencia mediante Streamlit optimiza los recursos computacionales y reduce la complejidad del sistema. Frente a las arquitecturas web tradicionales orientadas a microservicios, que separan el frontend del backend (por ejemplo, React y Django), Streamlit ofrece una integración nativa con el ecosistema de ciencia de datos de Python, lo que permite que la limpieza de datos, el entrenamiento del modelo y la renderización de la interfaz coexistan en un mismo entorno. El sistema emplea mecanismos de almacenamiento en caché para reutilizar el modelo entrenado y los datos ya procesados sin recalcularlos en cada interacción, y libera de forma explícita los recursos gráficos tras generar cada visualización, evitando el consumo progresivo de memoria durante sesiones de monitoreo prolongadas. Esta decisión arquitectónica disminuye la complejidad del despliegue, posibilita la publicación del dashboard en la nube y asegura tiempos de respuesta adecuados, entregando a la organización una herramienta de monitoreo preventiva, escalable y técnicamente viable.

**3.2 Proceso de Implementación**

La fase de implementación se ejecutó mediante un flujo de trabajo sistemático que permitió transformar los requerimientos funcionales, levantados junto al usuario, en módulos de software operativos. El proceso abarcó desde el aprovisionamiento del entorno de desarrollo y la configuración del hardware de captura, hasta la construcción del pipeline de datos, el entrenamiento del modelo y el despliegue de la interfaz de visualización. Cada etapa se desarrolló de forma incremental, verificando el correcto funcionamiento de un componente antes de integrarlo con el siguiente, lo que facilitó la detección temprana de errores y mantuvo el sistema operativo a lo largo de todo el desarrollo.

**3.2.1 Configuración del Entorno de Desarrollo**

Con el objetivo de garantizar la reproducibilidad de la solución y evitar conflictos entre dependencias, el desarrollo se realizó sobre un entorno virtual aislado de Python en su versión 3.14.4. La totalidad de las librerías, junto con sus versiones exactas, se consolidó en el archivo requirements.txt, descrito previamente en la Tabla 3.1, de modo que el entorno completo puede recrearse mediante una única instrucción de instalación. Este aislamiento asegura que la ejecución del sistema sea independiente de las configuraciones particulares de cada máquina y que los resultados obtenidos sean consistentes en distintos despliegues.

La gestión de las credenciales de acceso a la plataforma Adafruit IO se diseñó bajo el principio de no exponer información sensible en el código fuente. Para ello, el sistema contempla dos mecanismos complementarios: en el despliegue en la nube se emplean los secretos de aplicación de Streamlit (st.secrets), mientras que en el entorno local las credenciales se cargan desde un archivo de variables de entorno (.env) mediante la librería python-dotenv. En ambos casos, las llaves de la API permanecen fuera del repositorio de código y excluidas del control de versiones, lo que protege el acceso a la infraestructura del sistema.

**3.2.2 Construcción de los Módulos de Software y Entrenamiento del Modelo**

En coherencia con las metodologías adoptadas en la investigación, Extreme Programming (XP) para la gestión incremental del desarrollo y OSEMN para la organización del ciclo de vida de los datos, la solución se construyó de forma modular, separando el procesamiento y el entrenamiento del modelo de la capa de inferencia y visualización. Bajo el enfoque de XP, los requerimientos se derivaron de las historias de usuario levantadas con el personal de Faditex y el sistema se edificó de manera iterativa, manteniendo en todo momento una versión funcional y verificable; por su parte, OSEMN proporcionó la estructura conceptual que guió la secuencia de obtención, depuración, exploración y modelado de la información. Esta separación en módulos independientes favorece la reutilización del código, la realización de pruebas aisladas y el mantenimiento del sistema.

El archivo modelo\_prediccion.py constituye el motor analítico del sistema. Es el componente encargado de cargar los datos, depurarlos, explorarlos, construir las variables predictoras y entrenar el modelo; concentra, por tanto, las primeras fases de la metodología OSEMN y puede ejecutarse de forma autónoma para procesar por lotes el conjunto histórico y generar los gráficos del análisis exploratorio y de la predicción.

Durante la fase de obtención (Obtain), la función cargar\_y\_limpiar\_datos incorpora automáticamente los archivos del directorio mediante patrones de nombre, unificando en una sola serie temporal las exportaciones de la nube y los archivos locales. Acto seguido, en la fase de depuración (Scrub), esa misma función corrige las taras negativas con valor absoluto, descarta los registros nulos o no numéricos y aplica un filtro que conserva únicamente las lecturas comprendidas entre 50 y 2000 gramos, eliminando el ruido del sensor vacío y los picos de saturación, tal como se muestra en la Figura 3.2

![](data:image/png;base64...)

El procedimiento más determinante de esta etapa, ejecutado por la función integrar\_logica\_negocio, es la agregación temporal. Dado que el sensor entrega una medición de estado y no un conteo incremental, las múltiples lecturas de cada jornada se sintetizan en su valor máximo diario, que representa el mayor volumen de residuo acumulado antes del vaciado de la báscula. Sobre esa base se construyen las variables predictoras mediante ingeniería de características: los rezagos del peso de uno a tres días y una media móvil de tres días calculada exclusivamente sobre días previos para evitar la fuga de información hacia el modelo. La Figura 3.3 presenta la agregación por máximo diario y la generación de estas variables.

![](data:image/png;base64...)

*Figura3.3. Agregación por máximo diario e ingeniería de características en la función integrar\_logica\_negocio. Elaboración propia.*

Por último, en la fase de modelado (Model), la función entrenar\_modelo\_random\_forest divide el conjunto de forma cronológica, reservando el ochenta por ciento inicial para el entrenamiento y el veinte por ciento final para la prueba, sin aleatorización, condición indispensable en las series de tiempo. A diferencia de los modelos basados en distancia, no se aplica una estandarización de las magnitudes, como el Z-Score, ya que Random Forest es invariante a la escala de las variables. El modelo se configura con un número de árboles parametrizable desde la interfaz, entre 50 y 300 con un valor por defecto de 100, una profundidad máxima de cinco niveles y un mínimo de dos muestras por hoja, restricciones orientadas a prevenir el sobreajuste dado el reducido número de jornadas disponibles; su desempeño se evalúa mediante el error cuadrático medio (RMSE), el error absoluto medio (MAE) y el coeficiente de determinación (R2), complementados con una validación cruzada temporal (TimeSeriesSplit). La configuración y el entrenamiento del modelo se muestran en la Figura 3.4.

![](data:image/png;base64...)

*Figura3.4. Configuración y entrenamiento del modelo Random Forest en la función entrenar\_modelo\_random\_forest. Elaboración propia.*

Por su parte, el archivo dashboard\_tesis.py corresponde al módulo de inferencia y presentación. Es la aplicación web que reutiliza las funciones del motor analítico para entrenar el modelo, ejecutar la predicción y mostrar los resultados al usuario final. A diferencia de los esquemas que serializan el modelo en archivos binarios almacenados en disco, el sistema lo entrena en memoria y lo conserva mediante la directiva st.cache\_resource, apropiada para objetos no serializables como los modelos de Scikit-learn; de este modo, el modelo se entrena una sola vez por configuración y se reutiliza en las sucesivas interacciones del usuario sin recalcularse, optimizando el uso de memoria del servidor. El número de árboles seleccionado actúa como discriminador de la caché, de manera que el reentrenamiento ocurre únicamente cuando ese parámetro se modifica desde la barra lateral, como se aprecia en la Figura 3.5.

![](data:image/png;base64...)

*Figura3.5. Carga y almacenamiento en caché del modelo entrenado en dashboard\_tesis.py mediante st.cache\_resource. Elaboración propia.*

Finalmente, a partir del último día disponible en la serie, el módulo ejecuta la inferencia para estimar el desperdicio del siguiente ciclo y, sobre ese valor, deriva la producción estimada, la tela a consumir y la huella de carbono asociada, que se presentan en las páginas interactivas del dashboard.

**3.2.3 Integración y Despliegue del Dashboard**

La integración de los componentes consistió en unificar, dentro de una misma interfaz, el flujo de datos en vivo procedente de la nube con el análisis histórico y las predicciones generadas por el modelo. La lectura en tiempo real del sensor se gestionó mediante el decorador st.fragment con el parámetro run\_every igual a cuatro, que actualiza de forma autónoma únicamente el componente del sensor cada cuatro segundos, sin necesidad de recargar la página completa; de esta manera se evita el parpadeo visual (flickering) y se mantiene la fluidez de la interfaz, tal como se muestra en la Figura 3.6.

**![](data:image/png;base64...)**

Para preservar la eficiencia durante la sesión, las tareas más costosas, es decir, la carga de los datos, el entrenamiento del modelo y el procesamiento del histórico, se ejecutan una sola vez y se conservan en memoria mediante los mecanismos de caché de Streamlit (st.cache\_resource y st.cache\_data). De este modo, mientras el fragmento del sensor se refresca periódicamente, el resto del sistema no se recalcula, lo que optimiza el uso de los recursos del servidor.

Finalmente, el despliegue se realizó en la nube a través de Streamlit Community Cloud, lo que permite acceder al dashboard desde cualquier navegador sin instalación local. En este entorno, las credenciales de Adafruit IO se inyectan mediante los secretos de aplicación (st.secrets) y los archivos de datos se incorporan al repositorio, desde donde el sistema los carga automáticamente por patrón de nombre.

**3.2.4 Resolución de Incidencias Técnicas**

Durante la implementación se identificaron y resolvieron diversos desafíos técnicos propios de un entorno industrial, lo que reforzó la robustez del sistema.

Estabilización de las lecturas frente al ruido. Las interferencias electromagnéticas de la maquinaria y la propia deriva del sensor generaban fluctuaciones en las mediciones de peso. Este problema se atendió en dos niveles. En el firmware, cada medición se obtiene como el promedio de cinco muestras consecutivas mediante la instrucción get\_units(5), lo que atenúa las fluctuaciones eléctricas momentáneas en el origen. Posteriormente, en el pipeline de datos, se corrigen las taras negativas con valor absoluto y se descartan las lecturas fuera del rango válido de 50 a 2000 gramos, eliminando el ruido del sensor vacío y los picos de saturación antes de que la información llegue al modelo.

Tolerancia a fallos de conectividad. Las caídas intermitentes de la red o las limitaciones de la interfaz de programación de Adafruit IO podían interrumpir el servicio. Para evitar que estos eventos provocaran el cierre de la aplicación, las llamadas a la nube se encapsularon en bloques try/except que capturan el error, informan del estado de la conexión al usuario y permiten que la aplicación continúe operando, como se aprecia en la Figura 3.7. La actualización periódica del fragmento del sensor, cada cuatro segundos, actúa además como un mecanismo de reintento automático, de modo que el servicio se restablece por sí solo una vez recuperado el enlace. De forma complementaria, en el extremo del dispositivo, el firmware del ESP32 supervisa en cada ciclo el estado de la conexión Wi-Fi y MQTT y la restablece de manera automática ante una caída temporal, y realiza la lectura de las celdas únicamente cuando el amplificador confirma la disponibilidad del dato, evitando bloqueos del hardware.

**3.2.5 Despliegue Físico en Planta**

La etapa final de la implementación consistió en instalar el componente físico del sistema en el entorno real de producción de Faditex. El conjunto de hardware, conformado por el microcontrolador ESP32, los amplificadores HX711 y las celdas de carga, se ubicó en el área de corte y confección, integrando las celdas en el basurero donde se depositan los residuos del proceso.

De esta manera se garantizó un monitoreo puramente pasivo: los retazos caen por gravedad dentro del basurero instrumentado con las celdas de carga, de modo que el sistema registra automáticamente el peso depositado sin requerir ninguna intervención manual del operario. La ubicación del contenedor debajo de las estaciones de costura asegura que el material generado durante el corte y la confección sea capturado en el punto mismo de su origen, eliminando la dependencia del registro manual que caracterizaba al proceso anterior.

Cabe señalar que el contenedor recibe los residuos del área de corte, que pueden incluir material no textil; por lo tanto, el peso registrado corresponde a todo lo depositado en el basurero. Esta consideración constituye una limitación de la medición, que se aborda en el apartado de limitaciones del sistema.

Como evidencia del correcto funcionamiento del flujo de telemetría, la Figura 3.8 muestra el feed PESO en la plataforma Adafruit IO, donde se reciben y almacenan las lecturas transmitidas por el sensor instalado en planta, confirmando que el dato físico capturado en el basurero llega de forma íntegra a la nube.

**![](data:image/png;base64...)**

* 1. **Pruebas y Validación**

[Describir las pruebas realizadas para validar el funcionamiento de la solución, tales como pruebas funcionales, integrales, de seguridad, rendimiento o conectividad, según aplique.]

* 1. **Resultados**

[Presentar los resultados obtenidos durante la validación, comparando la situación inicial con la posterior a la implementación. Incluir métricas, indicadores o evidencias.]

* 1. **Cronograma y Presupuesto**

[Presentar la planificación de las fases de ejecución del proyecto y el detalle de los costos asociados a hardware, licencias, servicios u otros recursos.]

**CAPÍTULO IV**

**CONCLUSIONES Y RECOMENDACIONES**

* 1. **Conclusiones**

[Redactar conclusiones basadas en los resultados obtenidos y en el cumplimiento de los objetivos planteados.]

* 1. **Recomendaciones**

[Proponer mejoras, optimizaciones o ampliaciones del proyecto, fundamentadas en el análisis realizado.]

* 1. **Trabajos Futuros**

[Plantear líneas de desarrollo o investigación que puedan derivarse del proyecto implementado.]

**BIBLIOGRAFÍA**

[1] UNEP, «Sustainable fashion to take centre stage on Zero Waste Day». Accedido: 18 de marzo de 2026. [En línea]. Disponible en: <https://www.unep.org/technical-highlight/sustainable-fashion-take-centre-stage-zero-waste-day>

[2] «A New Textiles Economy: Redesigning fashion’s future». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://www.ellenmacarthurfoundation.org/a-new-textiles-economy>

[3] «UN Helps Fashion Industry Shift to Low Carbon | UNFCCC». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://unfccc.int/news/un-helps-fashion-industry-shift-to-low-carbon>

[4] «Fashion industry may use quarter of world’s carbon budget by 2050». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://www.downtoearth.org.in/environment/fashion-industry-may-use-quarter-of-world-s-carbon-budget-by-2050-61183>

[5] Redacción, «Sector textil en Ecuador, que genera cerca de 220.000 empleos a escala nacional, apunta a nuevos mercados», El Universo. Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://www.eluniverso.com/noticias/politica/sector-textil-en-ecuador-que-genera-cerca-de-220000-empleos-a-escala-nacional-apunta-a-nuevos-mercados-nota/>

[6] «home – Instituto Nacional de Estadística y Censos». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://www.ecuadorencifras.gob.ec/institucional/home/>

[7] «Proyecto Gestión de Residuos Sólidos y Economía Circular Inclusiva-GRECI – Viceministerio del Ambiente». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://www.ambienteyenergia.gob.ec/ambiente/proyecto-gestion-de-residuos-solidos-y-economia-circular-inclusiva-greci/>

[8] «GAD Municipal San Pedro de Pelileo – Municipio de Pelileo». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://pelileo.gob.ec/v3/>

[9] «Presentación de PowerPoint». Accedido: 20 de marzo de 2026. [En línea]. Disponible en: <https://pelileo.gob.ec/v3/documentos/PDOT2024.pdf>

[10] X. Li, K. Zhang, Z. Gao, y J. Xu, «Influencing Factors and Prediction Model for the Carbon Footprint of Textile Finishing Production: Case Study of 672 Textile Products», *Sustainability*, vol. 17, n.o 22, nov. 2025, doi: 10.3390/su172210350.

[11] G. de Oliveira Neto, D. Silva, V. Arns, H. Tucci, L. Pinto, y M. Seri, «Industry 4.0 technologies moderately spurred micro-level circular economy considering cleaner production, not promoting sustainable performance», *International Journal of Environmental Science and Technology*, vol. 22, sep. 2024, doi: 10.1007/s13762-024-06010-y.

[12] S. Wang *et al.*, «Tracing the Carbon Footprint of Cotton Garments Based on Their Life Cycle: Evidence from an Empirical Study of Multiple Sites in China», 8 de mayo de 2024, *Social Science Research Network, Rochester, NY*: 4821904. doi: 10.2139/ssrn.4821904.

[13] M. Guldurek, «A Dual Approach to Profitability and Sustainability: AI-Powered Pricing and Emissions Control in Textiles», *IEEE Access*, vol. PP, pp. 1-1, ene. 2026, doi: 10.1109/ACCESS.2026.3659532.

[14] A. P. Periyasamy y G. Duraisamy, «Carbon Footprint on Denim Manufacturing», en *Handbook of Ecomaterials*, Springer, Cham, 2018, pp. 1-18. doi: 10.1007/978-3-319-48281-1\_112-1.

[15] M. Zhao *et al.*, «Virtual carbon and water flows embodied in global fashion trade - a case study of denim products», *Journal of Cleaner Production*, vol. 303, p. 127080, jun. 2021, doi: 10.1016/j.jclepro.2021.127080.

[16]W. Cai, S. Jusoh, y X. Yue, «Digitalization and Sustainable Industrial Low-Carbon Transformation: Synergistic Effects, Policy Tools, Technical Pathways, and Financial Innovation», *Sustainability*, vol. 18, n.o 3, ene. 2026, doi: 10.3390/su18031433.

[17] S. T. Nowroz, N. M. Saleh, F. Amsaad, y M. I. Ibrahem, «A Cloud Computing-Enabled ESP32-CAM System for Real-Time Object Recognition with Feedback», en *IEEE Secur. Trustworthy Cyberinfrastructure IoT Microelectron., SATC - Conf. Proc.*, Institute of Electrical and Electronics Engineers Inc., 2025. doi: 10.1109/SATC65530.2025.11137265.

**GLOSARIO**

[Definir los términos técnicos relevantes utilizados en el documento.]

**ANEXOS**

Anexo A: [Título del Anexo]

[Descripción breve del contenido del anexo. Ejemplo: documentación técnica, diagramas, configuraciones, evidencias, etc.]

Por ejemplo:

* Documentación técnica
* Manuales de usuario y administración
* Evidencias de pruebas
* Autorizaciones y validaciones de la entidad receptora
* Repositorio de versionamiento (enlace)
* Formatos de entrevistas y encuestas aplicadas