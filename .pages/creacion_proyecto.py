import streamlit as st
import pandas as pd
import funciones as fn

@st.cache_data()
def cargar_datos():
    base= fn.leer_data()
    return base

base = cargar_datos()
st.title('Bienvenido a Capital Friend')
cliente = st.text_input('Nombre del cliente')
proyecto = st.text_input('Nombre del proyecto')
options = ['Rentee', 'Fix/Hold']
tipo_proyecto = st.selectbox('Tipo de proyecto', options= options)
descripcion = st.text_area('Descripción')
capital_disponible = st.number_input('Capital disponible', value=300000, step= 10000)
distritos = st.multiselect('Distritos', options=sorted(base['distrito'].unique()))

restricciones = st.text_area('Restricciones')

pr = pd.DataFrame(columns=['nombre_cliente', 'nombre_proyecto', 'tipo_proyecto', 'descripcion', 
                           'capital_disponible', 'distritos', 'restricciones_condiciones', 
                           'created_at', 'updated_at'])

distritos = ','.join(distritos)

# Almacenar los resultados en el DataFrame final
pr = pr._append({'nombre_cliente':cliente,'nombre_proyecto': proyecto, 
                'tipo_proyecto': tipo_proyecto, 'descripcion': descripcion, 
                'capital_disponible': capital_disponible, 'distritos': distritos,
                'restricciones_condiciones': restricciones, 
                'created_at': pd.Timestamp.now(), 
                'updated_at': pd.Timestamp.now()}, ignore_index=True)


if st.button('Crear proyecto'):
    fn.crear_proyecto(pr)
    st.write('Proyecto creado')
    total_minimo = capital_disponible*0.97
    total_maximo = capital_disponible*1.03
    base = base.loc[(base['total_cashflow_iva']>=total_minimo)&(base['total_cashflow_iva']<=total_maximo)]
    if len(base) == 0:
        st.warning("No hay datos disponibles con los filtros seleccionados.")
    else:
            proyecto = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Total Proyecto</p>'
    st.markdown(proyecto, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(total_minimo))
    with col2:
        st.metric('máximo', int(total_maximo))

    st.metric('Total de oportunidades:', base.shape[0])

    compra = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Precio Compra</p>'
    st.markdown(compra, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(base['precio_compra'].min()))
    with col2:
        st.metric('máximo', int(base['precio_compra'].max()))

    superficie = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Superficie</p>'
    st.markdown(superficie, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(base['area_util'].min()))
    with col2:
        st.metric('máximo', int(base['area_util'].max()))

    obra = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">Obra</p>'
    st.markdown(obra, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(base['obra_total_iva'].min()))
    with col2:
        st.metric('máximo', int(base['obra_total_iva'].max()))

    itp = '<p style="font-family:sans-serif; color:Gold; font-size: 25px;">ITP</p>'
    st.markdown(itp, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric('mínimo', int(base['itp'].min()))
    with col2:
        st.metric('máximo', int(base['itp'].max()))
