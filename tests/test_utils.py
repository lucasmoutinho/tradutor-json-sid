import pytest
from parameterized import parameterized
from mock import patch

import os

from app.lib.utils import load_json, \
                          validateDatagridStructure, \
                          loadConfFromEnv, \
                          checkConf

import logging
logger = logging.getLogger('test')


# Testing utils.load_json
class Test_load_json():

    def define_test_data():
        test_params = []

        test_params.append([
            'num',
            1,
            None,
            False,
            'Provided data cannot be processed via json.loads()'
        ])
        test_params.append([
            'simple_str',
            'some_data',
            None,
            False,
            'Provided data cannot be processed via json.loads()'
        ])
        test_params.append([
            'simple_str_number',
            '1',
            None,
            False,
            'Provided data cannot be transformed to dict/list'
        ])
        test_params.append([
            'str_wrong_dict',
            '{"key": "value"',
            None,
            False,
            'Provided data cannot be processed via json.loads()'
        ])
        test_params.append([
            'success',
            '{"key": "value"}',
            {'key': 'value'},
            True,
            None
        ])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(self, name, jsonInput, exp_jsonObject, exp_status, exp_errorMsg):

        jsonObject, status, errorMsg = load_json(jsonInput)

        assert jsonObject == exp_jsonObject
        assert status == exp_status
        assert errorMsg == exp_errorMsg


# Testing utils.validateDatagridStructure
class Test_validateDatagridStructure():

    def define_test_data():
        test_params = []

        test_params.append([
            'not_list',
            {'metadata': [{'name': 'key', 'type': 'decimal'}], 'data': [[1], [2]]},
            False,
            'Not list'
        ])
        test_params.append([
            'no_elements',
            [],
            False,
            'Must be 1 or 2 elements in list'
        ])
        test_params.append([
            'elements_are_not_dicts',
            ['metadata', 'data'],
            False,
            'Each element should be dict'
        ])
        test_params.append([
            'first_not_metadata_dict',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}], 'data': [[1], [2]]}],
            False,
            'First element must contain only metadata dict'
        ])
        test_params.append([
            'metadata_not_list',
            [{'metadata': {'name': 'key', 'type': 'decimal'}}],
            False,
            'Metadata should be list'
        ])
        test_params.append([
            'no_columns',
            [{'metadata': []}],
            False,
            'No columns in metadata'
        ])
        test_params.append([
            'not_dict_in_metadata',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}, 'smth_else']}],
            False,
            'One of elements in metadata is not dict'
        ])
        test_params.append([
            'second_not_data_dict',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}]}, {'data': [[1], [2]], 'another_key': 'smth_else'}],
            False,
            'Second element must contain only data dict'
        ])
        test_params.append([
            'data_not_list',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}]}, {'data': 'smth_else'}],
            False,
            'Data should be list'
        ])
        test_params.append([
            'not_list_in_data',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}]}, {'data': ['smth_else']}],
            False,
            'One of elements in data is not list'
        ])
        test_params.append([
            'column_count_not_match',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}]}, {'data': [[1], [2, 3]]}],
            False,
            'Number of elements in data does not match to metadata'
        ])
        test_params.append([
            'success',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}]}, {'data': [[1], [2]]}],
            True,
            None
        ])
        test_params.append([
            'success_no_data',
            [{'metadata': [{'name': 'key', 'type': 'decimal'}]}],
            True,
            None
        ])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(self, name, datagrid, exp_status, exp_errorMsg):

        status, errorMsg = validateDatagridStructure(datagrid)

        assert status == exp_status
        assert errorMsg == exp_errorMsg


# Testing utils.loadConfFromEnv
# Mock environment variables
class Test_loadConfFromEnv():
    @classmethod
    def setup_class(cls):
        cls._environ = dict(os.environ)

    @classmethod
    def teardown_class(cls):
        os.environ.clear()
        os.environ.update(cls._environ)

    def define_test_data():
        test_params = []
        test_params.append([
            'all_env',
            {
                'baseUrl': 'http://your-viya-instance.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'userId': 'dummy',
                'SASPASS': 'pwd',
                'callDecisionTimeoutConnect': '10',
                'callDecisionTimeoutRead': '10',
                'getAccessTokenTimeoutConnect': '10',
                'getAccessTokenTimeoutRead': '10',
                'dfltModules': 'rootPath:moduleID'
            },
            {
                'baseUrl': 'http://your-viya-instance.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'username': 'dummy',
                'password': 'pwd',
                'callDecisionTimeout': (10, 10),
                'getAccessTokenTimeout': (10, 10)
            },
            {'rootPath': 'moduleID'}
        ])
        test_params.append([
            'two_rootPath',
            {
                'baseUrl': 'http://your-viya-instance.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'userId': 'dummy',
                'SASPASS': 'pwd',
                'callDecisionTimeoutConnect': '10',
                'callDecisionTimeoutRead': '10',
                'getAccessTokenTimeoutConnect': '10',
                'getAccessTokenTimeoutRead': '10',
                'dfltModules': 'rootPath:moduleID,rootPath2:moduleID'
            },
            {
                'baseUrl': 'http://your-viya-instance.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'username': 'dummy',
                'password': 'pwd',
                'callDecisionTimeout': (10, 10),
                'getAccessTokenTimeout': (10, 10)
            },
            {'rootPath': 'moduleID', 'rootPath2': 'moduleID'}
        ])
        test_params.append([
            'no_timeout',
            {
                'baseUrl': 'http://your-viya-instance2.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'userId': 'dummy',
                'SASPASS': 'pwd',
                'dfltModules': 'rootPath:moduleID'
            },
            {
                'baseUrl': 'http://your-viya-instance2.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'username': 'dummy',
                'password': 'pwd',
                'callDecisionTimeout': (None, None),
                'getAccessTokenTimeout': (None, None)
            },
            {'rootPath': 'moduleID'}
        ])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(self, name, environ, exp_massrvconf, exp_dfltModules):
        os.environ.clear()
        mock_environ_patcher = patch.dict(
            'src.jde.app.lib.utils.os.environ', environ)
        mock_environ_patcher.start()

        massrvconf, dfltModules = loadConfFromEnv()

        mock_environ_patcher.stop()

        assert massrvconf == exp_massrvconf
        assert dfltModules == exp_dfltModules


# Testing utils.checkConf
class Test_checkConf():

    # Prepare list of testcases
    def define_test_data():
        from tests.data.test_utils.cases_checkConf import testcases

        test_params = []
        for tc in testcases:
            test_params.append([tc['name'], tc['cfgs'], 
                                tc['dfltModules'], tc['exp_confIsOK']])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(self, name, cfgs, dfltModules, exp_confIsOK):
        logger.debug(f'Test_checkConf - {name}')
        confIsOK = checkConf(cfgs, dfltModules)
        assert confIsOK == exp_confIsOK
