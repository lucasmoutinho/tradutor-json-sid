from collections import OrderedDict

import logging
logger = logging.getLogger(__name__)


def toFlatJSON(dgIn):
    """Convert SAS datagrid to key-value dict

    Parameters
    ----------
    dgIn : list
        SAS datagrid

    Returns
    -------
    list
        JSON with list of dicts in {key: value, ...} format

    """

    # Get metadata and data parts
    if len(dgIn) > 1:
        dgData = dgIn[1]['data']
    else:
        dgData = []

    keys = [list(item.keys())[0] for item in dgIn[0]['metadata']]

    final = []
    for srcEntry in dgData:
        entry = {}
        for i, val in enumerate(srcEntry):
            entry[keys[i]] = val
        final.append(entry)

    return final


def fromFlatJSON(jsonIn):
    """Convert key-value dicts to SAS datagrid.

    Parameters
    ----------
    jsonIn : list
        List of dicts in {key: value, ...} format
        Or None - empty datagrid in this case

    Returns
    -------
    list
        Data encoded in JSON of SAS datagrid style

    """

    # If no data, make it empty list
    if not jsonIn:
        jsonIn = []

    # Check for type
    if not isinstance(jsonIn, list):
        raise TypeError(
            f'Expected: list, but received: {type(jsonIn)}'
        )

    # jsonIn must be list with dicts
    for item in jsonIn:
        if not isinstance(item, dict):
            raise TypeError('Each item must be of dict type')
        for indict_key in item:
            # print(item[indict_key], type(item[indict_key]))
            if item[indict_key] \
                    and type(item[indict_key]) not in (
                        int, float, str, bool):
                raise TypeError(
                    'Every dict must contain only '
                    'int, float, str, bool items'
                )

    # Dictionary of python vs DS2 types
    pythonToDS2Type = {
            str: 'string',
            float: 'decimal',
            bool: 'decimal',
            type(None): 'string'
        }
    # Get all unique keys and their types
    # Use type from the first entry with not null value for keys
    keyTypes = {}
    uniqueVars = set()
    for entry in jsonIn:
        # Get entry vars and union the difference
        entryVars = set(entry.keys())
        diff = entryVars.difference(uniqueVars)
        if len(diff):
            uniqueVars = uniqueVars.union(diff)

        # print(entryVars, diff, uniqueVars)

        for key in uniqueVars:
            # print(key, keyTypes.get(key))
            val = entry.get(key)
            # If type was not found, add it
            # If type found, check for value type
            keyType = keyTypes.get(key)
            if not keyType:
                if val != None:
                    if isinstance(val, int) and not isinstance(val, bool):
                        keyTypes[key] = float
                    else:
                        keyTypes[key] = type(val)
            else:
                if val and not isinstance(val, keyType) \
                        and not (isinstance(val, int)
                                 and keyType == float):
                    raise TypeError(
                        f'Type mismatch for key {key}. '
                        f'Found {val} but expected {keyType}'
                    )

    # If key's type was not found - assign None type
    for key in uniqueVars:
        if not keyTypes.get(key):
            keyTypes[key] = type(None)
    # Sort by name
    keyTypesOrdered = OrderedDict(sorted(keyTypes.items()))

    # Create metadata part
    metadataList = []
    for key, keyType in keyTypesOrdered.items():
        DS2Type = pythonToDS2Type[keyType]
        metadataList.append({key: DS2Type})

    dataList = []

    for entry in jsonIn:
        dataItem = []
        for key, keyType in keyTypesOrdered.items():
            val = entry.get(key)

            # If bool, value must be either 0 or 1
            if keyType == bool:
                val = 1 if val else 0

            dataItem.append(val)

        # print(dataItem)
        dataList.append(dataItem)

    final = [{'metadata': metadataList}, {'data': dataList}]

    return final
