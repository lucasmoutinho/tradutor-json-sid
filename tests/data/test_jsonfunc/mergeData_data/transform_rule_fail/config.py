OUTconfigs = {}
OUTconfigs['mode'] = 'a2custom'
OUTconfigs['customDest'] = {'SASResponse': {}}
OUTconfigs['destTransformRule'] = None
OUTconfigs['params_cfg'] = []

cfg = {}
cfg['parameterName'] = 'all_data'
cfg['parameterType'] = 'data'
cfg['extractRule'] = None
cfg['renameColDict'] = None
cfg['transformRule'] = 'not pyjq rule'
cfg['reqTransformRule'] = None
cfg['mergeRule'] = {
    'path': ['SASResponse'],
    'keyAttr': None
}
OUTconfigs['params_cfg'].append(cfg)
