import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# Configurar página
st.set_page_config(page_title="Dashboard de Reclutamiento", layout="wide")

# Menú de navegación multipágina
st.sidebar.title("Navegación")
pagina = st.sidebar.radio("Ir a:", ["🏠 Presentación", "📌 KPIs", "📈 Gráficos"])

# Subir archivo
st.sidebar.header("📁 Cargar archivo Excel")
archivo = st.sidebar.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

if pagina == "🏠 Presentación":
    st.title("📊 Dashboard de Reclutamiento")
    st.markdown("""
    Bienvenido al **Dashboard de Reclutamiento**. 

    Aquí podrás analizar y visualizar información clave del proceso de selección:

    - Tiempo promedio de contratación
    - Costos de reclutamiento
    - Fuentes más efectivas
    - Comparativas por puesto, nivel y departamento
    - Evolución temporal del proceso

    Para comenzar, sube un archivo Excel válido desde el menú lateral.
    """)

elif archivo is not None:
    @st.cache_data
    def load_data(file):
        df = pd.read_excel(file, sheet_name=0)
        df['fecha_aplicacion'] = pd.to_datetime(df['fecha_aplicacion'], errors='coerce')
        df['fecha_oferta'] = pd.to_datetime(df['fecha_oferta'], errors='coerce')
        return df

    df = load_data(archivo)

    # Sidebar - Filtros
    st.sidebar.header("Filtros")
    año = st.sidebar.multiselect("Año de aplicación", df['año_aplicacion'].unique(), default=df['año_aplicacion'].unique())
    departamento = st.sidebar.multiselect("Departamento", df['departamento'].unique(), default=df['departamento'].unique())
    nivel = st.sidebar.multiselect("Nivel", df['nivel'].dropna().unique(), default=df['nivel'].dropna().unique())
    puesto = st.sidebar.multiselect("Puesto", df['puesto'].dropna().unique(), default=df['puesto'].dropna().unique())
    fuente = st.sidebar.multiselect("Fuente de reclutamiento", df['fuente_reclutamiento'].dropna().unique(), default=df['fuente_reclutamiento'].dropna().unique())

    # Filtrado
    filtered_df = df[
        (df['año_aplicacion'].isin(año)) &
        (df['departamento'].isin(departamento)) &
        (df['nivel'].isin(nivel)) &
        (df['puesto'].isin(puesto)) &
        (df['fuente_reclutamiento'].isin(fuente))
    ]

    contratados = filtered_df[filtered_df['estado_proceso'] == 'Oferta aceptada']

    if pagina == "📌 KPIs":
        from kpi_tab_logic import show_kpi_tab
        show_kpi_tab(filtered_df, contratados)

    elif pagina == "📈 Gráficos":
        from grafico_tab_logic import show_grafico_tab
        show_grafico_tab(filtered_df, contratados)

else:
    if pagina != "🏠 Presentación":
        st.warning("Por favor sube un archivo Excel para visualizar esta sección.")
