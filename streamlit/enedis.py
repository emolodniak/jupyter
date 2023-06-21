import streamlit as st
import numpy as np
import pandas as pd
import requests

#Setup
st.set_page_config(
    page_title="U-Need Enedis Dashboard",
    page_icon="https://d3v4jsc54141g1.cloudfront.net/uploads/mentor/avatar/1575105/normal_Enedis_Icone_couleur_RVB_300_dpi-1552312893.png",
    layout="wide",
)

#Sidebar
st.sidebar.title("Filtres")
with st.sidebar:
  dataset = st.sidebar.selectbox("Dataset",
      ('bilan-electrique', 'coefficients-des-profils')
  )
  category = st.sidebar.selectbox("CATEGORIE",
      ('Residentiel', 'Professionnel')
  )
  profile = st.sidebar.selectbox("SOUS_PROFIL",
      ('RES5_HPSH','RES5_HCSH','RES5_HPSB','RES5_HCSB','PRO1_BASE','PRO1WE_SEM','PRO1WE_WE','PRO2_HP','PRO2_HC')
  )
  year = st.radio("HORODATE",
        ('2019', '2020', '2021', '2022', '2023')
    )

def get_data():
  url = f'https://data.enedis.fr/api/records/1.0/search/?dataset=coefficients-des-profils&q=&rows=9999&facet=horodate&facet=sous_profil&facet=categorie&refine.categorie={category}&refine.sous_profil={profile}&refine.horodate={year}'
  df = pd.json_normalize(requests.get(url).json()['records'])
  df.drop(columns=['datasetid','recordid','record_timestamp'], inplace=True)
  df.columns = df.columns.str.replace('fields.', '')
  #df.sort_values('horodate', ignore_index=True, inplace=True)
  return df

with st.sidebar:
  with st.spinner("Loading..."):
    #@st.cache_data
    # Data
    data = get_data()

st.title(':blue[ENEDIS OPEN DATA]')

#Tab bar
css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size:18px; color:DodgerBlue;}
</style>
'''
st.markdown(css, unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['🛈 Informations', ':bookmark_tabs: Tableau', ':bar_chart: Analyse', 'ℹ En savoir plus', ':inbox_tray: Export', ':gear: API'])

with tab1:
  r = requests.get('https://data.enedis.fr/explore/dataset/coefficients-des-profils/information/')
  st.markdown(r.text.split('content="')[4].split('"')[0])
  st.divider()

tab2.write(data)
st.divider()

with tab3:
  variables = st.multiselect(
      "Selectionnez des variables", data.select_dtypes('float').columns, data.select_dtypes('float').columns.values
  )
  st.line_chart(data=data, x='horodate', y=variables) #['coefficient_ajuste','coefficient_prepare'])
  st.divider()


with tab5:
  st.download_button(
    label="Download data as CSV",
    data=data.to_csv(sep=';'),
    file_name=f'{dataset}_{category}_{profile}_{year}.csv',
    mime='text/csv')
  st.write('Le CSV utilise le point-virgule (;) comme séparateur.)')
  st.divider()
