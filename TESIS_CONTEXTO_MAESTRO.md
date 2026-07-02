# DOCUMENTO MAESTRO DE TESIS — Sistema IoT de Monitoreo de Residuos Textiles y Huella de Carbono
## Faditex Denim · Pelileo, Ecuador · Tesis de Grado 2026
### Carrera: Ingeniería en Tecnologías de la Información — Universidad Técnica de Ambato, Matriz Ambato
### Estudiante: Christian Zurita · Tutor: Ing. Christian Junta Mg.

> **Propósito de este documento:** Entrenamiento de IA para asistir en la construcción de documentación académica, validación de estructura y generación de contenido de tesis. Contiene el contexto técnico completo del proyecto más el Estado del Arte sintetizado de 21 papers académicos.

---

## PARTE 1: ESTRUCTURA GENERAL DE LA TESIS

### 1.1 Título de la Tesis

**"Implementación de un sistema IoT para el monitoreo y control de residuos textiles en la empresa Faditex Denim, utilizando Machine Learning para la estimación de la huella de carbono"**

### 1.2 Resumen Ejecutivo

Sistema de monitoreo pasivo de información para la presentación de resultados de la huella de carbono usando datos de producción textil en una industria de jeans de denim (Faditex, Pelileo, Ecuador). El pipeline convierte lecturas físicas de peso de residuos textiles en métricas operativas, ambientales y predictivas visualizadas en un dashboard interactivo.

**Objetivo general:** Implementar un dashboard para el monitoreo y control de datos de contaminación por residuos textiles en Faditex, usando un modelo de Machine Learning, con la finalidad de visualizar la cantidad de residuos textiles generados en el área de producción.

**Problema:** Las fábricas de denim en Latinoamérica no tienen sistemas automatizados para cuantificar residuos textiles ni calcular su huella de carbono. El monitoreo manual es esporádico, impreciso y no permite predicción ni optimización.

**Solución propuesta:** Pipeline de 5 capas: sensor físico (ESP32 + HX711) → nube MQTT (Adafruit IO) → ETL Python → modelo predictivo (Random Forest) → dashboard Streamlit con reportería PDF.

---

## PARTE 2: ARQUITECTURA TÉCNICA DEL SISTEMA

### 2.1 Pipeline Completo (5 Capas)

```
[ESP32 + HX711]  →  [Adafruit IO]  →  [ETL Python]  →  [Random Forest]  →  [Streamlit Dashboard]
  Sensor físico       MQTT/Nube        Limpieza y          Predicción           Visualización
  peso residuos       REST API         lógica negocio      desperdicio          + PDF report
  cada ~6 seg         feed: "peso"     agregación diaria   siguiente ciclo      KPIs + alertas
```

### 2.2 Capa 1 — Hardware (Sensor Físico)

| Componente | Especificación |
|---|---|
| Microcontrolador | ESP32 (WiFi integrado, 240 MHz, dual-core) |
| Amplificador | HX711 (celda de carga 24-bit ADC) |
| Configuraciones | 5 celdas (CodigoTesis.txt) y 2 celdas (Codigo-Tesis-2placas.txt) |
| Factor de calibración | 353.f |
| Frecuencia de lectura | ~6 segundos por lectura (~14,400 lecturas/día) |
| Protocolo de comunicación | MQTT → Adafruit IO feed "peso" |

**Justificación del ESP32:** Validado por Jayetileke, de Mel & Mukhopadhyay (IEEE, 2024) en arquitectura Industry 5.0 con Arduino Due/ESP32 y Xbee S2C para redes de sensores industriales. WiFi integrado elimina necesidad de módulo adicional. Costo ~USD 5–10 por nodo.

### 2.3 Capa 2 — Transmisión (Adafruit IO)

- **Plataforma:** Adafruit IO (IoT cloud MQTT/REST)
- **Usuario:** Sensorpeso2
- **Feed:** peso
- **Credenciales:** en `.env` (ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
- **Cliente Python:** `Adafruit_IO` con `@st.fragment(run_every=4)` para lectura en vivo cada 4 segundos

### 2.4 Capa 3 — ETL Python (`modelo_prediccion.py`)

#### Función `cargar_y_limpiar_datos()`
- Carga automática de todos los archivos `Datos*.xlsx` del directorio
- Columnas requeridas: `created_at`, `value`
- Limpieza: valores nulos, conversión numérica, valores absolutos (corrige taras negativas)
- **Filtro de ruido crítico:** conserva solo lecturas entre 50 g y 2000 g
  - `< 50 g` → ruido de tara del sensor vacío
  - `> 2000 g` → picos anómalos / saturación
- Zona horaria: UTC → local (tz_localize)

#### Función `integrar_logica_negocio()`
- **Agregación diaria:** `resample('D').agg({'value': 'max'})`
- **Razón crítica del MÁXIMO (no suma):** El sensor mide peso acumulado en báscula (medición de estado). El pico diario = mayor acumulado antes de vaciar = desperdicio real del día. `sum()` multiplicaría por ~14,400 lecturas/día generando valores 14,400× inflados.
- **Invalidación de lags:** se anulan lags contaminados por brechas > 2 días entre registros (evita que el modelo aprenda patrones temporales falsos en series con fines de semana o días sin producción)

### 2.5 Capa 4 — Modelo Predictivo (Random Forest)

#### Hiperparámetros
```python
RandomForestRegressor(
    n_estimators  = configurable (50–300, default 100),
    max_depth     = 5,
    min_samples_leaf = 2,
    random_state  = 42
)
```

#### Features del Modelo
- `dia_semana`, `dia_mes`, `mes` (temporales)
- `peso_lag_1`, `peso_lag_2`, `peso_lag_3` (rezagos en kg)
- `media_movil_3d` (ventana 3 días)
- **Target:** `peso_total_kg`

#### Métricas de Evaluación
| Métrica | Descripción |
|---|---|
| RMSE | Raíz del Error Cuadrático Medio (kg) |
| MAE | Error Absoluto Medio (kg) |
| R² Entrenamiento | Varianza explicada en datos de entrenamiento |
| R² Prueba | Varianza explicada en datos de prueba |
| Gap train-prueba | < 0.10 = sin overfitting |
| MAPE → Seguridad | `(1 - MAPE) × 100` — métrica correcta para series temporales con varianza comprimida |

**Split temporal:** 80% entrenamiento / 20% prueba, `shuffle=False` (obligatorio en series de tiempo).

**Validación con Estado del Arte:** Guldurek (2026, IEEE Access) obtuvo R² = 0.993 con Random Forest en ATLAS Denim Co. (Turquía), la fábrica de denim más metodológicamente cercana al proyecto. Li et al. (2025, Sustainability) validó Random Forest y GA-SVR para predicción de huella de carbono textil en 672 productos reales.

### 2.6 Capa 5 — Dashboard Streamlit (`dashboard_tesis.py`)

#### Estructura de Navegación
```
📊 Dashboard Principal
📈 Análisis de Datos
🌱 Huella de Carbono
🌲 Bosque Aleatorio
📄 Reporte
```

---

## PARTE 3: CONSTANTES DE NEGOCIO (FADITEX)

Definidas en `modelo_prediccion.py` líneas 90–93. Son el núcleo de todos los cálculos derivados.

```python
TELA_ADQUIRIDA_M       = 9805.66   # metros de tela adquirida por mes
TELA_POR_PANTALON_M    = 1.20      # metros de tela por pantalón (rango 1.10–1.30)
DESPERDICIO_PROM_M     = 45        # metros de tela desperdiciada por mes (rango 40–50)
DENSIDAD_TELA_G_POR_M  = 225       # gramos por metro lineal de tela denim
CO2_POR_PANTALON_KG    = 6.5       # kg CO₂eq por jean (etapa de fabricación, ~20% ciclo de vida)
```

### 3.1 Métricas Derivadas

```python
pantalones_por_mes              = (9805.66 - 45) / 1.20  = 8,134 pantalones/mes
metros_desperdicio_por_pantalon = 45 / 8134              = 0.005534 m/pant
factor_kg_a_pantalones          = 1000 / (225 × 0.005534) = 803.2 pant/kg
```

---

## PARTE 4: CADENA DE CÁLCULO — DEL SENSOR AL CO₂

### 4.1 Fórmula Completa (4 Pasos)

```
PASO 1: Sensor HX711 mide peso de residuos textiles acumulados en la báscula
        → peso_diario_g (valor máximo del día)

PASO 2: Conversión a metros de tela desperdiciada
        metros_desperdicio = peso_g ÷ 225 g/m

PASO 3: Estimación de pantalones que representan ese desperdicio
        pantalones = metros_desperdicio ÷ 0.005534 m/pant
        (donde 0.005534 = 45 m desperdicio/mes ÷ 8,134 pant/mes)

PASO 4: Cálculo de huella de carbono
        CO₂_kg = pantalones × 6.5 kg CO₂eq/jean
```

### 4.2 Columnas Calculadas en el ETL

```python
peso_total_kg          = peso_total_g / 1000
metros_desperdicio     = peso_total_g / 225
pantalones_procesados  = metros_desperdicio / 0.005534
tela_consumida_m       = pantalones_procesados × 1.20
desperdicio_estimado_g = peso_total_g   # dato real del sensor
```

---

## PARTE 5: JUSTIFICACIÓN CIENTÍFICA DEL FACTOR 6.5 kg CO₂eq/jean

### 5.1 Triple Respaldo Académico

| Fuente | Dato | Validación |
|---|---|---|
| Periyasamy & Duraisamy (2018, Springer) | Corte + Acabado + Lavado industrial + Empaque = 6.9 kg CO₂ | ≈ 6.5 kg para etapa controlable por fábrica |
| Zhao et al. (2021, J. Cleaner Production) | Ciclo completo jean = 33.4 kg CO₂eq (virtual carbon denim global) | 6.5 / 33.4 = 19.5% ≈ 20% fase fabricación |
| Wang et al. (2024, SSRN) | Knitwear algodón = 6.58 kg CO₂eq | Validación cruzada por tipo de prenda similar |

### 5.2 Desglose del Ciclo de Vida Completo (Periyasamy & Duraisamy, 2018)

| Fase | kg CO₂ | Controlable por Faditex |
|---|---|---|
| Cultivo de fibra | 4.64 | No |
| Producción de tela | 14.40 | Parcial |
| Corte y confección | 3.20 | **Sí** |
| Acabado | 0.96 | **Sí** |
| Lavado industrial | 2.10 | **Sí** |
| Empaque | 0.64 | **Sí** |
| Transporte y comercio | 6.10 | No |
| Fase consumidor (lavados del hogar) | ~20.00 | No (~80% del total) |
| Fin de vida | 1.44 | No |
| **TOTAL CICLO COMPLETO** | **~53.48** | — |

> **Este sistema monitorea y cuantifica exclusivamente las fases controlables por Faditex (6.5 kg CO₂eq).**

### 5.3 Notas Críticas para el Jurado

1. El **6.5 kg CO₂ NO es el ciclo de vida completo**. Es exclusivamente la etapa de fabricación. El ciclo completo incluye lavados del consumidor (~20 kg) que representan ~80% del total.
2. El **sensor no mide pantalones directamente**. Mide peso de retazos acumulados. La conversión usa proporción histórica de Faditex (45 m/mes sobre 8,134 pant/mes).
3. El modelo usa el **MÁXIMO diario, no la suma**. Porque el sensor es medición de estado (peso actual en báscula), no contador incremental.
4. La **precisión MAPE es la métrica correcta** para series temporales con varianza comprimida. R² puede dar valores negativos aunque el modelo sea útil.
5. Los **lags se invalidan automáticamente** con brechas > 2 días para evitar patrones temporales falsos.

---

## PARTE 6: KPIs DEL SISTEMA

### KPI 1 — Producción del Período

| Indicador | Fórmula | Unidad |
|---|---|---|
| Días Analizados | `len(df_historico)` | días |
| Pantalones Totales Estimados | `Σ(metros / 0.005534)` | unidades |
| Tela Consumida Estimada Total | `Σ(pantalones × 1.20)` | metros |

### KPI 2 — Huella de Carbono (Etapa de Fabricación)

| Indicador | Fórmula | Fuente |
|---|---|---|
| CO₂ Total del Período | `Σpantalones × 6.5` | Periyasamy 2018, Zhao 2021 |
| CO₂ por Jean (fabricación) | 6.5 kg CO₂eq (constante) | ACV / LCA |
| CO₂ Evitado si −10% Desperdicio | `co2_total × 0.10` | Indicador prospectivo |
| Intensidad CO₂ Diaria | `co2_total / días` | Comparación inter-períodos |

### KPI 3 — Eficiencia del Proceso

```
Eficiencia (%) = tela_consumida_m / (tela_consumida_m + metros_desperdicio) × 100
```

Benchmark industrial: 92–95%. Si marca 96% → 4% fue merma.

### KPI 4 — Pantalones No Producidos por Desperdicio

```
Pantalones perdidos = metros_desperdicio_total / 1.20
```

---

## PARTE 7: DASHBOARD — DESCRIPCIÓN DE PÁGINAS

### 7.1 Dashboard Principal (6 KPI cards)

| Métrica | Fórmula |
|---|---|
| Días Analizados | `len(df_historico)` |
| Pantalones Est. | `sum(metros_desperdicio / 0.005534)` |
| Tela Consumida | `sum(pantalones × 1.20)` |
| Eficiencia | `tela_útil / (tela_útil + desperdicio) × 100` |
| CO₂ Período | `total_pantalones × 6.5` |
| Precisión Modelo | `(1 - MAPE) × 100` |

**Gráficos:** Sensor en vivo (cada 4s), desperdicio diario en kg, tela útil vs desperdicio (torta), CO₂ diario.

**Panel de predicción (siguiente ciclo):**
```python
prediccion_futura_kg = modelo_rf.predict(ultimo_dia[features_modelo])
pantalones_futuros   = prediccion_futura_kg[0] × factor_kg_pantalones
tela_futura          = pantalones_futuros × 1.20
co2_prediccion       = pantalones_futuros × 6.5
```

### 7.2 Análisis de Datos (3 pestañas)

1. **Serie de Tiempo:** desperdicio diario en kg (histórico completo)
2. **Distribución del Peso:** histograma con KDE del peso diario
3. **Matriz de Correlación:** heatmap entre peso_kg, pantalones, tela, desperdicio_g

### 7.3 Huella de Carbono (4 KPIs + 4 gráficos)

- CO₂ diario por día de producción
- Tela útil vs desperdicio con valores absolutos en metros
- Producción vs Pérdida (barras verticales)
- Fabricación (6.5 kg) vs Ciclo Completo (32.7 kg)

### 7.4 Bosque Aleatorio (página conceptual)

- Explicación del algoritmo Random Forest
- Gráfico de votos de los primeros 20 árboles individuales vs promedio
- Slider para explorar predicción árbol por árbol (1–10 árboles)

### 7.5 Reporte PDF (ReportLab — 5 secciones)

1. Período medido y cobertura del sensor
2. Producción y eficiencia del proceso
3. Desperdicio generado e impacto en producción
4. Huella de carbono e impacto ambiental
5. Proyección y recomendaciones para próximo ciclo

---

## PARTE 8: ESTADO DEL ARTE — 21 PAPERS ACADÉMICOS

### 8.1 Categorías de la Literatura

El Estado del Arte se organiza en 5 ejes temáticos que validan cada componente del sistema propuesto:

| Eje | Componente Validado | Papers Clave |
|---|---|---|
| Sensores IoT / ESP32 | Capa hardware + transmisión | Jayetileke et al. 2024, Martikkala et al. 2023, Cai et al. 2026 |
| Machine Learning Predictivo | Modelo Random Forest | Guldurek 2026, Li et al. 2025, Dargan et al. 2019 |
| Huella de Carbono del Jean | Factor 6.5 kg CO₂eq | Periyasamy & Duraisamy 2018, Zhao et al. 2021, Wang et al. 2024 |
| ACV / Metodología LCA | Estandarización del cálculo | Karthik & Murugan 2017, Periyasamy et al. 2017, Karagöl et al. 2024 |
| Industria 4.0 / Economía Circular Textil | Pertinencia y contexto industrial | Oliveira Neto et al. 2024, Xu Chen et al. 2026, Niinimäki et al. 2020 |

---

### 8.2 Referencias Completas con Síntesis

---

#### REF-01 · Periyasamy & Duraisamy (2018) — REFERENCIA CENTRAL

**Título:** Carbon Footprint on Denim Manufacturing  
**Autores:** Aravin Prince Periyasamy, Gopalakrishnan Duraisamy  
**Año:** 2018  
**Fuente:** Handbook of Ecomaterials, Springer, pp. 1–18. DOI: 10.1007/978-3-319-48281-1_112-1  
**Institución:** Technical University of Liberec (República Checa) / PSG College of Technology (India)

**Resumen:** Capítulo de handbook especializado en huella de carbono en manufactura denim. Cubre el concepto de GWP, evaluación LCA cradle-to-grave, ciclo de vida del producto (materia prima, manufactura, uso del consumidor, disposición), cálculo de unidad funcional y límites del sistema.

**Datos Numéricos Clave:**
- GWP del algodón en cultivo: 53% CO₂, 45% N₂O, 2% CH₄
- Consumo de agua del algodón: 7–29 toneladas/kg de fibra cruda
- Lavado del garment: **40–50% del GHG del ciclo de vida total**
- Desglose fase fabricación: Corte 3.20 + Acabado 0.96 + Lavado industrial 2.10 + Empaque 0.64 = **6.90 kg CO₂eq**
- El factor 6.5 kg usado en esta tesis representa ≈ 94% de este valor (diferencia por variaciones de proceso)

**Metodología:** LCA conforme a ISO 14040/14044, GWP (Global Warming Potential), unidad funcional = 1 par de jeans, análisis cradle-to-grave.

**Cita APA:** Periyasamy, A. P., & Duraisamy, G. (2018). Carbon footprint on denim manufacturing. En *Handbook of Ecomaterials* (pp. 1–18). Springer.

**Conexión con el Proyecto:** Proporciona el respaldo primario para el factor 6.5 kg CO₂eq/jean usado en todos los cálculos del dashboard. Identifica las fases controlables por Faditex (corte, acabado, lavado industrial, empaque) como las que el sistema monitorea.

---

#### REF-02 · Periyasamy, Wiener & Militky (2017)

**Título:** Life-Cycle Assessment of Denim  
**Autores:** A.P. Periyasamy, J. Wiener, J. Militky  
**Año:** 2017  
**Fuente:** Book chapter en *Sustainability in Denim*, Elsevier, pp. 84–120  

**Resumen:** Análisis completo del ciclo de vida de jeans denim cubriendo desde extracción de materias primas hasta fin de vida. Examina impacto ambiental en cada etapa: cultivo de algodón (agua, pesticidas), hilatura, tejido, teñido, confección y uso por el consumidor. Define las 4 etapas del ACV para denim.

**Datos Numéricos Clave:**
- Algodón usa 25% de insecticidas y 12% de pesticidas globales
- 3% de tierra cultivable mundial dedicada al algodón
- USA: consumidores poseen 7 pares de jeans simultáneamente
- 4 etapas ACV denim: extracción fibra → procesamiento → manufactura → uso/disposición

**Metodología:** LCA conforme a ISO 14040/14044, análisis de impactos ambientales multifase.

**Cita APA:** Periyasamy, A. P., Wiener, J., & Militky, J. (2017). Life-cycle assessment of denim. En *Sustainability in Denim* (pp. 84–120). Elsevier.

**Conexión con el Proyecto:** Define el marco metodológico LCA que respalda la estructura de cálculo del sistema. Las 4 etapas del ACV para denim permiten ubicar el monitoreo de Faditex en la fase de manufactura.

---

#### REF-03 · Karthik & Murugan (2017)

**Título:** Carbon Footprint in Denim Manufacturing  
**Autores:** T. Karthik, R. Murugan  
**Año:** 2017  
**Fuente:** Book chapter en *Sustainability in Denim*, Elsevier, pp. 126–180  
**Institución:** PSG College of Technology, Coimbatore, India

**Resumen:** Capítulo especializado en evaluación de huella de carbono en manufactura de denim. Analiza métodos de cálculo conforme a ISO 14040, ISO 14064 y PAS 2050. Examina emisiones en cultivo de algodón (N₂O, CH₄), hilatura, teñido con índigo, acabado y uso por consumidor.

**Datos Numéricos Clave:**
- 59% del impacto climático ocurre en fase manufactura; 41% en uso + fin de vida
- Emisiones N₂O: 45% del GWP en cultivo de algodón
- Teñido índigo: 1 millón de toneladas de químicos y tintes anuales globalmente
- CO₂ contribuye 80% de emisiones en economías desarrolladas

**Metodología:** Carbon Footprint Protocol (CFP) basado en LCA, análisis bottom-up, cuantificación GEI con conversión a CO₂-eq conforme a ISO 14067 y GHG Protocol.

**Cita APA:** Karthik, T., & Murugan, R. (2017). Carbon footprint in denim manufacturing. En *Sustainability in Denim* (pp. 126–180). Elsevier.

**Conexión con el Proyecto:** Valida los estándares normativos (ISO 14040, ISO 14067, GHG Protocol, PAS 2050) que sustentan la metodología de cálculo del dashboard. El 59% manufactura justifica el enfoque del sistema en la etapa de producción.

---

#### REF-04 · Zhao et al. (2021)

**Título:** Virtual Carbon and Water Flows Embodied in Global Fashion Trade — A Case Study of Denim Products  
**Autores:** Minyi Zhao, Ya Zhou, Jing Meng, Heran Zheng, Yanpeng Cai, Yuli Shan, Dabo Guan, Zhifeng Yang  
**Año:** 2021  
**Fuente:** *Journal of Cleaner Production*, Vol. 303, p. 127080. DOI: 10.1016/j.jclepro.2021.127080  
**Instituciones:** Guangdong University of Technology, University College London, NTNU Noruega, Tsinghua University

**Resumen:** Primer análisis de flujos virtuales de carbono y agua en comercio global de denim (2001–2018) usando LCA + water footprint assessment. Análisis multi-país con datos de comercio bilateral.

**Datos Numéricos Clave:**
- Huella de carbono virtual denim 2001: **14.8 Mt CO₂eq**
- Huella de carbono virtual denim 2018: **16.0 Mt CO₂eq** (aumento global)
- Ciclo completo jean: **33.4 kg CO₂eq** (validación que 6.5 representa ~19.5% del ciclo)
- Denim polyester-blended: +5% carbono, -72% agua vs algodón puro
- Relocalización: USA/EU/Japan → China/India/Pakistan

**Metodología:** MRIO (Multi-Region Input-Output), LCA + Water Footprint Assessment, análisis temporal 2001–2018.

**Cita APA:** Zhao, M., Zhou, Y., Meng, J., Zheng, H., Cai, Y., Shan, Y., Guan, D., & Yang, Z. (2021). Virtual carbon and water flows embodied in global fashion trade: A case study of denim products. *Journal of Cleaner Production*, 303, 127080.

**Conexión con el Proyecto:** Proporciona el valor de referencia del ciclo completo (33.4 kg CO₂eq) que permite calcular que 6.5 kg = 19.5% ≈ 20% del total, acotando correctamente el alcance del sistema a la fase de fabricación controlable.

---

#### REF-05 · Wang et al. (2024)

**Título:** Tracing the Carbon Footprint of Cotton Garments Based on Their Life Cycle — Evidence from an Empirical Study of Multiple Sites in China  
**Autores:** Shuchen Wang et al. (Zhengzhou University, Chinese Academy of Agricultural Sciences)  
**Año:** 2024  
**Fuente:** Preprint SSRN: https://ssrn.com/abstract=4821904

**Resumen:** Estudio empírico cross-provincial en China de 5 tipos de ropa de algodón. LCA multi-sitio que valida variaciones significativas por tipo de prenda y factores productivos.

**Datos Numéricos Clave:**
- Knitwear (punto de algodón): **6.58 kg CO₂eq** ← validación cruzada del factor 6.5
- T-shirts: 8.88 kg CO₂eq
- Workwear: 18.68 kg CO₂eq
- Factores clave: electricidad 38.15%, película agrícola 27.57%, fertilizante 17.77%
- Escenarios reducción: energía limpia −57.58%, optimización fábrica −25 a −30%

**Metodología:** LCA multi-sitio empírico, análisis de escenarios, cuantificación de factores de emisión.

**Cita APA:** Wang, S., Chong, C., Huang, W., Guo, S., Wang, Y., Zhang, Y., Pan, Z., Wang, J., Li, X., Zhao, W., Zhang, Z., & Wang, Z. (2024). Tracing the carbon footprint of cotton garments based on their life cycle: Evidence from an empirical study of multiple sites in China. Preprint SSRN 4821904.

**Conexión con el Proyecto:** Tercer validador del factor 6.5 kg CO₂eq (knitwear = 6.58 ≈ 6.5). Demuestra que la electricidad (38.15%) es el principal factor operacional — el sistema IoT monitorea exactamente este componente.

---

#### REF-06 · Guldurek (2026) — REFERENCIA METODOLÓGICAMENTE MÁS CERCANA

**Título:** A Dual Approach to Profitability and Sustainability: AI-Powered Pricing and Emissions Control in Textiles  
**Autores:** Manolya Guldurek  
**Año:** 2026 (aceptado 2024)  
**Fuente:** *IEEE Access*. DOI: 10.1109/ACCESS.2024  
**Institución:** Adana Alparslan Türke Science and Technology University, Turquía  
**Caso de estudio:** ATLAS Denim Co., Adana, Turquía

**Resumen:** Digital twin framework para manufactura textil integrada (ATLAS Denim). Combina forecasting de energía solar PV con ML (RF, XGBoost, LSTM), carbon footprint accounting y dynamic pricing basado en intensidad de emisiones. Datos enero–mayo 2025.

**Datos Numéricos Clave:**
- **Random Forest R² = 0.993** (mejor modelo para predicción de energía/emisiones)
- Generación PV estimada: 55.18 MWh
- Carbon saving: 23.9 tCO₂ vs grid-only
- Modelos comparados: RF, XGBoost, LSTM
- Período: 5 meses (enero–mayo 2025)

**Metodología:** Machine Learning (RF, XGBoost, LSTM), digital twin architecture, predicción de series temporales, carbon accounting, dynamic pricing.

**Cita APA:** Guldurek, M. (2026). A dual approach to profitability and sustainability: AI-powered pricing and emissions control in textiles. *IEEE Access*.

**Conexión con el Proyecto:** **Caso validador más cercano metodológicamente.** Demuestra que Random Forest es el mejor modelo para predicción en fábrica de denim real (ATLAS Denim = misma industria que Faditex). R² = 0.993 es referencia de rendimiento objetivo.

---

#### REF-07 · Li et al. (2025)

**Título:** Influencing Factors and Prediction Model for the Carbon Footprint of Textile Finishing Production: Case Study of 672 Textile Products  
**Autores:** Xin Li, Ke Zhang, Zhiyuan Gao, Jingxuan Xu  
**Año:** 2025  
**Fuente:** *Sustainability*, Vol. 17, No. 10350. DOI: 10.3390/su17210350  
**Institución:** Zhejiang Sci-Tech University, China

**Resumen:** Estudio pionero con dataset de 672 productos textiles reales para predecir huella de carbono en fase de acabado. Desarrolló modelos ML: PCR, PLSR, GA-ELM, PSO-ELM, GA-SVR, PSO-SVR. Permite predicción en fase de diseño (ex-ante), no solo post-producción (ex-post).

**Datos Numéricos Clave:**
- Dataset: **672 productos textiles reales**
- Consumo de vapor: **97.24% de la huella de carbono de acabado**
- Consumo de electricidad: 2.76%
- GA-SVR: R² > 0.95 (mejor modelo)
- Factores principales: job allowance ratio y velocidad de máquina

**Metodología:** Ensemble ML (GA-SVR, PSO-SVR, LSTM), análisis de correlación Pearson/Spearman, feature engineering, cross-validation.

**Cita APA:** Li, X., Zhang, K., Gao, Z., & Xu, J. (2025). Influencing factors and prediction model for the carbon footprint of textile finishing production: Case study of 672 textile products. *Sustainability*, 17(10), 10350.

**Conexión con el Proyecto:** Valida que ML puede predecir huella de carbono textil con alta precisión (R² > 0.95). El sistema propuesto aplica la misma lógica: datos del sensor → modelo → predicción CO₂. El uso de Random Forest en Faditex sigue el mismo principio con la ventaja de mayor interpretabilidad.

---

#### REF-08 · Dargan et al. (2019)

**Título:** A Survey of Deep Learning and Its Applications: A New Paradigm to Machine Learning  
**Autores:** Shaveta Dargan, Munish Kumar, Maruthi Rohit Ayyagari, Gulshan Kumar  
**Año:** 2019  
**Fuente:** *Archives of Computational Methods in Engineering*, Vol. 26. DOI: 10.1007/s11831-019-09344-w

**Resumen:** Survey exhaustivo sobre deep learning y sus aplicaciones. Cubre arquitecturas fundamentales: CNN, LSTM, RNN, Auto-encoders, RBM, DSN. Analiza aplicaciones en visión por computadora, NLP y análisis de series temporales.

**Datos Numéricos Clave:**
- LSTM y CNN son las arquitecturas más usadas desde 2010–2017
- Gated Recurrent Units (GRU) para series temporales
- Backpropagation como estándar de entrenamiento

**Cita APA:** Dargan, S., Kumar, M., Ayyagari, M. R., & Kumar, G. (2019). A survey of deep learning and its applications: A new paradigm to machine learning. *Archives of Computational Methods in Engineering*, 26(5), 1–25.

**Conexión con el Proyecto:** Proporciona el marco teórico para la justificación del uso de ML en el sistema. Random Forest es preferido sobre redes neuronales por su interpretabilidad con datasets pequeños (~22 días de entrenamiento), su robustez sin necesidad de grandes volúmenes de datos, y la facilidad de visualización de importancia de features.

---

#### REF-09 · Jayetileke, de Mel & Mukhopadhyay (2024)

**Título:** A Reconfigurable SensorNet for Industry 5.0 Applications using Arduino Due/ESP32 and Xbee S2C Based on IEEE 802.15.4 Protocol with Programmable Sensor Array  
**Autores:** H.R. Jayetileke, W.R. de Mel, S.C. Mukhopadhyay  
**Año:** 2024  
**Fuente:** IEEE Conference Paper  
**Instituciones:** University of Sri Jayewardenepura; Macquarie University, Australia

**Resumen:** Arquitectura inalámbrica basada en Xbee S2C (IEEE 802.15.4) con Arduino Due/ESP32 para Industry 5.0. Sistema configurable con múltiples sensores, resolución variable y sincronización. Implementa API mode para transmisión fiable en ambientes industriales con ruido electromagnético.

**Datos Numéricos Clave:**
- Monitoreo de referencia: hasta **20 Hz**
- Rango Xbee 2.4–2.5 GHz: 60 m interior, **1,200 m exterior** line-of-sight
- 4 canales analógicos/digitales simultáneos
- Data Rate de interfaz: 230,400 bps
- PAN ID 16-bit

**Metodología:** Wireless sensor network design, IEEE 802.15.4, embedded systems (Arduino IDE), validación experimental.

**Cita APA:** Jayetileke, H. R., de Mel, W. R., & Mukhopadhyay, S. C. (2024). A reconfigurable sensornet for Industry 5.0 applications using Arduino Due/ESP32 and Xbee S2C based on IEEE 802.15.4 protocol with programmable sensor array. *IEEE Conference Proceedings*.

**Conexión con el Proyecto:** Valida el uso de ESP32 en arquitecturas de sensores industriales para Industry 5.0. La misma plataforma (ESP32) usada en Faditex fue evaluada en contexto académico con protocolos IEEE estándar.

---

#### REF-10 · Xu Chen et al. (2026)

**Título:** A Literature Review of Textile Industry Carbon Emissions Research: Research Hotspots, Themes and Emerging Trends  
**Autores:** Xu Chen, Xufeng Wu, Peihua Han, Di Wu  
**Año:** 2026  
**Fuente:** *Industria Textila*, Vol. 77, No. 2, pp. 338–354. DOI: 10.35530/IT.077.02.202596

**Resumen:** Análisis bibliométrico de 349 publicaciones (2005–2025, Web of Science) sobre emisiones de carbono en textiles usando CiteSpace. Identifica crecimiento exponencial post-2012 y tendencias emergentes.

**Datos Numéricos Clave:**
- **349 artículos** analizados (2005–2025)
- Crecimiento exponencial desde **2012**
- Hotspots actuales: monitoreo IA + huella de carbono + cadena verde
- Protocolo de Kioto (1997) y Acuerdo de París (2015) como catalizadores de investigación

**Cita APA:** Chen, X., Wu, X., Han, P., & Wu, D. (2026). A literature review of textile industry carbon emissions research: Research hotspots, themes and emerging trends. *Industria Textila*, 77(2), 338–354.

**Conexión con el Proyecto:** Valida la pertinencia y actualidad del tema de tesis. Los hotspots identificados (monitoreo IA + huella de carbono + cadena verde) son exactamente los 3 ejes del sistema propuesto.

---

#### REF-11 · de Oliveira Neto et al. (2024)

**Título:** Industry 4.0 Technologies Moderately Spurred Microlevel Circular Economy Considering Cleaner Production, Not Promoting Sustainable Performance  
**Autores:** G.C. de Oliveira Neto, D. da Silva, V.D. Arns, H.N.P. Tucci, L.F.R. Pinto, M.N. Seri  
**Año:** 2024  
**Fuente:** *International Journal of Environmental Science and Technology*. DOI: 10.1007/s13762-024-06010-y  
**Institución:** Federal University of ABC, Brasil

**Resumen:** Estudio estructural en grandes fábricas textiles brasileñas sobre adopción de I4.0 + economía circular + producción limpia (CECP) usando SEM. Identifica qué tecnologías I4.0 realmente funcionan para economía circular.

**Datos Numéricos Clave:**
- Industria textil Brasil: 100M toneladas de residuos en 2 décadas
- Banco Mundial: **20% de polución acuática** atribuida a textiles
- Consumo textil global: 7 → 13 kg per cápita/año
- Tecnologías I4.0 efectivas: **cyber-physical systems, robots, AR, big data, IoT, simulation, AI**
- Tecnologías inefectivas: cloud computing, cybersecurity aislado, additive manufacturing

**Metodología:** SEM (Structural Equation Modeling), revisión sistemática de 18 papers, survey, Pearson correlation, marco ReSOLVE.

**Cita APA:** Oliveira Neto, G. C., da Silva, D., Arns, V. D., Tucci, H. N. P., Pinto, L. F. R., & Seri, M. N. (2024). Industry 4.0 technologies moderately spurred microlevel circular economy considering cleaner production, not promoting sustainable performance. *International Journal of Environmental Science and Technology*.

**Conexión con el Proyecto:** Valida que **IoT + Big Data + AI son exactamente las tecnologías I4.0 efectivas** para economía circular en textiles. El sistema propuesto combina precisamente estas tres tecnologías.

---

#### REF-12 · Niinimäki et al. (2020)

**Título:** The Environmental Price of Fast Fashion  
**Autores:** Kirsi Niinimäki, Greg Peters, Helena Dahlbo, Patsy Perry, Timo Rissanen, Alison Gwilt  
**Año:** 2020  
**Fuente:** *Nature Reviews Earth & Environment*, Vol. 1, pp. 189–200. DOI: 10.1038/s43017-020-0039-9

**Resumen:** Review de Nature sobre impactos ambientales del fast fashion. Segundo mayor contaminador industrial. Examina agua, químicos, CO₂ y residuos a nivel global.

**Datos Numéricos Clave:**
- **10% de la polución global** (industria moda)
- **1.7 Gt CO₂-eq/año** emisiones totales moda
- 1.5 trillion litros agua/año
- **92 millones de toneladas** de residuo textil/año
- 35% del microplástico oceánico primario (190,000 t/año)
- Consumo fibra per cápita: 5.9 kg (1975) → 13 kg (2018)
- Proyección 2030: 102 Mt fibra (vs 62 Mt actual)

**Cita APA:** Niinimäki, K., Peters, G., Dahlbo, H., Perry, P., Rissanen, T., & Gwilt, A. (2020). The environmental price of fast fashion. *Nature Reviews Earth & Environment*, 1(4), 189–200.

**Conexión con el Proyecto:** Justifica la urgencia e impacto del sistema propuesto. Los 92 millones de toneladas de residuo textil anual contextualizan la importancia de monitorear incluso los residuos de una fábrica mediana como Faditex.

---

#### REF-13 · Peters, Li & Lenzen (2021)

**Título:** The Need to Decelerate Fast Fashion in a Hot Climate — A Global Sustainability Perspective on the Garment Industry  
**Autores:** Greg Peters, Mengyu Li, Manfred Lenzen  
**Año:** 2021  
**Fuente:** *Journal of Cleaner Production*, Vol. 295, p. 126390. DOI: 10.1016/j.jclepro.2021.126390

**Resumen:** Primer análisis MRIO (Eora model) de impactos globales del fast fashion cubriendo energía, agua, clima y empleo. Período 2000–2015.

**Datos Numéricos Clave:**
- Huella climática 2000–2015: 1.0 → **1.3 Gt CO₂-eq**
- **75% de la energía** del ciclo de vida ocurre pre-retail (manufactura)
- Producción fibra 2000–2018: duplicación (7.6 → 13.8 kg/cápita/año)
- Agua: 88% de la escasez hídrica ocurre en producción de fibra

**Cita APA:** Peters, G., Li, M., & Lenzen, M. (2021). The need to decelerate fast fashion in a hot climate. *Journal of Cleaner Production*, 295, 126390.

**Conexión con el Proyecto:** Demuestra que la fase de manufactura concentra 75% de los impactos ambientales — exactamente donde el sistema de Faditex aplica el monitoreo IoT, enfocando el esfuerzo donde tiene mayor impacto potencial.

---

#### REF-14 · Cai, Jusoh & Yue (2026)

**Título:** Digitalization and Sustainable Industrial Low-Carbon Transformation: Synergistic Effects, Policy Tools, Technical Pathways, and Financial Innovation  
**Autores:** Wei Cai, Sufian Jusoh, Xiaoguang Yue  
**Año:** 2026  
**Fuente:** *Sustainability*, Vol. 18, No. 1433. DOI: 10.3390/su18031433  
**Institución:** Wuhan University of Technology

**Resumen:** Framework teórico de 4 dimensiones (política + tecnología + finanzas + digitalización) para transformación industrial baja en carbono en el Delta del Río Yangtsé.

**Datos Numéricos Clave:**
- Reducción de costos de descarbonización: **18–23%** con política + finanzas coordinadas
- **IoT-based monitoring en textiles: 9.7% reducción de consumo energético**
- Digital twin en acero: 12% reducción de emisiones
- Zhejiang "Carbon Efficiency Code": >15% reducción intensidad carbono en 50% de empresas

**Cita APA:** Cai, W., Jusoh, S., & Yue, X. (2026). Digitalization and sustainable industrial low-carbon transformation. *Sustainability*, 18(3), 1433.

**Conexión con el Proyecto:** Cuantifica el beneficio concreto de IoT en textiles: **9.7% reducción energética**. Este dato puede usarse como referencia de impacto esperado del sistema propuesto si se escala en Faditex.

---

#### REF-15 · Martikkala et al. (2023)

**Título:** Smart Textile Waste Collection System — Dynamic Route Optimization with IoT  
**Autores:** Antti Martikkala, Bening Mayanti, Petri Helo, Andrei Lobov, Iñigo Flores Ituarte  
**Año:** 2023  
**Fuente:** *Journal of Environmental Management*, Vol. 335, p. 117548. DOI: 10.1016/j.jenvman.2023.117548  
**Instituciones:** Tampere University (Finlandia), Norwegian University of Science and Technology

**Resumen:** Sistema de smart bins con sensores de bajo costo (basado en Arduino, LoRa, sensor láser de distancia) para recolección de residuos textiles con optimización de ruta dinámica. Validado 12 meses en condiciones outdoor en Finlandia.

**Datos Numéricos Clave:**
- Costo módulo sensor: **€28.81** (Heltec CubeCell €10, sensor TOF láser €11)
- Solo 25% del textil global se recicla actualmente
- Reducción convencional vs dinámica: costo **−7.4%**, tiempo **−7.3%**, CO₂ **−10.2%**
- Rango LoRa: 1,200 m exterior
- Consumo en hibernación (Heltec CubeCell): ~12 μW

**Cita APA:** Martikkala, A., Mayanti, B., Helo, P., Lobov, A., & Flores Ituarte, I. (2023). Smart textile waste collection system – Dynamic route optimization with IoT. *Journal of Environmental Management*, 335, 117548.

**Conexión con el Proyecto:** Demuestra viabilidad económica de IoT para residuos textiles con costo de sensor ~€28. El sistema de Faditex usa ESP32 + HX711 (similar costo) con resultados de reducción CO₂ documentados.

---

#### REF-16 · Sen et al. (2023)

**Título:** Virtual Sensors for Erroneous Data Repair in Manufacturing — A Machine Learning Pipeline  
**Autores:** Sagar Sen, Erik Johannes Husom, Arda Goknil, et al.  
**Año:** 2023  
**Fuente:** *Computers in Industry*, Vol. 149, p. 103917. DOI: 10.1016/j.compind.2023.103917

**Resumen:** Pipeline ML (ErDRe) para reparación automática de datos sensoriales defectuosos. 7 etapas: data profiling, cleaning, feature engineering, sequencing, normalization, ML training, deployment. Validado en 4 casos industriales.

**Datos Numéricos Clave:**
- Desviación error operacional: **< 5%**
- Desviación error huella carbono: **< 3.23%**
- 12 features engineered: mean, sum, max, min, range, gradient, slope, sine/cosine slope, std, variance, peak frequency
- Validado en 4 case studies industriales

**Cita APA:** Sen, S., Husom, E. J., Goknil, A., Politaki, D., Tverdal, S., Nguyen, P., & Jourdan, N. (2023). Virtual sensors for erroneous data repair in manufacturing: A machine learning pipeline. *Computers in Industry*, 149, 103917.

**Conexión con el Proyecto:** Valida el pipeline ETL de la tesis: limpieza, feature engineering, filtrado de ruido (50–2,000 g) y variables lag son exactamente las etapas documentadas en el paper. El filtro de ruido del sistema tiene respaldo metodológico.

---

#### REF-17 · Yu et al. (2022)

**Título:** Energy Digital Twin Technology for Industrial Energy Management: Classification, Challenges and Future  
**Autores:** Wei Yu, Panos Patros, Brent Young, Elsa Klinac, Timothy Gordon Walmsley  
**Año:** 2022  
**Fuente:** *Renewable and Sustainable Energy Reviews*, Vol. 161, p. 112407. DOI: 10.1016/j.rser.2022.112407

**Resumen:** Review sistemática de digital twin para gestión energética industrial. Propone clasificación 3D y cubre aplicaciones de ciclo de vida de planta.

**Datos Numéricos Clave:**
- Sector industrial: **35.2% del CO₂-eq global** (17.4 Gt CO₂-e)
- Solo 25% de sitios industriales aplican mejores prácticas de gestión energética
- Schneider Electric: **−25% energía, −25% CO₂** post-DT
- Caso textil DT: **>12% ahorro energético**

**Cita APA:** Yu, W., Patros, P., Young, B., Klinac, E., & Walmsley, T. G. (2022). Energy digital twin technology for industrial energy management. *Renewable and Sustainable Energy Reviews*, 161, 112407.

**Conexión con el Proyecto:** Posiciona el sistema de Faditex como un prototipo de digital twin textil: el sensor alimenta en tiempo real un modelo que replica el estado ambiental de la fábrica (gemelo digital).

---

#### REF-18 · Winter et al. (2023)

**Título:** Live Estimating the Carbon Footprint of Additively Manufactured Components — A Case Study  
**Autores:** Sven Winter, Niklas Quernheim, Lars Arnemann, Reiner Anderl, Benjamin Schleich  
**Año:** 2023  
**Fuente:** *Procedia CIRP*, Vol. 116, pp. 642–647. DOI: 10.1016/j.procir.2023.02.108

**Resumen:** Framework para estimación live (tiempo real) de carbon footprint en manufactura. Integra sensores de máquina + backend + dashboard interactivo.

**Datos Numéricos Clave:**
- > 2,000 puntos de datos capturados real-time en ETA factory (TU Darmstadt)
- Variación PCF según suposiciones LCIA: significativa
- Monitoreo en tiempo real vs evaluación ex-post: ventajas de predicción en fase de diseño

**Cita APA:** Winter, S., Quernheim, N., Arnemann, L., Anderl, R., & Schleich, B. (2023). Live estimating the carbon footprint of additively manufactured components – a case study. *Procedia CIRP*, 116, 642–647.

**Conexión con el Proyecto:** El dashboard de Faditex implementa exactamente este concepto: estimación live de CO₂ con actualización cada 4 segundos desde el sensor, visualización en dashboard y generación de reporte PDF.

---

#### REF-19 · Lang et al. (2024)

**Título:** A Simplified Machine Learning Product Carbon Footprint Evaluation Tool  
**Autores:** Silvio Lang, Bastian Engelmann, Andreas Schiffler, Jan Schmitt  
**Año:** 2024  
**Fuente:** *Cleaner Environmental Systems*, Vol. 13, p. 100187. DOI: 10.1016/j.cesys.2024.100187

**Resumen:** Herramienta MINDFUL: web app ML para estimación simplificada de PCF. Modelo de 4 factores: materiales, procesos, logística upstream, logística downstream. Backend Python + scikit-learn, Flask, orientada a PYMEs.

**Datos Numéricos Clave:**
- 4-factor PCF model: materiales + procesos + logística in + logística out
- Factor emisión acero: 1.569 kg CO₂/kg; green steel variable
- Backend: Python + scikit-learn, Flask + HTML5

**Cita APA:** Lang, S., Engelmann, B., Schiffler, A., & Schmitt, J. (2024). A simplified machine learning product carbon footprint evaluation tool. *Cleaner Environmental Systems*, 13, 100187.

**Conexión con el Proyecto:** Valida la arquitectura técnica del dashboard de Faditex: Python + scikit-learn (sklearn RandomForest) + interfaz web (Streamlit), orientado a PYME textil, exactamente el stack tecnológico del sistema propuesto.

---

#### REF-20 · Karagöl et al. (2024)

**Título:** Sustainability Approach of Recycled Denim Fabrics with a Life Cycle Assessment  
**Autores:** Hakan Karagöl, Füsun Doba Kadem, Halil İbrahim Olucak, Mehmet Kertmen, Şehpal Özdemir  
**Año:** 2024  
**Fuente:** *Fibres & Textiles in Eastern Europe*, Vol. 32, No. 2, pp. 57–63. DOI: 10.2478/ftee-2024-0019  
**Institución:** SKUR TEKSTIL A.Ş. / Cukurova University, Turquía

**Resumen:** LCA de denim reciclado vs virgen usando SimaPro. Evalúa propiedades mecánicas y ambientales de mezclas reciclado/virgen.

**Datos Numéricos Clave:**
- Jeans denim: fabric más común a nivel mundial
- Composiciones evaluadas: 10–80% reciclado cotton vs 90–20% virgen
- LCA mejora en: depleción recursos fósiles, calentamiento global, toxicidad, uso de agua
- Software: SimaPro (estándar industrial LCA)

**Cita APA:** Karagöl, H., Doba Kadem, F., Olucak, H. İ., Kertmen, M., & Özdemir, Ş. (2024). Sustainability approach of recycled denim fabrics with a life cycle assessment. *Fibres and Textiles in Eastern Europe*, 32(2), 57–63.

**Conexión con el Proyecto:** Demuestra que el LCA en la industria denim es viable computacionalmente (SimaPro) y que los residuos de tela (retazos de corte que mide el sistema de Faditex) tienen un impacto ambiental cuantificable en el LCA completo.

---

#### REF-21 · Chen, Attari, Buck & Jiang (2024)

**Título:** IoTCO2: End-to-End Carbon Footprint Assessment of Internet-of-Things-Enabled Deep Learning  
**Autores:** Fan Chen, Shahzeen Attari, Gayle Buck, Lei Jiang  
**Año:** 2024  
**Fuente:** arXiv preprint 2403.10984v2. DOI: 10.48550/arXiv.2403.10984  
**Institución:** Indiana University Bloomington, USA

**Resumen:** Herramienta IoTCO2 para estimación precisa de carbon footprint end-to-end de modelos DL en dispositivos IoT. Cubre carbon operacional (inferencia) + carbon embebido (manufactura del hardware).

**Datos Numéricos Clave:**
- IoT devices: crecimiento **~40% anual**
- Proyección 2028: IoT carbon > carbon de datacenters globales
- Hardware no computacional: 30–60% del carbon embebido de dispositivos IoT
- Desviación error operacional: < 5%; embebido: < 3.23%

**Cita APA:** Chen, F., Attari, S., Buck, G., & Jiang, L. (2024). IoTCO2: End-to-end carbon footprint assessment of Internet-of-Things-enabled deep learning. arXiv preprint arXiv:2403.10984.

**Conexión con el Proyecto:** Provee perspectiva crítica: el propio sistema IoT tiene una huella de carbono. El ESP32 + HX711 tiene embodied carbon (~30–60% del total del dispositivo). Esto es una limitación del estudio que puede mencionarse en el capítulo de conclusiones y trabajo futuro.

---

## PARTE 9: MAPA DE VALIDACIÓN ACADÉMICA — CADA COMPONENTE Y SU RESPALDO

### 9.1 ¿Por qué ESP32 + HX711?

| Validación | Paper |
|---|---|
| ESP32 en Industry 5.0 | Jayetileke et al. 2024 (IEEE) |
| Sensores IoT low-cost en textiles | Martikkala et al. 2023 (< €30/nodo) |
| IoT reduce consumo energético 9.7% en textiles | Cai et al. 2026 (Sustainability) |

### 9.2 ¿Por qué Random Forest?

| Validación | Paper |
|---|---|
| RF R² = 0.993 en ATLAS Denim (misma industria) | Guldurek 2026 (IEEE Access) |
| ML para predicción CO₂ en 672 textiles (R² > 0.95) | Li et al. 2025 (Sustainability) |
| Survey de ML para series temporales | Dargan et al. 2019 (Archives Comp. Methods Eng.) |

### 9.3 ¿Por qué 6.5 kg CO₂eq/jean?

| Validación | Paper | Dato |
|---|---|---|
| Respaldo primario | Periyasamy & Duraisamy 2018 (Springer) | 6.9 kg fabricación → 6.5 Faditex |
| Ciclo completo referencia | Zhao et al. 2021 (J. Cleaner Production) | 33.4 kg total → 6.5 = 19.5% |
| Validación cruzada | Wang et al. 2024 (SSRN) | 6.58 kg knitwear ≈ 6.5 |

### 9.4 ¿Por qué MÁXIMO diario y no suma?

Validado internamente por Sen et al. (2023): el pipeline ETL debe usar la agregación apropiada para el tipo de sensor. El HX711 mide peso acumulativo (estado), no incremental, lo que equivale a un sensor de "nivel" donde el máximo diario representa el pico antes de vaciar.

### 9.5 ¿Por qué Streamlit + ReportLab?

| Elemento | Validación |
|---|---|
| Dashboard web en tiempo real | Winter et al. 2023 (live estimation + dashboard) |
| Python + scikit-learn para PYME | Lang et al. 2024 (MINDFUL tool) |
| PDF de reporte | Estándar de MRV (Monitoring, Reporting, Verification) en Yu et al. 2022 |

---

## PARTE 10: PREGUNTAS FRECUENTES DEL JURADO (Q&A)

**Q: ¿Por qué usa 6.5 kg CO₂ y no el ciclo de vida completo?**  
A: El sistema monitorea exclusivamente las fases controlables por Faditex (corte, confección, acabado, lavado industrial, empaque). El ciclo completo (32–33.4 kg) incluye lavados del consumidor (~20 kg = 80% del total) que están fuera del control de la fábrica. Tres papers independientes validan este valor: Periyasamy & Duraisamy (2018, 6.9 kg), Wang et al. (2024, 6.58 kg knitwear) y Zhao et al. (2021, 33.4 kg total donde 6.5 = 19.5%).

**Q: ¿Por qué Random Forest y no una red neuronal?**  
A: Con ~22 días de datos de entrenamiento, las redes neuronales requieren más datos para generalizar correctamente. RF con max_depth=5 y min_samples_leaf=2 previene overfitting. Guldurek (2026) obtuvo R²=0.993 con RF en ATLAS Denim (fábrica de denim idéntica), superando a XGBoost y LSTM en ese contexto.

**Q: ¿Por qué MAPE y no R²?**  
A: En series temporales con varianza comprimida en el conjunto de prueba, R² puede dar valores negativos aunque el modelo sea útil. MAPE mide el error porcentual relativo, que es más interpretable para el negocio ("el modelo se equivoca X% en promedio") y más robusto con distribuciones de varianza reducida.

**Q: ¿Por qué el máximo diario y no la suma?**  
A: El HX711 mide el peso acumulado en la báscula en cualquier momento del día (medición de estado, como un medidor de nivel). Si se tomara la suma de 14,400 lecturas diarias, el valor resultante estaría 14,400 veces inflado respecto al desperdicio real. El máximo diario representa el mayor acumulado antes de que la báscula sea vaciada, que es el desperdicio real generado en ese día.

**Q: ¿Cómo garantiza la representatividad del sistema con solo ESP32 + HX711?**  
A: El sistema es pasivo y continuo: toma ~14,400 lecturas/día con filtrado automático de ruido (50–2,000 g). La agregación al máximo diario captura el desperdicio real independientemente de fluctuaciones. El mismo principio es validado por Jayetileke et al. (2024) para Industry 5.0 con ESP32 en ambientes industriales.

**Q: ¿Qué limitaciones tiene el sistema?**  
A: (1) El sistema mide solo el peso de residuos en báscula, no el desperdicio que cae fuera. (2) El factor 6.5 kg CO₂eq asume composición de tela denim estándar. (3) El modelo predictivo tiene ~22 días de datos de entrenamiento, suficiente para patrones semanales pero no estacionales. (4) El propio dispositivo IoT tiene una huella de carbono embebida (Chen et al., 2024) no contabilizada en el sistema.

---

## PARTE 11: PALETA VISUAL Y ARCHIVOS DEL PROYECTO

### 11.1 Paleta de Colores del Dashboard

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

### 11.2 Archivos del Proyecto

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

## PARTE 12: ESTRUCTURA DE CAPÍTULOS SUGERIDA PARA LA TESIS

### Capítulo 1 — Introducción
- Contexto: industria textil global + denim + Ecuador
- Problema: falta de monitoreo automatizado de residuos y CO₂ en Faditex
- Justificación: impactos cuantificados (Niinimäki 2020: 1.7 Gt CO₂/año, 92 Mt residuos)
- Objetivos (general y específicos)
- Alcance y limitaciones

### Capítulo 2 — Marco Teórico y Estado del Arte
- 2.1 Huella de carbono en manufactura textil (Karthik 2017, Periyasamy 2017)
- 2.2 LCA en industria denim (ISO 14040/14044, Periyasamy & Duraisamy 2018)
- 2.3 Factor de emisión 6.5 kg CO₂eq (triple validación)
- 2.4 Sistemas IoT en manufactura textil (Jayetileke 2024, Martikkala 2023, Cai 2026)
- 2.5 Machine Learning para predicción de huella de carbono (Guldurek 2026, Li 2025, Dargan 2019)
- 2.6 Industria 4.0 y economía circular textil (Oliveira Neto 2024, Xu Chen 2026)
- 2.7 Análisis bibliométrico y tendencias (Xu Chen 2026: 349 papers, 2005–2025)

### Capítulo 3 — Metodología
- 3.1 Diseño de investigación
- 3.2 Hardware: ESP32 + HX711 (configuración, calibración, frecuencia)
- 3.3 Protocolo de comunicación: MQTT → Adafruit IO
- 3.4 Pipeline ETL: carga, limpieza, filtrado, agregación
- 3.5 Modelo predictivo: Random Forest (hiperparámetros, features, métricas)
- 3.6 Dashboard: páginas, KPIs, gráficos, reporte PDF

### Capítulo 4 — Implementación
- 4.1 Instalación del sensor en Faditex
- 4.2 Configuración de Adafruit IO y transmisión MQTT
- 4.3 Desarrollo del pipeline ETL (`modelo_prediccion.py`)
- 4.4 Entrenamiento y evaluación del modelo Random Forest
- 4.5 Desarrollo del dashboard Streamlit (`dashboard_tesis.py`)
- 4.6 Generación del reporte PDF con ReportLab

### Capítulo 5 — Resultados
- 5.1 Datos recolectados (período, días, frecuencia)
- 5.2 KPI 1: Producción del período (pantalones, tela, días)
- 5.3 KPI 2: Huella de carbono calculada
- 5.4 KPI 3: Eficiencia del proceso vs benchmark 92–95%
- 5.5 KPI 4: Pantalones no producidos por desperdicio
- 5.6 Rendimiento del modelo Random Forest (RMSE, MAE, R², MAPE)
- 5.7 Predicción del siguiente ciclo

### Capítulo 6 — Discusión
- 6.1 Comparación con Guldurek 2026 (ATLAS Denim, R²=0.993)
- 6.2 Validación del factor 6.5 kg CO₂eq (triple respaldo)
- 6.3 Limitaciones del sistema
- 6.4 Implicaciones para Faditex
- 6.5 Escalabilidad a otras fábricas de denim en Ecuador/Latinoamérica

### Capítulo 7 — Conclusiones y Recomendaciones
- 7.1 Conclusiones por objetivo específico
- 7.2 Aporte del sistema a la medición de huella de carbono en PYME textil
- 7.3 Trabajo futuro: multi-sensor, blockchain MRV, integraciones ERP, LoRa

---

## PARTE 13: CAMBIOS PENDIENTES EN EL SISTEMA

### Cambio 1 — Reestructurar KPI 1
- Mover `"🤖 Precisión Modelo"` de la fila de 6 métricas del Dashboard Principal a la página Bosque Aleatorio
- Renombrar el bloque de 3 métricas restantes a "Producción del Período"

### Cambio 2 — Reubicar gráfico CO₂ diario
- El gráfico `"🌱 CO₂ Diario por Producción (kg)"` (líneas 436–444) debe moverse o duplicarse como visual central de la página Huella de Carbono

### Cambio 3 — Crear KPI de Trazabilidad
- Nuevo elemento visual como primera sección del dashboard
- Muestra el flujo completo: `ESP32 + HX711 → Adafruit IO → ETL → Random Forest → Dashboard`
- Indicador: 100% trazabilidad del dato desde sensor hasta KPI

### Cambio 4 — Diapositiva nueva en PPTX (insertar entre diap. 21 y 22)
- **Título:** ¿Cómo se calcula la Huella de Carbono en este sistema?
- Tabla del ciclo de vida completo del jean con porcentajes
- Cadena de 4 pasos: sensor → metros → pantalones → CO₂
- Fuentes: Periyasamy & Duraisamy (2018), Zhao et al. (2021), Wang et al. (2024)

### Cambio 5 — Correcciones de redacción en diap. 22
- "Un **echo**" → "Un **hecho**"
- "product final" → "producto final"
- "pantalos" → "pantalones"
- "flujo complete" → "flujo completo"

---

## PARTE 14: NORMAS Y ESTÁNDARES CITADOS

| Norma | Título | Aplicación en la Tesis |
|---|---|---|
| ISO 14040:2006 | Environmental management — Life cycle assessment — Principles and framework | Marco metodológico del LCA en cap. 2 |
| ISO 14044:2006 | Environmental management — Life cycle assessment — Requirements and guidelines | Requisitos del LCA |
| ISO 14064:2006 | Greenhouse gases — Specification for quantification of GHG emissions | Cuantificación de emisiones |
| ISO 14067:2018 | Carbon footprint of products — Requirements and guidelines | Huella de carbono de productos textiles |
| PAS 2050:2011 | Specification for the assessment of the life cycle greenhouse gas emissions | Protocolo GHG productos |
| GHG Protocol (WRI) | A Corporate Accounting and Reporting Standard | Estándar corporativo de reporte |

---

## PARTE 15: GLOSARIO TÉCNICO

| Término | Definición |
|---|---|
| ACV / LCA | Análisis de Ciclo de Vida / Life Cycle Assessment — metodología ISO para cuantificar impactos ambientales de un producto en todas sus etapas |
| HX711 | Amplificador y convertidor ADC de 24 bits para celdas de carga. Convierte señal analógica de celda de carga en dato digital |
| ESP32 | Microcontrolador con WiFi y Bluetooth integrado. Procesador dual-core 240 MHz, usado como nodo IoT |
| MQTT | Message Queuing Telemetry Transport — protocolo ligero de mensajería para IoT sobre TCP/IP |
| Adafruit IO | Plataforma IoT en la nube para almacenamiento y visualización de datos de sensores vía MQTT/REST |
| Random Forest | Ensemble de árboles de decisión que promedia predicciones para mayor precisión y menor overfitting |
| MAPE | Mean Absolute Percentage Error — error porcentual absoluto medio. En este sistema: `(1 - MAPE) × 100 = Precisión` |
| GWP | Global Warming Potential — potencial de calentamiento global, medido en kg CO₂eq |
| CO₂eq | Dióxido de carbono equivalente — unidad que normaliza todos los GEI en términos de CO₂ |
| Tara | Peso muerto del recipiente/báscula que se resta del peso medido para obtener el peso neto |
| Lag variable | Variable que representa el valor de la serie temporal en un período anterior (t-1, t-2, t-3) |
| ETL | Extract, Transform, Load — proceso de extracción, transformación y carga de datos |
| Feature engineering | Proceso de crear variables derivadas a partir de datos crudos para mejorar modelos ML |
| Streamlit | Framework Python para crear dashboards web interactivos sin HTML/CSS/JS |
| ReportLab | Librería Python para generación programática de documentos PDF |

---

*Documento generado el 2 de junio de 2026.*  
*Basado en: CONTEXTO_PROYECTO.md + 21 papers académicos del Estado del Arte.*  
*Mantener actualizado con cada cambio al pipeline o a la documentación de tesis.*
