import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# Configurar página con favicon y layout
st.set_page_config(
    page_title="Dashboard de Reclutamiento",
    layout="wide",
    page_icon="📊"
)

# Encabezado con logo y título estilizado
st.markdown("""
    <div style='display: flex; align-items: center; justify-content: space-between; background-color: #1f2c56; padding: 1rem; border-radius: 10px;'>
        <div style='color: white;'>
            <h2 style='margin: 0;'>📊 Dashboard de Reclutamiento</h2>
            <p style='margin: 0;'>Análisis interactivo de procesos y métricas clave de selección</p>
        </div>
    </div>
    <br>
""", unsafe_allow_html=True)

# Subir archivo
st.markdown("### 📁 Cargar archivo Excel")
archivo = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

if archivo is not None:
    @st.cache_data
    def load_data(file):
        df = pd.read_excel(file, sheet_name=0)
        df['fecha_aplicacion'] = pd.to_datetime(df['fecha_aplicacion'], errors='coerce')
        df['fecha_oferta'] = pd.to_datetime(df['fecha_oferta'], errors='coerce')
        return df

    df = load_data(archivo)

    # Filtros
    st.markdown("### 🔎 Filtros")
    with st.expander("Mostrar / ocultar filtros", expanded=True):
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                año = st.multiselect("🗓️ Año de aplicación", df['año_aplicacion'].unique(), default=df['año_aplicacion'].unique())
                nivel = st.multiselect("📶 Nivel", df['nivel'].dropna().unique(), default=df['nivel'].dropna().unique())
            with col2:
                departamento = st.multiselect("🏢 Departamento", df['departamento'].unique(), default=df['departamento'].unique())
                puesto = st.multiselect("👔 Puesto", df['puesto'].dropna().unique(), default=df['puesto'].dropna().unique())
            with col3:
                fuente = st.multiselect("🌐 Fuente de reclutamiento", df['fuente_reclutamiento'].dropna().unique(), default=df['fuente_reclutamiento'].dropna().unique())

    # Filtrado de datos
    filtered_df = df[
        (df['año_aplicacion'].isin(año)) &
        (df['departamento'].isin(departamento)) &
        (df['nivel'].isin(nivel)) &
        (df['puesto'].isin(puesto)) &
        (df['fuente_reclutamiento'].isin(fuente))
    ]

    # KPIs
    st.markdown("""
    <hr style='margin-top: 1rem; margin-bottom: 1rem;'>
    <h3 style='color:#1f2c56;'>📈 Resultados Generales</h3>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    tiempo_prom = filtered_df['tiempo_contratacion_dias'].mean()
    total_candidatos = len(filtered_df)
    contratados = filtered_df[filtered_df['estado_proceso'] == 'Oferta aceptada']
    tasa_conversion = (len(contratados) / total_candidatos * 100) if total_candidatos else 0
    ofertas_totales = filtered_df[filtered_df['estado_proceso'].str.contains("Oferta", na=False)]
    ofertas_aceptadas = ofertas_totales[ofertas_totales['oferta_aceptada'] == True]
    tasa_aceptacion = (len(ofertas_aceptadas) / len(ofertas_totales) * 100) if len(ofertas_totales) else 0
    costo_prom = contratados['costo_reclutamiento'].mean()

    col1.metric("⏱️ Tiempo promedio contratación", f"{tiempo_prom:.1f} días")
    col2.metric("🎯 Tasa de conversión", f"{tasa_conversion:.1f}%")
    col3.metric("📩 Tasa aceptación de oferta", f"{tasa_aceptacion:.1f}%")
    col4.metric("💰 Costo por contratación", f"€{costo_prom:,.2f}")
    col5.metric("👥 Contrataciones", f"{len(contratados)}")

    style_metric_cards(background_color="#f0f2f6", border_left_color="#1f77b4", border_color="#FFFFFF")

    # Gráficos
    st.markdown("<h3 style='color:#1f2c56;'>📊 Gráficos</h3>", unsafe_allow_html=True)

    fuente_data = contratados['fuente_reclutamiento'].value_counts(normalize=True) * 100
    fig1 = px.bar(fuente_data, x=fuente_data.index, y=fuente_data.values, labels={'x': 'Fuente', 'y': 'Porcentaje'}, title="Fuente de contratación (%)")
    st.plotly_chart(fig1, use_container_width=True)

    contratados['mes_aplicacion'] = pd.to_datetime(contratados['mes_aplicacion'], errors='coerce')
    mensual = contratados.groupby('mes_aplicacion').size().reset_index(name='Contrataciones')
    fig2 = px.line(mensual, x='mes_aplicacion', y='Contrataciones', title="Contrataciones por Mes")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(contratados, y='tiempo_contratacion_dias', points="all", title="Distribución tiempo de contratación")
    st.plotly_chart(fig3, use_container_width=True)

    # Tabla de detalle
    st.markdown("### 📋 Detalle de Datos Filtrados")
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar datos filtrados", data=csv, file_name="reclutamiento_filtrado.csv", mime="text/csv")
else:
    st.warning("Por favor sube un archivo Excel para visualizar el dashboard.")




