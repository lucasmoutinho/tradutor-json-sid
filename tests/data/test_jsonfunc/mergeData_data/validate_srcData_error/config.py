
import pyjq

OUTconfigs = {}
OUTconfigs['mode'] = 'a2b'
OUTconfigs['customDest'] = None
OUTconfigs['destTransformRule'] = None
OUTconfigs['validationRule'] = pyjq.compile('''
[
    if .result.resultCode == "L0000" then 0 else 1 end,
    [
        .counterparty.creditFacilities[] | select(.result.resultCode != null) |
         if .result.resultCode == "L0000" then 0 else 1 end
    ][]
] | add | if . > 0 then 0 else 1 end
''')
OUTconfigs['params_cfg'] = []
