import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# =============================================================================
# CONSTANTES DE NEGOCIO — Variables del proceso productivo de Faditex
# Centralizar aquí facilita ajustarlas sin buscar en el código.
# =============================================================================
TELA_ADQUIRIDA_M     = 9805.66   # metros de tela adquirida por mes
TELA_POR_PANTALON_M  = 1.20      # metros de tela por pantalón (promedio 1.10–1.30)
DESPERDICIO_PROM_M   = 45        # metros de tela desperdiciada por mes (rango: 40–50)
DENSIDAD_TELA_G_POR_M = 225      # gramos por metro lineal de tela
# =============================================================================

def cargar_y_limpiar_datos(filepath_excel, filepath_csv1, filepath_csv3, umbral_min=50):
    print("Iniciando fase ETL (Extracción, Transformación y Carga) para Excel y CSVs...")

    # Cargar todos los archivos Datos*.xlsx del directorio automáticamente.
    # Al agregar un nuevo export de Adafruit IO con ese nombre, se incluye sin cambiar código.
    directorio = os.path.dirname(os.path.abspath(filepath_excel))
    archivos_excel = sorted(glob.glob(os.path.join(directorio, 'Datos*.xlsx')))
    dataframes = []
    for archivo in archivos_excel:
        try:
            df_tmp = pd.read_excel(archivo, sheet_name='Hoja2')[['created_at', 'value']].copy()
            dataframes.append(df_tmp)
            print(f"  Cargado: {os.path.basename(archivo)} ({len(df_tmp)} filas)")
        except Exception:
            pass

    # Cargar todos los CSVs de sensores (*PESO*.csv) del directorio automáticamente.
    # Igual que con los Excel: al agregar un nuevo export de Adafruit IO con 'PESO'
    # en el nombre, se incluye sin tocar código y el modelo reentrena con más datos.
    archivos_csv = sorted(glob.glob(os.path.join(directorio, '*PESO*.csv')))
    for archivo in archivos_csv:
        try:
            df_tmp = pd.read_csv(archivo)[['created_at', 'value']].copy()
            dataframes.append(df_tmp)
            print(f"  Cargado: {os.path.basename(archivo)} ({len(df_tmp)} filas)")
        except Exception:
            pass

    # Unir todos los datos
    df = pd.concat(dataframes, ignore_index=True)
    
    # Limpieza de valores nulos o numéricos inválidos
    df.dropna(inplace=True)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(inplace=True)
    
    # Transformación: Valores absolutos para corregir taras negativas
    df['value'] = df['value'].abs()
    
    # Filtrar ruido: Conservar solo pesos significativos entre umbral_min y 2000g.
    # umbral_min=50 (por defecto): ruido de tara del sensor vacío. Es el valor que
    #   usa el MODELO predictivo (días con desperdicio significativo).
    # umbral_min más bajo (ej. 30): se usa SOLO para la gráfica de monitoreo, para
    #   incluir días recientes de baja actividad realmente sensados. No alimenta el modelo.
    # >2000g: picos anómalos (ej: SensorPESO1 tenía -2464g → 2464g).
    df = df[(df['value'] >= umbral_min) & (df['value'] <= 2000)]
    
    # Convertir a formato fecha y tiempo, manejando zonas horarias (UTC a local)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['created_at'] = df['created_at'].apply(lambda x: x.tz_localize(None) if x.tzinfo else x)
    
    # Establecer el índice temporal
    df.set_index('created_at', inplace=True)
    df.sort_index(inplace=True)
    
    print(f"Datos limpios: {len(df)} registros disponibles tras filtrado de ruido e integración.")
    return df

def realizar_eda(df):
    print("Iniciando Análisis Exploratorio de Datos (EDA)...")
    # Configuración de estilo de Seaborn
    sns.set_theme(style="whitegrid")
    
    # 1. Gráfico de Serie de Tiempo
    plt.figure(figsize=(14, 6))
    plt.plot(df.index, df['value'], color='teal', alpha=0.7)
    plt.title('Serie de Tiempo - Peso Registrado por Sensores (g)', fontsize=14)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Peso Registrado (g)', fontsize=12)
    plt.tight_layout()
    plt.savefig('eda_serie_tiempo.png')
    plt.close()
    
    # 2. Distribución de los Datos
    plt.figure(figsize=(10, 6))
    sns.histplot(df['value'], bins=50, kde=True, color='indigo')
    plt.title('Distribución de los Valores de Peso', fontsize=14)
    plt.xlabel('Peso (g)', fontsize=12)
    plt.ylabel('Frecuencia', fontsize=12)
    plt.tight_layout()
    plt.savefig('eda_distribucion.png')
    plt.close()
    
    print("Gráficos de EDA generados y guardados: 'eda_serie_tiempo.png', 'eda_distribucion.png'.")

def integrar_logica_negocio(df):
    print("Integrando variables de negocio y preparación de Features para el modelo...")
    
    # ---- VARIABLES DE NEGOCIO (definidas a nivel de módulo, referenciadas aquí) ----
    # TELA_ADQUIRIDA_M, TELA_POR_PANTALON_M, DESPERDICIO_PROM_M, DENSIDAD_TELA_G_POR_M
    # ---------------------------------------------------------------------------------

    # Métricas de negocio derivadas de las constantes anteriores
    pantalones_por_mes = (TELA_ADQUIRIDA_M - DESPERDICIO_PROM_M) / TELA_POR_PANTALON_M
    metros_desperdicio_por_pantalon = DESPERDICIO_PROM_M / pantalones_por_mes

    # Factor de conversión: kg de desperdicio medido por el sensor → pantalones producidos
    # Derivado de: metros_desperdicio = peso_g / DENSIDAD; pantalones = metros / metros_desperdicio_por_pantalon
    factor_kg_a_pantalones = 1000.0 / (DENSIDAD_TELA_G_POR_M * metros_desperdicio_por_pantalon)

    # ── SUPUESTO DE DISEÑO: vaciado único diario de la báscula ──────────────────
    #
    # El sensor HX711 registra el peso INSTANTÁNEO sobre la báscula (~1 lectura cada 5 s
    # según delay(5000) en el firmware), no un acumulado incremental. La serie temporal de un día típico sigue un
    # patrón "diente de sierra": el peso sube a medida que se depositan retazos
    # y cae bruscamente a cero cuando el operario vacía la báscula.
    #
    # SUPUESTO: la báscula se vacía exactamente UNA vez por día, al final de la
    # jornada. Bajo este supuesto, el MÁXIMO diario corresponde al mayor acumulado
    # de retazos antes del vaciado y, por tanto, al desperdicio total generado en
    # ese día. Este comportamiento fue observado directamente en el taller durante
    # el período de recolección de datos (febrero–marzo 2026).
    #
    # Por qué max() y no sum():
    #   sum() sumaría todas las lecturas del día (~17 280 si hay 1 cada 5 segundos),
    #   convirtiendo 500 g reales en ~8 640 kg — un valor sin sentido físico.
    #   max() extrae el único valor significativo (el pico pre-vaciado).
    #
    # Sensibilidad del supuesto — qué ocurriría si no se cumple:
    #
    #   a) La báscula se vacía VARIAS veces al día (ej. al mediodía y al cierre):
    #      max() captura solo el pico más alto, ignorando los vaciados intermedios.
    #      El desperdicio diario quedaría SUBESTIMADO. Para este escenario sería
    #      necesario detectar cada ciclo "subida → reset a cero" y sumar los picos
    #      de cada ciclo (lógica de integración por segmentos).
    #
    #   b) La báscula NUNCA se vacía (el peso crece varios días seguidos):
    #      El máximo de un día incluiría el acumulado de días anteriores,
    #      sobreestimando el desperdicio diario. Los lags y la media móvil
    #      propagarían ese error sistemático hacia el modelo. En este caso
    #      habría que usar la DIFERENCIA entre el máximo del día y el mínimo
    #      de la noche anterior como estimador del desperdicio incremental.
    #
    # Mientras el protocolo operativo de vaciado diario se mantenga, max() es
    # la agregación correcta y computacionalmente más robusta ante lecturas
    # ruidosas o errores de tara.
    # ────────────────────────────────────────────────────────────────────────────
    df_diario = df.resample('D').agg({'value': 'max'})
    df_diario = df_diario[df_diario['value'] > 0].copy()

    df_diario.rename(columns={'value': 'peso_total_g'}, inplace=True)
    df_diario['peso_total_kg'] = df_diario['peso_total_g'] / 1000.0

    # Metros de desperdicio diario medido por la báscula
    df_diario['metros_desperdicio'] = df_diario['peso_total_g'] / DENSIDAD_TELA_G_POR_M

    # Pantalones estimados a partir del desperdicio diario medido
    df_diario['pantalones_procesados'] = df_diario['metros_desperdicio'] / metros_desperdicio_por_pantalon

    # Tela consumida: producción neta (sin el desperdicio)
    df_diario['tela_consumida_m'] = df_diario['pantalones_procesados'] * TELA_POR_PANTALON_M

    # El sensor mide el desperdicio directamente; se registra como dato real (no estimado)
    df_diario['desperdicio_estimado_g'] = df_diario['peso_total_g']
    
    # Variables temporales para el modelo de Machine Learning
    df_diario['dia_semana'] = df_diario.index.dayofweek
    df_diario['dia_mes'] = df_diario.index.day
    df_diario['mes'] = df_diario.index.month
    
    # Creación de variables rezagadas (Lags) usando kilogramos
    df_diario['peso_lag_1'] = df_diario['peso_total_kg'].shift(1)
    df_diario['peso_lag_2'] = df_diario['peso_total_kg'].shift(2)
    df_diario['peso_lag_3'] = df_diario['peso_total_kg'].shift(3)

    # Media móvil de los últimos 3 días en kg (solo días pasados, sin data leakage).
    # shift(1) desplaza la serie un día hacia adelante antes de promediar, de modo que
    # la ventana cubre [t-3, t-2, t-1] y nunca incluye el valor del día actual (target).
    df_diario['media_movil_3d'] = df_diario['peso_total_kg'].shift(1).rolling(window=3).mean()

    # Invalidar lags contaminados por brechas temporales > 2 días entre registros.
    # Sin esto, el lag del día siguiente a una brecha de 21 días apuntaría a datos
    # de 3 semanas atrás, enseñando al modelo patrones falsos.
    cols_lag = ['peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
    diff_dias = df_diario.index.to_series().diff().dt.days.fillna(0)
    for k in range(3):
        filas_invalidas = diff_dias.shift(k, fill_value=0) > 2
        df_diario.loc[filas_invalidas, cols_lag] = np.nan

    # Eliminar filas con NaN (inicio de serie + días posteriores a brechas)
    df_diario.dropna(inplace=True)

    return df_diario, factor_kg_a_pantalones

def entrenar_modelo_random_forest(df_procesado, n_arboles=100):
    print(f"Entrenando el modelo Predictivo Random Forest con {n_arboles} árboles...")
    
    # Variables predictoras (X) y variable objetivo (y)
    # Predeciremos el 'peso_total_kg' del día actual basado SOLO en el pasado y tiempos
    features = ['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
    X = df_procesado[features]
    y = df_procesado['peso_total_kg']
    
    # Split temporal fijo: primeros 80% de los 28 días = entrenamiento, últimos 20% = prueba.
    # shuffle=False preserva el orden cronológico (obligatorio en series de tiempo).
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    # Hiperparámetros controlados para evitar overfitting con ~22 días de entrenamiento:
    # max_depth=5 → máximo 32 nodos por árbol (vs 4096 con depth=12)
    # min_samples_leaf=2 → ninguna hoja puede ajustarse a un único dato
    rf_model = RandomForestRegressor(n_estimators=n_arboles, max_depth=5, min_samples_leaf=2, random_state=42)
    rf_model.fit(X_train, y_train)

    y_pred = rf_model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # R² de entrenamiento: sirve SOLO para medir el gap vs prueba (indicador de overfitting)
    r2_train = rf_model.score(X_train, y_train)
    gap = r2_train - r2

    # --- MÉTRICA DE SEGURIDAD (MAPE → "precisión") ---
    # Qué mide: el MAPE (Mean Absolute Percentage Error) expresa el error medio
    # de predicción como porcentaje del valor real. Se convierte en "seguridad"
    # como (1 - MAPE) * 100, interpretable como "el modelo acierta en promedio
    # este % del valor real" en el conjunto de prueba.
    #
    # Limitación importante: MAPE es inestable cuando y_test contiene valores
    # cercanos o iguales a cero (división por cero → inf o nan que inflan el
    # promedio). Para este dominio (peso en kg > 0) el riesgo es bajo, pero se
    # filtra igualmente por robustez. Además, MAPE penaliza más los errores en
    # valores pequeños que en valores grandes, por lo que puede dar una impresión
    # optimista cuando los pesos de prueba son altos.
    #
    # Nota: esta métrica se expone en el dashboard; no cambiar el nombre de la
    # variable ni el tipo de retorno para no romper dashboard_tesis.py.
    mascara_valida = np.abs(y_test) > 1e-6          # excluye ceros o casi-ceros
    if mascara_valida.sum() == 0:
        # Sin observaciones válidas: no se puede calcular MAPE
        mape = np.nan
        seguridad_pct = 0.0
    else:
        mape = np.mean(np.abs(
            (y_test[mascara_valida] - y_pred[mascara_valida]) / y_test[mascara_valida]
        ))
        seguridad_pct = max(0.0, (1 - mape) * 100)
    
    print("\n--- RESULTADOS DEL MODELO RANDOM FOREST ---")
    print(f"RMSE (Raíz del Error Cuadrático Medio): {rmse:.2f} kg")
    print(f"MAE (Error Absoluto Medio): {mae:.2f} kg")
    print(f"R² Entrenamiento: {r2_train:.4f}")
    print(f"R² Prueba (test set): {r2:.4f}")
    print(f"Gap train-prueba: {gap:.4f} (< 0.10 = sin overfitting)")
    print(f"Seguridad de Predicción: {seguridad_pct:.2f}%")
    print("-------------------------------------------\n")
    
    # Visualización de la Predicción vs Realidad
    plt.figure(figsize=(12, 6))
    plt.plot(y_test.index, y_test.values, label='Datos Reales (kg)', marker='o')
    plt.plot(y_test.index, y_pred, label='Predicción Random Forest (kg)', marker='x', linestyle='--')
    plt.title('Comparación: Predicción vs Valores Reales (Random Forest)', fontsize=14)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Peso Total (kg)', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig('prediccion_random_forest.png')
    plt.close()
    
    print("Gráfico de predicción guardado: 'prediccion_random_forest.png'.")
    
    # Importancia de las variables
    importancias = rf_model.feature_importances_
    df_importancia = pd.DataFrame({'Variable': features, 'Importancia': importancias})
    df_importancia = df_importancia.sort_values(by='Importancia', ascending=False)
    print("\nImportancia de las variables:")
    print(df_importancia.to_string(index=False))

    # ------------------------------------------------------------------
    # VALIDACIÓN CRUZADA TEMPORAL (solo para reporte — no altera el modelo)
    # ------------------------------------------------------------------
    # TimeSeriesSplit divide el dataset en n_splits folds respetando el orden
    # cronológico: cada fold entrena sobre todo lo anterior y prueba sobre la
    # siguiente ventana. Esto simula cómo el modelo se comportaría en producción
    # día a día y produce estimaciones de error más conservadoras (y honestas)
    # que un split aleatorio.
    #
    # Parámetros elegidos:
    #   n_splits=5  → con ~39 días, cada fold de prueba tiene ~5-6 días,
    #                 suficiente para calcular métricas sin vaciar el set de train.
    #   gap=0       → no se omiten días entre train y test (datos diarios,
    #                 no hay riesgo de filtrado por granularidad horaria).
    # Se usan los mismos hiperparámetros del modelo principal para coherencia.
    print("\n--- VALIDACIÓN CRUZADA TEMPORAL (TimeSeriesSplit, 5 folds) ---")
    tscv = TimeSeriesSplit(n_splits=5)
    cv_rmse, cv_mae, cv_r2 = [], [], []

    for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
        # Requiere al menos 2 muestras en train y 1 en test para ser significativo
        if len(train_idx) < 2 or len(test_idx) < 1:
            print(f"  Fold {fold_idx}: omitido (datos insuficientes)")
            continue

        X_cv_train, X_cv_test = X.iloc[train_idx], X.iloc[test_idx]
        y_cv_train, y_cv_test = y.iloc[train_idx], y.iloc[test_idx]

        rf_cv = RandomForestRegressor(
            n_estimators=n_arboles, max_depth=5, min_samples_leaf=2, random_state=42
        )
        rf_cv.fit(X_cv_train, y_cv_train)
        y_cv_pred = rf_cv.predict(X_cv_test)

        fold_rmse = np.sqrt(mean_squared_error(y_cv_test, y_cv_pred))
        fold_mae  = mean_absolute_error(y_cv_test, y_cv_pred)
        # R² puede ser negativo si el modelo es peor que la media — es válido y esperado
        # en folds pequeños; se reporta sin clampear para no ocultar mal desempeño.
        fold_r2   = r2_score(y_cv_test, y_cv_pred)

        cv_rmse.append(fold_rmse)
        cv_mae.append(fold_mae)
        cv_r2.append(fold_r2)
        print(f"  Fold {fold_idx} "
              f"(train={len(train_idx)} días, test={len(test_idx)} días): "
              f"RMSE={fold_rmse:.4f} kg  MAE={fold_mae:.4f} kg  R²={fold_r2:.4f}")

    if cv_rmse:  # al menos un fold válido
        print(f"  --- Promedio CV ---")
        print(f"  RMSE promedio : {np.mean(cv_rmse):.4f} kg  "
              f"(±{np.std(cv_rmse):.4f})")
        print(f"  MAE  promedio : {np.mean(cv_mae):.4f} kg  "
              f"(±{np.std(cv_mae):.4f})")
        print(f"  R²   promedio : {np.mean(cv_r2):.4f}  "
              f"(±{np.std(cv_r2):.4f})")
    else:
        print("  No se pudo completar ningún fold (dataset demasiado pequeño).")
    print("-------------------------------------------------------------\n")
    # Fin del bloque de CV — el modelo final y las métricas del split 80/20
    # (rmse, mae, r2, seguridad_pct) no han sido modificados.

    return rf_model, rmse, mae, r2, seguridad_pct

if __name__ == "__main__":
    archivo_excel = 'Datos-sensores-entrenamiento.xlsx'
    archivo_csv1 = 'SensorPESO1-20260310-2114.csv'
    archivo_csv3 = 'SensorPESO3-20260310-2122.csv'
    
    print("=== PIPELINE DE PREDICCIÓN Y ANÁLISIS DE DATOS ===")
    try:
        # 1. Ejecutar ETL
        df_limpio = cargar_y_limpiar_datos(archivo_excel, archivo_csv1, archivo_csv3)
        
        # 2. Ejecutar EDA
        realizar_eda(df_limpio)
        
        # 3. Aplicar parámetros y lógica de la tesis
        df_final, _ = integrar_logica_negocio(df_limpio)
        
        # 4. Entrenamiento del Modelo
        if len(df_final) > 10:  # Validar que hay suficientes datos después de agrupar por días
            modelo = entrenar_modelo_random_forest(df_final)
            print("\n¡Ejecución del pipeline completada con éxito!")
        else:
            print("\nAlerta: No hay suficientes datos agrupados diariamente para entrenar el modelo.")
            
    except Exception as e:
        print(f"\nOcurrió un error en la ejecución: {str(e)}")
