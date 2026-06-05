# Sistema IoT para Monitoreo de Residuos Textiles y Huella de Carbono

**Tesis de Grado — Ingeniería en Tecnologías de la Información**  
**Universidad Técnica de Ambato**  
**Estudiante:** Christian Zurita · **Tutor:** Ing. Christian Junta Mg.  
**Empresa:** Faditex Denim · Pelileo, Ecuador · 2026

---

## Descripción

Sistema de monitoreo pasivo basado en IoT que convierte lecturas físicas de peso de residuos textiles en métricas operativas, ambientales y predictivas. Captura datos de celdas de carga instaladas en la línea de producción de denim, los transmite a la nube, aplica un pipeline de limpieza de datos (ETL) y entrena un modelo de Machine Learning (Random Forest) para predecir el desperdicio del siguiente ciclo productivo. 

Los resultados y la huella de carbono estimada se visualizan en un dashboard interactivo desarrollado en Streamlit.

---

## Arquitectura del Sistema

```text
┌─────────────────┐     WiFi/MQTT      ┌──────────────────┐
│  ESP32 + HX711  │ ─────────────────► │   Adafruit IO    │
│  Celdas de carga│   ~6 seg/lectura   │  (MQTT / REST)   │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                                ▼
                                   ┌────────────────────────┐
                                   │   ETL Python           │
                                   │   Limpieza y Agregación│
                                   └────────────┬───────────┘
                                                │
                                                ▼
                                   ┌────────────────────────┐
                                   │   Random Forest        │
                                   │   Modelo Predictivo    │
                                   └────────────┬───────────┘
                                                │
                                                ▼
                                   ┌────────────────────────┐
                                   │   Streamlit Dashboard  │
                                   │   Visualización y PDF  │
                                   └────────────────────────┘
```

---

## Stack Tecnológico

- **Hardware:** ESP32, Amplificador HX711, Celdas de carga.
- **Nube y Comunicación:** MQTT, Adafruit IO.
- **Backend y Machine Learning:** Python (Pandas, NumPy, scikit-learn).
- **Frontend y Reportes:** Streamlit, Matplotlib, Seaborn, ReportLab.

---

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/CZurita14/Pipeline.git
cd Pipeline
```

### 2. Entorno virtual e instalación

```bash
python -m venv .venv

# Activar en Windows
.venv\Scripts\activate
# Activar en macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Credenciales
Para conectarse a la nube, el sistema requiere acceso a Adafruit IO. Por razones de seguridad, **este repositorio no incluye archivos de credenciales**. 
Debes configurar las variables de entorno necesarias (`ADAFRUIT_IO_USERNAME` y `ADAFRUIT_IO_KEY`) de forma segura a través de tu gestor de entorno local o en la configuración de *Secrets* si despliegas en Streamlit Cloud.

### 4. Archivos de Datos
Asegúrate de colocar los archivos `.xlsx` y `.csv` con los datos históricos de los sensores en el directorio raíz antes de ejecutar el proyecto.

---

## Uso

Para iniciar el dashboard interactivo de Streamlit, ejecuta:

```bash
streamlit run dashboard_tesis.py
```
El sistema se abrirá automáticamente en tu navegador (por defecto en `http://localhost:8501`).

Para ejecutar únicamente el proceso de extracción de datos y entrenamiento del modelo (que generará los gráficos exploratorios de forma local), ejecuta:

```bash
python modelo_prediccion.py
```

---

## Estructura Principal del Proyecto

- `dashboard_tesis.py`: Aplicación web principal (Frontend y lógicas de KPIs).
- `modelo_prediccion.py`: Script de extracción, transformación de datos (ETL) y entrenamiento del algoritmo Random Forest.
- `CodigoTesis.txt`: Código fuente (Firmware en C++) para el microcontrolador ESP32 de 5 placas.
- `Codigo-Tesis-2placas.txt`: Código fuente para el ESP32 de 2 placas.
- `requirements.txt`: Dependencias del proyecto.
- `EstadodelArte/`: Carpeta con la documentación y los papers académicos que respaldan el proyecto.

---

## Autor

**Christian Zurita**  
Estudiante de Ingeniería en Tecnologías de la Información  
Universidad Técnica de Ambato — Ambato, Ecuador  
GitHub: [@CZurita14](https://github.com/CZurita14)

---

## Licencia

Este proyecto fue desarrollado con fines académicos como tesis de grado. El uso del código es libre para fines educativos y de investigación. Para uso comercial, contactar al autor.
