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
    page_title='Visão Restaurante',
    page_icon='🍽',
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


def distances(df1, fig):
    if fig==False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        distance_avg = np.round(df1['distance'].mean(), 2)
    
        return distance_avg
    
    else:
        distance_city_avg = df1.loc[:, ['distance', 'City']].groupby(['City']).mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=distance_city_avg['City'], values=distance_city_avg['distance'], pull=[0.05, 0.05, 0.05])])
        
        return fig
    

def avgstd_timedelivery(df1, festival, op):
    cols = ['Time_taken(min)', 'Festival']
    df1_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)':['mean', 'std']})
    df1_aux.columns = ['avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    df1_aux = np.round(df1_aux.loc[(df1_aux['Festival'] == festival), op], 2)
    
    return df1_aux


def avgstd_timegraph (df1):
    cols = ['Time_taken(min)', 'City']
    time_per_city = df1.loc[:, cols].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
    time_per_city.columns = ['time_AVG', 'time_STD']
    time_per_city = time_per_city.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=time_per_city['City'], y=time_per_city['time_AVG'], error_y=dict(type='data', array=time_per_city['time_STD'])))
    fig.update_layout(barmode='group')
    
    return fig

def citytraffic_timegraph (df1):
    cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
    time_per_city_traffic = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    time_per_city_traffic.columns = ['time_AVG', 'time_STD']
    time_per_city_traffic = time_per_city_traffic.reset_index()
    fig = px.sunburst(time_per_city_traffic, path=['City', 'Road_traffic_density'], values='time_AVG', color='time_STD', color_continuous_scale="RdBu", color_continuous_midpoint=np.average(time_per_city_traffic['time_STD']))
    
    return fig


def cityorder_timedf(df1):
    cols = ['Time_taken(min)', 'City', 'Type_of_order']
    time_per_city_order = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
    time_per_city_order.columns = ['time_AVG', 'time_STD']
    time_per_city_order = time_per_city_order.reset_index()
    
    return time_per_city_order
#--------------------------------INÍCIO ESTRUTURA LÓGICA----------------------------------------------------------
#--------------------------------
#  IMPORTANDO DATASET
#--------------------------------
df_raw = pd.read_csv('C:/Users/Thiago/Desktop/DADOS/repos/ftc_programacao_python/dataset/train.csv')

#--------------------------------
#  LIMPEZA DATASET
#--------------------------------
df1 = clean_code(df_raw)

# ============================= 3.0 Visão Restaurantes

#===============================
# SIDEBAR STREAMLIT
#===============================
st.header(" Marketplace - Visão Restaurantes")

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            uniques = (df1['Delivery_person_ID'].nunique())
            col1.metric("Quantidade entregadores únicos", uniques)
            
        with col2:
            distance_avg = distances(df1, fig=False)
            col2.metric("Distância média", distance_avg)
            
        with col3:
            df1_aux = avgstd_timedelivery(df1, festival='Yes', op='avg_time')
            col3.metric('Tempo médio de entrega no Festival', df1_aux)
            
        with col4:
            df1_aux = avgstd_timedelivery(df1, festival='Yes', op='std_time')
            col4.metric('Desvio padrão de entrega no Festival', df1_aux)
            
        with col5:
            df1_aux = avgstd_timedelivery(df1, festival='No', op='avg_time')
            col5.metric('Tempo médio de entrega no Festival', df1_aux)
            
        with col6:
            df1_aux = avgstd_timedelivery(df1, festival='No', op='std_time')
            col6.metric('Desvio padrão de entrega sem Festival', df1_aux)
            
    with st.container():
        st.markdown("""____""")
        st.title('Distância média por cidade')
        fig = distances(df1, fig=True)
        st.plotly_chart(fig)
        
        
    with st.container():
        st.markdown("""____""")
        st.title('Distribuição de tempo')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Distribuição de tempo médio e desvio padrão por cidade (intervalos)')
            fig = avgstd_timegraph(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown('##### Tempo médio por entrega (tabela)')
            fig = citytraffic_timegraph (df1)
            st.plotly_chart(fig,use_container_width=True)
            
    with st.container():
        st.markdown("""____""")
        st.title("Tempo médio e desvio padrão por tipo de pedido e por cidade")
        time_per_city_order = cityorder_timedf(df1)
        st.dataframe(time_per_city_order)
        