import pandas as pd
import mysql.connector as sql
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st
from sqlalchemy import create_engine


def leer_data():
    user     = 'external_cfdata'
    password = '5g32W1i&o'
    host     = '87.106.125.178'
    database = 'pdfcf'
    db_connection = sql.connect(user=user, password=password, host=host, database=database)

    base = pd.read_sql(f"""SELECT tp.*
                            FROM data_idealista_total_proyecto as tp
                            
                        """ , con=db_connection) 
    return base

def dis_bar():
    path = 'distritos/Distritos_20210712.shp'
    distritos = gpd.read_file(path)
    distritos = distritos[['NOMBRE', 'geometry']]

    path2 = 'barrios/Barrios.shp'
    barrios = gpd.read_file(path2)

    return distritos, barrios

def grafica_mapa_distrito(gdf, indicador):
    fig, ax = plt.subplots(figsize=(20, 20))
    cmap = plt.cm.RdYlGn # Puedes elegir otro mapa de colores según tus preferencias
    gdf = gdf.fillna(0)
    # Grafica los polígonos utilizando geopandas y matplotlib
   # Filtrar los datos para obtener solo los elementos con yield != 0
    gdf_filtered = gdf[gdf[indicador] != 0]

    # Grafica los polígonos utilizando geopandas y matplotlib
    gdf_filtered.plot(column=indicador, cmap='summer', linewidth=2, ax=ax, edgecolor="0.8", legend=True)

    # Filtrar los datos para obtener solo los elementos con yield = 0
    gdf_zero_yield = gdf[gdf[indicador] == 0]

    # Graficar los elementos con yield = 0 en blanco
    gdf_zero_yield.plot(color="white", ax=ax, linewidth=2, edgecolor="0.8")      

    

    for row in gdf.itertuples():
        centroid = row.geometry.centroid
        label = row[2]  # Accede al nombre del distrito por su índice (1)
        ax.annotate(f"{label}", xy=(centroid.x, centroid.y), xytext=(3, 3), textcoords="offset points")

    # Muestra el mapa
    plt.title("Mapa de distritos")
    st.pyplot(fig)

def calcular_itp(precio_compra, inversor):
    return np.where(inversor == "general", precio_compra * 0.07,
                    np.where(inversor == "reducido", precio_compra * 0.03,
                             np.where(inversor == "sujeto_pasivo", precio_compra * 0.01, 0)))

def calcular_obra_total_iva(area_util):
    if area_util >= 110:
        return 780 * area_util
    else:
        return (780 + 2 * (110 - area_util)) * area_util

def total_proyecto(base, inversor):
    base['area_util'] = base['area'] * 0.85
    base['precio_compra'] = base['precio'] * 0.9
    base['itp'] = calcular_itp(base['precio_compra'], inversor)
    base['comision_venta'] = base['precio_compra'] * 0.03
    base['comision_venta_iva'] = base['comision_venta'] * 1.21
    base['obra_total_iva'] = base['area_util'].apply(calcular_obra_total_iva)
    base['obra_total_base'] = base['obra_total_iva'] / 1.21
    base['cf_fee'] = np.maximum(7000, base['precio_compra'] * 0.035)
    base['cf_fee_iva'] = base['cf_fee'] * 1.21
    base["total_invertido"] = (base['precio_compra'] + base['itp'] + base['comision_venta'] +
                               base['obra_total_base'] + base['cf_fee']).astype(int)
    base["total_cashflow_iva"] = (base['precio_compra'] + base['itp'] + base['comision_venta_iva'] +
                                  base['obra_total_iva'] + base['cf_fee_iva']).astype(int)

    base[['area_util','precio_compra', 'comision_venta', 'comision_venta_iva','obra_total_iva','obra_total_base', 'itp', 'cf_fee','cf_fee_iva', 'habitaciones', 'banos']] = \
        base[['area_util','precio_compra', 'comision_venta', 'comision_venta_iva','obra_total_iva','obra_total_base', 'itp', 'cf_fee', 'cf_fee_iva','habitaciones', 'banos']].astype(int)

    return base

def renta_habitaciones(base, habs):
    tasa_ocupacion = 0.95
    gastos = 400

    # Merge para agregar el precio_hab_sencilla al DataFrame base
    base = pd.merge(base, habs[['barrio', 'hab_sencilla', 'hab_doble']], on='barrio', how='left', suffixes=('', '_habs'))

    # Calcular renta_habitaciones1 y renta_habitaciones2 con operaciones vectorizadas
    base['renta_habitaciones1'] = ((base['habitaciones']*base["hab_sencilla"]+(base['hab_doble']))*tasa_ocupacion).astype(int)
    base['renta_habitaciones2'] = ((base['habitaciones']*base["hab_sencilla"]+(base['hab_doble']*2))*tasa_ocupacion).astype(int)

    #base['renta_habitaciones1'] = ((base['habitaciones']) * base['hab_sencilla'] * tasa_ocupacion).astype(int)
    #base['renta_habitaciones2'] = ((base['habitaciones']) * base['hab_sencilla'] * tasa_ocupacion).astype(int)
    base["yield1"] = round(base["renta_habitaciones1"]*12/(base["precio_compra"])*100,2)
    base["yield2"] = round(base["renta_habitaciones2"]*12/(base["precio_compra"])*100,2)

    base['renta_base1'] = (base['renta_habitaciones1'] - ((base['habitaciones'] + 1) * 100) - gastos)/1.21
    base['renta_base2'] = (base['renta_habitaciones2'] - ((base['habitaciones'] + 2) * 100) - gastos)/1.21

    base["roi1"] = round(base["renta_base"]*12/(base["total_cashflow_iva"])*100,2)
    base["roi2"] = round(base["renta_base"]*12/(base["total_cashflow_iva"])*100,2)


    return base


def margen_operativo_fs(base):
    fs_spread = 150
    base["fs_spread"] = 0
    base["flujo_mes_inversor"] = 0
    base["base_alquiler"] = 0

    for i in range(0,len(base.index)):
        if base["tipologia_coliving"].iloc[i] == "4,1":
            base["fs_spread"].iloc[i] = 5*fs_spread
        elif base['tipologia_coliving'].iloc[i] == "4,2":
            base["fs_spread"].iloc[i] = 6*fs_spread
        elif base['tipologia_coliving'].iloc[i] == "5,2":
            base["fs_spread"].iloc[i] = 7*fs_spread

        base["flujo_mes_inversor"].iloc[i] = base["renta_habitaciones"].iloc[i] - base["fs_spread"].iloc[i]
        base["base_alquiler"].iloc[i] = (base["flujo_mes_inversor"].iloc[i]/1.21).astype(int)

    base["yield"] = round(base["renta_habitaciones"]*12/(base["precio"]*0.9)*100,2)
    base["roi"] = round(base["base_alquiler"]*12/base["total_invertido"]*100,2)

def leer_proyectos():
    user     = 'external_cfdata'
    password = '5g32W1i&o'
    host     = '87.106.125.178'
    database = 'pdfcf'
    db_connection = sql.connect(user=user, password=password, host=host, database=database)

    proyectos = pd.read_sql(f"""SELECT *
                            FROM proyectos2
                        """ , con=db_connection) 
    return proyectos

def crear_proyecto(base):
    user     = 'external_cfdata'
    password = '5g32W1i&o'
    host     = '87.106.125.178'
    database = 'pdfcf'

    engine = create_engine('mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(user, password, host, 3306, database))
    dbConnection = engine.connect()
    base.to_sql("proyectos2",dbConnection, if_exists="append", index=False)
    dbConnection.close()