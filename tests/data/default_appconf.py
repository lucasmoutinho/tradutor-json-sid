# Default success configuration
cfgs = {}

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

cfgs['test-root-path'] = {
    'method': 'POST',
    'argsConvertTypes': {},
    'moduleIdHeader': True,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': True,
    'multiRequest': False,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs,
    'requiredProperties': {}
}

correct_dfltModules = {'test-root-path': 'moduleID1'}
