import streamlit as st
import pandas as pd
import funciones as fn
import folium
import streamlit_folium
from sqlalchemy import create_engine


@st.cache_data()
def cargar_datos():
    base= fn.leer_data()
    return base

base = cargar_datos()

st.sidebar.subheader("Filtros")
habs = st.sidebar.checkbox('Habitaciones')
bans = st.sidebar.checkbox('Baños')
area = st.sidebar.checkbox('Area')
rentabilidad = st.sidebar.checkbox('Rentabilidad')

st.subheader("Precio publicación")

col1, col2 = st.columns(2)
with col1:
    min_compra = st.number_input("Mínimo", value=180000, step= 10000)
with col2:
    max_compra = st.number_input("Máximo", value=200000, step= 10000)

col1, col2 = st.columns(2)
with col1:
    if habs:
        habitaciones = st.number_input("Habiaciones", value=4, step= 1)
        habitaciones = [habitaciones]
    else:
        habitaciones = base['habitaciones'].unique()
with col2:
    if bans:
        banos = st.number_input("Baños", value=2, step= 1)
        banos = [banos]
    else:
        banos = base['banos'].unique()

col1, col2 = st.columns(2)
with col1:      
    if area:
        area_min = st.number_input('Superficie mínima', value=100, step=10)
    else:
        area_min = base['area'].min()

with col2:
    if rentabilidad:
        rent = st.number_input('ROI mínimo', value=6.0, step=0.5)
    else:
        rent = base['roi2'].min()

premium = ['Salamanca', 'Chamartín', 'Chamberí', 'Retiro']
centro = ['Centro']
m30 = ['Centro', 'Arganzuela', 'Retiro', 'Salamanca', 'Chamartín', 'Tetuán', 'Chamberí']
fuera_m30 = ['Moncloa - Aravaca', 'Hortaleza', 'Fuencarral - El Pardo', 'Ciudad lineal', 
             'Barajas', 'San Blas - Canillejas', 'Moratalaz', 'Vicálvaro','Villa de Vallecas',
             'Latina', 'Carabanchel', 'Usera', 'Puente de Vallecas', 'Villaverde']
todos = base['distrito'].unique()

opciones = ['premium', 'centro', 'm30', 'fuera_m30', 'ninguna']
restriccion = st.selectbox('Restricción de zona', options=opciones, index=4)
if restriccion == 'premium':
    zona = premium
elif restriccion == 'centro':
    zona = centro
elif restriccion == 'm30':
    zona = m30
elif restriccion == 'fuera_m30':
    zona = fuera_m30
else:
    zona = todos

base = base[(base['precio']>=min_compra)&(base['precio']<=max_compra)&(base['habitaciones'].isin(habitaciones))&
            (base['banos'].isin(banos))&(base['distrito'].isin(zona))&(base['area']>=area_min)&
            (base['roi2']>=rent)]


if len(base) == 0:
    st.warning("No hay datos disponibles con los filtros seleccionados.")

else:


    m = folium.Map(location=[base['latitud'].mean(), base['longitud'].mean()], zoom_start=14)

    # Iterar sobre las filas de tu DataFrame
    for index, row in base.iterrows():
        # Seleccionar el color según el valor de la columna roi1
        if row['roi2'] < 4.0:
            color = 'black'
        elif (row['roi2'] >= 4.0) & (row['roi2'] < 6.0):
            color = 'red'
        elif (row['roi2'] >= 6.0) & (row['roi2'] < 8.0):
            color = 'blue'
        else:
            color = 'green'

        popup_html = f"<b>Precio:</b> {row['precio']}<br><b>ROI1:</b> {row['roi1']}<br><b>ROI2:</b> {row['roi2']}<br><b>URL:</b> <a href='{row['url_activo']}' target='_blank'>{row['url_activo']}</a><br><button type='submit' onclick='guardar_oportunidades({row.to_dict()})'>Guardar oportunidad</button>"

        # Crear un marcador con el color correspondiente y popup con dos columnas
        folium.Marker(
            location=[row['latitud'], row['longitud']],
             popup=folium.Popup(html=popup_html, max_width=300),
            icon=folium.Icon(color=color),
        ).add_to(m)
        

    st.metric('Número de inmuebles', base.shape[0])
    streamlit_folium.folium_static(m)

def guardar_oportunidades (row):
    user     = 'external_cfdata'
    password = '9hW6im_79'
    host     = '87.106.125.178'
    database = 'pdfcf'
    engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, password, host, 3306, database))
    dbConnection = engine.connect()

    df = pd.DataFrame([row]) 
    df.to_sql("oportunidades2",dbConnection, if_exists="append", index=False)

    dbConnection.close()  
