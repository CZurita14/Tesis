# Sistema IoT para Monitoreo de Residuos Textiles y Huella de Carbono

**Tesis de Grado — Ingeniería en Tecnologías de la Información**  
**Universidad Técnica de Ambato**  
**Estudiante:** Christian Zurita · **Tutor:** Ing. Christian Junta Mg.  
**Empresa:** Faditex Denim · Pelileo, Ecuador · 2026

---

## Descripción

Sistema de monitoreo pasivo basado en IoT que convierte lecturas físicas de peso de residuos textiles en métricas operativas, ambientales y predictivas. Una balanza con celdas de carga instalada en la línea de denim mide el desperdicio, lo envía a la nube, y un pipeline en Python lo limpia, lo modela con Machine Learning (Random Forest) y lo presenta en un dashboard interactivo con generación de reportes en PDF.

> **Alcance:** es una **prueba de concepto** que demuestra el pipeline completo de extremo a extremo. El modelo predictivo gana poder a medida que se acumulan más días de medición real (ver [Limitaciones conocidas](#limitaciones-conocidas)).

---

## Arquitectura del Sistema

```text
┌─────────────────┐     WiFi/MQTT      ┌──────────────────┐
│  ESP32 + HX711  │ ─────────────────► │   Adafruit IO    │
│  Celdas de carga│   1 lectura / 5 s  │  (MQTT / REST)   │
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

- **Hardware:** ESP32, amplificador HX711, celdas de carga.
- **Nube y comunicación:** MQTT, Adafruit IO.
- **Backend y Machine Learning:** Python (Pandas, NumPy, scikit-learn).
- **Frontend y reportes:** Streamlit, Matplotlib, Seaborn, ReportLab.

---

## Funcionalidades del Dashboard

El dashboard tiene 5 páginas:

1. **Dashboard Principal** — KPIs del período (pantalones, tela, eficiencia, CO₂), lectura del sensor **en vivo** (actualización cada 4 s), serie de tiempo, distribución tela útil vs desperdicio y predicción del siguiente ciclo.
2. **Análisis de Datos** — serie de tiempo, histograma de distribución del peso y **matriz de correlación** entre las variables del modelo (peso, rezagos, media móvil y variables temporales).
3. **Huella de Carbono** — métricas de CO₂ y una **gráfica dinámica con filtro de rango de fechas**: puedes elegir un día o una semana específica y la gráfica y el CO₂ del rango se recalculan.
4. **Bosque Aleatorio** — explicación visual e interactiva de cómo el Random Forest promedia los árboles para la predicción.
5. **Reporte** — generación y descarga de un **reporte PDF** completo del período (producción, eficiencia, huella de carbono y proyección).

---

## Modelo Predictivo (resumen técnico)

- **Variable objetivo:** peso de desperdicio diario (kg), agregado tomando el **máximo diario** del sensor (mide el peso acumulado en la báscula antes de vaciarla, no un incremental).
- **Variables predictoras:** día de la semana, día del mes, mes, rezagos de 1/2/3 días y media móvil de 3 días.
- **Validación temporal:** división cronológica 80/20 (`shuffle=False`) más validación cruzada temporal (`TimeSeriesSplit`) para métricas más robustas.
- **Anti-sobreajuste:** `max_depth=5` y `min_samples_leaf=2`, adecuados para un conjunto pequeño de días.
- **Cuidados metodológicos aplicados:**
  - La media móvil usa solo días pasados (se evita la fuga de datos / *data leakage*).
  - Los rezagos se invalidan tras brechas temporales mayores a 2 días, para no aprender patrones falsos.
  - La matriz de correlación usa las variables reales del modelo (no las de negocio, que son transformaciones lineales del mismo dato y correlacionan 1.00 trivialmente).

---

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/CZurita14/Tesis.git
cd Tesis
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

Las dependencias en `requirements.txt` están **fijadas a versiones específicas** para garantizar reproducibilidad.

### 3. Credenciales

El sistema requiere acceso a Adafruit IO. Por seguridad, **este repositorio no incluye credenciales**. Configura las variables de entorno `ADAFRUIT_IO_USERNAME` y `ADAFRUIT_IO_KEY`:

- **Local:** créalas en un archivo `.env` en la raíz (ya está en `.gitignore`).
- **Streamlit Cloud:** en *Settings → Secrets*.

### 4. Archivos de datos

Coloca los exports de los sensores en la raíz del proyecto. El ETL los carga **automáticamente por patrón de nombre**:

- Excel: cualquier archivo que empiece con `Datos` (`Datos*.xlsx`).
- CSV: cualquier archivo que contenga `PESO` (`*PESO*.csv`).

Así, al agregar un nuevo export de Adafruit IO con ese nombre, se incluye sin tocar el código.

---

## Uso

Iniciar el dashboard interactivo:

```bash
streamlit run dashboard_tesis.py
```

Se abre en el navegador (por defecto `http://localhost:8501`).

Ejecutar solo el ETL y el entrenamiento del modelo (genera los gráficos exploratorios y de predicción en disco):

```bash
python modelo_prediccion.py
```

---

## Estructura del Proyecto

- `dashboard_tesis.py` — aplicación web principal (Streamlit): KPIs, gráficos y generación del reporte PDF.
- `modelo_prediccion.py` — ETL (extracción, limpieza y agregación) y entrenamiento del Random Forest.
- `CodigoTesis.ino` — firmware (C++/Arduino) para el ESP32 de 5 celdas.
- `Codigo-Tesis-2placas.ino` — firmware para el ESP32 de 2 celdas.
- `requirements.txt` — dependencias con versiones fijadas.
- `Datos*.xlsx`, `*PESO*.csv` — datos históricos de los sensores.
- `EstadodelArte/` — papers académicos que respaldan el proyecto.

> **Nota sobre el firmware:** las credenciales WiFi están como *placeholders* (`TU_SSID`, `TU_PASSWORD_WIFI`). Reemplázalas por las reales antes de cargar el código al ESP32. Los pines GPIO de salida (SCK) usan pines válidos del ESP32 (evitando los GPIO 34–39, que son solo de entrada).

---

## Limitaciones conocidas

- **Cantidad de datos:** el modelo entrena con un número reducido de días con medición útil. Con esa muestra, las métricas son orientativas y el modelo debe interpretarse como **prueba de concepto**, no como un predictor de producción. A mayor cantidad de días con desperdicio real medido, mayor poder predictivo.
- **Calidad del dato:** las lecturas de báscula vacía (≈0 g) o por debajo de 50 g se filtran como ruido; solo aportan valor los períodos con desperdicio real sobre la báscula.
- **Variables de negocio:** cifras como pantalones, tela consumida y CO₂ son **estimaciones derivadas** del peso medido y de constantes del proceso productivo; la única medición física directa es el peso del sensor.

---

## Autor

**Christian Zurita**  
Estudiante de Ingeniería en Tecnologías de la Información  
Universidad Técnica de Ambato — Ambato, Ecuador  
GitHub: [@CZurita14](https://github.com/CZurita14)

---

## Licencia

Proyecto desarrollado con fines académicos como tesis de grado. Uso libre para fines educativos y de investigación. Para uso comercial, contactar al autor.
