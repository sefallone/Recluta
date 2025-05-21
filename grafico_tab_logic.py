import streamlit as st
import pandas as pd
import plotly.express as px

def show_grafico_tab(filtered_df, contratados):
    st.title("📈 Visualizaciones del Proceso de Reclutamiento")

    st.subheader("Contrataciones por Fuente")
    fuente_data = contratados['fuente_reclutamiento'].value_counts(normalize=True) * 100
    fig1 = px.bar(
        x=fuente_data.index,
        y=fuente_data.values,
        labels={'x': 'Fuente', 'y': 'Porcentaje'},
        title="Fuente de contratación (%)"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Evolución mensual de contrataciones")
    contratados['mes_aplicacion'] = pd.to_datetime(contratados['mes_aplicacion'], errors='coerce')
    mensual = contratados.groupby('mes_aplicacion').size().reset_index(name='Contrataciones')
    fig2 = px.line(mensual, x='mes_aplicacion', y='Contrataciones', title="Contrataciones por Mes")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribución del Tiempo de Contratación")
    fig3 = px.box(contratados, y='tiempo_contratacion_dias', points="all", title="Distribución tiempo de contratación")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📋 Detalle de Datos Filtrados")
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar datos filtrados", data=csv, file_name="reclutamiento_filtrado.csv", mime="text/csv")
