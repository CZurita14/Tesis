import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from Adafruit_IO import Client, RequestError
import os
from dotenv import load_dotenv
from modelo_prediccion import cargar_y_limpiar_datos, integrar_logica_negocio, entrenar_modelo_random_forest

st.set_page_config(page_title="Dashboard Predictivo de Producción", page_icon="👖", layout="wide")

# ==========================================
# CREDENCIALES DE ADAFRUIT IO
# ==========================================
if "ADAFRUIT_IO_USERNAME" in st.secrets:
    username = st.secrets["ADAFRUIT_IO_USERNAME"]
    key = st.secrets["ADAFRUIT_IO_KEY"]
else:
    load_dotenv()
    username = os.getenv("ADAFRUIT_IO_USERNAME")
    key = os.getenv("ADAFRUIT_IO_KEY")

if not username or not key:
    st.warning("⚠️ Faltan las credenciales de Adafruit IO (Usuario o Llave).")
    st.info("Configura tus credenciales en 'Settings -> Secrets' en tu panel de Streamlit.")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Adafruit IO Username:")
    with col2:
        key = st.text_input("Adafruit IO Key:", type="password")
    if not username or not key:
        st.stop()

try:
    aio = Client(username, key)
    _ = aio.feeds()
    conexion_exitosa = True
except Exception as e:
    conexion_exitosa = False

# ==========================================
# SIDEBAR — MENÚ DE NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.markdown("## 👖 Faditex")
    st.markdown("**Sistema IoT de Monitoreo Textil**")
    st.markdown("---")
    pagina = st.radio(
        "Navegación",
        ["📊 Dashboard Principal", "📈 Análisis de Datos", "🌱 Huella de Carbono", "🌲 Bosque Aleatorio"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**⚙️ Configuración del Modelo**")
    n_arboles_select = st.selectbox(
        "Árboles en el Random Forest:",
        [50, 100, 150, 200, 300],
        index=1
    )
    if conexion_exitosa:
        st.success("📡 Adafruit IO conectado")
    else:
        st.error("📡 Sin conexión a Adafruit IO")

# ==========================================
# CARGA Y ENTRENAMIENTO (en caché)
# ==========================================
archivo_excel = 'Datos-sensores-entrenamiento.xlsx'
archivo_csv1  = 'SensorPESO1-20260310-2114.csv'
archivo_csv3  = 'SensorPESO3-20260310-2122.csv'

@st.cache_data
def cargar_modelo(n_arboles):
    df_limpio = cargar_y_limpiar_datos(archivo_excel, archivo_csv1, archivo_csv3)
    df_final, factor_kg_pantalones = integrar_logica_negocio(df_limpio)
    rf_model, rmse, mae, r2, seguridad_pct = entrenar_modelo_random_forest(df_final, n_arboles)
    return df_final, rf_model, rmse, mae, r2, seguridad_pct, factor_kg_pantalones

@st.cache_data
def obtener_llave_feed(username_cache):
    try:
        feeds_disponibles = aio.feeds()
        nombres_feeds = [f.key for f in feeds_disponibles]
        if 'peso' in nombres_feeds:
            return 'peso'
        coincidencias = [f for f in nombres_feeds if 'peso' in f.lower()]
        return coincidencias[0] if coincidencias else (nombres_feeds[0] if nombres_feeds else 'peso')
    except Exception:
        return 'peso'

CO2_POR_PANTALON_KG = 6.5

if not (os.path.exists(archivo_excel) and os.path.exists(archivo_csv1) and os.path.exists(archivo_csv3)):
    st.error(f"Faltan archivos de datos. Verifica que {archivo_excel}, {archivo_csv1} y {archivo_csv3} estén en la carpeta.")
    st.stop()

with st.spinner("Cargando datos y entrenando modelo..."):
    df_historico, modelo_rf, rmse, mae, r2, seguridad_pct, factor_kg_pantalones = cargar_modelo(n_arboles_select)

# Métricas pre-calculadas
total_pantalones        = df_historico['pantalones_procesados'].sum()
co2_total_kg            = total_pantalones * CO2_POR_PANTALON_KG
co2_evitado_kg          = co2_total_kg * 0.10
co2_diario_kg_promedio  = co2_total_kg / len(df_historico)
total_tela_consumida    = df_historico['tela_consumida_m'].sum()
total_metros_desperdicio = df_historico['metros_desperdicio'].sum()
eficiencia_pct          = (total_tela_consumida / (total_tela_consumida + total_metros_desperdicio)) * 100
pantalones_perdidos     = total_metros_desperdicio / 1.20
df_historico['co2_diario_kg'] = df_historico['pantalones_procesados'] * CO2_POR_PANTALON_KG

features_modelo       = ['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
ultimo_dia            = df_historico.iloc[-1:]
prediccion_futura_kg  = modelo_rf.predict(ultimo_dia[features_modelo])
pantalones_futuros    = prediccion_futura_kg[0] * factor_kg_pantalones
tela_futura           = pantalones_futuros * 1.20
co2_prediccion        = pantalones_futuros * CO2_POR_PANTALON_KG

# ==========================================
# PÁGINA: DASHBOARD PRINCIPAL
# ==========================================
if pagina == "📊 Dashboard Principal":
    st.markdown("## 📊 Dashboard de Producción Textil — Faditex")
    st.markdown("Monitoreo en tiempo real · Predicción Random Forest · Huella de Carbono")
    st.divider()

    # --- FILA 1: KPIs compactos ---
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📅 Días Analizados",      f"{len(df_historico)}")
    c2.metric("👖 Pantalones Est.",       f"{total_pantalones:.0f} un")
    c3.metric("🧵 Tela Consumida",        f"{total_tela_consumida:.0f} m")
    c4.metric("⚙️ Eficiencia",            f"{eficiencia_pct:.1f} %")
    c5.metric("🌱 CO₂ Período",           f"{co2_total_kg:.0f} kg")
    c6.metric("🤖 Precisión Modelo",      f"{seguridad_pct:.1f} %")

    st.divider()

    # --- FILA 2: Tiempo real + Serie tiempo + CO₂ ---
    col_rt, col_serie, col_pie = st.columns([1, 2, 1])

    with col_rt:
        st.markdown("#### 📡 Sensor en Vivo")
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
                    st.metric("Equiv. pantalones", f"{peso_actual / 500:.2f} un")
                    st.caption(f"🔄 Actualización cada 4s")
                except RequestError as e:
                    st.warning(f"Error feed: {e}")

            sensor_en_vivo()
        else:
            st.warning("Sin conexión a Adafruit IO")

    with col_serie:
        st.markdown("#### 📈 Desperdicio Diario (kg)")
        fig_s, ax_s = plt.subplots(figsize=(7, 3))
        ax_s.fill_between(df_historico.index, df_historico['peso_total_kg'], alpha=0.2, color='#3498DB')
        ax_s.plot(df_historico.index, df_historico['peso_total_kg'], color='#3498DB', linewidth=1.5)
        ax_s.set_ylabel("kg", fontsize=9)
        ax_s.tick_params(labelsize=8)
        sns.despine(ax=ax_s)
        plt.tight_layout()
        st.pyplot(fig_s)

    with col_pie:
        st.markdown("#### 🧵 Tela Útil vs Desperdicio")
        fig_pie, ax_pie = plt.subplots(figsize=(3.5, 3))
        ax_pie.pie(
            [total_tela_consumida, total_metros_desperdicio],
            labels=['Útil', 'Desperdicio'],
            colors=['#2ECC71', '#E74C3C'],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 9},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
        )
        plt.tight_layout()
        st.pyplot(fig_pie)

    st.divider()

    # --- FILA 3: CO₂ diario + Predicción + Pantalones perdidos ---
    col_co2, col_pred, col_lost = st.columns([2, 1, 1])

    with col_co2:
        st.markdown("#### 🌱 CO₂ Diario por Producción (kg)")
        fig_co2, ax_co2 = plt.subplots(figsize=(6, 2.5))
        ax_co2.fill_between(df_historico.index, df_historico['co2_diario_kg'], alpha=0.25, color='#E67E22')
        ax_co2.plot(df_historico.index, df_historico['co2_diario_kg'], color='#E67E22', linewidth=1.5)
        ax_co2.set_ylabel("kg CO₂", fontsize=9)
        ax_co2.tick_params(labelsize=8)
        sns.despine(ax=ax_co2)
        plt.tight_layout()
        st.pyplot(fig_co2)

    with col_pred:
        st.markdown("#### 🔮 Predicción Siguiente Ciclo")
        st.metric("Desperdicio estimado",  f"{prediccion_futura_kg[0]:.2f} kg")
        st.metric("Pantalones a producir", f"{pantalones_futuros:.0f} un")
        st.metric("Tela a consumir",       f"{tela_futura:.1f} m")
        st.metric("CO₂ estimado",          f"{co2_prediccion:.1f} kg")

    with col_lost:
        st.markdown("#### ⚠️ Pérdida por Desperdicio")
        st.metric("Pantalones no producidos", f"{pantalones_perdidos:.0f} un",
                  delta=f"-{pantalones_perdidos:.0f}", delta_color="inverse")
        st.metric("CO₂ evitado si −10%",      f"{co2_evitado_kg:.1f} kg",
                  delta="Potencial ahorro", delta_color="normal")

# ==========================================
# PÁGINA: ANÁLISIS DE DATOS
# ==========================================
elif pagina == "📈 Análisis de Datos":
    st.markdown("## 📈 Análisis de Datos Históricos")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Serie de Tiempo", "Distribución del Peso", "Matriz de Correlación"])

    with tab1:
        st.line_chart(df_historico['peso_total_kg'])

    with tab2:
        col_d, _ = st.columns([1, 1])
        with col_d:
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.histplot(df_historico['peso_total_kg'], bins=20, kde=True, color='#6A0DAD', ax=ax)
            ax.set_xlabel("Peso Total (kg)", fontsize=10)
            ax.set_ylabel("Frecuencia", fontsize=10)
            ax.set_title("Distribución del Peso Diario", fontsize=11, fontweight='bold')
            ax.tick_params(labelsize=9)
            plt.tight_layout()
            st.pyplot(fig)

    with tab3:
        col_c, _ = st.columns([1, 1])
        with col_c:
            etiquetas = {
                'peso_total_kg':         'Peso\n(kg)',
                'pantalones_procesados': 'Pantalones\n(un)',
                'tela_consumida_m':      'Tela\n(m)',
                'desperdicio_estimado_g':'Desperdicio\n(g)'
            }
            matriz_corr = df_historico[list(etiquetas.keys())].corr()
            matriz_corr.columns = list(etiquetas.values())
            matriz_corr.index   = list(etiquetas.values())
            fig_corr, ax_corr = plt.subplots(figsize=(5, 4))
            sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap='RdYlGn',
                        vmin=-1, vmax=1, linewidths=0.8, linecolor='white',
                        square=True, annot_kws={'size': 11, 'weight': 'bold'}, ax=ax_corr)
            ax_corr.set_title("Correlación entre Variables", fontsize=11, fontweight='bold', pad=10)
            ax_corr.tick_params(labelsize=9)
            plt.tight_layout()
            st.pyplot(fig_corr)

# ==========================================
# PÁGINA: HUELLA DE CARBONO
# ==========================================
elif pagina == "🌱 Huella de Carbono":
    st.markdown("## 🌱 Huella de Carbono — Etapa de Fabricación")
    st.caption("Basado en 6.5 kg CO₂ por jean (≈20% del ciclo de vida completo de 32–33.4 kg, etapa de confección y materia prima)")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CO₂ Total del Período",         f"{co2_total_kg:.1f} kg")
    col2.metric("CO₂ por Jean (fabricación)",    "6.5 kg", "~20% ciclo de vida")
    col3.metric("CO₂ evitado si −10% desperdicio", f"{co2_evitado_kg:.1f} kg")
    col4.metric("Intensidad CO₂ diaria",          f"{co2_diario_kg_promedio:.1f} kg/día")

    st.markdown("#### CO₂ Diario por Día de Producción")
    fig_co2, ax_co2 = plt.subplots(figsize=(10, 3.5))
    ax_co2.fill_between(df_historico.index, df_historico['co2_diario_kg'], alpha=0.25, color='#E67E22')
    ax_co2.plot(df_historico.index, df_historico['co2_diario_kg'], color='#E67E22', linewidth=1.5)
    ax_co2.set_xlabel("Fecha", fontsize=10)
    ax_co2.set_ylabel("CO₂ (kg)", fontsize=10)
    ax_co2.set_title("CO₂ Generado por Día de Producción", fontsize=11, fontweight='bold')
    ax_co2.tick_params(labelsize=9)
    sns.despine(ax=ax_co2)
    plt.tight_layout()
    st.pyplot(fig_co2)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("#### Tela Útil vs Desperdicio")
        fig_pie, ax_pie = plt.subplots(figsize=(4, 3.5))
        wedges, texts, autotexts = ax_pie.pie(
            [total_tela_consumida, total_metros_desperdicio],
            labels=[f'Tela útil\n{total_tela_consumida:.1f} m', f'Desperdicio\n{total_metros_desperdicio:.1f} m'],
            colors=['#2ECC71', '#E74C3C'],
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 9}, pctdistance=0.75,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
        )
        for at in autotexts:
            at.set_fontweight('bold')
        ax_pie.set_title("Eficiencia del Proceso", fontsize=11, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig_pie)

    with col_b:
        st.markdown("#### Producción vs Pérdida")
        fig_bar, ax_bar = plt.subplots(figsize=(4, 3.5))
        categorias   = ['Pantalones\nProducidos', 'Pantalones\nPerdidos']
        valores_bar  = [total_pantalones, pantalones_perdidos]
        bars = ax_bar.bar(categorias, valores_bar, color=['#2ECC71', '#E74C3C'], width=0.5, edgecolor='white')
        for bar, val in zip(bars, valores_bar):
            ax_bar.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(valores_bar) * 0.02,
                        f'{val:.0f} un', ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax_bar.set_ylabel("Unidades", fontsize=10)
        ax_bar.set_title("Producción vs Pérdida por Desperdicio", fontsize=11, fontweight='bold')
        ax_bar.tick_params(labelsize=9)
        sns.despine(ax=ax_bar)
        plt.tight_layout()
        st.pyplot(fig_bar)

    with col_c:
        st.markdown("#### CO₂ Fabricación vs Ciclo Completo")
        fig_cv, ax_cv = plt.subplots(figsize=(4, 3.5))
        fases      = ['Fabricación\n(este sistema)', 'Ciclo de vida\ncompleto']
        valores_cv = [6.5, 32.7]
        bars_cv    = ax_cv.barh(fases, valores_cv, color=['#E67E22', '#BDC3C7'], edgecolor='white', height=0.4)
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

# ==========================================
# PÁGINA: BOSQUE ALEATORIO
# ==========================================
elif pagina == "🌲 Bosque Aleatorio":
    st.markdown("## 🌲 ¿Cómo funciona el Bosque Aleatorio?")
    st.divider()

    col_txt, col_img = st.columns([1, 1])
    with col_txt:
        st.markdown("""
        Un **Random Forest** (Bosque Aleatorio) es un algoritmo de Machine Learning
        que construye múltiples **Árboles de Decisión** de forma simultánea.

        Cada árbol:
        - Recibe una muestra **diferente** de los datos históricos
        - Analiza solo algunas de las variables disponibles
        - Genera su propia **predicción individual**

        El bosque promedia los resultados de todos los árboles para producir
        una predicción final más robusta y menos susceptible a errores aislados.

        ---
        **¿Por qué es útil aquí?**

        El desperdicio textil tiene un comportamiento **no lineal**: varía según el
        día de la semana, el volumen reciente de trabajo y patrones históricos.
        El Random Forest captura estas relaciones sin necesidad de asumir una
        forma matemática fija entre las variables.
        """)

    with col_img:
        st.markdown("#### Predicción de cada árbol vs promedio del bosque")
        preds_arboles = [
            modelo_rf.estimators_[i].predict(ultimo_dia[features_modelo].values)[0]
            for i in range(min(20, len(modelo_rf.estimators_)))
        ]
        fig_trees, ax_trees = plt.subplots(figsize=(6, 3.5))
        ax_trees.bar(range(1, len(preds_arboles) + 1), preds_arboles,
                     color='#27AE60', alpha=0.7, edgecolor='white')
        ax_trees.axhline(prediccion_futura_kg[0], color='#E74C3C', linewidth=2,
                         linestyle='--', label=f'Promedio bosque: {prediccion_futura_kg[0]:.2f} kg')
        ax_trees.set_xlabel("Árbol N°", fontsize=10)
        ax_trees.set_ylabel("Predicción (kg)", fontsize=10)
        ax_trees.set_title("Votos individuales de los primeros 20 árboles", fontsize=11, fontweight='bold')
        ax_trees.legend(fontsize=9)
        ax_trees.tick_params(labelsize=9)
        sns.despine(ax=ax_trees)
        plt.tight_layout()
        st.pyplot(fig_trees)

    st.divider()
    st.markdown("#### Explora los árboles individualmente")
    num_arboles_vis = st.slider("Cuántos árboles quieres ver:", min_value=1, max_value=10, value=5)
    cols_trees = st.columns(min(num_arboles_vis, 5))
    for i in range(num_arboles_vis):
        pred_arbol = modelo_rf.estimators_[i].predict(ultimo_dia[features_modelo].values)[0]
        col_idx = i % 5
        cols_trees[col_idx].info(f"🌳 **Árbol {i+1}**\n\n**{pred_arbol:.2f} kg**")

    st.success(f"💡 **Conclusión del Bosque:** promediando los {n_arboles_select} árboles, la predicción final es **{prediccion_futura_kg[0]:.2f} kg** de desperdicio.")
