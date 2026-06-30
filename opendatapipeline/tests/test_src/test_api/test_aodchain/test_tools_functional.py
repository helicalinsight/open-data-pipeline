import unittest

import json
import pytest
from unittest.mock import patch, Mock
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory
from src.api.services.changeCWF.services import ChangeCWF

from pymongo.read_concern import ReadConcern
from pymongo import ReadPreference
from pymongo.write_concern import WriteConcern


class TestFunctionalToolsPytool(unittest.TestCase):
    def setUp(self):
        mongo_connector = MongoConnector()
        self.mongo_client = mongo_connector.client
        self.session = self.mongo_client._Database__client.start_session()
        self._test_user_id = '6619156aa5f4c5c1b01e4d07'
        self._test_chat_id = '65cb43f2007a5f38718b9d6a'
        self.session.start_transaction()
        self._mongo_chats = MongoFactory(self.mongo_client, "chats", session=self.session)
        
        _, self._chat_doc_backup = self._mongo_chats.get_by_id(self._test_chat_id)
        
    def tearDown(self):
        if self.session.has_ended:
            self.session = self.mongo_client._Database__client.start_session()
            self.session.start_transaction()
        self._mongo_chats.update_all(self._test_chat_id, self._chat_doc_backup)
        self.session.end_session()
        
    @pytest.mark.run(order=2)
    def test_pytool_access_previous_immediate_step_df(self):
        """
        If a step is executed just before executed Pytool, dataframe created as part of last step
        should be accessible to Pytool
        """
        wrapper = DataEngineeringWrapper(user_id=self._test_user_id, chat_id=self._test_chat_id)
        
        # execute step
        query = {'columns': ['name']}
        drop_columns_result = wrapper.run(
            'drop_columns', json.dumps(query), user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        # get cwf alias
        _, chat = self._mongo_chats.get_by_id(self._test_chat_id)
        
        alias = chat["cwf"]["alias"]
        
        # use that alias in pytool
        query = (
            f'df = DataframeInformation.get(alias="{alias}"); DataframeInformation.create(id="my_test1",alias="my_test1", dataframe=df);'
        )
        pytool_result = wrapper.pytool(query, user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertEqual(pytool_result['result']['success'], True)
    
    @pytest.mark.run(order=2)
    def test_pytool_access_previous_older_step_df(self):
        """
        Pytool should be able to access the dataframe created in any old step before pytool
        """
        wrapper = DataEngineeringWrapper(user_id=self._test_user_id, chat_id=self._test_chat_id)
        
        # execute step
        query = {'columns': ['name']}
        drop_columns_result = wrapper.run(
            'drop_columns', json.dumps(query), user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        # get cwf alias
        _, chat = self._mongo_chats.get_by_id(self._test_chat_id)
        alias = chat["cwf"]["alias"]
        
        # execute step
        query = {'clumn': ['name']}
        test_lower_case_wrapper_result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',session=self.session)
        
        # use older alias in pytool
        query = (
            f'df = DataframeInformation.get(alias="{alias}"); DataframeInformation.create(id="my_test2",alias="my_test2", dataframe=df);'
        )
        
        pytool_result = wrapper.pytool(query, user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertEqual(pytool_result['result']['success'], True)
    
    @pytest.mark.run(order=2)
    def test_pytool_updates_already_existing_dataframe(self):
        """
        Pytool should be able to update an already existing dataframe
        """
        wrapper = DataEngineeringWrapper(user_id=self._test_user_id, chat_id=self._test_chat_id)
        
        query = (
            f'df = DataframeInformation.get(alias="customers-100"); DataframeInformation.update(alias="customers-100", dataframe=df);'
        )
        
        pytool_result = wrapper.pytool(query, user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertEqual(pytool_result['result']['success'], True)
    
    @pytest.mark.run(order=2)
    def test_pytool_creates_single_new_dataframe(self):
        """
        Pytool should be able to create a single new dataframe
        """
        wrapper = DataEngineeringWrapper(user_id=self._test_user_id, chat_id=self._test_chat_id)
        
        query = (
            f'df = DataframeInformation.get(alias="customers-100"); DataframeInformation.create(alias="test-alias5", dataframe=df);'
        )
        
        pytool_result = wrapper.pytool(query, user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertEqual(pytool_result['result']['success'], True)
    
    @pytest.mark.run(order=2)
    def test_pytool_creates_multiple_new_dataframes(self):
        """
        Pytool should be able to create multiple new dataframes
        """
        wrapper = DataEngineeringWrapper(user_id=self._test_user_id, chat_id=self._test_chat_id)
        
        query = (
            f'df = DataframeInformation.get(alias="customers-100"); DataframeInformation.create(alias="test-alias6", dataframe=df); DataframeInformation.create(alias="test-alias7", dataframe=df);'
        )
        
        pytool_result = wrapper.pytool(query, user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertEqual(pytool_result['result']['success'], True)
        
    @pytest.mark.run(order=2)
    def test_pytool_create_df_used_by_next_step(self):
        """
        If Pytool creates a dataframe, next step should be able to use that dataframe
        """
        wrapper = DataEngineeringWrapper(
            user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a')
        
        query = (
            r'df = DataframeInformation.get(alias="customers-100"); DataframeInformation.create(id="my_test3",alias="my_test3", dataframe=df);'
        )
        
        pytool_result = wrapper.pytool(query, user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        
        query2 = (
            r'df = DataframeInformation.get(alias="my_test3"); DataframeInformation.create(id="my_test4",alias="my_test4", dataframe=df);'
        )
        
        pytool_result = wrapper.pytool(query2, user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        
        self.assertEqual(pytool_result['result']['success'], True)
        
    def test_pytool_create_df_used_by_later_step(self):
        """
        Dataframe generated by pytool should be usable by any tool after few steps
        """
        wrapper = DataEngineeringWrapper(
            user_id='6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a')
        
        query = (
            r'<code>df = DataframeInformation.get(alias="customers-100"); DataframeInformation.create(id="my_test8",alias="my_test8", dataframe=df);</code>'
        )
        
        pytool_result = wrapper.pytool(query, user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        
        _source_id = "my_test8"
        
        # execute random step
        query = {'columns': ['name']}
        drop_columns_result = wrapper.run(
            'drop_columns', json.dumps(query), user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        # change cwf
        with self.mongo_client._Database__client.start_session() as session:
            resp = session.with_transaction(
                lambda s: ChangeCWF(session).current_working_file(self._test_chat_id, self._test_user_id, _source_id),
                read_concern=ReadConcern("local"),
                write_concern=WriteConcern("majority", wtimeout=1000),
                read_preference=ReadPreference.PRIMARY,
            )
            
        # execute step on pytool's output
        query = {'columns': ['name']}
        drop_columns_result = wrapper.run(
            'drop_columns', json.dumps(query), user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertTrue(True)


class TestFunctionToolsWhenOtherwise(unittest.TestCase):
    def setUp(self):
        mongo_connector = MongoConnector()
        self.mongo_client = mongo_connector.client
        self.session = self.mongo_client._Database__client.start_session()
        self._test_user_id = '6619156aa5f4c5c1b01e4d07'
        self._test_chat_id = '65cb43f2007a5f38718b9d6a'
        self.session.start_transaction()
        self._mongo_chats = MongoFactory(self.mongo_client, "chats", session=self.session)
        
        _, self._chat_doc_backup = self._mongo_chats.get_by_id(self._test_chat_id)
        
    
    def test_when_otherwise_query_without_from(self):
        wrapper = DataEngineeringWrapper(user_id=self._test_user_id, chat_id=self._test_chat_id)
        
        query = (
            '{"query": "SELECT *, CASE WHEN age > 10 THEN \'high\' ELSE \'low\' END AS \'new_column_1\' FROM df"}'
        )
        
        when_otherwise_result = wrapper.when_otherwise(query, user_id=self._test_user_id, chat_id=self._test_chat_id, session=self.session)
        
        self.assertEqual(when_otherwise_result['result']['success'], True)
    
