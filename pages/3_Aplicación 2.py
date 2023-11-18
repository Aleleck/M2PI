import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import geopandas as gpd
import matplotlib 
import matplotlib.pyplot as plt 
warnings.filterwarnings('ignore')

st.title(":motor_scooter: Hurto de motos en medellin :motor_scooter:")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)



df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'assets', 'hurto_de_moto.csv'))


col1, col2 = st.columns((2))
df["fecha_hecho"] = pd.to_datetime(df["fecha_hecho"]).dt.tz_convert(None)

starDate = pd.to_datetime(df["fecha_hecho"]).min()
endDate = pd.to_datetime(df["fecha_hecho"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Fecha de inicio", starDate))
with col2:
    date2 = pd.to_datetime(st.date_input("Fecha final", endDate))

df = df[(df["fecha_hecho"] >= pd.Timestamp(date1)) & (df["fecha_hecho"] <= pd.Timestamp(date2))].copy()

st.sidebar.header("Escoja su filtro: ")
comuna = st.sidebar.multiselect("Escoge la comuna", df["sede_receptora"].unique())
if not comuna:
    df2 = df.copy()
else:
    df2 = df[df["sede_receptora"].isin(comuna)]

barrio = st.sidebar.multiselect("Escoge el barrio", df2["nombre_barrio"].unique())

df['fecha_hecho'] = pd.to_datetime(df['fecha_hecho'])
df['year'] = df['fecha_hecho'].dt.year
theft_count_year = df.groupby(['year']).size().reset_index(name='Cantidad')
theft_count_year['Porcentaje'] = theft_count_year['Cantidad'] / theft_count_year['Cantidad'].sum() * 100

with col1:
    fig = px.bar(theft_count_year, x='year', y='Cantidad')
    fig.update_xaxes(tickmode = 'linear', tick0 = min(df['year']), dtick = 1)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(theft_count_year, values='Porcentaje', names='year', title='Porcentaje de hurtos por año')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

mapa = gpd.read_file(os.path.join(os.path.dirname(__file__), 'assets', 'LimiteComunaCorregimiento_2014.shp')).set_index('CODIGO')


hurto = pd.read_csv(os.path.join(os.path.dirname(__file__), 'assets', 'hurto_de_moto.csv')).set_index('codigo_comuna')


mapa.index = mapa.index.astype(str).str.zfill(2)
hurto.index = hurto.index.astype(str).str.zfill(2)

hurtos_agg = hurto.groupby('codigo_comuna')['sede_receptora'].agg(['count'])
hurtos_agg = hurtos_agg.rename(columns={'count': 'hurtos'})
datos = mapa.merge(hurtos_agg, left_index=True, right_index=True)

datos = mapa.merge(hurtos_agg, left_index=True, right_index=True)
fig = px.choropleth(datos,
                    geojson=datos.geometry,
                    locations=datos.index,
                    color='hurtos',
                    color_continuous_scale="Viridis",
                    hover_name=datos.NOMBRE,
                    projection="natural earth")
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.header('Mapa Medellin Hurtos')
st.plotly_chart(fig, use_container_width=True)
