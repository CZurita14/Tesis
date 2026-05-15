import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from Adafruit_IO import Client, RequestError
import os
from dotenv import load_dotenv
from modelo_prediccion import cargar_y_limpiar_datos, integrar_logica_negocio, entrenar_modelo_random_forest

st.set_page_config(page_title="Dashboard Predictivo de Producción", page_icon="👖", layout="wide")

# ==========================================
# PALETA OSCURA — consistente con Streamlit
# ==========================================
BG      = '#0E1117'   # fondo Streamlit
AX_BG   = '#1A1D27'   # fondo de ejes
FG      = '#FAFAFA'   # texto
GRID    = '#2B2D3A'   # grillas suaves
C_BLUE  = '#4A9EDB'
C_ORG   = '#F39C12'
C_GRN   = '#2ECC71'
C_RED   = '#E74C3C'
C_PUR   = '#9B59B6'
C_GRAY  = '#7F8C8D'

def _base_fig(figsize):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(AX_BG)
    return fig, ax

def _style(ax, grid=True):
    ax.tick_params(colors=FG, labelsize=9)
    ax.xaxis.label.set_color(FG)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color(GRID)
    if grid:
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color=GRID, linewidth=0.5, linestyle='--')
    return ax

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
except Exception:
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
    n_arboles_select = st.selectbox("Árboles en el Random Forest:", [50, 100, 150, 200, 300], index=1)
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
total_pantalones         = df_historico['pantalones_procesados'].sum()
co2_total_kg             = total_pantalones * CO2_POR_PANTALON_KG
co2_evitado_kg           = co2_total_kg * 0.10
co2_diario_kg_promedio   = co2_total_kg / len(df_historico)
total_tela_consumida     = df_historico['tela_consumida_m'].sum()
total_metros_desperdicio = df_historico['metros_desperdicio'].sum()
eficiencia_pct           = (total_tela_consumida / (total_tela_consumida + total_metros_desperdicio)) * 100
pantalones_perdidos      = total_metros_desperdicio / 1.20
df_historico['co2_diario_kg'] = df_historico['pantalones_procesados'] * CO2_POR_PANTALON_KG

features_modelo      = ['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
ultimo_dia           = df_historico.iloc[-1:]
prediccion_futura_kg = modelo_rf.predict(ultimo_dia[features_modelo])
pantalones_futuros   = prediccion_futura_kg[0] * factor_kg_pantalones
tela_futura          = pantalones_futuros * 1.20
co2_prediccion       = pantalones_futuros * CO2_POR_PANTALON_KG

# ==========================================
# PÁGINA: DASHBOARD PRINCIPAL
# ==========================================
if pagina == "📊 Dashboard Principal":
    st.markdown("## 📊 Dashboard de Producción Textil — Faditex")
    st.markdown("Monitoreo en tiempo real · Predicción Random Forest · Huella de Carbono")
    st.divider()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("📅 Días Analizados",  f"{len(df_historico)}")
    c2.metric("👖 Pantalones Est.",  f"{total_pantalones:.0f} un")
    c3.metric("🧵 Tela Consumida",   f"{total_tela_consumida:.0f} m")
    c4.metric("⚙️ Eficiencia",       f"{eficiencia_pct:.1f} %")
    c5.metric("🌱 CO₂ Período",      f"{co2_total_kg:.0f} kg")
    c6.metric("🤖 Precisión Modelo", f"{seguridad_pct:.1f} %")

    st.divider()

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
                    st.caption("🔄 Actualización cada 4s")
                except RequestError as e:
                    st.warning(f"Error feed: {e}")

            sensor_en_vivo()
        else:
            st.warning("Sin conexión a Adafruit IO")

    with col_serie:
        st.markdown("#### 📈 Desperdicio Diario (kg)")
        fig_s, ax_s = _base_fig((7, 3))
        ax_s.fill_between(df_historico.index, df_historico['peso_total_kg'], alpha=0.15, color=C_BLUE)
        ax_s.plot(df_historico.index, df_historico['peso_total_kg'], color=C_BLUE, linewidth=1.8)
        ax_s.set_ylabel("kg", fontsize=9)
        _style(ax_s)
        plt.tight_layout()
        st.pyplot(fig_s)
        plt.close(fig_s)

    with col_pie:
        st.markdown("#### 🧵 Tela Útil vs Desperdicio")
        fig_pie, ax_pie = plt.subplots(figsize=(3.5, 3))
        fig_pie.patch.set_facecolor(BG)
        ax_pie.set_facecolor(BG)
        wedges, texts, autotexts = ax_pie.pie(
            [total_tela_consumida, total_metros_desperdicio],
            labels=['Útil', 'Desperdicio'],
            colors=[C_GRN, C_RED],
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 9, 'color': FG},
            wedgeprops={'edgecolor': BG, 'linewidth': 2}
        )
        for at in autotexts:
            at.set_color(FG)
            at.set_fontweight('bold')
        plt.tight_layout()
        st.pyplot(fig_pie)
        plt.close(fig_pie)

    st.divider()

    col_co2, col_pred, col_lost = st.columns([2, 1, 1])

    with col_co2:
        st.markdown("#### 🌱 CO₂ Diario por Producción (kg)")
        fig_co2, ax_co2 = _base_fig((6, 2.8))
        ax_co2.fill_between(df_historico.index, df_historico['co2_diario_kg'], alpha=0.2, color=C_ORG)
        ax_co2.plot(df_historico.index, df_historico['co2_diario_kg'], color=C_ORG, linewidth=1.8)
        ax_co2.set_ylabel("kg CO₂", fontsize=9)
        _style(ax_co2)
        plt.tight_layout()
        st.pyplot(fig_co2)
        plt.close(fig_co2)

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
        st.metric("CO₂ evitado si −10%", f"{co2_evitado_kg:.1f} kg",
                  delta="Potencial ahorro", delta_color="normal")

# ==========================================
# PÁGINA: ANÁLISIS DE DATOS
# ==========================================
elif pagina == "📈 Análisis de Datos":
    st.markdown("## 📈 Análisis de Datos Históricos")
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Serie de Tiempo", "Distribución del Peso", "Matriz de Correlación"])

    with tab1:
        fig_st, ax_st = _base_fig((10, 3.5))
        ax_st.fill_between(df_historico.index, df_historico['peso_total_kg'], alpha=0.15, color=C_BLUE)
        ax_st.plot(df_historico.index, df_historico['peso_total_kg'], color=C_BLUE, linewidth=1.8)
        ax_st.set_ylabel("Peso (kg)", fontsize=10)
        ax_st.set_xlabel("Fecha", fontsize=10)
        ax_st.set_title("Desperdicio Diario Registrado por Sensores", fontsize=11, fontweight='bold')
        _style(ax_st)
        plt.tight_layout()
        st.pyplot(fig_st)
        plt.close(fig_st)

    with tab2:
        col_d, _ = st.columns([1, 1])
        with col_d:
            fig_h, ax_h = _base_fig((5, 3.5))
            sns.histplot(df_historico['peso_total_kg'], bins=20, kde=True,
                         color=C_PUR, alpha=0.7, ax=ax_h,
                         line_kws={'color': '#D4A0FF', 'linewidth': 2})
            ax_h.set_xlabel("Peso Total (kg)", fontsize=10)
            ax_h.set_ylabel("Frecuencia", fontsize=10)
            ax_h.set_title("Distribución del Peso Diario", fontsize=11, fontweight='bold')
            _style(ax_h)
            plt.tight_layout()
            st.pyplot(fig_h)
            plt.close(fig_h)

    with tab3:
        col_c, _ = st.columns([1, 1])
        with col_c:
            etiquetas = {
                'peso_total_kg':          'Peso\n(kg)',
                'pantalones_procesados':  'Pantalones\n(un)',
                'tela_consumida_m':       'Tela\n(m)',
                'desperdicio_estimado_g': 'Desperdicio\n(g)'
            }
            matriz_corr = df_historico[list(etiquetas.keys())].corr()
            matriz_corr.columns = list(etiquetas.values())
            matriz_corr.index   = list(etiquetas.values())

            fig_corr, ax_corr = plt.subplots(figsize=(5, 4))
            fig_corr.patch.set_facecolor(BG)
            ax_corr.set_facecolor(AX_BG)
            sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap='RdYlGn',
                        vmin=-1, vmax=1, linewidths=1, linecolor=BG,
                        square=True, annot_kws={'size': 11, 'weight': 'bold'},
                        ax=ax_corr, cbar_kws={'shrink': 0.8})
            ax_corr.set_title("Correlación entre Variables", fontsize=11, fontweight='bold', pad=10, color=FG)
            ax_corr.tick_params(colors=FG, labelsize=9)
            # colorbar text
            cbar = ax_corr.collections[0].colorbar
            cbar.ax.yaxis.set_tick_params(color=FG, labelsize=8)
            plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)
            cbar.ax.set_facecolor(AX_BG)
            plt.tight_layout()
            st.pyplot(fig_corr)
            plt.close(fig_corr)

# ==========================================
# PÁGINA: HUELLA DE CARBONO
# ==========================================
elif pagina == "🌱 Huella de Carbono":
    st.markdown("## 🌱 Huella de Carbono — Etapa de Fabricación")
    st.caption("Basado en 6.5 kg CO₂ por jean (≈20% del ciclo de vida completo de 32–33.4 kg, etapa de confección y materia prima)")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CO₂ Total del Período",            f"{co2_total_kg:.1f} kg")
    col2.metric("CO₂ por Jean (fabricación)",       "6.5 kg", "~20% ciclo de vida")
    col3.metric("CO₂ evitado si −10% desperdicio",  f"{co2_evitado_kg:.1f} kg")
    col4.metric("Intensidad CO₂ diaria",             f"{co2_diario_kg_promedio:.1f} kg/día")

    st.markdown("#### CO₂ Diario por Día de Producción")
    fig_co2, ax_co2 = _base_fig((10, 3.5))
    ax_co2.fill_between(df_historico.index, df_historico['co2_diario_kg'], alpha=0.2, color=C_ORG)
    ax_co2.plot(df_historico.index, df_historico['co2_diario_kg'], color=C_ORG, linewidth=1.8)
    ax_co2.set_xlabel("Fecha", fontsize=10)
    ax_co2.set_ylabel("CO₂ (kg)", fontsize=10)
    ax_co2.set_title("CO₂ Generado por Día de Producción", fontsize=11, fontweight='bold')
    _style(ax_co2)
    plt.tight_layout()
    st.pyplot(fig_co2)
    plt.close(fig_co2)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("#### Tela Útil vs Desperdicio")
        fig_pie, ax_pie = plt.subplots(figsize=(4, 3.5))
        fig_pie.patch.set_facecolor(BG)
        ax_pie.set_facecolor(BG)
        wedges, texts, autotexts = ax_pie.pie(
            [total_tela_consumida, total_metros_desperdicio],
            labels=[f'Tela útil\n{total_tela_consumida:.1f} m', f'Desperdicio\n{total_metros_desperdicio:.1f} m'],
            colors=[C_GRN, C_RED],
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 9, 'color': FG},
            pctdistance=0.75,
            wedgeprops={'edgecolor': BG, 'linewidth': 2}
        )
        for at in autotexts:
            at.set_color(FG)
            at.set_fontweight('bold')
        ax_pie.set_title("Eficiencia del Proceso", fontsize=11, fontweight='bold', color=FG)
        plt.tight_layout()
        st.pyplot(fig_pie)
        plt.close(fig_pie)

    with col_b:
        st.markdown("#### Producción vs Pérdida")
        fig_bar, ax_bar = _base_fig((4, 3.5))
        categorias  = ['Pantalones\nProducidos', 'Pantalones\nPerdidos']
        valores_bar = [total_pantalones, pantalones_perdidos]
        bars = ax_bar.bar(categorias, valores_bar,
                          color=[C_GRN, C_RED], width=0.5, edgecolor=BG, linewidth=1.5)
        for bar, val in zip(bars, valores_bar):
            ax_bar.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(valores_bar) * 0.02,
                        f'{val:.0f} un', ha='center', va='bottom',
                        fontsize=10, fontweight='bold', color=FG)
        ax_bar.set_ylabel("Unidades", fontsize=10)
        ax_bar.set_title("Producción vs Pérdida por Desperdicio", fontsize=11, fontweight='bold')
        _style(ax_bar)
        plt.tight_layout()
        st.pyplot(fig_bar)
        plt.close(fig_bar)

    with col_c:
        st.markdown("#### CO₂ Fabricación vs Ciclo Completo")
        fig_cv, ax_cv = _base_fig((4, 3.5))
        fases      = ['Fabricación\n(este sistema)', 'Ciclo de vida\ncompleto']
        valores_cv = [6.5, 32.7]
        bars_cv    = ax_cv.barh(fases, valores_cv,
                                color=[C_ORG, C_GRAY], edgecolor=BG, height=0.4, linewidth=1.5)
        for bar, val in zip(bars_cv, valores_cv):
            ax_cv.text(val + 0.4, bar.get_y() + bar.get_height() / 2,
                       f'{val} kg CO₂', va='center', fontsize=10, fontweight='bold', color=FG)
        ax_cv.set_xlabel("kg CO₂ por jean", fontsize=10)
        ax_cv.set_title("Huella de Carbono por Pantalón", fontsize=11, fontweight='bold')
        ax_cv.set_xlim(0, 40)
        _style(ax_cv, grid=False)
        ax_cv.xaxis.grid(True, color=GRID, linewidth=0.5, linestyle='--')
        plt.tight_layout()
        st.pyplot(fig_cv)
        plt.close(fig_cv)

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
        fig_trees, ax_trees = _base_fig((6, 3.5))
        ax_trees.bar(range(1, len(preds_arboles) + 1), preds_arboles,
                     color=C_GRN, alpha=0.8, edgecolor=BG, linewidth=0.8)
        ax_trees.axhline(prediccion_futura_kg[0], color=C_RED, linewidth=2,
                         linestyle='--', label=f'Promedio: {prediccion_futura_kg[0]:.2f} kg')
        ax_trees.set_xlabel("Árbol N°", fontsize=10)
        ax_trees.set_ylabel("Predicción (kg)", fontsize=10)
        ax_trees.set_title("Votos individuales — primeros 20 árboles", fontsize=11, fontweight='bold')
        legend = ax_trees.legend(fontsize=9)
        legend.get_frame().set_facecolor(AX_BG)
        legend.get_frame().set_edgecolor(GRID)
        for text in legend.get_texts():
            text.set_color(FG)
        _style(ax_trees)
        plt.tight_layout()
        st.pyplot(fig_trees)
        plt.close(fig_trees)

    st.divider()
    st.markdown("#### Explora los árboles individualmente")
    num_arboles_vis = st.slider("Cuántos árboles quieres ver:", min_value=1, max_value=10, value=5)
    cols_trees = st.columns(min(num_arboles_vis, 5))
    for i in range(num_arboles_vis):
        pred_arbol = modelo_rf.estimators_[i].predict(ultimo_dia[features_modelo].values)[0]
        cols_trees[i % 5].info(f"🌳 **Árbol {i+1}**\n\n**{pred_arbol:.2f} kg**")

    st.success(f"💡 **Conclusión del Bosque:** promediando los {n_arboles_select} árboles, la predicción final es **{prediccion_futura_kg[0]:.2f} kg** de desperdicio.")
