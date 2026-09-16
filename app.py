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
        
        div.stMarkdown {{
            margin-bottom: -10px !important;
        }}
        
        div[data-testid="stVerticalBlock"] {{
            gap: 0.4rem !important;
        }}

        h1, h2, h3, h4, h5, h6, span, p, label, 
        .stMarkdown, div[data-testid="stMarkdownContainer"], 
        div[data-testid="stText"], .stMetricLabel, .stMetricValue, .stCaption {{
            color: {TEXT_PRIMARY} !important;
        }}

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

    st.markdown("---")

    # Layout de Gráficos y Panel lateral de Resumen Ejecutivo
    col_graficos, col_resumen = st.columns([2.2, 1])

    with col_graficos:
        st.markdown("### 📅 Comparativo por año")
        
        # Gráfico Baterías
        st.markdown("##### 🔋 Cambios de baterías")
        df_chart_bat = pd.DataFrame({
            "Año": [str(anio_actual - 1), str(anio_actual)],
            "Cantidad": [val_bat_anterior, val_bat_actual]
        })
        fig_bat = px.bar(
            df_chart_bat, x="Cantidad", y="Año", orientation='h',
            text="Cantidad", color="Año",
            color_discrete_map={str(anio_actual - 1): "#1F6FEB", str(anio_actual): "#388BFd"}
        )
        fig_bat.update_layout(
            paper_bgcolor=BG_CARD, plot_bgcolor=BG_CARD,
            font=dict(color=TEXT_PRIMARY),
            margin=dict(l=10, r=10, t=10, b=10),
            height=200,
            xaxis=dict(showgrid=True, gridcolor=BORDER_COLOR),
            yaxis=dict(showgrid=False),
            showlegend=False
        )
        fig_bat.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_bat, use_container_width=True)

        # Gráfico Mantenimientos
        st.markdown("##### 🛠️ Mantenimientos")
        val_mant_anterior = val_mant_total - val_mant_actual
        df_chart_mant = pd.DataFrame({
            "Año": [str(anio_actual - 1), str(anio_actual)],
            "Cantidad": [val_mant_anterior, val_mant_actual]
        })
        fig_mant = px.bar(
            df_chart_mant, x="Año", y="Cantidad",
            text="Cantidad", color="Año",
            color_discrete_map={str(anio_actual - 1): "#1F6FEB", str(anio_actual): "#388BFd"}
        )
        fig_mant.update_layout(
            paper_bgcolor=BG_CARD, plot_bgcolor=BG_CARD,
            font=dict(color=TEXT_PRIMARY),
            margin=dict(l=10, r=10, t=10, b=10),
            height=220,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=BORDER_COLOR),
            showlegend=False
        )
        fig_mant.update_traces(textfont_size=12, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_mant, use_container_width=True)

    with col_resumen:
        st.markdown("### 📌 Resumen ejecutivo")
        
        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <div class="kpi-header">📦 Inventario actual</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: {SUMMARY_VAL_COLOR};">{val_inv:,} UPS</div>
            <div style="font-size: 0.75rem; color: {TEXT_SECONDARY}; margin-top: 2px;">Equipos registrados en el inventario.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <div class="kpi-header">🔋 Baterías {anio_actual}</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: {SUMMARY_VAL_COLOR};">{val_bat_actual:,}</div>
            <div style="font-size: 0.75rem; color: {TEXT_SECONDARY}; margin-top: 2px;">Baterías cambiadas durante {anio_actual}.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-card" style="margin-bottom: 12px;">
            <div class="kpi-header">💰 Alquileres</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: {SUMMARY_VAL_COLOR};">S/ {val_ingresos_alq:,.2f}</div>
            <div style="font-size: 0.75rem; color: {TEXT_SECONDARY}; margin-top: 2px;">Monto acumulado real de alquileres.</div>
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
    
    df_mant = st.session_state.df_Mantenimiento.copy()
    
    anos_disponibles = ["Todos"]
    col_mant_f = [c for c in df_mant.columns if "FECHA" in str(c).upper()]
    if col_mant_f:
        anos_encontrados = pd.to_datetime(df_mant[col_mant_f[0]], errors='coerce').dt.year.dropna().unique()
        anos_disponibles.extend(sorted([int(a) for a in anos_encontrados], reverse=True))

    col_filtro_ano, col_busqueda_t = st.columns([1.5, 2.5])
    with col_filtro_ano:
        anio_seleccionado = st.selectbox("📅 Filtrar por Año:", options=anos_disponibles)
    with col_busqueda_t:
        busqueda_tienda = st.text_input("🔎 Buscar tienda", placeholder="Nombre de tienda...")

    df_mant_filtrado = df_mant.copy()

    if anio_seleccionado != "Todos" and col_mant_f:
        anos_fila = pd.to_datetime(df_mant_filtrado[col_mant_f[0]], errors='coerce').dt.year
        df_mant_filtrado = df_mant_filtrado[anos_fila == anio_seleccionado]

    if busqueda_tienda.strip():
        mask = df_mant_filtrado.astype(str).apply(lambda row: row.str.contains(busqueda_tienda, case=False, na=False)).any(axis=1)
        df_mant_filtrado = df_mant_filtrado[mask]

    cant_mantenimientos = len(df_mant_filtrado)
    
    c_kpi, _ = st.columns([1, 2])
    with c_kpi:
        render_kpi("🛠️", f"Mantenimientos ({anio_seleccionado})", f"{cant_mantenimientos:,}")
        
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
    
    df_bat = st.session_state.df_Baterias
    df_bat_filtrado = df_bat.copy()

    anos_bat_opciones = ["Todos"]
    for col in df_bat.columns:
        c_str = str(col)
        for anio_prueba in range(2020, 2035):
            if str(anio_prueba) in c_str or str(anio_prueba)[-2:] in c_str:
                if anio_prueba not in [int(x) for x in anos_bat_opciones if x != "Todos"]:
                    anos_bat_opciones.append(anio_prueba)

    if len(anos_bat_opciones) == 1:
        anos_bat_opciones.extend([2025, 2026])

    col_f_bateria, col_busqueda_bat = st.columns([1.5, 2.5])
    with col_f_bateria:
        anio_sel_bat = st.selectbox("📅 Filtrar Año Baterías:", options=anos_bat_opciones, key="filtro_anio_bat")
    with col_busqueda_bat:
        busqueda_bat = st.text_input("🔍 Buscar", placeholder="Tienda, serie, modelo...", key="busqueda_baterias_txt")

    if anio_sel_bat != "Todos":
        cols_a_mantener = []
        for col in df_bat.columns:
            c_upper = str(col).upper()
            if any(k in c_upper for k in ['TIENDA', 'ITEM', 'MARCA', 'MODELO', 'SERIE', 'RAZON']):
                cols_a_mantener.append(col)
            elif str(anio_sel_bat) in str(col) or str(anio_sel_bat)[-2:] in str(col):
                cols_a_mantener.append(col)
        if cols_a_mantener:
            df_bat_filtrado = df_bat[cols_a_mantener]

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
    with c3: render_kpi("🔋", "Total Acumulado", f"{tot_general:,}")
    
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
    st.markdown("## 📝 Registrar Nuevo Evento TI")
    st.caption("Agrega un nuevo registro directamente a cualquiera de los módulos principales.")

    tipo_reg = st.selectbox("Seleccione el módulo donde desea agregar el registro:", ["Inventario UPS", "Mantenimientos", "Cambio de baterías", "Alquileres"])

    if tipo_reg == "Inventario UPS":
        df_actual = st.session_state.df_Inventario
        clave_reg = "Inventario"
    elif tipo_reg == "Mantenimientos":
        df_actual = st.session_state.df_Mantenimiento
        clave_reg = "Mantenimiento"
    elif tipo_reg == "Cambio de baterías":
        df_actual = st.session_state.df_Baterias
        clave_reg = "Baterias"
    else:
        df_actual = st.session_state.df_Alquiler
        clave_reg = "Alquiler"

    st.markdown("### Ingrese los datos del nuevo registro:")
    with st.form("form_nuevo_registro"):
        nuevos_datos = {}
        cols = list(df_actual.columns)
        
        for i in range(0, len(cols), 2):
            c1, c2 = st.columns(2)
            with c1:
                col_name = cols[i]
                nuevos_datos[col_name] = st.text_input(f"{col_name}")
            with c2:
                if i + 1 < len(cols):
                    col_name_2 = cols[i + 1]
                    nuevos_datos[col_name_2] = st.text_input(f"{col_name_2}")

        submitted = st.form_submit_button("➕ Agregar y Guardar en Excel", use_container_width=True)
        if submitted:
            nueva_fila = pd.DataFrame([nuevos_datos])
            df_actualizado = pd.concat([df_actual, nueva_fila], ignore_index=True)
            st.session_state[f"df_{clave_reg}"] = df_actualizado
            guardar_excel(df_actualizado, clave_reg)
            st.success(f"✅ ¡Nuevo registro agregado con éxito en {tipo_reg}!")

# -------------------------------------------------------------
# EXPORTAR DATOS
# -------------------------------------------------------------
elif opcion == "📥 Exportar datos" and st.session_state.rol_actual in ["admin", "visor_exportador"]:
    st.markdown("## 📥 Exportar Módulos del Sistema")
    st.caption("Descarga la información consolidada en formato Excel.")

    mod_exp = st.selectbox("Seleccione el módulo a exportar:", ["Inventario UPS", "Mantenimiento", "Cambio de baterías", "Alquiler"])
    
    if mod_exp == "Inventario UPS":
        df_exp = st.session_state.df_Inventario
        nombre_file = "Inventario_UPS.xlsx"
    elif mod_exp == "Mantenimiento":
        df_exp = st.session_state.df_Mantenimiento
        nombre_file = "Mantenimiento_UPS.xlsx"
    elif mod_exp == "Cambio de baterías":
        df_exp = st.session_state.df_Baterias
        nombre_file = "Cambios_Baterias.xlsx"
    else:
        df_exp = st.session_state.df_Alquiler
        nombre_file = "alquiler_de_UPS.xlsx"

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exp.to_excel(writer, index=False)
    buffer.seek(0)

    st.download_button(
        label=f"📥 Descargar {mod_exp} en Excel",
        data=buffer,
        file_name=nombre_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
