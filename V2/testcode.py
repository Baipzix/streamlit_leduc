import streamlit as st
import pandas as pd

# Load spreadsheet ID from secrets.toml
SPREADSHEET_ID = st.secrets["1cRSUykiV5tWa6917qEJfTcAJz9rAHMmfFCRl-UgM2wM"]


# Function to read a sheet as a DataFrame
def read_google_sheet(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    return df

# Streamlit UI
st.title("Inventory Budget Management")

tab1, tab2, tab3 = st.tabs(["Inflow", "Outflow", "Budget"])

with tab1:
    st.header("Inflow Data")
    inflow_df = read_google_sheet("Inflow")
    st.dataframe(inflow_df)

with tab2:
    st.header("Outflow Data")
    outflow_df = read_google_sheet("Outflow")
    st.dataframe(outflow_df)

with tab3:
    st.header("Budget Summary")
    budget_df = read_google_sheet("Budget")
    st.dataframe(budget_df)
