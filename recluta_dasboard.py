import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# Configurar página
st.set_page_config(page_title="Dashboard de Reclutamiento", layout="wide")

# Subir archivo
st.header("📁 Cargar archivo Excel")
archivo = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

if archivo is not None:
    @st.cache_data
    def load_data(file):
        df = pd.read_excel(file, sheet_name=0)
        df['fecha_aplicacion'] = pd.to_datetime(df['fecha_aplicacion'], errors='coerce')
        df['fecha_oferta'] = pd.to_datetime(df['fecha_oferta'], errors='coerce')
        return df

    df = load_data(archivo)

    # Filtros fuera del sidebar
    st.markdown("## 🔎 Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        año = st.multiselect("Año de aplicación", df['año_aplicacion'].unique(), default=df['año_aplicacion'].unique())
        nivel = st.multiselect("Nivel", df['nivel'].dropna().unique(), default=df['nivel'].dropna().unique())
    with col2:
        departamento = st.multiselect("Departamento", df['departamento'].unique(), default=df['departamento'].unique())
        puesto = st.multiselect("Puesto", df['puesto'].dropna().unique(), default=df['puesto'].dropna().unique())
    with col3:
        fuente = st.multiselect("Fuente de reclutamiento", df['fuente_reclutamiento'].dropna().unique(), default=df['fuente_reclutamiento'].dropna().unique())

    # Filtrado
    filtered_df = df[
        (df['año_aplicacion'].isin(año)) &
        (df['departamento'].isin(departamento)) &
        (df['nivel'].isin(nivel)) &
        (df['puesto'].isin(puesto)) &
        (df['fuente_reclutamiento'].isin(fuente))
    ]

    # KPIs Generales
    st.title("📊 Dashboard de Reclutamiento")

    col1, col2, col3, col4, col5 = st.columns(5)

    tiempo_prom = filtered_df['tiempo_contratacion_dias'].mean()
    col1.metric("⏱️ Tiempo promedio contratación", f"{tiempo_prom:.1f} días")

    total_candidatos = len(filtered_df)
    contratados = filtered_df[filtered_df['estado_proceso'] == 'Oferta aceptada']
    tasa_conversion = (len(contratados) / total_candidatos * 100) if total_candidatos else 0
    col2.metric("🎯 Tasa de conversión", f"{tasa_conversion:.1f}%")

    ofertas_totales = filtered_df[filtered_df['estado_proceso'].str.contains("Oferta", na=False)]
    ofertas_aceptadas = ofertas_totales[ofertas_totales['oferta_aceptada'] == True]
    tasa_aceptacion = (len(ofertas_aceptadas) / len(ofertas_totales) * 100) if len(ofertas_totales) else 0
    col3.metric("📩 Tasa aceptación de oferta", f"{tasa_aceptacion:.1f}%")

    costo_prom = contratados['costo_reclutamiento'].mean()
    col4.metric("💰 Costo por contratación", f"€{costo_prom:,.2f}")

    col5.metric("👥 Contrataciones", f"{len(contratados)}")

    style_metric_cards(background_color="#3333ff", border_left_color="#ff5733", border_color="#FFFFFF")

    # Tabs
    kpi_tab, grafico_tab, detalle_tab = st.tabs(["📌 KPIs", "📈 Gráficos", "📋 Detalle"])

    with kpi_tab:
        st.subheader("🔍 Comparativa de KPIs por Fuente de Reclutamiento")
        fuentes_kpi = contratados.groupby('fuente_reclutamiento').agg(
            Tiempo_Promedio=('tiempo_contratacion_dias', 'mean'),
            Costo_Promedio=('costo_reclutamiento', 'mean'),
            Total_Contrataciones=('id_candidato', 'count')
        ).reset_index()
        st.dataframe(fuentes_kpi)
        st.plotly_chart(px.bar(fuentes_kpi, x='fuente_reclutamiento', y='Tiempo_Promedio', title='Tiempo Promedio por Fuente'), use_container_width=True)
        st.plotly_chart(px.bar(fuentes_kpi, x='fuente_reclutamiento', y='Costo_Promedio', title='Costo Promedio por Fuente'), use_container_width=True)
        st.plotly_chart(px.bar(fuentes_kpi, x='fuente_reclutamiento', y='Total_Contrataciones', title='Total de Contrataciones por Fuente'), use_container_width=True)

        st.subheader("🔍 Comparativa de KPIs por Nivel")
        nivel_kpi = contratados.groupby('nivel').agg(
            Tiempo_Promedio=('tiempo_contratacion_dias', 'mean'),
            Costo_Promedio=('costo_reclutamiento', 'mean'),
            Total_Contrataciones=('id_candidato', 'count')
        ).reset_index()
        st.dataframe(nivel_kpi)
        st.plotly_chart(px.bar(nivel_kpi, x='nivel', y='Tiempo_Promedio', title='Tiempo Promedio por Nivel'), use_container_width=True)
        st.plotly_chart(px.bar(nivel_kpi, x='nivel', y='Costo_Promedio', title='Costo Promedio por Nivel'), use_container_width=True)
        st.plotly_chart(px.bar(nivel_kpi, x='nivel', y='Total_Contrataciones', title='Total de Contrataciones por Nivel'), use_container_width=True)

        st.subheader("🔍 Comparativa de KPIs por Departamento")
        dept_kpi = contratados.groupby('departamento').agg(
            Tiempo_Promedio=('tiempo_contratacion_dias', 'mean'),
            Costo_Promedio=('costo_reclutamiento', 'mean'),
            Total_Contrataciones=('id_candidato', 'count')
        ).reset_index()
        st.dataframe(dept_kpi)
        st.plotly_chart(px.bar(dept_kpi, x='departamento', y='Tiempo_Promedio', title='Tiempo Promedio por Departamento'), use_container_width=True)
        st.plotly_chart(px.bar(dept_kpi, x='departamento', y='Costo_Promedio', title='Costo Promedio por Departamento'), use_container_width=True)
        st.plotly_chart(px.bar(dept_kpi, x='departamento', y='Total_Contrataciones', title='Total de Contrataciones por Departamento'), use_container_width=True)

        st.subheader("🔍 Comparativa de KPIs por Puesto")
        puesto_kpi = contratados.groupby('puesto').agg(
            Tiempo_Promedio=('tiempo_contratacion_dias', 'mean'),
            Costo_Promedio=('costo_reclutamiento', 'mean'),
            Total_Contrataciones=('id_candidato', 'count')
        ).reset_index()
        st.dataframe(puesto_kpi)
        st.plotly_chart(px.bar(puesto_kpi, x='puesto', y='Tiempo_Promedio', title='Tiempo Promedio por Puesto'), use_container_width=True)
        st.plotly_chart(px.bar(puesto_kpi, x='puesto', y='Costo_Promedio', title='Costo Promedio por Puesto'), use_container_width=True)
        st.plotly_chart(px.bar(puesto_kpi, x='puesto', y='Total_Contrataciones', title='Total de Contrataciones por Puesto'), use_container_width=True)

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



