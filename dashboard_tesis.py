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

def cargar_y_entrenar_modelo_v2(filepath_excel, filepath_csv1, filepath_csv3, n_arboles):
    df_limpio = cargar_y_limpiar_datos(filepath_excel, filepath_csv1, filepath_csv3)
    df_final, factor_kg_pantalones = integrar_logica_negocio(df_limpio)

    rf_model, rmse, mae, r2, seguridad_pct = entrenar_modelo_random_forest(df_final, n_arboles)
    return df_final, rf_model, rmse, mae, r2, seguridad_pct, factor_kg_pantalones

archivo_excel = 'Datos-sensores-entrenamiento.xlsx'
archivo_csv1 = 'SensorPESO1-20260310-2114.csv'
archivo_csv3 = 'SensorPESO3-20260310-2122.csv'

st.subheader("⚙️ Configuración del Modelo")
n_arboles_select = st.selectbox("Cantidad de árboles en el Random Forest (n_estimators):", [50, 100, 150, 200, 300], index=1)

if os.path.exists(archivo_excel) and os.path.exists(archivo_csv1) and os.path.exists(archivo_csv3):
    with st.spinner(f"Entrenando el modelo con {n_arboles_select} árboles..."):
        df_historico, modelo_rf, rmse, mae, r2, seguridad_pct, factor_kg_pantalones = cargar_y_entrenar_modelo_v2(archivo_excel, archivo_csv1, archivo_csv3, n_arboles_select)
        
    st.success("¡Modelo Random Forest entrenado exitosamente con los datos históricos!")
    
    # CO₂ etapa fabricación: ~20% del ciclo de vida completo (32–33.4 kg CO₂/jean denim)
    CO2_POR_PANTALON_KG = 6.5
    total_pantalones = df_historico['pantalones_procesados'].sum()
    co2_total_kg = total_pantalones * CO2_POR_PANTALON_KG
    co2_evitado_kg = co2_total_kg * 0.10
    co2_diario_kg = co2_total_kg / len(df_historico)

    # Mostrar métricas del histórico
    st.subheader("KPIs Históricos y Precisión del Modelo")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Días Analizados", f"{len(df_historico)}")
    col2.metric("Tela Consumida Estimada Total", f"{df_historico['tela_consumida_m'].sum():.2f} m")
    col3.metric("Pantalones Totales (Estimado)", f"{df_historico['pantalones_procesados'].sum():.0f} un")
    col4.metric("Seguridad del Aprendizaje", f"{seguridad_pct:.1f} %", "Ajuste Interno (R²)")

    st.subheader("🌱 Huella de Carbono — Etapa de Fabricación")
    st.caption("Basado en 6.5 kg CO₂ por jean (≈20% del ciclo de vida completo de 32–33.4 kg, etapa de confección y materia prima)")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("CO₂ Total del Período", f"{co2_total_kg:.1f} kg")
    col6.metric("CO₂ por Jean (fabricación)", "6.5 kg", "~20% ciclo de vida")
    col7.metric("CO₂ evitado si −10% desperdicio", f"{co2_evitado_kg:.1f} kg")
    col8.metric("Intensidad CO₂ diaria", f"{co2_diario_kg:.1f} kg/día")

    # KPIs operativos no técnicos
    total_tela_consumida = df_historico['tela_consumida_m'].sum()
    total_metros_desperdicio = df_historico['metros_desperdicio'].sum()
    eficiencia_pct = (total_tela_consumida / (total_tela_consumida + total_metros_desperdicio)) * 100
    pantalones_perdidos = total_metros_desperdicio / 1.20

    st.subheader("📊 Indicadores Operativos")
    col9, col10 = st.columns(2)
    col9.metric("Eficiencia del Proceso", f"{eficiencia_pct:.1f} %", "Tela convertida en pantalones")
    col10.metric("Pantalones No Producidos por Desperdicio", f"{pantalones_perdidos:.0f} un", "Unidades perdidas por corte")

    # Gráficas
    st.subheader("Visualización del Análisis de Datos")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Serie de Tiempo Histórica",
        "Distribución del Peso",
        "Matriz de Correlación",
        "Eficiencia del Proceso",
        "Huella de Carbono"
    ])

    with tab1:
        st.line_chart(df_historico['peso_total_kg'])

    with tab2:
        col_dist, _ = st.columns([1, 1])
        with col_dist:
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.histplot(df_historico['peso_total_kg'], bins=20, kde=True, color='#6A0DAD', ax=ax)
            ax.set_xlabel("Peso Total (kg)", fontsize=10)
            ax.set_ylabel("Frecuencia", fontsize=10)
            ax.set_title("Distribución del Peso Diario", fontsize=11, fontweight='bold')
            ax.tick_params(labelsize=9)
            plt.tight_layout()
            st.pyplot(fig)

    with tab3:
        col_corr, _ = st.columns([1, 1])
        with col_corr:
            etiquetas = {
                'peso_total_kg': 'Peso\n(kg)',
                'pantalones_procesados': 'Pantalones\n(un)',
                'tela_consumida_m': 'Tela\n(m)',
                'desperdicio_estimado_g': 'Desperdicio\n(g)'
            }
            cols_corr = list(etiquetas.keys())
            matriz_corr = df_historico[cols_corr].corr()
            matriz_corr.columns = list(etiquetas.values())
            matriz_corr.index = list(etiquetas.values())

            fig_corr, ax_corr = plt.subplots(figsize=(5, 4))
            sns.heatmap(
                matriz_corr,
                annot=True,
                fmt=".2f",
                cmap='RdYlGn',
                vmin=-1, vmax=1,
                linewidths=0.8,
                linecolor='white',
                square=True,
                annot_kws={'size': 11, 'weight': 'bold'},
                ax=ax_corr
            )
            ax_corr.set_title("Correlación entre Variables", fontsize=11, fontweight='bold', pad=10)
            ax_corr.tick_params(labelsize=9)
            plt.tight_layout()
            st.pyplot(fig_corr)

    with tab4:
        col_ef1, col_ef2 = st.columns(2)
        with col_ef1:
            fig_pie, ax_pie = plt.subplots(figsize=(5, 4))
            valores_pie = [total_tela_consumida, total_metros_desperdicio]
            etiquetas_pie = [f'Tela útil\n{total_tela_consumida:.1f} m', f'Desperdicio\n{total_metros_desperdicio:.1f} m']
            colores_pie = ['#2ECC71', '#E74C3C']
            wedges, texts, autotexts = ax_pie.pie(
                valores_pie, labels=etiquetas_pie, colors=colores_pie,
                autopct='%1.1f%%', startangle=90,
                textprops={'fontsize': 10}, pctdistance=0.75
            )
            for at in autotexts:
                at.set_fontweight('bold')
            ax_pie.set_title("Tela Útil vs Desperdicio (metros)", fontsize=11, fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig_pie)

        with col_ef2:
            fig_bar, ax_bar = plt.subplots(figsize=(5, 4))
            categorias = ['Pantalones\nProducidos', 'Pantalones\nPerdidos por\nDesperdicio']
            valores_bar = [total_pantalones, pantalones_perdidos]
            colores_bar = ['#2ECC71', '#E74C3C']
            bars = ax_bar.bar(categorias, valores_bar, color=colores_bar, width=0.5, edgecolor='white')
            for bar, val in zip(bars, valores_bar):
                ax_bar.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(valores_bar) * 0.02,
                            f'{val:.0f} un', ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax_bar.set_ylabel("Unidades", fontsize=10)
            ax_bar.set_title("Producción vs Pérdida por Desperdicio", fontsize=11, fontweight='bold')
            ax_bar.tick_params(labelsize=9)
            sns.despine(ax=ax_bar)
            plt.tight_layout()
            st.pyplot(fig_bar)

    with tab5:
        # CO₂ diario por día de producción
        df_historico['co2_diario_kg'] = df_historico['pantalones_procesados'] * CO2_POR_PANTALON_KG

        fig_co2, ax_co2 = plt.subplots(figsize=(10, 4))
        ax_co2.fill_between(df_historico.index, df_historico['co2_diario_kg'], alpha=0.3, color='#E67E22')
        ax_co2.plot(df_historico.index, df_historico['co2_diario_kg'], color='#E67E22', linewidth=1.5)
        ax_co2.set_xlabel("Fecha", fontsize=10)
        ax_co2.set_ylabel("CO₂ (kg)", fontsize=10)
        ax_co2.set_title("CO₂ Diario por Día de Producción (Etapa Fabricación)", fontsize=11, fontweight='bold')
        ax_co2.tick_params(labelsize=9)
        sns.despine(ax=ax_co2)
        plt.tight_layout()
        st.pyplot(fig_co2)

        # CO₂ por pantalón: fabricación vs ciclo de vida completo
        st.markdown("#### Comparación: CO₂ Fabricación vs Ciclo de Vida Completo")
        col_cv1, _ = st.columns([1, 1])
        with col_cv1:
            fig_cv, ax_cv = plt.subplots(figsize=(5, 3))
            fases = ['Fabricación\n(este sistema)', 'Ciclo de vida\ncompleto']
            valores_cv = [6.5, 32.7]
            colores_cv = ['#E67E22', '#BDC3C7']
            bars_cv = ax_cv.barh(fases, valores_cv, color=colores_cv, edgecolor='white', height=0.4)
            for bar, val in zip(bars_cv, valores_cv):
                ax_cv.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                           f'{val} kg CO₂', va='center', fontsize=10, fontweight='bold')
            ax_cv.set_xlabel("kg CO₂ por jean", fontsize=10)
            ax_cv.set_title("Huella de Carbono por Pantalón", fontsize=11, fontweight='bold')
            ax_cv.set_xlim(0, 38)
            ax_cv.tick_params(labelsize=9)
            sns.despine(ax=ax_cv)
            plt.tight_layout()
            st.pyplot(fig_cv)
        
    # Zona de predicción
    st.subheader("🔮 Predicción a Futuro")
    st.write("Con base en los datos pasados, el modelo prevé lo siguiente para el próximo ciclo de producción:")
    
    ultimo_dia = df_historico.iloc[-1:]
    
    features_modelo = ['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
    
    prediccion_futura_kg = modelo_rf.predict(ultimo_dia[features_modelo])
    
    pantalones_futuros = prediccion_futura_kg[0] * factor_kg_pantalones
    tela_futura = pantalones_futuros * 1.20
    
    st.info(f"**Predicción de Peso Total para el siguiente ciclo:** {prediccion_futura_kg[0]:.2f} kilogramos")
    st.write(f"Esto representaría un equivalente de **{pantalones_futuros:.1f} pantalones** producidos y **{tela_futura:.2f} metros** de tela consumida.")
    
    st.markdown("---")
    st.markdown("### 🌲 ¿Cómo funciona el 'Bosque Aleatorio' (Random Forest)?")
    st.write("Un *Random Forest* está compuesto por múltiples 'Árboles de Decisión'. Cada árbol observa una parte diferente de los datos históricos y genera su propio cálculo o 'voto'. Al final, el 'Bosque' promedia todos estos árboles para entregar una predicción mucho más robusta y evitar errores de picos extraños (0.00 o valores disparados).")
    
    num_arboles = st.slider("Selecciona cuántos árboles individuales quieres observar por dentro (Máximo 10):", min_value=1, max_value=10, value=5)
    
    st.write("**Cálculos internos de los árboles seleccionados:**")
    for i in range(num_arboles):
        # Utilizamos .values para evitar warnings de feature names en scikit-learn
        pred_arbol = modelo_rf.estimators_[i].predict(ultimo_dia[features_modelo].values)[0]
        st.info(f"🌳 **Árbol {i+1}:** Analizó su parte de los datos y calculó **{pred_arbol:.2f} kg**")
        
    st.success(f"💡 **Conclusión del Bosque:** Promediando los votos de TODOS los árboles entrenados, el modelo final dictamina la predicción de **{prediccion_futura_kg[0]:.2f} kg**.")

else:
    st.error(f"Faltan archivos de datos. Por favor verifica que {archivo_excel}, {archivo_csv1} y {archivo_csv3} estén en la carpeta.")
