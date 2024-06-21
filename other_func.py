import streamlit as st
from io import BytesIO  
import base64
import altair as alt
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt

#--------------------------------------------------------------------------------------------------------
def gototop():
    # Add a button at the end of the page to scroll to the top
    st.markdown(
        """
        <style>
            .scroll-to-top-button {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 24px;
                cursor: pointer;
                transition: background-color 0.3s;
            }

            .scroll-to-top-button:hover {
                background-color: #0056b3;
            }
        </style>
        """
        , unsafe_allow_html=True)

    st.markdown(
        """
        <a href="#top">
        <button class="scroll-to-top-button" onclick="scrollToTop()">
            &#8679;
        </button>
        </a>
        """
        , unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------------------
def generate_excel_download_link(df):
    # Credit Excel: https://discuss.streamlit.io/t/how-to-add-a-download-excel-csv-function-to-a-button/4474/5
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Rename_This_File.xlsx">Download </a>'
    return st.markdown(href, unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------------------
#KPI colored boxes at the top
def display_custom_box(wch_colour_box, wch_colour_font, fontsize, valign, iconname, sline, i, per, shc, ayush, phc, uphc, uhwc):
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'
    htmlstr = f"""<p style='background-color: rgb({wch_colour_box[0]}, 
                                                {wch_colour_box[1]}, 
                                                {wch_colour_box[2]}, 0.75); 
                            color: rgb({wch_colour_font[0]}, 
                                    {wch_colour_font[1]}, 
                                    {wch_colour_font[2]}, 0.75); 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 12px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{iconname} fa-xs'></i><b> {i}</b> ({per}%)</style>
                            <BR><span style='font-size: 16px;margin-top: 0;'><b>{sline}</style></span>
                            <BR><span style='font-size: 14px;margin-top: 0;'> SHC - {shc}, AYUSH - {ayush}, PHC - {phc}, UPHC - {uphc}, UHWCS - {uhwc}</b></p>"""
    st.markdown(lnk + htmlstr, unsafe_allow_html=True)

