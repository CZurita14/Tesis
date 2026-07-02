CAPÍTULO III

IMPLEMENTACIÓN, PRUEBAS Y RESULTADOS

El presente capítulo describe la construcción del sistema IoT de monitoreo de residuos textiles y estimación de la huella de carbono implementado en la empresa Faditex Denim, las pruebas realizadas para verificar su funcionamiento y los resultados obtenidos durante el período de medición. Se parte de la descripción de la arquitectura general y el flujo de datos para, posteriormente, detallar la implementación de cada capa, los procedimientos de validación aplicados y el análisis de los resultados operativos, ambientales y predictivos generados por la solución.

3.1 Implementación del Sistema

3.1.1 Arquitectura del Sistema y Flujo de Datos

La arquitectura del sistema se estructuró en cuatro capas funcionales claramente diferenciadas, de modo que el diseño del software y del hardware refleje de manera fiel el recorrido de la información a lo largo de su ciclo de vida. Este enfoque por capas desacopladas permite trazar el flujo del dato desde el entorno físico de la planta de corte hasta la generación de indicadores de gestión, convirtiendo una magnitud física, el peso de los residuos textiles, en inteligencia operativa y ambiental. Cada capa cumple una responsabilidad específica y se comunica con la siguiente a través de una interfaz bien definida, lo que garantiza la trazabilidad completa del dato y la posibilidad de mantener o sustituir cualquier componente sin afectar al resto del sistema.

1. Capa de Ingesta y Comunicación. Corresponde a la obtención ininterrumpida del dato crudo. A nivel perimetral (Edge), se utiliza un microcontrolador ESP32 encargado de gobernar los amplificadores HX711 conectados a las celdas de carga, sobre las cuales se depositan los retazos de tela generados en el proceso de corte y confección. La señal del conversor analógico-digital de 24 bits es convertida a una magnitud de peso, en gramos, mediante un factor de calibración, y cada lectura es empaquetada y transmitida, con una cadencia de cinco segundos, mediante el protocolo ligero MQTT hacia el broker en la nube Adafruit IO, el cual opera como el middleware de recepción y almacenamiento de la serie temporal en el feed denominado peso.

2. Capa de Procesamiento y Limpieza. El motor analítico, implementado en Python, consume el histórico de mediciones exportado desde la nube en formatos CSV y XLSX, incorporando automáticamente todo archivo nuevo a partir de patrones de nombre, sin requerir modificaciones en el código. Los datos crudos atraviesan un proceso de depuración que corrige las taras negativas mediante valor absoluto, descarta lecturas nulas o no numéricas y aplica un filtro de ruido que conserva exclusivamente el rango válido comprendido entre 50 y 2000 gramos, mitigando así tanto el ruido de tara del sensor vacío como los picos anómalos de saturación. Un aspecto central de esta capa es la agregación temporal: dado que el sensor realiza una medición de estado, el peso presente sobre la báscula, y no un conteo incremental, las múltiples lecturas de cada jornada se sintetizan en su máximo diario, valor que representa el mayor volumen de residuo acumulado antes del vaciado de la báscula. Sobre esta base se construyen las variables predictoras mediante ingeniería de características: rezagos del peso de uno a tres días y una media móvil de tres días calculada exclusivamente sobre días previos, a fin de evitar la fuga de información hacia el modelo. Asimismo, el motor de Pandas genera resúmenes estadísticos, distribuciones de frecuencia y una matriz de correlación entre las variables del modelo, que permiten comprender el comportamiento del proceso.

3. Capa de Modelado Predictivo. Constituye el núcleo predictivo de la arquitectura. A diferencia de los algoritmos basados en distancia, el modelo Random Forest no requiere una estandarización previa de las magnitudes, por ejemplo mediante Z-Score, ya que su naturaleza basada en particiones sucesivas de árboles de decisión es invariante a la escala de las variables; esta propiedad simplifica el preprocesamiento sin sacrificar rigurosidad. El conjunto depurado se divide cronológicamente, sin aleatorización, condición obligatoria en las series de tiempo, en subconjuntos de entrenamiento y prueba, y se entrena un regresor Random Forest con la profundidad de los árboles y el tamaño mínimo de hoja controlados, a fin de prevenir el sobreajuste dado el reducido número de jornadas disponibles. El modelo, entrenado sobre el comportamiento histórico, estima el desperdicio esperado, en kilogramos, para el siguiente ciclo de producción.

4. Capa de Presentación e Interfaz Web. El conocimiento generado por el modelo es transformado en inteligencia operativa de fácil interpretación. Utilizando el framework Streamlit y los motores de graficación Matplotlib y Seaborn, el sistema traduce las predicciones y los datos depurados en indicadores de gestión, como la producción estimada, la eficiencia del proceso frente al referente industrial y la huella de carbono expresada en kilogramos de CO2 equivalente, distribuidos en cinco páginas interactivas. Entre los recursos de visualización destaca una gráfica dinámica de CO2 filtrable por rango de fechas, que permite analizar la evolución de las emisiones para un día o una semana específica. Esta capa culmina con la generación automática de un reporte ejecutivo en formato PDF mediante la librería ReportLab, facilitando al responsable de producción la interpretación inmediata del estado ambiental y productivo del proceso.

(En este punto se inserta la Figura 3.1)

Figura 3.1. Arquitectura en cuatro capas y flujo de datos del sistema. Elaboración propia.

La Figura 3.1 sintetiza la arquitectura descrita y evidencia el carácter unidireccional y trazable del flujo de datos: el dato avanza de forma secuencial desde el dispositivo físico de captura, pasa por la nube, el procesamiento y el modelo predictivo, y culmina en la interfaz que consume el usuario. Su importancia radica en que permite comprobar, de un solo vistazo, que un único dato físico, el peso de los residuos, se propaga a través de las cuatro capas sin puntos de quiebre ni transformaciones opacas, desde su obtención en el sensor hasta su interpretación como indicador de decisión. De esta manera, el esquema demuestra el cumplimiento del objetivo del sistema, cuantificar y visualizar la cantidad de residuos textiles generados en el área de producción y su impacto ambiental asociado, y respalda la confiabilidad de los indicadores entregados al responsable de producción gracias a la trazabilidad de extremo a extremo.

3.1.2 Stack Tecnológico

El desarrollo del sistema integró un conjunto de tecnologías de código abierto, seleccionadas por su madurez, su interoperabilidad y su amplia adopción en los ámbitos de la ciencia de datos y el Internet de las Cosas. Con el fin de garantizar la reproducibilidad de la investigación, la Tabla 3.1 presenta el stack tecnológico completo empleado en cada capa del sistema, especificando la versión exacta de cada herramienta y la justificación técnica que motivó su elección. Estas versiones corresponden al entorno virtual con el que se desarrolló y validó la solución, registradas en el archivo requirements.txt, lo que permite a cualquier investigador recrear el entorno de ejecución de manera idéntica y obtener resultados equivalentes.

Tabla 3.1. Stack tecnológico del sistema, con la versión y la justificación técnica de cada componente. Elaboración propia.

Lenguaje de programación: Python, versión 3.14.4. Estándar de la industria para la ciencia de datos, con un ecosistema maduro de librerías de análisis y aprendizaje automático.

Interfaz web: Streamlit, versión 1.58.0. Permite construir el dashboard interactivo directamente en Python, con integración nativa y manejo de estados de sesión para la actualización del sensor en vivo.

Procesamiento de datos: Pandas, versión 3.0.3. Proporciona estructuras y operaciones avanzadas para la manipulación de series temporales y el remuestreo (agregación diaria) de las lecturas del sensor.

Cálculo numérico: NumPy, versión 2.4.6. Soporta las operaciones vectoriales y numéricas que sustentan el procesamiento de datos y el cálculo de las métricas del modelo.

Machine Learning: Scikit-learn, versión 1.9.0. Provee la implementación del algoritmo Random Forest Regressor, empleado para la predicción del desperdicio textil del siguiente ciclo de producción.

Visualización: Matplotlib, versión 3.10.9, y Seaborn, versión 0.13.2. Generan los gráficos del dashboard (series de tiempo, histogramas, matriz de correlación y gráficos de torta) con un estilo visual claro y consistente.

Generación de reportes: ReportLab, versión 4.5.1. Permite la creación programática del reporte ejecutivo en formato PDF con tablas, secciones y estilos corporativos.

Conectividad IoT: cliente Adafruit IO, versión 3.0.0. Gestiona la comunicación con la plataforma en la nube para la lectura de los datos del feed mediante los protocolos MQTT y API REST.

Gestión de credenciales: python-dotenv, versión 1.2.2. Permite cargar las credenciales de Adafruit IO desde variables de entorno, manteniéndolas fuera del código fuente por motivos de seguridad.

Lectura de archivos Excel: openpyxl, versión 3.1.5. Habilita la lectura de los archivos de datos históricos exportados en formato XLSX.

3.1.3 Justificación de la Arquitectura

El diseño y la selección de la arquitectura del sistema se justifican bajo tres pilares de ingeniería: la idoneidad del modelo predictivo frente a la naturaleza de los datos, la resiliencia ante entornos de red industriales inestables y la eficiencia en el ciclo de vida del software. Estos criterios responden, además, a la problemática operativa identificada en Faditex durante el levantamiento de requisitos, en el cual se evidenció que el registro de los residuos textiles se realizaba de forma manual y esporádica: el depósito de retazos se controlaba únicamente cuando se encontraba lleno, sin una toma de datos diaria, lo que ocasionaba demoras en la elaboración de los informes ambientales mensuales solicitados por el GAD de Pelileo. La arquitectura propuesta sustituye ese proceso manual por un flujo de datos automatizado, continuo y trazable.

En primer lugar, la adopción del algoritmo Random Forest como núcleo predictivo responde a la naturaleza no lineal y temporal del desperdicio textil. El volumen de retazos generado en la planta no presenta un comportamiento constante, sino que varía en función del día de la semana, del ritmo de producción reciente y de patrones históricos. Frente a los modelos lineales clásicos, que asumen una relación fija entre las variables, Random Forest captura estas relaciones complejas sin necesidad de especificar una forma matemática previa. Asimismo, al fundamentarse en la combinación de múltiples árboles de decisión, resulta robusto frente al sobreajuste y ofrece una elevada interpretabilidad a través de la importancia de las variables, una ventaja decisiva dado el reducido número de jornadas disponibles para el entrenamiento; a diferencia de los algoritmos basados en distancia, tampoco requiere la estandarización previa de las magnitudes. La pertinencia de esta elección se sustenta, además, en antecedentes de la industria textil donde algoritmos de aprendizaje automático, y en particular Random Forest, han demostrado un buen desempeño en la predicción de variables de producción y de huella de carbono, los cuales se desarrollan en el marco teórico de la presente investigación.

Desde la perspectiva de la infraestructura de telecomunicaciones, la integración de una topología perimetral (Edge) acoplada a un broker MQTT en la nube (Adafruit IO) resuelve los desafíos de conectividad propios de las zonas industriales. El protocolo MQTT, al ser un estándar de mensajería asíncrona y de estructura ultraligera, garantiza una transmisión eficiente de la telemetría incluso en condiciones de bajo ancho de banda o latencia elevada. Como mecanismo de resiliencia, el firmware del microcontrolador ESP32 supervisa en cada ciclo el estado de la conexión Wi-Fi y del enlace MQTT, y los restablece de forma automática ante una caída temporal de la red, evitando la interrupción del servicio de medición; además, la lectura de cada celda de carga se ejecuta únicamente cuando el amplificador HX711 confirma la disponibilidad del dato, lo que previene el bloqueo del dispositivo ante una eventual desconexión del sensor. De manera complementaria, la arquitectura contempla una doble fuente de datos, la lectura en tiempo real desde la nube y el histórico exportado en archivos locales en formatos CSV y XLSX, lo que aporta resiliencia al análisis al permitir reconstruir la serie temporal aun cuando el enlace en vivo no esté disponible.

Finalmente, el despliegue de la capa de presentación y del motor de inferencia mediante Streamlit optimiza los recursos computacionales y reduce la complejidad del sistema. Frente a las arquitecturas web tradicionales orientadas a microservicios, que separan el frontend del backend (por ejemplo, React y Django), Streamlit ofrece una integración nativa con el ecosistema de ciencia de datos de Python, lo que permite que la limpieza de datos, el entrenamiento del modelo y la renderización de la interfaz coexistan en un mismo entorno. El sistema emplea mecanismos de almacenamiento en caché para reutilizar el modelo entrenado y los datos ya procesados sin recalcularlos en cada interacción, y libera de forma explícita los recursos gráficos tras generar cada visualización, evitando el consumo progresivo de memoria durante sesiones de monitoreo prolongadas. Esta decisión arquitectónica disminuye la complejidad del despliegue, posibilita la publicación del dashboard en la nube y asegura tiempos de respuesta adecuados, entregando a la organización una herramienta de monitoreo preventiva, escalable y técnicamente viable.

3.2 Proceso de Implementación

La fase de implementación se ejecutó mediante un flujo de trabajo sistemático que permitió transformar los requerimientos funcionales, levantados junto al usuario, en módulos de software operativos. El proceso abarcó desde el aprovisionamiento del entorno de desarrollo y la configuración del hardware de captura, hasta la construcción del pipeline de datos, el entrenamiento del modelo y el despliegue de la interfaz de visualización. Cada etapa se desarrolló de forma incremental, verificando el correcto funcionamiento de un componente antes de integrarlo con el siguiente, lo que facilitó la detección temprana de errores y mantuvo el sistema operativo a lo largo de todo el desarrollo.

3.2.1 Configuración del Entorno de Desarrollo

Con el objetivo de garantizar la reproducibilidad de la solución y evitar conflictos entre dependencias, el desarrollo se realizó sobre un entorno virtual aislado de Python en su versión 3.14.4. La totalidad de las librerías, junto con sus versiones exactas, se consolidó en el archivo requirements.txt, descrito previamente en la Tabla 3.1, de modo que el entorno completo puede recrearse mediante una única instrucción de instalación. Este aislamiento asegura que la ejecución del sistema sea independiente de las configuraciones particulares de cada máquina y que los resultados obtenidos sean consistentes en distintos despliegues.

La gestión de las credenciales de acceso a la plataforma Adafruit IO se diseñó bajo el principio de no exponer información sensible en el código fuente. Para ello, el sistema contempla dos mecanismos complementarios: en el despliegue en la nube se emplean los secretos de aplicación de Streamlit (st.secrets), mientras que en el entorno local las credenciales se cargan desde un archivo de variables de entorno (.env) mediante la librería python-dotenv. En ambos casos, las llaves de la API permanecen fuera del repositorio de código y excluidas del control de versiones, lo que protege el acceso a la infraestructura del sistema.

3.2.2 Construcción de los Módulos de Software y Entrenamiento del Modelo

En coherencia con las metodologías adoptadas en la investigación, Extreme Programming (XP) para la gestión incremental del desarrollo y OSEMN para la organización del ciclo de vida de los datos, la solución se construyó de forma modular, separando el procesamiento y el entrenamiento del modelo de la capa de inferencia y visualización. Bajo el enfoque de XP, los requerimientos se derivaron de las historias de usuario levantadas con el personal de Faditex y el sistema se edificó de manera iterativa, manteniendo en todo momento una versión funcional y verificable; por su parte, OSEMN proporcionó la estructura conceptual que guió la secuencia de obtención, depuración, exploración y modelado de la información. Esta separación en módulos independientes favorece la reutilización del código, la realización de pruebas aisladas y el mantenimiento del sistema.

El archivo modelo_prediccion.py constituye el motor analítico del sistema. Es el componente encargado de cargar los datos, depurarlos, explorarlos, construir las variables predictoras y entrenar el modelo; concentra, por tanto, las primeras fases de la metodología OSEMN y puede ejecutarse de forma autónoma para procesar por lotes el conjunto histórico y generar los gráficos del análisis exploratorio y de la predicción.

Durante la fase de obtención (Obtain), la función cargar_y_limpiar_datos incorpora automáticamente los archivos del directorio mediante patrones de nombre, unificando en una sola serie temporal las exportaciones de la nube y los archivos locales. Acto seguido, en la fase de depuración (Scrub), esa misma función corrige las taras negativas con valor absoluto, descarta los registros nulos o no numéricos y aplica un filtro que conserva únicamente las lecturas comprendidas entre 50 y 2000 gramos, eliminando el ruido del sensor vacío y los picos de saturación, tal como se muestra en la Figura 3.2.

(En este punto se inserta la Figura 3.2)

Figura 3.2. Corrección de taras y filtrado de ruido en la función cargar_y_limpiar_datos. Elaboración propia.

El procedimiento más determinante de esta etapa, ejecutado por la función integrar_logica_negocio, es la agregación temporal. Dado que el sensor entrega una medición de estado y no un conteo incremental, las múltiples lecturas de cada jornada se sintetizan en su valor máximo diario, que representa el mayor volumen de residuo acumulado antes del vaciado de la báscula. Sobre esa base se construyen las variables predictoras mediante ingeniería de características: los rezagos del peso de uno a tres días y una media móvil de tres días calculada exclusivamente sobre días previos para evitar la fuga de información hacia el modelo. La Figura 3.3 presenta la agregación por máximo diario y la generación de estas variables.

(En este punto se inserta la Figura 3.3)

Figura 3.3. Agregación por máximo diario e ingeniería de características en la función integrar_logica_negocio. Elaboración propia.

Por último, en la fase de modelado (Model), la función entrenar_modelo_random_forest divide el conjunto de forma cronológica, reservando el ochenta por ciento inicial para el entrenamiento y el veinte por ciento final para la prueba, sin aleatorización, condición indispensable en las series de tiempo. A diferencia de los modelos basados en distancia, no se aplica una estandarización de las magnitudes, como el Z-Score, ya que Random Forest es invariante a la escala de las variables. El modelo se configura con un número de árboles parametrizable desde la interfaz, entre 50 y 300 con un valor por defecto de 100, una profundidad máxima de cinco niveles y un mínimo de dos muestras por hoja, restricciones orientadas a prevenir el sobreajuste dado el reducido número de jornadas disponibles; su desempeño se evalúa mediante el error cuadrático medio (RMSE), el error absoluto medio (MAE) y el coeficiente de determinación (R2), complementados con una validación cruzada temporal (TimeSeriesSplit). La configuración y el entrenamiento del modelo se muestran en la Figura 3.4.

(En este punto se inserta la Figura 3.4)

Figura 3.4. Configuración y entrenamiento del modelo Random Forest en la función entrenar_modelo_random_forest. Elaboración propia.

Por su parte, el archivo dashboard_tesis.py corresponde al módulo de inferencia y presentación. Es la aplicación web que reutiliza las funciones del motor analítico para entrenar el modelo, ejecutar la predicción y mostrar los resultados al usuario final. A diferencia de los esquemas que serializan el modelo en archivos binarios almacenados en disco, el sistema lo entrena en memoria y lo conserva mediante la directiva st.cache_resource, apropiada para objetos no serializables como los modelos de Scikit-learn; de este modo, el modelo se entrena una sola vez por configuración y se reutiliza en las sucesivas interacciones del usuario sin recalcularse, optimizando el uso de memoria del servidor. El número de árboles seleccionado actúa como discriminador de la caché, de manera que el reentrenamiento ocurre únicamente cuando ese parámetro se modifica desde la barra lateral, como se aprecia en la Figura 3.5.

(En este punto se inserta la Figura 3.5)

Figura 3.5. Carga y almacenamiento en caché del modelo entrenado en dashboard_tesis.py mediante st.cache_resource. Elaboración propia.

Finalmente, a partir del último día disponible en la serie, el módulo ejecuta la inferencia para estimar el desperdicio del siguiente ciclo y, sobre ese valor, deriva la producción estimada, la tela a consumir y la huella de carbono asociada, que se presentan en las páginas interactivas del dashboard.

3.2.3 Integración y Despliegue del Dashboard

La integración de los componentes consistió en unificar, dentro de una misma interfaz, el flujo de datos en vivo procedente de la nube con el análisis histórico y las predicciones generadas por el modelo. La lectura en tiempo real del sensor se gestionó mediante el decorador st.fragment con el parámetro run_every igual a cuatro, que actualiza de forma autónoma únicamente el componente del sensor cada cuatro segundos, sin necesidad de recargar la página completa; de esta manera se evita el parpadeo visual (flickering) y se mantiene la fluidez de la interfaz, tal como se muestra en la Figura 3.6.

(En este punto se inserta la Figura 3.6)

Figura 3.6. Actualización del sensor en vivo mediante el fragmento st.fragment(run_every=4). Elaboración propia.

Para preservar la eficiencia durante la sesión, las tareas más costosas, es decir, la carga de los datos, el entrenamiento del modelo y el procesamiento del histórico, se ejecutan una sola vez y se conservan en memoria mediante los mecanismos de caché de Streamlit (st.cache_resource y st.cache_data). De este modo, mientras el fragmento del sensor se refresca periódicamente, el resto del sistema no se recalcula, lo que optimiza el uso de los recursos del servidor.

Finalmente, el despliegue se realizó en la nube a través de Streamlit Community Cloud, lo que permite acceder al dashboard desde cualquier navegador sin instalación local. En este entorno, las credenciales de Adafruit IO se inyectan mediante los secretos de aplicación (st.secrets) y los archivos de datos se incorporan al repositorio, desde donde el sistema los carga automáticamente por patrón de nombre.

3.2.4 Resolución de Incidencias Técnicas

Durante la implementación se identificaron y resolvieron diversos desafíos técnicos propios de un entorno industrial, lo que reforzó la robustez del sistema.

Estabilización de las lecturas frente al ruido. Las interferencias electromagnéticas de la maquinaria y la propia deriva del sensor generaban fluctuaciones en las mediciones de peso. Este problema se atendió en dos niveles. En el firmware, cada medición se obtiene como el promedio de cinco muestras consecutivas mediante la instrucción get_units(5), lo que atenúa las fluctuaciones eléctricas momentáneas en el origen. Posteriormente, en el pipeline de datos, se corrigen las taras negativas con valor absoluto y se descartan las lecturas fuera del rango válido de 50 a 2000 gramos, eliminando el ruido del sensor vacío y los picos de saturación antes de que la información llegue al modelo.

Tolerancia a fallos de conectividad. Las caídas intermitentes de la red o las limitaciones de la interfaz de programación de Adafruit IO podían interrumpir el servicio. Para evitar que estos eventos provocaran el cierre de la aplicación, las llamadas a la nube se encapsularon en bloques try/except que capturan el error, informan del estado de la conexión al usuario y permiten que la aplicación continúe operando, como se aprecia en la Figura 3.7. La actualización periódica del fragmento del sensor, cada cuatro segundos, actúa además como un mecanismo de reintento automático, de modo que el servicio se restablece por sí solo una vez recuperado el enlace. De forma complementaria, en el extremo del dispositivo, el firmware del ESP32 supervisa en cada ciclo el estado de la conexión Wi-Fi y MQTT y la restablece de manera automática ante una caída temporal, y realiza la lectura de las celdas únicamente cuando el amplificador confirma la disponibilidad del dato, evitando bloqueos del hardware.

```python
# 1. Comprobación inicial de la conexión con el Broker
try:
    aio = Client(username, key)
    _ = aio.feeds()
    conexion_exitosa = True
except Exception:
    conexion_exitosa = False

# 2. Fragmento asíncrono con reintento automático cada 4 segundos
if conexion_exitosa:
    llave_feed = obtener_llave_feed(username)

    @st.fragment(run_every=4)
    def sensor_en_vivo():
        try:
            datos = aio.data(llave_feed)
            if not datos:
                st.warning("Feed vacío.")
                return
            
            ultimo = datos[0]
            peso_actual = float(ultimo.value)
            st.metric("Peso actual (g)", f"{peso_actual:.1f} g")
            st.metric("Equiv. pantalones", f"{(peso_actual / 1000) * factor_kg_pantalones:.2f} un")
            st.caption("🔄 Actualización cada 4s")
            
        except RequestError as e:
            st.warning(f"Error feed: {e}")

    sensor_en_vivo()
else:
    st.warning("Sin conexión a Adafruit IO")
```

Figura 3.7. Manejo de errores de conexión con Adafruit IO mediante bloques try/except. Elaboración propia.

3.2.5 Despliegue Físico en Planta

La etapa final de la implementación consistió en instalar el componente físico del sistema en el entorno real de producción de Faditex. El conjunto de hardware, conformado por el microcontrolador ESP32, los amplificadores HX711 y las celdas de carga, se ubicó en el área de corte y confección, integrando las celdas en el basurero donde se depositan los residuos del proceso.

De esta manera se garantizó un monitoreo puramente pasivo: los retazos caen por gravedad dentro del basurero instrumentado con las celdas de carga, de modo que el sistema registra automáticamente el peso depositado sin requerir ninguna intervención manual del operario. La ubicación del contenedor debajo de las estaciones de costura asegura que el material generado durante el corte y la confección sea capturado en el punto mismo de su origen, eliminando la dependencia del registro manual que caracterizaba al proceso anterior.

Cabe señalar que el contenedor recibe los residuos del área de corte, que pueden incluir material no textil; por lo tanto, el peso registrado corresponde a todo lo depositado en el basurero. Esta consideración constituye una limitación de la medición, que se aborda en el apartado de limitaciones del sistema.

Como evidencia del correcto funcionamiento del flujo de telemetría, la Figura 3.8 muestra el feed PESO en la plataforma Adafruit IO, donde se reciben y almacenan las lecturas transmitidas por el sensor instalado en planta, confirmando que el dato físico capturado en el basurero llega de forma íntegra a la nube.

(En este punto se inserta la Figura 3.8)

Figura 3.8. Recepción de las lecturas del sensor en el feed PESO de la plataforma Adafruit IO. Elaboración propia.

3.3 Pruebas y Validación

Para verificar el correcto funcionamiento de la solución se aplicaron pruebas de tipo funcional, de validación de datos, de validación del modelo y de conectividad, abarcando tanto el componente físico como el lógico del sistema.

Pruebas funcionales. Se verificó la ejecución completa del pipeline mediante la corrida autónoma del módulo modelo_prediccion.py, comprobando que los procesos de carga, depuración, agregación, entrenamiento y generación de gráficos se ejecutaran de principio a fin sin errores. De igual forma, se validó la integridad del código de la interfaz mediante su compilación, y se comprobó que el dashboard cargara correctamente sus cinco páginas, actualizara la lectura del sensor en vivo y generara el reporte en formato PDF.

Pruebas de validación de datos. Se comprobó que las rutinas de depuración cumplieran su función: la corrección de taras negativas, el descarte de registros nulos o no numéricos y el filtrado del rango válido de 50 a 2000 gramos. Asimismo, se verificó que la agregación por máximo diario produjera una serie temporal coherente con el comportamiento real del proceso, y que la invalidación de los rezagos posteriores a brechas mayores a dos días evitara la incorporación de patrones falsos al modelo.

Pruebas de validación del modelo. El desempeño del modelo Random Forest se evaluó sobre el conjunto de prueba, separado cronológicamente del de entrenamiento, mediante las métricas de error cuadrático medio (RMSE), error absoluto medio (MAE) y coeficiente de determinación (R2), cuyo cálculo se muestra en la Figura 3.9. Para obtener una estimación más robusta, dada la reducida cantidad de jornadas disponibles, se aplicó adicionalmente una validación cruzada temporal (TimeSeriesSplit), que entrena y evalúa el modelo sobre múltiples particiones sucesivas en el tiempo, tal como se presenta en la Figura 3.10. Los valores obtenidos se presentan y analizan en la sección de resultados.

(En este punto se inserta la Figura 3.9)

Figura 3.9. Cálculo de las métricas de evaluación del modelo (RMSE, MAE y R2). Elaboración propia.

(En este punto se inserta la Figura 3.10)

Figura 3.10. Validación cruzada temporal del modelo mediante TimeSeriesSplit. Elaboración propia.

Pruebas de conectividad. Se verificó el comportamiento del sistema ante fallos de red. En el dashboard, la conexión con Adafruit IO se valida al inicio y se gestiona mediante bloques try/except que informan el estado de la conexión y evitan el cierre de la aplicación; la actualización periódica del sensor actúa como reintento automático una vez restablecido el enlace. En el extremo del dispositivo, se comprobó que el firmware del ESP32 restablece de forma automática la conexión Wi-Fi y MQTT tras una caída temporal, y que la lectura de las celdas se realiza únicamente cuando el sensor confirma la disponibilidad del dato.

Aporte a los Objetivos de Desarrollo Sostenible (ODS)

El proyecto contribuye de manera directa a la agenda global de sostenibilidad establecida por la Organización de las Naciones Unidas, aportando a tres de los Objetivos de Desarrollo Sostenible.

ODS 9 (Industria, Innovación e Infraestructura). El sistema fomenta la modernización tecnológica de una micro y pequeña industria local mediante la incorporación de tecnologías de Internet de las Cosas (IoT) y aprendizaje automático (Machine Learning). Al sustituir el registro manual por una infraestructura de monitoreo automatizada y de bajo costo, demuestra que la transformación digital es viable y replicable incluso en pequeñas empresas del sector textil ecuatoriano, reduciendo la brecha tecnológica frente a la gran industria.

ODS 12 (Producción y Consumo Responsables). Al cuantificar de forma objetiva y continua el peso de los residuos textiles generados en el área de corte, el sistema proporciona la información necesaria para optimizar el aprovechamiento de la tela y reducir la generación de desechos. La medición precisa del desperdicio, su equivalencia en unidades de producción perdidas y la predicción del próximo ciclo permiten a la empresa tomar decisiones orientadas a una producción más eficiente y responsable con los recursos.

ODS 13 (Acción por el Clima). El proyecto aporta una metodología técnica para la medición y el seguimiento de la huella de carbono asociada a la fase de fabricación del denim. Al traducir el desperdicio medido en kilogramos de CO2 equivalente, ofrece a la empresa una herramienta concreta para visualizar su impacto ambiental y sustentar acciones de reducción de emisiones, contribuyendo así a la mitigación del cambio climático desde la cadena de valor textil.

En conjunto, la solución no solo resuelve una necesidad operativa de la empresa, sino que la inscribe en el marco de la sostenibilidad, articulando la innovación tecnológica, la eficiencia productiva y la responsabilidad ambiental.
