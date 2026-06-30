
import unittest
import pandas 
import pytest

from src.etl.transfrom.pytool.pytool import PyTool

from src.models.connector import MongoConnector
from pymongo.write_concern import WriteConcern
wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestPyTool(unittest.TestCase):
    def test_execute(self):
        data1 = [
            [1, 'Alice', 25, pandas.Timestamp('2022-01-01 00:00:00')],
            [2, 'Bob', 30, pandas.Timestamp('2022-02-15 00:00:00')],
            [3, 'Charlie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'David', 40, pandas.Timestamp('2022-04-10 00:00:00')]
        ]
        columns1 = ['ID', 'Name', 'Age', 'Date']
        df1 = pandas.DataFrame(data1, columns=columns1)
        data2 = [
            [3, 'Charlie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'David', 40, pandas.Timestamp('2022-04-10 00:00:00')],
            [5, 'Eve', 45, pandas.Timestamp('2022-05-05 00:00:00')],
            [6, 'Frank', 50, pandas.Timestamp('2022-06-20 00:00:00')]
        ]
        columns2 = ['ID', 'Name', 'Age', 'Date']
        df2 = pandas.DataFrame(data2, columns=columns2)
        dataframes = {'6602a3a74475001648200351':{'df': df1, 'alias': 'customers-100'},
                           '6602a3a74475001648200352':{'df': df2, 'alias': 'industry'}}
        parameters = {"code": """print('hello world !!')\na = 5\nb = 10\nprint(f"The sum of a and b is {a + b}")\nprint(DataframeInformation)"""}
        PyTool().execute(dataframes, parameters, {}, None)
        #self.assertTrue(actual_result)

    def test_execute_with_create_dfinfo(self):
        data1 = [
            [1, 'Ali-ce', 25, pandas.Timestamp('2022-01-01 00:00:00')],
            [2, 'Bo-b', 30, pandas.Timestamp('2022-02-15 00:00:00')],
            [3, 'Char-lie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'Dav-id', 40, pandas.Timestamp('2022-04-10 00:00:00')]
        ]
        columns1 = ['ID', 'Name', 'Age', 'Date']
        df1 = pandas.DataFrame(data1, columns=columns1)
        data2 = [
            [3, 'Cha-rlie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'Dav-id', 40, pandas.Timestamp('2022-04-10 00:00:00')],
            [5, 'Ev-e', 45, pandas.Timestamp('2022-05-05 00:00:00')],
            [6, 'Fra-nk', 50, pandas.Timestamp('2022-06-20 00:00:00')]
        ]
        columns2 = ['ID', 'Name', 'Age', 'Date']
        df2 = pandas.DataFrame(data2, columns=columns2)
        dataframes = {'6602a3a74475001648200351':{'df': df1, 'alias': 'customers-100'},
                           '6602a3a74475001648200352':{'df': df2, 'alias': 'industry'},"type": "LLM"}
        parameters = {"code": "df = DataframeInformation.get(alias=\"customers-100\"); c_id, c_name = df['Name'].str.split('-', expand=True); df[['c_id', 'c_name']] = c_id, c_name; DataframeInformation.create('Data_2020', df, '3456456')"}

        succ, message, output, data_dict = PyTool().execute(dataframes, parameters, {"user_id": "6619156aa5f4c5c1b01e4d07", "chat_id": "65cb43f2007a5f38718b9d6a"}, session)
        self.assertTrue(succ)
        self.assertEqual(output, [{'source_id': '3456456', 'dataframe_alias': 'Data_2020'}])

    def test_execute_with_import_statements(self):
        data1 = [
            [1, 'Alice', 25, pandas.Timestamp('2022-01-01 00:00:00')],
            [2, 'Bob', 30, pandas.Timestamp('2022-02-15 00:00:00')],
            [3, 'Charlie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'David', 40, pandas.Timestamp('2022-04-10 00:00:00')]
        ]
        columns1 = ['ID', 'Name', 'Age', 'Date']
        df1 = pandas.DataFrame(data1, columns=columns1)
        data2 = [
            [3, 'Charlie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'David', 40, pandas.Timestamp('2022-04-10 00:00:00')],
            [5, 'Eve', 45, pandas.Timestamp('2022-05-05 00:00:00')],
            [6, 'Frank', 50, pandas.Timestamp('2022-06-20 00:00:00')]
        ]
        columns2 = ['ID', 'Name', 'Age', 'Date']
        df2 = pandas.DataFrame(data2, columns=columns2)
        dataframes = {'6602a3a74475001648200351':{'df': df1, 'alias': 'customers-100'},
                           '6602a3a74475001648200352':{'df': df2, 'alias': 'industry'}}
        parameters = {"code": """\nimport pandas as pd\ndef sample(a):\n    df=pd.DataFrame()\n    print("empty Dataframe",df)	\n    print("sampleWord",a)\nsample("utkarsh")"""}
        PyTool().execute(dataframes, parameters, {}, None)
        #self.assertTrue(actual_result)

    def test_execute_with_numpy(self):
        # Sample data for DataFrame 1
        data1 = [
            [1, 'Alice', 25, pandas.Timestamp('2022-01-01 00:00:00')],
            [2, 'Bob', 30, pandas.Timestamp('2022-02-15 00:00:00')],
        ]
        columns1 = ['ID', 'Name', 'Age', 'Date']
        df1 = pandas.DataFrame(data1, columns=columns1)

        # Sample data for DataFrame 2
        data2 = [
            [3, 'Charlie', 35, pandas.Timestamp('2022-03-20 00:00:00')],
            [4, 'David', 40, pandas.Timestamp('2022-04-10 00:00:00')],
        ]
        columns2 = ['ID', 'Name', 'Age', 'Date']
        df2 = pandas.DataFrame(data2, columns=columns2)

        # Store the DataFrames in a dictionary
        dataframes = {'6602a3a74475001648200351': {'df': df1, 'alias': 'customers-100'},
                    '6602a3a74475001648200352': {'df': df2, 'alias': 'industry'}}

        # Example parameters
        parameters = {
        "code": """
import numpy as np
df1 = DataframeInformation.get(alias="customers-100")
df2 = DataframeInformation.get(alias="industry")

# Create a NumPy array of ages from both DataFrames
ages_df1 = np.array(df1['Age'])
ages_df2 = np.array(df2['Age'])

# Calculate the sum of ages in both DataFrames
sum_ages_df1 = np.sum(ages_df1)
sum_ages_df2 = np.sum(ages_df2)

# Print the sum of ages
print(f"Sum of ages in customers-100: {sum_ages_df1}")
print(f"Sum of ages in industry: {sum_ages_df2}")
"""
        }

        # Simulating the execution of the parameters and code within the PyTool context
        PyTool().execute(dataframes, parameters, {}, None)

    def test_execute_with_fuzzywuzzy(self):
        old_prd_dataset = pandas.DataFrame({
            'new_price_$':[1,4,3.5,0.7,0.8],
            'old_product_name':['milk','cheese white','cheese yellow','pepper r','apples']
        })

        new_prd_dataset = pandas.DataFrame({
            'new_price_$':[1.4,4.2,3.5,0.7,0.9],
            'new_product_name':['lf milk','white cheese','yellow cheese','pepper red','apples']
        })

        # Store the DataFrames in a dictionary
        dataframes = {'6602a3a74475001648200351': {'df': old_prd_dataset, 'alias': 'old_prd_dataset'},
                    '6602a3a74475001648200352': {'df': new_prd_dataset, 'alias': 'new_prd_dataset'}}

        # Example parameters
        parameters = {
        "code": """

from fuzzywuzzy import fuzz

old_prd_dataset = DataframeInformation.get(alias="old_prd_dataset")
new_prd_dataset = DataframeInformation.get(alias="new_prd_dataset")
new_prd_dataset['merge']='all'
old_prd_dataset['merge']='all'
all_products = pd.merge(new_prd_dataset,old_prd_dataset,on='merge')
del all_products['merge']
products_tuple = all_products[['old_product_name', 'new_product_name']].apply(tuple, axis=1).tolist()
all_products['ratio'] = [fuzz.ratio(*i) for i in products_tuple]
"""
        }

        # Simulating the execution of the parameters and code within the PyTool context
        PyTool().execute(dataframes, parameters, {}, None)
