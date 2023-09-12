# ==============================================================================
# IMPORTAR BIBLIOTECAS
# ==============================================================================

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium as fl
import inflection
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from millify import millify as mil


st.set_page_config (page_title="Visão Geral", page_icon='❄', layout='wide') 

# ==============================================================================
# IMPORTAR DATASETS 
# ==============================================================================

df = pd.read_csv("datasets/zomato.csv")

# ==============================================================================
# FUNÇÕES 
# ==============================================================================

# Renomear as colunas do DataFrame
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df
df = rename_columns(df)

# Preenchimento do nome dos países
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",

}
def country_name(df):
  country_code = df['country_code']
  return COUNTRIES.get(country_code)
df['country'] = df.apply(country_name, axis=1)

# Criação do Tipo de Categoria de Comida
def create_price_type(df):
  price_range = df['price_range']
  if price_range == 1:
    return "cheap"
  elif price_range == 2:
    return "normal"
  elif price_range == 3:
    return "expensive"
  else:
    return "gourmet"
df['price_type'] = df.apply(create_price_type, axis=1)


# Criação do nome das Cores
COLORS = {
"3F7E00": "darkgreen",
"5BA829": "green",
"9ACD32": "lightgreen",
"CDD614": "orange",
"FFBA00": "red",
"CBCBC8": "darkred",
"FF7800": "magenta",
}

def color_name(df):
  rating_color = df['rating_color']
  return COLORS.get(rating_color)
df['color_name'] = df.apply(color_name, axis=1)

# Retirar os nan e nulos
def nan_nulo(df, columns_to_check):
    for column in columns_to_check:
        df = df.loc[df[column].notnull(), :]
    return df

# Linhas e colunas nulas
linhas_nulas = df.isnull().any(axis=1)
colunas_nulas = df.isnull().sum()
colunas_nan_none = df.isna().any()
df = df.dropna(axis=0, how="any", inplace=False)
df = df.dropna(axis=1, how="any", inplace=False)

# Duplicadas
df = df.drop_duplicates()

# Ordenação das culinarias
df["cuisines"] = df.loc[:, "cuisines"].astype(str).apply(lambda x: x.split(",")[0])

# Ordenar restaurantes pelo registro
df = df.sort_values(by='restaurant_id')

# Deletar as culinarias mineira e drinks
df = df.drop(df[df['cuisines'].isin(['Mineira', 'Drinks Only'])].index)

# ==============================================================================
# BARRA LATERAL - SIDEBAR
# ==============================================================================

image = Image.open ('logotipo.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown(' ### Zomato: Food Delivery & Dining ')
st.sidebar.markdown(' ### For the love of Food ')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Qual seria a data limite?')

paises = st.sidebar.multiselect('Escolha os países que Deseja visualizar dos restaurantes', 
                                df.loc[:, "country"].unique().tolist(),   
                                default=df.loc[:, "country"].unique().tolist())

# Aplicando o filtro de países
linhas_selec = df['country'].isin(paises)
df = df.loc[linhas_selec, :]

with st.sidebar:

    st.sidebar.markdown('## Dados Tratados')
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download",
        data=df.to_csv(index=False, sep=";"),
        file_name='d.csv',
        mime='text/csv')

st.sidebar.markdown('''---''')

st.sidebar.markdown('### Powered by Alexadrerss© 🌎🎓📊') 
with st.sidebar:
    components.html("""
                    <div class="badge-base LI-profile-badge" data-locale="en_US" data-size="large" data-theme="light" data-type="VERTICAL" data-vanity="alexandrerss" data-version="v1"><a class="badge-base__link LI-simple-link" href=https://www.linkedin.com/in/alexandrerss/"></a></div>
                    <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>              
              """, height= 310)

# ==============================================================================
# LAYOUT DA PAGINA
# ==============================================================================

st.header('Zomato: Food Delivery & Dining')

st.markdown('''
            A Zomato é um serviço de busca de restaurantes para quem quer sair para jantar, 
            buscar comida ou pedir em casa na Índia, Brasil, Portugal, Turquia, Indonésia, Nova Zelândia, 
            Itália, Filipinas, África do Sul, Sri Lanka, Catar, Emirados Árabes Unidos, Reino Unido, Estados Unidos, Austrália e Canadá. 
            ''')

st.markdown('### Temos as seguintes marcas dentro da nossa plataforma:')

with st.container():
    col1, col2,col3,col4,col5 = st.columns(5)
    
    with col1:
        unico = len(df.loc[:,'restaurant_id'].unique())
        col1.metric("Restaurantes", unico)
        
    with col2:
        paises = df.loc[:,'country'].nunique()
        col2.metric("Países", paises)
        
    with col3:
        cidades = df.loc[:,'city'].nunique()
        col3.metric("Cidades", cidades)
        
    with col4:
        avaliacoes = df.loc[:,'votes'].sum()
        col4.metric("Avaliações", mil(avaliacoes, precision= 2))
        
    with col5:
        culinaria = df.loc[:,'cuisines'].nunique()
        col5.metric("Tipos de Culinárias", culinaria)  
        

mapa = fl.Map()

marcadores = MarkerCluster().add_to(mapa)

for index, valor in df.iterrows():

    latitude = valor ['latitude']
    longitude = valor ['longitude']
    cozinha = valor['cuisines']
    price_for_two = valor["average_cost_for_two"]
    moeda = valor["currency"]
    rating = valor['aggregate_rating']
    color = f'{valor["color_name"]}'
    nome = valor["restaurant_name"]
    
    html = "<p><strong>{}</strong></p>"
    html += "<p>Preço: {},00 ({}) para dois"
    html += "<br />Culinária: {}"
    html += "<br />Avaliação: {}/5.0"
    html = html.format(nome, price_for_two, moeda, cozinha, rating)
    
    popup = fl.Popup(fl.Html(html, script=True),max_width=500)
     
    fl.Marker(location = [latitude, longitude],
    popup = popup,
    icon=fl.Icon(color=color, icon="home", prefix="fa")
    ).add_to(marcadores)

folium_static(mapa,width=1024, height=768)

