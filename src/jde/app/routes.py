import time
import json
import uuid
import jsonschema
import re
import pyjq

from app.lib.jsonfunc import dgFromJSON, mergeData, \
    sortReqEntries, prepMultiBody
from app.lib import utils

from flask import current_app, g, request, Blueprint, make_response, request, abort

logger = current_app.logger

dfltModules = getattr(g, 'dfltModules', None)
mas = getattr(g, 'mas', None)
cfgs = getattr(g, 'cfgs', None)
validators = getattr(g, 'validators', None)

bp = Blueprint('main', __name__)


def createErrorBody(code, status, message, traceId=None, errBody=None):
    """
    Preparing error body

    Parameters
    ----------
    code : str
       Error code
    status : int
        HTTP status code
    message : str
        Error message
    traceId : str, optional
        request trace ID
    errBody : int, optional
        Available error body

    Returns
    -------
    string
        Error body
    """

    err = {}
    err['code'] = code
    err['status'] = status
    err['message'] = message
    err['traceId'] = getattr(g, 'traceId', None)
    if errBody:
        errBody['errors'].append(err)
    else:
        errBody = {
            'errors': [
                err
            ]
        }
    return errBody


def singleRequest(origRequestBody, cfgs, moduleID, requestOrderNum=0):
    """
    Process single request

    Parameters
    ----------
    origRequestBody : dict/list
        Original request body
    cfgs : dict
        Configuration for chosen rootPath
    moduleID : str
        MAS module
    requestOrderNum : int, optional
        Order number of the request, by default 0

    Returns
    -------
    object
        Response body
    int
        Response code
    bool
        True if error
    str
        Response message in simple text, only errors here
    """
    logger.debug(f'Start processing request No: {requestOrderNum}')
    logger.trace('origRequestBody:\n{}'.format(
        json.dumps(origRequestBody, indent=4)
    ))

    err = None
    responseCode = None

    # Start stopwatch for logging
    logSteps = []
    t0 = time.time()

    # Get info from cfgs
    dfltSuccessResponseCode = cfgs['dfltSuccessResponseCode']
    dfltErrorResponseCode = cfgs['dfltErrorResponseCode']
    useSASResponseCode = cfgs['useSASResponseCode']
    INconfigs = cfgs['INconfigs']
    OUTconfigs = cfgs['OUTconfigs']

    # -------------------------------------------------------------------------
    # Construct SAS request
    # -------------------------------------------------------------------------
    SASRequestBody, status, errorMsg = dgFromJSON(origRequestBody, INconfigs)
    logger.trace('Result of dgFromJSON: {} {}\n{}'.format(
        status,
        errorMsg,
        json.dumps(SASRequestBody, indent=4)
    ))
    # print(json.dumps(SASRequestBody, indent=4), status, errorMsg)

    # Log step
    t1 = time.time()
    logSteps.append({
        'step': 'dataExtraction(IN)',
        'time': round((t1 - t0)*1000, 3)
    })
    t0 = t1

    # If error occured on INPUT stage
    if not status:
        logger.error(f'Error occurred while extraction request data: {errorMsg}')
        abort(500)

    # ---------------------------------------------------------------------
    # Call MAS module
    # ---------------------------------------------------------------------
    SASResponse, status, errorMsg = mas.callDecision(
        moduleID,
        SASRequestBody
    )
    logger.trace('Result of callDecision: {} {}\n{}'.format(
        status,
        errorMsg,
        json.dumps(SASResponse, indent=4)
    ))
    # print(json.dumps(SASResponse.get('body'), indent=4),
    #       SASResponse.get('code'), status, errorMsg)

    # Log step
    t1 = time.time()
    logSteps.append({
        'step': 'decision executed',
        'time': round((t1 - t0)*1000, 3)
    })
    t0 = t1

    # If error occurred on SAS stage
    if not status:
        logger.error(f'Error occurred while decision call: {errorMsg}')
        abort(500)

    # ---------------------------------------------------------------------
    # Construct output message
    # ---------------------------------------------------------------------
    if not err:
        finaleResponse, status, errorMsg = mergeData(
            SASResponse.get('body'),
            origRequestBody,
            OUTconfigs
        )
        logger.trace('Result of mergeData: {} {}\n{}'.format(
            status,
            errorMsg,
            json.dumps(finaleResponse, indent=4)
        ))
        # print(json.dumps(finaleResponse, indent=4),
        #       status, errorMsg)

        # If error occurred on OUTPUT stage
        if not status:
            logger.error(f'Error occurred while merging data: {errorMsg}')
            abort(500)

    # Log step
    t1 = time.time()
    logSteps.append({
        'step': 'dataExtraction(OUT)',
        'time': round((t1 - t0)*1000, 3)
    })
    t0 = t1

    # Define responseCode
    if not responseCode:
        if useSASResponseCode:
            responseCode = SASResponse.get('code', dfltSuccessResponseCode)
        else:
            responseCode = dfltSuccessResponseCode

    logger.trace(f'Response code: {responseCode}')

    logMsg = ', '.join(
        '{} in {}ms'.format(key['step'], key['time']) for key in logSteps
    )
    total = round(sum(key['time'] for key in logSteps), 3)
    logger.debug(
        f'Finish processing request No: {requestOrderNum}. '
        f'INFO: {logMsg}. TOTAL: {total}ms.'
    )

    return finaleResponse, responseCode, False, None


# =============================================================================
# =============================================================================
# =============================================================================


# Status page
@bp.route('/')
def index():
    d = {
        'status': {
            'serverReady': mas.serverReady,
            'accessTokenStatus': mas.accessTokenStatus
        }
    }

    logger.debug(d)
    return d, 200


@bp.route(
    '/<string:_rootPath>',
    methods=['GET', 'POST'])
def main(_rootPath):
    """
    Process received data, sends request(s) to MAS
    and provide response according to configuration

    Parameters
    ----------
    _rootPath : str
        Endpoint of the request. Points to the configuration

    Returns
    -------
    object
        Response body
    int
        Response code
    """

    traceId = request.headers.get("Trace-Id")
    g.traceId = traceId
    
    consumerId = request.headers.get("Consumer-Id")
    g.consumerId = consumerId

    logger.debug('STARTED. {} {}'.format(request.method, request.path))
    logger.debug('Trace Id : {}'.format(traceId))
    logger.debug('Consumer Id: {}'.format(consumerId))
    logger.trace(request)
    logger.trace(request.headers)
    logger.trace(request.get_data())

    moduleID = None
    responseCode = None

    # Start stopwatch for logging
    logSteps = []
    t0 = time.time()

    # -------------------------------------------------------------------------
    # Parse URL and get rootPath
    # -------------------------------------------------------------------------

    # Check if requested rootPath is configured
    if _rootPath not in cfgs:
        logger.error(f'No configuration for requested rootPath {_rootPath}')
        abort(500)

    # Get info from cfgs
    method = cfgs[_rootPath]['method']
    argsConvertTypes = cfgs[_rootPath].get('argsConvertTypes', {})
    dfltErrorResponseCode = cfgs[_rootPath]['dfltErrorResponseCode']
    multiRequest = cfgs[_rootPath]['multiRequest']
    multiRequestSettings = cfgs[_rootPath].get('multiRequestSettings', {})
    moduleIdHeader = cfgs[_rootPath]['moduleIdHeader']
    requiredProperties = cfgs[_rootPath]['requiredProperties']

    # Get validator
    validator = validators.get(_rootPath)

    if moduleIdHeader:
        headers = request.headers
        moduleID = headers.get("Module-ID")

    # Method must match to configured
    if request.method != method:
        logger.error('Method must match to configured')
        abort(500)

    # Choose requested or default moduleID
    if moduleID:
        moduleID = moduleID.lower()
        logger.debug(f'moduleID {moduleID} is supplied from headers')
    else:
        if _rootPath in dfltModules:
            moduleID = dfltModules[_rootPath].lower()
            logger.debug(f'Default moduleID {moduleID} is applied')
        else:
            logger.error(f'No default moduleID is configured for '
                         f'requested rootPath {_rootPath}')
            abort(500)

    # -------------------------------------------------------------------------
    # Get request body
    # -------------------------------------------------------------------------

    if method == 'POST':
        # Check for Content-Type
        if request.content_type != 'application/json':
            logger.error(f'"Content-Type" must be "application/json", '
                         f'but received {request.content_type}')
            httpResponseCode = 415
            errBody = createErrorBody(
                'CONTENT_TYPE_INVALID', 
                httpResponseCode, 
                '"Content-Type" must be "application/json"'
            )
            return errBody, httpResponseCode

        # Check for input message
        try:
            root, status, errorMsg = utils.load_json(request.get_data())
            if not status:
                logger.error(f'Request body cannot be loaded: {errorMsg}')
                httpResponseCode = 415
                errBody = createErrorBody(
                    'REQUEST_BODY_INVALID', 
                    httpResponseCode, 
                    'Request body is not JSON'
                )
                return errBody, httpResponseCode
        # Keep it just-in-case, but exclude from coverage
        except Exception as e:  # pragma: no cover
            logger.error(e, exc_info=True)
            httpResponseCode = 415
            errBody = createErrorBody(
                'REQUEST_BODY_INVALID', 
                httpResponseCode, 
                'Request body is not JSON'
            )
            return errBody, httpResponseCode

        # Log step
        t1 = time.time()
        logSteps.append({
            'step': '({} KB) getFile'.format(
                round(request.content_length/1024, 2)
            ),
            'time': round((t1 - t0)*1000, 3)
        })
        t0 = t1

    elif method == 'GET':
        # Get data from URL arguments and add it to dictionary
        root = {}
        for key in request.args:
            if key in argsConvertTypes:
                try:
                    if argsConvertTypes[key] == int:
                        val = int(request.args[key])
                    if argsConvertTypes[key] == float:
                        val = float(request.args[key])
                    if argsConvertTypes[key] in (dict, list):
                        val, status, errorMsg = utils.load_json(
                                                    request.args[key]
                                                )
                        if not status:
                            logger.error(f'Request body for parameter {key} '
                                         f'cannot be loaded: {errorMsg}')
                            httpResponseCode = 415
                            errBody = createErrorBody(
                                'REQUEST_BODY_INVALID', 
                                httpResponseCode, 
                                'Request body cannot be loaded'
                            )
                            return errBody, httpResponseCode
                    logger.debug(f'Type for {key} converted successfully')
                except Exception as e:
                    logger.error(e, exc_info=True)
                    httpResponseCode = 415
                    errBody = createErrorBody(
                        'REQUEST_BODY_INVALID', 
                        httpResponseCode, 
                        'Request body cannot be loaded'
                    )
                    return errBody, httpResponseCode
            else:
                val = request.args[key]

            root[key] = val

        # Log step
        t1 = time.time()
        logSteps.append({
            'step': 'parseArgs',
            'time': round((t1 - t0)*1000, 3)
        })
        t0 = t1

    logger.trace('Retrieved original request message: \n{}'.format(
        json.dumps(root, indent=4)
    ))

    # -------------------------------------------------------------------------
    # Validate input message
    # -------------------------------------------------------------------------
    if validator:
        try:
            validator.validate(root)
        except jsonschema.ValidationError as e:
            logger.error(e, exc_info=True)
            httpResponseCode = 400
            if requiredProperties:
                for reqProp in requiredProperties:
                    if e.message == f"'{reqProp}' is a required property":
                        errBody = createErrorBody(
                            f'{requiredProperties[reqProp]}_MISSING',
                            httpResponseCode,
                            f'{reqProp} is missing'
                        )
                        return errBody, httpResponseCode
                errBody = createErrorBody(
                    'REQUEST_BODY_VALIDATION_FAILED',
                    httpResponseCode,
                    'Request body cannot be validated'
                )
                return errBody, httpResponseCode
            else:
                if re.search(r'is a required property', e.message):
                    errMsg = e.message.split()[0].strip().replace("'", '')
                    errAttrib = re.sub(
                        '((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))', 
                        r'_\1', 
                        errMsg
                    )
                    errBody = createErrorBody(
                        errAttrib.upper()+'_REQUIRED',
                        httpResponseCode,
                        f'{errMsg} is required'
                    )
                    return errBody, httpResponseCode
                    
                if re.search(r'is not of type', e.message):
                    errMsg = e.path.pop()
                    errAttrib = re.sub(
                        '((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))', 
                        r'_\1', 
                        errMsg
                    )
                    errBody = createErrorBody(
                        errAttrib.upper()+'_INVALID',
                        httpResponseCode,
                        f'{errMsg} is invalid'
                    )
                    return errBody, httpResponseCode

                errBody = createErrorBody(
                    'REQUEST_BODY_VALIDATION_FAILED',
                    httpResponseCode,
                    'Request body cannot be validated. Unknown error.'
                )
                return errBody, httpResponseCode

    # Log step
    t1 = time.time()
    logSteps.append({
        'step': 'inputValidation',
        'time': round((t1 - t0)*1000, 3)
    })
    t0 = t1

    # -------------------------------------------------------------------------
    # Prepare input message
    # -------------------------------------------------------------------------
    # Parse input message and transform it to MAS style message according cfgs
    if multiRequest:
        # If multiRequest, request body must be list
        # It is split and processed subsequently
        # Response of earlier entry can be used for the next

        sortSettings = multiRequestSettings.get('sortSettings', {})
        mergeSettings = multiRequestSettings['mergeSettings']
        inputSettings = multiRequestSettings['inputSettings']
        outputSettings = multiRequestSettings['outputSettings']

        if inputSettings:
            root, status, errorMsg = prepMultiBody(root, inputSettings)
            if not status:
                logger.error(f'Array cannot be extracted from request: {errorMsg}')
                abort(500)

        if not isinstance(root, list):
            logger.error('If multiRequest, prepared body must be list')
            httpResponseCode = 400
            errBody = createErrorBody(
                'ARRAY_EXTRACT_ERROR',
                httpResponseCode,
                'Array cannot be extracted according to JQ rule - .[]'
            )
            return errBody, httpResponseCode

        responseList = []
        responses = {}
        # data sorting
        if sortSettings:
            root, status, errorMsg = sortReqEntries(root, sortSettings)
            logger.trace('Result of sorting: {} {}\n{}'.format(
                status,
                errorMsg,
                json.dumps(root, indent=4)
            ))

            # Log step
            t1 = time.time()
            logSteps.append({
                'step': 'Sorting entries',
                'time': round((t1 - t0)*1000, 3)
            })
            t0 = t1

            if not status:
                logger.error(f'Error occurred while sorting: {errorMsg}')
                abort(500)

        # Looping call of the MAS module to process each entry
        for entryNum, entryBody in enumerate(root):
            responseCode = None
            # Merge for entries starting from the 2nd
            if entryNum >= 1:
                logger.debug('Merging response from {} to {} entry'.format(
                    entryNum - 1, entryNum
                ))
                # Get the last response
                prevEntryResponse = responses[entryNum - 1]['body']

                entryBody, status, errorMsg = mergeData(
                    prevEntryResponse,
                    entryBody,
                    mergeSettings
                )
                logger.debug('Result of merge: {} {}'.format(
                    status, errorMsg
                ))

                # If merge is failed, try to embed the result
                # to original body and break the loop
                # If this is also failed, stop the request
                if not status:
                    if errorMsg == 'Source data failed validation':
                        logger.debug(
                            f'Entry No {entryNum-1} was failed (merge). '
                            'Breaking loop'
                        )
                        break
                    else:
                        logger.trace('Result of mergeData (err): {} {}\n{}'.format(
                            status,
                            errorMsg,
                            json.dumps(entryResponse, indent=4)
                        ))
                        abort(500)

                        # print(json.dumps(entryResponse, indent=4),
                        #       status, errorMsg)

                # Log step
                t1 = time.time()
                logSteps.append({
                    'step': f'Req {entryNum}. Merge data',
                    'time': round((t1 - t0)*1000, 3)
                })
                t0 = t1

            r = singleRequest(
                entryBody,
                cfgs[_rootPath],
                moduleID,
                entryNum
            )

            # Log step
            t1 = time.time()
            logSteps.append({
                'step': f'Req {entryNum}. Process',
                'time': round((t1 - t0)*1000, 3)
            })
            t0 = t1

            entryResponse = r[0]
            responseCode = r[1]  # Keep the last until the end
            errorOccured = r[2]
            errBody = r[3]

            logger.debug(
                f'Entry No {entryNum}: '
                f'responseCode {responseCode}, '
                f'errorOccured {errorOccured}, '
                f'errorMsg {errorMsg}'
            )

            responses[entryNum] = {
                'body': entryResponse,
                'code': responseCode,
                'errorOccured': errorOccured
            }
            responseList.append(entryResponse)

        if outputSettings:
            finaleResponse, status, message = prepMultiBody(
                responseList, 
                outputSettings
           )
            if not status:
                logger.error(f'Output data cannot be transformed: {message}')
                abort(500)
        else:
            finaleResponse = responseList

        finaleResponse = json.dumps(finaleResponse)

    else:
        r = singleRequest(root, cfgs[_rootPath], moduleID)

        # Log step
        t1 = time.time()
        logSteps.append({
            'step': f'Req 0. Process',
            'time': round((t1 - t0)*1000, 3)
        })
        t0 = t1

        finaleResponse = r[0] if not r[3] else r[3]
        responseCode = r[1]

    logMsg = ', '.join(
        '{} in {}ms'.format(key['step'], key['time']) for key in logSteps
    )
    total = round(sum(key['time'] for key in logSteps), 3)
    logger.debug(
        f'INFO: {logMsg}. TOTAL: {total}ms.'
    )

    logger.debug('FINISHED. {} {}'.format(request.method, request.path))

    finaleResponse = make_response(finaleResponse)
    finaleResponse.headers['Trace-Id'] = traceId
    finaleResponse.headers['Consumer-Id'] = consumerId
    finaleResponse.headers['Content-Type'] = 'application/json'

    return finaleResponse, responseCode
