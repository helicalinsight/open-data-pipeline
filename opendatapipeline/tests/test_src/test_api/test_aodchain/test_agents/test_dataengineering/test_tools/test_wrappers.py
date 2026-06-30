import configparser
import unittest
import json
import pytest
from src.cache.cache_factory import get_cache
from src.cache.cache_base import CacheBase
from unittest.mock import patch, Mock
from src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper import DataEngineeringWrapper
from src.models.connector import MongoConnector
from src.models.mongo.mongo_factory import MongoFactory


class TestToolsAddColumn(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) age_1 with default value 10.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'default': 10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) age_1 with default value 10.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_input_columns_as_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) age_1 with default value 10.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'default': 10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) age_1 with default value 10.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_columns_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'default': 10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'default': 10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "'Failed to update metadata.."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'default': 10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert 'Failed to update metadata..' in result.get('result').get('text'
            )

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_column_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [], 'default': 10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) age_1 with default value None.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'default': ''}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) age_1 with default value None.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) age_1 with default value None.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'default': None}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) age_1 with default value None.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_negative_integer(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) age_1 with default value -10.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'default': -10}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) age_1 with default value -10.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_boolean(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) marks with default value True.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'marks', 'default': True}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) marks with default value True.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_decimal(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) marks with default value 50.6.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'marks', 'default': 50.6}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) marks with default value 50.6.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_negative_decimal(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) marks with default value -50.6.'}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'marks', 'default': -50.6}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) marks with default value -50.6.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_fraction_value(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) average with default value 16.666666666666668.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'average', 'default': 50 / 3}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) average with default value 16.666666666666668.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_scientific(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) scientific_value with default value 12300.0.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'scientific_value', 'default': 12300.0}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) scientific_value with default value 12300.0.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_percentage(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) percent with default value 50%.'}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'percent', 'default': '50%'}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) percent with default value 50%.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_currency(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) currency with default value $50.'}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'currency', 'default': '$50'}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) currency with default value $50.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_phone_number(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) phone with default value 9934565324.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'phone', 'default': 9934565324}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) phone with default value 9934565324.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_add_column_wrapper_with_default_as_date(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully added column(s) date with default value 2024-05-29.'}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'date', 'default': '2024-05-29'}
        add_column_result = wrapper.run('add_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(add_column_result)
        assert result.get('result').get('text'
            ) == 'Successfully added column(s) date with default value 2024-05-29.'


class TestToolsDropColumn(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully dropped column(s) name.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name']}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == 'Successfully dropped column(s) name.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_with_no_existing_columns_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to drop columns."[\'full_name\'] not found in axis"'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['full_name']}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == 'Failed to drop columns."[\'full_name\'] not found in axis"'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_with_empty_string_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['']}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_with_none_in_list_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None]}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_with_none_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_with_incomplete_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': ['name']}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_columns_wrapper_with_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        drop_columns_result = wrapper.run('drop_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."


class TestToolsAggregation(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully performed aggregations'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['new_age'],
            'agg': ['sum'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert 'Successfully performed aggregations' in result.get('result'
            ).get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_as_blank_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to aggregate columns.object of type'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'destination_columns': '', 'agg': '',
            'group_by': ''}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert 'Failed to aggregate columns.object of type' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_as_None(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to aggregate columns.object of type'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'destination_columns': None, 'agg': None,
            'group_by': None}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert 'Failed to aggregate columns.object of type' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_as_None_inside_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to aggregate columns.object of type'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'destination_columns': [None], 'agg': [
            None], 'group_by': [None]}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert 'Failed to aggregate columns.object of type' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_as_empty_string_inside_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to aggregate columns.object of type'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'destination_columns': [], 'agg': [''],
            'group_by': ['']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert 'Failed to aggregate columns.object of type' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_mean(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['new_age'],
            'agg': ['mean'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_mean_without_group_by(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by ''."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['new_age'],
            'agg': ['mean']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by ''." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_max_without_destination_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'agg': ['max'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_min_without_destination_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'agg': ['min'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_median_without_group_by(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by ''."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['age_median'],
            'agg': ['median']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by ''." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_median_with_group_by(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['age_median'],
            'agg': ['median'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_standard_deviation_with_group_by(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['age_median'],
            'agg': ['stddev'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_distinct_with_group_by(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['age_median'],
            'agg': ['distinct'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_for_variance(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed aggregations on 'age' grouped by 'id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['age_median'],
            'agg': ['variance'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Successfully performed aggregations on 'age' grouped by 'id'." == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_with_invalig_agg(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to aggregate columns.'SeriesGroupBy' object has no attribute 'total_sum'"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'destination_columns': ['age_median'],
            'agg': ['total_sum'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert "Failed to aggregate columns.'SeriesGroupBy' object has no attribute 'total_sum'" == result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_aggregations_wrapper_with_non_existing_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to aggregate columns."Column(s) [\'age1\'] do not exist"'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age1'], 'destination_columns': ['age_median'],
            'agg': ['sum'], 'group_by': ['id']}
        aggregation_result = wrapper.run('aggregations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(aggregation_result)
        assert 'Failed to aggregate columns."Column(s) [\'age1\'] do not exist"' == result.get(
            'result').get('text')


class TestToolsLowerCase(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully updated column(s) name to lowercase.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully updated column(s) name to lowercase.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ''}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None]}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None]}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_columns_as_two_empty_strings_in_list(self, MockExecuteService
        ):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', '']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_incorrect_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': ['name']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_with_non_existing_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform lower case.'name_1'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name_1']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform lower case.'name_1'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_for_date_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform lower case.'end_date'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['end_date']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform lower case.'end_date'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_for_integer_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully updated column(s) age to lowercase.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully updated column(s) age to lowercase.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_lower_case_wrapper_for_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform lower case.'end_date'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name', 'end_date']}
        result = wrapper.run('lowercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform lower case.'end_date'"


class TestToolsArithmetic(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.cache_collection = MongoFactory(mongo_client, "cache", session=self.session)
        self.chats = MongoFactory(mongo_client, "chats", session=self.session)
        self.session.start_transaction()
        self.cache: CacheBase = get_cache(session=self.session)

    def tearDown(self):
        self.session.end_session()

    def test_arithmetic_operations_wrapper_without_mock(self):
        user_info = {
            'user_id': "6619156aa5f4c5c1b01e4d07",
            'chat_id': "65cb43f2007a5f38718b9d6a"
        }
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age + 5', 'destination_column': 'Increased_age'}
        status, chat_document = self.chats.get_by_id(user_info["chat_id"])
        cache_item = self.cache.get_item(chat_document["cwf"]["source_id"], user_info["user_id"], user_info['chat_id'])
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        
        updated_cache_item = self.cache.get_item(chat_document["cwf"]["source_id"], user_info["user_id"], user_info['chat_id'])
        self.assertIn('Increased_age', updated_cache_item['metadata']['column_information']['column_names'])
        expected_text = "Arithmetic operation performed on the given query 'age + 5' and stored to 'Increased_age'."
        self.assertTrue(result['result']['success'])
        self.assertEqual(result['result']['text'], expected_text)

    def test_arithmetic_operations_wrapper_without_success(self):
        
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'new_name + 5', 'destination_column': 'new_age'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)

        result = json.loads(result)
        expected_text = "Function failed: Failed to perform arithmetic.name 'new_name' is not defined"
        self.assertFalse(result['result']['success'])
        self.assertEqual(result['result']['text'], expected_text)


    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query 'age + 5' and stored to 'Increased_age'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age + 5', 'destination_column': 'Increased_age'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query 'age + 5' and stored to 'Increased_age'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_destination_column_as_empty_string(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query 'age + 5' and stored to 'new_column_1'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age + 5', 'destination_column': ''}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query 'age + 5' and stored to 'new_column_1'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_destination_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query 'age + 5' and stored to 'new_column_1'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age + 5', 'destination_column': None}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query 'age + 5' and stored to 'new_column_1'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_query_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': '', 'destination_column': ''}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_query_as_None(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': None, 'destination_column': ''}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_unknown_column_in_query(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform arithmetic.name 'marks' is not defined"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'marks + 5', 'destination_column': None}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform arithmetic.name 'marks' is not defined"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_without_column_in_query(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query '3 + 5' and stored to 'new_column_1'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': '3 + 5', 'destination_column': None}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query '3 + 5' and stored to 'new_column_1'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_string_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform arithmetic.unsupported operand type(s) for +: 'object' and '<class 'int'>'"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'name + 5', 'destination_column': None}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform arithmetic.unsupported operand type(s) for +: 'object' and '<class 'int'>'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_without_column_in_query_with_destination_column(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query '3 + 5' and stored to 'addition'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': '3 + 5', 'destination_column': 'addition'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query '3 + 5' and stored to 'addition'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_float(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query 'age + 0.5' and stored to 'Increased_age'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age + 0.5', 'destination_column': 'Increased_age'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query 'age + 0.5' and stored to 'Increased_age'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_two_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query 'age + id' and stored to 'Increased_age'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age + id', 'destination_column': 'Increased_age'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query 'age + id' and stored to 'Increased_age'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_date_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to perform arithmetic.Given date string "5" not likely a datetime'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'join_date + 5', 'destination_column': 'date5'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to perform arithmetic.Given date string "5" not likely a datetime'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_date_and_object_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform arithmetic.name 'end_date' is not defined"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'join_date + end_date', 'destination_column': 'date5'
            }
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform arithmetic.name 'end_date' is not defined"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_date_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to perform arithmetic.cannot add DatetimeArray and DatetimeArray'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'join_date + join_date', 'destination_column':
            'date5'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to perform arithmetic.cannot add DatetimeArray and DatetimeArray'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_string_date_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform arithmetic.name 'end_date' is not defined"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'end_date + 5', 'destination_column': 'date5'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform arithmetic.name 'end_date' is not defined"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_date_column_subtract(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to perform arithmetic.Given date string "5" not likely a datetime'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'join_date - 5', 'destination_column': 'date5'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to perform arithmetic.Given date string "5" not likely a datetime'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_arithmetic_operations_wrapper_with_int_column_subtract(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Arithmetic operation performed on the given query 'age - 2' and stored to 'age1'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'age - 2', 'destination_column': 'age1'}
        result = wrapper.run('arithmetic_operations', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Arithmetic operation performed on the given query 'age - 2' and stored to 'age1'."


class TestToolsCast(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) id to 'string'."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'id', 'new_type': 'string', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) id to 'string'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'new_type': 'string', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'new_type': 'string', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_with_new_type_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_type']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'id', 'new_type': None, 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_type']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_with_new_type_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_type']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'id', 'new_type': '', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['new_type']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_with_unknown_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns."None of [Index([\'school_id\'], dtype=\'object\')] are in the [columns]"'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'school_id', 'new_type': 'string', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns."None of [Index([\'school_id\'], dtype=\'object\')] are in the [columns]"'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_date(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) join_date to 'date'."}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'new_type': 'date', 'old_type':
            'yyyy-mm-dd'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) join_date to 'date'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_timestamp(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) join_date to 'timestamp'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'new_type': 'timestamp',
            'old_type': 'yyyy-mm-dd'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) join_date to 'timestamp'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_date_with_old_type_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) join_date to 'date'."}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'new_type': 'date', 'old_type': None}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) join_date to 'date'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_date_with_string_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            """Failed to cast columns.time data "Alice" doesn't match format "%Y-%m-%d", at position 0. You might want to try:
    - passing `format` if your strings have a consistent format;
    - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format;
    - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this."""
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'name', 'new_type': 'date', 'old_type':
            'yyyy-mm-dd'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == """Failed to cast columns.time data "Alice" doesn't match format "%Y-%m-%d", at position 0. You might want to try:
    - passing `format` if your strings have a consistent format;
    - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format;
    - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this."""

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_date_with_int_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            """Failed to cast columns.time data "25" doesn't match format "%Y-%m-%d", at position 0. You might want to try:
    - passing `format` if your strings have a consistent format;
    - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format;
    - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this."""
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'date', 'old_type': 'yyyy-mm-dd'
            }
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == """Failed to cast columns.time data "25" doesn't match format "%Y-%m-%d", at position 0. You might want to try:
    - passing `format` if your strings have a consistent format;
    - passing `format='ISO8601'` if your strings are all ISO8601 but not necessarily in exactly the same format;
    - passing `format='mixed'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this."""

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_boolean(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns.Cannot map values to boolean: age contains [40, 25, 35, 30]'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'bool', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns.Cannot map values to boolean: age contains [40, 25, 35, 30]'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_float(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) age to 'float'."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'float', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) age to 'float'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_to_integer(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) age to 'integer'."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'integer', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) age to 'integer'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_string_to_float(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns.Unable to parse string "Alice" at position 0'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'name', 'new_type': 'float', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns.Unable to parse string "Alice" at position 0'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_string_to_integer(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns.Unable to parse string "Alice" at position 0'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'name', 'new_type': 'integer', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns.Unable to parse string "Alice" at position 0'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_with_invalid_new_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Please provide the casting type from the below list: ['float', 'integer','bool', 'boolean', 'string', 'date', 'timestamp','object']"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'bigint', 'old_type': ''}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Please provide the casting type from the below list: ['float', 'integer','bool', 'boolean', 'string', 'date', 'timestamp','object']"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_integer_to_float(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) age to 'float'."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'float'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) age to 'float'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_mixed_string_date_values_to_date(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns.Failed to check unix.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'end_date', 'new_type': 'date'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns.Failed to check unix.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_integer_to_object(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) age to 'object'."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'new_type': 'object'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) age to 'object'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_date_to_object(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) join_date to 'object'."}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'new_type': 'object'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) join_date to 'object'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_date_to_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Updated data type of the given column(s) join_date to 'string'."}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'new_type': 'string'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Updated data type of the given column(s) join_date to 'string'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_unix_mixed_date_to_date_type_without_giving_old_type_as_unix(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns.Failed to check unix.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'unix_dates', 'new_type': 'date'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns.Failed to check unix.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_cast_wrapper_unix_mixed_date_to_date_type_with_giving_old_type_as_unix(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to cast columns.Failed to check unix.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'unix_dates', 'new_type': 'date', 'old_type':
            'unix'}
        result = wrapper.run('cast', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to cast columns.Failed to check unix.'


class TestToolsConcat(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with '-' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '-',
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with '-' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'separator': '-', 'destination_column':
            'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [], 'separator': '-', 'destination_column':
            'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'separator': '-', 'destination_column':
            'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'separator': '-', 'destination_column':
            'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None], 'separator': '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'separator': '-', 'destination_column':
            'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', ''], 'separator': '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'separator': '-', 'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_destination_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with '-' to the column 'id_name_concat'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '-',
            'destination_column': None}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with '-' to the column 'id_name_concat'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_destination_column_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with '-' to the column 'id_name_concat'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '-',
            'destination_column': ''}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with '-' to the column 'id_name_concat'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_without_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with '-' to the column 'id_name_concat'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '-'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with '-' to the column 'id_name_concat'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_separator_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': None,
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_separator_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '',
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_without_separator(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'destination_column':
            'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_incorrect_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': [''], 'separators': '-', 'destination_columns':
            'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_separator_as_special_character(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with '#' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '#',
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with '#' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_columns_as_mixed_data_types(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to concat columns.'[123] not in index'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 123], 'separator': '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to concat columns.'[123] not in index'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_missing_columns_and_separator(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_invalid_json_format(self, MockExecuteService):
        with self.assertRaises(json.decoder.JSONDecodeError):
            wrapper = DataEngineeringWrapper(user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a')
            query = (
                '{columns: [id, name], separator: -, destination_column: concatenated_column}'
                )
            result = wrapper.run('concat', query, user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id=
                '65cb43f2007a5f38718b9d6a', session=self.session)
            result = json.loads(result)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_invalid_json_key_types(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], (123): '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with ' ' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_extra_unnecessary_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, name with '-' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'separator': '-',
            'destination_column': 'concatenated_column', 'extra_param':
            'extra_value'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, name with '-' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_large_number_of_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text': False}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        columns = [f'col{i}' for i in range(100)]
        query = {'columns': columns, 'separator': '-', 'destination_column':
            'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text') == False

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_duplicate_column_names(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully concatenated column(s) id, id with '-' to the column 'concatenated_column'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'id'], 'separator': '-',
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Successfully concatenated column(s) id, id with '-' to the column 'concatenated_column'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_all_parameters_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'separator': None, 'destination_column': None
            }
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_mixed_none_and_valid_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', None], 'separator': '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_empty_and_none_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', None], 'separator': '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_nested_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to concat columns.unhashable type: 'list'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', ['nested_name']], 'separator': '-',
            'destination_column': 'concatenated_column'}
        result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to concat columns.unhashable type: 'list'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_special_characters_in_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to concat columns."[\'na@me\'] not in index"'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'na@me'], 'separator': '-',
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Failed to concat columns."[\'na@me\'] not in index"'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_concat_wrapper_with_mixed_case_in_column_names(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to concat columns."None of [Index([\'Id\', \'Name\'], dtype=\'object\')] are in the [columns]"'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['Id', 'Name'], 'separator': '-',
            'destination_column': 'concatenated_column'}
        concat_result = wrapper.run('concat', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Failed to concat columns."None of [Index([\'Id\', \'Name\'], dtype=\'object\')] are in the [columns]"'


class TestToolsCorrelation(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_non_numeric_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to find correlation of columns.could not convert string to float: 'Alice'"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name'], 'destination_column':
            'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to find correlation of columns.could not convert string to float: 'Alice'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_invalid_json_format(self, MockExecuteService):
        with self.assertRaises(json.decoder.JSONDecodeError):
            wrapper = DataEngineeringWrapper(user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a')
            query = (
                '{"columns": ["id", "age", "marks], "destination_column": "correlation_column"}'
                )
            result = wrapper.run('correlation', query, user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id=
                '65cb43f2007a5f38718b9d6a', session=self.session)
            result = json.loads(result)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_duplicate_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, id to correlation_column.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'id'], 'destination_column':
            'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, id to correlation_column.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_non_existing_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to non_existing_column.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column':
            'non_existing_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to non_existing_column.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_empty_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [], 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_invalid_columns_type(self, MockExecuteService):
        with self.assertRaises(TypeError):
            wrapper = DataEngineeringWrapper(user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a')
            query = {'columns': 123, 'destination_column': 'correlation_column'
                }
            result = wrapper.run('correlation', json.dumps(query), user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id=
                '65cb43f2007a5f38718b9d6a', session=self.session)
            result = json.loads(result)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_invalid_destination_column_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column': 123}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_destination_column_same_as_input_columns(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to age_1.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column': 'age'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to age_1.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_missing_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age']}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None], 'destination_column':
            'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_destination_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column': None}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_destination_column_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column': ''}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_without_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age']}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_incorrect_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': [''], 'destination_columns': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to correlation_column.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column':
            'correlation_column'}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to correlation_column.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [], 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None], 'destination_column':
            'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_columns_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', ''], 'destination_column':
            'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_column': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_destination_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column': None}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_destination_column_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age'], 'destination_column': ''}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_without_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age']}
        correlation_result = wrapper.run('correlation', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(correlation_result)
        assert result.get('result').get('text'
            ) == 'Successfully calculated correlation for the column(s) id, age to id_age_correlation.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_correlation_wrapper_with_incorrect_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': [''], 'destination_columns': 'correlation_column'}
        result = wrapper.run('correlation', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."


class TestToolsDateFormat(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_invalid_date_format(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully updated the format of the date for the column(s) join_date to 'yyyy-mm-dd'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'format': 'yyyy-mm-dd'}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Successfully updated the format of the date for the column(s) join_date to 'yyyy-mm-dd'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_invalid_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully updated the format of the date for the column(s) join_date to 'yyyy/mm/dd'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['join_date'], 'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully updated the format of the date for the column(s) join_date to 'yyyy/mm/dd'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_invalid_format_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'format': ['yyyy/mm/dd']}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_columns_not_found(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to format the date.'non_existing_column'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'non_existing_column', 'format': 'yyyy/mm/dd'}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Failed to format the date.'non_existing_column'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to format the date.'leave_date'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['join_date', 'leave_date'], 'format': 'yyyy/mm/dd'
            }
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Failed to format the date.'leave_date'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_without_format_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date'}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully updated the format of the date for the column(s) join_date to 'yyyy/mm/dd'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'format': 'yyyy/mm/dd'}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Successfully updated the format of the date for the column(s) join_date to 'yyyy/mm/dd'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [], 'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'format': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_format_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'format': None}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_format_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date', 'format': ''}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_without_format(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'join_date'}
        date_format_result = wrapper.run('date_format', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(date_format_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['format']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_date_format_wrapper_with_incorrect_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns', 'format']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'formats': 'yyyy/mm/dd'}
        result = wrapper.run('date_format', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns', 'format']."


class TestToolsDeduplicate(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully deduplicated column(s) id and name and age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name', 'age']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == 'Successfully deduplicated column(s) id and name and age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_non_existing_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to deduplicate columns.Index(['non_existing_column'], dtype='object')"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['non_existing_column']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Failed to deduplicate columns.Index(['non_existing_column'], dtype='object')"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_one_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to deduplicate columns.Index(['email'], dtype='object')"}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['email']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Failed to deduplicate columns.Index(['email'], dtype='object')"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_all_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to deduplicate columns.Index(['email'], dtype='object')"}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name', 'age', 'email']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Failed to deduplicate columns.Index(['email'], dtype='object')"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_duplicate_values(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to deduplicate columns.Index(['department'], dtype='object')"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['department']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Failed to deduplicate columns.Index(['department'], dtype='object')"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_empty_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_incorrect_parameter_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': ['name']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully deduplicated column(s) id and name.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name']}
        deduplicate_result = wrapper.run('deduplicate', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(deduplicate_result)
        assert result.get('result').get('text'
            ) == 'Successfully deduplicated column(s) id and name.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ''}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None]}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None]}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['']}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_columns_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', '']}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_with_incorrect_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': ['id', 'name']}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_deduplicate_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        result = wrapper.run('deduplicate', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."


class TestToolsDropAllExcept(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully dropped all column(s) except id and age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'age']}
        drop_all_except_columns_result = wrapper.run('drop_all_except_columns',
            json.dumps(query), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_all_except_columns_result)
        assert result.get('result').get('text'
            ) == 'Successfully dropped all column(s) except id and age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_non_existing_columns_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully dropped all column(s) except id_1 and age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id_1', 'age']}
        drop_all_except_columns_result = wrapper.run('drop_all_except_columns',
            json.dumps(query), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_all_except_columns_result)
        assert result.get('result').get('text'
            ) == 'Successfully dropped all column(s) except id_1 and age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ''}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None]}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_two_nones_in_list(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None]}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_empty_string_in_list(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['']}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_columns_as_two_empty_strings_in_list(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', '']}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_with_incorrect_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': ['id', 'age']}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_all_except_columns_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        result = wrapper.run('drop_all_except_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."


class TestToolsFilter(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully filtered column(s) 'age' based on the given criteria."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': [25, 40]}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Successfully filtered column(s) 'age' based on the given criteria."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_integer(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully filtered column(s) 'age' based on the given criteria."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'equals', 'value': 25}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Successfully filtered column(s) 'age' based on the given criteria."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [], 'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None], 'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': None}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': ''}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': []}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': [None]}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': ['']}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': [None, None]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': ['', '']}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_without_value(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between'}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_value_as_null(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to filter values.name 'Age' is not defined"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'Age', 'expr': 'is_null'}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Failed to filter values.name 'Age' is not defined"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_expr_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': None, 'value': [25, 40]}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_expr_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': '', 'value': [25, 40]}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_without_expr(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'value': [25, 40]}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_incorrect_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns', 'expr']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'age', 'expression': 'in_between', 'values': [25,
            40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns', 'expr']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_non_string_column_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 123, 'expr': 'in_between', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_non_string_expr_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 123, 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['expr']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_non_list_value_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': 'string'}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_non_string_value_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'contains', 'value': 123}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_invalid_expr_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'invalid_expr', 'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_invalid_column_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to filter values.name 'invalid_column' is not defined"}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'invalid_column', 'expr': 'in_between', 'value':
            [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to filter values.name 'invalid_column' is not defined"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_non_existing_column_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to filter values.name 'non_existing_column' is not defined"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'non_existing_column', 'expr': 'in_between',
            'value': [25, 40]}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to filter values.name 'non_existing_column' is not defined"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_invalid_value_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': [
            'invalid_value']}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to filter values.expr must be a string to be evaluated, <class 'NoneType'> given"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_empty_value_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to filter values.Failed to generate query.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'in_between', 'value': []}
        result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to filter values.Failed to generate query.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_incorrect_expr_for_data_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully filtered column(s) 'name' based on the given criteria."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'name', 'expr': 'is_null', 'value': None}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Successfully filtered column(s) 'name' based on the given criteria."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_filter_wrapper_with_empty_value_string_expr(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully filtered column(s) 'age' based on the given criteria."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'expr': 'equals', 'value': ''}
        filter_result = wrapper.run('filter', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(filter_result)
        assert result.get('result').get('text'
            ) == "Successfully filtered column(s) 'age' based on the given criteria."

@pytest.mark.skip()
class TestToolsJoins(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_when_file_not_present(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy', 'customers-100'], 'join_type':
            'inner', 'left_on': ['id'], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': '', 'join_type': 'inner', 'left_on': ['Id'],
            'right_on': ['Id']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': [], 'separator': '-', 'destination_column':
            'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': None, 'separator': '-', 'destination_column':
            'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': [None], 'separator': '-',
            'destination_column': 'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': [None, None], 'separator': '-',
            'destination_column': 'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': [''], 'separator': '-', 'destination_column':
            'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_file_names_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['', ''], 'separator': '-',
            'destination_column': 'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_without_file_names_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation completed with an exception"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'separator': '-', 'destination_column': 'joinsenated_column'}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_join_type_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed joins on files Dummy_Data (1), customers-100 on columns id and id with the type inner."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': None, 'left_on': ['id'], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Successfully performed joins on files Dummy_Data (1), customers-100 on columns id and id with the type inner.' in result.get(
            'result')['text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_join_type_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed joins on files Dummy_Data (1), customers-100 on columns id and id with the type inner."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': '', 'left_on': ['id'], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        self.assertEqual(result['success'], True)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_without_join_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully performed joins on files Dummy_Data (1), customers-100 on columns id and id with the type inner."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'left_on': ['id'], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Successfully performed joins on files Dummy_Data (1), customers-100 on columns id and id with the type inner.' in result.get(
            'result')['text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': None, 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': '', 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': [], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': [None], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': [''], 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': [None, None], 'right_on': ['id']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_left_on_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': ['', ''], 'right_on': ['id']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_without_left_on(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': None, 'left_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': '', 'left_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': [], 'left_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': [None], 'left_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': [''], 'left_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': [None, None], 'left_on': ['id']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_right_on_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'right_on': ['', ''], 'left_on': ['id']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_without_right_on(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100'],
            'join_type': 'inner', 'left_on': ['id']}
        joins_result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(joins_result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_incorrect_parameters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'join_types': 'inner', 'left_ons': ['id'], 'right_ons': [
            'id'], 'file_name': ['Dummy_Data (1)', 'customers-100']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation completed with an exception' in result

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_joins_wrapper_with_incorrect_parameters_1(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'join_types': 'inner', 'left_ons': ['id'], 'right_ons': [
            'id'], 'file_names': ['Dummy_Data (1)', 'customers-100']}
        result = wrapper.run('joins', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception' in result.get('result')[
            'text']


class TestToolsRearrangeColumns(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully rearranged column(s) in the given order 'name, age, id'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name', 'age', 'id']}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully rearranged column(s) in the given order 'name, age, id'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ''}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None]}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None]}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_empty_string_in_list(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['']}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_columns_as_two_empty_strings_in_list(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', '']}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_incorrect_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name'}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rearrange_columns_wrapper_with_non_existing_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to rearrange columns."[\'name_1\'] not in index"'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name_1', 'age', 'id']}
        result = wrapper.run('rearrange_columns', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to rearrange columns."[\'name_1\'] not in index"'


class TestToolsRenameColumns(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rename_columns_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully renamed column(s) name with full_name.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'old_name': 'name', 'new_name': 'full_name'}
        result = wrapper.run('rename_columns', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully renamed column(s) name with full_name.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rename_columns_wrapper_without_newname(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['old_name', 'new_name']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'old_name': 'name'}
        result = wrapper.run('rename_columns', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['old_name', 'new_name']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rename_columns_wrapper_as_blank_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception: Incomplete Parameter Detection. '
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'old_name': '', 'new_name': ''}
        result = wrapper.run('rename_columns', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception: Incomplete Parameter Detection. ' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rename_columns_wrapper_as_None(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception: Incomplete Parameter Detection. '}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'old_name': None, 'new_name': None}
        result = wrapper.run('rename_columns', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception: Incomplete Parameter Detection. ' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rename_columns_wrapper_with_column_name_not_present(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "['given_name'] not found in axis"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'old_name': 'given_name', 'new_name': 'full_name'}
        result = wrapper.run('rename_columns', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert "['given_name'] not found in axis" in result.get('result').get(
            'text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_rename_columns_wrapper_with_already_existing_name(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully renamed column(s) name with name_1.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'old_name': 'name', 'new_name': 'name'}
        result = wrapper.run('rename_columns', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully renamed column(s) name with name_1.'


class TestToolsReplaceSpecialCharacter(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully replaced special characters in column(s) name: a to b.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'a', 'columns': 'name',
            'replacement_character': 'b'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully replaced special characters in column(s) name: a to b.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_as_blank_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': '', 'columns': '',
            'replacement_character': ''}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': None, 'columns': None,
            'replacement_character': None}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_unknown_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to replace special characters.'abc'"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'b', 'columns': 'abc',
            'replacement_character': 'a'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert "Failed to replace special characters.'abc'" in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_empty_target_character(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': '', 'columns': 'name',
            'replacement_character': 'b'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_empty_replacement_character(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully replaced special characters in column(s) name: a to .'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'a', 'columns': 'name',
            'replacement_character': ''}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully replaced special characters in column(s) name: a to .'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_same_target_and_replacement_character(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully replaced special characters in column(s) name: a to a.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'a', 'columns': 'name',
            'replacement_character': 'a'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully replaced special characters in column(s) name: a to a.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_non_string_target_character(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['target_character']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 123, 'columns': 'name',
            'replacement_character': 'b'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['target_character']." in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_non_string_replacement_character(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully replaced special characters in column(s) name: a to .'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'a', 'columns': 'name',
            'replacement_character': 123}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert 'Successfully replaced special characters in column(s) name: a to .' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_empty_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'a', 'columns': '',
            'replacement_character': 'b'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert 'Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters.' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_non_string_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to replace special characters.123'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': 'a', 'columns': 123,
            'replacement_character': 'b'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert 'Failed to replace special characters.123' in result.get(
            'result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to replace special characters.'name, address'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': '-', 'columns': 'name, address',
            'replacement_character': '_'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to replace special characters.'name, address'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_replace_special_character_wrapper_with_special_characters_in_replacement(
        self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to replace special characters.'description'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'target_character': '*', 'columns': 'description',
            'replacement_character': '&'}
        result = wrapper.run('replace_special_characters', json.dumps(query
            ), user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to replace special characters.'description'"


class TestToolsSort(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age'], 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_input_columns_as_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': '', 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_ascending_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'ascending': ''}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_ascending_as_false(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'ascending': False}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_invalid_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to sort columns.'invalid_column'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'invalid_column', 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to sort columns.'invalid_column'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_missing_ascending(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age'}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_empty_query(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age and name.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age', 'name'], 'ascending': [True, False]}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age and name.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_ascending_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'ascending': None}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_invalid_ascending_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'ascending': 'invalid_type'}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_multiple_columns_and_single_ascending(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age and name.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age', 'name'], 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age and name.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_missing_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_unexpected_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully sorted column(s)  age.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age', 'ascending': True, 'unexpected_param':
            'value'}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully sorted column(s)  age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sort_wrapper_with_boolean_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to sort columns.'is_active'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'is_active', 'ascending': True}
        result = wrapper.run('sort', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to sort columns.'is_active'"


class TestToolsSplit(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully splitted column(s) name into firstname, lastname at the delimiter '_'."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': ['firstname', 'lastname'], 'column':
            'name', 'delimiter': '_'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully splitted column(s) name into firstname, lastname at the delimiter '_'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_without_delimiter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully splitted column(s) name into firstname, lastname at the delimiter ' '."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': ['firstname', 'lastname'], 'column':
            'name'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully splitted column(s) name into firstname, lastname at the delimiter ' '."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_destination_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text': True}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': [], 'column': 'name', 'delimiter': '_'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == True

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_destination_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text': True}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': ['', ''], 'column': 'name',
            'delimiter': '_'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == True

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_destination_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text': True}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': [None], 'column': 'name',
            'delimiter': '_'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == True

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_column_and_delimiter_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': ['firstname', 'lastname'], 'column':
            '', 'delimiter': ''}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_column_and_delimiter_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_columns': ['firstname', 'lastname'], 'column':
            None, 'delimiter': None}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_missing_destination_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text': True}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'delimiter': '_'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == True

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_multiple_delimiters(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to split columns.'address'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'address', 'delimiter': ', ',
            'destination_columns': ['street', 'city', 'state', 'zip']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to split columns.'address'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_no_delimiter_and_destination_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to split columns.'full_name'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'full_name'}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to split columns.'full_name'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_special_character_delimiter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to split columns.'tags'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'tags', 'delimiter': '|', 'destination_columns':
            ['tag1', 'tag2', 'tag3']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to split columns.'tags'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_single_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to split columns.'dob'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'dob', 'delimiter': '-', 'destination_columns':
            ['year']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to split columns.'dob'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_incorrect_delimiter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to split columns.'dob'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'dob', 'delimiter': '/', 'destination_columns':
            ['day', 'month', 'year']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to split columns.'dob'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_non_string_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 12345, 'delimiter': '-', 'destination_columns':
            ['part1', 'part2']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_non_string_delimiter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully splitted column(s) name into part1, part2 at the delimiter ' '."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'delimiter': 123, 'destination_columns':
            ['part1', 'part2']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully splitted column(s) name into part1, part2 at the delimiter ' '."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_invalid_destination_columns(self, MockExecuteService):
        with self.assertRaises(TypeError):
            wrapper = DataEngineeringWrapper(user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a')
            query = {'column': 'name', 'delimiter': '_',
                'destination_columns': 'invalid_column_names'}
            result = wrapper.run('split', json.dumps(query), user_id=
                '6619156aa5f4c5c1b01e4d07', chat_id=
                '65cb43f2007a5f38718b9d6a', session=self.session)
            result = json.loads(result)

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_missing_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'delimiter': '-', 'destination_columns': ['part1', 'part2']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_split_wrapper_with_empty_destination_columns_and_delimiter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully splitted column(s) name into first, last at the delimiter ' '."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'delimiter': '', 'destination_columns':
            ['first', 'last']}
        result = wrapper.run('split', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully splitted column(s) name into first, last at the delimiter ' '."


class TestToolsSqlOperations(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sql_operations_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Executed the given query 'SELECT * FROM df' successfully."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'SELECT * FROM df'}
        result = wrapper.run('sql_operations', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Executed the given query 'SELECT * FROM df' successfully."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sql_operations_wrapper_with_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Executed the given query 'SELECT 'age' FROM df' successfully."}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': "SELECT 'age' FROM df"}
        result = wrapper.run('sql_operations', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Executed the given query 'SELECT 'age' FROM df' successfully."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sql_operations_wrapper_with_unknown_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            """Failed to perform sql operations.Binder Error: Referenced column "marks" not found in FROM clause!
Candidate bindings: "df.age\""""
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': 'SELECT marks FROM df'}
        result = wrapper.run('sql_operations', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == """Failed to perform sql operations.Binder Error: Referenced column "marks" not found in FROM clause!
Candidate bindings: "df.age\""""

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sql_operations_wrapper_with_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': None}
        result = wrapper.run('sql_operations', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_sql_operations_wrapper_with_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': ''}
        result = wrapper.run('sql_operations', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."


class TestToolsTrim(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully trimmed column(s) age to '1' character(s) to its right."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'number_of_characters': 1, 'location': 'right', 'columns':
            'age'}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully trimmed column(s) age to '1' character(s) to its right."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'number_of_characters': 1, 'location': 'right', 'columns': ''}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'number_of_characters': 1, 'location': 'right', 'columns':
            None}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper_with_number_of_characters_less_or_equal_to_zero(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'number_of_characters': -1, 'location': 'right', 'columns':
            None}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper_with_location_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully trimmed column(s) age to '1' character(s) to its left."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'number_of_characters': 1, 'location': '', 'columns': 'age'}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully trimmed column(s) age to '1' character(s) to its left."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper_with_only_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully trimmed column(s) age to '1' character(s) to its left."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': 'age'}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully trimmed column(s) age to '1' character(s) to its left."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_trim_wrapper_with_only_columns_as_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Successfully trimmed column(s) age, name to '1' character(s) to its left."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age', 'name']}
        result = wrapper.run('trim', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Successfully trimmed column(s) age, name to '1' character(s) to its left."

@pytest.mark.skip()
class TestToolsUnion(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @pytest.mark.run(order=1)
    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Union performed successfully.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['Dummy_Data (1)', 'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Union performed successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_non_existing_files(self, MockExecuteService):
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['New_Data', 'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result == 'Operation completed with an exception, please make sure you have the files uploaded: list index out of range'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_similar_file_names(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Union performed successfully.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': ['DummyData (1)', 'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Union performed successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_similar_file_names_and_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully performed union based on column(s) id, name, age.'}
            ]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name', 'age'], 'file_names': [
            'DummyData (1)', 'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully performed union based on column(s) id, name, age.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_unknown_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to perform union."[\'Age\'] not in index"'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['id', 'name', 'Age'], 'file_names': [
            'Dummy_Data (1)', 'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Failed to perform union."[\'Age\'] not in index"'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Union performed successfully.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None, 'file_names': ['Dummy_Data (1)',
            'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Union performed successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Union performed successfully.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [''], 'file_names': ['Dummy_Data (1)',
            'customers-100']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Union performed successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_file_names_as_none(self, MockExecuteService):
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': None}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result == "Operation completed with an exception, please make sure you have the files uploaded: 'NoneType' object is not iterable"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_union_wrapper_with_none_in_list_of_filenames(self, MockExecuteService):
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file_names': [None, 'students']}
        result = wrapper.run('union', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result == "Operation completed with an exception, please make sure you have the files uploaded: 'NoneType' object is not iterable"


class TestToolsUpperCase(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully updated column(s) name to uppercase.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully updated column(s) name to uppercase.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ''}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': []}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': None}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None]}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_two_nones_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': [None, None]}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_columns_as_two_empty_strings_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['', '']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_incorrect_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': ['name']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_without_columns_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['columns']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_with_non_existing_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform upper case.'name_1'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name_1']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform upper case.'name_1'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_for_date_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform upper case.'end_date'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['end_date']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform upper case.'end_date'"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_for_integer_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Successfully updated column(s) age to uppercase.'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['age']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Successfully updated column(s) age to uppercase.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_upper_case_wrapper_for_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to perform upper case.'end_date'"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name', 'end_date']}
        result = wrapper.run('uppercase', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to perform upper case.'end_date'"


class TestToolsWhenOtherwise(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_when_otherwise_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'When otherwise query executed and stored in new_column_1 successfully.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query':
            """SELECT *, CASE 
	WHEN name  = 'mya' THEN 'helical'
	WHEN name  = 'vya' THEN 'askdata'
	WHEN name  = 'noj' THEN 'tech'
	ELSE NULL
END AS __newcolumn__
FROM df;"""
            }
        result = wrapper.run('when_otherwise', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'When otherwise query executed and stored in new_column_1 successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_when_otherwise_wrapper_1(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'When otherwise query executed and stored in new_column_1 successfully.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query':
            """SELECT *, CASE
	WHEN name = 'Alice' THEN 'a'
	WHEN 'name' = 'David' THEN 'd'
	ELSE 'e'
END AS __newcolumn__
FROM df;"""
            }
        result = wrapper.run('when_otherwise', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'When otherwise query executed and stored in new_column_1 successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_when_otherwise_wrapper_by_giving_column_name(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'When otherwise query executed and stored in final_output successfully.'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query':
            """SELECT *, CASE
	WHEN name = 'Alice' THEN 'a'
	WHEN 'name' = 'David' THEN 'd'
	ELSE 'e'
END AS final_output
FROM df;"""
            }
        result = wrapper.run('when_otherwise', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'When otherwise query executed and stored in final_output successfully.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_when_otherwise_wrapper_with_unknown_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            """Failed to perform when otherwise.Binder Error: Referenced column "marks" not found in FROM clause!
Candidate bindings: "df.age\""""
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query':
            """SELECT *, CASE
	WHEN marks > 35 THEN '35'
	WHEN marks < 50 THEN '40'
	ELSE 'MODERATE'
END AS __newcolumn__
FROM df;"""
            }
        result = wrapper.run('when_otherwise', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text') == """Failed to perform when otherwise.Binder Error: Referenced column "marks" not found in FROM clause!
Candidate bindings: "df.age\""""

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_when_otherwise_wrapper_if_query_is_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': None}
        result = wrapper.run('when_otherwise', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_when_otherwise_wrapper_if_query_is_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'query': ''}
        result = wrapper.run('when_otherwise', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Operation Completed with Exception: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['query']."


class TestToolsExtract(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Extracted '['year']' from 'join_date' column"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'component': 'year',
            'destination_column': 'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Extracted '['year']' from 'join_date' column"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_with_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': None, 'component': 'year', 'destination_column':
            'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_with_column_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': '', 'component': 'year', 'destination_column':
            'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_without_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'component': 'year', 'destination_column': 'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_with_component_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['component']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'component': None,
            'destination_column': 'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['component']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_with_component_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['component']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'component': '',
            'destination_column': 'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['component']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_without_component(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['component']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'destination_column': 'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['component']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_with_destination_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Extracted '['year']' from 'join_date' column"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'component': 'year',
            'destination_column': None}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Extracted '['year']' from 'join_date' column"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_with_destination_column_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Extracted '['year']' from 'join_date' column"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'component': 'year',
            'destination_column': ''}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Extracted '['year']' from 'join_date' column"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_without_destination_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Extracted '['year']' from 'join_date' column"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'join_date', 'component': 'year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Extracted '['year']' from 'join_date' column"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_extract_wrapper_without_column_component(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column', 'component']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'destination_column': 'joining_year'}
        result = wrapper.run('extract', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == "Failed to extract.Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['column', 'component']."


class TestToolsCurrentWorkingFile(unittest.TestCase):

    def setUp(self):
        self.mongo_connector = MongoConnector()
        self.mongo_client = self.mongo_connector.client
        self.session = self.mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    @pytest.mark.skip("cwf does not call execute service")
    def test_current_working_file_with_matching_alias(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation completed: customers-100 is selected as current working file'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file': 'customers-100'}
        result = wrapper.run('cwf', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Operation completed: customers-100 is selected as current working file'


    @pytest.mark.skip("cwf does not call execute service")
    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_current_working_file_with_matching_alias_with_only_teache(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation completed: customers-100 is selected as current working file'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file': 'customers-'}
        result = wrapper.run('cwf', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Operation completed: customers-100 is selected as current working file'
        mongo_chats = MongoFactory(self.mongo_client, 'chats', self.session)
        status_msg, chat = mongo_chats.get_by_id('65cb43f2007a5f38718b9d6a')
        assert chat['cwf'] == {'source_id': '662bb3d788e28e8af8679eb7'}

    @pytest.mark.skip("cwf does not call execute service")
    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_current_working_file_with_matching_alias_with_only_teac(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Operation completed with exception: custm does not match any file name'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'file': 'custm'}
        result = wrapper.run('cwf', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(result)
        assert result.get('result').get('text'
            ) == 'Operation completed with exception: custm does not match any file name'


class TestToolsDropNa(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': ['name']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_empty_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': []}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_empty_string_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': ['']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_none_in_list(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': [None]}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_multiple_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to drop na.['weight']"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': ['age', 'weight']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert "Failed to drop na.['weight']" in result.get('result').get(
            'text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_non_existing_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to drop na.['non_existing_column']"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': ['non_existing_column']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == "Failed to drop na.['non_existing_column']"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_all_columns(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to drop na.['email']"
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': ['name', 'age', 'email']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert "Failed to drop na.['email']" in result.get('result').get('text'
            )

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_no_subset(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_incorrect_parameter_type(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for None columns'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'columns': ['name']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == 'Dropped NaN values for None columns'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_empty_subset(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'subset': []}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_with_incorrect_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for None columns'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'sub': ['name']}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert result.get('result').get('text'
            ) == 'Dropped NaN values for None columns'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_drop_na_wrapper_without_subset_parameter(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Dropped NaN values for'
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        drop_columns_result = wrapper.run('drop_na', json.dumps(query),
            user_id='6619156aa5f4c5c1b01e4d07', chat_id=
            '65cb43f2007a5f38718b9d6a', session=self.session)
        result = json.loads(drop_columns_result)
        assert 'Dropped NaN values for' in result.get('result').get('text')


class TestToolsFillNa(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Filled NaN values with 'Fail' value"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'value': 'Fail'}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Filled NaN values with 'Fail' value"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_and_axis(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Filled NaN values with 'Unknown' along the columns"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'value': 'Unknown', 'axis': 'columns'}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Filled NaN values with 'Unknown' along the columns"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_and_with_axis_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Filled NaN values with 'Unknown' value"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'value': 'Unknown', 'axis': ''}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Filled NaN values with 'Unknown' value"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_and_with_axis_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Filled NaN values with 'Unknown' value"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'value': 'Unknown', 'axis': ''}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Filled NaN values with 'Unknown' value"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_and_column(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to update metadata..'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'value': 'No name'}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Failed to update metadata..'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_and_with_column_as_None(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Filled NaN values with 'No name' value"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': None, 'value': 'No name'}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Filled NaN values with 'No name' value"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_and_with_column_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Filled NaN values with 'No name' value"}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': '', 'value': 'No name'}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Filled NaN values with 'No name' value"

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_method(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Filled NaN values using bfill method'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'method': 'bfill'}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Filled NaN values using bfill method'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_method_column_and_limit(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to update metadata..'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'method': 'ffill', 'limit': 1}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Failed to update metadata..'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_method_column_and_with_limit_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Failed to update metadata..'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'method': 'ffill', 'limit': None}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Failed to update metadata..'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_method_limit_and_with_column_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'Filled NaN values using ffill method with limit 1'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': None, 'method': 'ffill', 'limit': 1}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == 'Filled NaN values using ffill method with limit 1'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_limit_column_and_with_method_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'column': 'name', 'method': None, 'limit': 1}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_as_None(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'value': None}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_value_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'value': ''}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_method_as_None(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'method': None}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_with_method_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'method': ''}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_fill_na_wrapper_without_value_and_method(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."
            }]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        concat_result = wrapper.run('fill_na', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(concat_result)
        assert result.get('result').get('text'
            ) == "Error: Incomplete Parameter Detection. Unable to detect all parameters. Please ensure that all required parameters are provided. The following parameter(s) are not detected: ['value' or 'method']."


class TestToolsWrappers(unittest.TestCase):

    def setUp(self):
        mongo_connector = MongoConnector()
        mongo_client = mongo_connector.client
        self.session = mongo_client._Database__client.start_session()
        self.session.start_transaction()

    def tearDown(self):
        self.session.end_session()

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_wrapper_with_unknown_mode(self, MockExecuteService):
        wrapper = DataEngineeringWrapper(user_id='65365001d9654d9ec1172f87',
            chat_id='65d9e5f71dee0028fca0055c')
        query = {'columns': ['name']}
        result = wrapper.run('upper_case', json.dumps(query), user_id=
            '65365001d9654d9ec1172f87', chat_id='65d9e5f71dee0028fca0055c',
            session=self.session)
        result = json.loads(result)
        assert result == 'ModeError: Got unexpected mode upper_case.'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_export_wrapper(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'File Ready To Download'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'export_name': 'test.csv'}
        export_result = wrapper.run('export', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(export_result)
        assert result.get('result').get('text') == 'File Ready To Download'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_export_wrapper_with_export_name_as_empty_string(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'File Ready To Download'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'export_name': ''}
        export_result = wrapper.run('export', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(export_result)
        assert result.get('result').get('text') == 'File Ready To Download'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_export_wrapper_with_export_name_as_none(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'File Ready To Download'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'export_name': None}
        export_result = wrapper.run('export', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(export_result)
        assert result.get('result').get('text') == 'File Ready To Download'

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_export_wrapper_without_cwf(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            "Failed to execute the operation ' execute_export'."}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {'export_name': 'test.csv'}
        export_result = wrapper.run('export', json.dumps(query), user_id=
            '65365001d9654d9ec1172f87', chat_id='65cb43f2007a5f38718b9d6e',
            session=self.session)
        result = json.loads(export_result)
        assert result.get('result').get('text'
            ) == "Failed to execute the operation ' execute_export'."

    @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
    def test_export_wrapper_without_export_name(self, MockExecuteService):
        mock_execute_service_instance = MockExecuteService.return_value
        mock_execute_service_instance.execute.return_value = [{'text':
            'File Ready To Download'}]
        wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
            chat_id='65cb43f2007a5f38718b9d6a')
        query = {}
        export_result = wrapper.run('export', json.dumps(query), user_id=
            '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
            session=self.session)
        result = json.loads(export_result)
        assert result.get('result').get('text') == 'File Ready To Download'


# class TestToolsPyTool(unittest.TestCase):

#     def setUp(self):
#         mongo_connector = MongoConnector()
#         mongo_client = mongo_connector.client
#         self.session = mongo_client._Database__client.start_session()
#         self.session.start_transaction()

#     def tearDown(self):
#         self.session.end_session()

#     @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
#     def test_pytool_wrapper_with_import_statements(self, MockExecuteService):
#         wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
#             chat_id='65cb43f2007a5f38718b9d6a')
#         query = {'code':
#             """ <code>
# import pandas as pd
# def sample(a):
#     df=pd.DataFrame()
#     print("empty Dataframe",df)	
#     print("sampleWord",a)
# sample("utkarsh") </code>"""
#             }
#         result = wrapper.pytool(json.dumps(query), user_id=
#             '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
#             session=self.session)
#         self.assertFalse(result.get('result').get('success'))

#     @patch('src.api.services.langchain_service.odpgraph.odpchain.agents.dataengineering.tools.wrapper.ExecuteService')
#     def test_pytool_wrapper(self, MockExecuteService):
#         wrapper = DataEngineeringWrapper(user_id='6619156aa5f4c5c1b01e4d07',
#             chat_id='65cb43f2007a5f38718b9d6a')
#         query = {'code':
#             """ <code> print('hello world !!')
# a = 5
# b = 10
# print(f"The sum of a and b is {a + b}")
# print(DataframeInformation) </code>"""
#             }
#         result = wrapper.pytool(json.dumps(query), user_id=
#             '6619156aa5f4c5c1b01e4d07', chat_id='65cb43f2007a5f38718b9d6a',
#             session=self.session)
#         self.assertFalse(result.get('result').get('success'))
