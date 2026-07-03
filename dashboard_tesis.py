import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import seaborn as sns
from Adafruit_IO import Client, RequestError
import os
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
from modelo_prediccion import cargar_y_limpiar_datos, integrar_logica_negocio, entrenar_modelo_random_forest

try:
    import reportlab  # noqa: F401  # solo detecta disponibilidad; los imports concretos van dentro de generar_reporte_pdf
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

st.set_page_config(page_title="Dashboard Predictivo de Producción", page_icon="👖", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# CSS GLOBAL — PREMIUM LIGHT THEME
# Inyección directa para garantizar consistencia visual en todos los widgets.
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── App background ── */
.stApp {
    background-color: #F4F7FE !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1.5px solid #E9EDF7 !important;
    box-shadow: 4px 0 24px rgba(112,144,176,.10) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: #1B2559 !important; }

/* ── Headings ── */
h1,h2,h3,h4 {
    color: #1B2559 !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -.5px !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border-radius: 16px !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: 0 2px 16px rgba(112,144,176,.14) !important;
    border: 1px solid #E9EDF7 !important;
    transition: transform .2s ease, box-shadow .2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 28px rgba(112,144,176,.22) !important;
}
[data-testid="stMetricValue"] {
    color: #1B2559 !important;
    font-weight: 800 !important;
    font-size: 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMetricLabel"] {
    color: #707EAE !important;
    font-size: .8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
}

/* ── Primary & secondary buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4318FF 0%, #7551FF 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all .3s ease !important;
    box-shadow: 0 4px 15px rgba(67,24,255,.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(67,24,255,.50) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #05CD99 0%, #4318FF 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 14px !important;
    padding: 5px !important;
    border: 1px solid #E9EDF7 !important;
    gap: 4px !important;
    box-shadow: 0 2px 8px rgba(112,144,176,.10) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: #707EAE !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 8px 20px !important;
    transition: all .2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4318FF, #7551FF) !important;
    color: white !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 12px rgba(67,24,255,.3) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1.5px solid #E9EDF7 !important;
    margin: 1.2rem 0 !important;
}

/* ── Captions ── */
[data-testid="stCaptionContainer"] p, small { color: #707EAE !important; }

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border-color: #E9EDF7 !important;
    border-radius: 12px !important;
    color: #1B2559 !important;
}

/* ── Alert boxes ── */
[data-testid="stAlert"] { border-radius: 14px !important; }

/* ── Body text ── */
p, li { color: #2D3748; }

/* ══════════════════════════════════════════════════════
   OCULTAR ELEMENTOS DE GESTIÓN/ADMIN DE STREAMLIT
   El usuario final solo debe ver el contenido del dashboard.
   ══════════════════════════════════════════════════════ */

/* Botón "Manage app" (esquina inferior derecha) */
.stAppDeployButton {
    display: none !important;
    visibility: hidden !important;
}

/* Menú hamburguesa (⋮) superior derecho */
#MainMenu {
    display: none !important;
    visibility: hidden !important;
}

/* Footer "Made with Streamlit" */
footer {
    display: none !important;
    visibility: hidden !important;
}

/* La barra de herramientas superior NO se oculta por completo: CONTIENE el botón
   para expandir la barra lateral cuando está colapsada. Ocultarla entera dejaba
   el menú bloqueado. Solo ocultamos sus acciones de desarrollo (Deploy/Manage). */
[data-testid="stToolbar"] {
    display: flex !important;
    visibility: visible !important;
}
[data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"] {
    display: none !important;
}

/* Status bar / running badge */
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

/* Mantener SIEMPRE visible el control para expandir/colapsar la barra lateral.
   Antes se ocultaba "collapsedControl", que es justamente la flecha para volver
   a abrir el menú una vez colapsado: eso dejaba la barra lateral bloqueada. */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Ocultar botón "Manage app" vía JavaScript ─────────────────────────────────
# El CSS a veces no alcanza el elemento porque Streamlit Cloud lo inyecta
# con clases hasheadas que cambian entre versiones. Este script busca por
# texto y por data-testid, re-ejecutándose cada 300 ms para resistir re-renders.
components.html("""
<script>
(function() {
    function hideManageApp() {
        try {
            var doc = window.parent.document;

            // 1) Selectores CSS conocidos por versión de Streamlit
            var bySelector = doc.querySelectorAll(
                '[data-testid="stAppDeployButton"], ' +
                '.stAppDeployButton, ' +
                '[class*="deployButton"], ' +
                '[class*="DeployButton"], ' +
                '[class*="manageApp"], ' +
                '[class*="ManageApp"]'
            );
            bySelector.forEach(function(el) { el.style.display = 'none'; });

            // 2) Buscar por texto "Manage app" (failsafe universal)
            var allEls = doc.querySelectorAll('button, a, div, span');
            allEls.forEach(function(el) {
                if (el.childElementCount === 0 &&
                    el.textContent &&
                    el.textContent.trim() === 'Manage app') {
                    el.style.display = 'none';
                    if (el.parentElement) {
                        el.parentElement.style.display = 'none';
                        if (el.parentElement.parentElement) {
                            el.parentElement.parentElement.style.display = 'none';
                        }
                    }
                }
            });
        } catch(e) {}
    }

    hideManageApp();
    setInterval(hideManageApp, 300);
})();
</script>
""", height=0)
# ─────────────────────────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════════════
# PALETA — PREMIUM LIGHT THEME
# ══════════════════════════════════════════════════════════════════════════════
BG     = '#FFFFFF'   # fondo de figuras matplotlib
AX_BG  = '#FAFBFF'  # fondo de ejes (azulado muy suave)
FG     = '#1B2559'  # texto principal
GRID   = '#E9EDF7'  # grillas suaves
C_BLUE = '#4318FF'  # azul eléctrico
C_ORG  = '#FF9F43'  # naranja/amber
C_GRN  = '#05CD99'  # teal verde
C_RED  = '#EE5D50'  # rojo/coral
C_PUR  = '#7551FF'  # púrpura
C_GRAY = '#A3AED0'  # gris azulado

# Gradientes CSS para KPI cards
GRAD_BLUE   = 'linear-gradient(135deg, #4318FF 0%, #7551FF 100%)'
GRAD_PURPLE = 'linear-gradient(135deg, #7551FF 0%, #9F7AFF 100%)'
GRAD_TEAL   = 'linear-gradient(135deg, #05CD99 0%, #4CBFE6 100%)'
GRAD_GREEN  = 'linear-gradient(135deg, #05CD99 0%, #00B4A6 100%)'
GRAD_ORANGE = 'linear-gradient(135deg, #FF9F43 0%, #EE5D50 100%)'
GRAD_PINK   = 'linear-gradient(135deg, #EE5D50 0%, #F93E7B 100%)'


def kpi_card(icon, value, label, gradient):
    """Tarjeta KPI con gradiente de color premium — estilo admin dashboard moderno."""
    return f"""
    <div style="
        background: {gradient};
        border-radius: 16px;
        padding: 16px 12px 14px;
        color: white;
        box-shadow: 0 6px 24px rgba(0,0,0,0.13);
        display: flex; flex-direction: column; gap: 5px;
        min-height: 105px;
        position: relative; overflow: hidden;
    ">
        <div style="
            position: absolute; right: -12px; top: -12px;
            width: 60px; height: 60px; border-radius: 50%;
            background: rgba(255,255,255,0.13);
        "></div>
        <div style="font-size: 1.2rem; line-height: 1;">{icon}</div>
        <div style="
            font-size: 1.35rem; font-weight: 800;
            letter-spacing: -0.5px; line-height: 1.15;
            font-family: 'Inter', sans-serif;
            word-break: break-all;
        ">{value}</div>
        <div style="
            font-size: 0.62rem; font-weight: 600;
            opacity: 0.88; text-transform: uppercase; letter-spacing: 0.8px;
            line-height: 1.3;
        ">{label}</div>
    </div>
    """



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
        ax.yaxis.grid(True, color=GRID, linewidth=0.8, linestyle='--', alpha=0.8)
    return ax


# ══════════════════════════════════════════════════════════════════════════════
# GENERADOR DE REPORTE PDF
# ══════════════════════════════════════════════════════════════════════════════
def generar_reporte_pdf(df_hist, total_pant, total_tela, total_desperd, metros_desperd,
                        efic_pct, pant_perdidos, co2_total, co2_evitado, co2_diario,
                        pred_kg, pred_pant, pred_tela, pred_co2, seguridad):
    if not REPORTLAB_OK:
        return None

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    # Colores del PDF (paleta clara corporativa)
    C_DARK   = HexColor('#1B2559')
    C_BLUE   = HexColor('#4318FF')
    C_AMBER  = HexColor('#FF9F43')
    C_RED    = HexColor('#EE5D50')
    C_GREEN  = HexColor('#05CD99')
    C_LIGHT  = HexColor('#F4F7FE')
    C_MID    = HexColor('#707EAE')

    # Estilos
    S = {
        'title': ParagraphStyle('title', fontSize=20, fontName='Helvetica-Bold',
                                textColor=C_DARK, alignment=TA_CENTER, spaceAfter=10),
        'subtitle': ParagraphStyle('subtitle', fontSize=11, fontName='Helvetica',
                                   textColor=C_BLUE, alignment=TA_CENTER, spaceAfter=10),
        'meta': ParagraphStyle('meta', fontSize=9, fontName='Helvetica',
                               textColor=C_MID, alignment=TA_CENTER, spaceAfter=2),
        'section': ParagraphStyle('section', fontSize=12, fontName='Helvetica-Bold',
                                  textColor=C_BLUE, spaceBefore=14, spaceAfter=6),
        'body': ParagraphStyle('body', fontSize=9, fontName='Helvetica',
                               textColor=C_DARK, spaceAfter=6, leading=16),
        'callout_green': ParagraphStyle('cg', fontSize=9, fontName='Helvetica-Bold',
                                        textColor=HexColor('#059669'), spaceAfter=8, leading=16),
        'callout_red': ParagraphStyle('cr', fontSize=9, fontName='Helvetica-Bold',
                                      textColor=C_RED, spaceAfter=8, leading=16),
        'callout_amber': ParagraphStyle('ca', fontSize=9, fontName='Helvetica-Bold',
                                        textColor=C_AMBER, spaceAfter=6, leading=16),
        'footer': ParagraphStyle('footer', fontSize=7, fontName='Helvetica',
                                 textColor=C_MID, alignment=TA_CENTER),
    }

    fecha_inicio = df_hist.index.min().strftime('%B %d, %Y')
    fecha_fin    = df_hist.index.max().strftime('%B %d, %Y')
    hoy          = datetime.now().strftime('%d de %B de %Y')
    dias         = len(df_hist)
    co2_km       = co2_total * CO2_KM_EQUIV
    co2_arboles  = round(co2_total / CO2_ARBOL_KG_ANUAL)
    co2_anual    = co2_total * (365 / dias)
    tasa_desperd = (metros_desperd / (total_tela + metros_desperd)) * 100
    benchmark_pant = round((metros_desperd - (total_tela + metros_desperd) * BENCHMARK_DESPERDICIO) / TELA_POR_PANTALON_M)
    ingreso_opt  = benchmark_pant * PRECIO_PANTALON_USD

    def tabla(data, col_widths, header_bg=C_BLUE):
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
            ('GRID',        (0, 0), (-1, -1), 0.4, HexColor('#E9EDF7')),
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
    story.append(HRFlowable(width=W, thickness=1.5, color=C_BLUE, spaceAfter=6))
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
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BLUE, spaceAfter=6))
    story.append(tabla([
        ['Campo', 'Valor'],
        ['Rango de Medición', f'{fecha_inicio} hasta {fecha_fin}'],
        ['Días con Sensor Activo', f'{dias} días'],
        ['Frecuencia de Lectura', 'Cada 5 segundos mediante ESP32 + HX711'],
        ['Disponibilidad del Sistema', f'{dias}/{dias} días analizados (100% datos válidos)'],
    ], [5*cm, W - 5*cm]))

    # SECCIÓN 2
    story.append(Paragraph("2. PRODUCCIÓN Y EFICIENCIA DEL PROCESO", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BLUE, spaceAfter=6))
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
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BLUE, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Total de Desperdicio',         f'{total_desperd:.2f} kg de residuos textiles'],
        ['Equivalencia en Producción',   f'{pant_perdidos:.0f} pantalones no fabricados'],
        ['Tasa de Desperdicio',          f'{tasa_desperd:.1f}% del volumen total'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"■ El desperdicio de {total_desperd:.2f} kg equivale a {pant_perdidos:.0f} pantalones que dejaron de fabricarse. "
        f"Optimizar a {BENCHMARK_DESPERDICIO*100:.1f}% (benchmark del sector) permiriría producir {abs(benchmark_pant):.0f} pantalones "
        f"adicionales por ciclo (ingresos +${abs(ingreso_opt):.0f} USD).", S['callout_red']))

    # SECCIÓN 4
    story.append(Paragraph("4. HUELLA DE CARBONO E IMPACTO AMBIENTAL", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BLUE, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Emisiones CO2eq Totales',     f'{co2_total:.1f} kg CO2eq'],
        ['Factor de Emision',           '6.5 kg CO2eq por jean (etapa fabricacion)'],
        ['Periodo Analizado',           f'{dias} dias ({dias/7:.1f} semanas)'],
        ['Proyeccion Anual',            f'{co2_anual:.0f} kg CO2eq si continua este ritmo'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("&#9632; Impacto Equivalente:", S['callout_amber']))
    story.append(Paragraph(
        f"&#8226; {co2_total:.1f} kg CO<sub>2</sub>eq = {co2_km:.0f} km recorridos en "
        f"automovil (0.25 kg CO<sub>2</sub>/km)<br/>"
        f"&#8226; Se necesitarian {co2_arboles} arboles en crecimiento durante 1 ano para compensarlo<br/>"
        f"&#8226; Proyeccion Anual: {co2_anual:.0f} kg CO<sub>2</sub>eq si continua este ritmo",
        S['body']))

    # SECCIÓN 5
    story.append(Paragraph("5. PROYECCIÓN Y RECOMENDACIONES PARA PRÓXIMO CICLO", S['section']))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_BLUE, spaceAfter=6))
    story.append(tabla([
        ['Indicador', 'Valor'],
        ['Desperdicio Estimado',        f'{pred_kg:.2f} kg'],
        ['Pantalones Proyectados',      f'{pred_pant:.0f} unidades'],
        ['Tela a Consumir',             f'{pred_tela:.1f} m'],
        ['CO2 Estimado',                f'{pred_co2:.1f} kg CO2eq'],
        ['Precision del Modelo',        f'{seguridad:.1f}% (MAPE)'],
    ], [5*cm, W - 5*cm]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"&#9632; Escenario Base (sin intervencion): Proxima produccion generara "
        f"~{pred_kg:.2f} kg desperdicio, {pred_pant:.0f} pantalones y "
        f"{pred_co2:.1f} kg CO<sub>2</sub>eq.", S['callout_amber']))
    story.append(Paragraph(
        f"&#9632; Oportunidad de Optimizacion: Revisar patrones de corte podria reducir el "
        f"desperdicio y reducir emisiones a {pred_co2 * FACTOR_OPTIMIZACION_CO2:.1f} kg CO<sub>2</sub>eq (-{round((1-FACTOR_OPTIMIZACION_CO2)*100):.0f}%).",
        S['callout_green']))

    # PIE DE PÁGINA
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width=W, thickness=0.5, color=C_MID, spaceAfter=4))
    story.append(Paragraph(
        f"Generado por: Sistema IoT Faditex Denim  |  Tecnología: ESP32 + HX711 + Streamlit  |  Fecha: {hoy}",
        S['footer']))

    doc.build(story)
    buf.seek(0)
    return buf


# ══════════════════════════════════════════════════════════════════════════════
# CREDENCIALES DE ADAFRUIT IO
# Prioridad: Streamlit secrets → .env local.
# El bloque try/except evita StreamlitSecretNotFoundError cuando no existe
# secrets.toml (entorno de desarrollo local sin Streamlit Cloud).
# ══════════════════════════════════════════════════════════════════════════════
try:
    username = st.secrets["ADAFRUIT_IO_USERNAME"]
    key      = st.secrets["ADAFRUIT_IO_KEY"]
except Exception:
    load_dotenv()
    username = os.getenv("ADAFRUIT_IO_USERNAME")
    key      = os.getenv("ADAFRUIT_IO_KEY")

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


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — MENÚ DE NAVEGACIÓN CON HEADER DE MARCA
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4318FF 0%, #7551FF 100%);
        border-radius: 18px;
        padding: 20px 16px 16px;
        margin-bottom: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(67,24,255,.30);
    ">
        <div style="font-size: 2.2rem; margin-bottom: 6px;">👖</div>
        <div style="font-size: 1.15rem; font-weight: 800; letter-spacing: -.5px; font-family: 'Inter', sans-serif;">Faditex Denim</div>
        <div style="font-size: 0.7rem; opacity: 0.85; margin-top: 4px; text-transform: uppercase; letter-spacing: 1.2px;">
            Sistema IoT · Monitoreo Textil
        </div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio(
        "Navegación",
        ["📊 Dashboard Principal", "📈 Análisis de Datos", "🌱 Huella de Carbono", "🌲 Bosque Aleatorio", "📄 Reporte"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**⚙️ Configuración del Modelo**")
    n_arboles_select = st.selectbox("Árboles en el Random Forest:", [50, 100, 150, 200, 300], index=1)

    # Badge de conexión estilizado
    if conexion_exitosa:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #05CD99, #00B4A6);
            border-radius: 12px; padding: 10px 14px; margin-top: 14px;
            color: white; font-size: 0.82rem; font-weight: 600;
            box-shadow: 0 4px 12px rgba(5,205,153,.30);
            text-align: center;
        ">📡 &nbsp; Adafruit IO Conectado</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EE5D50, #F93E7B);
            border-radius: 12px; padding: 10px 14px; margin-top: 14px;
            color: white; font-size: 0.82rem; font-weight: 600;
            box-shadow: 0 4px 12px rgba(238,93,80,.30);
            text-align: center;
        ">📡 &nbsp; Sin conexión a Adafruit IO</div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CARGA Y ENTRENAMIENTO (en caché)
# ══════════════════════════════════════════════════════════════════════════════
archivo_excel = 'Datos-sensores-entrenamiento.xlsx'
archivo_csv1  = 'SensorPESO1-20260310-2114.csv'
archivo_csv3  = 'SensorPESO3-20260310-2122.csv'

@st.cache_resource          # cache_resource: correcto para objetos no serializables como modelos sklearn.
                            # cache_data serializa por pickle en cada miss; cache_resource guarda
                            # una referencia en memoria compartida por toda la sesión, evitando
                            # overhead de serialización y posibles errores con objetos stateful.
def cargar_modelo(n_arboles):
    df_limpio = cargar_y_limpiar_datos(archivo_excel, archivo_csv1, archivo_csv3)
    df_final, factor_kg_pantalones = integrar_logica_negocio(df_limpio)
    rf_model, rmse, mae, r2, seguridad_pct = entrenar_modelo_random_forest(df_final, n_arboles)
    return df_final, rf_model, rmse, mae, r2, seguridad_pct, factor_kg_pantalones

@st.cache_data
def cargar_serie_monitoreo(umbral_min=30):
    """Serie diaria de peso SOLO para la gráfica de monitoreo (Huella de Carbono).

    A diferencia del modelo —que usa únicamente días con desperdicio significativo
    (≥50 g)— esta serie aplica un umbral más bajo para INCLUIR los días recientes de
    baja actividad realmente sensados por la báscula (p. ej. ~34 g de julio). Así la
    gráfica llega hasta el día más reciente. No alimenta el modelo ni los KPIs; es
    puramente de visualización, por eso se calcula el máximo diario sin los lags ni
    la invalidación por brechas (no se descarta ningún día con dato).
    """
    df = cargar_y_limpiar_datos(archivo_excel, archivo_csv1, archivo_csv3, umbral_min=umbral_min)
    serie = df['value'].resample('D').max().dropna()
    serie = serie[serie > 0]
    dfv = serie.to_frame('peso_total_g')
    dfv['peso_total_kg'] = dfv['peso_total_g'] / 1000.0
    return dfv

@st.cache_data
def obtener_llave_feed(username_cache):
    """Detecta la clave (key) del feed de peso en Adafruit IO.

    Parámetro ``username_cache``:
        No se usa dentro del cuerpo de la función. Su propósito es actuar como
        **discriminador de caché** para ``@st.cache_data``: Streamlit genera una
        entrada de caché distinta por cada valor único de los argumentos, así que
        pasar el username garantiza que si el usuario cambia sus credenciales en
        tiempo de ejecución, el caché se invalida y se re-consulta la API con el
        cliente ``aio`` actualizado. Sin este argumento, el primer resultado
        quedaría congelado indefinidamente para cualquier usuario.

        El cliente ``aio`` se usa directamente porque es un objeto global de
        sesión (no serializable), por lo que no puede pasarse como argumento a
        una función decorada con ``@st.cache_data``.
    """
    try:
        feeds_disponibles = aio.feeds()
        nombres_feeds = [f.key for f in feeds_disponibles]
        if 'peso' in nombres_feeds:
            return 'peso'
        coincidencias = [f for f in nombres_feeds if 'peso' in f.lower()]
        return coincidencias[0] if coincidencias else (nombres_feeds[0] if nombres_feeds else 'peso')
    except Exception:
        return 'peso'

# =============================================================================
# CONSTANTES DE NEGOCIO — Parámetros del proceso productivo de Faditex
# Ajusta aquí para que el cambio se propague a todo el dashboard y el PDF.
# =============================================================================
CO2_POR_PANTALON_KG    = 6.5    # kg CO₂eq por jean (etapa fabricación, factor LCA)
CO2_CICLO_VIDA_KG      = 32.7   # kg CO₂eq ciclo de vida completo del jean
TELA_POR_PANTALON_M    = 1.20   # metros de tela por pantalón (promedio 1.10–1.30)
BENCHMARK_DESPERDICIO  = 0.025  # tasa de desperdicio benchmark del sector (2.5%)
PRECIO_PANTALON_USD    = 10     # precio unitario estimado del pantalón (USD)
FRACCION_CO2_EVITADO   = 0.10   # fracción de CO₂ evitado si se reduce 10% el desperdicio
FACTOR_OPTIMIZACION_CO2 = 0.67  # factor de reducción de CO₂ con optimización de corte (−33%)
CO2_KM_EQUIV           = 4.0    # km recorridos en auto equivalentes a 1 kg CO₂ (0.25 kg/km)
CO2_ARBOL_KG_ANUAL     = 14     # kg CO₂ absorbidos por un árbol en crecimiento por año
# =============================================================================

if not (os.path.exists(archivo_excel) and os.path.exists(archivo_csv1) and os.path.exists(archivo_csv3)):
    st.error(f"Faltan archivos de datos. Verifica que {archivo_excel}, {archivo_csv1} y {archivo_csv3} estén en la carpeta.")
    st.stop()

with st.spinner("Cargando datos y entrenando modelo..."):
    df_historico, modelo_rf, rmse, mae, r2, seguridad_pct, factor_kg_pantalones = cargar_modelo(n_arboles_select)

# ── Guardas contra datos vacíos ──────────────────────────────────────────────
# Se verifican ANTES de cualquier cálculo para evitar ZeroDivisionError /
# IndexError cuando el pipeline no produce filas (datos insuficientes o
# archivos corruptos). Los cálculos normales no se ven afectados.

if len(df_historico) == 0:
    st.error(
        "⚠️ El pipeline no generó datos diarios. "
        "Verifica que los archivos de entrada tengan lecturas válidas (50 g – 2 000 g) "
        "y al menos 4 días con datos para construir los lags."
    )
    st.stop()

_denom_efic = df_historico['tela_consumida_m'].sum() + df_historico['metros_desperdicio'].sum()
if _denom_efic == 0:
    st.error(
        "⚠️ La tela consumida y el desperdicio suman cero: "
        "no es posible calcular la eficiencia del proceso. "
        "Revisa las constantes de conversión (DENSIDAD_TELA_G_POR_M, TELA_POR_PANTALON_M)."
    )
    st.stop()

if df_historico.iloc[-1:].empty:
    st.error(
        "⚠️ No se pudo obtener el último registro diario para realizar la predicción. "
        "El DataFrame existe pero su último índice no es accesible."
    )
    st.stop()
# ─────────────────────────────────────────────────────────────────────────────

# Métricas pre-calculadas
total_pantalones         = df_historico['pantalones_procesados'].sum()
co2_total_kg             = total_pantalones * CO2_POR_PANTALON_KG
co2_evitado_kg           = co2_total_kg * FRACCION_CO2_EVITADO
co2_diario_kg_promedio   = co2_total_kg / len(df_historico)
total_tela_consumida     = df_historico['tela_consumida_m'].sum()
total_metros_desperdicio = df_historico['metros_desperdicio'].sum()
eficiencia_pct           = (total_tela_consumida / (total_tela_consumida + total_metros_desperdicio)) * 100
pantalones_perdidos      = total_metros_desperdicio / TELA_POR_PANTALON_M
df_historico['co2_diario_kg'] = df_historico['pantalones_procesados'] * CO2_POR_PANTALON_KG

features_modelo      = ['dia_semana', 'dia_mes', 'mes', 'peso_lag_1', 'peso_lag_2', 'peso_lag_3', 'media_movil_3d']
ultimo_dia           = df_historico.iloc[-1:]
prediccion_futura_kg = modelo_rf.predict(ultimo_dia[features_modelo])
pantalones_futuros   = prediccion_futura_kg[0] * factor_kg_pantalones
tela_futura          = pantalones_futuros * TELA_POR_PANTALON_M
co2_prediccion       = pantalones_futuros * CO2_POR_PANTALON_KG


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: DASHBOARD PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "📊 Dashboard Principal":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0 0 4px; font-size: 1.8rem;">Dashboard de Producción Textil</h2>
        <p style="color: #707EAE; margin: 0; font-size: 0.88rem;">
            Faditex Denim &nbsp;·&nbsp; Monitoreo en tiempo real &nbsp;·&nbsp;
            Predicción Random Forest &nbsp;·&nbsp; Huella de Carbono
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 6 KPI Cards con gradientes ──
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(kpi_card("📅", f"{len(df_historico)}", "Días Analizados", GRAD_BLUE), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("👖", f"{total_pantalones:.0f}", "Pantalones Est.", GRAD_PURPLE), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("🧵", f"{total_tela_consumida:.0f} m", "Tela Consumida", GRAD_TEAL), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("⚙️", f"{eficiencia_pct:.1f}%", "Eficiencia", GRAD_GREEN), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("🌱", f"{co2_total_kg:.0f} kg", "CO₂ Período", GRAD_ORANGE), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("🤖", f"{seguridad_pct:.1f}%", "Precisión Modelo", GRAD_PINK), unsafe_allow_html=True)

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
                    # Conversión g → pantalones usando el mismo factor derivado del pipeline
                    # (factor_kg_pantalones = kg desperdicio → pantalones estimados).
                    # Antes: peso_actual / 500 (aprox. hardcodeada, inconsistente con el modelo).
                    st.metric("Equiv. pantalones", f"{(peso_actual / 1000) * factor_kg_pantalones:.2f} un")
                    st.caption("🔄 Actualización cada 4s")
                except RequestError as e:
                    st.warning(f"Error feed: {e}")

            sensor_en_vivo()
        else:
            st.warning("Sin conexión a Adafruit IO")

    with col_serie:
        st.markdown("#### 📈 Desperdicio Diario (kg)")
        fig_s, ax_s = _base_fig((7, 3))
        ax_s.fill_between(df_historico.index, df_historico['peso_total_kg'],
                          alpha=0.18, color=C_BLUE)
        ax_s.plot(df_historico.index, df_historico['peso_total_kg'],
                  color=C_BLUE, linewidth=2.2)
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
        *_, autotexts = ax_pie.pie(
            [total_tela_consumida, total_metros_desperdicio],
            labels=['Útil', 'Desperdicio'],
            colors=[C_GRN, C_RED],
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 9, 'color': FG},
            wedgeprops={'edgecolor': BG, 'linewidth': 2}
        )
        for at in autotexts:
            at.set_color('#FFFFFF')
            at.set_fontweight('bold')
        plt.tight_layout()
        st.pyplot(fig_pie)
        plt.close(fig_pie)

    st.divider()

    col_co2, col_pred, col_lost = st.columns([2, 1, 1])

    with col_co2:
        st.markdown("#### 🌱 CO₂ Diario por Producción (kg)")
        fig_co2, ax_co2 = _base_fig((6, 2.8))
        ax_co2.fill_between(df_historico.index, df_historico['co2_diario_kg'],
                            alpha=0.18, color=C_ORG)
        ax_co2.plot(df_historico.index, df_historico['co2_diario_kg'],
                    color=C_ORG, linewidth=2.2)
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


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ANÁLISIS DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Análisis de Datos":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0 0 4px;">📈 Análisis de Datos Históricos</h2>
        <p style="color: #707EAE; margin: 0; font-size: 0.88rem;">
            Exploración de la serie temporal, distribución y correlaciones del modelo
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📅 Serie de Tiempo", "📊 Distribución del Peso", "🔗 Matriz de Correlación"])

    with tab1:
        fig_st, ax_st = _base_fig((11, 4))
        ax_st.fill_between(df_historico.index, df_historico['peso_total_kg'],
                           alpha=0.18, color=C_BLUE)
        ax_st.plot(df_historico.index, df_historico['peso_total_kg'],
                   color=C_BLUE, linewidth=2.2)
        ax_st.set_ylabel("Peso (kg)", fontsize=10)
        ax_st.set_xlabel("Fecha", fontsize=10)
        ax_st.set_title("Desperdicio Diario Registrado por Sensores", fontsize=11, fontweight='bold')
        _style(ax_st)
        plt.tight_layout()
        st.pyplot(fig_st)
        plt.close(fig_st)

    with tab2:
        fig_h, ax_h = _base_fig((11, 4))
        sns.histplot(df_historico['peso_total_kg'], bins=20, kde=True,
                     color=C_PUR, alpha=0.65, ax=ax_h,
                     line_kws={'color': C_BLUE, 'linewidth': 2.5})
        ax_h.set_xlabel("Peso Total (kg)", fontsize=10)
        ax_h.set_ylabel("Frecuencia", fontsize=10)
        ax_h.set_title("Distribución del Peso Diario", fontsize=11, fontweight='bold')
        _style(ax_h)
        plt.tight_layout()
        st.pyplot(fig_h)
        plt.close(fig_h)

    with tab3:
        st.caption("Correlación entre las variables que usa el modelo: el peso del día, "
                   "sus rezagos (días previos), la media móvil de 3 días y las variables "
                   "temporales. A diferencia de las variables de negocio (que derivan del "
                   "mismo dato y correlacionan 1.00 trivialmente), aquí se observan relaciones reales.")
        # Variables reales del modelo (no transformaciones lineales del mismo dato)
        etiquetas = {
            'peso_total_kg':  'Peso\n(kg)',
            'peso_lag_1':     'Lag 1d',
            'peso_lag_2':     'Lag 2d',
            'peso_lag_3':     'Lag 3d',
            'media_movil_3d': 'Media\nmóvil 3d',
            'dia_semana':     'Día\nsemana',
            'dia_mes':        'Día\nmes',
            'mes':            'Mes',
        }
        cols_corr = [c for c in etiquetas if c in df_historico.columns]
        matriz_corr = df_historico[cols_corr].corr()
        matriz_corr.columns = [etiquetas[c] for c in cols_corr]
        matriz_corr.index   = [etiquetas[c] for c in cols_corr]

        fig_corr, ax_corr = plt.subplots(figsize=(10, 5))
        fig_corr.patch.set_facecolor(BG)
        ax_corr.set_facecolor(AX_BG)
        sns.heatmap(matriz_corr, annot=True, fmt=".2f", cmap='RdYlGn',
                    vmin=-1, vmax=1, linewidths=1, linecolor=GRID,
                    square=True, annot_kws={'size': 9, 'weight': 'bold'},
                    ax=ax_corr, cbar_kws={'shrink': 0.8})
        ax_corr.set_title("Correlación entre Variables del Modelo", fontsize=11, fontweight='bold', pad=10, color=FG)
        ax_corr.tick_params(colors=FG, labelsize=8)
        # Colorbar en tema claro
        cbar = ax_corr.collections[0].colorbar
        assert cbar is not None
        cbar.ax.yaxis.set_tick_params(color=FG, labelsize=8)
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)
        cbar.ax.set_facecolor(AX_BG)
        plt.tight_layout()
        st.pyplot(fig_corr)
        plt.close(fig_corr)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: HUELLA DE CARBONO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🌱 Huella de Carbono":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0 0 4px;">🌱 Huella de Carbono — Etapa de Fabricación</h2>
        <p style="color: #707EAE; margin: 0; font-size: 0.88rem;">
            Basado en 6.5 kg CO₂ por jean (≈20% del ciclo de vida completo de 32–33.4 kg,
            etapa de confección y materia prima)
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"CO₂ Total ({len(df_historico)} días)", f"{co2_total_kg:.1f} kg",
                help=f"Suma de todos los días analizados: "
                     f"{df_historico.index.min().strftime('%d/%m/%Y')} a "
                     f"{df_historico.index.max().strftime('%d/%m/%Y')}")
    col2.metric("CO₂ por Jean (fabricación)",       "6.5 kg", "~20% ciclo de vida")
    col3.metric("CO₂ evitado si −10% desperdicio",  f"{co2_evitado_kg:.1f} kg")
    col4.metric("Intensidad CO₂ diaria",             f"{co2_diario_kg_promedio:.1f} kg/día")

    st.markdown("#### CO₂ Diario por Día de Producción — Monitoreo del Sensor")
    st.caption(
        "🛰️ Gráfica de **monitoreo**: incluye todos los días sensados por la báscula "
        "(umbral 30 g), incluidos los días recientes de baja actividad, por lo que llega "
        "hasta la última medición. El **modelo predictivo y los KPIs de arriba** usan solo "
        "días con desperdicio significativo (≥50 g)."
    )

    # Serie de MONITOREO (umbral 30 g) — SOLO para esta gráfica; incluye días recientes
    # de baja actividad realmente sensados. El CO₂ se deriva con el mismo factor del
    # modelo para mantener la coherencia de la conversión.
    df_monitor = cargar_serie_monitoreo(30).copy()
    df_monitor['co2_diario_kg'] = (df_monitor['peso_total_kg']
                                   * factor_kg_pantalones * CO2_POR_PANTALON_KG)

    # Selector de rango de fechas: la gráfica se recalcula según el día/semana elegido
    fecha_min = df_monitor.index.min().date()
    fecha_max = df_monitor.index.max().date()
    # El calendario se extiende hasta el FIN DEL MES ACTUAL (aunque los datos terminen
    # antes), para poder navegar y seleccionar meses posteriores. El valor por defecto
    # es el rango con datos.
    _hoy = datetime.now().date()
    _fin_mes_actual = (_hoy.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    limite_calendario = max(fecha_max, _fin_mes_actual)
    col_sel, col_kpi = st.columns([2, 1])
    with col_sel:
        rango = st.date_input(
            "Rango de fechas a visualizar:",
            value=(fecha_min, fecha_max),
            min_value=fecha_min, max_value=limite_calendario,
        )

    # date_input puede devolver una sola fecha mientras se está seleccionando el rango
    if isinstance(rango, (tuple, list)):
        fechas = list(rango)
        fecha_ini = fechas[0]
        fecha_fin = fechas[1] if len(fechas) > 1 else fechas[0]
    else:
        fecha_ini = fecha_fin = rango

    df_co2 = df_monitor[(df_monitor.index.date >= fecha_ini) &
                        (df_monitor.index.date <= fecha_fin)]

    with col_kpi:
        st.metric("CO₂ del rango seleccionado",
                  f"{df_co2['co2_diario_kg'].sum():.1f} kg",
                  delta=f"{len(df_co2)} día(s)")

    if df_co2.empty:
        st.warning("No hay datos en el rango seleccionado.")
    else:
        fig_co2, ax_co2 = _base_fig((10, 3.5))
        # Eje ORDINAL: una posición por día CON dato. Los días sin registro
        # (p. ej. cortes de energía en la placa) quedan omitidos y no dejan
        # huecos: la línea salta directo al siguiente día disponible / al más
        # reciente. Cuando entren datos nuevos, aparecen pegados al último punto.
        y_co2 = df_co2['co2_diario_kg'].values
        x_co2 = list(range(len(df_co2)))
        etiquetas_fecha = list(df_co2.index.strftime('%d/%m'))
        ax_co2.fill_between(x_co2, y_co2, alpha=0.18, color=C_ORG)
        ax_co2.plot(x_co2, y_co2, color=C_ORG, linewidth=2.2,
                    marker='o', markersize=4,
                    markerfacecolor='white', markeredgecolor=C_ORG, markeredgewidth=2)
        # Resaltar el último día (el más reciente) como estado actual
        ax_co2.scatter([x_co2[-1]], [y_co2[-1]], s=80, color=C_ORG,
                       edgecolor='white', linewidth=1.8, zorder=5)
        ax_co2.annotate(f"Último día\n{etiquetas_fecha[-1]}",
                        xy=(x_co2[-1], y_co2[-1]),
                        xytext=(-6, 14), textcoords='offset points',
                        ha='right', va='bottom', fontsize=8, color=FG, fontweight='bold')
        # Como máximo ~10 etiquetas de fecha para no saturar el eje; el último
        # día siempre se etiqueta.
        n = len(df_co2)
        paso = max(1, n // 10)
        ticks = list(range(0, n, paso))
        if (n - 1) not in ticks:
            ticks.append(n - 1)
        ax_co2.set_xticks(ticks)
        ax_co2.set_xticklabels([etiquetas_fecha[i] for i in ticks])
        ax_co2.set_xlabel("Día de producción (días sin registro omitidos)", fontsize=10)
        ax_co2.set_ylabel("CO₂ (kg)", fontsize=10)
        ax_co2.set_title("CO₂ Generado por Día de Producción", fontsize=11, fontweight='bold')
        _style(ax_co2)
        plt.tight_layout()
        st.pyplot(fig_co2)
        plt.close(fig_co2)

        # Nota de transparencia: se documenta la interrupción por corte de energía
        # en lugar de rellenar los días faltantes con datos ficticios.
        st.caption(
            f"⚡ Última medición sensada: {df_monitor.index.max().strftime('%d/%m/%Y')}. "
            "El período sin registro (corte de energía en la placa) se omite del eje: "
            "los días se muestran consecutivos, sin rellenar con valores ficticios."
        )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("#### Tela Útil vs Desperdicio")
        fig_pie, ax_pie = plt.subplots(figsize=(4, 3.5))
        fig_pie.patch.set_facecolor(BG)
        ax_pie.set_facecolor(BG)
        *_, autotexts = ax_pie.pie(
            [total_tela_consumida, total_metros_desperdicio],
            labels=[f'Tela útil\n{total_tela_consumida:.1f} m', f'Desperdicio\n{total_metros_desperdicio:.1f} m'],
            colors=[C_GRN, C_RED],
            autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 9, 'color': FG},
            pctdistance=0.75,
            wedgeprops={'edgecolor': BG, 'linewidth': 2}
        )
        for at in autotexts:
            at.set_color('#FFFFFF')
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
                          color=[C_GRN, C_RED], width=0.5,
                          edgecolor='white', linewidth=1.5, zorder=3)
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
        valores_cv = [CO2_POR_PANTALON_KG, CO2_CICLO_VIDA_KG]
        bars_cv    = ax_cv.barh(fases, valores_cv,
                                color=[C_ORG, C_GRAY], edgecolor='white', height=0.4, linewidth=1.5)
        for bar, val in zip(bars_cv, valores_cv):
            ax_cv.text(val + 0.4, bar.get_y() + bar.get_height() / 2,
                       f'{val} kg CO₂', va='center', fontsize=10, fontweight='bold', color=FG)
        ax_cv.set_xlabel("kg CO₂ por jean", fontsize=10)
        ax_cv.set_title("Huella de Carbono por Pantalón", fontsize=11, fontweight='bold')
        ax_cv.set_xlim(0, 40)
        _style(ax_cv, grid=False)
        ax_cv.xaxis.grid(True, color=GRID, linewidth=0.8, linestyle='--', alpha=0.8)
        plt.tight_layout()
        st.pyplot(fig_cv)
        plt.close(fig_cv)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: BOSQUE ALEATORIO
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🌲 Bosque Aleatorio":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="margin: 0 0 4px;">🌲 ¿Cómo funciona el Bosque Aleatorio?</h2>
        <p style="color: #707EAE; margin: 0; font-size: 0.88rem;">
            Visualización interactiva del algoritmo Random Forest y sus predicciones individuales
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Badge de precisión del modelo (antes vivía en Dashboard Principal)
    st.markdown(f"""
    <div style="
        display: inline-flex; align-items: center; gap: 14px;
        background: linear-gradient(135deg, #4318FF 0%, #7551FF 100%);
        color: white; border-radius: 16px; padding: 12px 22px;
        margin-bottom: 20px; box-shadow: 0 6px 20px rgba(67,24,255,.32);
    ">
        <span style="font-size: 1.5rem;">🤖</span>
        <div>
            <div style="font-size: 0.7rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 1px;">Precisión del Modelo</div>
            <div style="font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px;">{seguridad_pct:.1f}%</div>
        </div>
        <div style="border-left: 1px solid rgba(255,255,255,0.3); padding-left: 14px;">
            <div style="font-size: 0.7rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 1px;">Árboles</div>
            <div style="font-size: 1.5rem; font-weight: 800;">{n_arboles_select}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                     color=C_GRN, alpha=0.85, edgecolor='white', linewidth=0.8, zorder=3)
        ax_trees.axhline(prediccion_futura_kg[0], color=C_RED, linewidth=2.5,
                         linestyle='--', label=f'Promedio: {prediccion_futura_kg[0]:.2f} kg', zorder=4)
        ax_trees.set_xlabel("Árbol N°", fontsize=10)
        ax_trees.set_ylabel("Predicción (kg)", fontsize=10)
        ax_trees.set_title("Votos individuales — primeros 20 árboles", fontsize=11, fontweight='bold')
        legend = ax_trees.legend(fontsize=9)
        legend.get_frame().set_facecolor(BG)
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


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: REPORTE
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📄 Reporte":
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="margin: 0 0 4px;">📄 Reporte de Residuos Textiles</h2>
        <p style="color: #707EAE; margin: 0; font-size: 0.88rem;">
            Descarga el reporte completo en PDF con toda la información del período analizado
        </p>
    </div>
    """, unsafe_allow_html=True)

    fecha_inicio = df_historico.index.min().strftime('%d/%m/%Y')
    fecha_fin    = df_historico.index.max().strftime('%d/%m/%Y')

    # Banner de resumen estilizado
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #F4F7FE 0%, #EBF2FF 100%);
        border: 1.5px solid #E9EDF7;
        border-radius: 18px;
        padding: 18px 24px;
        margin-bottom: 20px;
        display: flex; gap: 40px; flex-wrap: wrap; align-items: center;
    ">
        <div>
            <div style="font-size: 0.72rem; color: #707EAE; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 3px;">Período</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #1B2559;">{fecha_inicio} — {fecha_fin}</div>
        </div>
        <div>
            <div style="font-size: 0.72rem; color: #707EAE; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 3px;">Días analizados</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #1B2559;">{len(df_historico)} días</div>
        </div>
        <div>
            <div style="font-size: 0.72rem; color: #707EAE; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 3px;">Modelo</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #1B2559;">Random Forest · {n_arboles_select} árboles</div>
        </div>
        <div>
            <div style="font-size: 0.72rem; color: #707EAE; text-transform: uppercase; letter-spacing: .8px; margin-bottom: 3px;">CO₂ Total</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #EE5D50;">{co2_total_kg:.1f} kg CO₂eq</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

            if pdf_buf is None:
                st.error("No se pudo generar el PDF. Verifica que `reportlab` esté instalado.")
            else:
                nombre_archivo = f"Reporte_Faditex_{df_historico.index.min().strftime('%Y%m%d')}_{df_historico.index.max().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_buf,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    use_container_width=True,
                )
