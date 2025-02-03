import streamlit as st
import pandas as pd

# File upload
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

if uploaded_file is not None:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)
    
    # Display and edit the data
    edited_df = st.data_editor(df)
    
    # Add functionality to save changes
    if st.button("Save Changes"):
        edited_df.to_excel("updated_file.xlsx", index=False)
        st.success("Changes saved successfully!")