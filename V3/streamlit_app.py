import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

def load_data():
    """Load data from all sheets into pandas DataFrames"""
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
    # fetch the local path of the uploaded file 

    if uploaded_file:
        try:
            inflow_df = pd.read_excel(uploaded_file, sheet_name='Inflow', parse_dates=['Purchase_Date'])
            outflow_df = pd.read_excel(uploaded_file, sheet_name='Outflow', parse_dates=['Date_of_Distribution'])
            budget_df = pd.read_excel(uploaded_file, sheet_name='Budget')

            # Convert relevant columns to numeric, coercing errors to NaN
            inflow_df['Purchase_Date'] = pd.to_datetime(inflow_df['Purchase_Date'], errors='coerce')
           
            # inflow_df['Total_Cost'] = pd.to_numeric(inflow_df['Total_Cost'], errors='coerce')
            # outflow_df['Cost_per_Item'] = pd.to_numeric(outflow_df['Cost_per_Item'], errors='coerce')
            # outflow_df['Quantity'] = pd.to_numeric(outflow_df['Quantity'], errors='coerce')
            # budget_df['2025_Budget_Amount'] = pd.to_numeric(budget_df['2025_Budget_Amount'], errors='coerce')
            # budget_df['Actual_Amount_Spent'] = pd.to_numeric(budget_df['Actual_Amount_Spent'], errors='coerce')         


            filepath = os.path.join(os.path.dirname(__file__), uploaded_file.name)
            return inflow_df, outflow_df, budget_df, filepath
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None, None, None, None
    return None, None, None, None

def generate_summary_report(inflow_df, outflow_df, budget_df):
    """Create summary of Event Types and Item Types"""
    # Get unique types
    event_types = pd.concat([
        outflow_df['Event_Type'],
        budget_df['Event_Type']
    ]).unique()
    
    item_types = pd.concat([
        inflow_df['Item_Type'],
        outflow_df['Item_Type']
    ]).unique()
    
    # Create summary DataFrames
    event_type_summary = pd.DataFrame({
        'Event_Type': event_types,
        'Total_Budget': [budget_df[budget_df['Event_Type'] == et]['2025_Budget_Amount'].sum() for et in event_types],
        'Total_Distributions': [outflow_df[outflow_df['Event_Type'] == et]['Cost_per_Item'].mul(outflow_df['Quantity']).sum() for et in event_types],
        'Distribution_Count': [outflow_df[outflow_df['Event_Type'] == et].shape[0] for et in event_types]
    })
    
    item_type_summary = pd.DataFrame({
        'Item_Type': item_types,
        'Total_Purchases': [inflow_df[inflow_df['Item_Type'] == it]['Total_Cost'].sum() for it in item_types],
        'Total_Distributions': [outflow_df[outflow_df['Item_Type'] == it]['Cost_per_Item'].mul(outflow_df['Quantity']).sum() for it in item_types],
        'Purchase_Count': [inflow_df[inflow_df['Item_Type'] == it].shape[0] for it in item_types],
        'Distribution_Count': [outflow_df[outflow_df['Item_Type'] == it].shape[0] for it in item_types]
    })
    
    return event_type_summary, item_type_summary

def purchase_page(inflow_df, filepath):
    """Purchase Form Page"""
    st.header("Add New Purchase")
    
    # Initialize session state for temporary records
    if "temp_records" not in st.session_state:
        st.session_state.temp_records = []

    purchase_form = st.form("purchaseform")
    with purchase_form:
        # Required fields
        
        item_type = st.selectbox(
            "Item Type*",
            options=['S', 'M', 'L'],
            help="Select the size of the item"
        )
        item_name = st.text_input("Item Name*")  # Added * to indicate required field
        
        col1, col2 = st.columns(2)
        with col1:
            cost_per_item = st.number_input(
                "Cost per Item*",
                min_value=0.00,
                step=0.01,
                format="%.2f",
                help="Enter the cost per item"
            )
        
        with col2:
            quantity = st.number_input(
                "Quantity*",
                min_value=1,
                value=1,
                help="Enter the quantity to purchase"
            )       

        code = st.text_input("Code")
        purchase_date = st.date_input("Purchase Date")
        vendor_address = st.text_input("Vendor Address")
        vendor_name = st.text_input("Vendor Name*")  # Added * to indicate required field
        contact_name = st.text_input("Contact Name (Vendor)")
        vendor_email = st.text_input("Vendor Email")
        vendor_phone = st.text_input("Vendor Phone")
        
        # Optional fields using expander
        with st.expander("Additional Information (Optional)"):
            extra_vendor_email = st.text_input("Additional Vendor Email")  # Different variable
            extra_vendor_phone = st.text_input("Additional Vendor Phone")  # Different variable
            extra_description = st.text_area("Additional Description")  # Different variable
        
        # Submit Button - Ensure it's inside the form
        submitted = st.form_submit_button("Submit Purchase")  

    # Processing the form submission
    if submitted:
        # Validate required fields
        if not all([item_type, item_name, cost_per_item, quantity, vendor_name]):
            st.error("Please fill in all required fields marked with *")
        else:
            # Generate unique item ID
            item_id = datetime.now().strftime("%y%m%d%H%M%S")
            total_cost = cost_per_item * quantity
            purchase_date_pd = pd.to_datetime(purchase_date)

            # Store submission data
            purchase_data = {
                'Item_ID': item_id,
                'Item_Type': item_type,
                'Item_Name': item_name,
                'Cost_per_Item': cost_per_item,
                'Quantity': quantity,
                'Total_Cost': total_cost,
                'Code': code,
                'Purchase_Date': purchase_date_pd,
                'Vendor_Address': vendor_address,
                'Vendor_Name': vendor_name,
                'Contact_Name_(Vendor)': contact_name,
                'Vendor_Email': vendor_email,
                'Vendor_Phone': vendor_phone,
                'Submission_Timestamp': pd.to_datetime(datetime.now())
            }

            # Append to session state
            st.session_state.temp_records.append(purchase_data)

            try:
                # Create DataFrame for new records
                new_records_df = pd.DataFrame(st.session_state.temp_records)
                
                # Ensure date columns are datetime formatted
                new_records_df['Purchase_Date'] = pd.to_datetime(new_records_df['Purchase_Date'])
                new_records_df['Submission_Timestamp'] = pd.to_datetime(new_records_df['Submission_Timestamp'])
                
                # Concatenate with original data
                updated_df = pd.concat([inflow_df, new_records_df], ignore_index=True)

                st.success("Data successfully saved!")

                # Display the new inflow data
                st.header("Updated Inflow Data")
                st.write(updated_df)

                # Display session submissions
                st.header("Current Session Submissions")
                st.write(new_records_df)

                # Save updated data to Excel
                try:
                    with pd.ExcelWriter(filepath, mode='w', engine='openpyxl') as writer:
                        updated_df['Purchase_Date'] = updated_df['Purchase_Date'].dt.date
                        updated_df.to_excel(writer, sheet_name='Inflow', index=False)
                except Exception as e: 
                    st.error(f"Error saving data: {e}")

            except Exception as e:
                st.error(f"Error processing data: {e}")






def distribute_page():
    """Distribution Form Page"""
    st.header("Distribute Items")
    
    # Load current data
    inflow_df, outflow_df, budget_df = load_data()
    
    if inflow_df is None:
        return
    
    # Show available items
    st.subheader("Available Items")
    available_items = inflow_df[['Item_ID', 'Item_Type', 'Item_name', 'Quantity', 'Cost_per_Item']]
    available_items = available_items[available_items['Quantity'] > 0]  # Only show items with quantity > 0
    st.dataframe(available_items)
    
    with st.form("distribution_form"):
        # Item Selection
        selected_item = st.selectbox(
            "Select Item to Distribute*",
            options=available_items['Item_ID'].tolist(),
            format_func=lambda x: f"{x} - {available_items[available_items['Item_ID'] == x]['Item_name'].iloc[0]}"
        )
        
        # Get selected item details
        item_details = available_items[available_items['Item_ID'] == selected_item].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            # Required fields
            department = st.text_input(
                "Department*",
                help="Enter the receiving department"
            )
            
            gift = st.selectbox(
                "Gift*",
                options=['Yes', 'No'],
                help="Is this a gift?"
            )
            
            quantity = st.number_input(
                "Quantity*",
                min_value=1,
                max_value=int(item_details['Quantity']),
                help=f"Available quantity: {item_details['Quantity']}"
            )
        
        with col2:
            event_type = st.selectbox(
                "Event Type*",
                options=budget_df['Event_Type'].unique().tolist(),
                help="Select the type of event"
            )
            
            event_name = st.text_input(
                "Event Name*",
                help="Enter the name of the event"
            )
            
            distribution_date = st.date_input(
                "Distribution Date*",
                help="Select the date of distribution"
            )
        
        # Optional Notes
        notes = st.text_area(
            "Notes (Optional)",
            help="Add any additional information"
        )
        
        submitted = st.form_submit_button("Submit Distribution")
        
        if submitted:
            # Validate required fields
            if not all([department, event_type, event_name]):
                st.error("Please fill in all required fields marked with *")
                return
            
            # Prepare distribution data
            distribution_data = {
                'Item_ID': selected_item,
                'Event_Type': event_type,
                'Event_Name': event_name,
                'Department': department,
                'Gift': gift,
                'Quantity': quantity,
                'Cost_per_Item': item_details['Cost_per_Item'],
                'Item_Code': '',  # Leave blank or generate if needed
                'Contact_Name_(Event)': '',  # Can be added to form if needed
                'Item_Type': item_details['Item_Type'],
                'Gift_Type': 'Regular' if gift == 'No' else 'Gift',
                'Date_of_Distribution': distribution_date.strftime('%Y-%m-%d'),
                'Completion_Status': 'Completed'
            }
            
            # Display the data that will be added
            st.success("Here's what will be added to the Outflow sheet:")
            st.write(distribution_data)
            

def create_visualizations(inflow_df, outflow_df, budget_df):
    """Create visualizations using plotly"""
    # Total Inflow vs Outflow Bar Chart
    fig1 = go.Figure(data=[
        go.Bar(name='Total Purchases', x=['Total'], y=[inflow_df['Total_Cost'].sum()]),
        go.Bar(name='Total Distributions', x=['Total'], 
               y=[outflow_df['Cost_per_Item'].mul(outflow_df['Quantity']).sum()])
    ])
    fig1.update_layout(title='Total Purchases vs Distributions')

    # Item Type Distribution for Inflow
    inflow_by_type = inflow_df.groupby('Item_Type')['Total_Cost'].sum()
    fig2 = px.pie(values=inflow_by_type.values,
                  names=inflow_by_type.index,
                  title='Purchase Distribution by Item Type')

    # Department-wise Distribution for Outflow
    outflow_by_dept = outflow_df.groupby('Department')['Cost_per_Item'].sum()
    fig3 = px.pie(values=outflow_by_dept.values,
                  names=outflow_by_dept.index,
                  title='Distribution by Department')

    # Budget vs Actual Spending
    fig4 = go.Figure(data=[
        go.Bar(name='Budget Amount', x=budget_df['Event_Type'], y=budget_df['2025_Budget_Amount']),
        go.Bar(name='Actual Spent', x=budget_df['Event_Type'], y=budget_df['Actual_Amount_Spent'])
    ])
    fig4.update_layout(title='Budget vs Actual Spending by Event Type',
                      barmode='group')

    # New visualization: Item Count by Type Pie Chart
    item_type_counts = inflow_df.groupby('Item_Type')['Quantity'].sum()
    fig5 = px.pie(
        values=item_type_counts.values,
        names=item_type_counts.index,
        title='Item Distribution by Type',
        hole=0.4  # Makes it a donut chart
    )
    fig5.update_traces(textposition='inside', textinfo='percent+label')

    # New visualization: Purchase Costs Over Time
    # Date is already in datetime format from load_data()
    daily_costs = inflow_df.groupby('Purchase_Date')['Total_Cost'].sum().reset_index()
    
    fig6 = go.Figure()
    fig6.add_trace(go.Scatter(
        x=daily_costs['Purchase_Date'],
        y=daily_costs['Total_Cost'],
        mode='lines+markers',
        name='Daily Purchase Cost',
        hovertemplate='Date: %{x|%d/%m/%Y}<br>Cost: $%{y:,.2f}<extra></extra>'
    ))
    
    # Add trend line
    fig6.add_trace(go.Scatter(
        x=daily_costs['Purchase_Date'],
        y=daily_costs['Total_Cost'].rolling(window=7).mean(),
        mode='lines',
        name='7-day Moving Average',
        line=dict(dash='dash'),
        hovertemplate='Date: %{x|%d/%m/%Y}<br>Average: $%{y:,.2f}<extra></extra>'
    ))
    
    fig6.update_layout(
        title='Purchase Costs Over Time',
        xaxis_title='Date',
        yaxis_title='Total Cost ($)',
        hovermode='x unified',
        xaxis=dict(
            tickformat='%d/%m/%Y',
            tickangle=45
        )
    )

    return fig1, fig2, fig3, fig4, fig5, fig6          


def main():
    st.title('Inventory Management System')
    # Sidebar navigation
    page = st.sidebar.selectbox('Select Function', ['View Data', 'Purchase', 'Distribute'])
    # Load and display data
    inflow_df, outflow_df, budget_df, filepath = load_data()
    if page == 'Purchase':
        purchase_page(inflow_df, filepath)
    elif page == 'Distribute':
        distribute_page()
    else:  # View Data page
        try:
            if inflow_df is not None:
                # Data Tables Section
                st.header('Current Inventory')
                tabs = st.tabs(['Inflow', 'Outflow', 'Budget'])
                for tab, df in zip(tabs, [inflow_df, outflow_df, budget_df]):
                    with tab:
                        st.dataframe(df)
                
                # Visualizations Section
                st.header('Data Visualizations')
                
                # Create visualizations
                fig1, fig2, fig3, fig4, fig5, fig6 = create_visualizations(inflow_df, outflow_df, budget_df)
                
                # Display main metrics
                col1, col2, col3 = st.columns(3)
                total_purchases = inflow_df['Total_Cost'].sum()
                total_distributions = outflow_df['Cost_per_Item'].mul(outflow_df['Quantity']).sum()
                total_budget = budget_df['2025_Budget_Amount'].sum()
                
                with col1:
                    st.metric("Total Purchases", f"${total_purchases:,.2f}")
                with col2:
                    st.metric("Total Distributions", f"${total_distributions:,.2f}")
                with col3:
                    st.metric("Total Budget", f"${total_budget:,.2f}")
                
                # Display visualizations in tabs
                viz_tabs = st.tabs([
                    'Overview', 
                    'Item Type Analysis', 
                    'Department Analysis',
                    'Budget Analysis',
                    'Item Distribution',
                    'Purchase Trends'
                ])
                
                with viz_tabs[0]:
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Additional summary
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Top 5 Items by Quantity")
                        top_items = inflow_df.nlargest(5, 'Quantity')[
                            ['Item_name', 'Quantity', 'Total_Cost']
                        ]
                        st.dataframe(top_items)
                    
                    with col2:
                        st.subheader("Recent Distributions")
                        recent_dist = outflow_df.nlargest(5, 'Date_of_Distribution')[
                            ['Event_Name', 'Department', 'Quantity', 'Date_of_Distribution']
                        ]
                        # Format the date column
                        recent_dist['Date_of_Distribution'] = recent_dist['Date_of_Distribution'].dt.strftime('%d/%m/%Y')
                        st.dataframe(recent_dist)
                
                with viz_tabs[1]:
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Item type summary
                    st.subheader("Item Type Summary")
                    item_summary = inflow_df.groupby('Item_Type').agg({
                        'Quantity': 'sum',
                        'Total_Cost': 'sum'
                    }).reset_index()
                    st.dataframe(item_summary)
                
                with viz_tabs[2]:
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    # Department distribution summary
                    st.subheader("Department Distribution Summary")
                    dept_summary = outflow_df.groupby('Department').agg({
                        'Quantity': 'sum',
                        'Cost_per_Item': lambda x: (x * outflow_df.loc[x.index, 'Quantity']).sum()
                    }).reset_index()
                    dept_summary.columns = ['Department', 'Total Items', 'Total Value']
                    st.dataframe(dept_summary)
                
                with viz_tabs[3]:
                    st.plotly_chart(fig4, use_container_width=True)
                    
                    # Budget utilization
                    st.subheader("Budget Utilization")
                    budget_summary = budget_df[['Event_Type', '2025_Budget_Amount', 'Actual_Amount_Spent']]
                    budget_summary['Utilization %'] = (
                        budget_summary['Actual_Amount_Spent'] / 
                        budget_summary['2025_Budget_Amount'] * 100
                    ).round(2)
                    st.dataframe(budget_summary)
                
                with viz_tabs[4]:  # New Item Distribution tab
                    st.plotly_chart(fig5, use_container_width=True)
                    
                    # Add summary table
                    st.subheader("Item Type Distribution Summary")
                    type_summary = inflow_df.groupby('Item_Type').agg({
                        'Quantity': 'sum',
                        'Total_Cost': 'sum',
                        'Item_name': 'count'
                    }).reset_index()
                    type_summary.columns = ['Item Type', 'Total Quantity', 'Total Cost', 'Unique Items']
                    st.dataframe(type_summary.style.format({
                        'Total Cost': '${:,.2f}',
                        'Total Quantity': '{:,}',
                        'Unique Items': '{:,}'
                    }))
                
                with viz_tabs[5]:  # New Purchase Trends tab
                    st.plotly_chart(fig6, use_container_width=True)
                    
                    # Add monthly summary
                    st.subheader("Monthly Purchase Summary")
                    monthly_summary = inflow_df.set_index('Purchase_Date').resample('ME').agg({
                        'Total_Cost': 'sum',
                        'Quantity': 'sum',
                        'Item_name': 'count'
                    }).reset_index()
                    monthly_summary.columns = ['Month', 'Total Cost', 'Items Purchased', 'Unique Items']
                    # Format the month in dd/mm/yyyy
                    monthly_summary['Month'] = monthly_summary['Month'].dt.strftime('%d/%m/%Y')
                    st.dataframe(monthly_summary.style.format({
                        'Total Cost': '${:,.2f}',
                        'Items Purchased': '{:,}',
                        'Unique Items': '{:,}'
                    }))
                
                # Add Text Summary Section
                st.header('Summary Report')
                st.markdown("""---""")  # Horizontal line

                # Calculate key metrics
                total_purchases = inflow_df['Total_Cost'].sum()  # Sum of Total_Cost from Inflow sheet
                total_distributions = outflow_df['Total_Cost'].sum()  # Sum of Total_Cost from Outflow sheet
                total_items_purchased = inflow_df['Quantity'].sum()
                total_items_distributed = outflow_df['Quantity'].sum()
                items_in_stock = total_items_purchased - total_items_distributed
                budget_utilization = (budget_df['Actual_Amount_Spent'].sum() / budget_df['2025_Budget_Amount'].sum() * 100).round(2)
                
                # Get top departments and items
                top_departments = outflow_df.groupby('Department')['Quantity'].sum().nlargest(3)
                top_items = inflow_df.groupby('Item_name')['Quantity'].sum().nlargest(3)
                
                # Create summary text
                summary_text = f"""
                ### Inventory Overview
                As of {datetime.now().strftime('%B %d, %Y')}, our inventory system shows the following key metrics:

                **Financial Summary:**
                - Total purchases amount to ${total_purchases:,.2f}
                - Total distributions value is ${total_distributions:,.2f}
                - Current budget utilization is {budget_utilization}% of the total ${total_budget:,.2f} budget

                **Inventory Status:**
                - Total items purchased: {total_items_purchased:,}
                - Total items distributed: {total_items_distributed:,}
                - Current items in stock: {items_in_stock:,}

                **Top Performing Departments:**
                {', '.join([f"{dept} ({qty:,} items)" for dept, qty in top_departments.items()])}

                **Most Active Items:**
                {', '.join([f"{item} ({qty:,} units)" for item, qty in top_items.items()])}

                **Key Observations:**
                - {'Budget utilization is within expected range' if budget_utilization < 80 else 'Budget utilization is high and needs attention'}
                - {'Inventory levels are healthy' if items_in_stock > 100 else 'Inventory levels are low and may need restocking'}
                - The distribution pattern shows {outflow_df['Department'].nunique()} active departments
                """
                
                st.markdown(summary_text)
                
                # Additional Notes or Recommendations
                if budget_utilization > 80:
                    st.warning("⚠️ Budget utilization is high. Consider reviewing spending patterns.")
                if items_in_stock < 100:
                    st.warning("⚠️ Low inventory levels detected. Consider restocking popular items.")

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("Please make sure the data Sheet is accessible.")
    
    
if __name__ == '__main__':
    main()
