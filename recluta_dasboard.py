import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(page_title="Dashboard de Reclutamiento", layout="wide", page_icon="📊")

# Título
st.title("📊 Dashboard de Reclutamiento - KPIs de RH")

# Generar datos de ejemplo (en un caso real, estos vendrían de una base de datos)
def generar_datos_ejemplo(num_candidatos=100):
    fuentes = ['LinkedIn', 'Portal interno', 'Referencias', 'Bolsa de trabajo', 'Indeed', 'Glassdoor', 'Eventos']
    puestos = ['Desarrollador', 'Diseñador', 'Gerente', 'Analista', 'Marketing', 'Ventas', 'Soporte']
    estados = ['Aplicó', 'Entrevista inicial', 'Pruebas técnicas', 'Entrevista final', 'Oferta extendida', 'Oferta aceptada', 'Rechazado']
    
    data = []
    for i in range(num_candidatos):
        fecha_aplicacion = datetime.now() - timedelta(days=random.randint(1, 90))
        fuente = random.choice(fuentes)
        puesto = random.choice(puestos)
        estado = random.choices(
            estados, 
            weights=[0.15, 0.15, 0.15, 0.15, 0.1, 0.2, 0.1], 
            k=1
        )[0]
        
        if estado in ['Oferta extendida', 'Oferta aceptada']:
            fecha_oferta = fecha_aplicacion + timedelta(days=random.randint(10, 30))
            aceptada = estado == 'Oferta aceptada'
            tiempo_contratacion = (fecha_oferta - fecha_aplicacion).days if aceptada else None
        else:
            fecha_oferta = None
            aceptada = False
            tiempo_contratacion = None
            
        costo = random.randint(500, 5000) if estado == 'Oferta aceptada' else random.randint(100, 2000)
        
        data.append({
            'ID': i+1,
            'Nombre': f'Candidato {i+1}',
            'Puesto': puesto,
            'Fuente': fuente,
            'Fecha aplicación': fecha_aplicacion,
            'Estado': estado,
            'Fecha oferta': fecha_oferta,
            'Oferta aceptada': aceptada,
            'Tiempo contratación (días)': tiempo_contratacion,
            'Costo reclutamiento': costo
        })
    
    return pd.DataFrame(data)

# Cargar datos
df = generar_datos_ejemplo(200)

# Sidebar con filtros
st.sidebar.header("Filtros")
puesto_seleccionado = st.sidebar.selectbox("Seleccionar puesto", ['Todos'] + list(df['Puesto'].unique()))
fuente_seleccionada = st.sidebar.selectbox("Seleccionar fuente", ['Todas'] + list(df['Fuente'].unique()))
rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    [df['Fecha aplicación'].min(), df['Fecha aplicación'].max()]
)

# Aplicar filtros
if puesto_seleccionado != 'Todos':
    df = df[df['Puesto'] == puesto_seleccionado]
if fuente_seleccionada != 'Todas':
    df = df[df['Fuente'] == fuente_seleccionada]
df = df[(df['Fecha aplicación'] >= pd.to_datetime(rango_fechas[0])) & 
        (df['Fecha aplicación'] <= pd.to_datetime(rango_fechas[1]))]

# KPIs principales
st.header("Indicadores Clave de Rendimiento (KPIs)")

# Dividir en columnas
col1, col2, col3, col4 = st.columns(4)

# KPI 1: Tiempo promedio de contratación
contratados = df[df['Oferta aceptada'] == True]
tiempo_promedio = contratados['Tiempo contratación (días)'].mean()
col1.metric(
    label="⏳ Tiempo Promedio de Contratación", 
    value=f"{int(tiempo_promedio)} días" if not np.isnan(tiempo_promedio) else "N/A",
    delta=f"{(tiempo_promedio - 35):.1f} días vs meta" if not np.isnan(tiempo_promedio) else None
)

# KPI 2: Tasa de conversión
total_candidatos = len(df)
candidatos_contratados = len(contratados)
tasa_conversion = (candidatos_contratados / total_candidatos) * 100 if total_candidatos > 0 else 0
col2.metric(
    label="🔄 Tasa de Conversión", 
    value=f"{tasa_conversion:.1f}%",
    delta=f"{(tasa_conversion - 15):.1f}% vs meta" if total_candidatos > 0 else None
)

# KPI 3: Tasa de aceptación de ofertas
ofertas_extendidas = len(df[df['Estado'].isin(['Oferta extendida', 'Oferta aceptada'])])
ofertas_aceptadas = len(contratados)
tasa_aceptacion = (ofertas_aceptadas / ofertas_extendidas) * 100 if ofertas_extendidas > 0 else 0
col3.metric(
    label="✅ Tasa de Aceptación de Ofertas", 
    value=f"{tasa_aceptacion:.1f}%" if ofertas_extendidas > 0 else "N/A",
    delta=f"{(tasa_aceptacion - 65):.1f}% vs meta" if ofertas_extendidas > 0 else None
)

# KPI 4: Costo por contratación
costo_total = df[df['Oferta aceptada']]['Costo reclutamiento'].sum()
costo_por_contratacion = costo_total / candidatos_contratados if candidatos_contratados > 0 else 0
col4.metric(
    label="💰 Costo por Contratación", 
    value=f"${costo_por_contratacion:,.0f}" if candidatos_contratados > 0 else "N/A",
    delta=f"${(costo_por_contratacion - 2500):,.0f} vs meta" if candidatos_contratados > 0 else None
)

# Gráficos y visualizaciones
st.header("Visualización de Datos")

# Gráfico 1: Fuentes de contratación
st.subheader("Fuentes de Contratación")
fuentes_contratacion = contratados['Fuente'].value_counts().reset_index()
fuentes_contratacion.columns = ['Fuente', 'Contrataciones']
fuentes_contratacion['Porcentaje'] = (fuentes_contratacion['Contrataciones'] / fuentes_contratacion['Contrataciones'].sum()) * 100

fig1 = px.pie(
    fuentes_contratacion, 
    values='Contrataciones', 
    names='Fuente', 
    hole=0.3,
    title='Distribución por Fuente de Contratación'
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Tiempo de contratación por puesto
st.subheader("Tiempo de Contratación por Puesto")
if not contratados.empty:
    fig2 = px.box(
        contratados, 
        x='Puesto', 
        y='Tiempo contratación (días)',
        title='Distribución del Tiempo de Contratación por Puesto'
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No hay datos de contrataciones para mostrar.")

# Gráfico 3: Embudo de reclutamiento
st.subheader("Embudo de Reclutamiento")
embudo = df['Estado'].value_counts().reset_index()
embudo.columns = ['Estado', 'Cantidad']
orden_estados = ['Aplicó', 'Entrevista inicial', 'Pruebas técnicas', 'Entrevista final', 'Oferta extendida', 'Oferta aceptada', 'Rechazado']
embudo['Estado'] = pd.Categorical(embudo['Estado'], categories=orden_estados, ordered=True)
embudo = embudo.sort_values('Estado')

fig3 = px.funnel(
    embudo, 
    x='Cantidad', 
    y='Estado',
    title='Embudo de Reclutamiento'
)
st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Costo por fuente
st.subheader("Costo Promedio por Fuente")
if not contratados.empty:
    costo_fuente = contratados.groupby('Fuente')['Costo reclutamiento'].mean().reset_index()
    fig4 = px.bar(
        costo_fuente, 
        x='Fuente', 
        y='Costo reclutamiento',
        title='Costo Promedio de Reclutamiento por Fuente'
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("No hay datos de contrataciones para mostrar.")

# Tabla de datos detallados
st.header("Datos Detallados")
st.dataframe(df.sort_values('Fecha aplicación', ascending=False))

# KPIs adicionales en expanders
with st.expander("📈 KPIs Adicionales"):
    col5, col6, col7 = st.columns(3)
    
    # KPI 5: Ratio de candidatos por puesto
    ratio_candidatos_puesto = total_candidatos / len(df['Puesto'].unique()) if len(df['Puesto'].unique()) > 0 else 0
    col5.metric(
        label="👥 Ratio de Candidatos por Puesto", 
        value=f"{ratio_candidatos_puesto:.1f}",
        delta=f"{(ratio_candidatos_puesto - 10):.1f} vs meta" if len(df['Puesto'].unique()) > 0 else None
    )
    
    # KPI 6: Tasa de abandono del proceso
    abandonos = len(df[df['Estado'] == 'Rechazado'])
    tasa_abandono = (abandonos / total_candidatos) * 100 if total_candidatos > 0 else 0
    col6.metric(
        label="🚪 Tasa de Abandono del Proceso", 
        value=f"{tasa_abandono:.1f}%",
        delta=f"{(tasa_abandono - 20):.1f}% vs meta" if total_candidatos > 0 else None
    )
    
    # KPI 7: Eficiencia del reclutamiento
    eficiencia = (candidatos_contratados / (total_candidatos - abandonos)) * 100 if (total_candidatos - abandonos) > 0 else 0
    col7.metric(
        label="⚡ Eficiencia de Reclutamiento", 
        value=f"{eficiencia:.1f}%",
        delta=f"{(eficiencia - 25):.1f}% vs meta" if (total_candidatos - abandonos) > 0 else None
    )

# Notas finales
st.markdown("---")
st.caption("""
*Notas:*  
- Los datos mostrados son generados automáticamente para propósitos de demostración.  
- Los valores delta comparan con metas hipotéticas.  
- Filtra los datos usando los controles en la barra lateral para análisis específicos.
""")
