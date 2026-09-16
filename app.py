import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import io
import os
import glob
import plotly.express as px

# Importaciones de ReportLab para generación de PDFs
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Gestión TI - UPS",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta corporativa optimizada de alto contraste
BG_MAIN = "#0D1117"        # Fondo principal negro carbón profundo
BG_CARD = "#161B22"        # Fondo de tarjetas y contenedores
BORDER_COLOR = "#30363D"   # Bordes sutiles pero definidos
TEXT_PRIMARY = "#FFFFFF"   # Texto blanco puro para máxima legibilidad
TEXT_SECONDARY = "#C9D1D9" # Texto secundario claro
SUMMARY_VAL_COLOR = "#58A6FF" # Azul brillante para valores clave
INPUT_BG = "#21262D"       # Fondo para campos de entrada
BTN_BG = "#21262D"         # Fondo para botones

def aplicar_estilos_corporativos():
    css = f"""
        <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        header[data-testid="stHeader"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
        }}
        .block-container {{
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
            margin-top: -20px !important;
        }}
        
        .stApp {{
            background-color: {BG_MAIN} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        
        /* Reducir espacios generales entre elementos de Streamlit */
        div.stMarkdown {{
            margin-bottom: -10px !important;
        }}
        
        div[data-testid="stVerticalBlock"] {{
            gap: 0.4rem !important;
        }}

        /* Textos generales */
        h1, h2, h3, h4, h5, h6, span, p, label, 
        .stMarkdown, div[data-testid="stMarkdownContainer"], 
        div[data-testid="stText"], .stMetricLabel, .stMetricValue, .stCaption {{
            color: {TEXT_PRIMARY} !important;
        }}

        /* CORRECCIÓN PARA INPUTS Y CAMPOS */
        input[type="date"], input[type="text"], input[type="password"], input[type="number"] {{
            color-scheme: dark !important;
            color: {TEXT_PRIMARY} !important;
            background-color: {INPUT_BG} !important;
        }}

        div[data-baseweb="select"] > div, 
        div[data-baseweb="input"] > div, 
        div[data-baseweb="base-input"],
        div[data-baseweb="base-input"] > input,
        div[data-baseweb="calendar"] {{
            background-color: {INPUT_BG} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {BORDER_COLOR} !important;
            color-scheme: dark !important;
        }}
        
        div[data-baseweb="popover"], div[data-baseweb="menu"], 
        div[data-testid="stDataFrameToolbar"], div[data-testid="stElementToolbar"],
        div[data-baseweb="popover"] > div, div[data-baseweb="menu"] > div,
        ul[data-baseweb="menu"], li[data-baseweb="menu-item"] {{
            background-color: {BG_CARD} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {BORDER_COLOR} !important;
        }}
        
        div[data-baseweb="popover"] *, div[data-baseweb="menu"] *,
        div[data-testid="stDataFrameToolbar"] *, div[data-testid="stElementToolbar"] * {{
            color: {TEXT_PRIMARY} !important;
            background-color: transparent !important;
        }}

        textarea, select {{
            color: {TEXT_PRIMARY} !important;
            background-color: {INPUT_BG} !important;
        }}

        /* Botones generales */
        .stButton > button, div.stButton > button, button[kind="secondary"], 
        div[data-testid="stDownloadButton"] > button, .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button {{
            background-color: {BTN_BG} !important;
            color: {TEXT_PRIMARY} !important;
            border: 1px solid {BORDER_COLOR} !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }}
        .stButton > button *, .stDownloadButton > button *, div[data-testid="stFormSubmitButton"] > button * {{
            color: {TEXT_PRIMARY} !important;
            opacity: 1 !important;
            font-weight: 700 !important;
        }}
        .stButton > button:hover, .stButton > button:hover *, 
        .stDownloadButton > button:hover, .stDownloadButton > button:hover *,
        div[data-testid="stFormSubmitButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover * {{
            border-color: {SUMMARY_VAL_COLOR} !important;
            color: {SUMMARY_VAL_COLOR} !important;
        }}

        /* CABECERAS DE TABLAS */
        div[data-testid="stDataFrame"] th, 
        div[data-testid="stDataEditor"] th,
        .dataframe th,
        div[data-testid="stDataFrame"] div[role="columnheader"],
        div[data-testid="stDataEditor"] div[role="columnheader"] {{
            background-color: #1F6FEB !important;
            color: #FFFFFF !important;
            font-weight: 900 !important;
            font-size: 0.9rem !important;
            opacity: 1 !important;
            border-bottom: 3px solid #58A6FF !important;
            border-right: 1px solid {BORDER_COLOR} !important;
        }}
        
        div[data-testid="stDataFrame"] td, 
        div[data-testid="stDataEditor"] td,
        .dataframe td {{
            color: #FFFFFF !important;
            background-color: {BG_CARD} !important;
            font-weight: 600 !important;
            opacity: 1 !important;
            border-right: 1px solid {BORDER_COLOR} !important;
            border-bottom: 1px solid {BORDER_COLOR} !important;
        }}

        /* HEADER PRINCIPAL COMPACTO */
        .main-header {{
            background-color: {BG_CARD};
            padding: 12px 18px;
            border-radius: 10px;
            border: 1px solid {BORDER_COLOR};
            margin-bottom: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }}
        .main-header h1 {{
            font-size: 1.4rem !important;
            font-weight: 800;
            color: {TEXT_PRIMARY};
            margin: 0;
        }}
        .main-header p {{
            color: {TEXT_SECONDARY};
            margin: 2px 0 4px 0;
            font-size: 0.85rem;
        }}

        /* TARJETAS KPI MÁS ACHICADAS Y COMPACTAS */
        .kpi-card {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }}
        .kpi-header {{
            font-size: 0.72rem;
            font-weight: 800;
            color: {TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}
        .kpi-value {{
            font-size: 1.4rem;
            font-weight: 900;
            color: {TEXT_PRIMARY};
            line-height: 1.1;
        }}

        .summary-card {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 8px;
        }}
        .summary-title {{
            font-size: 0.85rem;
            font-weight: 800;
            color: {TEXT_PRIMARY};
        }}
        .summary-val {{
            font-size: 1.2rem;
            font-weight: 900;
            color: {SUMMARY_VAL_COLOR};
            margin: 4px 0;
        }}
        .summary-sub {{
            font-size: 0.78rem;
            color: {TEXT_SECONDARY};
        }}

        /* BARRA LATERAL (SIDEBAR) REDUCIDA A 220px */
        section[data-testid="stSidebar"] {{
            background-color: {BG_CARD} !important;
            border-right: 1px solid {BORDER_COLOR};
            min-width: 220px !important;
            max-width: 220px !important;
            width: 220px !important;
        }}
        section[data-testid="stSidebar"] > div:first-child {{
            width: 220px !important;
            padding: 0.8rem 0.4rem !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT_PRIMARY} !important;
        }}
        
        section[data-testid="stSidebar"] h1 {{
            font-size: 1rem !important;
            font-weight: 800 !important;
            margin-bottom: 0.1rem !important;
        }}
        
        section[data-testid="stSidebar"] .stCaption p {{
            font-size: 0.75rem !important;
            color: {TEXT_SECONDARY} !important;
            margin-bottom: 0.5rem !important;
        }}

        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
            gap: 2px !important;
        }}
        
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {{
            background-color: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 6px !important;
            padding: 4px 6px !important;
            margin-bottom: 1px !important;
        }}
        
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {{
            background-color: {INPUT_BG} !important;
            border-color: {BORDER_COLOR} !important;
        }}
        
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:has(input:checked) {{
            background-color: {INPUT_BG} !important;
            border: 1px solid #1F6FEB !important;
        }}

        section[data-testid="stSidebar"] .stRadio label p {{
            font-size: 0.8rem !important;
            font-weight: 600 !important;
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos_corporativos()

def buscar_archivo_excel(patron_nombre):
    archivos = glob.glob(f"*{patron_nombre}*.xlsx")
    if archivos:
        return archivos[0]
    return None

PATRONES = {
    "Inventario": "Inventario_UPS",
    "Mantenimiento": "Mantenimiento_UPS",
    "Baterias": "Cambios_Baterias",
    "Alquiler": "alquiler_de_UPS"
}

USUARIOS = {
    "admin": {"password": "123", "rol": "admin", "nombre": "Administrador TI"},
    "reportes": {"password": "123", "rol": "visor_exportador", "nombre": "Analista TI"},
    "invitado": {"password": "123", "rol": "solo_vista", "nombre": "Soporte Técnico"}
}

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.session_state.rol_actual = None

def login():
    st.title("🔐 Acceso - Infraestructura TI & UPS")
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("Usuario TI:").strip().lower()
            pwd = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Ingresar al Sistema", use_container_width=True):
                if user in USUARIOS and USUARIOS[user]["password"] == pwd:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = USUARIOS[user]["nombre"]
                    st.session_state.rol_actual = USUARIOS[user]["rol"]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

def logout():
    st.session_state.autenticado = False
    st.rerun()

if not st.session_state.autenticado:
    login()
    st.stop()

def cargar_excel(clave):
    ruta = buscar_archivo_excel(PATRONES[clave])
    if ruta and os.path.exists(ruta):
        try:
            if clave == "Inventario":
                return pd.read_excel(ruta, sheet_name='UPS Inventario')
            elif clave == "Mantenimiento":
                return pd.read_excel(ruta, header=1)
            elif clave == "Baterias":
                return pd.read_excel(ruta, header=0)
            else:
                return pd.read_excel(ruta)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def guardar_excel(df, clave):
    ruta = buscar_archivo_excel(PATRONES[clave]) or f"{PATRONES[clave]}.xlsx"
    try:
        if clave == "Inventario":
            with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='UPS Inventario', index=False)
        else:
            df.to_excel(ruta, index=False, engine='openpyxl')
        return True
    except Exception:
        return False

for clave in PATRONES.keys():
    if f"df_{clave}" not in st.session_state:
        st.session_state[f"df_{clave}"] = cargar_excel(clave)

def exportar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

def generar_pdf(titulo, df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(letter), 
        rightMargin=10, 
        leftMargin=10, 
        topMargin=15, 
        bottomMargin=15
    )
    elementos = []
    estilos = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'T', parent=estilos['Heading1'], fontSize=12, textColor=colors.HexColor('#58A6FF'), alignment=1
    )
    elementos.append(Paragraph(f"<b>{titulo}</b>", estilo_titulo))
    elementos.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/><br/>", estilos['Normal']))
    
    num_cols = max(len(df.columns), 1)
    font_size = 5 if num_cols > 15 else 7
    leading_size = font_size + 2

    estilo_c = ParagraphStyle(
        'C', parent=estilos['Normal'], fontSize=font_size, leading=leading_size, wordWrap='CJK'
    )
    estilo_h = ParagraphStyle(
        'H', parent=estilos['Normal'], fontSize=font_size, leading=leading_size, 
        textColor=colors.white, fontName='Helvetica-Bold', wordWrap='CJK'
    )
    
    if df.empty:
        elementos.append(Paragraph("Sin datos disponibles", estilos['Normal']))
    else:
        tbl_data = [[Paragraph(str(c), estilo_h) for c in df.columns]]
        for _, row in df.iterrows():
            tbl_data.append([Paragraph(str(val) if pd.notna(val) and str(val).strip() != "" else "-", estilo_c) for val in row])
        
        ancho_disponible = 772
        ancho_col = max(20, ancho_disponible / num_cols)
        
        tabla = Table(tbl_data, colWidths=[ancho_col] * num_cols, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F6FEB')),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#30363D')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))
        elementos.append(tabla)
        
    doc.build(elementos)
    return buffer.getvalue()

def render_kpi(icono, titulo, valor):
    html = f"""
    <div class="kpi-card">
        <div class="kpi-header">{icono}&nbsp;{titulo}</div>
        <div class="kpi-value">{valor}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.sidebar.title("💻 GESTIÓN DE UPS")
st.sidebar.caption(f"👤 **{st.session_state.usuario_actual}**")

menu = ["📊 Panel de control", "📦 Inventario UPS", "🛠️ Mantenimientos", "🔋 Cambio de baterías", "🤝 Alquileres"]

if st.session_state.rol_actual == "admin":
    menu.insert(3, "📝 Nuevo Registro")

if st.session_state.rol_actual in ["admin", "visor_exportador"]:
    menu.append("📥 Exportar datos")

opcion = st.sidebar.radio("Seleccionar módulo:", menu)

if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    logout()

anio_actual = datetime.now().year

st.markdown("""
    <div class="main-header">
        <h1>💻 Sistemas TI - Control de UPS</h1>
        <p>Plataforma centralizada de infraestructura para el control de inventario, mantenimiento, baterías y alquileres.</p>
""", unsafe_allow_html=True)

components.html("""
    <div style="display: inline-flex; align-items:center; background-color: #21262D; color: #58A6FF; padding: 2px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: 700; border: 1px solid #30363D; font-family: sans-serif;">
        🟢 Servidor TI Activo • Actualizado <span id="reloj" style="margin-left: 4px;"></span>
    </div>
    <script>
        function actualizarReloj() {
            const ahora = new Date();
            const dia = String(ahora.getDate()).padStart(2, '0');
            const mes = String(ahora.getMonth() + 1).padStart(2, '0');
            const anio = ahora.getFullYear();
            const horas = String(ahora.getHours()).padStart(2, '0');
            const minutos = String(ahora.getMinutes()).padStart(2, '0');
            const segundos = String(ahora.getSeconds()).padStart(2, '0');
            document.getElementById('reloj').innerText = `${dia}/${mes}/${anio} ${horas}:${minutos}:${segundos}`;
        }
        actualizarReloj();
        setInterval(actualizarReloj, 1000);
    </script>
""", height=28)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# PANEL DE CONTROL (DASHBOARD)
# -------------------------------------------------------------
if opcion == "📊 Panel de control":

    st.subheader("📊 Panel de control TI")
    st.caption("Resumen ejecutivo de la infraestructura de UPS.")

    df_inv = st.session_state.df_Inventario
    df_mant = st.session_state.df_Mantenimiento
    df_bat = st.session_state.df_Baterias
    df_alq = st.session_state.df_Alquiler

    val_inv = len(df_inv)

    val_mant_total = 0
    val_mant_actual = 0
    if not df_mant.empty:
        col_mant_f = [c for c in df_mant.columns if "FECHA" in str(c).upper()]
        if col_mant_f:
            val_mant_total = int(df_mant[col_mant_f[0]].notna().sum())
            anos_col = pd.to_datetime(df_mant[col_mant_f[0]], errors='coerce').dt.year
            val_mant_actual = int((anos_col == anio_actual).sum())
        else:
            val_mant_total = len(df_mant)
            val_mant_actual = len(df_mant)

    val_bat_anterior = 0
    val_bat_actual = 0
    val_bat_total = 0
    if not df_bat.empty:
        col_bat_actual = [c for c in df_bat.columns if ('CANT' in str(c).upper() or 'CANTDAD' in str(c).upper()) and '26' in str(c)]
        col_bat_ant = [c for c in df_bat.columns if ('CANT' in str(c).upper() or 'CANTDAD' in str(c).upper()) and '25' in str(c)]
        
        if col_bat_ant:
            val_bat_anterior = int(pd.to_numeric(df_bat[col_bat_ant[0]], errors='coerce').sum())
        if col_bat_actual:
            val_bat_actual = int(pd.to_numeric(df_bat[col_bat_actual[0]], errors='coerce').sum())
            
        val_bat_total = val_bat_anterior + val_bat_actual

    val_alq_total = 0
    val_dias_alq = 0
    val_ingresos_alq = 0.0
    if not df_alq.empty:
        col_cot = [c for c in df_alq.columns if 'COTIZACION' in str(c).upper()]
        if col_cot:
            df_alq_real = df_alq.dropna(subset=[col_cot[0]])
            df_alq_real = df_alq_real[~df_alq_real[col_cot[0]].astype(str).str.contains('SUB-TOTAL|TOTAL', case=False, na=False)]
        else:
            df_alq_real = df_alq.dropna(how='all')

        val_alq_total = len(df_alq_real)
        col_dias = [c for c in df_alq_real.columns if 'DIAS' in str(c).upper()]
        if col_dias:
            val_dias_alq = int(pd.to_numeric(df_alq_real[col_dias[0]], errors='coerce').sum())
        
        col_costo = [c for c in df_alq_real.columns if 'COSTO TOTAL' in str(c).upper() or 'TOTAL' in str(c).upper()]
        if col_costo:
            val_ingresos_alq = float(pd.to_numeric(df_alq_real[col_costo[0]], errors='coerce').sum())

    k1, k2, k3, k4 = st.columns(4)
    with k1: render_kpi("📦", "UPS EN INVENTARIO", f"{val_inv:,}")
    with k2: render_kpi("🛠️", "MANTENIMIENTOS", f"{val_mant_total:,}")
    with k3: render_kpi("🔋", "BATERÍAS CAMBIADAS", f"{val_bat_total:,}")
    with k4: render_kpi("⏱️", "ALQUILERES", f"{val_alq_total:,}")

    k5, k6, k7, k8 = st.columns(4)
    with k5: render_kpi("📅", "DÍAS ALQUILADOS", f"{val_dias_alq:,}")
    with k6: render_kpi("💰", "INGRESOS POR ALQUILER", f"S/ {val_ingresos_alq:,.2f}")
    with k7: render_kpi("🛠️", f"MANTENIMIENTOS {anio_actual}", f"{val_mant_actual:,}")
    with k8: render_kpi("🔋", f"BATERÍAS {anio_actual}", f"{val_bat_actual:,}")

    col_graficos, col_resumen = st.columns([2.2, 1])
    theme_bg = "rgba(0,0,0,0)"
    font_color = "#FFFFFF"

    with col_graficos:
        st.markdown("### 📅 Comparativo por año")
        
        data_bat = pd.DataFrame({
            "Año": [str(anio_actual - 1), str(anio_actual)],
            "Cantidad": [val_bat_anterior, val_bat_actual]
        })
        fig_bat = px.bar(
            data_bat, x="Cantidad", y="Año", orientation='h', text="Cantidad",
            title="🔋 Cambios de baterías", color_discrete_sequence=['#58A6FF']
        )
        fig_bat.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=10), plot_bgcolor=theme_bg, paper_bgcolor=theme_bg, font_color=font_color)
        st.plotly_chart(fig_bat, use_container_width=True)

        data_mant = pd.DataFrame({
            "Año": [str(anio_actual - 1), str(anio_actual)],
            "Cantidad": [val_mant_total - val_mant_actual, val_mant_actual]
        })
        fig_mant = px.bar(
            data_mant, x="Año", y="Cantidad", text="Cantidad",
            title="🛠️ Mantenimientos", color_discrete_sequence=['#58A6FF']
        )
        fig_mant.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=10), plot_bgcolor=theme_bg, paper_bgcolor=theme_bg, font_color=font_color)
        st.plotly_chart(fig_mant, use_container_width=True)

    with col_resumen:
        st.markdown("### 📌 Resumen ejecutivo")
        st.markdown(f"""
            <div class="summary-card">
                <div class="summary-title">📦 Inventario actual</div>
                <div class="summary-val">{val_inv:,} UPS</div>
                <div class="summary-sub">Equipos registrados en el inventario.</div>
            </div>
            
            <div class="summary-card">
                <div class="summary-title">🔋 Baterías {anio_actual}</div>
                <div class="summary-val">{val_bat_actual:,}</div>
                <div class="summary-sub">Baterías cambiadas durante {anio_actual}.</div>
            </div>

            <div class="summary-card">
                <div class="summary-title">💰 Alquileres</div>
                <div class="summary-val">S/ {val_ingresos_alq:,.2f}</div>
                <div class="summary-sub">Monto acumulado real de alquileres.</div>
            </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# INVENTARIO UPS
# -------------------------------------------------------------
elif opcion == "📦 Inventario UPS":
    st.markdown("## 📦 Inventario de UPS")
    
    col_busqueda, col_registros = st.columns([3.5, 1])
    df_inv = st.session_state.df_Inventario
    
    with col_busqueda:
        busqueda = st.text_input("🔍 Buscar UPS", placeholder="Escribe un modelo, tienda, serie, marca...")
    
    if busqueda.strip():
        mask = df_inv.astype(str).apply(lambda row: row.str.contains(busqueda, case=False, na=False)).any(axis=1)
        df_mostrar = df_inv[mask]
    else:
        df_mostrar = df_inv

    with col_registros:
        render_kpi("", "Registros", f"{len(df_mostrar):,}")

    if st.session_state.rol_actual == "admin":
        df_edit = st.data_editor(df_mostrar, num_rows="dynamic", use_container_width=True, key="ed_inv")
        if st.button("💾 Guardar Cambios en Excel"):
            st.session_state.df_Inventario = df_edit
            guardar_excel(df_edit, "Inventario")
            st.success("✅ Archivo Inventario guardado.")
            st.rerun()
    else:
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# MANTENIMIENTO DE UPS
# -------------------------------------------------------------
elif opcion == "🛠️ Mantenimientos":
    st.markdown("## 🛠️ Mantenimiento de UPS")
    
    busqueda_tienda = st.text_input("🔎 Buscar tienda", placeholder="Nombre de tienda...")
    df_mant_filtrado = st.session_state.df_Mantenimiento.copy()
            
    if busqueda_tienda.strip():
        col_t = [c for c in df_mant_filtrado.columns if 'TIENDA' in str(c).upper()]
        if col_t:
            mask = df_mant_filtrado[col_t[0]].astype(str).str.contains(busqueda_tienda, case=False, na=False)
            df_mant_filtrado = df_mant_filtrado[mask]

    cant_mantenimientos = len(df_mant_filtrado)
    
    c_kpi, _ = st.columns([1, 1])
    with c_kpi:
        render_kpi("🛠️", "Mantenimientos", f"{cant_mantenimientos:,}")
        
    if st.session_state.rol_actual == "admin":
        df_edit_mant = st.data_editor(df_mant_filtrado, num_rows="dynamic", use_container_width=True, key="ed_mant")
        if st.button("💾 Guardar Cambios en Mantenimiento"):
            st.session_state.df_Mantenimiento = df_edit_mant
            guardar_excel(df_edit_mant, "Mantenimiento")
            st.success("✅ Archivo de Mantenimiento guardado.")
            st.rerun()
    else:
        st.dataframe(df_mant_filtrado, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# CAMBIO BATERÍAS
# -------------------------------------------------------------
elif opcion == "🔋 Cambio de baterías":
    st.markdown("## 🔋 Cambios de Baterías")
    
    busqueda_bat = st.text_input("🔍 Buscar", placeholder="Tienda, serie, modelo...")
    df_bat = st.session_state.df_Baterias
    df_bat_filtrado = df_bat.copy()
        
    if busqueda_bat.strip():
        mask = df_bat_filtrado.astype(str).apply(lambda row: row.str.contains(busqueda_bat, case=False, na=False)).any(axis=1)
        df_bat_filtrado = df_bat_filtrado[mask]
        
    col_bat_ant = [c for c in df_bat.columns if ('CANT' in str(c).upper() or 'CANTDAD' in str(c).upper()) and '25' in str(c)]
    col_bat_act = [c for c in df_bat.columns if ('CANT' in str(c).upper() or 'CANTDAD' in str(c).upper()) and '26' in str(c)]

    tot_anterior = int(pd.to_numeric(df_bat[col_bat_ant[0]], errors='coerce').sum()) if col_bat_ant else 0
    tot_actual = int(pd.to_numeric(df_bat[col_bat_act[0]], errors='coerce').sum()) if col_bat_act else 0
    tot_general = tot_anterior + tot_actual
    
    c1, c2, c3 = st.columns(3)
    with c1: render_kpi("🔋", f"Baterías {anio_actual - 1}", f"{tot_anterior:,}")
    with c2: render_kpi("🔋", f"Baterías {anio_actual}", f"{tot_actual:,}")
    with c3: render_kpi("🔋", "Total", f"{tot_general:,}")
    
    if st.session_state.rol_actual == "admin":
        df_edit_bat = st.data_editor(df_bat_filtrado, num_rows="dynamic", use_container_width=True, key="ed_bat")
        if st.button("💾 Guardar Cambios en Baterías"):
            st.session_state.df_Baterias = df_edit_bat
            guardar_excel(df_edit_bat, "Baterias")
            st.success("✅ Archivo de Baterías guardado.")
            st.rerun()
    else:
        st.dataframe(df_bat_filtrado, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# ALQUILER DE UPS
# -------------------------------------------------------------
elif opcion == "🤝 Alquileres":
    st.markdown("## ⏱️ Alquiler de UPS")
    
    busqueda_alq = st.text_input("🔎 Buscar alquiler", placeholder="Cotización o tienda...")
    df_alq = st.session_state.df_Alquiler
    df_alq_filtrado = df_alq.copy()

    if busqueda_alq.strip():
        mask = df_alq_filtrado.astype(str).apply(lambda row: row.str.contains(busqueda_alq, case=False, na=False)).any(axis=1)
        df_alq_filtrado = df_alq_filtrado[mask]

    col_cot = [c for c in df_alq.columns if 'COTIZACION' in str(c).upper()]
    if col_cot:
        df_alq_real = df_alq.dropna(subset=[col_cot[0]])
        df_alq_real = df_alq_real[~df_alq_real[col_cot[0]].astype(str).str.contains('SUB-TOTAL|TOTAL', case=False, na=False)]
    else:
        df_alq_real = df_alq.dropna(how='all')

    tot_alquileres = len(df_alq_real)
    col_dias = [c for c in df_alq_real.columns if 'DIAS' in str(c).upper()]
    tot_dias = int(pd.to_numeric(df_alq_real[col_dias[0]], errors='coerce').sum()) if col_dias else 0
    
    col_costo = [c for c in df_alq_real.columns if 'COSTO TOTAL' in str(c).upper() or 'TOTAL' in str(c).upper()]
    tot_costo = float(pd.to_numeric(df_alq_real[col_costo[0]], errors='coerce').sum()) if col_costo else 0.0

    a1, a2, a3 = st.columns(3)
    with a1: render_kpi("⏱️", "ALQUILERES", f"{tot_alquileres}")
    with a2: render_kpi("📅", "DÍAS ALQUILADOS", f"{tot_dias}")
    with a3: render_kpi("💰", "TOTAL", f"S/ {tot_costo:,.2f}")
    
    if st.session_state.rol_actual == "admin":
        df_edit_alq = st.data_editor(df_alq_filtrado, num_rows="dynamic", use_container_width=True, key="ed_alq")
        if st.button("💾 Guardar Cambios en Alquileres"):
            st.session_state.df_Alquiler = df_edit_alq
            guardar_excel(df_edit_alq, "Alquiler")
            st.success("✅ Archivo de Alquileres guardado.")
            st.rerun()
    else:
        st.dataframe(df_alq_filtrado, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# NUEVO REGISTRO
# -------------------------------------------------------------
elif opcion == "📝 Nuevo Registro" and st.session_state.rol_actual == "admin":
    st.title("📝 Registrar Nuevo Evento TI")
    
    tipo = st.selectbox("Tipo de Evento:", ["Mantenimiento", "Cambio de Batería"])
    df_inv = st.session_state.df_Inventario
    df_mant = st.session_state.df_Mantenimiento
    
    set_tiendas = set()
    for df in [df_inv, df_mant]:
        if not df.empty:
            col_t = [c for c in df.columns if str(c).strip().upper() == 'TIENDA']
            if col_t:
                valores = df[col_t[0]].dropna().astype(str).str.strip().unique()
                for v in valores:
                    if v and v.upper() not in ["NAN", "NONE", "NULL", "TIENDA"]:
                        set_tiendas.add(v)
    
    lista_tiendas = sorted(list(set_tiendas))
    col_a, col_b = st.columns(2)
    
    with col_a:
        if lista_tiendas:
            tienda_sel = st.selectbox("Tienda / Ubicación:", options=[""] + lista_tiendas)
            tienda_manual = st.text_input("O escribe una nueva tienda:")
            tienda_final = tienda_manual.strip() if tienda_manual.strip() else tienda_sel
        else:
            tienda_final = st.text_input("Tienda / Ubicación:")

    modelo_auto = ""
    mant_atencion_auto = ""
    mant_se_encontro_auto = ""
    mant_queda_auto = ""
    mant_carga_auto = ""

    if tienda_final and not df_mant.empty:
        col_t_mant = [c for c in df_mant.columns if str(c).strip().upper() == 'TIENDA']
        if col_t_mant:
            match_mant = df_mant[df_mant[col_t_mant[0]].astype(str).str.strip().str.upper() == tienda_final.upper()]
            if not match_mant.empty:
                ult_reg = match_mant.iloc[-1]
                for col in df_mant.columns:
                    c_up = str(col).strip().upper()
                    if 'MODELO' in c_up and pd.notna(ult_reg[col]): modelo_auto = str(ult_reg[col])
                    elif 'MANT. ATENCION' in c_up or 'ATENCION' in c_up: 
                        if pd.notna(ult_reg[col]): mant_atencion_auto = str(ult_reg[col])
                    elif 'MANT SE ENCONTRO' in c_up or 'ENCONTRO' in c_up: 
                        if pd.notna(ult_reg[col]): mant_se_encontro_auto = str(ult_reg[col])
                    elif 'MANT QUEDA' in c_up or 'QUEDA' in c_up: 
                        if pd.notna(ult_reg[col]): mant_queda_auto = str(ult_reg[col])
                    elif 'MANT CARGA' in c_up or 'CARGA' in c_up: 
                        if pd.notna(ult_reg[col]): mant_carga_auto = str(ult_reg[col])

    with st.form("f_nuevo", clear_on_submit=False):
        f1, f2 = st.columns(2)
        with f1:
            fec = st.date_input("Fecha:", datetime.now())
            mant_atencion = st.text_input("MANT. ATENCION:", value=mant_atencion_auto)
        with f2:
            modelo = st.text_input("Modelo / Serie UPS:", value=modelo_auto)
            mant_se_encontro = st.text_input("MANT SE ENCONTRO:", value=mant_se_encontro_auto)
            mant_queda = st.text_input("MANT QUEDA:", value=mant_queda_auto)
            mant_carga = st.text_input("MANT CARGA:", value=mant_carga_auto)

        if st.form_submit_button("💾 Guardar Registro TI", use_container_width=True):
            if not tienda_final:
                st.warning("⚠️ Selecciona o escribe una tienda antes de guardar.")
            else:
                fec_str = fec.strftime("%Y-%m-%d")
                if tipo == "Mantenimiento":
                    nuevo_registro = {
                        "TIENDA": tienda_final, "MODELO": modelo, "MANT. ATENCION": mant_atencion,
                        "MANT FECHA": fec_str, "MANT SE ENCONTRO": mant_se_encontro,
                        "MANT QUEDA": mant_queda, "MANT CARGA": mant_carga
                    }
                    df_target = st.session_state.df_Mantenimiento
                    col_t_target = [c for c in df_target.columns if str(c).strip().upper() == 'TIENDA']
                    if col_t_target and tienda_final.upper() in df_target[col_t_target[0]].astype(str).str.strip().str.upper().values:
                        idx = df_target[df_target[col_t_target[0]].astype(str).str.strip().str.upper() == tienda_final.upper()].index[0]
                        for k, v in nuevo_registro.items():
                            if k in df_target.columns: df_target.at[idx, k] = v
                        st.session_state.df_Mantenimiento = df_target
                    else:
                        df_nuevo = pd.DataFrame([nuevo_registro])
                        st.session_state.df_Mantenimiento = pd.concat([df_target, df_nuevo], ignore_index=True)
                    
                    guardar_excel(st.session_state.df_Mantenimiento, "Mantenimiento")
                    st.success("✅ Mantenimiento registrado y guardado correctamente.")

# -------------------------------------------------------------
# EXPORTAR DATOS
# -------------------------------------------------------------
elif opcion == "📥 Exportar datos" and st.session_state.rol_actual in ["admin", "visor_exportador"]:
    st.title("📥 Exportación de Reportes TI")
    
    modulo_exp = st.selectbox("Selecciona el módulo a exportar:", ["Inventario", "Mantenimiento", "Baterias", "Alquiler"])
    df_a_exportar = st.session_state.get(f"df_{modulo_exp}", pd.DataFrame())
    
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        if not df_a_exportar.empty:
            excel_bytes = exportar_excel(df_a_exportar)
            st.download_button(
                label="📥 Descargar en Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"Reporte_{modulo_exp}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("No hay datos disponibles para exportar en este módulo.")
            
    with col_ex2:
        if not df_a_exportar.empty:
            pdf_bytes = generar_pdf(f"Reporte de {modulo_exp}", df_a_exportar)
            st.download_button(
                label="📄 Descargar en PDF (.pdf)",
                data=pdf_bytes,
                file_name=f"Reporte_{modulo_exp}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
