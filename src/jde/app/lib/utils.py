import json
import logging
import os
import time
import pyjq

logger = logging.getLogger(__name__)


# Load string to JSON with checks
def load_json(jsonInput):
    """Perform json.loads(s) with checks and exception handling.

    While trying to load JSON string via json module, next checks are performing:
        input variable cannot be converted to string
        cannot be processed via json.loads in try/except block
        provided string cannot be transformed to dict/list

    Parameters
    ----------
    jsonInput : any
        String with data in JSON format

    Returns
    -------
    dict/list
        result of json.loads(s)
    boolean
        False if any error occurred, else True
    string
        error message text

    """

    try:
        jsonObject = json.loads(jsonInput)
        if type(jsonObject) not in (dict, list):
            return None, False, 'Provided data cannot be transformed to dict/list'
    except Exception:
        return None, False, 'Provided data cannot be processed via json.loads()'

    return jsonObject, True, None


class logWithTime():
    """Class for logging with completion time.

    Attributes
    ----------
    t0 : float
        Last timestamp
    """

    def __init__(self):
        self.t0 = time.time()

    def log(self, msg):
        """Write the message to log with completion time

        Parameters
        ----------
        msg : string
            Message for log

        Returns
        -------
        none

        """
        t1 = time.time()
        s = '{}. Completed in {} ms'.format(msg, round((t1 - self.t0)*1000, 3))
        self.t0 = t1
        logger.debug(s)


def validateDatagridStructure(datagrid):
    """Check for correct structure of datagrid.

    Parameters
    ----------
    datagrid : list
        SAS datagrid converted to Python list.

    Returns
    -------
    boolean
        True if datagrid is correct structure
    string
        Found error, empty if no errors

    """

    if not isinstance(datagrid, list):
        return False, 'Not list'

    i = 0
    metadataColCnt = 0
    for part in datagrid:
        i += 1
        if not isinstance(part, dict):
            return False, 'Each element should be dict'
        if i == 1:
            if bool(set(list(part.keys())).symmetric_difference(['metadata'])):
                return False, 'First element must contain only metadata dict'
            if not isinstance(part['metadata'], list):
                return False, 'Metadata should be list'
            metadataColCnt = len(part['metadata'])
            if metadataColCnt == 0:
                return False, 'No columns in metadata'
            for key in part['metadata']:
                if not isinstance(key, dict):
                    return False, 'One of elements in metadata is not dict'
        elif i == 2:
            if bool(set(list(part.keys())).symmetric_difference(['data'])):
                return False, 'Second element must contain only data dict'
            if not isinstance(part['data'], list):
                return False, 'Data should be list'
            for key in part['data']:
                if not isinstance(key, list):
                    return False, 'One of elements in data is not list'
                if len(key) != metadataColCnt:
                    return False, 'Number of elements in data does not match to metadata'

    if not(i >= 1 and i <= 2):
        return False, 'Must be 1 or 2 elements in list'

    return True, None


def loadConfFromEnv():
    """
    Load configuration for MAS

    Returns
    -------
    dict
        configuration for MAS
    dict
        configuration for default moduleID
    """
    massrvconf = {}
    massrvconf['baseUrl'] = os.environ.get('baseUrl')
    massrvconf['oauth_client_id'] = os.environ.get('oauth_client_id')
    massrvconf['oauth_client_secret'] = os.environ.get('oauth_client_secret')
    # Auth
    massrvconf['grant_type'] = os.environ.get('grant_type')
    massrvconf['username'] = os.environ.get('userId')
    massrvconf['password'] = os.environ.get('SASPASS')

    try:
        callDecisionTimeoutConnect = int(os.environ.get('callDecisionTimeoutConnect'))
    except Exception:
        callDecisionTimeoutConnect = None
    try:
        callDecisionTimeoutRead = int(os.environ.get('callDecisionTimeoutRead'))
    except Exception:
        callDecisionTimeoutRead = None
    try:
        getAccessTokenTimeoutConnect = int(os.environ.get('getAccessTokenTimeoutConnect'))
    except Exception:
        getAccessTokenTimeoutConnect = None
    try:
        getAccessTokenTimeoutRead = int(os.environ.get('getAccessTokenTimeoutRead'))
    except Exception:
        getAccessTokenTimeoutRead = None

    massrvconf['callDecisionTimeout'] = (
        callDecisionTimeoutConnect,
        callDecisionTimeoutRead
    )
    massrvconf['getAccessTokenTimeout'] = (
        getAccessTokenTimeoutConnect,
        getAccessTokenTimeoutRead
    )

    dfltModules = {}
    dfltModulesStr = os.environ.get('dfltModules')
    if dfltModulesStr:
        for key in [rp.split(':') for rp in dfltModulesStr.split(',')]:
            dfltModules[key[0]] = key[1]

    return massrvconf, dfltModules


def checkConf(cfgs, dfltModules):
    """
    Check for configuration in appconf
    massrvconf is not needed to be checked because it is done in masserver

    Parameters
    ----------
    cfgs : dict
        Configuration for JDE
    dfltModules : dict
        configuration for default moduleID

    Returns
    -------
    bool
        True if configuration is OK. Otherwise, False
    """

    # -------------------------------------------------------------------
    # Custom fuction for checking dictionaries
    def checkDict(dict2check, properVars):
        """
        Check variables of dictionary

        Parameters
        ----------
        dict2check : [type]
            [description]
        properVars : dict
            Dictionary with info for each variable
            In format 'var': {'type': type, 'mustHave': bool)

        Returns
        -------
        str
            String with errors
        """

        allowedVarsSet = set(properVars.keys())
        mustHaveVarsSet = set()
        for var in properVars:
            if properVars[var]['mustHave']:
                mustHaveVarsSet.add(var)

        dictVarsSet = set(dict2check.keys())

        # Check if configuration does not contain any invalid variables
        allowedDiff = dictVarsSet.difference(allowedVarsSet)
        # Check if configuration contains all must-have variables
        mustHaveDiff = mustHaveVarsSet.difference(dictVarsSet)

        passed = True

        msgList = []

        if bool(allowedDiff):
            passed = False
            msgList.append(
                'Wrong variables: {}. '.format(
                    list(allowedDiff)
                )
            )

        if bool(mustHaveDiff):
            passed = False
            msgList.append(
                'Missing variables: {}. '.format(
                    list(mustHaveDiff)
                )
            )

        if passed:
            for key in dict2check:
                requiredType = properVars[key]['type']
                if dict2check[key] is not None:
                    if not isinstance(dict2check[key], requiredType):
                        passed = False
                        msgList.append('{} must be of type {}'.format(
                            key,
                            str(requiredType)
                        ))
                elif properVars[key]['mustHave']:
                    passed = False
                    msgList.append(f'{key} cannot be empty')

        msg = '; '.join(msgList)

        return msg
    # -------------------------------------------------------------------

    confIsOK = True

    # must be dict
    if not isinstance(cfgs, dict):
        logger.error('cfgs must be dict')
        return False
    # at least one rootPath must be configured
    if len(cfgs) == 0:
        logger.error('At least one rootPath must be configured')
        return False

    # Check all configurations one-by-one
    # Variables, their types and mustHave flag
    properVars = {
        'method': {'type': str, 'mustHave': True},
        'argsConvertTypes': {'type': dict, 'mustHave': False},
        'moduleIdHeader': {'type': bool, 'mustHave': True},
        'dfltSuccessResponseCode': {'type': int, 'mustHave': True},
        'dfltErrorResponseCode': {'type': int, 'mustHave': True},
        'useSASResponseCode': {'type': bool, 'mustHave': True},
        'multiRequest': {'type': bool, 'mustHave': True},
        'multiRequestSettings': {'type': dict, 'mustHave': False},
        'INconfigs': {'type': list, 'mustHave': True},
        'OUTconfigs': {'type': dict, 'mustHave': True},
        'jsonschemaFile': {'type': str, 'mustHave': False},
        'requiredProperties': {'type': dict, 'mustHave': False}
    }

    for cfgName in cfgs:
        msg = checkDict(cfgs[cfgName], properVars)
        if msg:
            logger.error(f'Config for {cfgName}. {msg}')
            return False

    # Check values in all configurations one-by-one
    for cfgName in cfgs:
        for key in cfgs[cfgName]:
            foundVar = cfgs[cfgName][key]

            if key == 'method':
                if foundVar not in ['GET', 'POST']:
                    confIsOK = False
                    logger.error(
                        f'Config for {cfgName}. {key} can be only GET/POST'
                    )

            elif key == 'multiRequestSettings' \
                    and foundVar:
                properVars = {
                    'sortSettings': {'type': dict, 'mustHave': False},
                    'mergeSettings': {'type': dict, 'mustHave': False},
                    'inputSettings': {'type': pyjq._pyjq.Script, 'mustHave': False},
                    'outputSettings': {'type': pyjq._pyjq.Script, 'mustHave': False}

                }
                msg = checkDict(foundVar, properVars)
                if msg:
                    confIsOK = False
                    logger.error(f'Config for {cfgName}, {key}. {msg}')
                elif foundVar.get('sortSettings') is not None:
                    # Check sortSettings
                    sortSettings = foundVar.get('sortSettings')
                    # Variables, their types and mustHave flag
                    properVars = {
                        'sortAttr': {'type': str, 'mustHave': True},
                        'datefmt': {'type': str, 'mustHave': False},
                        'direction': {'type': str, 'mustHave': False}
                    }
                    msg = checkDict(sortSettings, properVars)
                    if msg:
                        confIsOK = False
                        logger.error(
                            f'Config for {cfgName}, {key}, sortSettings. '
                            f'{msg}'
                        )
                    elif sortSettings.get('direction', '') not in ('',
                                                                   'asc',
                                                                   'desc'):
                        confIsOK = False
                        logger.error(
                            f'Config for {cfgName}, {key}, sortSettings. '
                            'direction can be None, \'\', \'asc\', \'desc\''
                        )
                elif foundVar.get('mergeSettings') is not None:
                    mergeSettings = foundVar.get('mergeSettings')
                    # Variables, their types and mustHave flag
                    properVars = {
                        'mode': {'type': str, 'mustHave': True},
                        'customDest': {'type': dict, 'mustHave': False},
                        'destTransformRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                        'validationRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                        'params_cfg': {'type': list, 'mustHave': True}
                    }
                    msg = checkDict(mergeSettings, properVars)
                    if msg:
                        confIsOK = False
                        logger.error(f'Config for {cfgName}, {key}. {msg}')
                    else:
                        for i, params in enumerate(mergeSettings['params_cfg']):
                            if not isinstance(params, dict):
                                confIsOK = False
                                logger.error(
                                    f'Config for {cfgName}, {key}, '
                                    f'params_cfg[{i}]. Element is not dict'
                                )
                            else:
                                # Variables, their types and mustHave flag
                                properVars = {
                                    'parameterName': {'type': str, 'mustHave': True},
                                    'parameterType': {'type': str, 'mustHave': True},
                                    'extractRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                                    'renameColDict': {'type': dict, 'mustHave': False},
                                    'transformRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                                    'reqTransformRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                                    'mergeRule': {'type': dict, 'mustHave': True}
                                }
                                msg = checkDict(params, properVars)
                                if msg:
                                    confIsOK = False
                                    logger.error(
                                        f'Config for {cfgName}, {key}, '
                                        f'mergeSettings, params_cfg[{i}]. {msg}'
                                    )

            elif key == 'INconfigs':
                for i, params in enumerate(foundVar):
                    if not isinstance(params, dict):
                        confIsOK = False
                        logger.error(
                            f'Config for {cfgName}, {key}, '
                            f'params_cfg[{i}]. Element is not dict'
                        )
                    else:
                        # Variables, their types and mustHave flag
                        properVars = {
                            'name': {'type': str, 'mustHave': True},
                            'rule': {'type': pyjq._pyjq.Script, 'mustHave': True},
                            'type': {'type': str, 'mustHave': True},
                            'newNames': {'type': dict, 'mustHave': False},
                            'defaultType': {'type': str, 'mustHave': False},
                            'dataTypes': {'type': dict, 'mustHave': False},
                            'addUnderscore': {'type': int, 'mustHave': True}
                        }
                        msg = checkDict(params, properVars)
                        if msg:
                            confIsOK = False
                            logger.error(
                                f'Config for {cfgName}, {key}[{i}]. {msg}'
                            )

            elif key == 'OUTconfigs':
                # Variables, their types and mustHave flag
                properVars = {
                    'mode': {'type': str, 'mustHave': True},
                    'customDest': {'type': dict, 'mustHave': False},
                    'destTransformRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                    'params_cfg': {'type': list, 'mustHave': True}
                }
                msg = checkDict(foundVar, properVars)
                if msg:
                    confIsOK = False
                    logger.error(f'Config for {cfgName}, {key}. {msg}')
                else:
                    for i, params in enumerate(foundVar['params_cfg']):
                        if not isinstance(params, dict):
                            confIsOK = False
                            logger.error(
                                f'Config for {cfgName}, {key}, '
                                f'params_cfg[{i}]. Element is not dict'
                            )
                        else:
                            # Variables, their types and mustHave flag
                            properVars = {
                                'parameterName': {'type': str, 'mustHave': True},
                                'parameterType': {'type': str, 'mustHave': True},
                                'extractRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                                'renameColDict': {'type': dict, 'mustHave': False},
                                'transformRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                                'reqTransformRule': {'type': pyjq._pyjq.Script, 'mustHave': False},
                                'mergeRule': {'type': dict, 'mustHave': True}
                            }
                            msg = checkDict(params, properVars)
                            if msg:
                                confIsOK = False
                                logger.error(
                                    f'Config for {cfgName}, {key},'
                                    f' params_cfg[{i}]. {msg}'
                                )

            elif key == 'argsConvertTypes' \
                    and foundVar:
                for param in foundVar:
                    if foundVar[param] not in (int,
                                               float,
                                               dict,
                                               list):
                        confIsOK = False
                        logger.error(
                            f'Config for {cfgName}, {key}. '
                            f'Wrong value for {param}'
                        )

    # must be dict
    if not isinstance(dfltModules, dict):
        confIsOK = False
        logger.error('dfltModules must be dict')
    else:
        for rootPath in dfltModules:
            # check for proper vars in conf
            if not isinstance(dfltModules[rootPath], str):
                confIsOK = False
                logger.error('moduleID for {} has incorrect format'.format(
                    rootPath
                ))

    if confIsOK:
        s1 = set(cfgs.keys())
        s2 = set(dfltModules.keys())
        diff = s2.difference(s1)
        if bool(diff):
            confIsOK = False
            logger.error(f'Unknown rootPath in dfltModules: {diff}')

    return confIsOK
