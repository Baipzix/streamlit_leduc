import streamlit as st
import pandas as pd 

#st.title("interactive edit  ")

readt= st.header("orignial data")
#create an interface to that can browse files and return the file path
uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)




input_form = st.form("inputform ")

# create input form with the following name Item_ID	Item_Type	Item_name	Cost_per_Item	Quantity	Total_Cost	Code	Purchase_Date	Vendor_Address	Description	Vendor_Name	Contact_Name_(Vendor)	Vendor_Email	Vendor_Phone
with input_form:
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
    contact_name = st.text_input("Contact Name (Vendor)")
    vendor_email = st.text_input("Vendor Email")
    vendor_phone = st.text_input("Vendor Phone")
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not item_id or not item_name:
            st.error("Item ID and Item Name are required!")
        else:
            total_cost = cost_per_item * quantity
            new_data = {
                'Item_ID': item_id,
                'Item_Type': item_type,
                'Item_name': item_name,
                'Cost_per_Item': cost_per_item,
                'Quantity': quantity,
                'Total_Cost': total_cost,
                'Code': code,
                'Purchase_Date': purchase_date,
                'Vendor_Address': vendor_address,
                'Description': description,
                'Vendor_Name': vendor_name,
                'Contact_Name_(Vendor)': contact_name,
                'Vendor_Email': vendor_email,
                'Vendor_Phone': vendor_phone
            }
            new_df = pd.DataFrame([new_data])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(r"C:\Users\hli69\Downloads\2025-01-31T07-16_export.csv", index = False)
            st.header("new data")
            st.write(df)
            


