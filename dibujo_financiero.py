import streamlit as st
import pandas as pd
import funciones as fn
import geopandas as gpd

@st.cache_data()
def cargar_datos():
    base= fn.leer_data()
    distritos, barrios = fn.dis_bar()
    return base, distritos, barrios  # Hacer copias de los objetos

base, distritos, barrios = cargar_datos()

capital_disponible = st.number_input('Capital disponible', value=300000, step= 10000)
habitaciones = st.sidebar.selectbox('Habitaciones', sorted(base['habitaciones'].unique()))
banos = st.sidebar.selectbox('banos', sorted(base['banos'].unique()))

total_minimo = capital_disponible*0.97
total_maximo = capital_disponible*1.03
base = base.loc[(base['total_cashflow_iva']>=total_minimo)&(base['total_cashflow_iva']<=total_maximo)]
base = base.loc[(base['habitaciones']==habitaciones)&(base['banos']==banos)]
if len(base) == 0:
    st.warning("No hay datos disponibles con los filtros seleccionados.")



else:
    minimo = base['precio'].idxmin()
    minimo = base.loc[minimo]
    maximo = base['precio'].idxmax()
    maximo = base.loc[maximo]

    proyecto = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Total Proyecto</p>'
    st.markdown(proyecto, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(base['total_cashflow_iva'].min()))
    with col2:
        st.metric('máximo', int(base['total_cashflow_iva'].max()))

    st.metric('Total de oportunidades:', base.shape[0])

    compra = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Precio Compra</p>'
    st.markdown(compra, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(minimo['precio_compra']))
    with col2:
        st.metric('máximo', int(maximo['precio_compra']))
    
    itp = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">ITP</p>'
    st.markdown(itp, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(minimo['itp']))
    with col2:
        st.metric('máximo', int(maximo['itp']))

    inmo = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Comisión inmobiliaria</p>'
    st.markdown(inmo, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(minimo['comision_venta_iva']))
    with col2:
        st.metric('máximo', int(maximo['comision_venta_iva']))

    superficie = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Superficie</p>'
    st.markdown(superficie, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(minimo['area_util']))
    with col2:
        st.metric('máximo', int(maximo['area_util']))

    obra = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Obra</p>'
    st.markdown(obra, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(minimo['obra_total_iva']))
    with col2:
        st.metric('máximo', int(maximo['obra_total_iva']))

    cf = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Comisión CF</p>'
    st.markdown(cf, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(minimo['cf_fee_iva']))
    with col2:
        st.metric('máximo', int(maximo['cf_fee_iva']))
