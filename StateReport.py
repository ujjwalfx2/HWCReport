import pandas as pd
import streamlit as st
import hydralit_components as hc

def load_data():
    # Load the CSV file
    FPE = pd.read_csv("data/Op-FPE.csv", encoding='unicode_escape')    
    DE = pd.read_csv("data/DE.csv", encoding='unicode_escape')    
    sd = pd.read_csv("data/SD.csv", encoding='unicode_escape')    
    wl=pd.read_csv('data/Wellness.csv', encoding='unicode_escape')
    target=pd.read_csv('data/target.csv', encoding='unicode_escape')
    return FPE, DE, sd, wl, target

st.set_page_config(page_title="Ujjwal", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
st.markdown("<div id='top'></div>", unsafe_allow_html=True)
#load all csv data in dataframe
FPE, DE, sd, wl, target = load_data()

# hide menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .css-1lsmgbg.egzxvld0 {visibility: hidden;}  /* Specific class used by Streamlit footer */
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Set the configuration option to hide the Streamlit footer
#st.set_option('deprecation.showStreamlitFooter', False)

# specify the primary menu definition
menu_data = [
    {'label':"State Report", 'id':"statereport"},   
    {'label': "District Report", 'id': "districtreport"},
    {'label': "Block Report", 'id': "blockreport"},
    {'label': "Facility Report", 'id': "facilityreport"}
    ]

menu_id = hc.nav_bar(menu_definition=menu_data)

if menu_id == "statereport":
    st.dataframe(target)

if menu_id == "districtreport":
    st.dataframe(FPE)

if menu_id == "blockreport":
    st.dataframe(DE)

if menu_id == "facilityreport":
    st.dataframe(sd)

