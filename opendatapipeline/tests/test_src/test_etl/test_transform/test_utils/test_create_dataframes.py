import os
import unittest
import pandas 
import pytest

# from src.etl.transfrom.utils.create_dataframes import CreateDataframeDictionary
from pymongo import ReadPreference
from src.models.connector import MongoConnector
from src.exceptions.exception import *
from pymongo.write_concern import WriteConcern

wc_majority = WriteConcern("majority", wtimeout=1000)
session = MongoConnector().client._Database__client.start_session()

class TestCreateDataframeDictionary(unittest.TestCase):
    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires DataframeDictionary")
    def test_create(self):
        chat_id = "66729ec22ee1491c32b05b53"
        actual_output = session.with_transaction(lambda s:CreateDataframeDictionary(session).create(chat_id),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
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
        expected_output = {'6602a3a74475001648200351':{'df': df1, 'alias': 'customers-100'},
                           '6602a3a74475001648200352':{'df': df2, 'alias': 'industry'}}
        self.assertEqual(expected_output['6602a3a74475001648200351']['df'].values.tolist(), actual_output['6602a3a74475001648200351']['df'].values.tolist())
        self.assertEqual(expected_output['6602a3a74475001648200352']['df'].values.tolist(), actual_output['6602a3a74475001648200352']['df'].values.tolist())
        self.assertEqual(expected_output['6602a3a74475001648200351']['alias'], actual_output['6602a3a74475001648200351']['alias'])
        self.assertEqual(expected_output['6602a3a74475001648200352']['alias'], actual_output['6602a3a74475001648200352']['alias'])

    @pytest.mark.skipif(os.getenv("APP_ENVIRONMENT") == "test", reason="requires DataframeDictionary")
    def test_create_with_non_existing_chat_id(self):
        chat_id = "66729ec22ee1491c32b05b52"
        with pytest.raises(UtilsException) as test_func:
            session.with_transaction(lambda s:CreateDataframeDictionary(session).create(chat_id),
                    write_concern=wc_majority,
                    read_preference=ReadPreference.PRIMARY,)
        self.assertEqual("Failed to create dataframes dictionaries due to Failed to get data by id.", str(test_func.value))
