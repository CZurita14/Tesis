import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

def cargar_y_limpiar_datos(filepath_excel, filepath_csv1, filepath_csv3):
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

    # Cargar datos desde CSVs
    df_csv1 = pd.read_csv(filepath_csv1)[['created_at', 'value']].copy()
    df_csv3 = pd.read_csv(filepath_csv3)[['created_at', 'value']].copy()
    dataframes.extend([df_csv1, df_csv3])

    # Unir todos los datos
    df = pd.concat(dataframes, ignore_index=True)
    
    # Limpieza de valores nulos o numéricos inválidos
    df.dropna(inplace=True)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df.dropna(inplace=True)
    
    # Transformación: Valores absolutos para corregir taras negativas
    df['value'] = df['value'].abs()
    
    # Filtrar ruido: Conservar solo pesos significativos entre 50g y 500g.
    # <50g: ruido de tara del sensor vacío. >500g: picos anómalos del sensor (ej: -2464g → 2464g).
    df = df[(df['value'] >= 50) & (df['value'] <= 500)]
    
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
    
    # ---- VARIABLES DE NEGOCIO PROPORCIONADAS ----
    TELA_ADQUIRIDA_M = 9805.66        # metros de tela adquirida por mes
    TELA_POR_PANTALON_M = 1.20        # metros de tela por pantalón (promedio 1.10–1.30)
    DESPERDICIO_PROM_M = 45           # metros de tela desperdiciada por mes (rango: 40–50)
    DENSIDAD_TELA_G_POR_M = 225       # gramos por metro lineal de tela
    # ---------------------------------------------

    # Métricas de negocio derivadas de las constantes anteriores
    pantalones_por_mes = (TELA_ADQUIRIDA_M - DESPERDICIO_PROM_M) / TELA_POR_PANTALON_M
    metros_desperdicio_por_pantalon = DESPERDICIO_PROM_M / pantalones_por_mes

    # Factor de conversión: kg de desperdicio medido por el sensor → pantalones producidos
    # Derivado de: metros_desperdicio = peso_g / DENSIDAD; pantalones = metros / metros_desperdicio_por_pantalon
    factor_kg_a_pantalones = 1000.0 / (DENSIDAD_TELA_G_POR_M * metros_desperdicio_por_pantalon)

    # Agregación diaria: MÁXIMO del peso sobre la báscula en el día.
    # El sensor mide el peso ACTUAL en la báscula (medición de estado, no incremental).
    # El pico diario equivale al mayor acumulado de retazos antes de vaciar la báscula,
    # que es el desperdicio real generado en el día. Usar sum() multiplica ese peso
    # por la cantidad de lecturas (~14 400/día) y produce valores absurdamente inflados.
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
    
    # Media móvil de los últimos 3 días en kg
    df_diario['media_movil_3d'] = df_diario['peso_total_kg'].rolling(window=3).mean()
    
    # Eliminar valores NaN generados por el lag y la media móvil
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

    # Seguridad = R² del conjunto de PRUEBA (datos nunca vistos por el modelo)
    # Un gap train-prueba < 0.10 confirma que no hay overfitting
    seguridad_pct = max(0.0, r2 * 100)
    
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
