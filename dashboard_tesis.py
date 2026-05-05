import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Adafruit_IO import Client, RequestError
import os
from dotenv import load_dotenv
from modelo_prediccion import cargar_y_limpiar_datos, integrar_logica_negocio, entrenar_modelo_random_forest

# Configuración de la página del Dashboard
st.set_page_config(page_title="Dashboard Predictivo de Producción", page_icon="👖", layout="wide")

st.title("👖 Dashboard de Producción y Análisis de Desperdicio Textil")
st.markdown("Monitoreo en tiempo real (Adafruit IO) y Predicción mediante Machine Learning (Random Forest).")

# ==========================================
# 1. CREDENCIALES DE ADAFRUIT IO
# ==========================================
# Intentar cargar desde secrets o .env
if "ADAFRUIT_IO_USERNAME" in st.secrets:
    username = st.secrets["ADAFRUIT_IO_USERNAME"]
    key = st.secrets["ADAFRUIT_IO_KEY"]
else:
    load_dotenv()
    username = os.getenv("ADAFRUIT_IO_USERNAME")
    key = os.getenv("ADAFRUIT_IO_KEY")

# Interfaz para ingresar credenciales si faltan (Solución al error 404 en Streamlit Cloud)
if not username or not key:
    st.warning("⚠️ Faltan las credenciales de Adafruit IO (Usuario o Llave).")
    st.info("Dado que estás en la nube (Streamlit Cloud), tu archivo '.env' no se subió por seguridad. Puedes ingresar temporalmente tus credenciales aquí para ver el dashboard funcionando, o configurarlas permanentemente en 'Settings -> Secrets' en tu panel de Streamlit.")
    
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Adafruit IO Username:")
    with col2:
        key = st.text_input("Adafruit IO Key:", type="password")
        
    if not username or not key:
        st.stop()  # Detener ejecución hasta que se ingresen

# Inicializar cliente de Adafruit IO
try:
    aio = Client(username, key)
    # Hacer una llamada rápida para validar credenciales (Evita el 404 posterior si el usuario es erróneo)
    _ = aio.feeds()
    conexion_exitosa = True
except Exception as e:
    conexion_exitosa = False
    st.error(f"❌ Error conectando a Adafruit IO. Revisa que tu usuario '{username}' y tu llave sean correctos. Error técnico: {e}")

# ==========================================
# 2. SECCIÓN EN TIEMPO REAL (ADAFRUIT IO)
# ==========================================
st.header("📡 Monitoreo en Tiempo Real")

@st.cache_data
def obtener_llave_feed_correcta(username_cache):
    try:
        feeds_disponibles = aio.feeds()
        nombres_feeds = [f.key for f in feeds_disponibles]
        llave_feed = 'peso'
        if 'peso' not in nombres_feeds:
            coincidencias = [f for f in nombres_feeds if 'peso' in f.lower()]
            if coincidencias:
                llave_feed = coincidencias[0]
            elif len(nombres_feeds) > 0:
                llave_feed = nombres_feeds[0]
        return llave_feed
    except Exception:
        return 'peso'

if conexion_exitosa:
    # Pasamos el username para que cache_data se invalide si el usuario cambia
    llave_feed = obtener_llave_feed_correcta(username)
    
    @st.fragment(run_every=4)
    def render_realtime_dashboard():
        try:
            # 1 sola llamada a data() (historial), optimizando el límite de la API.
            datos_recientes = aio.data(llave_feed)
            
            if not datos_recientes:
                st.warning(f"El feed '{llave_feed}' está vacío.")
                return
                
            ultimo_dato = datos_recientes[0]
            ultimo_peso_real = float(ultimo_dato.value)
            
            # Lógica de Negocio básica para el dato actual
            PESO_PANTALON = 500  # gramos
            pantalones_actuales = ultimo_peso_real / PESO_PANTALON
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Último Peso Registrado (g)", f"{ultimo_peso_real:.2f} g")
            col2.metric("Equivalente en Pantalones", f"{pantalones_actuales:.2f} un")
            col3.metric("Última Actualización", f"{ultimo_dato.created_at}")
            st.caption(f"Leyendo desde el feed de Adafruit: '{llave_feed}' | 🔄 Auto-actualización cada 4s")
            
            # Visualización gráfica de los datos en tiempo real de Adafruit
            st.markdown("### 📈 Gráfica de Sensores en Tiempo Real")
            valores_rt = [float(d.value) for d in datos_recientes]
            fechas_rt = [pd.to_datetime(d.created_at) for d in datos_recientes]
            
            df_rt = pd.DataFrame({'Peso (g)': valores_rt}, index=fechas_rt)
            # Ordenar cronológicamente
            df_rt = df_rt.sort_index()
            st.line_chart(df_rt)
            
        except RequestError as e:
            st.warning(f"No se pudo obtener datos del feed '{llave_feed}'. Verifica tu configuración. Error: {e}")
            
    render_realtime_dashboard()

st.divider()

# ==========================================
# 3. SECCIÓN MODELO PREDICTIVO (HISTÓRICO)
# ==========================================
st.header("🤖 Análisis Histórico y Predicción (Random Forest)")

@st.cache_data
def cargar_y_entrenar_modelo_v2(filepath_excel, filepath_csv1, filepath_csv3):
    df_limpio = cargar_y_limpiar_datos(filepath_excel, filepath_csv1, filepath_csv3)
    df_final = integrar_logica_negocio(df_limpio)
    
    rf_model = entrenar_modelo_random_forest(df_final)
    return df_final, rf_model

archivo_excel = 'Datos-sensores-entrenamiento.xlsx'
archivo_csv1 = 'SensorPESO1-20260310-2114.csv'
archivo_csv3 = 'SensorPESO3-20260310-2122.csv'

if os.path.exists(archivo_excel) and os.path.exists(archivo_csv1) and os.path.exists(archivo_csv3):
    with st.spinner("Entrenando el modelo con datos históricos combinados..."):
        df_historico, modelo_rf = cargar_y_entrenar_modelo_v2(archivo_excel, archivo_csv1, archivo_csv3)
        
    st.success("¡Modelo Random Forest entrenado exitosamente con los datos históricos!")
    
    # Mostrar métricas del histórico
    st.subheader("KPIs Históricos")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Días Analizados", f"{len(df_historico)}")
    col2.metric("Tela Consumida Estimada Total", f"{df_historico['tela_consumida_m'].sum():.2f} m")
    col3.metric("Pantalones Totales (Estimado)", f"{df_historico['pantalones_procesados'].sum():.0f} un")
    col4.metric("Desperdicio Estimado Diario", f"{df_historico['desperdicio_estimado_g'].iloc[0]:.2f} g")

    # Gráficas
    st.subheader("Visualización del Análisis de Datos")
    
    tab1, tab2, tab3 = st.tabs(["Serie de Tiempo Histórica", "Distribución del Peso", "Matriz de Correlación"])
    
    with tab1:
        st.line_chart(df_historico['peso_total_g'])
        
    with tab2:
        fig, ax = plt.subplots(figsize=(8,4))
        sns.histplot(df_historico['peso_total_g'], bins=30, kde=True, color='purple', ax=ax)
        st.pyplot(fig)
        
    with tab3:
        fig_corr, ax_corr = plt.subplots(figsize=(8,6))
        cols_corr = ['peso_total_g', 'pantalones_procesados', 'tela_consumida_m', 'desperdicio_estimado_g']
        matriz_corr = df_historico[cols_corr].corr()
        sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', fmt=".2f", ax=ax_corr)
        st.pyplot(fig_corr)
        
    # Zona de predicción
    st.subheader("🔮 Predicción a Futuro")
    st.write("Con base en los datos pasados, el modelo prevé lo siguiente para el próximo ciclo de producción:")
    
    ultimo_dia = df_historico.iloc[-1:]
    
    features_modelo = ['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
    
    prediccion_futura = modelo_rf.predict(ultimo_dia[features_modelo])
    
    pantalones_futuros = prediccion_futura[0] / 500
    tela_futura = pantalones_futuros * 1.20
    
    st.info(f"**Predicción de Peso Total para el siguiente ciclo:** {prediccion_futura[0]:.2f} gramos")
    st.write(f"Esto representaría un equivalente de **{pantalones_futuros:.1f} pantalones** producidos y **{tela_futura:.2f} metros** de tela consumida.")
    
    st.markdown("---")
    st.markdown("### 🌲 ¿Cómo funciona el 'Bosque Aleatorio' (Random Forest)?")
    st.write("Un *Random Forest* está compuesto por múltiples 'Árboles de Decisión'. Cada árbol observa una parte diferente de los datos históricos y genera su propio cálculo o 'voto'. Al final, el 'Bosque' promedia todos estos árboles para entregar una predicción mucho más robusta y evitar errores de picos extraños (0.00 o valores disparados).")
    
    num_arboles = st.slider("Selecciona cuántos árboles individuales quieres observar por dentro (Máximo 10):", min_value=1, max_value=10, value=5)
    
    st.write("**Cálculos internos de los árboles seleccionados:**")
    for i in range(num_arboles):
        # Utilizamos .values para evitar warnings de feature names en scikit-learn
        pred_arbol = modelo_rf.estimators_[i].predict(ultimo_dia[features_modelo].values)[0]
        st.info(f"🌳 **Árbol {i+1}:** Analizó su parte de los datos y calculó **{pred_arbol:.2f} gramos**")
        
    st.success(f"💡 **Conclusión del Bosque:** Promediando los votos de TODOS los árboles entrenados, el modelo final dictamina la predicción de **{prediccion_futura[0]:.2f} gramos**.")

else:
    st.error(f"Faltan archivos de datos. Por favor verifica que {archivo_excel}, {archivo_csv1} y {archivo_csv3} estén en la carpeta.")
