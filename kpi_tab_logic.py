import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

def show_kpi_tab(filtered_df, contratados):
    st.title("📌 Indicadores Clave (KPIs)")

    col1, col2, col3, col4, col5 = st.columns(5)

    tiempo_prom = filtered_df['tiempo_contratacion_dias'].mean()
    col1.metric("⏱️ Tiempo promedio contratación", f"{tiempo_prom:.1f} días")

    total_candidatos = len(filtered_df)
    tasa_conversion = (len(contratados) / total_candidatos * 100) if total_candidatos else 0
    col2.metric("🎯 Tasa de conversión", f"{tasa_conversion:.1f}%")

    ofertas_totales = filtered_df[filtered_df['estado_proceso'].str.contains("Oferta", na=False)]
    ofertas_aceptadas = ofertas_totales[ofertas_totales['oferta_aceptada'] == True]
    tasa_aceptacion = (len(ofertas_aceptadas) / len(ofertas_totales) * 100) if len(ofertas_totales) else 0
    col3.metric("📩 Tasa aceptación de oferta", f"{tasa_aceptacion:.1f}%")

    costo_prom = contratados['costo_reclutamiento'].mean()
    col4.metric("💰 Costo por contratación", f"€{costo_prom:,.2f}")

    col5.metric("👥 Contrataciones", f"{len(contratados)}")

    style_metric_cards(background_color="#f0f2f6", border_left_color="#1f77b4", border_color="#FFFFFF")

    st.subheader("🔍 Comparativas de KPIs")

    dimensiones = {
        "Fuente de Reclutamiento": 'fuente_reclutamiento',
        "Nivel": 'nivel',
        "Departamento": 'departamento',
        "Puesto": 'puesto'
    }

    for nombre, columna in dimensiones.items():
        st.markdown(f"### {nombre}")
        df_grouped = contratados.groupby(columna).agg(
            Tiempo_Promedio=('tiempo_contratacion_dias', 'mean'),
            Costo_Promedio=('costo_reclutamiento', 'mean'),
            Total_Contrataciones=('id_candidato', 'count')
        ).reset_index()

        st.dataframe(df_grouped)

        fig1 = px.bar(df_grouped, x=columna, y='Tiempo_Promedio', title=f'Tiempo Promedio por {nombre}')
        fig2 = px.bar(df_grouped, x=columna, y='Costo_Promedio', title=f'Costo Promedio por {nombre}')
        fig3 = px.bar(df_grouped, x=columna, y='Total_Contrataciones', title=f'Total de Contrataciones por {nombre}')

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
