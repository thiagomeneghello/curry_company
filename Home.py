import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲')

#image_path = "C:/Users/Thiago/Desktop/DADOS/repos/ftc_programacao_python/logo1.png"
image = Image.open( 'logo1.png')
st.sidebar.image( image, width=120 )

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest delivery in town")
st.sidebar.markdown("""____""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dasboard foi construído para acompanhar as métricas de crescimento da empresa, relação com Entregadores e Restaurantes.
    ### Como utilizar o Growth Dashboard?
    - Visão Empresa:
        - Gerencial: Métricas gerais de comportamento;
        - Tática: Indicadores semanais de crescimento;
        - Geográfica: Insights de geolocalização.
    
    - Visão Entregadores:
        Acompanhamento dos indicadores semanais de demanda.
    
    - Visão Restaurantes:
        Indicadores semanais de crescimento em vendas dos restaurantes.
    
    ### Ask for Help:
        Time de Data Science
            - @tfmeneghello
        """)
