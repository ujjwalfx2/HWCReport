import pandas as pd
import numpy as np
import streamlit as st
from st_aggrid import AgGrid
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from dash import Dash, html, dash_table, dcc
import plotly.express as px
import altair as alt
import plotly.graph_objects as go
import plotly.figure_factory as ff
import other_func #function calling from key_indicator py file
import io
import base64
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
import hydralit_components as hc
import re 
#with st.expander("Upload Files"):
        # file upload
        #upload_file_FPE = st.file_uploader("Upload Facility Profile Entry Data in CSV format", type=['csv'])
        #upload_file_DE = st.file_uploader("Upload Daily Entry Data of one month in CSV format", type=['csv'])
        #upload_file_SD = st.file_uploader("Upload Service Delivery Data of one month in CSV format", type=['csv'])
        #upload_file_WL = st.file_uploader("Upload Wellness Activity of on month in CSV format", type=['csv'])
        #upload_file_Target = st.file_uploader("Upload Target of the State in CSV format", type=['csv'])

def selectdistrict(fpe_df):
  # Display the styled label separately
  st.write("##### Select the District:")
  district= st.selectbox(
    "",      
    options=sorted(fpe_df["District_Name"].unique()),
    index=None,
    placeholder="Select District..."
  )
  #filter slection
  df_selection=fpe_df.query("District_Name== @district")
  return df_selection

def KPI_Box_Calculation(df_raw):
    op_shc = df_raw['FACILITY_TYPE'].eq("SHC").sum()
    op_ayush = df_raw['FACILITY_TYPE'].eq("AYUSH").sum()
    op_phc = df_raw['FACILITY_TYPE'].eq("PHC").sum()
    op_uphc = df_raw['FACILITY_TYPE'].eq("UPHC").sum()
    op_uhwc =df_raw['FACILITY_TYPE'].eq("UHWCs").sum()
    total_op_facility=op_shc+op_ayush+op_phc+op_uphc+op_uhwc

    #count Medicine/Drug facility type >=80% daily reporting Type_of_Medicine 
    drug_shc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "SHC") & (df_raw['Type_of_Medicine'] >= 84)].shape[0]
    drug_ayush = df_raw.loc[(df_raw['FACILITY_TYPE'] == "AYUSH") & (df_raw['Type_of_Medicine'] >= 160)].shape[0]
    drug_phc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "PHC") & (df_raw['Type_of_Medicine'] >= 138)].shape[0]
    drug_uphc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UPHC") & (df_raw['Type_of_Medicine'] >= 138)].shape[0]
    drug_uhwc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UHWCs") & (df_raw['Type_of_Medicine'] >= 138)].shape[0]
    drug_total = (drug_shc+drug_ayush+drug_phc+drug_uphc+drug_uhwc)

    #count Diagnostic facility type >=80% daily reporting Type_of_Diagnostics
    diagnostics_shc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "SHC") & (df_raw['Type_of_Diagnostics'] >= 11)].shape[0]
    diagnostics_ayush = df_raw.loc[(df_raw['FACILITY_TYPE'] == "AYUSH") & (df_raw['Type_of_Diagnostics'] >= 4)].shape[0]
    diagnostics_phc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "PHC") & (df_raw['Type_of_Diagnostics'] >= 51)].shape[0]
    diagnostics_uphc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UPHC") & (df_raw['Type_of_Diagnostics'] >= 51)].shape[0]
    diagnostics_uhwc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UHWCs") & (df_raw['Type_of_Diagnostics'] >= 51)].shape[0]
    diagnostics_total = (diagnostics_shc+diagnostics_ayush+diagnostics_phc+diagnostics_uphc+diagnostics_uhwc)

    #count DE facility type >=20 daily reporting 
    DE_shc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "SHC") & (df_raw['ReportingDE'] >= 20)].shape[0]
    DE_ayush = df_raw.loc[(df_raw['FACILITY_TYPE'] == "AYUSH") & (df_raw['ReportingDE'] >= 20)].shape[0]
    DE_phc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "PHC") & (df_raw['ReportingDE'] >= 20)].shape[0]
    DE_uphc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UPHC") & (df_raw['ReportingDE'] >= 20)].shape[0]
    DE_uhwc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UHWCs") & (df_raw['ReportingDE'] >= 20)].shape[0]
    DE_total = df_raw.loc[(df_raw['State_Name'] == "Jharkhand") & (df_raw['ReportingDE'] >= 20)].shape[0]

    #count SD facility reporting monthly service delivery
    sd_shc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "SHC") & (df_raw['ReportingSD'] == 1)].shape[0]
    sd_ayush = df_raw.loc[(df_raw['FACILITY_TYPE'] == "AYUSH") & (df_raw['ReportingSD'] == 1)].shape[0]
    sd_phc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "PHC") & (df_raw['ReportingSD'] == 1)].shape[0]
    sd_uphc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UPHC") & (df_raw['ReportingSD'] == 1)].shape[0]
    sd_uhwc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UHWCs") & (df_raw['ReportingSD'] == 1)].shape[0]
    sd_total = df_raw.loc[(df_raw['State_Name'] == "Jharkhand") & (df_raw['ReportingSD'] == 1)].shape[0]

    #count WL facility reporting monthly Wellness
    w_shc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "SHC") & (df_raw['ReportingWL'] >= 10)].shape[0]
    w_ayush = df_raw.loc[(df_raw['FACILITY_TYPE'] == "AYUSH") & (df_raw['ReportingWL'] >= 10)].shape[0]
    w_phc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "PHC") & (df_raw['ReportingWL'] >= 10)].shape[0]
    w_uphc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UPHC") & (df_raw['ReportingWL'] >= 10)].shape[0]
    w_uhwc = df_raw.loc[(df_raw['FACILITY_TYPE'] == "UHWCs") & (df_raw['ReportingWL'] >= 10)].shape[0]
    w_total = df_raw.loc[(df_raw['State_Name'] == "Jharkhand") & (df_raw['ReportingWL'] >= 10)].shape[0]

    return (op_shc, op_ayush, op_phc, op_uphc, op_uhwc, total_op_facility, 
            DE_shc, DE_ayush, DE_phc, DE_uphc, DE_uhwc, DE_total,
            sd_shc, sd_ayush, sd_phc, sd_uphc, sd_uhwc, sd_total,            
            w_shc, w_ayush, w_phc, w_uphc, w_uhwc, w_total,
            drug_shc, drug_ayush, drug_phc, drug_uphc, drug_uhwc, drug_total, 
            diagnostics_shc, diagnostics_ayush, diagnostics_phc, diagnostics_uphc, diagnostics_uhwc, diagnostics_total
            )

def blockwiseoperationa(selectdist):
  #st.write(selectdist)
  # Alternatively, using crosstab
  blockOP_crosstab = pd.crosstab(selectdist['Block_Name'], selectdist['FACILITY_TYPE']).reset_index()
  # Reordering the columns to B, C, A
  desired_order = ['Block_Name', 'SHC', 'AYUSH', 'PHC', 'UPHC', 'UHWCs']
  blockOP_crosstab = blockOP_crosstab[desired_order]
  blockOP_crosstab_without_total=blockOP_crosstab.copy()
  # Adding the row total
  blockOP_crosstab['Total'] = blockOP_crosstab.iloc[:, 1:].sum(axis=1)
  # Calculating the grand total for each column
  grand_total_crosstab = blockOP_crosstab.iloc[:, 1:].sum(axis=0)
  grand_total_crosstab['Block_Name'] = 'Total'
  # Appending the grand total row to the DataFrame
  blockOP_crosstab = pd.concat([blockOP_crosstab, pd.DataFrame([grand_total_crosstab])], ignore_index=True)
  # Coloring cells with a value of 0 in pink
  def color_zero(val):
    color = 'background-color: pink' if val == 0 else ''
    return color
  # Function to center-align values
  def center_align(val):
    return 'text-align: center;'  
  # Applying table styles
  styled_df = blockOP_crosstab.style.set_table_styles(
      [{'selector': 'thead th', 'props': [('background-color', '#2196F3'), ('color', 'white'), ('text-align', 'center')]}]
  ).applymap(color_zero, subset=pd.IndexSlice[:, desired_order[1:] + ['Total']]).applymap(
      center_align, subset=pd.IndexSlice[:, desired_order[1:] + ['Total']]
  )
  # Applying bold styling to the total row
  styled_df = styled_df.apply(lambda x: ['font-weight: bold' if x.name == len(blockOP_crosstab) - 1 else '' for _ in x], axis=1)
  # Applying bold styling to the total column
  styled_df = styled_df.applymap(lambda x: 'font-weight: bold' if blockOP_crosstab.columns[-1] == x else '')
  styled_df = styled_df.applymap(color_zero, subset=pd.IndexSlice[:, desired_order[1:]])
  # Displaying the styled DataFrame
  styled_df = styled_df.hide(axis='index')       
  col1,col2=st.columns(2)
  with col1:      
    tableheading = "Block wise Operational Facilities"
    st.write(f"\n###### ",tableheading,":")    
    st.markdown(styled_df.to_html(), unsafe_allow_html=True)
    other_func.generate_excel_download_link_with_file_name(styled_df,tableheading)    
  with col2:
    block_name = st.selectbox('**Select Block :**', blockOP_crosstab['Block_Name'])
    #block_name = st.selectbox('<span style="font-weight:bold;">Select Block</span>', blockOP_crosstab['Block_Name'], unsafe_allow_html=True)
    other_func.create_bar_graph_streamlit(blockOP_crosstab_without_total,block_name)
  st.markdown("""<div style="background: linear-gradient(to right, orange, yellow, green, blue, indigo, violet, red); height: 3px; width: 100%;"></div><br><br>""", unsafe_allow_html=True)    

  # specify the primary menu definition
  menu_data = [
      {'label':"Monthly Report", 'id':"MonthlyReport"},   
      {'label': "Daily Report", 'id': "DailyReport"},
      {'label': "Wellness Report", 'id': "WellnessReport"},
      {'label': "Other Checks", 'id': "OtherChecks"}
      ]

  menu_id = hc.nav_bar(menu_definition=menu_data)
   
  
  



