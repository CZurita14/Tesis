# Contexto del Proyecto — Sistema IoT de Monitoreo de Residuos Textiles
**Faditex Denim · Pelileo, Ecuador · Tesis de Grado 2026**
**Carrera:** Ingeniería en Tecnologías de la Información — Matriz Ambato
**Estudiante:** Christian Zurita · Tutor: Ing. Christian Junta Mg.

---

## 1. Descripción General del Proyecto

Sistema de monitoreo pasivo de información para la presentación de resultados de la huella de carbono usando datos de producción textil en una industria de jeans de denim. El pipeline convierte lecturas físicas de peso de residuos textiles en métricas operativas, ambientales y predictivas visualizadas en un dashboard interactivo.

**Objetivo general:** Implementar un dashboard para el monitoreo y control de datos de contaminación por residuos textiles en Faditex, usando un modelo de Machine Learning, con la finalidad de visualizar la cantidad de residuos textiles generados en el área de producción.

---

## 2. Arquitectura del Pipeline (5 capas)

```
[ESP32 + HX711]  →  [Adafruit IO]  →  [ETL Python]  →  [Random Forest]  →  [Streamlit Dashboard]
  Sensor físico       MQTT/Nube        Limpieza y          Predicción           Visualización
  peso residuos       REST API         lógica negocio      desperdicio          + PDF report
  cada ~6 seg         feed: "peso"     agregación diaria   siguiente ciclo      KPIs + alertas
```

### Hardware
- **Microcontrolador:** ESP32 (WiFi integrado)
- **Celdas de carga:** HX711 (amplificador de celda de carga)
- **Configuraciones:** 5 celdas (CodigoTesis.txt) y 2 celdas (Codigo-Tesis-2placas.txt)
- **Factor de calibración:** 353.f
- **Frecuencia de lectura:** ~6 segundos por lectura
- **Protocolo:** MQTT → Adafruit IO feed "peso"

### Transmisión (Adafruit IO)
- **Usuario:** Sensorpeso2
- **Feed:** peso
- **Credenciales:** en `.env` (ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
- **Cliente Python:** `Adafruit_IO` con `@st.fragment(run_every=4)` para lectura en vivo

---

## 3. Archivos del Proyecto

| Archivo | Descripción |
|---|---|
| `dashboard_tesis.py` | Dashboard Streamlit principal (747 líneas, 5 páginas) |
| `modelo_prediccion.py` | ETL + entrenamiento Random Forest (245 líneas) |
| `Datos-sensores-entrenamiento.xlsx` | Datos históricos de Adafruit IO (hoja "Hoja2") |
| `Datos-actuales.xlsx` | Datos más recientes |
| `SensorPESO1-20260310-2114.csv` | CSV de sensor 1 |
| `SensorPESO3-20260310-2122.csv` | CSV de sensor 3 |
| `requirements.txt` | streamlit, pandas, numpy, matplotlib, seaborn, scikit-learn, adafruit-io, python-dotenv, openpyxl, reportlab |
| `.env` | Credenciales Adafruit IO |
| `CodigoTesis.txt` | Firmware ESP32 para 5 celdas de carga |
| `Codigo-Tesis-2placas.txt` | Firmware ESP32 para 2 celdas de carga |
| `EstadodelArte/` | 21 papers académicos de respaldo teórico |

---

## 4. Constantes de Negocio (Faditex)

Definidas en `modelo_prediccion.py` líneas 90–93. Son el núcleo de todos los cálculos derivados.

```python
TELA_ADQUIRIDA_M       = 9805.66   # metros de tela adquirida por mes
TELA_POR_PANTALON_M    = 1.20      # metros de tela por pantalón (rango 1.10–1.30)
DESPERDICIO_PROM_M     = 45        # metros de tela desperdiciada por mes (rango 40–50)
DENSIDAD_TELA_G_POR_M  = 225       # gramos por metro lineal de tela denim
CO2_POR_PANTALON_KG    = 6.5       # kg CO₂eq por jean (etapa de fabricación, ~20% ciclo de vida)
```

**Métricas derivadas de estas constantes:**
```python
pantalones_por_mes              = (9805.66 - 45) / 1.20  = 8134 pantalones/mes
metros_desperdicio_por_pantalon = 45 / 8134              = 0.005534 m/pant
factor_kg_a_pantalones          = 1000 / (225 × 0.005534) = 803.2 pant/kg
```

---

## 5. Pipeline ETL — `modelo_prediccion.py`

### 5.1 Función `cargar_y_limpiar_datos()`
- Carga automática de todos los archivos `Datos*.xlsx` del directorio
- Columnas requeridas: `created_at`, `value`
- Limpieza: valores nulos, conversión numérica, valores absolutos (corrige taras negativas)
- **Filtro de ruido:** conserva solo lecturas entre 50g y 2000g
  - `< 50g` → ruido de tara del sensor vacío
  - `> 2000g` → picos anómalos
- Zona horaria: UTC → local (tz_localize)
- Resultado: DataFrame con índice temporal ordenado

### 5.2 Función `integrar_logica_negocio()`
- **Agregación diaria:** `resample('D').agg({'value': 'max'})`
  - Se usa el MÁXIMO porque el sensor mide el peso acumulado en la báscula (medición de estado, no incremental)
  - El pico diario = mayor acumulado antes de vaciar = desperdicio real del día
  - `sum()` multiplicaría por ~14,400 lecturas/día → valores erróneos
- Columnas calculadas:
  ```python
  peso_total_kg          = peso_total_g / 1000
  metros_desperdicio     = peso_total_g / 225          # DENSIDAD_TELA_G_POR_M
  pantalones_procesados  = metros_desperdicio / 0.005534
  tela_consumida_m       = pantalones_procesados × 1.20
  desperdicio_estimado_g = peso_total_g                # dato real del sensor
  ```
- **Features temporales:** dia_semana, dia_mes, mes
- **Variables lag:** peso_lag_1, peso_lag_2, peso_lag_3 (en kg)
- **Media móvil:** media_movil_3d (ventana 3 días)
- **Invalidación de lags:** se anulan lags contaminados por brechas > 2 días entre registros (evita patrones falsos)
- Elimina filas con NaN tras el proceso de lags

### 5.3 Función `entrenar_modelo_random_forest()`
- **Features (X):** `['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']`
- **Target (y):** `peso_total_kg`
- **Split temporal:** 80% entrenamiento / 20% prueba, `shuffle=False` (obligatorio en series de tiempo)
- **Hiperparámetros:**
  ```python
  RandomForestRegressor(
      n_estimators  = configurable (50–300, default 100),
      max_depth     = 5,      # máximo 32 nodos por árbol
      min_samples_leaf = 2,   # evita overfitting con ~22 días de entrenamiento
      random_state  = 42
  )
  ```
- **Métricas de evaluación:**
  - RMSE (Raíz del Error Cuadrático Medio) en kg
  - MAE (Error Absoluto Medio) en kg
  - R² Entrenamiento y R² Prueba
  - Gap train-prueba (< 0.10 = sin overfitting)
  - **MAPE → Seguridad (%):** `(1 - MAPE) × 100`
- Genera gráfico: `prediccion_random_forest.png`

---

## 6. Dashboard Streamlit — `dashboard_tesis.py`

### Estructura de navegación (sidebar)
```
📊 Dashboard Principal
📈 Análisis de Datos
🌱 Huella de Carbono
🌲 Bosque Aleatorio
📄 Reporte
```

Configuración del modelo en sidebar: selector de árboles [50, 100, 150, 200, 300]

---

### 6.1 Página: Dashboard Principal

**Fila de 6 métricas (KPI cards):**

| Métrica | Fórmula | Descripción |
|---|---|---|
| Días Analizados | `len(df_historico)` | Días con registros válidos post-ETL |
| Pantalones Est. | `sum(metros_desperdicio / 0.005534)` | Derivado del desperdicio medido |
| Tela Consumida | `sum(pantalones × 1.20)` | Metros netos de producción |
| Eficiencia | `tela_útil / (tela_útil + desperdicio) × 100` | Benchmark industrial: 92–95% |
| CO₂ Período | `total_pantalones × 6.5` | kg CO₂eq etapa fabricación |
| Precisión Modelo | `(1 - MAPE) × 100` | Exactitud del Random Forest |

**Gráficos:**
- Sensor en vivo (Adafruit IO, actualización cada 4s)
- Desperdicio diario en kg (serie temporal, área bajo la curva)
- Tela útil vs desperdicio (gráfico de torta, verde/rojo)
- CO₂ diario por producción (serie temporal naranja)

**Panel de predicción (siguiente ciclo):**
```python
prediccion_futura_kg = modelo_rf.predict(ultimo_dia[features_modelo])
pantalones_futuros   = prediccion_futura_kg[0] × factor_kg_pantalones
tela_futura          = pantalones_futuros × 1.20
co2_prediccion       = pantalones_futuros × 6.5
```

**Panel de pérdida:**
- Pantalones no producidos: `total_metros_desperdicio / 1.20`
- CO₂ evitado si −10%: `co2_total_kg × 0.10`

---

### 6.2 Página: Análisis de Datos

Tres pestañas:
1. **Serie de Tiempo:** desperdicio diario en kg (histórico completo)
2. **Distribución del Peso:** histograma con KDE del peso diario
3. **Matriz de Correlación:** heatmap entre peso_kg, pantalones, tela, desperdicio_g

---

### 6.3 Página: Huella de Carbono

**4 métricas KPI:**

| KPI | Valor / Fórmula |
|---|---|
| CO₂ Total del Período | `total_pantalones × 6.5` |
| CO₂ por Jean (fabricación) | 6.5 kg CO₂eq (constante LCA) |
| CO₂ evitado si −10% desperdicio | `co2_total × 0.10` |
| Intensidad CO₂ Diaria | `co2_total / días` |

**Gráficos:**
- CO₂ diario por día de producción (serie temporal)
- Tela útil vs desperdicio con valores absolutos en metros
- Producción vs Pérdida (barras verticales pantalones producidos vs perdidos)
- Fabricación vs Ciclo Completo: 6.5 kg fabricación vs 32.7 kg ciclo de vida

---

### 6.4 Página: Bosque Aleatorio

- Explicación conceptual del algoritmo
- Gráfico de votos de los primeros 20 árboles individuales vs promedio final
- Slider para explorar predicción árbol por árbol (1–10 árboles)
- Conclusión final: predicción promedio del bosque

---

### 6.5 Página: Reporte PDF (ReportLab)

Genera PDF con 5 secciones:

1. **Período medido y cobertura del sensor**
   - Fechas, días activos, frecuencia (~6 seg, ESP32 + HX711)

2. **Producción y eficiencia del proceso**
   - Pantalones, tela consumida, desperdicio, eficiencia %
   - Comparación vs benchmark industrial 92–95%

3. **Desperdicio generado e impacto en producción**
   - kg residuos, equivalencia pantalones no fabricados, tasa de desperdicio %
   - Cálculo de oportunidad: benchmark 2.5% sector

4. **Huella de carbono e impacto ambiental**
   - CO₂ total, factor 6.5 kg, proyección anual
   - Equivalencias: `co2_total × 4.0` km en automóvil, `co2_total / 14` árboles/año

5. **Proyección y recomendaciones para próximo ciclo**
   - Predicción RF: kg, pantalones, tela, CO₂
   - Precisión MAPE
   - Escenario de optimización: −33% CO₂ si se revisan patrones de corte

---

## 7. Fórmula de Huella de Carbono — Cadena Completa

### De sensor a CO₂ (4 pasos)

```
PASO 1: Sensor HX711 mide peso de residuos textiles acumulados en la báscula
        → peso_diario_g (valor máximo del día)

PASO 2: Conversión a metros de tela desperdiciada
        metros_desperdicio = peso_g ÷ 225 g/m

PASO 3: Estimación de pantalones que representan ese desperdicio
        pantalones = metros_desperdicio ÷ 0.005534 m/pant
        (donde 0.005534 = 45 m desperdicio/mes ÷ 8134 pant/mes)

PASO 4: Cálculo de huella de carbono
        CO₂_kg = pantalones × 6.5 kg CO₂eq/jean
```

### Justificación científica del factor 6.5 kg CO₂eq/jean

El factor 6.5 kg CO₂eq tiene triple respaldo en el Estado del Arte:

| Fuente | Dato | Validación |
|---|---|---|
| Periyasamy & Duraisamy (2018) — Springer | Corte + Acabado + Lavado + Empaque = 6.9 kg CO₂ | ≈ 6.5 kg para la etapa controlable por la fábrica |
| Zhao et al. (2021) — J. Cleaner Production | Ciclo completo jean 340g = 33.4 kg CO₂eq | 6.5 / 33.4 = 19.5% ≈ 20% fase fabricación |
| Wang et al. (2024) — SSRN | Knitwear de algodón = 6.58 kg CO₂eq | Validación cruzada por tipo de prenda similar |

**Desglose del ciclo de vida completo (Periyasamy & Duraisamy, 2018, Fig. 11):**

| Fase | kg CO₂ | Controlable por fábrica |
|---|---|---|
| Cultivo de fibra | 4.64 | No |
| Producción de tela | 14.4 | Parcial |
| Corte y confección | 3.20 | **Sí** |
| Acabado | 0.96 | **Sí** |
| Lavado industrial | 2.10 | **Sí** |
| Empaque | 0.64 | **Sí** |
| Transporte y comercio | 6.10 | No |
| **Fase consumidor (lavados)** | **20.00** | No (~80% del total) |
| Fin de vida | 1.44 | No |

**Este sistema monitorea y cuantifica exclusivamente las fases controlables por Faditex.**

---

## 8. KPIs del Sistema (4 grupos validados)

### KPI 1 — Producción del Período

| Indicador | Fórmula | Unidad |
|---|---|---|
| Días Analizados | `len(df_historico)` | días |
| Pantalones Totales Estimados | `Σ(metros / 0.005534)` | unidades |
| Tela Consumida Estimada Total | `Σ(pantalones × 1.20)` | metros |

> **Nota:** La "Seguridad del Aprendizaje" (MAPE del modelo) está actualmente en este bloque pero conceptualmente pertenece a la página técnica del Bosque Aleatorio. Pendiente de mover.

---

### KPI 2 — Huella de Carbono (Etapa de Fabricación)

| Indicador | Fórmula | Fuente |
|---|---|---|
| CO₂ Total del Período | `Σpantalones × 6.5` | Periyasamy 2018, Zhao 2021 |
| CO₂ por Jean (fabricación) | 6.5 kg CO₂eq (constante) | ACV / LCA |
| CO₂ Evitado si −10% Desperdicio | `co2_total × 0.10` | Indicador prospectivo |
| Intensidad CO₂ Diaria | `co2_total / días` | Comparación inter-períodos |

> **Pendiente:** Reubicar el gráfico de CO₂ diario del Dashboard Principal a esta sección como visual central.
> **Pendiente:** Crear KPI de Trazabilidad (flujo ESP32 → Nube → ML → Dashboard) como primer elemento del dashboard.

---

### KPI 3 — Eficiencia del Proceso

```
Eficiencia (%) = tela_consumida_m / (tela_consumida_m + metros_desperdicio) × 100
```

Benchmark industrial: 92–95%. Si marca 96% → 4% fue merma.
**Estado:** completamente implementado.

---

### KPI 4 — Pantalones No Producidos por Desperdicio

```
Pantalones perdidos = metros_desperdicio_total / 1.20
```

Convierte metros de desperdicio en unidades de producción perdidas. Responde: ¿cuántos pantalones adicionales podrían haberse fabricado?
**Estado:** completamente implementado.

---

## 9. Estado de Implementación del Dashboard

| Elemento | Estado | Ubicación actual |
|---|---|---|
| KPI 1 (3 indicadores de producción) | ✅ Implementado | dashboard_tesis.py:365-367 |
| KPI 1 "Seguridad del Aprendizaje" | ⚠️ Mal ubicado | dashboard_tesis.py:370 (mover a Bosque Aleatorio) |
| KPI 2 (4 métricas CO₂) | ✅ Implementado | Página Huella de Carbono, líneas 535-539 |
| KPI 2 Gráfico CO₂ diario | ⚠️ Página incorrecta | Está en Dashboard Principal, debería estar en Huella de Carbono |
| KPI 3 Eficiencia | ✅ Implementado | dashboard_tesis.py:368 |
| KPI 4 Pantalones perdidos | ✅ Implementado | dashboard_tesis.py:455-456 |
| KPI Trazabilidad (flujo IoT) | ❌ No existe | Pendiente crear como primer elemento del dashboard |

---

## 10. Cambios Pendientes en el Dashboard (3 cambios)

### Cambio 1 — Reestructurar KPI 1
- Mover `"🤖 Precisión Modelo"` de la fila de 6 métricas del Dashboard Principal a la página Bosque Aleatorio
- Renombrar el bloque de 3 métricas restantes a "Producción del Período"

### Cambio 2 — Reubicar gráfico de CO₂ diario
- El gráfico `"🌱 CO₂ Diario por Producción (kg)"` (líneas 436-444) debe moverse o duplicarse como visual central de la página Huella de Carbono

### Cambio 3 — Crear KPI de Trazabilidad
- Nuevo elemento visual como primer sección del dashboard
- Muestra el flujo completo: `ESP32 + HX711 → Adafruit IO → ETL → Random Forest → Dashboard`
- Indicador: 100% trazabilidad del dato desde sensor hasta KPI

---

## 11. Cambios Pendientes en la Presentación PPTX

### Diapositiva nueva (insertar entre diap. 21 y 22)
**Título:** ¿Cómo se calcula la Huella de Carbono en este sistema?

**Contenido:**
- Tabla del ciclo de vida completo del jean con porcentajes
- Cadena de 4 pasos: sensor → metros → pantalones → CO₂
- Fuentes: Periyasamy & Duraisamy (2018), Zhao et al. (2021), Wang et al. (2024)

### Diapositiva 22 — Completar bloque "EMISIONES POR FABRICACIÓN"
- Valor: `6.5 kg CO₂ / jean`
- Descripción con conexión a los 3 KPIs del dashboard: CO₂ Período, Intensidad Diaria, CO₂ Evitado
- Fuente ACV citada

### Correcciones de redacción en diapositiva 22
- "Un **echo**" → "Un **hecho**"
- "product final" → "producto final"
- "pantalos" → "pantalones"
- "flujo complete" → "flujo completo"

---

## 12. Estado del Arte — Mapa de Referencias por Componente

### Sensores IoT / ESP32
- Jayetileke, de Mel & Mukhopadhyay (2024 — IEEE): ESP32 + Xbee S2C para Industry 5.0, 20 Hz
- Cai, Jusoh & Yue (2026 — Sustainability): IoT reduce consumo energético 9.7% en textiles

### Machine Learning / Random Forest
- Guldurek (2024 — IEEE Access): RF R²=0.993 en fábrica de denim (ATLAS Denim, Turquía) — el más cercano metodológicamente
- Li et al. (2025 — Sustainability): ML para predicción de huella de carbono en 672 productos textiles
- Dargan et al. (2019 — Arch. Computational Methods Engineering): Survey de ML y Deep Learning

### Huella de Carbono del Jean
- Periyasamy & Duraisamy (2018 — Springer): Datos numéricos fase a fase, Fig. 11 → 6.9 kg confección ≈ 6.5 kg
- Zhao et al. (2021 — J. Cleaner Production): Ciclo completo 33.4 kg CO₂eq, 80% en fabricación
- Wang et al. (2024 — SSRN): Knitwear = 6.58 kg CO₂eq, validación cruzada

### ACV / Metodología LCA
- Karthik & Murugan (2017 — Elsevier): ISO 14040, ISO 14067, PAS 2050, GHG Protocol
- Periyasamy, Wiener & Militky (2017 — Elsevier): 4 etapas del ACV para denim
- Karagöl et al. (2024 — Fibres & Textiles): LCA con SimaPro en denim reciclado

### Industria 4.0 / Economía Circular Textil
- de Oliveira Neto et al. (2024 — IJECT): I4.0 en industria jeanera brasileña, cyber-physical systems
- Xu Chen et al. (2026 — Industria Textilă): Revisión bibliométrica 349 papers (2005–2025), crecimiento exponencial desde 2012
- Xu Chen et al. (2026): Hot topics actuales: monitoreo IA + huella de carbono + cadena verde

---

## 13. Paleta Visual del Dashboard

```python
BG     = '#0E1117'  # fondo Streamlit (negro azulado)
AX_BG  = '#1A1D27'  # fondo de ejes
FG     = '#FAFAFA'  # texto
GRID   = '#2B2D3A'  # grillas
C_BLUE = '#4A9EDB'  # desperdicio diario (serie temporal)
C_ORG  = '#F39C12'  # CO₂ diario (naranja)
C_GRN  = '#2ECC71'  # tela útil / producción
C_RED  = '#E74C3C'  # desperdicio / pérdida
C_PUR  = '#9B59B6'  # distribución de peso
C_GRAY = '#7F8C8D'  # ciclo de vida completo (referencia)
```

---

## 14. Notas Importantes para el Jurado

1. **El sensor no mide pantalones directamente.** Mide el peso de los retazos acumulados en la báscula. La conversión a pantalones usa la proporción histórica de desperdicio de Faditex (45 m/mes sobre 8,134 pant/mes).

2. **El 6.5 kg CO₂ NO es el ciclo de vida completo.** Es exclusivamente la etapa de fabricación controlable por la empresa. El ciclo completo es 32–33.4 kg CO₂eq (incluyendo lavados del consumidor que representan ~80%).

3. **El modelo usa el MÁXIMO diario, no la suma.** Porque el sensor es una medición de estado (peso actual en báscula), no un contador incremental. Usar suma produciría valores 14,400 veces inflados.

4. **La precisión del modelo (MAPE) es la métrica correcta** para series temporales con varianza comprimida en el conjunto de prueba. R² puede dar valores negativos en estos casos aunque el modelo sea útil.

5. **Los lags se invalidan automáticamente** cuando hay brechas de más de 2 días entre registros, evitando que el modelo aprenda patrones temporales falsos.

---

*Documento generado el 2 de junio de 2026. Mantener actualizado con cada cambio al pipeline.*
