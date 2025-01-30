import pandas as pd
import streamlit as st
from io import BytesIO

def load_excel(file):
    """Load Excel file with three sheets: Inflow, Outflow, and Budget"""
    try:
        inflow_df = pd.read_excel(file, sheet_name='Inflow')
        outflow_df = pd.read_excel(file, sheet_name='Outflow')
        budget_df = pd.read_excel(file, sheet_name='Budget')
        return inflow_df, outflow_df, budget_df
    except Exception as e:
        st.error(f"Error loading Excel file: {str(e)}")
        return None, None, None

def save_excel(original_file, inflow_df, outflow_df, budget_df):
    """Save updated data back to Excel file"""
    try:
        # Create a BytesIO object to store the Excel file
        buffer = BytesIO()
        
        # Create Excel writer object
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            inflow_df.to_excel(writer, sheet_name='Inflow', index=False)
            outflow_df.to_excel(writer, sheet_name='Outflow', index=False)
            budget_df.to_excel(writer, sheet_name='Budget', index=False)
        
        # Get the value of the BytesIO buffer
        excel_data = buffer.getvalue()
        
        # Create download button
        st.download_button(
            label="Download updated Excel file",
            data=excel_data,
            file_name="updated_inventory.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Error saving Excel file: {str(e)}") 