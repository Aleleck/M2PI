import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import plotly.graph_objects as go
import geopandas as gpd

warnings.filterwarnings('ignore')

st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.title('Analisis de hurtos en la ciudad de Medellín.')
hurto = pd.read_excel(os.path.join(os.path.dirname(__file__), 'assets', 'Hurtos.xlsx'))
hurto['Código Postal'] = hurto['Código Postal'].str.replace('#', '')  # quitar "#"
hurto['Hora Hurto'] = pd.to_datetime(hurto['Hora Hurto'], format='%H:%M:%S')
col1, col2, col3 = st.columns((3))
# Crear un filtro de años
year_range = st.slider("Seleccione un rango de años:", min_value=int(hurto['Fecha Hurto Año'].min()), max_value=int(hurto['Fecha Hurto Año'].max()), value=(int(hurto['Fecha Hurto Año'].min()), int(hurto['Fecha Hurto Año'].max())))

# Filtrar por rango de años seleccionado
hurto_filtered = hurto[(hurto['Fecha Hurto Año'] >= year_range[0]) & (hurto['Fecha Hurto Año'] <= year_range[1])]

# Crear columnas
col1, col2, col3 = st.columns((3, 3, 4))

# En col1, agregar filtro por género (Hombre o Mujer)
with col1:
    gender_filter = st.multiselect("Seleccione el género:", ["Todos", "Hombre", "Mujer"], default=["Todos"])
    if "Todos" not in gender_filter:
        hurto_filtered = hurto_filtered[hurto_filtered['Sexo'].isin(gender_filter)]

# En col2, agregar filtro por rango de edad
with col2:
    age_ranges = st.multiselect("Seleccione el rango de edad:", ["Todos", "10-20", "21-30", "31-40", "41-50", "51-60", "Más de 60"], default=["Todos"])
    if "Todos" not in age_ranges:
        age_filter = []
        for age_range in age_ranges:
            if age_range == "Más de 60":
                age_filter.extend(list(range(61, 200)))  # Usar un número grande para representar más de 60
            else:
                lower, upper = map(int, age_range.split('-'))
                age_filter.extend(list(range(lower, upper + 1)))

        hurto_filtered = hurto_filtered[hurto_filtered['Edad'].isin(age_filter)]

# En col3, agregar filtro por modalidad de hurto
with col3:
    theft_modes = st.multiselect("Seleccione la modalidad de hurto:", ["Todos"] + list(hurto['Modalidad de hurto'].unique()), default=["Todos"])
    if "Todos" not in theft_modes:
        hurto_filtered = hurto_filtered[hurto_filtered['Modalidad de hurto'].isin(theft_modes)]


# Extraer la hora de la hora
hurto_filtered['Hora'] = hurto_filtered['Hora Hurto'].dt.hour

# Contar la cantidad de hurtos por hora
hxhora_filtered = hurto_filtered.groupby('Hora')['Fecha Hurto Año'].agg(['count']).reset_index()

# Crear gráfico de líneas con Plotly Express
fig = px.line(hxhora_filtered, x='Hora', y='count',
            labels={'Hora': 'Hora del día', 'count': 'Cantidad de hurtos'},
            title=f'Hurto por horas en el rango de años {year_range[0]}-{year_range[1]} ({", ".join(gender_filter)}) - Edades: {", ".join(age_ranges)} - Modalidades: {", ".join(theft_modes)}', width=800, height=400, markers=True)

st.plotly_chart(fig)

# Mapa de hurtos por barrios
mapa = gpd.read_file(os.path.join(os.path.dirname(__file__), 'assets', 'BarrioVereda_2014.shp'))
mapa = mapa.set_index('CODIGO')

# Contar los hurtos por barrio
hurtos_agg = hurto_filtered.groupby('Código Postal')['Barrio'].agg(['count'])
hurtos_agg = hurtos_agg.rename(columns={'count': 'hurtos'})
datos = mapa.merge(hurtos_agg, left_index=True, right_index=True)


# Crear gráfico de choropleth con Plotly Express
fig_mapa = px.choropleth(datos,
                        geojson=datos.geometry,
                        locations=datos.index,
                        color='hurtos',
                        color_continuous_scale="Viridis",
                        hover_name=datos.NOMBRE,
                        hover_data={'NOMBRE': False, 'hurtos': True},
                        projection="natural earth")

fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    autosize=False,
    width=800,
    height=800,
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)
#fig_mapa.update_traces(marker_line_width=1, marker_line_color="white", selector=dict(type='choropleth'))
st.plotly_chart(fig_mapa)
