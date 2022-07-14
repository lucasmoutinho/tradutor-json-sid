import pyjq

OUTconfigs = {}
OUTconfigs['mode'] = 'b2a'
OUTconfigs['customDest'] = None
OUTconfigs['destTransformRule'] = pyjq.compile(
    'del(.links) | del(.version) | del(.moduleId) | del(.stepId) | del(.executionState)'
)
OUTconfigs['params_cfg'] = []
