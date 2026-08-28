import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import os
import glob
import time
import plotly.express as px

# Importaciones de ReportLab para generación de PDFs
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuración de página con temática de Sistemas TI
st.set_page_config(
    page_title="Sistema de Gestión TI - UPS",
    page_icon="💻",
    layout="wide"
)

# Menú lateral - Selección de tema
if "tema_actual" not in st.session_state:
    st.session_state.tema_actual = "Claro"

# Estilos CSS dinámicos (Modo Claro vs Modo Oscuro) con soporte global y corrección de inputs/botones
def aplicar_estilos(tema):
    if tema == "Oscuro":
        bg_main = "#0F172A"
        bg_card = "#1E293B"
        border_color = "#334155"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        status_bg = "#064E3B"
        status_text = "#6EE7B7"
        status_border = "#065F46"
        summary_val_color = "#38BDF8"
        input_bg = "#334155"
        btn_bg = "#334155"
    else:
        bg_main = "#F8FAFC"
        bg_card = "#FFFFFF"
        border_color = "#E2E8F0"
        text_primary = "#0F172A"
        text_secondary = "#64748B"
        status_bg = "#F0FDF4"
        status_text = "#166534"
        status_border = "#BBF7D0"
        summary_val_color = "#0284C7"
        input_bg = "#FFFFFF"
        btn_bg = "#FFFFFF"

    css = f"""
        <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        .stApp {{
            background-color: {bg_main} !important;
            color: {text_primary} !important;
        }}
        
        /* Forzar visibilidad global de textos en modo oscuro */
        h1, h2, h3, h4, h5, h6, span, p, label, 
        .stMarkdown, div[data-testid="stMarkdownContainer"], 
        div[data-testid="stText"], .stMetricLabel, .stMetricValue, .stCaption {{
            color: {text_primary} !important;
        }}

        /* Corrección visibilidad de Selectbox y Inputs en Modo Oscuro */
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] {{
            background-color: {input_bg} !important;
            color: {text_primary} !important;
        }}
        div[data-baseweb="select"] span, div[data-baseweb="select"] option, div[data-baseweb="select"] div {{
            color: {text_primary} !important;
        }}
        div[data-baseweb="popover"] div, div[data-baseweb="menu"] div {{
            background-color: {bg_card} !important;
            color: {text_primary} !important;
        }}

        /* Botones generales, de descarga y de envío de formularios */
        .stButton > button, div.stButton > button, button[kind="secondary"], 
        div[data-testid="stDownloadButton"] > button, .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button {{
            background-color: {btn_bg} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            opacity: 1 !important;
        }}
        .stButton > button *, .stDownloadButton > button *, div[data-testid="stFormSubmitButton"] > button * {{
            color: {text_primary} !important;
            opacity: 1 !important;
        }}
        .stButton > button:hover, .stButton > button:hover *, 
        .stDownloadButton > button:hover, .stDownloadButton > button:hover *,
        div[data-testid="stFormSubmitButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover * {{
            border-color: {summary_val_color} !important;
            color: {summary_val_color} !important;
        }}

        .main-header {{
            background-color: {bg_card};
            padding: 20px 24px;
            border-radius: 12px;
            border: 1px solid {border_color};
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .main-header h1 {{
            font-size: 1.6rem !important;
            font-weight: 800;
            color: {text_primary};
            margin: 0;
        }}
        .main-header p {{
            color: {text_secondary};
            margin: 4px 0 8px 0;
            font-size: 0.9rem;
        }}
        .status-badge {{
            display: inline-flex;
            align-items: center;
            background-color: {status_bg};
            color: {status_text};
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
            border: 1px solid {status_border};
        }}

        .kpi-card {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        .kpi-header {{
            font-size: 0.75rem;
            font-weight: 700;
            color: {text_secondary};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        .kpi-value {{
            font-size: 1.75rem;
            font-weight: 800;
            color: {text_primary};
            line-height: 1.1;
        }}

        .summary-card {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }}
        .summary-title {{
            font-size: 0.85rem;
            font-weight: 700;
            color: {text_primary};
        }}
        .summary-val {{
            font-size: 1.3rem;
            font-weight: 800;
            color: {summary_val_color};
            margin: 4px 0;
        }}
        .summary-sub {{
            font-size: 0.78rem;
            color: {text_secondary};
        }}

        .status-item {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 8px;
            font-size: 0.88rem;
            font-weight: 600;
            color: {text_primary};
        }}
        .check-icon {{
            color: #16A34A;
            font-weight: bold;
            margin-right: 8px;
        }}
        
        /* Ajustes barra lateral */
        section[data-testid="stSidebar"] {{
            background-color: {bg_card} !important;
            border-right: 1px solid {border_color};
        }}
        section[data-testid="stSidebar"] * {{
            color: {text_primary} !important;
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Buscar archivos Excel automáticamente
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
        'T', parent=estilos['Heading1'], fontSize=12, textColor=colors.HexColor('#0F172A'), alignment=1
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
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#CBD5E1')),
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

# Menú lateral
st.sidebar.title("💻 Gestión de Infraestructura TI")
st.sidebar.caption(f"👤 **{st.session_state.usuario_actual}**")

# Selector de Tema
tema_sel = st.sidebar.selectbox("🎨 Modo de Color", ["Claro", "Oscuro"], index=0 if st.session_state.tema_actual == "Claro" else 1)
if tema_sel != st.session_state.tema_actual:
    st.session_state.tema_actual = tema_sel
    st.rerun()

aplicar_estilos(st.session_state.tema_actual)

menu = ["📊 Panel de control", "📦 Inventario UPS", "🛠️ Mantenimientos", "🔋 Cambio de baterías", "🤝 Alquileres"]

if st.session_state.rol_actual == "admin":
    menu.insert(3, "📝 Nuevo Registro")

if st.session_state.rol_actual in ["admin", "visor_exportador"]:
    menu.append("📥 Exportar datos")

opcion = st.sidebar.radio("Seleccionar módulo:", menu)

if st.sidebar.button("🚪 Cerrar Sesión"):
    logout()

# Cabecera superior común con hora automática (Detecta Local vs Streamlit Cloud)
if "HOSTNAME" in os.environ or time.daylight == 0:
    fecha_actual_str = (datetime.utcnow() - timedelta(hours=5)).strftime("%d/%m/%Y %H:%M")
else:
    fecha_actual_str = datetime.now().strftime("%d/%m/%Y %H:%M")

st.markdown(f"""
    <div class="main-header">
        <h1>💻 Sistemas TI - Control de UPS</h1>
        <p>Plataforma centralizada de infraestructura para el control de inventario, mantenimiento, baterías y alquileres.</p>
        <div class="status-badge">🟢 Servidor TI Activo • Actualizado {fecha_actual_str}</div>
    </div>
""", unsafe_allow_html=True)

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
    val_mant_2026 = 0
    if not df_mant.empty:
        col_mant_f = [c for c in df_mant.columns if "FECHA" in str(c).upper()]
        if col_mant_f:
            val_mant_total = int(df_mant[col_mant_f[0]].notna().sum())
            val_mant_2026 = val_mant_total
        else:
            val_mant_total = len(df_mant)
            val_mant_2026 = len(df_mant)

    val_bat_2025 = 0
    val_bat_2026 = 0
    val_bat_total = 0
    if not df_bat.empty:
        col_bat_26 = [c for c in df_bat.columns if 'CANT' in str(c).upper() and '26' in str(c)]
        col_bat_25 = [c for c in df_bat.columns if 'CANT' in str(c).upper() and '25' in str(c)]
        
        if col_bat_25:
            val_bat_2025 = int(pd.to_numeric(df_bat[col_bat_25[0]], errors='coerce').sum())
        if col_bat_26:
            val_bat_2026 = int(pd.to_numeric(df_bat[col_bat_26[0]], errors='coerce').sum())
            
        val_bat_total = val_bat_2025 + val_bat_2026

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
    with k7: render_kpi("🛠️", "MANTENIMIENTOS 2026", f"{val_mant_2026:,}")
    with k8: render_kpi("🔋", "BATERÍAS 2026", f"{val_bat_2026:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_graficos, col_resumen = st.columns([2.2, 1])

    is_dark = st.session_state.tema_actual == "Oscuro"
    theme_bg = "rgba(0,0,0,0)"
    font_color = "#F8FAFC" if is_dark else "#0F172A"

    with col_graficos:
        st.markdown("### 📅 Comparativo por año")
        
        data_bat = pd.DataFrame({
            "Año": ["2025", "2026"],
            "Cantidad": [val_bat_2025, val_bat_2026]
        })
        fig_bat = px.bar(
            data_bat, x="Cantidad", y="Año", orientation='h', text="Cantidad",
            title="🔋 Cambios de baterías", color_discrete_sequence=['#38BDF8' if is_dark else '#0EA5E9']
        )
        fig_bat.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor=theme_bg, paper_bgcolor=theme_bg, font_color=font_color)
        st.plotly_chart(fig_bat, use_container_width=True)

        data_mant = pd.DataFrame({
            "Año": ["2025", "2026"],
            "Cantidad": [0, val_mant_2026]
        })
        fig_mant = px.bar(
            data_mant, x="Año", y="Cantidad", text="Cantidad",
            title="🛠️ Mantenimientos", color_discrete_sequence=['#38BDF8' if is_dark else '#0EA5E9']
        )
        fig_mant.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor=theme_bg, paper_bgcolor=theme_bg, font_color=font_color)
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
                <div class="summary-title">🔋 Baterías 2026</div>
                <div class="summary-val">{val_bat_2026:,}</div>
                <div class="summary-sub">Baterías cambiadas durante 2026.</div>
            </div>

            <div class="summary-card">
                <div class="summary-title">💰 Alquileres</div>
                <div class="summary-val">S/ {val_ingresos_alq:,.2f}</div>
                <div class="summary-sub">Monto acumulado real de alquileres.</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📁 Estado de módulos")
        st.markdown("""
            <div class="status-item"><span class="check-icon">✓</span> Inventario</div>
            <div class="status-item"><span class="check-icon">✓</span> Mantenimiento</div>
            <div class="status-item"><span class="check-icon">✓</span> Baterías</div>
            <div class="status-item"><span class="check-icon">✓</span> Alquileres</div>
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
        
    st.caption(f"Registros mostrados: {cant_mantenimientos}")
    
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
        
    col_bat_25 = [c for c in df_bat.columns if 'CANT' in str(c).upper() and '25' in str(c)]
    col_bat_26 = [c for c in df_bat.columns if 'CANT' in str(c).upper() and '26' in str(c)]

    tot_2025 = int(pd.to_numeric(df_bat[col_bat_25[0]], errors='coerce').sum()) if col_bat_25 else 0
    tot_2026 = int(pd.to_numeric(df_bat[col_bat_26[0]], errors='coerce').sum()) if col_bat_26 else 0
    tot_general = tot_2025 + tot_2026
    
    c1, c2, c3 = st.columns(3)
    with c1: render_kpi("🔋", "Baterías 2025", f"{tot_2025:,}")
    with c2: render_kpi("🔋", "Baterías 2026", f"{tot_2026:,}")
    with c3: render_kpi("🔋", "Total", f"{tot_general:,}")
    
    st.caption(f"Registros mostrados: {len(df_bat_filtrado)}")
    
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
    
    st.caption(f"Registros mostrados: {len(df_alq_filtrado)}")

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
            tienda_manual = st.text_input("O escribe una nueva tienda (si no está en la lista):")
            tienda_final = tienda_manual.strip() if tienda_manual.strip() else tienda_sel
        else:
            tienda_final = st.text_input("Tienda / Ubicación:")

    modelo_auto = ""
    mant_atencion_auto = ""
    mant_se_encontro_auto = ""
    mant_queda_auto = ""
    mant_carga_auto = ""

    if tienda_final:
        if not df_mant.empty:
            col_t_mant = [c for c in df_mant.columns if str(c).strip().upper() == 'TIENDA']
            if col_t_mant:
                match_mant = df_mant[df_mant[col_t_mant[0]].astype(str).str.strip().str.upper() == tienda_final.upper()]
                if not match_mant.empty:
                    ult_reg = match_mant.iloc[-1]
                    
                    for col in df_mant.columns:
                        c_up = str(col).strip().upper()
                        if 'MODELO' in c_up and pd.notna(ult_reg[col]):
                            modelo_auto = str(ult_reg[col])
                        elif 'MANT. ATENCION' in c_up or 'ATENCION' in c_up:
                            if pd.notna(ult_reg[col]): mant_atencion_auto = str(ult_reg[col])
                        elif 'MANT SE ENCONTRO' in c_up or 'ENCONTRO' in c_up:
                            if pd.notna(ult_reg[col]): mant_se_encontro_auto = str(ult_reg[col])
                        elif 'MANT QUEDA' in c_up or 'QUEDA' in c_up:
                            if pd.notna(ult_reg[col]): mant_queda_auto = str(ult_reg[col])
                        elif 'MANT CARGA' in c_up or 'CARGA' in c_up:
                            if pd.notna(ult_reg[col]): mant_carga_auto = str(ult_reg[col])

        if not modelo_auto and not df_inv.empty:
            col_t_inv = [c for c in df_inv.columns if str(c).strip().upper() == 'TIENDA']
            if col_t_inv:
                match_inv = df_inv[df_inv[col_t_inv[0]].astype(str).str.strip().str.upper() == tienda_final.upper()]
                if not match_inv.empty:
                    col_m = [c for c in df_inv.columns if 'MODELO' in str(c).strip().upper()]
                    if col_m and pd.notna(match_inv.iloc[0][col_m[0]]):
                        modelo_auto = str(match_inv.iloc[0][col_m[0]])

    with st.form("f_nuevo", clear_on_submit=False):
        f1, f2 = st.columns(2)
        
        with f1:
            fec = st.date_input("Fecha:", datetime.now())
            mant_atencion = st.text_input("MANT. ATENCION (Técnico / Atención):", value=mant_atencion_auto)

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
                        "TIENDA": tienda_final,
                        "MODELO": modelo,
                        "MANT. ATENCION": mant_atencion,
                        "MANT FECHA": fec_str,
                        "MANT SE ENCONTRO": mant_se_encontro,
                        "MANT QUEDA": mant_queda,
                        "MANT CARGA": mant_carga
                    }
                    
                    df_target = st.session_state.df_Mantenimiento
                    col_t_target = [c for c in df_target.columns if str(c).strip().upper() == 'TIENDA']
                    
                    if col_t_target and tienda_final.upper() in df_target[col_t_target[0]].astype(str).str.strip().str.upper().values:
                        idx = df_target[df_target[col_t_target[0]].astype(str).str.strip().str.upper() == tienda_final.upper()].index[0]
                        for k, v in nuevo_registro.items():
                            if k in df_target.columns:
                                df_target.at[idx, k] = v
                        st.session_state.df_Mantenimiento = df_target
                    else:
                        st.session_state.df_Mantenimiento = pd.concat([df_target, pd.DataFrame([nuevo_registro])], ignore_index=True)
                    
                    guardar_excel(st.session_state.df_Mantenimiento, "Mantenimiento")
                    st.success(f"✅ Mantenimiento guardado para '{tienda_final}'.")
                    st.rerun()

                else:
                    nuevo_bat = {
                        "TIENDA": tienda_final,
                        "MODELO": modelo,
                        "FECHA": fec_str,
                        "ATENCION": mant_atencion,
                        "OBSERVACION": f"Encontró: {mant_se_encontro} | Queda: {mant_queda} | Carga: {mant_carga}"
                    }
                    st.session_state.df_Baterias = pd.concat([st.session_state.df_Baterias, pd.DataFrame([nuevo_bat])], ignore_index=True)
                    guardar_excel(st.session_state.df_Baterias, "Baterias")
                    st.success(f"✅ Cambio de batería guardado para '{tienda_final}'.")
                    st.rerun()

# -------------------------------------------------------------
# EXPORTAR DATOS
# -------------------------------------------------------------
elif opcion == "📥 Exportar datos" and st.session_state.rol_actual in ["admin", "visor_exportador"]:
    
    col_tit, col_anio, col_btn_xl, col_btn_pdf = st.columns([2.2, 1.2, 1, 1])
    
    with col_tit:
        st.markdown("## 📥 Exportar informes TI")
    
    with col_anio:
        anio_filtro = st.selectbox("📅 Filtrar por Año:", ["Todos", "2026", "2025"])

    col_mod, _ = st.columns([2, 2])
    with col_mod:
        sel = st.selectbox("Seleccionar Módulo:", list(PATRONES.keys()))

    df_exp = st.session_state[f"df_{sel}"].copy()

    if anio_filtro != "Todos" and not df_exp.empty:
        if sel == "Baterias":
            col_cant_26 = [c for c in df_exp.columns if 'CANT' in str(c).upper() and '26' in str(c)]
            col_fec_26 = [c for c in df_exp.columns if 'FECHA' in str(c).upper() and '26' in str(c)]
            col_cant_25 = [c for c in df_exp.columns if 'CANT' in str(c).upper() and '25' in str(c)]
            col_fec_25 = [c for c in df_exp.columns if 'FECHA' in str(c).upper() and '25' in str(c)]

            if anio_filtro == "2026":
                cond = pd.Series(False, index=df_exp.index)
                if col_cant_26: cond |= pd.to_numeric(df_exp[col_cant_26[0]], errors='coerce').fillna(0) > 0
                if col_fec_26: cond |= df_exp[col_fec_26[0]].notna()
                df_exp = df_exp[cond]
            elif anio_filtro == "2025":
                cond = pd.Series(False, index=df_exp.index)
                if col_cant_25: cond |= pd.to_numeric(df_exp[col_cant_25[0]], errors='coerce').fillna(0) > 0
                if col_fec_25: cond |= df_exp[col_fec_25[0]].notna()
                df_exp = df_exp[cond]

        elif sel == "Mantenimiento":
            col_f = [c for c in df_exp.columns if "FECHA" in str(c).upper()]
            if col_f:
                df_exp = df_exp[pd.to_datetime(df_exp[col_f[0]], errors='coerce').dt.year == int(anio_filtro)]

        elif sel == "Alquiler":
            col_a = [c for c in df_exp.columns if "AÑO" in str(c).upper()]
            if col_a:
                df_exp = df_exp[pd.to_numeric(df_exp[col_a[0]], errors='coerce') == int(anio_filtro)]

    with col_btn_xl:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "📊 Excel", 
            exportar_excel(df_exp), 
            f"Reporte_TI_{sel}_{anio_filtro}.xlsx", 
            use_container_width=True
        )
    
    with col_btn_pdf:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.download_button(
            "📄 PDF", 
            generar_pdf(f"Reporte TI - {sel} ({anio_filtro})", df_exp), 
            f"Reporte_TI_{sel}_{anio_filtro}.pdf", 
            mime="application/pdf", 
            use_container_width=True
        )

    st.caption(f"Registros a exportar: {len(df_exp)}")
    st.dataframe(df_exp, use_container_width=True, hide_index=True)
