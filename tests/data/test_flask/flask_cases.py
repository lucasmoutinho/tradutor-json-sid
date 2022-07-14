import copy
import pyjq
from tests.data.default_appconf import cfgs as base_cfgs, correct_dfltModules

testcases = []

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# Successful call, code from SAS
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}
expected = '{"in_param_001": "smth", "sas_param_001": 0}'
testcases.append({
    'name': 'success_SASResponse_code',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 201,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

cfgs['test-root-path']['useSASResponseCode'] = False

# Successful call, default response code
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}
expected = '{"in_param_001": "smth", "sas_param_001": 0}'
testcases.append({
    'name': 'success_default_code',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 200,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# Header "Content-Type" must be application/json
SASResponse = None

expected = '''{
    "errors": [
        {
            "code": "CONTENT_TYPE_INVALID",
            "status": 415,
            "message": "\\"Content-Type\\" must be \\"application/json\\"",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'content_type',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': 'some_data',
    'headers': {'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 415,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# Invalid input data
SASResponse = None

expected = '''{
    "errors": [
        {
            "code": "REQUEST_BODY_INVALID",
            "status": 415,
            "message": "Request body is not JSON",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'invalid_input_data',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': 'some_data',
    'headers': {'Content-Type': 'application/json','Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 415,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# callDecision_fail_ue_SASResponse_code
SASResponse = {'code': 401, 'body': None}

expected = '''{
    "errors": [
        {
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "message": "Internal server error occurred",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'callDecision_fail_ue_SASResponse_code',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, False, 'some error'),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[..]'
)
cfgs['test-root-path']['useSASResponseCode'] = False


# constructOutput_fail_ue
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}

expected = '''{
    "errors": [
        {
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "message": "Internal server error occurred",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'constructOutput_fail_ue',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# ----------------------------------------------------------
# 'initFails': True
# Missing must-have params in config
testcases.append({
    'name': 'initFails_no_params',
    'cfgs': {},
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': None,
    'headers': None,
    'mock_callDecision_return': None,
    'exp_status_code': None,
    'exp_json': None,
    'expected': None,
    'initFails': True
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# ----------------------------------------------------------
# multiple config
# Explicit moduleID
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}
expected = '{"in_param_001": "smth", "sas_param_001": 0}'
testcases.append({
    'name': 'multi_explicit_moduleID',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {
        'Content-Type': 'application/json', 
        'Module-ID': 'moduleID2', 
        'Trace-Id': 'testId'
        },
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 201,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# no default moduleID
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}

expected = '''{
    "errors": [
        {
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "message": "Internal server error occurred",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'multi_no_default_moduleID',
    'cfgs': cfgs,
    'dfltModules': {},
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)


# wrong rootPath
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}

expected = '''{
    "errors": [
        {
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "message": "Internal server error occurred",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'multi_wrong_rootPath',
    'cfgs': cfgs,
    'dfltModules': {},
    'endpoint': 'not-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)

cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)

# wrong method
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}

expected = '''{
    "errors": [
        {
            "code": "INTERNAL_SERVER_ERROR",
            "status": 500,
            "message": "Internal server error occurred",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'multi_wrong_method',
    'cfgs': cfgs,
    'dfltModules': {},
    'endpoint': 'test-root-path',
    'method': 'GET',
    'request': '',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['method'] = 'GET'
cfgs['test-root-path']['argsConvertTypes'] = {
    'in_param_002': float,
    'in_param_003': dict
}
cfgs['test-root-path']['OUTconfigs']['destTransformRule'] = pyjq.compile(
    'del(.in_param_002) | del(.in_param_003)'
)

# GET, success
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}
expected = '{"in_param_001": "smth", "sas_param_001": 0}'
testcases.append({
    'name': 'GET_success',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'GET',
    'request': '?in_param_001=smth&in_param_002=100&in_param_003={"key": "value"}',
    'headers': None,
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 201,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['method'] = 'GET'
cfgs['test-root-path']['argsConvertTypes'] = {
    'in_param_002': float,
    'in_param_003': dict
}
cfgs['test-root-path']['OUTconfigs']['destTransformRule'] = pyjq.compile(
    'del(.in_param_002) | del(.in_param_003)'
)



# GET, invalid request exception
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}

expected = '''{
    "errors": [
        {
            "code": "REQUEST_BODY_INVALID",
            "status": 415,
            "message": "Request body cannot be loaded",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'GET_inv_req_exc',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'GET',
    'request': '?in_param_001=smth&in_param_002=notnumber&in_param_003={"key": "value"}',
    'headers': {'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 415,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['method'] = 'GET'
cfgs['test-root-path']['argsConvertTypes'] = {
    'in_param_002': int,
    'in_param_003': dict
}
cfgs['test-root-path']['OUTconfigs']['destTransformRule'] = pyjq.compile(
    'del(.in_param_002) | del(.in_param_003)'
)

# GET, invalid request json
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}

expected = '''{
    "errors": [
        {
            "code": "REQUEST_BODY_INVALID",
            "status": 415,
            "message": "Request body cannot be loaded",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'GET_inv_req_json',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'GET',
    'request': '?in_param_001=smth&in_param_002=100&in_param_003=}}{{',
    'headers': {'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 415,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['jsonschemaFile'] = 'correct.json'

# Successful call, correct jsonschema
SASResponse = {
    'code': 201,
    'body': {
        'links': [],
        'version': 2,
        'moduleId': 'moduleId',
        'stepId': 'execute',
        'executionState': 'completed',
        'outputs': [
            {
                'name': 'sas_param_001',
                'value': 0
            }
        ]
    }
}
expected = '{"in_param_001": "smth", "sas_param_001": 0}'
testcases.append({
    'name': 'jsonschema_Correct',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 201,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['jsonschemaFile'] = 'missing.json'

# Missing must-have params in config
testcases.append({
    'name': 'jsonschema_nofile',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': None,
    'headers': None,
    'mock_callDecision_return': None,
    'exp_status_code': None,
    'exp_json': None,
    'expected': None,
    'initFails': True
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['jsonschemaFile'] = 'invalid_json.json'

# Missing must-have params in config
testcases.append({
    'name': 'jsonschema_invalid_json',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': None,
    'headers': None,
    'mock_callDecision_return': None,
    'exp_status_code': None,
    'exp_json': None,
    'expected': None,
    'initFails': True
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['jsonschemaFile'] = 'invalid_schema.json'

# Missing must-have params in config
testcases.append({
    'name': 'jsonschema_invalid_schema',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': None,
    'headers': None,
    'mock_callDecision_return': None,
    'exp_status_code': None,
    'exp_json': None,
    'expected': None,
    'initFails': True
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['jsonschemaFile'] = 'correct.json'

# Unsuccessful call, correct jsonschema
expected = '''
{
    "errors": [
        {
            "code": "IN_PARAM_001_REQUIRED",
            "message": "in_param_001 is required",
            "status": 400,
            "traceId": "testId"
        }
    ]
}
'''
testcases.append({
    'name': 'jsonschema_Correct_fail',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_002": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': None,
    'exp_status_code': 400,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['jsonschemaFile'] = 'correct.json'

# Unsuccessful call, correct jsonschema
expected = '''
{
    "errors": [
        {
            "code": "IN_PARAM_001_INVALID",
            "message": "in_param_001 is invalid",
            "status": 400,
            "traceId": "testId"
        }
    ]
}
'''
testcases.append({
    'name': 'jsonschema_validation_error',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": 1}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': None,
    'exp_status_code': 400,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['jsonschemaFile'] = 'correct.json'

# Unsuccessful call, correct jsonschema
expected = '''
{
    "errors": [
        {
            "code": "REQUEST_BODY_VALIDATION_FAILED",
            "message": "Request body cannot be validated. Unknown error.",
            "status": 400,
            "traceId": "testId"
        }
    ]
}
'''
testcases.append({
    'name': 'jsonschema_unknown_error',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "manysymbols"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': None,
    'exp_status_code': 400,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['jsonschemaFile'] = 'correct.json'
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['requiredProperties'] = {'in_param_001':'IN_PARAM_001'}

# Unsuccessful call, correct jsonschema
expected = '''
{
    "errors": [
        {
            "code": "IN_PARAM_001_MISSING",
            "message": "in_param_001 is missing",
            "status": 400,
            "traceId": "testId"
        }
    ]
}
'''
testcases.append({
    'name': 'jsonschema_missing_error',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_002": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': None,
    'exp_status_code': 400,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# Copy base config and change it if needed
cfgs = copy.deepcopy(base_cfgs)
cfgs['test-root-path']['jsonschemaFile'] = 'correct.json'
cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfgs['test-root-path']['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfgs['test-root-path']['requiredProperties'] = {'in_param_001':'IN_PARAM_001'}

# Unsuccessful call, correct jsonschema
expected = '''
{
    "errors": [
        {
            "code": "REQUEST_BODY_VALIDATION_FAILED",
            "message": "Request body cannot be validated",
            "status": 400,
            "traceId": "testId"
        }
    ]
}
'''
testcases.append({
    'name': 'jsonschema_validation_error',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": 1}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': None,
    'exp_status_code': 400,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})