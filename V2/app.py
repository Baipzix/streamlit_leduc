import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import load_excel, save_excel

def submit_purchase_form():
    """Handles submission of the purchase form"""
    with st.form("purchase_form"):
        item_id = st.text_input("Item ID")
        item_type = st.text_input("Item Type")
        item_name = st.text_input("Item Name")
        cost_per_item = st.number_input("Cost per Item", min_value=0.0)
        quantity = st.number_input("Quantity", min_value=1)
        code = st.text_input("Code")
        purchase_date = st.date_input("Purchase Date")
        vendor_address = st.text_input("Vendor Address")
        description = st.text_area("Description")
        vendor_name = st.text_input("Vendor Name")
        vendor_email = st.text_input("Vendor Email")
        vendor_phone = st.text_input("Vendor Phone")

        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if not item_id or not item_name:
                st.error("Item ID and Item Name are required!")
                return

            total_cost = cost_per_item * quantity
            quantity_left = quantity
            
            new_row = {
                'Item_ID': item_id,
                'Item_Type': item_type,
                'Item_name': item_name,
                'Cost_per_Item': cost_per_item,
                'Quantity': quantity,
                'Quantity_Left': quantity_left,
                'Total_Cost': total_cost,
                'Code': code,
                'Purchase_Date': purchase_date,
                'Vendor_Address': vendor_address,
                'Description': description,
                'Vendor_Name': vendor_name,
                'Vendor_Email': vendor_email,
                'Vendor_Phone': vendor_phone
            }

            # Ensure inflow_df is initialized
            if "inflow_df" not in st.session_state or st.session_state.inflow_df is None:
                st.session_state.inflow_df = pd.DataFrame(columns=new_row.keys())

            # Append new row to inflow DataFrame
            st.session_state.inflow_df = pd.concat([st.session_state.inflow_df, pd.DataFrame([new_row])], ignore_index=True)

            # Save updated data
            save_excel(st.session_state.uploaded_file, st.session_state.inflow_df, st.session_state.outflow_df, st.session_state.budget_df)
            
            st.success("Purchase record added successfully!")

            # Force UI refresh to display the new row
            st.rerun()

def submit_distribution_form(df):
    st.subheader("Add Distribution Record")
    if st.session_state.inflow_df is not None and not st.session_state.inflow_df.empty:
        selected_item = st.selectbox(
            "Select Item",
            st.session_state.inflow_df[['Item_ID', 'Item_Type', 'Item_name']].apply(
                lambda x: f"{x['Item_ID']} - {x['Item_Type']} - {x['Item_name']}", 
                axis=1
            )
        )

    if selected_item:
        item_id = selected_item.split(' - ')[0]
        item_data = st.session_state.inflow_df[st.session_state.inflow_df['Item_ID'] == item_id].iloc[0]

        with st.form("distribution_form"):
            st.text(f"Item ID: {item_data['Item_ID']}")
            st.text(f"Item Type: {item_data['Item_Type']}")
            st.text(f"Item Name: {item_data['Item_name']}")

            quantity = st.number_input("Quantity", min_value=1, max_value=int(item_data['Quantity_Left']))
            event_type = st.text_input("Event Type")
            event_name = st.text_input("Event Name")
            event_date = st.date_input("Event Date")

            submit_button = st.form_submit_button("Submit")

            if submit_button:
                new_row = {
                    'Item_ID': item_data['Item_ID'],
                    'Item_Type': item_data['Item_Type'],
                    'Item_name': item_data['Item_name'],
                    'Quantity': quantity,
                    'Event_type': event_type,
                    'Event_Name': event_name,
                    'Event_Date': event_date
                }

                st.session_state.outflow_df = pd.concat([st.session_state.outflow_df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.inflow_df.loc[st.session_state.inflow_df['Item_ID'] == item_id, 'Quantity_Left'] -= quantity

                save_excel(uploaded_file, st.session_state.inflow_df, st.session_state.outflow_df, st.session_state.budget_df)
                st.success("Distribution record added successfully!")
                st.rerun()


def main():
    st.title("Inventory Management System")

    # Initialize session state variables
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'inflow_df' not in st.session_state:
        st.session_state.inflow_df = None
    if 'outflow_df' not in st.session_state:
        st.session_state.outflow_df = None
    if 'budget_df' not in st.session_state:
        st.session_state.budget_df = None

    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        if st.session_state.inflow_df is None:
            st.session_state.inflow_df, st.session_state.outflow_df, st.session_state.budget_df = load_excel(uploaded_file)

        st.subheader("Inflow Data")
        st.dataframe(st.session_state.inflow_df)

        col1, col2 = st.columns(2)
        with col1:
            purchase_button = st.button("Purchase")
        with col2:
            distribution_button = st.button("Distribution")

        if purchase_button:
            submit_purchase_form()

        if distribution_button:
            submit_distribution_form(inflow_df, outflow_df)

        st.subheader("Data Visualization")
        if st.session_state.inflow_df is not None and not st.session_state.inflow_df.empty:
            fig1 = px.pie(st.session_state.inflow_df, names='Item_Type', title='Distribution of Items by Type')
            st.plotly_chart(fig1)

            st.session_state.inflow_df['Purchase_Date'] = pd.to_datetime(st.session_state.inflow_df['Purchase_Date'])
            monthly_purchases = st.session_state.inflow_df.groupby(st.session_state.inflow_df['Purchase_Date'].dt.strftime('%Y-%m'))[['Total_Cost']].sum()
            fig2 = px.line(monthly_purchases, title='Monthly Purchase Trends')
            st.plotly_chart(fig2)

            inventory_status = st.session_state.inflow_df.groupby('Item_Type')[['Quantity_Left']].sum()
            fig3 = px.bar(inventory_status, title='Current Inventory Status by Item Type')
            st.plotly_chart(fig3)

if __name__ == "__main__":
    main()
