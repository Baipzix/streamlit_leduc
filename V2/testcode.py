import streamlit as st
import pandas as pd
import io

# App title
st.title("Inventory Management System")

# Session state to store the uploaded data
if "df_inflow" not in st.session_state:
    st.session_state.df_inflow = None

# File uploader
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    # Read Excel file
    xls = pd.ExcelFile(uploaded_file)

    # Load sheets
    if "Inflow" in xls.sheet_names:
        st.session_state.df_inflow = pd.read_excel(xls, sheet_name="Inflow")
    else:
        st.session_state.df_inflow = pd.DataFrame(columns=[
            'Item_ID', 'Item_Type', 'Item_name', 'Cost_per_Item', 'Quantity', 
            'Quantity_Left', 'Total_Cost', 'Code', 'Purchase_Date', 
            'Vendor_Address', 'Description', 'Vendor_Name', 
            'Vendor_Email', 'Vendor_Phone'
        ])

# Ensure the dataframe exists
if st.session_state.df_inflow is not None:
    # Select sheet to display
    sheet_selection = st.selectbox("Select Data Sheet", ["Inflow", "Outflow", "Budget"])

    if sheet_selection == "Inflow":
        st.dataframe(st.session_state.df_inflow)

    # Buttons for actions
    action = st.radio("Select an action", ["View Only", "Purchase"])

    if action == "Purchase":
        with st.form("purchase_form"):
            item_id = st.text_input("Item ID")
            item_type = st.text_input("Item Type")
            item_name = st.text_input("Item Name")
            cost_per_item = st.number_input("Cost per Item", min_value=0.0, format="%.2f")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            total_cost = cost_per_item * quantity
            code = st.text_input("Code")
            purchase_date = st.date_input("Purchase Date")
            vendor_address = st.text_area("Vendor Address")
            description = st.text_area("Description")
            vendor_name = st.text_input("Vendor Name")
            vendor_email = st.text_input("Vendor Email")
            vendor_phone = st.text_input("Vendor Phone")

            submitted = st.form_submit_button("Submit")

            if submitted:
                # Create new row as a DataFrame
                new_row = pd.DataFrame([{
                    'Item_ID': item_id,
                    'Item_Type': item_type,
                    'Item_name': item_name,
                    'Cost_per_Item': cost_per_item,
                    'Quantity': quantity,
                    'Quantity_Left': quantity,  # Assume quantity left = quantity initially
                    'Total_Cost': total_cost,
                    'Code': code,
                    'Purchase_Date': purchase_date,
                    'Vendor_Address': vendor_address,
                    'Description': description,
                    'Vendor_Name': vendor_name,
                    'Vendor_Email': vendor_email,
                    'Vendor_Phone': vendor_phone
                }])

                # Append new data
                st.session_state.df_inflow = pd.concat([st.session_state.df_inflow, new_row], ignore_index=True)

                # Display updated data
                st.success("Data added successfully!")
                st.dataframe(st.session_state.df_inflow)

    # Save updated file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.df_inflow.to_excel(writer, sheet_name="Inflow", index=False)
    output.seek(0)

    # Download button
    st.download_button(
        "Download Updated File",
        output,
        file_name="Updated_Inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
