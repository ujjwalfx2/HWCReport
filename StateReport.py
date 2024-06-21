import pandas as pd
import streamlit as st
import hydralit_components as hc
import numpy as np
import other_func #function calling from key_indicator py file
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from openpyxl import Workbook

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

# Facility PE cleaning **********************************************************************************************************
# copy missing Taluka as District name
FPE['Taluka_Name'].fillna(FPE['District_Name'], inplace=True)    
#copy missing block as Taluka name
FPE['Block_Name'].fillna(FPE['Taluka_Name'], inplace=True) 
FPE.rename(columns={'NIN_2_HFI':'NIN ID'}, inplace=True)
FPE.rename(columns={'FACILITY_TYPE_IN_HWC':'FACILITY_TYPE'}, inplace=True)
FPE.rename(columns={'Types of medicines available at Ayushman Arogya Mandir':'Type_of_Medicine','Type of Diagnostics Available':'Type_of_Diagnostics'}, inplace=True)
#cout SHC in OP FPE
FPE1=FPE
op_shc = FPE['FACILITY_TYPE'].eq("SHC").sum()
op_ayush = FPE['FACILITY_TYPE'].eq("AYUSH").sum()
op_phc = FPE['FACILITY_TYPE'].eq("PHC").sum()
op_uphc = FPE['FACILITY_TYPE'].eq("UPHC").sum()
op_uhwc =FPE['FACILITY_TYPE'].eq("UHWCs").sum()

# Total Population in catchment area of facility remove any commas and convert in int format
FPE['Total Population in catchment area of facility']=FPE['Total Population in catchment area of facility'].replace({',': ''}, regex=True)
FPE['Total Population in catchment area of facility']=FPE['Total Population in catchment area of facility'].astype(int)

col=['NIN ID', 'HFI_Name', 'PHC_CHC_Type', 'FACILITY_TYPE',
    'State_Name', 'District_Name', 'Taluka_Name', 'Block_Name',
    'Proposed Date', 'Progressive Date',
    'Total Population in catchment area of facility','Type_of_Medicine','Type_of_Diagnostics']
FPE=FPE[col]
col5 = ['District_Name','FACILITY_TYPE']
pivot_data=FPE[col5]
district_operational = pd.pivot_table(pivot_data, index='District_Name', columns='FACILITY_TYPE', aggfunc=len, fill_value=0)
#add total column
district_operational['Total'] = district_operational.sum(axis=1)
pivot_table = pd.pivot_table(pivot_data, index='District_Name', columns='FACILITY_TYPE', aggfunc=len, fill_value=0, margins=True, margins_name='Total')
pivot_table1=pivot_table

#target and achievement Table merge
# Calculate the totals for each column
target1=target
target1 = target1.rename(columns={'District': 'District_Name'})
#merge District Operational list with Target 1 list without total row
TargetOperationlWithoutTotal=pd.merge(district_operational,target1, on=['District_Name'], how='outer')
# Calculate totals for each numeric column
totals = target1.select_dtypes(include=[np.number]).sum()
totals['District_Name'] = 'Total'
# Facility wise Target table with Total row at the end
df_with_total = pd.concat([target1, pd.DataFrame(totals).T], ignore_index=True)
# merge Target and achievement datafram and calculate facility type wise %
targetachievementtable=pd.merge(df_with_total,pivot_table1, on=['District_Name'], how='outer')
#Creating new dataframe for total target and operational
targetachievementtable1=pd.merge(pivot_table1,df_with_total, on=['District_Name'], how='outer')
# Extract row labeled "Total" into a new DataFrame
total_row_only = targetachievementtable1[targetachievementtable1['District_Name'] == 'Total']
total_row_only = total_row_only.rename(columns={'Target': 'Total-Target'})
#converting row to column
# Melt the DataFrame
melted_df = total_row_only.melt(var_name='Category', value_name='Operational')
# Create 'Achievement' column
melted_df['Target'] = None
# Assign the values from row 7 onwards to the 'Achievement' column of the corresponding categories
for i in range(7, len(melted_df)):
    category = melted_df.loc[i, 'Category']
    value = melted_df.loc[i, 'Operational']
    melted_df.loc[melted_df['Category'] == category.replace('-Target', ''), 'Target'] = value

# Delete rows 7 onwards
melted_df = melted_df[:7]
melted_df = melted_df.drop(0)

# Display the DataFrame
total_row_only = melted_df
total_row_only.reset_index(drop=True, inplace=True)

targetachievementtable['SHC_%'] = np.round((targetachievementtable['SHC'] / targetachievementtable['SHC-Target'].replace(0, np.nan)) * 100).fillna(0).round(2)
targetachievementtable['AYUSH_%'] = np.round((targetachievementtable['AYUSH'] / targetachievementtable['AYUSH-Target'].replace(0, np.nan)) * 100).fillna(0).round(2)
targetachievementtable['PHC_%'] = np.round((targetachievementtable['PHC'] / targetachievementtable['PHC-Target'].replace(0, np.nan)) * 100).fillna(0).round(2)
targetachievementtable['UPHC_%'] = np.round((targetachievementtable['UPHC'] / targetachievementtable['UPHC-Target'].replace(0, np.nan)) * 100).fillna(0).round(2)
targetachievementtable['UHWCs_%'] = np.round((targetachievementtable['UHWCs'] / targetachievementtable['UHWCs-Target'].replace(0, np.nan)) * 100).fillna(0).round(2)
targetachievementtable['Total_%'] = np.round((targetachievementtable['Total'] / targetachievementtable['Target'].replace(0, np.nan)) * 100).fillna(0).round(2)
#arange columns for display
targetachievementtable=targetachievementtable[['District_Name',	'SHC',	'SHC-Target',	'SHC_%',	'AYUSH',	'AYUSH-Target',	'AYUSH_%',	'PHC',	'PHC-Target',	'PHC_%',	'UPHC',	'UPHC-Target',
                                               	'UPHC_%',	'UHWCs',	'UHWCs-Target',	'UHWCs_%',	'Total',	'Target',	'Total_%']]

# Convert pivot table to Markdown table
pivot_table_styled = pivot_table.applymap(lambda x: f'<div style="text-align: center;"><b>{x}</b></div>')

geo=['HFI_Name', 'PHC_CHC_Type','State_Name', 'District_Name', 'Taluka_Name', 'Block_Name']
# fill NA if any value is missing in geo 
FPE[geo]=FPE[geo].fillna('NA')
# total facility 
total_facility=FPE.shape[0]


# DE cleaning *******************************************************************************************************************
#Entry Date convert in date format in format of 2022-05-09
DE['Entry Date'] = pd.to_datetime(DE['Entry Date'], format='%Y-%m-%d')
DE.head(3)
# add month-year column from entry date
DE['Month-Year'] = DE['Entry Date'].dt.strftime('%b-%Y')
DE['Footfall Total'] = DE["Footfall Male"] + DE["Footfall Female "]+DE["Footfall Others "]
# if wellness session conducted is yes then 1 else 0
DE['Wellness sessions conducted ']=DE['Wellness sessions conducted '].replace({'Yes': 1, 'No': 0})
DE['ReportingDE']=1
DE_col=['NIN ID', 'ReportingDE', 'Footfall Total',
    ' Patients availed tele-consulation services ',
    'Wellness sessions conducted ',
        'Month-Year']
DE=DE[DE_col]
#groupby
DE=DE.groupby(['NIN ID','Month-Year']).sum().reset_index()
#total facility in DE
#st.write(f"Total facility in DE is :{DE['NIN ID'].nunique()}") 

# SD cleaning ********************************************************************************************************************
#Entry Date convert in date format in format of 2022-11-30
sd['Entry Month'] = pd.to_datetime(sd['Entry Month'], format='%Y-%m-%d')
# # add month-year column from entry date
sd['Month-Year'] = sd['Entry Month'].dt.strftime('%b-%Y')
#show all the columns in view
pd.set_option('display.max_columns', None)
int_col=['Individuals empanelled',
    'Community Based Assessment Checklist filled',
    'HTN Individuals screened Male', 'HTN Individuals screened Female',
    'HTN Individuals screened Other', 'HTN Newly diagnosed Male',
    'HTN Newly diagnosed Female', 'HTN Newly diagnosed Other',
    'HTN On treatment Male', 'HTN On treatment Female',
    'HTN On treatment Other', 'DM Individuals screened Male',
    'DM Individuals screened Female', 'DM Individuals screened Other',
    'DM Newly diagnosed Male', 'DM Newly diagnosed Female',
    'DM Newly diagnosed Other', 'DM On treatment Male',
    'DM On treatment Female', 'DM On treatment Other',
    'OC Individuals screened Male', 'OC Individuals screened Female',
    'OC Individuals screened Other', 'OC Newly diagnosed Male',
    'OC Newly diagnosed Female', 'OC Newly diagnosed Other',
    'OC On treatment male', 'OC On treatment Female',
    'OC On treatment Other', 'BC Individuals screened female',
    'BC Newly diagnosed female', 'BC On treatment female',
    'CC Individuals screened female', 'CC Newly diagnosed female',
    'CC On treatment female', 'Individuals referred for screening male',
    'Individuals referred for screening female',
    'Individuals referred for screening other', 'Newly diagnosed Male',
    'Newly diagnosed Female', 'Newly diagnosed Other', 'On treatment Male',
    'On treatment Female', 'On treatment Other',
    'Total Patients received antihypertensive medicines at this centre',
    'Total Patients received ant-diabetic medicines at this centre','Medicines_TPR_AO_M',"Closing stock of glucostrips"]

# convert all the int columns in int format
sd_int=sd[int_col].head()
# remove any commas in the int columns
sd[sd_int.columns] = sd[sd_int.columns].replace({',': ''}, regex=True)
#convert all the int columns in int format
sd[int_col] = sd[int_col].apply(pd.to_numeric, errors='coerce', axis=1)
# add total column in sd_int
sd['Facility Type'] = sd['FACILITY_TYPE']

#HTN
sd['HTN screened '] = sd['HTN Individuals screened Male']+ sd['HTN Individuals screened Female']+ sd['HTN Individuals screened Other']
sd['HTN diagnosed '] = sd['HTN Newly diagnosed Male']+ sd['HTN Newly diagnosed Female']+ sd['HTN Newly diagnosed Other']
sd['HTN on treatment '] = sd['HTN On treatment Male']+ sd['HTN On treatment Female']+ sd['HTN On treatment Other']

#DM
sd['DM screened '] = sd['DM Individuals screened Male']+ sd['DM Individuals screened Female']+ sd['DM Individuals screened Other']
sd['DM diagnosed '] = sd['DM Newly diagnosed Male']+ sd['DM Newly diagnosed Female']+ sd['DM Newly diagnosed Other']
sd['DM on treatment '] = sd['DM On treatment Male']+ sd['DM On treatment Female']+ sd['DM On treatment Other']

#DM
sd['OC screened '] = sd['OC Individuals screened Male']+ sd['OC Individuals screened Female']+ sd['OC Individuals screened Other']
sd['OC diagnosed '] = sd['OC Newly diagnosed Male']+ sd['OC Newly diagnosed Female']+ sd['OC Newly diagnosed Other']
sd['OC on treatment '] = sd['OC On treatment male']+ sd['OC On treatment Female']+ sd['OC On treatment Other']

#referred
sd['TB_Referred'] = sd['Individuals referred for screening male']+ sd['Individuals referred for screening female']+ sd['Individuals referred for screening other']

#Newly diagnosed
sd['TB_Newly diagnosed'] = sd['Newly diagnosed Male']+ sd['Newly diagnosed Female']+ sd['Newly diagnosed Other']

#On treatment
sd['TB_On treatment'] = sd['On treatment Male']+ sd['On treatment Female']+ sd['On treatment Other']
# if yes than 1 else 0 add both
sd["equipments_BP_gluco"]=sd["Availability of functional BP apparatus"].replace({'Yes': 1, 'No': 0})+sd["Availability of functional glucometer"].replace({'Yes': 1, 'No': 0})
sd["pbi_tbi"]=sd["Performance/team based incentives for MO/SN/CHO"].replace({'Yes': 1, 'No': 0})+sd["Team based incentives for ASHA/MPW"].replace({'Yes': 1, 'No': 0})
sd["JASmeeting"]=sd["JAS monthly meeting conducted"].replace({'Yes': 1, 'No': 0})
sd['ReportingSD']=1
#select columns
selected_col=['NIN ID', 'Facility Name', 'Facility Type', 'State', 'District',
    'Taluka', 'Block', 'Entry Month',
            'Month-Year','ReportingSD',
    'HTN screened ', 'DM screened ',
    'OC screened ','BC Individuals screened female', 'TB_Referred','equipments_BP_gluco',"pbi_tbi", "JASmeeting"]
sd=sd[selected_col]

# group by NIN-ID and month-year sum
sd = sd.groupby(['NIN ID', 'Entry Month']).sum().reset_index()
# total facility in SD
#st.write(f"Total facility in SD is :{sd['NIN ID'].nunique()}")

#Wellness cleaning ********************************************************************************************************************
#rename NIN column to NIN ID
wl = wl.rename(columns={'NIN':'NIN ID'})

#merge DE and sd
df=pd.merge(DE, sd, on=['NIN ID','Month-Year'], how='outer')
#merge with FPE
df=pd.merge(FPE,df, on=['NIN ID'], how='outer').reset_index().reset_index()
#df add a target population column with 80 percent of the total population
df['Target Population']=round(df['Total Population in catchment area of facility']*0.08,0)
# cal_Reporting map value>=20 than 15, IF value >=10 than 10 else 0
df['cal_Reporting']=np.where(df['ReportingDE']>=20,15,np.where(df['ReportingDE']>=10,10,0))
# cal_footfall map if 'Footfall Total'/'Target Population'>=1, 15,if 'Footfall Total'/'Target Population'>=.8, 10,if 'Footfall Total'/'Target Population'>=.5,5, else 0
df['cal_footfall']=np.where((df['Footfall Total']/df['Target Population'])>=1,15,np.where((df['Footfall Total']/df['Target Population'])>=.8,10,np.where((df['Footfall Total']/df['Target Population'])>=.5,5,0)))
# Equipment value AV4=2,10,IF value =1,5,0
df['cal_Equipment']=np.where(df['equipments_BP_gluco']==2,5,0)
df['cal_JAS']=np.where(df['JASmeeting']==1,10,0)
# pbi_tbi value AV4=2,10,IF value =1,5,0
df['cal_pbi_tbi']=np.where(df['pbi_tbi']==2,20,np.where(df['pbi_tbi']==1,10,0))
# tb refered value referred/total >=30,10 ,if referred/total >=20,5, else 0
df['cal_tb']=np.where((df['TB_Referred']/df['Footfall Total'])>=.03,10,np.where((df['TB_Referred']/df['Footfall Total'])>=.02,5,0))
# teleconsultation value AM4>=30,5,IF(AM4>=15,3,IF(AM4>=1,1,0
df['cal_teleconsultation']=np.where(df[' Patients availed tele-consulation services ']>=25,5,np.where(df[' Patients availed tele-consulation services ']>=15,3,np.where(df[' Patients availed tele-consulation services ']>=1,1,0)))
# wellness and yoga AQ6>=10,5,IF(AQ6>=5,3,0)
df['cal_wellness']=np.where(df['Wellness sessions conducted ']>=10,5,np.where(df['Wellness sessions conducted ']>=5,3,0))

# save the df in csv
#df.to_excel("data/df.xlsx",sheet_name='df') 

distcount = df.groupby(["District_Name"], sort=True)["State_Name"].count().rename('Total Facility').reset_index()
# Calculate Grand Total
jharkhand = df["State_Name"].count()
# Add Grand Total row to the DataFrame
grand_total_row = pd.DataFrame({"District_Name": ["Total"], "Total Facility": [jharkhand]})
distcount = pd.concat([distcount, grand_total_row], ignore_index=True)
# Rename column
distcount = distcount.rename(columns={'District_Name':'District'})
# Count occurrences in the second dataframe
new_cal_wellness = wl['NIN ID'].value_counts().reset_index()
new_cal_wellness.columns = ['NIN ID', 'ReportingWL']
df = pd.merge(df, new_cal_wellness, on='NIN ID', how='left')

#Store calculated df into df_raw dataframe
df_raw = df
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

# Group by 'District_Name' and aggregate count and conditional value
summary_df = df.groupby('District_Name').agg({'State_Name': 'count', 'ReportingDE': lambda x: (x >= 20).sum(), 'ReportingSD': lambda y: (y == 1).sum(), 'ReportingWL': lambda x: (x >= 10).sum()}).reset_index()

# Rename columns for clarity
summary_df = summary_df.rename(columns={'District_Name': 'District', 'State_Name': 'Operational Facility', 'ReportingDE': 'Daily Reporting >= 20 days', 'ReportingSD': 'Monthly Reporting', 'ReportingWL': 'Wellness Reporting >=10 days'})
df=summary_df

# merged Target and Operational facility numbers
target_op_merged_df = pd.merge(target[['District', 'Target']], df[['District', 'Operational Facility']], on="District")

op_percent=(df['Operational Facility'].sum()/target['Target'].sum()) *100
op_percent = f"{op_percent:.0f}"

# specify the primary menu definition
menu_data = [
    {'label':"State Report", 'id':"statereport"},   
    {'label': "District Report", 'id': "districtreport"},
    {'label': "Block Report", 'id': "blockreport"},
    {'label': "Facility Report", 'id': "facilityreport"}
    ]

menu_id = hc.nav_bar(menu_definition=menu_data)

if menu_id == "statereport":
    #KPI
    st.subheader(f"AAM Dashboard for the month of : {DE['Month-Year'].unique()}")
    with st.expander("Click to see Key Performance Indicators (KPI)"):    
        col1, col2, col3 = st.columns(3)
        with col1:
            wch_colour_box = (50,1810,26)
            wch_colour_font = (0,0,0)
            fontsize = 36
            valign = "left"
            iconname = "fas fa-hospital"
            sline = "Total Operational Facility"
            i = total_facility
            per = op_percent
            shc = op_shc
            ayush = op_ayush
            phc = op_phc
            uphc = op_uphc
            uhwc = op_uhwc
            other_func.display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc)
            
        with col2:
            wch_colour_box = (0,102,204)
            wch_colour_font = (0,0,0)
            fontsize = 36
            valign = "left"
            iconname = "fas fa-pen"
            sline = "Total Facility Reported Daily Entry >=20 days"
            i = DE_total
            per = round(DE_total/total_facility * 100)
            shc = DE_shc
            ayush = DE_ayush
            phc = DE_phc
            uphc = DE_uphc
            uhwc = DE_uhwc
            other_func.display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc)
            
        with col3:
            wch_colour_box = (204,20,200)
            wch_colour_font = (0,0,0)
            fontsize = 36
            valign = "left"
            iconname = "fas fa-file"
            sline = "Total Facility Reported Monthly Report (SD)"
            i = sd_total
            per = round(sd_total/total_facility * 100)
            shc = sd_shc
            ayush = sd_ayush
            phc = sd_phc
            uphc = sd_uphc
            uhwc = sd_uhwc
            other_func.display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc)
            
        col1, col2, col3 = st.columns(3)
        with col1:
            wch_colour_box = (50,500,150)
            wch_colour_font = (0,0,0)
            fontsize = 36
            valign = "left"
            iconname = "fas fa-hand-holding-heart"
            sline = "Total Facility Reported Wellness Entry >=10 days"
            i = w_total
            per = round(w_total/total_facility * 100)
            shc = w_shc
            ayush = w_ayush
            phc = w_phc
            uphc = w_uphc
            uhwc = w_uhwc
            other_func.display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc)
                
        with col2:
            wch_colour_box = (230,173,170)
            wch_colour_font = (0,0,0)
            fontsize = 36
            valign = "left"
            iconname = "fas fa-file"
            sline = "80 % availability of Medicine"
            i = drug_total
            per = round(drug_total/total_facility * 100)
            shc = drug_shc
            ayush = drug_ayush
            phc = drug_phc
            uphc = drug_uphc
            uhwc = drug_uhwc
            other_func.display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc)        
        with col3:
            wch_colour_box = (255,195,0)
            wch_colour_font = (0,0,0)
            fontsize = 36
            valign = "left"
            iconname = "fas fa-hand-holding-heart"
            sline = "80 % availability of Diagnostics"
            i = diagnostics_total
            per = round(diagnostics_total/total_facility * 100)
            shc = diagnostics_shc
            ayush = diagnostics_ayush
            phc = diagnostics_phc
            uphc = diagnostics_uphc
            uhwc = diagnostics_uhwc
            other_func.display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc)
    st.markdown("""<div style="background: linear-gradient(to right, orange, yellow, green, blue, indigo, violet, red); height: 3px; width: 100%;"></div><br><br>""", unsafe_allow_html=True)

    menu_data = [
        {'label':"Operational AAM", 'id':"opaam"},   
        {'label': "Monthly Report", 'id': "Monthly_Report"},
        {'label': "Daily Report", 'id': "Daily_Report"},
        {'label': "Wellness Report", 'id': "Wellness_Report"}        
        ]

    menu_id = hc.nav_bar(menu_definition=menu_data)

    if menu_id == "opaam":
        col1, col2=st.columns(2)
        category_order = ['SHC', 'AYUSH', 'PHC', 'UPHC', 'UHWCs', 'Total']
        # Sort the DataFrame based on the custom order
        total_row_only['Category'] = pd.Categorical(total_row_only['Category'], categories=category_order, ordered=True)
        total_row_only = total_row_only.sort_values('Category')
        total_row_only.reset_index(drop=True, inplace=True)                
        total_row_only1 = total_row_only.rename(columns={ 'Operational': 'Operational Facility'})
        with col1:
            st.write("#### Total Target Vs Total Operational Facility")
            st.write("")
            st.write("")
            other_func.formattedtable(total_row_only1[["Category","Target", "Operational Facility"]])             
        with col2:        
            total_row_only1 = total_row_only1.rename(columns={'Category': 'District'})
            other_func.bargraph2(
                total_row_only1,
                x='District',
                y='Operational Facility',
                top='Target',
                titlegraph='Total Target Vs Total Operational Facility',
                yaxistitle='Operational/Target'
            )
        st.markdown("""<div style="background: linear-gradient(to right, orange, yellow, green, blue, indigo, violet, red); height: 3px; width: 100%;"></div><br><br>""", unsafe_allow_html=True)

        #Operational AAM Tab - Formatted Table
        st.write("##### District wise and Facility Type wise Target Vs Operational Ayushman Arogya Mandir")
        def color_percentage(value, cmap='RdYlGn'):
            try:
                if isinstance(value, str):
                    value = float(value.rstrip('%')) / 100  # Convert to a value between 0 and 1
                elif isinstance(value, (int, float)):
                    value = value / 100
                else:
                    raise ValueError("Invalid value type")                
                norm = mcolors.Normalize(vmin=0, vmax=1)
                cmap = plt.get_cmap(cmap)
                rgba = cmap(norm(value))
                color = mcolors.to_hex(rgba)
            except ValueError:
                color = '#ffffff'  # Default to white for non-numeric values
            return color

        def merge_table_headings_with_color(df, cmap='RdYlGn'):
            html = "<table style='border-collapse: collapse;'>"
            html += "<tr style='background-color: #f2f2f2;' align='center'><th rowspan='2' style='border: 1px solid #dddddd;  background-color: #CFE267;'>District_Name</th><th colspan='3' style='border: 1px solid #dddddd; background-color: #6BB8EA;'>SHC</th><th colspan='3' style='border: 1px solid #dddddd; background-color: #A16BEA;'>AYUSH</th><th colspan='3' style='border: 1px solid #dddddd; background-color: #CB6BEA;'>PHC</th><th colspan='3' style='border: 1px solid #dddddd; background-color: #67E2B0;'>UPHC</th><th colspan='3' style='border: 1px solid #dddddd; background-color: #67B0E2;'>UHWCs</th><th colspan='3' style='border: 1px solid #dddddd; background-color: #776BEA;'>TOTAL</th></tr>"
            html += "<tr style='background-color: #f2f2f2;'><th style='border: 1px solid #dddddd; background-color: #6BB8EA;'>SHC</th><th style='border: 1px solid #dddddd; background-color: #6BB8EA;'>Target</th><th style='border: 1px solid #dddddd; background-color: #6BB8EA;'>%</th><th style='border: 1px solid #dddddd; background-color: #A16BEA;'>AYUSH</th><th style='border: 1px solid #dddddd; background-color: #A16BEA;'>Target</th><th style='border: 1px solid #dddddd; background-color: #A16BEA;'>%</th><th style='border: 1px solid #dddddd;background-color: #CB6BEA;'>PHC</th><th style='border: 1px solid #dddddd;background-color: #CB6BEA;'>Target</th><th style='border: 1px solid #dddddd;background-color: #CB6BEA;'>%</th><th style='border: 1px solid #dddddd; background-color: #67E2B0;'>UPHC</th><th style='border: 1px solid #dddddd;background-color: #67E2B0;'>Target</th><th style='border: 1px solid #dddddd; background-color: #67E2B0;'>%</th><th style='border: 1px solid #dddddd; background-color: #67B0E2;'>UHWC</th><th style='border: 1px solid #dddddd; background-color: #67B0E2;'>Target</th><th style='border: 1px solid #dddddd; background-color: #67B0E2;'>%</th><th style='border: 1px solid #dddddd; background-color: #776BEA;'>Total Achievement</th><th style='border: 1px solid #dddddd; background-color: #776BEA;'>Total Target</th><th style='border: 1px solid #dddddd; background-color: #776BEA;'>%</th></tr>"
            for idx, row in df.iterrows():
                if idx == len(df) - 1:  # Check if it's the last row
                    html += "<tr style='font-weight: bold; text-align: center;'>"
                else:
                    html += "<tr>"
                for val, col_name in zip(row, df.columns):
                    if col_name.endswith('%'):
                        color = color_percentage(val, cmap)
                        html += f"<td style='border: 1px solid #dddddd; background-color: {color};' align='center'>{val}</td>"
                    else:
                        html += f"<td style='border: 1px solid #dddddd;' align='center'>{val}</td>"
                html += "</tr>"            
            html += "</table>"
            return html
        # Display the merged table headings with color using HTML
        st.write(merge_table_headings_with_color(targetachievementtable), unsafe_allow_html=True)
        st.markdown(other_func.get_table_download_link(targetachievementtable), unsafe_allow_html=True)        
        st.markdown("---")


if menu_id == "districtreport":
    st.dataframe(FPE)

if menu_id == "blockreport":
    st.dataframe(DE)

if menu_id == "facilityreport":
    st.dataframe(sd)

#gototop button, it will always be at the bootom of the page
other_func.gototop()

other_func.pagecounter()