import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar página
st.set_page_config(page_title="Dashboard de Reclutamiento", layout="wide")

# Subir archivo
st.sidebar.header("📁 Cargar archivo Excel")
archivo = st.sidebar.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

if archivo is not None:
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

    # Filtrado
    filtered_df = df[(df['año_aplicacion'].isin(año)) & (df['departamento'].isin(departamento))]

    # KPIs
    st.title("📊 Dashboard de Reclutamiento")

    col1, col2, col3, col4, col5 = st.columns(5)

    # 1. Tiempo promedio de contratación
    tiempo_prom = filtered_df['tiempo_contratacion_dias'].mean()
    col1.metric("⏱️ Tiempo promedio contratación", f"{tiempo_prom:.1f} días")

    # 2. Tasa de conversión de candidatos
    total_candidatos = len(filtered_df)
    contratados = filtered_df[filtered_df['estado_proceso'] == 'Oferta aceptada']
    tasa_conversion = (len(contratados) / total_candidatos * 100) if total_candidatos else 0
    col2.metric("🎯 Tasa de conversión", f"{tasa_conversion:.1f}%")

    # 3. Tasa de aceptación de ofertas
    ofertas_totales = filtered_df[filtered_df['estado_proceso'].str.contains("Oferta", na=False)]
    ofertas_aceptadas = ofertas_totales[ofertas_totales['oferta_aceptada'] == True]
    tasa_aceptacion = (len(ofertas_aceptadas) / len(ofertas_totales) * 100) if len(ofertas_totales) else 0
    col3.metric("📩 Tasa aceptación de oferta", f"{tasa_aceptacion:.1f}%")

    # 4. Costo por contratación promedio
    costo_prom = contratados['costo_reclutamiento'].mean()
    col4.metric("💰 Costo por contratación", f"€{costo_prom:,.2f}")

    # 5. Número total de contrataciones
    col5.metric("👥 Contrataciones", f"{len(contratados)}")

    # Tabs
    kpi_tab, grafico_tab, detalle_tab = st.tabs(["📌 KPIs", "📈 Gráficos", "📋 Detalle"])

    with grafico_tab:
        st.subheader("Contrataciones por Fuente")
        fuente_data = contratados['fuente_reclutamiento'].value_counts(normalize=True) * 100
        fig1 = px.bar(fuente_data, x=fuente_data.index, y=fuente_data.values,
                      labels={'x': 'Fuente', 'y': 'Porcentaje'}, title="Fuente de contratación (%)")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Evolución mensual de contrataciones")
        contratados['mes_aplicacion'] = pd.to_datetime(contratados['mes_aplicacion'], errors='coerce')
        mensual = contratados.groupby('mes_aplicacion').size().reset_index(name='Contrataciones')
        fig2 = px.line(mensual, x='mes_aplicacion', y='Contrataciones', title="Contrataciones por Mes")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Distribución del Tiempo de Contratación")
        fig3 = px.box(contratados, y='tiempo_contratacion_dias', points="all", title="Distribución tiempo de contratación")
        st.plotly_chart(fig3, use_container_width=True)

    with detalle_tab:
        st.dataframe(filtered_df)
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar datos filtrados", data=csv, file_name="reclutamiento_filtrado.csv", mime="text/csv")
else:
    st.warning("Por favor sube un archivo Excel para visualizar el dashboard.")
