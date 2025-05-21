import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")
st.title("Dashboard de Reclutamiento 📊")

# Cargar datos
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # ---- KPIs ---- #
    st.header("Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    
    # KPI 1: Tiempo promedio de contratación
    avg_time = df["tiempo_contratacion_dias"].mean()
    col1.metric("Tiempo Promedio de Contratación (días)", f"{avg_time:.1f}")

    # KPI 2: Tasa de conversión
    hired = df[df["estado_proceso"] == "Contratado"].shape[0]  # Ajusta según tus datos
    total_candidates = df.shape[0]
    conversion_rate = (hired / total_candidates) * 100
    col2.metric("Tasa de Conversión (%)", f"{conversion_rate:.1f}")

    # KPI 3: Tasa de aceptación de ofertas
    accepted_offers = df[df["oferta_aceptada"] == "Sí"].shape[0]  # Ajusta según tus datos
    total_offers = df[df["estado_proceso"] == "Oferta"].shape[0]  # Ajusta según tus datos
    acceptance_rate = (accepted_offers / total_offers) * 100 if total_offers > 0 else 0
    col3.metric("Tasa de Aceptación de Ofertas (%)", f"{acceptance_rate:.1f}")

    # KPI 4: Costo promedio por contratación
    avg_cost = df["costo_reclutamiento"].mean()
    col4.metric("Costo Promedio por Contratación", f"${avg_cost:,.0f}")

    # ---- Gráficos ---- #
    st.header("Visualizaciones")
    
    # Gráfico 1: Fuentes de reclutamiento (pie chart)
    fig1 = px.pie(df, names="fuente_reclutamiento", title="Contrataciones por Fuente de Reclutamiento")
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Tiempo de contratación por puesto (bar chart)
    fig2 = px.bar(
        df.groupby("puesto")["tiempo_contratacion_dias"].mean().reset_index(),
        x="puesto",
        y="tiempo_contratacion_dias",
        title="Tiempo Promedio de Contratación por Puesto"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico 3: Tendencias mensuales (línea)
    df["fecha_aplicacion"] = pd.to_datetime(df["fecha_aplicacion"])
    monthly_trends = df.groupby(df["fecha_aplicacion"].dt.to_period("M")).size()
    fig3 = px.line(
        monthly_trends.reset_index(),
        x="fecha_aplicacion",
        y=0,
        title="Candidatos por Mes"
    )
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.warning("Por favor, sube un archivo Excel para comenzar.")
