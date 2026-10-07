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
    " inventario, mantenimientos y baterías (Periodo 2026)."
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


# Función para filtrar estrictamente los registros del año 2026
def filtrar_solo_2026(df):
  if df is None or df.empty:
    return df

  df_f = df.copy()
  cols_fecha = [
      c
      for c in df_f.columns
      if "fecha" in c.lower() or "date" in c.lower() or "2026" in c
  ]

  if cols_fecha:
    for col_f in cols_fecha:
      try:
        fechas_dt = pd.to_datetime(df_f[col_f], errors="coerce")
        mask_2026 = fechas_dt.dt.year == 2026
        if mask_2026.sum() > 0:
          df_f = df_f[mask_2026 | fechas_dt.isna()]
      except Exception:
        pass

  columnas_a_mantener = []
  for c in df_f.columns:
    c_upper = c.upper()
    tiene_otro_anio = any(
        f"20{yr}" in c_upper
        for yr in range(20, 30)
        if yr != 26 and f"20{yr}" in c_upper
    )
    if tiene_otro_anio:
      continue
    columnas_a_mantener.append(c)

  df_f = df_f[columnas_a_mantener]
  return df_f


# Cargar los datasets principales y restringirlos a 2026
df_inventario = filtrar_solo_2026(cargar_excel("Inventario_UPS_2026.xlsx"))
df_mantenimiento = filtrar_solo_2026(cargar_excel("Mantenimiento_UPS_2026.xlsx"))
df_baterias = filtrar_solo_2026(cargar_excel("Cambios_Baterias_UPS_2026.xlsx"))
df_alquiler = filtrar_solo_2026(cargar_excel("alquiler_de_UPS.xlsx"))


# Función para obtener tiendas únicas y suma total de baterías estrictamente para el año 2026
def obtener_metricas_baterias_2026(df):
  if df is None or df.empty:
    return 0, 0

  df_temp = df.copy()
  df_temp.columns = df_temp.columns.str.strip()

  # Filtrar filas donde la fecha de cambio pertenezca estrictamente al año 2026
  cols_fecha = [
      c for c in df_temp.columns if "fecha" in c.lower() or "date" in c.lower()
  ]
  if cols_fecha:
    for col_f in cols_fecha:
      try:
        fechas_dt = pd.to_datetime(df_temp[col_f], errors="coerce")
        mask_2026 = fechas_dt.dt.year == 2026
        if mask_2026.sum() > 0:
          df_temp = df_temp[mask_2026]
          break
      except Exception:
        pass

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


# Conteos seguros exclusivos para 2026
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
    nombre_base = "inventario_ups_2026"
    titulo_modulo = "Inventario UPS 2026"
  elif "Mantenimiento" in menu:
    st.subheader("🔧 Registro de Mantenimientos 2026")
    df = df_mantenimiento
    nombre_archivo = "Mantenimiento_UPS_2026.xlsx"
    nombre_base = "mantenimiento_ups_2026"
    titulo_modulo = "Mantenimiento 2026"
  elif "Cambios de Baterías" in menu:
    st.subheader("🔋 Control de Cambios de Baterías 2026")
    df = df_baterias
    nombre_archivo = "Cambios_Baterias_UPS_2026.xlsx"
    nombre_base = "cambios_baterias_2026"
    titulo_modulo = "Cambios de Baterías 2026"
  elif "Alquiler de UPS" in menu:
    st.subheader("📋 Gestión de Alquiler de UPS 2026")
    df = df_alquiler
    nombre_archivo = "alquiler_de_UPS.xlsx"
    nombre_base = "alquiler_ups_2026"
    titulo_modulo = "Alquiler de UPS 2026"

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
      st.markdown("### 📈 Distribución y Detalle por Categoría")
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
        " proyecto."
    )
