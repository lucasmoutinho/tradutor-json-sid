import pytest
from parameterized import parameterized
# import sys

import os

import json
import copy

from app.lib.jsonfunc import dgFromJSON, getElementByPath, \
    mergeData, sortReqEntries

import logging
logger = logging.getLogger('test')


class Test_dgFromJSON():

    # Prepare list of testcases
    # testcase name, input data, config, expected
    # input data is the same for all testcases, but can be easily modified
    def define_test_data():
        with open('./tests/data/test_jsonfunc/dgFromJSON_data/input_data.json', 'r') as f:
            jsonInput = json.loads(f.read())

        from tests.data.test_jsonfunc.dgFromJSON_data.jsonfunc_dgFromJSON_cases \
            import testcases

        test_params = []
        for tc in testcases:
            test_params.append([tc['name'], jsonInput, tc['INconfigs'], tc['expected']])

        return test_params

    @parameterized.expand(define_test_data())
    def test(self, name, jsonInput, INconfigs, expected):
        logger.debug(f'Test_dgFromJSON - {name}')

        # Copy input to check for mutation
        jsonInput_backup = copy.deepcopy(jsonInput)

        dataForSAS = dgFromJSON(jsonInput, INconfigs)

        assert dataForSAS == expected
        # Check if not mutated
        assert jsonInput == jsonInput_backup


class Test_getElementByPath():

    # Only list can be in the input
    def test_only_list_as_input(self):

        expected = []

        # Dict
        jsonInput = {}
        elementList = getElementByPath('some_path', jsonInput)
        assert elementList == expected

        # None
        jsonInput = None
        elementList = getElementByPath('some_path', jsonInput)
        assert elementList == expected

        # String
        jsonInput = 'some_string'
        elementList = getElementByPath('some_path', jsonInput)
        assert elementList == expected

    # Path should be provided
    def test_no_path(self):

        jsonInput = [
            {
                "some_path": {"key": 1, "value": "ABC"}
            }
        ]
        expected = []

        elementList = getElementByPath(None, jsonInput)
        assert elementList == expected

    # Prepare list of testcases
    # testcase name, input data, expected
    def define_test_data():
        from tests.data.test_jsonfunc.getElementByPath_data.jsonfunc_getElementByPath_cases \
            import testcases

        test_params = []
        for tc in testcases:
            test_params.append([tc['name'], tc['jsonInput'], tc['expected']])

        return test_params

    @parameterized.expand(define_test_data())
    def test(self, name, jsonInput, expected):

        elementList = getElementByPath('some_path', jsonInput)

        # Check for value
        assert elementList == expected
        # Check if referenced
        if isinstance(jsonInput[0], dict):
            assert id(elementList[0]) == id(jsonInput[0]['some_path'])
        elif isinstance(jsonInput[0], list):
            assert id(elementList[0]) == id(jsonInput[0][0]['some_path'])


class Test_mergeData():

    # Prepare list of testcases
    # Contain only names, that are used as test case name and directory name
    def define_test_data():

        # name is used to get config and json files within test case

        from tests.data.test_jsonfunc.mergeData_data.jsonfunc_mergeData_cases \
            import testcases

        test_params = []
        for tc in testcases:
            test_params.append([tc['name'], tc['status'], tc['errorMsg']])

        return test_params

    @parameterized.expand(define_test_data())
    def test(self, name, exp_status, exp_errorMsg):

        # print(name)
        logger.debug(f'Test_mergeData - {name}')

        # Import config
        importlib = __import__('importlib')
        basePath = 'tests.data.test_jsonfunc.mergeData_data'
        cfgs = importlib.import_module(f'{basePath}.{name}.config')

        # Read files
        with open(f'./tests/data/test_jsonfunc/mergeData_data/{name}/baseResponse.json', 'r') as f:
            baseResponse = json.loads(f.read())
        with open(f'./tests/data/test_jsonfunc/mergeData_data/{name}/SASResponse.json', 'r') as f:
            SASResponse = json.loads(f.read())

        if exp_status:
            with open(f'./tests/data/test_jsonfunc/mergeData_data/{name}/expected.json', 'r') as f:
                expected = json.loads(f.read())
        else:
            expected = None

        finalResponse, status, errorMsg = mergeData(
            SASResponse,
            baseResponse,
            cfgs.OUTconfigs
        )

        # print(json.dumps(finalResponse, indent=4))

        assert finalResponse == expected
        assert status == exp_status
        assert errorMsg == exp_errorMsg


class Test_sortReqEntries():

    # Prepare list of testcases
    # Contain only names, that are used as test case name and directory name
    def define_test_data():

        test_params = []
        
        # no_sort
        origRequest = [
            {'sortAttr': 'C'},
            {'sortAttr': 'A'},
            {'sortAttr': 'B'}
        ]
        sortSettings = {}
        expected = [
            {'sortAttr': 'C'},
            {'sortAttr': 'A'},
            {'sortAttr': 'B'}
        ]
        exp_status = True
        exp_errorMsg = None
        test_params.append([
            'no_sort',
            origRequest, sortSettings,
            expected, exp_status, exp_errorMsg
        ])
        
        # sort_asc_nofmt
        origRequest = [
            {'sortAttr': 'C'},
            {'sortAttr': 'A'},
            {'sortAttr': 'B'}
        ]
        sortSettings = {
            'sortAttr': 'sortAttr'
        }
        expected = [
            {'sortAttr': 'A'},
            {'sortAttr': 'B'},
            {'sortAttr': 'C'}
        ]
        exp_status = True
        exp_errorMsg = None
        test_params.append([
            'sort_asc_nofmt',
            origRequest, sortSettings,
            expected, exp_status, exp_errorMsg
        ])
        
        # sort_desc_withfmt
        origRequest = [
            {'sortAttr': '1990-03-26'},
            {'sortAttr': '2010-02-10'},
            {'sortAttr': '1991-11-16'}
        ]
        sortSettings = {
            'sortAttr': 'sortAttr',
            'datefmt': '%Y-%m-%d',
            'direction': 'desc'
        }
        expected = [
            {'sortAttr': '2010-02-10'},
            {'sortAttr': '1991-11-16'},
            {'sortAttr': '1990-03-26'}
        ]
        exp_status = True
        exp_errorMsg = None
        test_params.append([
            'sort_desc_withfmt',
            origRequest, sortSettings,
            expected, exp_status, exp_errorMsg
        ])
        
        # error
        origRequest = [
            {'sortAttr': 'not date'},
            {'sortAttr': '2010-02-10'},
            {'sortAttr': '1991-11-16'}
        ]
        sortSettings = {
            'sortAttr': 'sortAttr',
            'datefmt': '%Y-%m-%d',
            'direction': 'desc'
        }
        expected = None
        exp_status = False
        exp_errorMsg = 'Error occurred while sorting'
        test_params.append([
            'error',
            origRequest, sortSettings,
            expected, exp_status, exp_errorMsg
        ])

        return test_params

    @parameterized.expand(define_test_data())
    def test(
        self,
        name,
        origRequest,
        sortSettings,
        expected,
        exp_status,
        exp_errorMsg
    ):

        logger.debug(f'Test_sortReqEntries - {name}')
        sortedDicts, status, errorMsg = sortReqEntries(origRequest,
                                                       sortSettings)

        assert sortedDicts == expected
        assert status == exp_status
        assert errorMsg == exp_errorMsg
