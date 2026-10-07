from datetime import datetime
from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
import streamlit as st

st.set_page_config(
    page_title="Sistema de Gestión de UPS", page_icon="⚡", layout="wide"
)

st.title("⚡ Plataforma de Control y Gestión de UPS")
st.markdown(
    "Panel de control centralizado avanzado para la administración de activos,"
    " inventario, mantenimientos y baterías."
)


# Función para cargar Excel en tiempo real y limpiar columnas duplicadas
def cargar_excel(nombre_archivo):
  try:
    df = pd.read_excel(nombre_archivo)
    df.columns = df.columns.str.strip()
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


# Función para obtener tiendas únicas y la suma total directa de baterías
def obtener_metricas_baterias_2026(df):
  if df is None:
    return 0, 0

  df_temp = df.copy()
  df_temp.columns = df_temp.columns.str.strip()

  cant_tiendas = 0
  if "TIENDA" in df_temp.columns:
    cant_tiendas = df_temp["TIENDA"].dropna().nunique()

  total_baterias = 0
  cols_cant = [c for c in df_temp.columns if "CANTIDAD" in c.upper()]
  for col_c in cols_cant:
    total_baterias += int(
        pd.to_numeric(df_temp[col_c], errors="coerce").sum()
    )

  return cant_tiendas, total_baterias


# Cargar los datasets principales
df_inventario = cargar_excel("Inventario_UPS_2026.xlsx")
df_mantenimiento = cargar_excel("Mantenimiento_UPS_2026.xlsx")
df_baterias = cargar_excel("Cambios_Baterias_UPS_2026.xlsx")
df_alquiler = cargar_excel("alquiler_de_UPS.xlsx")

# Conteos seguros
c_inv = len(df_inventario) if df_inventario is not None else 0
c_alq = len(df_alquiler) if df_alquiler is not None else 0
c_mant = len(df_mantenimiento) if df_mantenimiento is not None else 0

tiendas_bat_2026, total_bat_2026 = obtener_metricas_baterias_2026(df_baterias)
c_bat = len(df_baterias) if df_baterias is not None else 0

# Menú lateral principal
menu = st.sidebar.selectbox(
    "Navegación",
    [
        "🏠 Resumen General",
        f"📦 Inventario UPS ({c_inv})",
        f"🔧 Mantenimiento ({c_mant})",
        f"🔋 Cambios de Baterías ({c_bat})",
        f"📋 Alquiler de UPS ({c_alq})",
    ],
)


# Función para generar reporte PDF completo en formato horizontal (Landscape)
def generar_pdf(df_exportar, titulo_reporte):
  buffer = BytesIO()
  p = canvas.Canvas(buffer, pagesize=landscape(letter))
  width, height = landscape(letter)

  p.setFont("Helvetica-Bold", 16)
  p.drawString(40, height - 40, f"Reporte: {titulo_reporte}")
  p.setFont("Helvetica", 10)
  p.drawString(
      40, height - 58, "Sistema de Gestión de UPS - Generado Automáticamente"
  )

  y = height - 90
  p.setFont("Helvetica-Bold", 8)

  # Columnas clave que queremos forzar si existen
  cols_disponibles = list(df_exportar.columns)
  forzadas = [
      "ITEM",
      "TIENDA",
      "RAZON",
      "MARCA",
      "CAPACIDAD",
      "MARCA DE UPS",
      "MODELO",
      "CANTIDAD",
  ]

  columnas = [c for c in forzadas if c in cols_disponibles]

  # Si faltasen o hubiese espacio, completamos con las primeras disponibles hasta 8 columnas
  for c in cols_disponibles:
    if c not in columnas and len(columnas) < 8:
      columnas.append(c)

  ancho_columna = (width - 80) / len(columnas)

  x_pos = 40
  for col in columnas:
    p.drawString(x_pos, y, str(col)[:15])
    x_pos += ancho_columna

  y -= 15
  p.setLineWidth(0.5)
  p.line(40, y + 5, width - 40, y + 5)

  y -= 15
  p.setFont("Helvetica", 7)

  for index, row in df_exportar.iterrows():
    if y < 40:
      p.showPage()
      y = height - 40
      p.setFont("Helvetica-Bold", 8)
      x_pos = 40
      for col in columnas:
        p.drawString(x_pos, y, str(col)[:15])
        x_pos += ancho_columna
      y -= 15
      p.setLineWidth(0.5)
      p.line(40, y + 5, width - 40, y + 5)
      y -= 15
      p.setFont("Helvetica", 7)

    x_pos = 40
    for col in columnas:
      val = str(row[col]) if pd.notna(row[col]) else ""
      p.drawString(x_pos, y, val[:18])
      x_pos += ancho_columna
    y -= 12

  p.save()
  buffer.seek(0)
  return buffer


if menu == "🏠 Resumen General":
  st.subheader("📊 Panel General de Activos")
  st.markdown("Estado actual de los registros en el sistema para el periodo 2026.")

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
          ">Mantenimientos</p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"<h2 style='margin-top:0px; margin-bottom:0px;'>{c_mant}</h2>",
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
          ">Cambio de baterías</p>",
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
          ' style="font-size:14px; font-weight:600; margin-bottom:5px;"'
          ">Equipos Alquilados</p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          f"<h2 style='margin-top:0px; margin-bottom:0px;'>{c_alq if df_alquiler is not None else 'Error'}</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p"
          ' style="font-size:11px; color:transparent;'
          ' margin-bottom:0px;">-</p>',
          unsafe_allow_html=True,
      )

  st.markdown("---")
  st.info(
      "👉 Selecciona un módulo en el menú de la izquierda para ver el detalle"
      " completo, buscar equipos, aplicar filtros y exportar a Excel y PDF."
  )

else:
  if "Inventario UPS" in menu:
    st.subheader("📦 Inventario General de UPS 2026")
    df = df_inventario
    nombre_archivo = "Inventario_UPS_2026.xlsx"
    nombre_base = "inventario_ups"
    titulo_modulo = "Inventario UPS"
  elif "Mantenimiento" in menu:
    st.subheader("🔧 Registro de Mantenimientos")
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
        ["📋 Vista de Datos y Exportación", "📊 Análisis y Distribución"]
    )

    with tab_tabla:
      st.markdown("### 🔍 Panel de Búsqueda y Filtros Avanzados")

      df_filtrado = df_vista.copy()

      busqueda = st.text_input(
          "Búsqueda rápida global (equipo, código, serie, etc.):"
      )
      if busqueda:
        mask = (
            df_filtrado.astype(str)
            .apply(lambda x: x.str.contains(busqueda, case=False, na=False))
            .any(axis=1)
        )
        df_filtrado = df_filtrado[mask]

      columnas_texto = [
          col for col in df.select_dtypes(include=["object", "category"]).columns
      ]
      candidatas_razon_marca = [
          c
          for c in columnas_texto
          if any(
              k in c.lower()
              for k in ["razon", "social", "marca", "proveedor", "cliente", "empresa"]
          )
      ]

      if candidatas_razon_marca:
        col_rm = st.selectbox(
            "Filtrar por Razón Social / Marca (Opcional):",
            ["-- Todos --"] + candidatas_razon_marca,
        )
        if col_rm != "-- Todos --":
          valores_unicos = ["-- Todos --"] + sorted(
              df[col_rm].dropna().astype(str).unique().tolist()
          )
          val_seleccionado = st.selectbox(
              f"Selecciona valor para `{col_rm}`:", valores_unicos
          )
          if val_seleccionado != "-- Todos --":
            df_filtrado = df_filtrado[
                df_filtrado[col_rm].astype(str) == val_seleccionado
            ]

      columnas_fecha = []
      for col in df.columns:
        if "fecha" in col.lower() or "date" in col.lower():
          columnas_fecha.append(col)
        else:
          try:
            pd.to_datetime(df[col].dropna().head(10))
            if df[col].dtype == "object":
              columnas_fecha.append(col)
          except:
            pass

      if columnas_fecha:
        with st.expander("📅 Filtro Avanzado por Rango de Fechas"):
          col_fecha_sel = st.selectbox(
              "Selecciona la columna de fecha a evaluar:", columnas_fecha
          )
          if col_fecha_sel:
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
                    "Selecciona el rango de fechas:",
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
            except Exception as e:
              st.warning(
                  "No se pudo aplicar el filtro de fecha automáticamente en"
                  " este formato."
              )

      with st.expander("⚙️ Personalizar columnas visibles"):
        columnas_visibles = st.multiselect(
            "Selecciona las columnas que deseas visualizar en pantalla:",
            options=list(df.columns),
            default=list(df.columns),
        )
        if columnas_visibles:
          df_filtrado = df_filtrado[columnas_visibles]

      st.markdown("---")

      col_tit, col_btn = st.columns([2, 3])
      with col_tit:
        st.markdown(
            "### 📋 Vista de Datos\n*Descarga los registros filtrados*"
        )
      with col_btn:
        c_ex1, c_ex2, c_ex3 = st.columns(3)
        with c_ex1:
          csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
          st.download_button(
              label="📄 CSV",
              data=csv_data,
              file_name=f"{nombre_base}_filtrado.csv",
              mime="text/csv",
          )
        with c_ex2:
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
          )
        with c_ex3:
          pdf_buffer = generar_pdf(
              df_filtrado, f"{titulo_modulo} ({len(df_filtrado)}) (Filtrado)"
          )
          st.download_button(
              label="📑 PDF",
              data=pdf_buffer,
              file_name=f"{nombre_base}_filtrado.pdf",
              mime="application/pdf",
          )

      st.markdown("---")
      st.dataframe(df_filtrado, width="stretch")
      st.info(
          f"Mostrando {len(df_filtrado)} registros (de un total de {len(df)})."
      )

    with tab_resumen:
      st.markdown("### 📈 Distribución y Detalle por Categoría")
      st.markdown(
          "Selecciona cualquier columna de texto para desglosar y ver el"
          " conteo exacto de registros por categoría:"
      )

      columnas_texto = [
          col for col in df.select_dtypes(include=["object", "category"]).columns
      ]
      if columnas_texto:
        col_seleccionada = st.selectbox(
            "Selecciona la columna a analizar:", columnas_texto
        )
        if col_seleccionada:
          resumen_df = (
              df[col_seleccionada].value_counts().reset_index(name="Cantidad")
          )
          resumen_df.columns = [col_seleccionada, "Total de Registros"]
          st.dataframe(resumen_df, width="stretch")
      else:
        st.info("No hay columnas de texto disponibles para este análisis.")

  else:
    st.error(
        f"No se encontró el archivo `{nombre_archivo}` en la carpeta del"
        " proyecto. Asegúrate de que esté en el directorio correcto."
    )
