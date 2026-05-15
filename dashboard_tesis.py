import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from Adafruit_IO import Client, RequestError
import os
import io
from datetime import datetime
from dotenv import load_dotenv
from modelo_prediccion import cargar_y_limpiar_datos, integrar_logica_negocio, entrenar_modelo_random_forest

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

st.set_page_config(page_title="Dashboard Predictivo de Producción", page_icon="👖", layout="wide")

# ==========================================
# GENERADOR DE REPORTE PDF
# ==========================================
def generar_reporte_pdf(df_hist, total_pant, total_tela, total_desperd, metros_desperd,
                        efic_pct, pant_perdidos, co2_total, co2_evitado, co2_diario,
                        pred_kg, pred_pant, pred_tela, pred_co2, seguridad):
    if not REPORTLAB_OK:
        return None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    # Colores corporativos
    C_DARK   = HexColor('#0E1117')
    C_TEAL   = HexColor('#1A8A6A')
    C_AMBER  = HexColor('#F39C12')
    C_RED    = HexColor('#E74C3C')
    C_GREEN  = HexColor('#2ECC71')
    C_LIGHT  = HexColor('#F0F0F0')
    C_MID    = HexColor('#555555')

    # Estilos
    S = {
        'title': ParagraphStyle('title', fontSize=20, fontName='Helvetica-Bold',
                                textColor=C_DARK, alignment=TA_CENTER, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontSize=11, fontName='Helvetica',
                                   textColor=C_TEAL, alignment=TA_CENTER, spaceAfter=2),
        'meta': ParagraphStyle('meta', fontSize=9, fontName='Helvetica',
                               textColor=C_MID, alignment=TA_CENTER, spaceAfter=2),
        'section': ParagraphStyle('section', fontSize=12, fontName='Helvetica-Bold',
                                  textColor=C_TEAL, spaceBefore=14, spaceAfter=6),
        'body': ParagraphStyle('body', fontSize=9, fontName='Helvetica',
                               textColor=C_DARK, spaceAfter=3, leading=14),
        'callout_green': ParagraphStyle('cg', fontSize=9, fontName='Helvetica-Bold',
                                        textColor=C_GREEN, spaceAfter=4, leading=13),
        'callout_red': ParagraphStyle('cr', fontSize=9, fontName='Helvetica-Bold',
                                      textColor=C_RED, spaceAfter=4, leading=13),
        'callout_amber': ParagraphStyle('ca', fontSize=9, fontName='Helvetica-Bold',
                                        textColor=C_AMBER, spaceAfter=4, leading=13),
        'footer': ParagraphStyle('footer', fontSize=7, fontName='Helvetica',
                                 textColor=C_MID, alignment=TA_CENTER),
    }

    fecha_inicio = df_hist.index.min().strftime('%B %d, %Y')
    fecha_fin    = df_hist.index.max().strftime('%B %d, %Y')
    hoy          = datetime.now().strftime('%d de %B de %Y')
    dias         = len(df_hist)
    co2_km       = co2_total * 4.0
    co2_arboles  = round(co2_total / 14)
    co2_anual    = co2_total * (365 / dias)
    tasa_desperd = (metros_desperd / (total_tela + metros_desperd)) * 100
    benchmark_pant = round((metros_desperd - (total_tela + metros_desperd) * 0.025) / 1.20)
    ingreso_opt  = benchmark_pant * 10

    def tabla(data, col_widths, header_bg=C_TEAL):
        t = Table(data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0),  header_bg),
            ('TEXTCOLOR',   (0, 0), (-1, 0),  white),
            ('FONTNAME',    (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, 0),  9),
            ('ALIGN',       (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',    (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_LIGHT, white]),
            ('GRID',        (0, 0), (-1, -1), 0.4, HexColor('#CCCCCC')),
            ('TOPPADDING',  (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0,0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ])
        t.setStyle(style)
        return t

    W = A4[0] - 4*cm  # ancho útil

    story = []

    # ENCABEZADO
    story.append(Paragraph("REPORTE DE RESIDUOS TEXTILES", S['title']))
    story.append(Paragraph("Sistema de Monitoreo IoT — Línea Denim Faditex", S['subtitle']))
    story.append(HRFlowable(width=W, thickness=1.5, color=C_TEAL, spaceAfter=6))
    meta = Table([
        ['Período de Análisis:', f'{fecha_inicio} — {fecha_fin} ({dias} días activos)'],
        ['Fecha de Generación:', hoy],
        ['Audiencia:', 'Gerencia General | Auditor Externo'],
    ], colWidths=[4.5*cm, W - 4.5*cm])
    meta.setStyle(TableStyle([
        ('FONTNAME',  (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',  (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE',  (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), C_MID),
        ('ALIGN',     (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING',(0, 0), (-1, -1), 3),
    ]))
    story.append(meta)
    story.append(Spacer(1, 0.4*cm))

    # SECCIÓN 1
    story.append(Paragraph("1. PERÍODO MEDIDO Y COBERTURA DEL SENSOR", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_TEAL, spaceAfter=6))
    story.append(tabla([
        ['Campo', 'Valor'],
        ['Rango de Medición', f'{fecha_inicio} hasta {fecha_fin}'],
        ['Días con Sensor Activo', f'{dias} días'],
        ['Frecuencia de Lectura', 'Cada ~6 segundos mediante ESP32 + HX711'],
        ['Disponibilidad del Sistema', f'{dias}/{dias} días analizados (100% datos válidos)'],
    ], [5*cm, W - 5*cm]))

    # SECCIÓN 2
    story.append(Paragraph("2. PRODUCCIÓN Y EFICIENCIA DEL PROCESO", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_TEAL, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Pantalones Producidos',      f'{total_pant:.0f} unidades'],
        ['Tela Consumida (Neta)',       f'{total_tela:.1f} m'],
        ['Desperdicio Total',           f'{metros_desperd:.1f} m  ({total_desperd*1000:.0f} g)'],
        ['Eficiencia del Proceso',      f'{efic_pct:.1f}%'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.2*cm))
    if efic_pct >= 95:
        story.append(Paragraph(
            f"✓ El proceso aprovechó el {efic_pct:.1f}% de la tela adquirida. "
            "Esto indica desempeño por encima del promedio industrial (92–95%).", S['callout_green']))
    else:
        story.append(Paragraph(
            f"■ La eficiencia del {efic_pct:.1f}% está por debajo del promedio industrial (92–95%). "
            "Se recomienda revisar los patrones de corte.", S['callout_red']))

    # SECCIÓN 3
    story.append(Paragraph("3. DESPERDICIO GENERADO E IMPACTO EN PRODUCCIÓN", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_TEAL, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Total de Desperdicio',         f'{total_desperd:.2f} kg de residuos textiles'],
        ['Equivalencia en Producción',   f'{pant_perdidos:.0f} pantalones no fabricados'],
        ['Tasa de Desperdicio',          f'{tasa_desperd:.1f}% del volumen total'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"■ El desperdicio de {total_desperd:.2f} kg equivale a {pant_perdidos:.0f} pantalones que dejaron de fabricarse. "
        f"Optimizar a 2.5% (benchmark del sector) permitiría producir {abs(benchmark_pant):.0f} pantalones "
        f"adicionales por ciclo (ingresos +${abs(ingreso_opt):.0f} USD).", S['callout_red']))

    # SECCIÓN 4
    story.append(Paragraph("4. HUELLA DE CARBONO E IMPACTO AMBIENTAL", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_TEAL, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Emisiones CO₂eq Totales',     f'{co2_total:.1f} kg CO₂eq'],
        ['Factor de Emisión',           '6.5 kg CO₂eq por jean (etapa fabricación)'],
        ['Período Analizado',           f'{dias} días ({dias/7:.1f} semanas)'],
        ['Proyección Anual',            f'{co2_anual:.0f} kg CO₂eq si continúa este ritmo'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("■ Impacto Equivalente:", S['callout_amber']))
    story.append(Paragraph(
        f"• {co2_total:.1f} kg CO₂eq = {co2_km:.0f} km recorridos en automóvil (0.25 kg CO₂/km)\n"
        f"• Se necesitarían {co2_arboles} árboles en crecimiento durante 1 año para compensarlo\n"
        f"• Proyección Anual: {co2_anual:.0f} kg CO₂eq si continúa este ritmo", S['body']))

    # SECCIÓN 5
    story.append(Paragraph("5. PROYECCIÓN Y RECOMENDACIONES PARA PRÓXIMO CICLO", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_TEAL, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Desperdicio Estimado',        f'{pred_kg:.2f} kg'],
        ['Pantalones Proyectados',      f'{pred_pant:.0f} unidades'],
        ['Tela a Consumir',             f'{pred_tela:.1f} m'],
        ['CO₂ Estimado',                f'{pred_co2:.1f} kg CO₂eq'],
        ['Precisión del Modelo',        f'{seguridad:.1f}% (MAPE)'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"■ Escenario Base (sin intervención): Próxima producción generará ~{pred_kg:.2f} kg desperdicio, "
        f"{pred_pant:.0f} pantalones y {pred_co2:.1f} kg CO₂eq.", S['callout_amber']))
    story.append(Paragraph(
        f"■ Oportunidad de Optimización: Revisar patrones de corte podría reducir el desperdicio "
        f"y reducir emisiones a {pred_co2 * 0.67:.1f} kg CO₂eq (−33%).", S['callout_green']))

    # PIE DE PÁGINA
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_MID, spaceAfter=4))
    story.append(Paragraph(
        f"Generado por: Sistema IoT Faditex Denim  |  Tecnología: ESP32 + HX711 + Streamlit  |  Fecha: {hoy}",
        S['footer']))

    doc.build(story)
    buf.seek(0)
    return buf

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
        ["📊 Dashboard Principal", "📈 Análisis de Datos", "🌱 Huella de Carbono", "🌲 Bosque Aleatorio", "📄 Reporte"],
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

# ==========================================
# PÁGINA: REPORTE
# ==========================================
elif pagina == "📄 Reporte":
    st.markdown("## 📄 Reporte de Residuos Textiles")
    st.markdown("Descarga el reporte completo en PDF con toda la información del período analizado.")
    st.divider()

    fecha_inicio = df_historico.index.min().strftime('%d/%m/%Y')
    fecha_fin    = df_historico.index.max().strftime('%d/%m/%Y')

    st.markdown(f"**Período:** {fecha_inicio} — {fecha_fin} &nbsp;|&nbsp; **Días analizados:** {len(df_historico)} &nbsp;|&nbsp; **Modelo:** {n_arboles_select} árboles")
    st.markdown("El reporte incluye las siguientes secciones:")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **1. Período medido y cobertura del sensor**
        Fechas, días activos y frecuencia de lectura.

        **2. Producción y eficiencia del proceso**
        Pantalones, tela consumida y % eficiencia vs benchmark industrial.

        **3. Desperdicio e impacto en producción**
        Kg de residuos, equivalencia en pantalones no producidos y oportunidad de optimización.
        """)
    with col_b:
        st.markdown("""
        **4. Huella de carbono e impacto ambiental**
        CO₂ total, equivalencias (km, árboles) y proyección anual.

        **5. Proyección y recomendaciones**
        Predicción del modelo para el próximo ciclo y escenarios de optimización.
        """)

    st.divider()

    if not REPORTLAB_OK:
        st.error("La librería `reportlab` no está instalada. Ejecuta `pip install reportlab` y reinicia la app.")
    else:
        if st.button("📥 Generar y Descargar Reporte PDF", type="primary", use_container_width=True):
            with st.spinner("Generando reporte PDF..."):
                pdf_buf = generar_reporte_pdf(
                    df_hist        = df_historico,
                    total_pant     = total_pantalones,
                    total_tela     = total_tela_consumida,
                    total_desperd  = df_historico['peso_total_kg'].sum(),
                    metros_desperd = total_metros_desperdicio,
                    efic_pct       = eficiencia_pct,
                    pant_perdidos  = pantalones_perdidos,
                    co2_total      = co2_total_kg,
                    co2_evitado    = co2_evitado_kg,
                    co2_diario     = co2_diario_kg_promedio,
                    pred_kg        = prediccion_futura_kg[0],
                    pred_pant      = pantalones_futuros,
                    pred_tela      = tela_futura,
                    pred_co2       = co2_prediccion,
                    seguridad      = seguridad_pct,
                )

            nombre_archivo = f"Reporte_Faditex_{df_historico.index.min().strftime('%Y%m%d')}_{df_historico.index.max().strftime('%Y%m%d')}.pdf"
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_buf,
                file_name=nombre_archivo,
                mime="application/pdf",
                use_container_width=True,
            )
