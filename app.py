from datetime import datetime
from io import BytesIO
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
import streamlit as st

st.set_page_config(
    page_title="Sistema de Gestión de UPS", page_icon="⚡", layout="wide"
)

# ==========================================
# ESTILOS CSS RESPONSIVOS PARA ADAPTARSE A PANTALLAS
# ==========================================
st.markdown(
    """
    <style>
    /* Ocupar todo el ancho disponible y ajustar márgenes fluidos */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100% !important;
    }
    /* Tarjetas métricas y contenedores responsivos */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Tablas y DataFrames responsivos */
    div[data-testid="stDataFrame"] {
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# CONFIGURACIÓN DE ACCESO Y CREDENCIALES
# ==========================================
USUARIOS_VALIDOS = {
    "admin": "admin2026",
    "supervisor": "ups2026",
    "operador": "123456",
}

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = ""


def mostrar_login():
  st.markdown("<br><br>", unsafe_allow_html=True, help=None)
  col1, col2, col3 = st.columns([1, 1.2, 1])

  with col2:
    with st.container(border=True):
      st.markdown(
          "<h2 style='text-align: center;'>🔐 Control de Acceso</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p"
          " style='text-align: center; color: gray;'>Ingrese sus"
          " credenciales para continuar</p>",
          unsafe_allow_html=True,
      )

      with st.form("form_login"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button(
            "Iniciar Sesión", use_container_width=True
        )

        if submit:
          if (
              usuario in USUARIOS_VALIDOS
              and USUARIOS_VALIDOS[usuario] == password
          ):
            st.session_state.autenticado = True
            st.session_state.usuario_actual = usuario
            st.success("¡Acceso concedido! Redirigiendo...")
            st.rerun()
          else:
            st.error("Usuario o contraseña incorrectos.")


if not st.session_state.autenticado:
  mostrar_login()
  st.stop()


# ==========================================
# APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================

st.title("⚡ Plataforma de Control y Gestión de UPS")
st.markdown(
    "Panel de control centralizado avanzado para la administración de activos,"
    " inventario, mantenimientos y baterías."
)


# Función para cargar Excel, limpiar columnas duplicadas, sin nombre y vacías base
def cargar_excel(nombre_archivo):
  try:
    df = pd.read_excel(nombre_archivo)
    df.columns = df.columns.str.strip()
    df = df.dropna(axis=1, how="all")
    df = df.loc[
        :,
        ~df.columns.str.contains(
            r"^(Unnamed|Sin nombre)", case=False, na=False
        ),
    ]

    if df.columns.duplicated().any():
      cols = pd.Series(df.columns)
      for dup in cols[cols.duplicated()].unique():
        cols[cols == dup] = [
            f"{dup}_{i}" if i != 0 else dup
            for i in range(sum(cols == dup))
        ]
      df.columns = cols
    return df
  except FileNotFoundError:
    return None


# Función para guardar datos nuevos en el Excel respectivo
def guardar_en_excel(nombre_archivo, nuevo_registro):
  try:
    df_actual = cargar_excel(nombre_archivo)
    if df_actual is not None:
      df_nuevo = pd.DataFrame([nuevo_registro])
      for col in df_actual.columns:
        if col not in df_nuevo.columns:
          df_nuevo[col] = None
      df_nuevo = df_nuevo[df_actual.columns]
      df_concatenado = pd.concat([df_actual, df_nuevo], ignore_index=True)
      df_concatenado.to_excel(nombre_archivo, index=False)
      return True
  except Exception as e:
    st.error(f"Error al guardar el registro: {e}")
  return False


# Función para obtener métricas de Mantenimiento 2026
def obtener_metricas_mantenimiento_2026(df):
  if df is None or df.empty:
    return 0, 0

  df_temp = df.copy()
  df_temp.columns = df_temp.columns.str.strip()

  if "MANT FECHA" in df_temp.columns and "MANT. ATENCION" in df_temp.columns:
    df_2026 = df_temp[
        df_temp["MANT FECHA"].notna() | (df_temp["MANT. ATENCION"] == 1.0)
    ]
    cant_tiendas = (
        df_2026["TIENDA"].dropna().nunique()
        if "TIENDA" in df_2026.columns
        else len(df_2026)
    )
    return int(cant_tiendas), int(len(df_2026))

  return len(df_temp), len(df_temp)


# Función para métricas de Baterías 2026
def obtener_metricas_baterias_2026(df):
  if df is None or df.empty:
    return 0, 0

  df_temp = df.copy()
  df_temp.columns = df_temp.columns.str.strip()

  if "CANTIDAD 2026" in df_temp.columns and "FECHA 2026" in df_temp.columns:
    df_2026 = df_temp[
        df_temp["CANTIDAD 2026"].notna() & (df_temp["CANTIDAD 2026"] > 0)
    ]
    cant_tiendas = (
        df_2026["TIENDA"].dropna().nunique()
        if "TIENDA" in df_2026.columns
        else len(df_2026)
    )
    total_baterias = int(
        pd.to_numeric(df_2026["CANTIDAD 2026"], errors="coerce").sum()
    )
    return int(cant_tiendas), int(total_baterias)

  cant_tiendas = 0
  cols_tienda = [c for c in df_temp.columns if "TIENDA" in c.upper()]
  if cols_tienda:
    cant_tiendas = df_temp[cols_tienda[0]].dropna().nunique()

  total_baterias = 0
  cols_cant = [c for c in df_temp.columns if "CANTIDAD 2026" in c.upper()]
  if cols_cant:
    total_baterias = int(
        pd.to_numeric(df_temp[cols_cant[0]], errors="coerce").sum()
    )

  return int(cant_tiendas), int(total_baterias)


# Función para métricas de Equipos Alquilados
def obtener_metricas_alquiler(df):
  if df is None or df.empty:
    return 0, 0

  df_temp = df.copy()
  df_temp.columns = df_temp.columns.str.strip()

  cant_tiendas = (
      df_temp["TIENDA"].dropna().nunique()
      if "TIENDA" in df_temp.columns
      else len(df_temp)
  )
  cols_dias = [
      c
      for c in df_temp.columns
      if any(
          k in c.upper()
          for k in ["DIA", "CANTIDAD", "TOTAL", "PLAZO", "TIEMPO"]
      )
  ]
  total_dias = 0
  if cols_dias:
    total_dias = int(
        pd.to_numeric(df_temp[cols_dias[0]], errors="coerce").sum()
    )
  else:
    total_dias = len(df_temp)

  return int(cant_tiendas), int(total_dias)


# Cargar los datasets principales
df_inventario = cargar_excel("Inventario_UPS_2026.xlsx")
df_mantenimiento = cargar_excel("Mantenimiento_UPS_2026.xlsx")
df_baterias = cargar_excel("Cambios_Baterias_UPS_2026.xlsx")
df_alquiler = cargar_excel("alquiler_de_UPS.xlsx")

# Conteos seguros
c_inv = len(df_inventario) if df_inventario is not None else 0
tiendas_mant_2026, total_mant_2026 = obtener_metricas_mantenimiento_2026(
    df_mantenimiento
)
tiendas_bat_2026, total_bat_2026 = obtener_metricas_baterias_2026(df_baterias)
c_bat = len(df_baterias) if df_baterias is not None else 0
tiendas_alq, dias_alq = obtener_metricas_alquiler(df_alquiler)

# Menú lateral principal
st.sidebar.markdown(
    f"👤 **Usuario:** `{st.session_state.usuario_actual.capitalize()}`"
)
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
  st.session_state.autenticado = False
  st.session_state.usuario_actual = ""
  st.rerun()

st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Navegación",
    [
        "🏠 Resumen General",
        f"📦 Inventario UPS ({c_inv})",
        f"🔧 Mantenimiento ({tiendas_mant_2026})",
        f"🔋 Cambios de Baterías ({c_bat})",
        f"📋 Alquiler de UPS ({tiendas_alq})",
        "📝 Registrar Nuevo Dato",
    ],
)


# Función generalizada para generar reporte PDF dinámico
def generar_pdf(df_exportar, titulo_reporte):
  buffer = BytesIO()
  p = canvas.Canvas(buffer, pagesize=landscape(letter))
  width, height = landscape(letter)

  p.setFont("Helvetica-Bold", 14)
  p.drawString(40, height - 35, f"Reporte: {titulo_reporte}")
  p.setFont("Helvetica", 9)
  p.drawString(
      40, height - 50, "Sistema de Gestión de UPS - Generado Automáticamente"
  )

  y = height - 75
  p.setFont("Helvetica-Bold", 7)

  columnas = list(df_exportar.columns)
  total_cols = len(columnas) if len(columnas) > 0 else 1

  ancho_disponible = width - 80
  ancho_columna = ancho_disponible / total_cols

  x_pos = 40
  for col in columnas:
    max_caracteres = max(4, int(ancho_columna / 4.5))
    p.drawString(x_pos, y, str(col)[:max_caracteres])
    x_pos += ancho_columna

  y -= 12
  p.setLineWidth(0.5)
  p.line(40, y + 4, width - 40, y + 4)

  y -= 12
  p.setFont("Helvetica", 6)

  for index, row in df_exportar.iterrows():
    if y < 35:
      p.showPage()
      y = height - 40
      p.setFont("Helvetica-Bold", 7)
      x_pos = 40
      for col in columnas:
        max_caracteres = max(4, int(ancho_columna / 4.5))
        p.drawString(x_pos, y, str(col)[:max_caracteres])
        x_pos += ancho_columna
      y -= 12
      p.setLineWidth(0.5)
      p.line(40, y + 4, width - 40, y + 4)
      y -= 12
      p.setFont("Helvetica", 6)

    x_pos = 40
    for col in columnas:
      val = str(row[col]) if pd.notna(row[col]) else ""
      max_caracteres = max(4, int(ancho_columna / 4))
      p.drawString(x_pos, y, val[:max_caracteres])
      x_pos += ancho_columna
    y -= 10

  p.save()
  buffer.seek(0)
  return buffer


if menu == "🏠 Resumen General":
  st.subheader("📊 Panel General de Activos")
  st.markdown("Estado actual de los registros en el sistema para el periodo.")

  col1, col2, col3, col4 = st.columns(4)

  with col1:
    with st.container(border=True):
      st.markdown(
          "<p"
          ' style="font-size:14px; font-weight:600; margin-bottom:5px;"'
          ">Inventario Total</p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"<h2 style='margin-top:0px; margin-bottom:0px;'>{c_inv if df_inventario is not None else 'Error'}</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p"
          ' style="font-size:11px; color:transparent;'
          ' margin-bottom:0px;">-</p>',
          unsafe_allow_html=True,
      )

  with col2:
    with st.container(border=True):
      st.markdown(
          "<p"
          ' style="font-size:14px; font-weight:600; margin-bottom:5px;"'
          ">Mantenimientos (2026)</p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"<h2 style='margin-top:0px; margin-bottom:0px;'>{tiendas_mant_2026}</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p"
          ' style="font-size:11px; color:transparent;'
          ' margin-bottom:0px;">-</p>',
          unsafe_allow_html=True,
      )

  with col3:
    with st.container(border=True):
      st.markdown(
          "<p"
          ' style="font-size:14px; font-weight:600; margin-bottom:8px;"'
          ">Cambio de baterías (2026)</p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <div style="flex: 1; text-align: left;">
                        <span style="font-size: 11px; color: gray; display: block;">Tiendas</span>
                        <span style="font-size: 22px; font-weight: bold; display: block;">{tiendas_bat_2026}</span>
                    </div>
                    <div style="flex: 1; text-align: right;">
                        <span style="font-size: 11px; color: gray; display: block;">Cantidad</span>
                        <span style="font-size: 22px; font-weight: bold; display: block;">{total_bat_2026}</span>
                    </div>
                </div>
                """,
          unsafe_allow_html=True,
      )

  with col4:
    with st.container(border=True):
      st.markdown(
          "<p"
          ' style="font-size:14px; font-weight:600; margin-bottom:8px;"'
          ">Equipos Alquilados</p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <div style="flex: 1; text-align: left;">
                        <span style="font-size: 11px; color: gray; display: block;">Tiendas</span>
                        <span style="font-size: 22px; font-weight: bold; display: block;">{tiendas_alq}</span>
                    </div>
                    <div style="flex: 1; text-align: right;">
                        <span style="font-size: 11px; color: gray; display: block;">Días / Total</span>
                        <span style="font-size: 22px; font-weight: bold; display: block;">{dias_alq}</span>
                    </div>
                </div>
                """,
          unsafe_allow_html=True,
      )

  st.markdown("---")
  st.subheader("🚨 Panel de Alertas y Equipos Críticos (2026)")
  st.markdown(
      "Equipos registrados con anomalías técnicas o estados críticos durante"
      " las revisiones:"
  )

  if df_mantenimiento is not None:
    df_m_temp = df_mantenimiento.copy()
    df_m_temp.columns = df_m_temp.columns.str.strip()
    if "MANT SE ENCONTRO" in df_m_temp.columns:
      criticos = df_m_temp[
          df_m_temp["MANT SE ENCONTRO"]
          .astype(str)
          .str.upper()
          .str.contains(
              "BYPASS|BAD|FALLA|FAIL|SHORT|APAGADO|DC BUS", na=False
          )
      ]
      if not criticos.empty:
        st.warning(
            f"⚠️ Se detectaron {len(criticos)} registros con incidencias o"
            " estados críticos."
        )
        st.dataframe(
            criticos[[
                "TIENDA",
                "RAZON",
                "MARCA",
                "MODELO",
                "NUMERO DE SERIE",
                "MANT FECHA",
                "MANT SE ENCONTRO",
            ]],
            width="stretch",
        )
      else:
        st.success(
            "✅ No se registran equipos en estado crítico o con fallas graves"
            " reportadas."
        )
    else:
      st.info("No se encontró la columna de incidencias de mantenimiento.")
  else:
    st.info("No hay datos de mantenimiento disponibles.")

elif menu == "📝 Registrar Nuevo Dato":
  st.subheader("📝 Formulario de Registro de Nuevo Mantenimiento o Batería")
  st.markdown(
      "Ingrese los datos correspondientes para agregarlos de forma segura a"
      " los registros del sistema."
  )

  if st.session_state.usuario_actual not in ["admin", "supervisor"]:
    st.error(
        "⛔ Acceso restringido. Solo los roles `admin` y `supervisor` pueden"
        " registrar nuevos datos."
    )
  else:
    modulo_destino = st.selectbox(
        "Seleccione el módulo donde desea registrar:",
        ["Mantenimiento (2026)", "Cambios de Baterías (2026)"],
    )

    with st.form("form_nuevo_registro"):
      col_r1, col_r2 = st.columns(2)
      with col_r1:
        tienda_val = st.text_input("Código de Tienda (Ej: KFC01)")
        razon_val = st.text_input("Razón Social / Empresa (Ej: DELOSI)")
        marca_val = st.text_input("Marca (Ej: KFC)")
        capacidad_val = st.text_input("Capacidad (Ej: 6 kva)")
      with col_r2:
        marca_ups_val = st.text_input("Marca de UPS (Ej: TRIPPLITE)")
        modelo_val = st.text_input("Modelo")
        serie_val = st.text_input("Número de Serie")
        fecha_val = st.date_input(
            "Fecha de Registro", value=datetime.today().date()
        )

      detalle_val = st.text_input(
          "Detalle / Estado encontrado (Ej: ON-LINE o BYPASS)"
      )
      submit_registro = st.form_submit_button(
          "Guardar Registro", use_container_width=True
      )

      if submit_registro:
        if not tienda_val or not serie_val:
          st.error(
              "Por favor complete al menos la Tienda y el Número de Serie."
          )
        else:
          if "Mantenimiento" in modulo_destino:
            nuevo_reg = {
                "ITEM": len(df_mantenimiento) + 1
                if df_mantenimiento is not None
                else 1,
                "TIENDA": tienda_val,
                "RAZON": razon_val,
                "MARCA": marca_val,
                "CAPACIDAD": capacidad_val,
                "MARCA DE UPS": marca_ups_val,
                "MODELO": modelo_val,
                "NUMERO DE SERIE": serie_val,
                "MANT. ATENCION": 1.0,
                "MANT FECHA": str(fecha_val),
                "MANT SE ENCONTRO": detalle_val,
                "MANT QUEDA": "ON-LINE",
                "MANT CARGA": 1.0,
            }
            exito = guardar_en_excel("Mantenimiento_UPS_2026.xlsx", nuevo_reg)
          else:
            nuevo_reg = {
                "ITEM": len(df_baterias) + 1
                if df_baterias is not None
                else 1,
                "TIENDA": tienda_val,
                "RAZON": razon_val,
                "MARCA": marca_val,
                "CAPACIDAD": capacidad_val,
                "MARCA DE UPS": marca_ups_val,
                "MODELO": modelo_val,
                "NUMERO DE SERIE": serie_val,
                "FECHA 2026": str(fecha_val),
                "CANTIDAD 2026": 20,
                "FECHA 2025": None,
                "CANTIDAD 2025": None,
            }
            exito = guardar_en_excel(
                "Cambios_Baterias_UPS_2026.xlsx", nuevo_reg
            )

          if exito:
            st.success(
                "¡Registro guardado exitosamente en el archivo Excel!"
                " Actualice la página para ver las nuevas métricas."
            )
          else:
            st.error("No se pudo guardar el registro.")

else:
  if "Inventario UPS" in menu:
    st.subheader("📦 Inventario General de UPS 2026")
    df = df_inventario
    nombre_archivo = "Inventario_UPS_2026.xlsx"
    nombre_base = "inventario_ups"
    titulo_modulo = "Inventario UPS"
  elif "Mantenimiento" in menu:
    st.subheader("🔧 Registro de Mantenimientos 2026")
    df = df_mantenimiento
    nombre_archivo = "Mantenimiento_UPS_2026.xlsx"
    nombre_base = "mantenimiento_ups"
    titulo_modulo = "Mantenimiento"
  elif "Cambios de Baterías" in menu:
    st.subheader("🔋 Control de Cambios de Baterías 2026")
    df = df_baterias
    nombre_archivo = "Cambios_Baterias_UPS_2026.xlsx"
    nombre_base = "cambios_baterias"
    titulo_modulo = "Cambios de Baterías"
  elif "Alquiler de UPS" in menu:
    st.subheader("📋 Gestión de Alquiler de UPS")
    df = df_alquiler
    nombre_archivo = "alquiler_de_UPS.xlsx"
    nombre_base = "alquiler_ups"
    titulo_modulo = "Alquiler de UPS"

  if df is not None:
    df_vista = df.copy()
    for col in df_vista.columns:
      if "CARGA" in col.upper() or "PORCENTAJE" in col.upper():
        df_vista[col] = pd.to_numeric(df_vista[col], errors="coerce").apply(
            lambda x: f"{x * 100:.1f}%" if pd.notna(x) else ""
        )

    tab_tabla, tab_resumen = st.tabs(
        [
            "📋 Vista de Datos y Exportación",
            "📊 Análisis y Distribución Interactiva",
        ]
    )

    with tab_tabla:
      df_filtrado = df_vista.copy()

      with st.expander("🔍 Filtros y Opciones de Vista", expanded=True):
        col_f1, col_f2 = st.columns(2)

        with col_f1:
          busqueda = st.text_input("Búsqueda rápida global:")

          columnas_texto = [
              col
              for col in df.select_dtypes(
                  include=["object", "category"]
              ).columns
          ]
          candidatas_razon_marca = [
              c
              for c in columnas_texto
              if any(
                  k in c.lower()
                  for k in [
                      "razon",
                      "social",
                      "marca",
                      "proveedor",
                      "cliente",
                      "empresa",
                  ]
              )
          ]

          if candidatas_razon_marca:
            col_rm = st.selectbox(
                "Filtrar por Razón / Marca:",
                ["-- Todos --"] + candidatas_razon_marca,
            )
            if col_rm != "-- Todos --":
              valores_unicos = ["-- Todos --"] + sorted(
                  df[col_rm].dropna().astype(str).unique().tolist()
              )
              val_seleccionado = st.selectbox(
                  f"Valor para `{col_rm}`:", valores_unicos
              )
              if val_seleccionado != "-- Todos --":
                df_filtrado = df_filtrado[
                    df_filtrado[col_rm].astype(str) == val_seleccionado
                ]

        with col_f2:
          columnas_visibles = st.multiselect(
              "Columnas visibles:",
              options=list(df.columns),
              default=list(df.columns),
          )
          if columnas_visibles:
            df_filtrado = df_filtrado[columnas_visibles]

          columnas_fecha = []
          for col in df.columns:
            if "fecha" in col.lower() or "date" in col.lower():
              columnas_fecha.append(col)

          if columnas_fecha:
            col_fecha_sel = st.selectbox(
                "Filtrar por Fecha (Columna):", ["-- Ninguna --"] + columnas_fecha
            )
            if col_fecha_sel != "-- Ninguna --":
              try:
                df_temp = df_filtrado.copy()
                df_temp[col_fecha_sel] = pd.to_datetime(
                    df_temp[col_fecha_sel], errors="coerce"
                )
                fechas_validas = df_temp[col_fecha_sel].dropna()
                if not fechas_validas.empty:
                  min_f = fechas_validas.min().date()
                  max_f = fechas_validas.max().date()
                  rango_fechas = st.date_input(
                      "Rango:",
                      value=(min_f, max_f),
                      min_value=min_f,
                      max_value=max_f,
                  )
                  if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
                    f_inicio, f_fin = rango_fechas
                    mask_fecha = (
                        df_temp[col_fecha_sel].dt.date >= f_inicio
                    ) & (df_temp[col_fecha_sel].dt.date <= f_fin)
                    df_filtrado = df_filtrado[mask_fecha]

                    import re

                    match_anio = re.search(r"(20\d{2})", col_fecha_sel)
                    if match_anio:
                      anio_sel = match_anio.group(1)
                      columnas_a_mantener = []
                      for c in df_filtrado.columns:
                        c_upper = c.upper()
                        tiene_otro_anio = any(
                            str(yr) in c_upper
                            for yr in range(2020, 2030)
                            if str(yr) != anio_sel
                        )
                        if tiene_otro_anio and c != col_fecha_sel:
                          continue
                        columnas_a_mantener.append(c)
                      df_filtrado = df_filtrado[columnas_a_mantener]
              except Exception:
                pass

      if busqueda:
        mask = (
            df_filtrado.astype(str)
            .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
            .any(axis=1)
        )
        df_filtrado = df_filtrado[mask]

      st.markdown("---")

      col_tit, c_csv, c_excel, c_pdf = st.columns([2.5, 0.8, 0.8, 0.8])
      with col_tit:
        st.markdown(f"### 📋 Registros Filtrados ({len(df_filtrado)})")
      with c_csv:
        csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📄 CSV",
            data=csv_data,
            file_name=f"{nombre_base}_filtrado.csv",
            mime="text/csv",
            key="btn_csv",
            use_container_width=True,
        )
      with c_excel:
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
          df_filtrado.to_excel(writer, index=False, sheet_name="Reporte")
        excel_data = output_excel.getvalue()
        st.download_button(
            label="📊 Excel",
            data=excel_data,
            file_name=f"{nombre_base}_filtrado.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            key="btn_excel",
            use_container_width=True,
        )
      with c_pdf:
        pdf_buffer = generar_pdf(
            df_filtrado, f"{titulo_modulo} ({len(df_filtrado)}) (Filtrado)"
        )
        st.download_button(
            label="📑 PDF",
            data=pdf_buffer,
            file_name=f"{nombre_base}_filtrado.pdf",
            mime="application/pdf",
            key="btn_pdf",
            use_container_width=True,
        )

      st.dataframe(df_filtrado, width="stretch")

    with tab_resumen:
      st.markdown(
          "### 📈 Gráficos Interactivos y Distribución por Categoría"
      )
      columnas_texto = [
          col for col in df.select_dtypes(include=["object", "category"]).columns
      ]

      if columnas_texto:
        col_g1, col_g2 = st.columns([1, 1])
        with col_g1:
          col_seleccionada = st.selectbox(
              "Selecciona la columna para graficar:",
              columnas_texto,
              key="sel_grafico",
          )
        with col_g2:
          tipo_grafico = st.selectbox(
              "Tipo de Gráfico:", ["Gráfico de Barras", "Gráfico Circular (Pie)"]
          )

        if col_seleccionada:
          resumen_df = (
              df[col_seleccionada]
              .value_counts()
              .reset_index(name="Cantidad")
          )
          resumen_df.columns = [col_seleccionada, "Cantidad"]

          st.markdown("---")

          if tipo_grafico == "Gráfico de Barras":
            fig = px.bar(
                resumen_df.head(15),
                x=col_seleccionada,
                y="Cantidad",
                text="Cantidad",
                title=f"Top distribución de {col_seleccionada}",
                color="Cantidad",
                color_continuous_scale="blues",
            )
            fig.update_layout(xaxis_tickangle=-45, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
          else:
            fig = px.pie(
                resumen_df.head(10),
                names=col_seleccionada,
                values="Cantidad",
                title=f"Proporción de {col_seleccionada}",
                hole=0.4,
            )
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

          st.markdown("#### 📋 Detalle Numérico")
          st.dataframe(resumen_df, width="stretch")
      else:
        st.info("No hay columnas de texto disponibles para este análisis.")

  else:
    st.error(
        f"No se encontró el archivo `{nombre_archivo}` en la carpeta del"
        " proyecto."
    )
