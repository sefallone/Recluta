import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

# Configurar página
st.set_page_config(page_title="Dashboard Marycel Mercado", layout="wide")

# Sidebar - Imagen superior
st.sidebar.image("hunter1.jpg", use_container_width=True)
st.sidebar.markdown("""
<div style='text-align: center; color: #FFFFFF; font-weight: bold; margin-top: 10px;'>
    Marycel Mercado<br>Senior People Hunter
    <hr style='border: none; height: 2px; background-color: #FFFFFF; margin-top: 10px;'>
    <div style='font-size: 12px; font-weight: normal; margin-top: 10px;'>
        🌐 <a href='https://www.thepeoplehunter.com' target='_blank' style='color: #FFFFFF; text-decoration: none;'>www.thepeoplehunter.com</a><br>
        🌐 <a href='https://www.themedicalhunter.com' target='_blank' style='color: #FFFFFF; text-decoration: none;'>www.themedicalhunter.com</a><br>
        📞 <span style='color: #FFFFFF;'>Teléfono: +34 667 668 047</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Título
st.title("📊 Marycel Mercado THE PEOPLE HUNTER")

# Subida de archivo
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

    # Sidebar - Filtros
    st.sidebar.header("Filtros")
    año = st.sidebar.multiselect("Año de aplicación", df['año_aplicacion'].unique(), default=df['año_aplicacion'].unique())
    departamento = st.sidebar.multiselect("Departamento", df['departamento'].unique(), default=df['departamento'].unique())
    nivel = st.sidebar.multiselect("Nivel", df['nivel'].dropna().unique(), default=df['nivel'].dropna().unique())
    puesto = st.sidebar.multiselect("Puesto", df['puesto'].dropna().unique(), default=df['puesto'].dropna().unique())
    fuente = st.sidebar.multiselect("Fuente de reclutamiento", df['fuente_reclutamiento'].dropna().unique(), default=df['fuente_reclutamiento'].dropna().unique())

    # Filtrado de datos
    filtered_df = df[
        (df['año_aplicacion'].isin(año)) &
        (df['departamento'].isin(departamento)) &
        (df['nivel'].isin(nivel)) &
        (df['puesto'].isin(puesto)) &
        (df['fuente_reclutamiento'].isin(fuente))
    ]

    # Tabs
    kpi_tab, grafico_tab, detalle_tab = st.tabs(["📌 KPIs", "📈 Gráficos", "📋 Detalle"])

    with kpi_tab:
        st.subheader("📈 Resultados Generales")

        # Primera fila de KPIs
        col1, col2, col3, col4 = st.columns(4)
        tiempo_prom = filtered_df['tiempo_contratacion_dias'].mean()
        total_candidatos = len(filtered_df)
        contratados = filtered_df[filtered_df['estado_proceso'] == 'Oferta aceptada']
        tasa_conversion = (len(contratados) / total_candidatos * 100) if total_candidatos else 0
        ofertas_totales = filtered_df[filtered_df['estado_proceso'].str.contains("Oferta", na=False)]
        ofertas_aceptadas = ofertas_totales[ofertas_totales['oferta_aceptada'] == True]
        tasa_aceptacion = (len(ofertas_aceptadas) / len(ofertas_totales) * 100) if len(ofertas_totales) else 0
        costo_prom = contratados['costo_reclutamiento'].mean()

        col1.metric("⏱️ Tiempo promedio contratación", f"{tiempo_prom:.1f} días", help="Promedio de días entre la fecha de aplicación y la aceptación de oferta.")
        col2.metric("🎯 Tasa de conversión", f"{tasa_conversion:.1f}%", help="Porcentaje de candidatos contratados sobre el total de candidatos.")
        col3.metric("📩 Tasa aceptación de oferta", f"{tasa_aceptacion:.1f}%", help="Porcentaje de ofertas aceptadas sobre el total de ofertas.")
        col4.metric("💰 Costo por contratación", f"€{costo_prom:,.2f}", help="Promedio de costos por contratación exitosa.")

        # Espaciado visual
        st.markdown("<div style='margin-top: 1rem'></div>", unsafe_allow_html=True)

        # Segunda fila de KPIs
        col5, col6, col7 = st.columns(3)
        col5.metric("👥 Contrataciones", f"{len(contratados)}", help="Número total de candidatos que aceptaron una oferta.")

        tasa_ofertas_realizadas = (len(ofertas_totales) / total_candidatos * 100) if total_candidatos else 0
        col6.metric("📤 Tasa de ofertas realizadas", f"{tasa_ofertas_realizadas:.1f}%", help="Porcentaje de candidatos que recibieron oferta.")

        if not contratados.empty:
            fuente_principal = contratados['fuente_reclutamiento'].value_counts(normalize=True).idxmax()
            porcentaje_fuente = contratados['fuente_reclutamiento'].value_counts(normalize=True).max() * 100
            col7.metric("🏆 Fuente principal de contratación", f"{fuente_principal} ({porcentaje_fuente:.1f}%)", help="Fuente con mayor proporción de contrataciones.")

        style_metric_cards(background_color="#1647ec", border_left_color="#ec16dc", border_color="#ec16dc")

    with grafico_tab:
        st.subheader("📊 Gráficos")

        fuente_data = contratados['fuente_reclutamiento'].value_counts(normalize=True) * 100
        fig1 = px.bar(fuente_data, x=fuente_data.index, y=fuente_data.values, labels={'x': 'Fuente', 'y': 'Porcentaje'}, title="Fuente de contratación (%)")
        st.plotly_chart(fig1, use_container_width=True)

        contratados['mes_aplicacion'] = pd.to_datetime(contratados['mes_aplicacion'], errors='coerce')
        mensual = contratados.groupby('mes_aplicacion').size().reset_index(name='Contrataciones')
        fig2 = px.line(mensual, x='mes_aplicacion', y='Contrataciones', title="Contrataciones por Mes")
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.box(contratados, y='tiempo_contratacion_dias', points="all", title="Distribución tiempo de contratación")
        st.plotly_chart(fig3, use_container_width=True)

        # Comparativas
        st.subheader("📊 Comparativas por categoría")

        tiempo_por_nivel = contratados.groupby('nivel')['tiempo_contratacion_dias'].mean().reset_index()
        fig4 = px.bar(tiempo_por_nivel, x='nivel', y='tiempo_contratacion_dias', title="Tiempo Promedio de Contratación por Nivel")
        st.plotly_chart(fig4, use_container_width=True)

        costo_por_fuente = contratados.groupby('fuente_reclutamiento')['costo_reclutamiento'].mean().reset_index()
        fig5 = px.bar(costo_por_fuente, x='fuente_reclutamiento', y='costo_reclutamiento', title="Costo Promedio por Fuente de Reclutamiento")
        st.plotly_chart(fig5, use_container_width=True)

        ofertas_por_departamento = filtered_df[filtered_df['estado_proceso'].str.contains("Oferta", na=False)]
        aceptadas_por_dpto = ofertas_por_departamento.groupby('departamento')['oferta_aceptada'].mean().reset_index()
        aceptadas_por_dpto['oferta_aceptada'] *= 100
        fig6 = px.bar(aceptadas_por_dpto, x='departamento', y='oferta_aceptada', title="Tasa de Aceptación de Oferta por Departamento (%)")
        st.plotly_chart(fig6, use_container_width=True)

    with detalle_tab:
        st.subheader("📋 Detalle de Datos Filtrados")
        st.dataframe(filtered_df)
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar datos filtrados", data=csv, file_name="reclutamiento_filtrado.csv", mime="text/csv")

else:
    st.warning("Por favor sube un archivo Excel para visualizar el dashboard.")













