import copy
import pyjq

testcases = []

# =============================================================================
# =============================================================================
# =============================================================================
# Base configuration

base_cfgs = {}

INconfigs = []

cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

OUTconfigs = {}
OUTconfigs['mode'] = 'a2b'
OUTconfigs['customDest'] = None
OUTconfigs['destTransformRule'] = None
OUTconfigs['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'sas_param_001'
cfg['parameterType'] = 'data'
cfg['extractRule'] = '[.outputs[] | select(.name == "sas_param_001")]'
cfg['renameColDict'] = None
cfg['transformRule'] = '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': [],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)

multiRequestSettings = {}
cfg = {}

mergeSettings = {}
mergeSettings['mode'] = 'a2b'
mergeSettings['customDest'] = None
mergeSettings['destTransformRule'] = None
mergeSettings['validationRule'] = ''
mergeSettings['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'data from previous signal'
cfg['parameterType'] = 'data'
cfg['renameColDict'] = None
cfg['transformRule'] = None
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': [],
    'keyAttr': 'in_param_001'
}
mergeSettings['params_cfg'].append(cfg)

multiRequestSettings['mergeSettings'] = mergeSettings
multiRequestSettings['sortSettings'] = {
    'sortAttr': 'TestDate',
    'datefmt': '%Y-%m-%d',
    'direction': 'asc'
}
multiRequestSettings['inputSettings'] = ''
multiRequestSettings['outputSettings'] = ''

base_cfgs['test-root-path'] = {
    'method': 'POST',
    'argsConvertTypes': {},
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 400,
    'useSASResponseCode': True,
    'multiRequest': True,
    'multiRequestSettings': multiRequestSettings,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs,
    'requiredProperties': {}
}

correct_dfltModules = {'test-root-path': 'moduleID1'}

# =============================================================================
# Copy base config and change it if needed
# Invalid multirequest request, not a list

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

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['outputSettings']= None
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')
cfgs['test-root-path']['multiRequestSettings']['inputSettings'] = pyjq.compile('.[]')

expected = '''{
    "errors": [
        {
            "code": "ARRAY_EXTRACT_ERROR",
            "status": 400,
            "message": "Array cannot be extracted according to JQ rule - .[]",
            "traceId": "testId"
        }
    ]
}'''

testcases.append({
    'name': 'Multirequest_InvalidReq',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"in_param_001": "smth"}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 400,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Error occurred while sorting

cfgs = copy.deepcopy(base_cfgs)
cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['inputSettings']= pyjq.compile('')
cfg['multiRequestSettings']['outputSettings']= None
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')
cfgs['test-root-path']['multiRequestSettings']['sortSettings'] = {
    'sortAttr': 'test',
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
    'name': 'Multirequest_InvSort',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"in_param_001": "smth"},{"in_param_002": "smth"}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Success sorting

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['inputSettings']= pyjq.compile('')
cfg['multiRequestSettings']['outputSettings']= None
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')

testcases.append({
    'name': 'Multirequest_SucSort',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"TestDate": "2013-06-09"},{"TestDate": "2018-06-09"}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 201,
    'exp_json': False,
    'expected': '[{"TestDate": "2013-06-09", "sas_param_001": 0}, {"TestDate": "2018-06-09", "sas_param_001": 0}]',
    'initFails': False
})


# =============================================================================
# Copy base config and change it if needed
# Source data failed validation

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['inputSettings']= pyjq.compile('')
cfg['multiRequestSettings']['outputSettings']= None
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile(
    'if .TestVar == "test10" then 1 else 0 end'
)


testcases.append({
    'name': 'Multirequest_SrcValidFail',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"TestDate": "2013-06-09","TestVar": "test1"},{"TestDate": "2018-06-09","TestVar": "test2"}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 200,
    'exp_json': False,
    'expected': '[{"TestDate": "2013-06-09", "TestVar": "test1", "sas_param_001": 0}]',
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Error while merging data

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['inputSettings']= pyjq.compile('')
cfg['multiRequestSettings']['outputSettings']= None
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')
cfg['multiRequestSettings']['mergeSettings']['destTransformRule'] = 'test'

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
    'name': 'Multirequest_MergeErr',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"TestDate": "2013-06-09","TestVar": "test1"},{"TestDate": "2018-06-09","TestVar": "test2"}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Urgent exit

cfgs = copy.deepcopy(base_cfgs)

INconfigs = []

cfg = {}
cfg['name'] = 'test'
cfg['rule'] = pyjq.compile('[.test]')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 1
INconfigs.append(cfg)

cfgs['test-root-path']['INconfigs'] = INconfigs
cfgs['test-root-path']['multiRequestSettings']['mergeSettings']['mode'] = 'a2ba'
cfg = cfgs['test-root-path']
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['inputSettings']= pyjq.compile('')
cfg['multiRequestSettings']['outputSettings']= None
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')


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
    'name': 'Multirequest_UrgentExit',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"TestDate": "2013-06-09","TestVar": "test1"}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Error prepared input body

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')
cfg['multiRequestSettings']['inputSettings'] = pyjq.compile('.[]|select(.test)')
cfg['multiRequestSettings']['outputSettings'] = None


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
    'name': 'Multirequest_prepareInBodyError',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '{"TestDate": "2013-06-09", "TestVar": "test1", "sas_param_001": 0}',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Error prepared out body

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')
cfg['multiRequestSettings']['inputSettings'] = pyjq.compile('.')
cfg['multiRequestSettings']['outputSettings'] = pyjq.compile('..[]|select(.test)')


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
    'name': 'Multirequest_prepareOutBodyError',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"TestDate": "2013-06-09", "TestVar": "test1", "sas_param_001": 0}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 500,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})

# =============================================================================
# Copy base config and change it if needed
# Error prepared out body

cfgs = copy.deepcopy(base_cfgs)

cfg = cfgs['test-root-path']
cfg['INconfigs'][0]['rule'] = pyjq.compile(
    '[. | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "sas_param_001")]'
)
cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['multiRequestSettings']['mergeSettings']['validationRule'] = pyjq.compile('')
cfg['multiRequestSettings']['inputSettings'] = pyjq.compile('.')
cfg['multiRequestSettings']['outputSettings'] = None


expected = '[{"TestDate": "2013-06-09", "TestVar": "test1", "sas_param_001": 0}]'

testcases.append({
    'name': 'Multirequest_prepareOutBodyError',
    'cfgs': cfgs,
    'dfltModules': correct_dfltModules,
    'endpoint': 'test-root-path',
    'method': 'POST',
    'request': '[{"TestDate": "2013-06-09", "TestVar": "test1", "sas_param_001": 0}]',
    'headers': {'Content-Type': 'application/json', 'Trace-Id': 'testId'},
    'mock_callDecision_return': (SASResponse, True, None),
    'exp_status_code': 201,
    'exp_json': True,
    'expected': expected,
    'initFails': False
})