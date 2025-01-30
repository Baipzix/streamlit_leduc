# Standard library imports
import os

# Third party imports
import streamlit as st
import pandas as pd
import plotly.express as px

# Local imports
from data_manager import DataManager

# Initialize DataManager
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

def main():
    st.title("Inventory Management System")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select a page",
        ["Data Upload", "Data Visualization", "Data Management"]
    )
    
    if page == "Data Upload":
        show_upload_page()
    elif page == "Data Visualization":
        show_visualization_page()
    else:
        show_management_page()

def show_upload_page():
    st.header("Data Upload")
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            # Read all sheets
            inflow_df = pd.read_excel(uploaded_file, sheet_name="Inflow")
            outflow_df = pd.read_excel(uploaded_file, sheet_name="Outflow")
            budget_df = pd.read_excel(uploaded_file, sheet_name="Budget")
            
            # Store in session state
            st.session_state.data_manager.set_data(inflow_df, outflow_df, budget_df)
            st.success("Data uploaded successfully!")
            
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")

def show_visualization_page():
    st.header("Data Visualization")
    
    if not st.session_state.data_manager.has_data():
        st.warning("Please upload data first!")
        return
    
    # Select visualization type
    viz_type = st.selectbox(
        "Select Visualization",
        ["Inventory Flow", "Item Types Distribution", "Vendor Analysis", "Cost Analysis"]
    )
    
    if viz_type == "Inventory Flow":
        show_inventory_flow()
    elif viz_type == "Item Types Distribution":
        show_item_types_distribution()
    elif viz_type == "Vendor Analysis":
        show_vendor_analysis()
    else:
        show_cost_analysis()

def show_management_page():
    st.header("Data Management")
    
    if not st.session_state.data_manager.has_data():
        st.warning("Please upload data first!")
        return
    
    operation = st.selectbox(
        "Select Operation",
        ["View Data", "Add Item", "Modify Item", "Delete Item"]
    )
    
    data_type = st.selectbox("Select Data Type", ["Inflow", "Outflow", "Budget"])
    
    if operation == "View Data":
        display_data(data_type)
    elif operation == "Add Item":
        add_item(data_type)
    elif operation == "Modify Item":
        modify_item(data_type)
    else:
        delete_item(data_type)

def display_data(data_type):
    df = st.session_state.data_manager.get_data(data_type.lower())
    st.dataframe(df)

def add_item(data_type):
    st.subheader(f"Add New {data_type} Item")
    # Add form fields based on data type
    # Implementation details will be added later

def modify_item(data_type):
    st.subheader(f"Modify {data_type} Item")
    # Modification form
    # Implementation details will be added later

def delete_item(data_type):
    st.subheader(f"Delete {data_type} Item")
    # Delete interface
    # Implementation details will be added later

def show_inventory_flow():
    # Create inventory flow visualization
    inflow_df = st.session_state.data_manager.get_data("inflow")
    outflow_df = st.session_state.data_manager.get_data("outflow")
    
    # Example visualization
    fig = px.timeline(
        inflow_df,
        x_start="date",
        y="item_name",
        color="item_type"
    )
    st.plotly_chart(fig)

def show_item_types_distribution():
    # Create item types distribution visualization
    pass

def show_vendor_analysis():
    # Create vendor analysis visualization
    pass

def show_cost_analysis():
    # Create cost analysis visualization
    pass

if __name__ == "__main__":
    main() 