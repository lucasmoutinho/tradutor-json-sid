import pyjq

testcases = []


# ============================================================
# datagrid_empty
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid0'
cfg['rule'] = pyjq.compile('.root.datagrid0')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'datagrid0',
            'type': 'datagrid',
            'value': [
                {'metadata': []},
                {'data': []}
            ]
        }
    ]},
    True,
    None
)

testcases.append({'name': 'datagrid_empty', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# datagrid_one
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid1'
cfg['rule'] = pyjq.compile('.root.datagrid1')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'datagrid1',
            'type': 'datagrid',
            'value': [
                {'metadata': [{'param1': 'decimal'}, {'param2': 'string'}]},
                {'data': [[100, 'ABC'], [101, 'DEF']]}
            ]
        }
    ]},
    True,
    None
)

testcases.append({'name': 'datagrid_one', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# datagrid_two
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid1'
cfg['rule'] = pyjq.compile('.root.datagrid1')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)
cfg = {}
cfg['name'] = 'datagrid2'
cfg['rule'] =pyjq.compile('.root.datagrid2')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 1
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'datagrid1',
            'type': 'datagrid',
            'value': [
                {'metadata': [{'param1': 'decimal'}, {'param2': 'string'}]},
                {'data': [[100, 'ABC'], [101, 'DEF']]}
            ]
        },
        {
            'name': 'datagrid2_',
            'type': 'datagrid',
            'value': [
                {'metadata': [{'param3': 'decimal'}, {'param4': 'string'}]},
                {'data': [[200, 'GHI'], [201, 'JKL']]}
            ]
        }
    ]},
    True,
    None
)

testcases.append({'name': 'datagrid_two', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# datagrid_wrong
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid_wrong'
cfg['rule'] = pyjq.compile('.root.data')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    None,
    False,
    'Error occured while creating >> datagrid_wrong <<'
)

testcases.append({'name': 'datagrid_wrong', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__no_defaultType
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['addUnderscore'] = 0
# cfg['defaultType'] = 'string'
# cfg['dataTypes'] = {'param1': 'decimal', 'param2': 'string'}
# cfg['newNames'] = {'debtRecovery': 'debtRecovery_', 'watchStatus': 'watchStatus_'}
INconfigs.append(cfg)

expected = (
    None,
    False,
    'Error occured while creating >> just data <<'
)

testcases.append({'name': 'data__no_defaultType', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__only_defaultType
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['addUnderscore'] = 0
# cfg['dataTypes'] = {'param1': 'decimal', 'param2': 'string'}
# cfg['newNames'] = {'debtRecovery': 'debtRecovery_', 'watchStatus': 'watchStatus_'}
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__only_defaultType', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__dataTypes
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['dataTypes'] = {'param1': 'decimal'}
cfg['addUnderscore'] = 0
# cfg['newNames'] = {'debtRecovery': 'debtRecovery_', 'watchStatus': 'watchStatus_'}
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'decimal',
            'value': 100
        },
        {
            'name': 'param2',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__dataTypes', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__newNames
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
# cfg['dataTypes'] = {'param1': 'decimal'}
cfg['newNames'] = {'param2': 'param2_'}
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2_',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__newNames', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__newNames_1
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
# cfg['dataTypes'] = {'param1': 'decimal'}
cfg['newNames'] = {'param2': 'param2_'}
cfg['addUnderscore'] = 1
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1_',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2__',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__newNames_1', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__newNames_2
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
# cfg['dataTypes'] = {'param1': 'decimal'}
cfg['newNames'] = {'param2': 'param2_'}
cfg['addUnderscore'] = 2
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1_',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2_',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__newNames_2', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__nonscalar_list
# It's OK, but SAS will return error
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.nonscalar_list | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2',
            'type': 'string',
            'value': ['A', 'B', 'C']
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__nonscalar_list', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__nonscalar_dict
# It's OK, but SAS will return error
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.nonscalar_dict | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2',
            'type': 'string',
            'value': {"param3": 110, "param4": "DEF"}
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__nonscalar_dict', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# invalid_pyjq_rule
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid0'
cfg['rule'] = 'it is invalid rule'
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    None,
    False,
    'Error occured while creating >> datagrid0 <<'
)

testcases.append({'name': 'invalid_pyjq_rule', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# no_data_found
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid0'
cfg['rule'] = pyjq.compile('.root.datagrid0[]')
cfg['type'] = 'datagrid'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    None,
    False,
    'Error occured while creating >> datagrid0 <<'
)

testcases.append({'name': 'no_data_found', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# no_appropriate_type
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid1'
cfg['rule'] = pyjq.compile('.root.datagrid1')
cfg['type'] = 'no_appropriate_type'
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': []},
    True,
    None
)

testcases.append({'name': 'no_appropriate_type', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__null_newNames
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['dataTypes'] = {'param1': 'decimal'}
cfg['addUnderscore'] = 0
cfg['newNames'] = None
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'decimal',
            'value': 100
        },
        {
            'name': 'param2',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__null_newNames', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# data__null_dataTypes
INconfigs = []
cfg = {}
cfg['name'] = 'just data'
cfg['rule'] = pyjq.compile(
    '[.root.data | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
)
cfg['type'] = 'data'
cfg['defaultType'] = 'string'
cfg['dataTypes'] = None
cfg['newNames'] = {'param2': 'param2_'}
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'param1',
            'type': 'string',
            'value': 100
        },
        {
            'name': 'param2_',
            'type': 'string',
            'value': 'ABC'
        }
    ]},
    True,
    None
)

testcases.append({'name': 'data__null_dataTypes', 'INconfigs': INconfigs, 'expected': expected})


# ============================================================
# datagrid1_newNames
INconfigs = []
cfg = {}
cfg['name'] = 'datagrid1'
cfg['rule'] = pyjq.compile('.root.datagrid1')
cfg['type'] = 'datagrid'
cfg['newNames'] = {
    'param2': 'param2_changed'
}
cfg['addUnderscore'] = 0
INconfigs.append(cfg)

expected = (
    {'inputs': [
        {
            'name': 'datagrid1',
            'type': 'datagrid',
            'value': [
                {'metadata': [{'param1': 'decimal'}, {'param2_changed': 'string'}]},
                {'data': [[100, 'ABC'], [101, 'DEF']]}
            ]
        }
    ]},
    True,
    None
)

testcases.append({'name': 'datagrid1_newNames', 'INconfigs': INconfigs, 'expected': expected})