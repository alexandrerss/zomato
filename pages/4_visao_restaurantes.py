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

st.set_page_config (page_title="Visão Cozinhas", page_icon='🍜', layout='wide') 

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
"FF7800": "darkred",
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

quant_restaurantes = st.sidebar.slider('Selecione a quantidade de Restaurantes que deseja visualizar', 1,20,10)

culinaria = st.sidebar.multiselect('Escolha os Tipos de Culinária', 
                                df.loc[:, "cuisines"].unique().tolist(),   
                                default=['Home-made','BBQ','Japanese','Brazilian','Arabian','American','Italian'])

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

st.markdown('# 🍜 Visão Cozinhas')

st.markdown('##  Melhores Restaurantes dos Principais tipos Culinários')

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        italiana = df[df['cuisines'].str.contains('Italian', case=False)]
        italiana = italiana.sort_values(['aggregate_rating','restaurant_id'], ascending = [False, True])
        italiana = italiana.iloc[0]
        culinaria_media = italiana["aggregate_rating"]
        restaurante = italiana['restaurant_name']
        pais = italiana["country"]
        cidade = italiana["city"]
        preco = italiana["average_cost_for_two"]
        col1.metric(f'Italiana: {restaurante}', f'{culinaria_media}/5.0', help=f'País: {pais}\n\nCidade: {cidade}\n\nMédia de prato para duas pessoas: {preco}')
        
    with col2:    
        america = df[df['cuisines'].str.contains('American', case=False)]
        america = america.sort_values(['aggregate_rating','restaurant_id'], ascending = [False, True])
        america = america.iloc[0]
        culinaria_media = america["aggregate_rating"]
        restaurante = america['restaurant_name']
        pais = america["country"]
        cidade = america["city"]
        preco = america["average_cost_for_two"]
        col2.metric(f'Americana: {restaurante}', f'{culinaria_media}/5.0', help=f'País: {pais}\n\nCidade: {cidade}\n\nMédia de prato para duas pessoas: {preco}')
    
    with col3:
        arabia = df[df['cuisines'].str.contains('Arabian', case=False)]
        arabia = df[df['cuisines'].str.contains('Arabian', case=False)]
        arabia = arabia.sort_values(['aggregate_rating','restaurant_id'], ascending = [False, True])
        arabia = arabia.iloc[0]
        culinaria_media = arabia["aggregate_rating"]
        restaurante = arabia['restaurant_name']
        pais = arabia["country"]
        cidade = arabia["city"]
        preco = arabia["average_cost_for_two"]
        col3.metric(f'Arábia: {restaurante}', f'{culinaria_media}/5.0', help=f'País: {pais}\n\nCidade: {cidade}\n\nMédia de prato para duas pessoas: {preco}')

    with col4:
        japa = df[df['cuisines'].str.contains('Japanese', case=False)]
        japa = japa.sort_values(['aggregate_rating','restaurant_id'], ascending = [False, True])
        japa = japa.iloc[0]
        culinaria_media = japa["aggregate_rating"]
        restaurante = japa['restaurant_name']
        pais = japa["country"]
        cidade = japa["city"]
        preco = japa["average_cost_for_two"]
        col4.metric(f'Japonesa: {restaurante}', f'{culinaria_media}/5.0', help=f'País: {pais}\n\nCidade: {cidade}\n\nMédia de prato para duas pessoas: {preco}')

    with col5:
        brasa = df[df['cuisines'].str.contains('Brazilian', case=False)]
        brasa = brasa.sort_values(['aggregate_rating','restaurant_id'], ascending = [False, True])
        brasa = brasa.iloc[0]
        culinaria_media = brasa["aggregate_rating"]
        restaurante = brasa['restaurant_name']
        pais = brasa["country"]
        cidade = brasa["city"]
        preco = brasa["average_cost_for_two"]
        col5.metric(f'Brasileira: {restaurante}', f'{culinaria_media}/5.0', help=f'País: {pais}\n\nCidade: {cidade}\n\nMédia de prato para duas pessoas: {preco}')

st.markdown('## Top Restaurantes')

top10 = (df.loc[:,['restaurant_id','restaurant_name', 'country', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes']].sort_values(['aggregate_rating','restaurant_id'], ascending = [False, True]))
tabela = top10.head(quant_restaurantes)
st.dataframe(tabela)

with st.container():
    
    col1,col2 = st.columns(2)

    with col1:
        maior = df.loc[:,['aggregate_rating','cuisines']].groupby('cuisines').mean().sort_values('aggregate_rating', ascending = False).round(2)
        maior = maior[:20]
        limitador = maior.head(quant_restaurantes)
        grafico = px.bar(limitador, y='aggregate_rating' , labels={'cuisines':'Culinárias', 'aggregate_rating':'Média de Avaliações'})
        grafico.update_traces(text=limitador['aggregate_rating'],textposition='inside', hovertemplate='Tipo de culinarias: %{x}<br>Média da Avaliação: %{y}')
        grafico.update_layout(title = "As Melhores avaliações de culinarias",)
        st.plotly_chart(grafico, use_container_width = True)

    with col2:
        menor = df.loc[:,['aggregate_rating','cuisines']].groupby('cuisines').mean().sort_values('aggregate_rating', ascending = True).round(2)
        menor = menor[:20]
        limitador = menor.head(quant_restaurantes)        
        grafico = px.bar(limitador, y='aggregate_rating',labels={'cuisines':'Culinárias', 'aggregate_rating':'Média de Avaliações'})
        grafico.update_traces(text=limitador['aggregate_rating'],textposition='inside', hovertemplate='Tipo de culinarias: %{x}<br>Média da Avaliação: %{y}')
        grafico.update_layout(title = "Os Piores avaliações de culinarias",)
        st.plotly_chart(grafico, use_container_width = True)

