import streamlit as st



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

#--------------------------------------------------------------------------------------------------------
def gototop():
    # Add a button at the end of the page to scroll to the top
    st.markdown(
        """
        <style>
            .scroll-to-top-button {
                position: fixed;
                bottom: 45px;
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
    
    #------------------------------------------------
    #formatted Table
def formattedtable(table_df):     
        table_df1=table_df
        # Calculate the percentage and store in a new column
        table_df1.iloc[:, 0] = table_df1.iloc[:, 0].replace('Total', 'Jharkhand Total')
        #divided by 0 error aslo handeled
        table_df1['Percentage'] = (table_df1.iloc[:, 2] / (table_df1.iloc[:, 1] + 1e-10)) * 100
        table_df1=table_df1.sort_values(by='Percentage', ascending=False)
        # Handle division by zero and NaN values
        table_df1['Percentage'] = table_df1['Percentage'].fillna(0).replace([float('inf'), -float('inf')], 0)
        # Format the percentage to 2 decimal places
        table_df1['Percentage'] = table_df1['Percentage'].map('{:.2f}'.format)
        # Apply heatmap to the Occurrences column (RdYlGn/summer_r/PiYG)
        styled_df = table_df1.style.background_gradient(subset=['Percentage'], cmap='RdYlGn').set_properties(**{'font-weight': 'bold','color': 'black', 'border-color': 'light gray'})
        # Add custom styling for column headers
        styled_df = styled_df.set_table_styles(
            [{'selector': 'thead th', 'props': [('background-color', '#2196F3'), ('color', 'white')]}]
        )
        # Hide the index column
        styled_df = styled_df.hide(axis='index')        
        # Convert styled dataframe to HTML
        html_table = styled_df.to_html()
        # Display the styled, sorted merged dataframe with heatmap
        st.markdown(html_table, unsafe_allow_html=True)         
        #generate_excel_download_link(styled_df)  