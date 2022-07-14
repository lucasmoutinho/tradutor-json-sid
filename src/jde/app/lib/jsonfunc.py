# import time
import copy
import json
import logging
from datetime import datetime

import pyjq
from app.lib import sasdgfunc, utils

logger = logging.getLogger(__name__)


def prepMultiBody(jsonRequest, configs):
    """Transform input and output JSON body for multirequest.

    Parameters
    ----------
    jsonRequest : dict
        JSON input or output message
    configs : str
        Rule for construction of the input or output message.

    Returns
    -------
    dict
       prepared JSON body
    boolean
        True for success, False if failed
    string
        Short error description.

    """
    try:
        jsonBody = configs.first(jsonRequest)
    except Exception:
        logger.error('Provided body cannot be transform', exc_info=True)
        return None, False, 'Provided body cannot be transform'

    return jsonBody, True, None

def dgFromJSON(jsonRequest, configs):
    """Extract data from input JSON message and transform it to MAS style.
    MAS style is like this for every input parameter:
        {"name": <name>,"type": <type>,"value":<value>}
    Datagrid transformation is supported
    Multiple parameter transformation is supported

    Parameters
    ----------
    jsonRequest : dict
        JSON input message
    configs : list
        Configuration for construction of the input message.


    Returns
    -------
    dict
        JSON data in MAS style.
    boolean
        True for success, False if failed
    string
        Short error description.

    """

    logger.debug('Creating SAS request body...')
    lwt = utils.logWithTime()

    datas = []

    for cfg in configs:
        # Break if error occurs while creating input parameter
        try:
            logger.debug('-- Creating {}'.format(cfg.get('name')))
            # timings0 = time.time()

            # Extract data for parameter
            extracted =cfg.get('rule').first(jsonRequest)
            lwt.log('---- 1. Extract from request')
            # print(json.dumps(extracted, indent=4))

            if cfg.get('type') == 'datagrid':
                # Rename
                if cfg.get('newNames'):
                    newNames = cfg.get('newNames')
                else:
                    newNames = {}
                try:
                    for j in range(len(extracted)):
                        for variableName in list(extracted[j]):
                            newName = newNames.get(variableName)
                            if newName:
                                extracted[j][newName] = extracted[j].pop(variableName)
                except Exception as e:
                    logger.debug('Renaming is skipped due to error', exc_info=True)
                # print(json.dumps(extracted, indent=4))
                lwt.log('---- 2a. Provide new names')

                # Transform to datagrid
                dgCurrent = sasdgfunc.fromFlatJSON(extracted)
                lwt.log('---- 2b. Transform to datagrid')

                variableName = cfg.get('name')
                if cfg.get('addUnderscore') == 1:
                    variableName = f'{variableName}_'
                d = {
                    'name': variableName,
                    'type': 'datagrid',
                    'value': dgCurrent
                }
                # print(json.dumps(d, indent=4))
                datas.append(d)
            elif cfg.get('type') == 'data':
                # Provide data type
                if cfg.get('dataTypes'):
                    dataTypes = cfg.get('dataTypes')
                else:
                    dataTypes = {}
                for j in range(len(extracted)):
                    extracted[j]['type'] = dataTypes.get(
                                                extracted[j]['name'],
                                                cfg.get('defaultType')
                                            )

                    if not extracted[j]['type']:
                        logger.error(f'No data type is provided for element {j}')
                        return None, False, \
                            'Error occured while creating >> {} <<'.format(
                                cfg.get('name')
                            )

                lwt.log('---- 2b. Provide types')

                # Rename
                if cfg.get('newNames'):
                    newNames = cfg.get('newNames')
                else:
                    newNames = {}
                for j in range(len(extracted)):
                    variableName = extracted[j]['name']
                    newName = newNames.get(variableName)
                    addUnderscore = cfg.get('addUnderscore')
                    if newName:
                        if addUnderscore == 1:
                            variableName = f'{newName}_'
                        else:
                            variableName = newName
                    elif addUnderscore in (1, 2):
                        variableName = f'{variableName}_'

                    extracted[j]['name'] = variableName
                lwt.log('---- 3b. Provide new names')

                datas.extend(extracted)
        except Exception as e:
            logger.error(e, exc_info=True)
            return None, False, \
                'Error occured while creating >> {} <<'.format(cfg.get('name'))

    SASReq_body = {'inputs': datas}
    return SASReq_body, True, None


def getElementByPath(path, inputObject):
    """Constructs list of elements found in path
    Elements are only mutable types (dict/list) and they reference to source
    Can be either dict or list - is determined by the first found

    Parameters
    ----------
    path : string
        assumed that it is key in dict, that points to dict/list
    inputObject : list
        Where to search by path. List with elements referencing to source.
        Elements are list or dict

    Returns
    -------
    elementList: list
        List with dicts/lists found by path, elements are referencing to source

    """

    elementList = []
    # Can be either dict or list - is determined by the first found
    firstElementType = None

    # Only list as input
    # Path should be provided
    if isinstance(inputObject, list) and path:
        for key in inputObject:
            # Expecting dict or list with dicts for elements
            if isinstance(key, dict):
                key = [key]
            if isinstance(key, list):
                for childElement in key:
                    if isinstance(childElement, dict):
                        # Search by path.
                        # Found variables can be only dict or list
                        byPath = childElement.get(path)
                        if firstElementType:
                            if isinstance(byPath, firstElementType):
                                elementList.append(byPath)
                        else:
                            if isinstance(byPath, dict) or \
                                    isinstance(byPath, list):
                                elementList.append(byPath)
                                firstElementType = type(byPath)

    return elementList


def mergeData(srcJSON_a, srcJSON_b, configs):
    """Merge two JSON messages according to configuration

    Parameters
    ----------
    srcJSON_a : dict
        JSON message 'a'
    srcJSON_b : dict
        JSON message 'b'
    configs : dict
        Configuration for merging.

    Returns
    -------
    dict
        Final output message.
    boolean
        True for success, False if failed
    string
        Short error description.

    """

    logger.debug('Creating output...')
    lwt = utils.logWithTime()

    # Determine from where to where merge data
    mode = configs['mode']
    if mode == 'a2b':
        srcData = copy.deepcopy(srcJSON_a)
        dest = copy.deepcopy(srcJSON_b)
    elif mode == 'a2a':
        srcData = copy.deepcopy(srcJSON_a)
        dest = copy.deepcopy(srcJSON_a)
    elif mode == 'b2a':
        srcData = copy.deepcopy(srcJSON_b)
        dest = copy.deepcopy(srcJSON_a)
    elif mode == 'a2custom':
        srcData = copy.deepcopy(srcJSON_a)
        dest = copy.deepcopy(configs.get('customDest'))
    else:
        return None, False, f'mode {mode} is not allowed'

    # Transform dest
    try:
        if configs.get('destTransformRule'):
            dest = configs.get('destTransformRule').first(dest)
    except Exception as e:
        logger.error(e, exc_info=True)
        return None, False, 'Error occured while creating dest'

    # Validate srcData
    try:
        if configs.get('validationRule'):
            validationResult =configs.get('validationRule').first(srcData)

            if validationResult == 0:
                logger.debug('Validation failed. Exiting...')
                return None, False, 'Source data failed validation'

    except Exception as e:
        logger.error(e, exc_info=True)
        return None, False, 'Error occured while validation'

    # print(json.dumps(srcData, indent=4))
    # print(json.dumps(dest, indent=4))

    lwt.log('---- 0. Destination preparation')

    # Cumulative embedding according to configuration
    for cfg in configs.get('params_cfg'):
        try:
            logger.debug('-- Embedding {}'.format(cfg.get('parameterName')))

            # --------------------------------------------------
            # 1. Extract from new data
            if cfg.get('extractRule'):
                extracted =cfg.get('extractRule').first(srcData)
                # print(json.dumps(extracted, indent=4))
            else:
                extracted = srcData
            lwt.log('---- 1. Extract from new data')

            # --------------------------------------------------
            # Only for datagrids
            if cfg.get('parameterType') == 'datagrid':

                # Validate structure
                status, errorMsg = utils.validateDatagridStructure(extracted)
                if not status:
                    logger.debug(f'Skipped. Parameter is not datagrid due to {errorMsg}')
                    continue

                # DG1. Rename columns
                if cfg.get('renameColDict'):
                    for key in extracted[0]['metadata']:
                        for mdColName in list(key):
                            if mdColName in list(cfg.get('renameColDict')):
                                key[cfg.get('renameColDict').get(mdColName)] = key.pop(mdColName)
                lwt.log('---- DG1. Rename columns')

                # DG2. Transform to key-value pair
                extracted = sasdgfunc.toFlatJSON(extracted)
                # print(json.dumps(extracted, indent=4))
                lwt.log('---- DG2. Transform to key-value pair')

            # --------------------------------------------------
            # 2. Transform
            transformed = extracted
            if cfg.get('transformRule'):
                transformed =cfg.get('transformRule').first(extracted)
                # print(json.dumps(transformed, indent=4))
            lwt.log('---- 2. Transform')

            # --------------------------------------------------
            # 3. Transform the original input message
            if cfg.get('reqTransformRule'):
                dest =cfg.get('reqTransformRule').first(dest)
                # print(json.dumps(dest, indent=4))
            lwt.log('---- 3. Transform the original input message')

            # --------------------------------------------------
            # 4. Merge extracted data to original request
            if isinstance(transformed, list) and len(transformed) >= 1:
                path = cfg.get('mergeRule')['path']
                keyAttr = cfg.get('mergeRule')['keyAttr']

                # Extract all elements from path as list of dicts
                # with reference to dest
                # if path is provided, go to the finish step by step
                target = [dest]
                for i in range(len(path)):
                    target = getElementByPath(path[i], target)
                # print('target before', json.dumps(target, indent=4))
                # print('transformed', json.dumps(transformed, indent=4))

                # If keyAttr is provided,
                # target should be like [[{},{}],[{},{}],[{},{}]]
                # Merge data from transformed with dicts in target
                if keyAttr:
                    # Get list of values of keyAttr for each element in transformed
                    # It gives null if no keyAttr is in element
                    # Keep the same order as in transformed - it's IMPORTANT!
                    keyAttr_val_list = []
                    rule = f'[.[] | .{keyAttr}]'
                    keyAttr_val_list.extend(pyjq.first(rule, transformed))

                    # For each element in request - merge with transformed
                    for j in range(len(target)):
                        if isinstance(target[j], list):
                            for k in range(len(target[j])):
                                if isinstance(target[j][k], dict):
                                    # Search for index of element with the same keyAttr
                                    elementIndex = None
                                    elementKeyVal = target[j][k].get(keyAttr)
                                    # Ignore null and "" as key values
                                    if elementKeyVal:
                                        try:
                                            # Take only the first found
                                            elementIndex = keyAttr_val_list.index(elementKeyVal)
                                        except ValueError:
                                            elementIndex = None

                                    # If no index was found, keep this target
                                    # as is and go to the next one
                                    if elementIndex is not None:
                                        # Copy parameters from found element to dest
                                        # Create new or overwrite value
                                        for key in list(transformed[elementIndex]):
                                            # Exclude keyAttr
                                            if key != keyAttr:
                                                val = transformed[elementIndex].get(key)
                                                # Make "" as null
                                                if not val:
                                                    val = None
                                                target[j][k][key] = val
                else:
                    # If no keyAttr is provided,
                    # add all information from transformed to target
                    # If target is like [{}<,{},{},...>],
                    # transformed should be [{}], add keys
                    # If target is like [[]<,[],[],...>],
                    # transformed should be [[],[],[]], extend it
                    for j in range(len(target)):
                        if isinstance(target[j], dict):
                            # Works only with the first element of transformed
                            # others are ignored
                            for key in transformed[0]:
                                target[j][key] = transformed[0][key]
                        elif isinstance(target[j], list):
                            target[j].extend(transformed)

                # print('target after', json.dumps(target, indent=4))
                # print('dest after', json.dumps(dest, indent=4))

                lwt.log('---- 4. Merge in dg2json style')

        except Exception as e:
            logger.error(e, exc_info=True)
            return None, False, \
                'Error occured while creating {}'.format(
                    cfg.get('parameterName')
                )

    # print(json.dumps(dest, indent=4))
    return dest, True, None


def sortReqEntries(origRequest, sortSettings):
    """Sorting request data by key

    Parameters
    ----------
    origRequest : list
        Original request.
    sortSettings : dict
        Special settings for multi requests

    Returns
    -------
    list
        Original request after sorting
    boolean
        True for success, False if failed
    string
        Short error description.

    """

    try:
        if sortSettings:
            sortAttr = sortSettings['sortAttr']
            datefmt = sortSettings.get('datefmt')
            reverse = True if sortSettings.get('direction') == 'desc' else False
            logger.debug('Sort by {}, desc={}, datefmt {}'.format(
                sortAttr,
                reverse,
                datefmt
            ))

            # if date format is provided, apply
            if datefmt:
                sortedDicts = sorted(
                    origRequest,
                    key=lambda x: datetime.strptime(x.get(sortAttr), datefmt),
                    reverse=reverse
                )
            else:
                sortedDicts = sorted(
                    origRequest,
                    key=lambda x: x.get(sortAttr),
                    reverse=reverse
                )
        else:
            logger.debug('Keep default order')
            sortedDicts = origRequest

        return sortedDicts, True, None

    except Exception as e:
        logger.error(e, exc_info=True)
        return None, False, \
            'Error occurred while sorting'
