import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import load_excel, save_excel

def main():
    st.title("Inventory Management System")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx'])
    
    if uploaded_file is not None:
        # Load Excel file
        inflow_df, outflow_df, budget_df = load_excel(uploaded_file)
        
        # Display Inflow data
        st.subheader("Inflow Data")
        st.dataframe(inflow_df)
        
        # Create buttons for Purchase and Distribution
        col1, col2 = st.columns(2)
        with col1:
            purchase_button = st.button("Purchase")
        with col2:
            distribution_button = st.button("Distribution")
            
        if purchase_button:
            st.subheader("New Purchase")
            
            # Create input form
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
                    # Calculate total cost and quantity left
                    total_cost = cost_per_item * quantity
                    quantity_left = quantity
                    
                    # Create new row
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
                    
                    # Add new row to inflow_df
                    inflow_df = pd.concat([inflow_df, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Save updated data
                    save_excel(uploaded_file, inflow_df, outflow_df, budget_df)
                    st.success("Purchase record added successfully!")
                    
        if distribution_button:
            st.subheader("Add Distribution Record")
            
            # Let user select an item from inflow
            selected_item = st.selectbox(
                "Select Item",
                inflow_df[['Item_ID', 'Item_Type', 'Item_name']].apply(
                    lambda x: f"{x['Item_ID']} - {x['Item_Type']} - {x['Item_name']}", 
                    axis=1
                )
            )
            
            if selected_item:
                item_id = selected_item.split(' - ')[0]
                item_data = inflow_df[inflow_df['Item_ID'] == item_id].iloc[0]
                
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
                        # Create new row for outflow
                        new_row = {
                            'Item_ID': item_data['Item_ID'],
                            'Item_Type': item_data['Item_Type'],
                            'Item_name': item_data['Item_name'],
                            'Quantity': quantity,
                            'Event_type': event_type,
                            'Event_Name': event_name,
                            'Event_Date': event_date
                        }
                        
                        # Update outflow_df
                        outflow_df = pd.concat([outflow_df, pd.DataFrame([new_row])], ignore_index=True)
                        
                        # Update quantity_left in inflow_df
                        inflow_df.loc[inflow_df['Item_ID'] == item_id, 'Quantity_Left'] -= quantity
                        
                        # Save updated data
                        save_excel(uploaded_file, inflow_df, outflow_df, budget_df)
                        st.success("Distribution record added successfully!")
        
        # Data Visualization
        st.subheader("Data Visualization")
        
        # Item Type Distribution
        fig1 = px.pie(inflow_df, names='Item_Type', title='Distribution of Items by Type')
        st.plotly_chart(fig1)
        
        # Monthly Purchase Trends
        inflow_df['Purchase_Date'] = pd.to_datetime(inflow_df['Purchase_Date'])
        monthly_purchases = inflow_df.groupby(inflow_df['Purchase_Date'].dt.strftime('%Y-%m'))[['Total_Cost']].sum()
        fig2 = px.line(monthly_purchases, title='Monthly Purchase Trends')
        st.plotly_chart(fig2)
        
        # Inventory Status
        inventory_status = inflow_df.groupby('Item_Type')[['Quantity_Left']].sum()
        fig3 = px.bar(inventory_status, title='Current Inventory Status by Item Type')
        st.plotly_chart(fig3)

if __name__ == "__main__":
    main() 