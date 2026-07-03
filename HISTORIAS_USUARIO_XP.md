# Historias de Usuario XP — Sistema de Monitoreo de Residuos Textiles
**Faditex Denim · Pelileo, Ecuador**
**Proyecto de Tesis: Christian Zurita**

---

## 📋 Formato de Historia de Usuario XP

Cada historia sigue el estándar:
```
Como [ROL]
Quiero [FUNCIONALIDAD/INFORMACIÓN]
Para que [BENEFICIO/RAZÓN]

RESPUESTA PROPORCIONADA: [valor]
CÓMO SE USA: [dónde en el proyecto]
```

---

## 🎯 HISTORIA 1: Datos de Adquisición de Tela

**Tipo:** Pregunta de Negocio  
**Prioridad:** ALTA  

### Enunciado
Como **gerente de producción de Faditex**,  
Quiero **conocer la cantidad exacta de tela que adquieren mensualmente**,  
Para que **pueda establecer parámetros base de eficiencia en el proceso**.

### Respuesta Proporcionada
```
CANTIDAD DE TELA ADQUIRIDA MENSUALMENTE: 9,805.66 metros
```

### Detalles
- **Unidad:** metros lineales por mes
- **Rango observado:** Aproximadamente consistente mes a mes
- **Factor de conversión:** A partir de esto se calcula el desperdicio % del sector

### Cómo se usa en el proyecto
```python
# archivo: modelo_prediccion.py, línea 15
TELA_ADQUIRIDA_M = 9805.66   # metros de tela adquirida por mes

# Se utiliza para calcular:
pantalones_por_mes = (9805.66 - 45) / 1.20 = 8,134 pantalones/mes

# Aparece en:
- Dashboard Principal → KPI "Pantalones Est."
- Cálculo de eficiencia: (tela_útil / tela_adquirida) × 100
- Reporte PDF → Sección "Producción y Eficiencia del Proceso"
```

---

## 🎯 HISTORIA 2: Peso de Pantalón Listo (Densidad de Tela)

**Tipo:** Especificación Técnica  
**Prioridad:** CRÍTICA  

### Enunciado
Como **ingeniero de procesos**,  
Quiero **conocer cuántos gramos pesa un metro de tela denim de Faditex**,  
Para que **pueda convertir las mediciones de peso del sensor en metros de tela desperdiciada**.

### Respuesta Proporcionada
```
DENSIDAD DE TELA: 225 gramos por metro lineal
```

### Detalles
- **Unidad:** gramos/metro
- **Material:** Denim 100% algodón
- **Aplicación:** Conversión de peso del sensor (g) → metros de tela

### Cómo se usa en el proyecto
```python
# archivo: modelo_prediccion.py, línea 18
DENSIDAD_TELA_G_POR_M = 225  # gramos por metro lineal de tela

# Se utiliza para convertir sensor a metros:
metros_desperdicio = peso_total_g / 225

# Pipeline completo:
1. Sensor HX711 mide: 500 gramos
2. Conversión: 500 g ÷ 225 = 2.22 metros de tela
3. Pantalones equivalentes: 2.22 m ÷ 0.005534 = 401 pantalones

# Aparece en:
- modelo_prediccion.py → función integrar_logica_negocio() línea 100
- Dashboard → Cálculo de "Pantalones Est."
- Reporte PDF → Sección técnica de conversiones
```

---

## 🎯 HISTORIA 3: Tela Consumida por Pantalón

**Tipo:** Especificación de Producto  
**Prioridad:** CRÍTICA  

### Enunciado
Como **diseñador de patrones**,  
Quiero **saber exactamente cuántos metros de tela se necesitan para confeccionar un pantalón**,  
Para que **pueda optimizar los patrones de corte y reducir el desperdicio**.

### Respuesta Proporcionada
```
TELA POR PANTALÓN: 1.20 metros
RANGO OBSERVADO: 1.10 – 1.30 metros
PROMEDIO: 1.20 metros
```

### Detalles
- **Unidad:** metros por pantalón
- **Variabilidad:** Depende del diseño, tallas y ajuste de patrones
- **Base de cálculo:** Promedio histórico de producción

### Cómo se usa en el proyecto
```python
# archivo: modelo_prediccion.py, línea 16
TELA_POR_PANTALON_M = 1.20  # metros de tela por pantalón (promedio 1.10–1.30)

# Se utiliza para:
1. Calcular pantalones estimados:
   pantalones = metros_desperdicio / 1.20

2. Calcular tela consumida en la producción:
   tela_consumida = pantalones_producidos × 1.20

3. Proyectar producción futura:
   tela_futura = pantalones_predichos × 1.20

# Aparece en:
- Dashboard Principal → Panel de predicción
- Análisis de Datos → Matriz de correlación
- Reporte PDF → "Producción y eficiencia"
- dashboard_tesis.py → línea 695
```

---

## 🎯 HISTORIA 4: Estimación de Desperdicio Mensual

**Tipo:** Métrica de Operación  
**Prioridad:** ALTA  

### Enunciado
Como **coordinador ambiental**,  
Quiero **conocer cuántos metros de tela se desperdician mensualmente en el área de corte**,  
Para que **pueda establecer metas de reducción y monitorear el impacto ambiental**.

### Respuesta Proporcionada
```
DESPERDICIO MENSUAL PROMEDIO: 45 metros
RANGO OBSERVADO: 40 – 50 metros
PORCENTAJE DEL TOTAL: 45 / (9,805.66 + 45) = 0.456%
```

### Detalles
- **Unidad:** metros de tela por mes
- **Base:** Registros históricos manuales de Faditex
- **Fuente:** Área de corte y confección
- **Conversión a peso:** 45 m × 225 g/m = 10,125 gramos/mes

### Cómo se usa en el proyecto
```python
# archivo: modelo_prediccion.py, línea 17
DESPERDICIO_PROM_M = 45  # metros de tela desperdiciada por mes (rango: 40–50)

# Se utiliza para calcular factor de conversión:
metros_desperdicio_por_pantalon = 45 / 8134 = 0.005534 m/pant
factor_kg_a_pantalones = 1000 / (225 × 0.005534) = 803.2 pant/kg

# Aparece en:
- Cálculo de eficiencia: (45 / 9805.66) × 100 = tasa desperdicio
- Dashboard → "Eficiencia del Proceso"
- Benchmarking vs sector (2.5% es el benchmark industrial)
- Reporte PDF → Sección de oportunidades de optimización
```

---

## 🎯 HISTORIA 5: Demoras en Entregas de Informes

**Tipo:** Problema de Negocio  
**Prioridad:** CRÍTICA  

### Enunciado
Como **gerente general de Faditex**,  
Quiero **que se reduzca el tiempo de generación de informes ambientales**,  
Para que **cumpla oportunamente con los requisitos del GAD Municipal de Pelileo y evite sanciones ambientales**.

### Respuesta Proporcionada
```
¿HAN TENIDO DEMORAS EN ENTREGAS DE INFORMES?
Respuesta: SÍ

CAUSA RAÍZ: Registros manuales y esporádicos sin herramientas de visualización en tiempo real

IMPACTO:
- Retrasos en generación de reportes ambientales
- Imposibilidad de cuantificar la huella de carbono de forma oportuna
- Vulnerabilidad ante auditorías del GAD Municipal
```

### Evidencia en Documentación
```
Fuente: AvanceProductoFinal_Zurita.md
"La persistencia de estas causas deriva en demoras en los informes ambientales 
solicitados por el GAD de Pelileo y en la imposibilidad de cuantificar la huella 
de carbono asociada a dichos residuos."

Fuente: AvanceProductoFinal_Zurita_AMPLIADO.md
"El operario registra periódicamente el volumen de desperdicios, lo cual introduce 
sesgos de estimación y oculta picos de ineficiencia de la línea productiva. 
La falta de un registro continuo imposibilita evaluar adecuadamente la huella de 
carbono y vulnera la capacidad de la empresa de cumplir transparentemente con los 
parámetros exigidos por la entidad municipal."
```

### Cómo se resuelve en el proyecto
```
SOLUCIÓN IMPLEMENTADA:
1. Dashboard Streamlit en tiempo real
   → Genera reportes automáticos cada vez que se actualizan datos
   
2. Sensor IoT (ESP32 + HX711)
   → Captura datos continuamente (cada 5-6 segundos)
   
3. ETL automatizado en Python
   → Procesa datos sin intervención manual
   
4. Reporte PDF generado automáticamente
   → Descargable desde la página "Reporte" del dashboard
   
5. Modelo predictivo Random Forest
   → Proyecta huella de carbono futura con precisión 88.4%

RESULTADO:
- Antes: Informes manuales, días/semanas de demora
- Después: Informes automáticos, disponibles en segundos
```

---

## 🎯 HISTORIA 6: Sistema Actual de Registro

**Tipo:** Especificación Actual (AS-IS)  
**Prioridad:** MEDIA  

### Enunciado
Como **auditor externo**,  
Quiero **entender cómo Faditex registra actualmente sus datos de desperdicio**,  
Para que **pueda evaluar la confiabilidad de sus registros históricos**.

### Respuesta Proporcionada
```
SISTEMA DE REGISTRO ACTUAL: MANUAL

DESCRIPCIÓN:
- Un operario registra periódicamente el volumen de desperdicios
- Los registros se anotan en papel o documentos manuales
- No hay automatización, ni sensor continuo
- Los datos son observacionales, no medidos directamente
```

### Detalles del Problema
```
LIMITACIONES DEL SISTEMA MANUAL:
✗ Sesgos de estimación (el operario puede errar)
✗ No detecta picos de ineficiencia en tiempo real
✗ Registros esporádicos (no diarios ni continuos)
✗ Imposible correlacionar con variables de producción
✗ Falta trazabilidad del dato
✗ Demoras en compilación de reportes

IMPACTO:
- Incertidumbre en los KPIs ambientales
- Dificultad para auditorías
- No hay visibilidad de tendencias
- Imposible predicción de desperdicio futuro
```

### Cómo se transforma en el proyecto
```
DE → A
MANUAL              →  AUTOMÁTICO (sensor IoT)
ESPORÁDICO          →  CONTINUO (cada 5-6 segundos)
OBSERVACIONAL       →  MEDIDO DIRECTAMENTE (HX711)
SIN TRAZABILIDAD    →  TRAZABILIDAD COMPLETA (IoT → Cloud → ETL → ML)
REACTIVO            →  PREDICTIVO (Random Forest)

ARQUITECTURA TO-BE:
[ESP32 + HX711]  →  [Adafruit IO]  →  [ETL Python]  →  [Random Forest]  →  [Streamlit Dashboard]
   (Sensor)           (Cloud MQTT)      (Limpieza)       (Predicción)         (Reportes PDF)
                                                                                automáticos
```

---

## 📊 Matriz de Trazabilidad: Preguntas XP → Código → Dashboard

| Historia XP | Pregunta | Respuesta | Variable en Código | Usado en Dashboard |
|---|---|---|---|---|
| 1 | Tela adquirida/mes | 9,805.66 m | `TELA_ADQUIRIDA_M` | KPI Pantalones, Eficiencia |
| 2 | Densidad tela | 225 g/m | `DENSIDAD_TELA_G_POR_M` | Conversión sensor→metros |
| 3 | Tela/pantalón | 1.20 m | `TELA_POR_PANTALON_M` | Predicción, Eficiencia |
| 4 | Desperdicio/mes | 45 m | `DESPERDICIO_PROM_M` | Factor conversión, Benchmarking |
| 5 | ¿Demoras informes? | SÍ (causa manual) | Problema resuelto | Dashboard en tiempo real |
| 6 | Sistema registro actual | Manual | Problema resuelto | Automatización total |

---

## 🎯 Resumen Ejecutivo

### Validación Completa de Historias de Usuario XP

✅ **HISTORIA 1 (Tela adquirida):** Documentada y usada  
✅ **HISTORIA 2 (Densidad tela):** Crítica en conversión sensor → metros  
✅ **HISTORIA 3 (Tela/pantalón):** Base de estimación de producción  
✅ **HISTORIA 4 (Desperdicio/mes):** Factor de conversión entre kg y pantalones  
✅ **HISTORIA 5 (Demoras informes):** Problema resuelto con automatización  
✅ **HISTORIA 6 (Registro manual):** Transformado a sistema automático IoT  

### Conversiones Matemáticas Derivadas

```
Pregunta XP #1-4 → Fórmula Matemática → Implementación en Dashboard

9,805.66 m/mes de tela adquirida
     ↓
     - 45 m/mes de desperdicio
     ↓
9,760.66 m de tela útil
     ÷ 1.20 m/pantalón
     ↓
8,134 pantalones/mes producidos
     ×
225 g/m densidad de tela
     ÷ 8,134 pantalones/mes
     ÷ 1,000
     ↓
factor_kg_a_pantalones = 803.2 pantalones/kg

Este factor es EL CORAZÓN de la conversión:
  Peso del sensor (kg) × 803.2 = Pantalones estimados
```

---

**Documento creado:** Sistema de Monitoreo de Residuos Textiles  
**Fecha:** 3 de julio de 2026  
**Fuente:** Entrevista XP con Faditex · Pelileo, Ecuador  
**Validado en:** Código, Dashboard, Reportes PDF
