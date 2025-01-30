import pandas as pd

class DataManager:
    def __init__(self):
        self.inflow_data = None
        self.outflow_data = None
        self.budget_data = None
    
    def set_data(self, inflow_df, outflow_df, budget_df):
        self.inflow_data = inflow_df
        self.outflow_data = outflow_df
        self.budget_data = budget_df
    
    def has_data(self):
        return self.inflow_data is not None and \
               self.outflow_data is not None and \
               self.budget_data is not None
    
    def get_data(self, data_type):
        if data_type == "inflow":
            return self.inflow_data
        elif data_type == "outflow":
            return self.outflow_data
        elif data_type == "budget":
            return self.budget_data
        else:
            raise ValueError("Invalid data type")
    
    def add_item(self, data_type, item_data):
        if data_type == "inflow":
            self.inflow_data = pd.concat([self.inflow_data, pd.DataFrame([item_data])])
        elif data_type == "outflow":
            self.outflow_data = pd.concat([self.outflow_data, pd.DataFrame([item_data])])
        elif data_type == "budget":
            self.budget_data = pd.concat([self.budget_data, pd.DataFrame([item_data])])
    
    def modify_item(self, data_type, index, item_data):
        if data_type == "inflow":
            self.inflow_data.loc[index] = item_data
        elif data_type == "outflow":
            self.outflow_data.loc[index] = item_data
        elif data_type == "budget":
            self.budget_data.loc[index] = item_data
    
    def delete_item(self, data_type, index):
        if data_type == "inflow":
            self.inflow_data = self.inflow_data.drop(index)
        elif data_type == "outflow":
            self.outflow_data = self.outflow_data.drop(index)
        elif data_type == "budget":
            self.budget_data = self.budget_data.drop(index) 