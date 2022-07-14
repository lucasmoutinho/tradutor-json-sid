import pyjq

cfgs = {}

# ----------------------------------------------------------------------------
# --- Config for: POST -------------------------------------------------------
# ----------------------------------------------------------------------------

INconfigs = []

# Example data
root = {}
root['name'] = 'data from root'
root['rule'] = pyjq.compile('[to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]')
root['type'] = 'data'
root['defaultType'] = 'string'
root['dataTypes'] = {'in_double': 'decimal'}
root['addUnderscore'] = 1
INconfigs.append(root)

# Example datagrid
# INconfigs = []

# cfg = {}
# cfg['name'] = 'counterparty'
# cfg['rule'] = pyjq.compile('[. | del(.testAttrib1) | del (.testAttrib2)]')
# cfg['type'] = 'datagrid'
# cfg['addUnderscore'] = 1
# INconfigs.append(cfg)

# -----------------------------------------------------------------------------

OUTconfigs = {}
OUTconfigs['mode'] = 'a2custom'
OUTconfigs['customDest'] = {}
OUTconfigs['destTransformRule'] = None
OUTconfigs['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'out_double,out_string'
cfg['parameterType'] = 'data'
# cfg['extractRule'] = pyjq.compile('[.outputs[] | select(.name == "out_double"), select (.name == "out_string")]')
cfg['extractRule'] = pyjq.compile('[.outputs[]]')
cfg['renameColDict'] = None
cfg['transformRule'] = pyjq.compile('[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]')
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': [],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)


# Example datagrid
# OUTconfigs = {}
# OUTconfigs['mode'] = 'a2b'
# OUTconfigs['customDest'] = None
# OUTconfigs['destTransformRule'] = None
# OUTconfigs['params_cfg'] = []

# cfg = {}
# cfg['parameterName'] = 'dg_out'
# cfg['parameterType'] = 'datagrid'
# cfg['extractRule'] = pyjq.compile('.outputs[] | select(.name=="dg_out") | .value')
# cfg['renameColDict'] = {
#     'OldNameColumn': 'NewNameColumn'
# }
# cfg['transformRule'] = None
# cfg['reqTransformRule'] = None
# cfg['mergeRule'] = {
#     'path': ['path_to_merge'],
#     'keyAttr': 'key_to_merge'
# }
# OUTconfigs['params_cfg'].append(cfg)

# -----------------------------------------------------------------------------

# MultiRequest example

# multiRequestSettings = {}
# cfg = {}

# multiRequestSettings['sortSettings'] = {
#     'sortAttr': 'keyForSort',
#     'datefmt': '%Y-%m-%d',
#     'direction': 'asc'
# }

# mergeSettings = {}
# mergeSettings['mode'] = 'a2b'
# mergeSettings['customDest'] = None
# mergeSettings['destTransformRule'] = None
# mergeSettings['validationRule'] = pyjq.compile(
#     '''
# [
#     if result == "Success"  then 0 else 1 end,
#     [
#         . | select(.result != null) |
#          if .result == "Success" then 0 else 1 end
#     ][]
# ] | add | if . > 0 then 0 else 1 end
# '''
# )
# mergeSettings['params_cfg'] = []

# cfg = {}
# cfg['parameterName'] = 'data from previous step'
# cfg['parameterType'] = 'data'
# cfg['extractRule'] = (pyjq.compile(
#     '[.test[]]'
# ))
# cfg['renameColDict'] = None
# cfg['transformRule'] = None
# cfg['reqTransformRule'] = None
# cfg['mergeRule'] = {
#     'path': ['path_to_merge'],
#     'keyAttr': 'key_to_merge'
# }
# mergeSettings['params_cfg'].append(cfg)

# multiRequestSettings['mergeSettings'] = mergeSettings

# multiRequestSettings['inputSettings'] = pyjq.compile('.[]')
# multiRequestSettings['outputSettings'] = pyjq.compile('{"Result" : .}')


cfgs['test-root-path-post'] = {
    'method': 'POST',
    'argsConvertTypes': {},
    'moduleIdHeader': True,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'multiRequestSettings': {},
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs,
    'jsonschemaFile': '',
    'requiredProperties': {
        'testAttrib':'TEST_ATTRIB'
    }
}

# ----------------------------------------------------------------------------
# --- Config for: POST -------------------------------------------------------
# ----------------------------------------------------------------------------

INconfigs = []

# Example data
root = {}
root['name'] = 'data from root'
root['rule'] = pyjq.compile('[to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]')
root['type'] = 'data'
root['defaultType'] = 'string'
root['dataTypes'] = {'in_double': 'decimal'}
root['addUnderscore'] = 1
INconfigs.append(root)


OUTconfigs = {}
OUTconfigs['mode'] = 'a2b'
OUTconfigs['customDest'] = None
OUTconfigs['destTransformRule'] = None
OUTconfigs['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'out_double,out_string'
cfg['parameterType'] = 'datagrid'
cfg['extractRule'] = pyjq.compile('.outputs[] | select(.name=="dg_out") | .value')
cfg['renameColDict'] = {}
# cfg['transformRule'] = pyjq.compile('[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]')
cfg['transformRule'] = None
cfg['reqTransformRule'] = pyjq.compile('{dg_out_array: []}')
cfg['mergeRule'] = {
    'path': ['dg_out_array'],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)

cfg = {}
cfg['parameterName'] = 'teste'
cfg['parameterType'] = 'data'
#cfg['extractRule'] = pyjq.compile('[.outputs[] | select(.name == "out_double"), select (.name == "out_string")]')
cfg['extractRule'] = pyjq.compile('[.outputs[] | select(.name!="cd_sql_datamart_dgo")]')
cfg['renameColDict'] = None
cfg['transformRule'] = pyjq.compile('[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]')
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': [],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)

cfgs['fl_sql_datamart_query'] = {
    'method': 'POST',
    'argsConvertTypes': {},
    'moduleIdHeader': True,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'multiRequestSettings': {},
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs,
    'jsonschemaFile': '',
    'requiredProperties': {
        'testAttrib':'TEST_ATTRIB'
    }
}

# ----------------------------------------------------------------------------
# --- Config for: GET -------------------------------------------------------
# ----------------------------------------------------------------------------

argsConvertTypes = {
    'in_double': float,
    'in_json': dict
}

INconfigs = []

# Example
root = {}
root['name'] = 'data from root'
root['rule'] = pyjq.compile('[to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]')
root['type'] = 'data'
root['defaultType'] = 'string'
root['dataTypes'] = {'in_double': 'decimal'}
root['addUnderscore'] = 0
INconfigs.append(root)

# -----------------------------------------------------------------------------

OUTconfigs = {}
OUTconfigs['mode'] = 'a2custom'
OUTconfigs['customDest'] = {}
OUTconfigs['destTransformRule'] = None
OUTconfigs['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'out_double,out_string'
cfg['parameterType'] = 'data'
cfg['extractRule'] = pyjq.compile('[.outputs[] | select(.name == "out_double"), select (.name == "out_string")]')
cfg['renameColDict'] = None
cfg['transformRule'] = pyjq.compile('[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]')
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': [],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)


# -----------------------------------------------------------------------------

cfgs['test-root-path-get'] = {
    'method': 'GET',
    'argsConvertTypes': argsConvertTypes,
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'multiRequestSettings': {},
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs,
    'jsonschemaFile': '',
    'requiredProperties': {}
}

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
