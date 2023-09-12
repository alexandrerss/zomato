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

st.set_page_config (page_title="Visão Cidades", page_icon='🌇', layout='wide') 

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

st.markdown('# 🌇 Visão Cidades')


top_cidades = df.loc[:,['city','country','restaurant_id']].groupby(['city','country']).count().sort_values(['restaurant_id','city'], ascending=[False,True]).reset_index()
top_cidades = top_cidades[:10]
fig = px.bar(top_cidades, x='city', y='restaurant_id', color='country', labels={'city':'Cidades', 'country': 'País', 'restaurant_id':'Quantidade de restaurantes'})
fig.update_traces(text=top_cidades['restaurant_id'], textposition='outside', textfont_size = 12 ,
                  hovertemplate='País: %{x}<br>Quantidade de Restaurantes: %{y}',
                  marker_line_color = 'black',
                  marker_line_width = 2 )
fig.update_layout(title = "TOP 10 Cidades com mais restaurantes registrados")
st.plotly_chart(fig,use_container_width = True)

with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            nota = df[df['aggregate_rating'] >= 4]
            top7 = nota.loc[:,['city', 'aggregate_rating', 'country']].groupby(['country','city']).count().sort_values('aggregate_rating',  ascending=False).reset_index()
            top7 = top7[:7]
            fig = px.bar(top7, x='city', y='aggregate_rating', text='aggregate_rating', color='country', labels={'city': 'Cidade','aggregate_rating':'Quantidade de Restaurantes', 'country': 'País' })
            fig.update_traces(textposition='outside', textfont_size = 12 , marker_line_color = 'black', marker_line_width = 2 )
            fig.update_layout(title = "7 melhores restaurantes com média acima")
            st.plotly_chart(fig,use_container_width = True)
            
        with col2:
            pior = df[df['aggregate_rating'] <= 2.5]
            top7 = pior.loc[:,['city', 'aggregate_rating', 'country']].groupby(['country','city']).count().sort_values('aggregate_rating',  ascending=False).reset_index()
            top7 = top7[:7]
            fig = px.bar(top7, x='city', y='aggregate_rating', text='aggregate_rating', color='country', labels={'city': 'Cidade','aggregate_rating':'Quantidade de Restaurantes', 'country': 'País' })
            fig.update_traces(textposition='outside', textfont_size = 12 , marker_line_color = 'black', marker_line_width = 2 )
            fig.update_layout(title = "7 melhores restaurantes com média abaixo")
            st.plotly_chart(fig,use_container_width = True)
            
distintas = df.loc[:,['city','cuisines', 'country']].groupby(['country','city']).nunique().sort_values(['cuisines', 'country'], ascending=[False,True]).reset_index()
distintas = distintas[:10]
fig = px.bar(distintas, x='city', y='cuisines', color='country', text='cuisines', labels={'city':'Cidades', 'country': 'País', 'cuisines':'Quantidade de tipos de culinária'})
fig.update_traces(textposition='outside', textfont_size = 12 ,
                  marker_line_color = 'black',
                  marker_line_width = 2 )
fig.update_layout(title = "TOP 10 Cidades com mais restaurantes com tipos de culinárias diferentes")
st.plotly_chart(fig,use_container_width = True)



        
        


    
