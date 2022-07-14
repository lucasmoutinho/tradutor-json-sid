import copy
import pyjq

testcases = []

# =============================================================================
# =============================================================================
# =============================================================================
# Default sample
INconfigs = [{'name': '', 'rule': '', 'type': '', 'addUnderscore': 0}]
OUTconfigs = {
    'mode': '',
    'params_cfg': [
        {
            'parameterName': '',
            'parameterType': '',
            'mergeRule': {}
        }
    ]
}
cfgs = {}
cfgs['rootPath1'] = {
    'method': 'POST',
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs
}
correct_config = cfgs

# Short sample of correct configuration
INconfigs = [{'name': '', 'rule': pyjq.compile(''), 'type': '', 'addUnderscore': 0}]
OUTconfigs = {
    'mode': '',
    'params_cfg': [
        {
            'parameterName': '',
            'parameterType': '',
            'mergeRule': {}
        }
    ]
}
cfgs = {}
cfgs['rootPath1'] = {
    'method': 'POST',
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs
}
corr_config = cfgs

correct_dfltModules = {
    'rootPath1': 'moduleID1'
}
# =============================================================================
# =============================================================================
# =============================================================================


# =============================================================================
# Is OK, not mandatory are None
INconfigs = [{'name': '', 'rule': pyjq.compile(''), 'type': '', 'addUnderscore': 0}]
OUTconfigs = {
    'mode': '',
    'customDest': None,
    'destTransformRule': None,
    'params_cfg': [
        {
            'parameterName': '',
            'parameterType': '',
            'extractRule': None,
            'renameColDict': None,
            'transformRule': None,
            'reqTransformRule': None,
            'mergeRule': {}
        }
    ]
}
cfgs = {}
cfgs['rootPath1'] = {
    'method': 'POST',
    'argsConvertTypes': None,
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'multiRequestSettings': None,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs
}
cfgs['rootPath2'] = {
    'method': 'POST',
    'argsConvertTypes': None,
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': False,
    'multiRequestSettings': None,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs
}
dfltModules = {
    'rootPath1': 'moduleID1', 'rootPath2': 'moduleID1'
}
testcases.append(
    {
        'name': 'isOK_1',
        'cfgs': cfgs,
        'dfltModules': dfltModules,
        'exp_confIsOK': True
    }
)

# =============================================================================
# Is OK, not mandatory are missing
testcases.append(
    {
        'name': 'isOK_2',
        'cfgs': corr_config,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': True
    }
)

# =============================================================================
# Is OK, not mandatory are filled
INconfigs = [{'name': '', 'rule': pyjq.compile(''), 'type': '', 'addUnderscore': 0}]
OUTconfigs = {
    'mode': '',
    'customDest': {},
    'destTransformRule': pyjq.compile(''),
    'params_cfg': [
        {
            'parameterName': '',
            'parameterType': '',
            'extractRule': pyjq.compile(''),
            'renameColDict': {},
            'transformRule': pyjq.compile(''),
            'reqTransformRule': pyjq.compile(''),
            'mergeRule': {}
        }
    ]
}
multiRequestSettings = {
    'sortSettings': {
        'sortAttr': 's',
        'datefmt': '%Y-%m-%d',
        'direction': 'asc'
    },
    'mergeSettings': {
        'mode': '',
        'customDest': {},
        'destTransformRule': '',
        'validationRule': '',
        'params_cfg': [
            {
                'parameterName': '',
                'parameterType': '',
                'extractRule': '',
                'renameColDict': {},
                'transformRule': '',
                'reqTransformRule': '',
                'mergeRule': {}
            }
        ]
    }
}
cfgs = {}
cfgs['rootPath1'] = {
    'method': 'POST',
    'argsConvertTypes': {'a': int},
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': True,
    'multiRequestSettings': multiRequestSettings,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs
}
cfgs['rootPath2'] = {
    'method': 'GET',
    'argsConvertTypes': {'a': int},
    'moduleIdHeader': False,
    'dfltSuccessResponseCode': 200,
    'dfltErrorResponseCode': 500,
    'useSASResponseCode': False,
    'multiRequest': True,
    'multiRequestSettings': multiRequestSettings,
    'INconfigs': INconfigs,
    'OUTconfigs': OUTconfigs
}
dfltModules = {
    'rootPath1': 'moduleID1', 'rootPath2': 'moduleID1'
}
testcases.append(
    {
        'name': 'isOK_3',
        'cfgs': cfgs,
        'dfltModules': dfltModules,
        'exp_confIsOK': True
    }
)

# =============================================================================
# cfgs: must be dict
testcases.append(
    {
        'name': 'cfgs_must_be_dict',
        'cfgs': None,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: At least one rootPath must be configured
testcases.append(
    {
        'name': 'cfgs_no_rootPath',
        'cfgs': {},
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: Missing variables #1
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1'].pop('method')
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
testcases.append(
    {
        'name': 'cfgs_missing_vars_1',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: Missing variables #2
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['method'] = None
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
testcases.append(
    {
        'name': 'cfgs_missing_vars_2',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: Wrong variables
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['wrong'] = 999
testcases.append(
    {
        'name': 'cfgs_wrong_vars',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: Wrong types
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['method'] = 999
testcases.append(
    {
        'name': 'cfgs_wrong_types',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: incorrect method
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['method'] = 'wrong'
testcases.append(
    {
        'name': 'incorrect_method',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: incorrect INconfigs
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
INconfigs = [{}, 'lalala']
cfgs['rootPath1']['INconfigs'] = INconfigs
testcases.append(
    {
        'name': 'incorrect_OUTconfigs_1',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: incorrect OUTconfigs #1
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
OUTconfigs = {
    'mode': 1,
    'params_cfg': [
        {
            'parameterName': '',
            'parameterType': '',
            'mergeRule': {}
        }
    ]
}
cfgs['rootPath1']['OUTconfigs'] = OUTconfigs
testcases.append(
    {
        'name': 'incorrect_OUTconfigs_1',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# cfgs: incorrect OUTconfigs #2
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
OUTconfigs = {
    'mode': '',
    'params_cfg': [
        {},
        'lalala'
    ]
}
cfgs['rootPath1']['OUTconfigs'] = OUTconfigs
testcases.append(
    {
        'name': 'incorrect_OUTconfigs_2',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# incorrect type in argsConvertTypes
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['argsConvertTypes'] = {'a': object}
testcases.append(
    {
        'name': 'incorrect_argsConvertTypes',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# Incorrect multiRequestSettings
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['multiRequest'] = True
cfgs['rootPath1']['multiRequestSettings'] = {
    'wrong': {}
}
testcases.append(
    {
        'name': 'incorrect_multiRequestSettings',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# Incorrect sortSettings #1
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['multiRequest'] = True
cfgs['rootPath1']['multiRequestSettings'] = {
    'sortSettings': {}
}
testcases.append(
    {
        'name': 'incorrect_sortSettings_1',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# Incorrect sortSettings #2
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['multiRequest'] = True
cfgs['rootPath1']['multiRequestSettings'] = {
    'sortSettings': {
        'sortAttr': 's',
        'datefmt': '%Y-%m-%d',
        'direction': 'wrong'
    }
}
testcases.append(
    {
        'name': 'incorrect_sortSettings_2',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# Incorrect mergeSettings #1
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['multiRequest'] = True
cfgs['rootPath1']['multiRequestSettings'] = {
    'mergeSettings': {}
}
testcases.append(
    {
        'name': 'incorrect_mergeSettings_1',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# Incorrect mergeSettings #2
cfgs = copy.deepcopy(correct_config)
cfgs['rootPath1']['INconfigs'][0]['rule'] = pyjq.compile('')
cfgs['rootPath1']['multiRequest'] = True
cfgs['rootPath1']['multiRequestSettings'] = {
    'mergeSettings': {
        'mode': '',
        'params_cfg': [
            {},
            'lalala'
        ]
    }
}
testcases.append(
    {
        'name': 'incorrect_mergeSettings_2',
        'cfgs': cfgs,
        'dfltModules': correct_dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# =============================================================================
# dfltModules: must be dict
dfltModules = None
correct_config['rootPath1']['INconfigs']= [
    {
        'name': '', 
        'rule': pyjq.compile(''), 
        'type': '', 
        'addUnderscore': 0
        }
]

testcases.append(
    {
        'name': 'dfltModules_must_be_dict',
        'cfgs': correct_config,
        'dfltModules': dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# dfltModules: incorrect moduleID
dfltModules = {'rootPath1': 999}
testcases.append(
    {
        'name': 'dfltModules_incorrect_moduleID',
        'cfgs': correct_config,
        'dfltModules': dfltModules,
        'exp_confIsOK': False
    }
)

# =============================================================================
# dfltModules: Unknown rootPath
dfltModules = {'rootPath3': 'moduleID1'}
testcases.append(
    {
        'name': 'dfltModules_Unknown_rootPath',
        'cfgs': correct_config,
        'dfltModules': dfltModules,
        'exp_confIsOK': False
    }
)
