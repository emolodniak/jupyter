import streamlit as st
import pandas as pd
import requests

#Setup
st.set_page_config(
    page_title="U-Need Enedis Dashboard",
    page_icon="https://d3v4jsc54141g1.cloudfront.net/uploads/mentor/avatar/1575105/normal_Enedis_Icone_couleur_RVB_300_dpi-1552312893.png",
    layout="wide"
)

#Sidebar
dic = pd.read_csv('https://raw.githubusercontent.com/emolodniak/jupyter/main/streamlit/DictionnaireProfils_4JUIL20.csv', encoding='utf-8', sep=';')

st.sidebar.title("Filtres")
with st.sidebar:
  dataset = st.sidebar.selectbox("DATASET",
      (['coefficients-des-profils'])
  )
  category = st.sidebar.selectbox("CATEGORIE",
      (dic['Categorie'].unique())
  )
  profile = st.sidebar.selectbox("SOUS_PROFIL",
      dic['Sous-profil'][dic['Categorie']==category]
  )
  year = st.radio("HORODATE",
        ('2020', '2021', '2022', '2023'), horizontal=True
    )

def url():
  url = f'https://data.enedis.fr/api/records/1.0/search/?dataset=coefficients-des-profils&q=&rows=9999&facet=horodate&facet=sous_profil&facet=categorie&refine.categorie={category}&refine.sous_profil={profile}&refine.horodate={year}'
  return url

url = url()

def get_data():
  df = pd.json_normalize(requests.get(url).json()['records'])
  df.drop(columns=['datasetid','recordid','record_timestamp'], inplace=True)
  df.columns = df.columns.str.replace('fields.', '')
  df['horodate'] = pd.to_datetime(df['horodate'])
  df.sort_values('horodate', ignore_index=True, inplace=True)
  return df

with st.sidebar:
  with st.spinner("Loading..."):
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
  r = requests.get(f'https://data.enedis.fr/explore/dataset/{dataset}/information/')
  st.markdown(r.text.split('content="')[4].split('"')[0])

with tab2:
  st.write(data)
  st.divider()

with tab3:
  st.subheader(''.join(dic['Libelle'][dic['Sous-profil']==profile]))
  period = st.radio("PERIOD",
        ('Mois', 'Jour', 'Heure'), horizontal=True
    )
  DF = data.drop(columns=['categorie', 'sous_profil'])
  if period == 'Mois':
    DF = DF.set_index('horodate').resample('M').mean().reset_index()
  if period == 'Jour':
    DF = DF.set_index('horodate').resample('D').mean().reset_index()
  if period == 'Heure':
    DF = DF.set_index('horodate').resample('H').mean().reset_index()
  variables = st.multiselect(
      "VARIABLES", 
      DF.select_dtypes('float').columns.values, DF.select_dtypes('float').columns.values[0]
  )
  st.line_chart(data=DF, x='horodate', y=variables)

with tab4:
  st.markdown("[ :link: Page du site d'origine ENEDIS OPEN DATA]('https://data.enedis.fr/explore/dataset/coefficients-des-profils/information/')")

with tab5:
  st.write('Jeu de données entier')
  st.download_button(
    label="Download data as CSV",
    data=data.to_csv(sep=';'),
    file_name=f'{dataset}_{category}_{profile}_{year}.csv',
    mime='text/csv')
  st.write('Le CSV utilise le point-virgule (;) comme séparateur.)')

with tab6:
  st.markdown(f'[ :link: API GET request]({url})')