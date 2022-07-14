import pyjq

OUTconfigs = {}
OUTconfigs['mode'] = 'a2b'
OUTconfigs['customDest'] = None
OUTconfigs['destTransformRule'] = None
OUTconfigs['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'datagrid_level1'
cfg['parameterType'] = 'datagrid'
cfg['extractRule'] = pyjq.compile(
    '.outputs[] | select(.name=="datagrid_level1") | .value'
)
cfg['renameColDict'] = {
    'LEVEL1_KEY': 'level1_key',
    'LEVEL1_PARAM_002': 'level1Param_002'
}
cfg['transformRule'] = None
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': ['level1'],
    'keyAttr': 'level1_key'
}
OUTconfigs['params_cfg'].append(cfg)

cfg = {}
cfg['parameterName'] = 'datagrid_in_level1'
cfg['parameterType'] = 'datagrid'
cfg['extractRule'] = pyjq.compile(
    '.outputs[] | select(.name=="datagrid_in_level1") | .value'
)
cfg['renameColDict'] = {
    'LEVEL1_KEY': 'level1_key'
}
cfg['transformRule'] = pyjq.compile(
    'map({level1_key: .level1_key, level1_in: del(.level1_key)})'
)
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': ['level1'],
    'keyAttr': 'level1_key'
}
OUTconfigs['params_cfg'].append(cfg)

cfg = {}
cfg['parameterName'] = 'datagrid_level2'
cfg['parameterType'] = 'datagrid'
cfg['extractRule'] = pyjq.compile(
    '.outputs[] | select(.name=="datagrid_level2") | .value'
)
cfg['renameColDict'] = {
    'LEVEL2_KEY': 'level2_key',
    'LEVEL2_PARAM_002': 'level2_param_002',
    'LEVEL2_PARAM_003': 'level2_param_003'
}
cfg['transformRule'] = None
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': ['level1', 'level2'],
    'keyAttr': 'level2_key'
}
OUTconfigs['params_cfg'].append(cfg)

cfg = {}
cfg['parameterName'] = 'root2_param_001,root2_param_002'
cfg['parameterType'] = 'data'
cfg['extractRule'] = pyjq.compile(
    '[.outputs[] | select(.name == "root2_param_001"), select (.name == "root2_param_002")]'
)
cfg['renameColDict'] = None
cfg['transformRule'] = pyjq.compile(
    '[map(with_entries(if .key == "name" then .key = "key" else . end)) | from_entries]'
)
cfg['reqTransformRule'] = pyjq.compile('{root: ., root2: {}, root3: []}')
cfg['mergeRule'] = {
    'path': ['root2'],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)

cfg = {}
cfg['parameterName'] = 'datagrid_level2'
cfg['parameterType'] = 'datagrid'
cfg['extractRule'] = pyjq.compile(
    '.outputs[] | select(.name=="datagrid_level2") | .value'
)
cfg['renameColDict'] = {
    'LEVEL2_KEY': 'level2_key',
    'LEVEL2_PARAM_002': 'level2_param_002',
    'LEVEL2_PARAM_003': 'level2_param_003'
}
cfg['transformRule'] = None
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': ['root3'],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)

cfg = {}
cfg['parameterName'] = 'dummy_datagrid'
cfg['parameterType'] = 'datagrid'
cfg['extractRule'] = pyjq.compile(
    '.outputs[] | select(.name=="root2_param_001") | .value'
)
cfg['renameColDict'] = None
cfg['transformRule'] = None
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': ['root3'],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)
