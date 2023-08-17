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
    page_title='Visão Entregador',
    page_icon='🛵',
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


def top_delivers(df1, top_asc):
    cols = ['Time_taken(min)', 'Delivery_person_ID', 'City']
    df2 = (df1.loc[:, cols].groupby(['Delivery_person_ID', 'City'])
                           .mean()
                           .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
                           .reset_index())
    aux1 = df2.loc[(df2['City'] == 'Metropolitian'), :].head(10)
    aux2 = df2.loc[(df2['City'] == 'Urban'), :].head(10) 
    aux3 = df2.loc[(df2['City'] == 'Semi-Urban'), :].head(10)
    df3 = pd.concat([aux1, aux2, aux3])
    df3 = df3.reset_index(drop=True)
    
    return df3

#--------------------------------INÍCIO ESTRUTURA LÓGICA----------------------------------------------------------
#--------------------------------
#  IMPORTANDO DATASET
#--------------------------------
df_raw = pd.read_csv('C:/Users/Thiago/Desktop/DADOS/repos/ftc_programacao_python/dataset/train.csv')

#--------------------------------
#  LIMPEZA DATASET
#--------------------------------
df1 = clean_code( df_raw )


# ============================= 2.0 Visão Entregaor

#===============================
#SIDEBAR STREAMLIT
#===============================
st.header(" Marketplace - Visão Entregador")

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



#==============================
#LAYOUT STREAMLIT
#==============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição veicular', melhor_condicao)
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição veicular', pior_condicao)
            
    with st.container():
        st.markdown("""____""")
        st.title("Avaliações")
        
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown("##### Avaliação média por entregador")
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID']
            rating_mean_person = (df1.loc[:, cols]
                                     .groupby(['Delivery_person_ID'])
                                     .mean()
                                     .sort_values('Delivery_person_Ratings', ascending=False)
                                     .reset_index())
            st.dataframe(rating_mean_person)
            
        with col2:
            st.markdown("##### Avaliação média por trânsito")
            cols = ['Delivery_person_Ratings', 'Road_traffic_density']
            rating_per_traffic = (df1.loc[:, cols].groupby('Road_traffic_density')
                                                  .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            rating_per_traffic.columns = ['Ratings_MEAN', 'Ratings_STD']
            rating_per_traffic.reset_index()
            st.dataframe(rating_per_traffic)
            
            st.markdown("##### Avaliação média por clima")
            cols = ['Delivery_person_Ratings', 'Weatherconditions']
            rating_per_traffic = (df1.loc[:, cols].groupby('Weatherconditions')
                                                  .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            rating_per_traffic.columns = ['Ratings_MEAN', 'Ratings_STD']
            rating_per_traffic.reset_index()
            st.dataframe(rating_per_traffic)
            
    with st.container():
        st.markdown("""____""")
        st.title("Velocidade de entrega")
        
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown("##### Top entregadores mais rápidos por cidade")
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3) 
            
        with col2:
            st.markdown("##### Top entregadores mais lentos")
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
        