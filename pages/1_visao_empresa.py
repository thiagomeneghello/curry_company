#--------------------------------
#  LIBRARIES
#--------------------------------
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static


st.set_page_config(
    page_title='Visão Empresa',
    page_icon='🏢',
    layout='wide')

#--------------------------------
#  FUNÇÕES
#--------------------------------
def clean_code(df1):
    """ Objetivo: Limpeza do Dataframe
        1. Retirar linhas NaN;
        2. Resetar index;
        3. Retirar espaço final dos dados tipo str;
        4. Alterar datatypes;
        5. Formatar coluna de tempo
        
        Input: Dataframe
        Output: Dataframe
    """
    # limpeza de linhas NaN
    linhas_selecionadas = df1["Delivery_person_Age"] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    linhas_selecionadas = df1['Delivery_person_Ratings'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    linhas_selecionadas = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[linhas_selecionadas, :]
    linhas_selecionadas = df1["multiple_deliveries"] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    linhas_selecionadas = df1["Festival"] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    linhas_selecionadas = df1["City"] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]

    # resetando index pos limpeza de NAN pois index fica pulando numeração e trava a corrida por linhas
    df1 = df1.reset_index(drop=True)

    # retirada de espaços no final
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()

    # alterar datatype
    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1["multiple_deliveries"] = df1["multiple_deliveries"].astype(int)
    df1["Order_Date"] = pd.to_datetime(df1['Order_Date'], dayfirst=True)

    # retirar o ''(min)_' da coluna Time Taken e transformar em int
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1


def order_day(df1):
    """ Objetivo: Criar gráfico específico
    """
    cols = ['ID', 'Order_Date']
    order_per_day = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    graph_orders_day = px.bar(order_per_day, x='Order_Date', y='ID')

    return graph_orders_day

def traffic_share(df1):
    """ Objetivo: Criar gráfico específico
    """
    cols = ['ID','Road_traffic_density']
    order_per_traffic = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    order_per_traffic['percentual_order'] = order_per_traffic['ID']/order_per_traffic['ID'].sum()
    graph_orders_traffic = px.pie(order_per_traffic, values='percentual_order', names='Road_traffic_density')
    
    return graph_orders_traffic

def city_traffic(df1):
    """ Objetivo: Criar gráfico específico
    """
    cols = ["ID", 'City', 'Road_traffic_density']
    compare_city_density = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    graph_city_traffic = px.scatter(compare_city_density, x='City', y='Road_traffic_density', size='ID')
    
    return graph_city_traffic

def order_week(df1):
    """ Objetivo: Criar gráfico específico
    """
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'week_of_year']
    order_per_week = df1.loc[:, cols].groupby(['week_of_year']).count().reset_index()
    graph_order_week = px.line(order_per_week, x='week_of_year', y="ID")
    
    return graph_order_week

def person_week(df1):
    """ Objetivo: Criar gráfico específico
    """
    colsa = ['ID', 'week_of_year']
    colsb = ['Delivery_person_ID', 'week_of_year']
    order_per_week = df1.loc[:, colsa].groupby(['week_of_year']).count().reset_index()
    person_per_week = df1.loc[:, colsb].groupby(['week_of_year']).nunique().reset_index()
    order_per_person_in_week = pd.merge(order_per_week, person_per_week, how='inner')
    order_per_person_in_week['order_per_person'] = order_per_person_in_week['ID']/order_per_person_in_week['Delivery_person_ID']
    graph_person_week = px.line(order_per_person_in_week, x='week_of_year', y='order_per_person')
    
    return graph_person_week

def maps(df1):
    """ Objetivo: Criar mapa
    """
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    location_marker = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
    mapa = folium.Map()
    for index, loc_info in location_marker.iterrows():
        folium.Marker([loc_info['Delivery_location_latitude'],
                 loc_info['Delivery_location_longitude']],
                 popup=loc_info[['City','Road_traffic_density']]).add_to(mapa)
    folium_static(mapa, width=1024, height=600)
    
#--------------------------------INÍCIO ESTRUTURA LÓGICA----------------------------------------------------------
#--------------------------------
#  IMPORTANDO DATASET
#--------------------------------
df_raw = pd.read_csv('dataset/train.csv')

#--------------------------------
#  LIMPEZA DATASET
#--------------------------------
df1 = clean_code( df_raw )

# ============================= 1.0 Visão Empresa

#===============================
# SIDEBAR STREAMLIT
#===============================
st.header(" Marketplace - Visão Cliente")

image_path = "C:/Users/Thiago/Desktop/DADOS/repos/ftc_programacao_python/logo1.png"
image = Image.open( image_path)
st.sidebar.image( image, width=120 )

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest delivery in town")

st.sidebar.markdown("""____""")

date_slider = st.sidebar.slider("Selecione uma data", 
                                value=datetime(2022, 4, 16), 
                                min_value=datetime(2022, 2, 11), 
                                max_value=datetime(2022, 4, 13), 
                                format="DD-MM-YYYY")

st.sidebar.markdown("""____""")

traffic_options = st.sidebar.multiselect("Quais as condições de tráfego?", 
                      ["Low", "Medium", "High", "Jam"],
                      default="Low")

st.sidebar.markdown("""____""")

#Linkar filtro de data
linhas_selecionadas = df1['Order_Date'] <= date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Linkar filtro de condição de trafego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#===============================
# LAYOUT STREAMLIT
#===============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.header("Orders by day")
        graph_orders_day = order_day(df1)
        st.plotly_chart(graph_orders_day, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic order share')
            graph_orders_traffic = traffic_share(df1)
            st.plotly_chart(graph_orders_traffic, use_container_width=True)
            
        with col2:
            st.header('Compare City x Traffic')
            graph_city_traffic = city_traffic(df1)
            st.plotly_chart(graph_city_traffic, use_container_width=True)
    
with tab2:
    with st.container():
        st.header("Order by week")
        graph_order_week = order_week(df1)
        st.plotly_chart(graph_order_week, use_container_width=True)
    
    with st.container():
        st.header("Order by person/week")
        graph_person_week = person_week(df1)
        st.plotly_chart(graph_person_week, use_container_width=True)
    
with tab3:
    st.header("Mapa")
    maps(df1)
