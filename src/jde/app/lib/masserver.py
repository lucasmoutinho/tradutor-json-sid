import base64
import requests
import time
import json
import re

import logging
logger = logging.getLogger(__name__)


class CustomError(Exception):
    # Constructor method
    def __init__(self, value):
        self.value = value

    # __str__ display function
    def __str__(self):
        return(repr(self.value))


class MASServerClass:
    """Class for MAS server instance.
    Initialization includes checks for configuration and initial token retrieval

    Parameters
    ----------
    srvconf : dict
        Dict with server configuration. Keys:
            baseUrl : string
                URL of MAS server. Obligatory
            oauth_client_id : string
                OAUTH client id. Obligatory
            oauth_client_secret : string
                OAUTH client secret. Obligatory
            grant_type : string
                type of initial token retrieval. Obligatory
                Can be 'authorization_code', 'password', 'refresh_token'
            code : string
                Authorization code. grant_type='authorization_code' is required
            username : string
                Username. grant_type='password' is required
            password : string
                Password. grant_type='password' is required
            refresh_token : string
                Valid refresh token. grant_type='refresh_token' is required
            callDecisionTimeout : float/tuple
                Timeout for POST /microanalyticScore/modules
                Can be provided as one number (in seconds)
                or tuple with two numbers (connectionTimeout, readTimeout)
            getAccessTokenTimeout : float/tuple
                Timeout for POST /SASLogon/oauth/token
                Can be provided as one number (in seconds)
                or tuple with two numbers (connectionTimeout, readTimeout)

    Attributes
    ----------
    serverReady : boolean
        Indicator of server state.
    errorMsg : string
        Error message after initialization
    accessTokenStatus : string
        Status of token. 'OK', 'FAILED', None
    baseUrl : string
    oauth_client_id : string
    oauth_client_secret : string
    callDecisionTimeout : float/tuple
    getAccessTokenTimeout : float/tuple
    __authConf : dict
        initial authentication configuration
    __sess : requests.session
        requests.session object for REST calls
    __accessToken : string
        Access token
    __refreshToken : string
        Refresh token

    """

    serverReady = False
    errorMsg = None
    accessTokenStatus = None
    baseUrl = None
    oauth_client_id = None
    oauth_client_secret = None
    callDecisionTimeout = None
    getAccessTokenTimeout = None

    __authConf = {}
    __accessToken = None
    __refreshToken = None
    # Create a connection session.
    __sess = requests.Session()

    def __init__(self, srvconf):
        try:
            
            # Check for srvconf
            if not srvconf:
                raise CustomError('No server configuration provided')
            if type(srvconf) != dict:
                raise CustomError('Provided server configuration is not dictionary')

            # Obligatory variables
            for key in ['baseUrl',
                        'oauth_client_id']:
                if not srvconf.get(key):
                    raise CustomError(f'>> {key} << is missing in server configuration')
            self.baseUrl = srvconf.get('baseUrl')
            self.oauth_client_id = srvconf.get('oauth_client_id')
            self.oauth_client_secret = srvconf.get('oauth_client_secret')  # can be empty

            # Auth info for initial token retrieval
            self.__authConf = {}
            grant_type = srvconf.get('grant_type', '')
            if grant_type not in ('authorization_code', 'password', 'refresh_token'):
                raise CustomError('grant_type >> {} << is not permitted'.format(grant_type))

            self.__authConf['grant_type'] = grant_type

            authVars = []
            if self.__authConf['grant_type'] == 'authorization_code':
                authVars.extend(['code'])
            elif self.__authConf['grant_type'] == 'password':
                authVars.extend(['username', 'password'])
            elif self.__authConf['grant_type'] == 'refresh_token':
                authVars.extend(['refresh_token'])

            for key in authVars:
                if not srvconf.get(key):
                    raise CustomError('>> {} << is missing in server configuration (required for grant_type {})'.format(key, self.__authConf['grant_type']))
                self.__authConf[key] = srvconf.get(key)

            # Timeouts
            self.callDecisionTimeout = srvconf.get('callDecisionTimeout')
            self.getAccessTokenTimeout = srvconf.get('getAccessTokenTimeout')

            self.serverReady = True     # Server is ready
            logger.info('Server instance initialization is successful')

        except Exception as e:
            self.serverReady = False
            self.errorMsg = e.value
            logger.error(f'Error occured during server instance initialization: {e}', exc_info=True)
            logger.error('Server instance initialization is failed')
            return None

        # Initial token retrieval
        try:
            self.getAccessToken()
        except Exception as e:
            self.accessTokenStatus = 'FAILED'
            logger.error(f'Error occured during initial token retrieval: {e}', exc_info=True)
            return None

    def __post(self, myUrl, myHeaders, myParams, myData, myTimeout):
        """Define the POST function. This function converts the request body into
        a JSON object, defines the request headers, posts the request, and
        returns the response.

        Parameters
        ----------
        myUrl : string
            Endpoint of some Viya REST API
        myHeaders : dict
            Headers for POST request
        myParams : dict
            Params for POST request
        myData : string
            Request body
        myTimeout : float/tuple
            Timeout. Can be provided as one number (in seconds)
            or tuple with two numbers (connectionTimeout, readTimeout)

        Returns
        -------
        dict
            code : int
                Status code of SAS response.
            body : dict
                Response from SAS.
        boolean
            True if SAS cannot authenticate based on provided credentials. Otherwise False
        string
            Short error description.
        """

        logger.debug('Sending POST request to SAS...')
        response = {'code': None, 'body': None}

        # Post the request.
        try:
            timings0 = time.time()
            SASresponse = self.__sess.post(
                myUrl,
                data=myData,
                params=myParams,
                headers=myHeaders,
                timeout=myTimeout
            )
            timings1 = time.time()
            logger.debug('SAS response status code: {}. Time: {}ms'.format(
                SASresponse.status_code,
                round((timings1 - timings0)*1000, 3))
            )
            timings0 = timings1

            SASresponse.raise_for_status()
            jResponse = SASresponse.json()
        except requests.Timeout as e:
            e = re.sub(r'password=\w+', 'password=XXXXXX', str(e))
            logger.error(f'Request to SAS failed with timeout. Details: \n{e}')
            response['code'] = 408
            return response, False, 'Timeout'
        except requests.exceptions.ConnectionError as e:
            logger.error('Connection to SAS cannot be established')
            e = re.sub(r'password=\w+', 'password=XXXXXX', str(e))
            logger.debug(f'Details: {e}')
            return response, False, 'ConnectionError'
        except requests.HTTPError:
            logger.error(f'Request to SAS was unsuccessful. Response text: \n{SASresponse.text}')
            response['code'] = SASresponse.status_code
            if SASresponse.status_code == 401:
                return response, True, 'Check your credentials and restart'
            else:
                return response, False, 'HTTPError'
        except Exception as e:
            logger.error(f'Request to SAS failed with exception: \n{e}', exc_info=True)
            return response, False, 'Unknown'

        response['code'] = SASresponse.status_code
        response['body'] = jResponse
        return response, False, None

    def getAccessToken(self, authConf=None):
        """Get access token for Viya authentication
        The GETACCESSTOKEN function requests an access token using the SAS Logon
        OAuth API. The response contains a field named access_token that contains
        the value of the token that you use for subsequent API requests.

        Make POST request to Viya
        https://developer.sas.com/apis/rest/Topics/#authentication-and-access-tokens

        Parameters
        ----------
        authConf : dict
            Authentication configuration

        Returns
        -------
        boolean
            True for success, False if failed

        """
        logger.info('Retrieving access token...')
        # print(self.accessTokenStatus)
        if not self.serverReady:
            logger.error('Server instance is not ready to serve requests')
            return False

        # URL and headers according to documentation
        requestUrl = f'{self.baseUrl}/SASLogon/oauth/token'
        # Encode the value of the client ID.
        oauth_client_id_secret = f'{self.oauth_client_id}:{self.oauth_client_secret}'
        tokenCredentials = base64.b64encode(oauth_client_id_secret.encode('ascii')).decode('ascii')
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Basic {tokenCredentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # auth info
        # if authConf is not overrided and refresh token is already retrieved, use it
        # it is much faster
        params = {}
        refreshTokenUsed = False
        if not authConf and self.__refreshToken:
            params['grant_type'] = 'refresh_token'
            params['refresh_token'] = self.__refreshToken
            refreshTokenUsed = True
            logger.info('Use previously retrieved refresh token')
        else:
            if not authConf:
                authConf = self.__authConf
                logger.info('Use initial authConf')
            else:
                logger.info('Use overrided authConf')

            params['grant_type'] = authConf.get('grant_type')
            if params['grant_type'] == 'authorization_code':
                params['code'] = authConf.get('code')
            elif params['grant_type'] == 'password':
                params['username'] = authConf.get('username')
                params['password'] = authConf.get('password')
            elif params['grant_type'] == 'refresh_token':
                params['refresh_token'] = authConf.get('refresh_token')

        response, badCredentials, errorMsg = self.__post(
            myUrl=requestUrl,
            myHeaders=headers,
            myParams=params,
            myData=None,
            myTimeout=self.getAccessTokenTimeout
        )

        if errorMsg:
            # Case: refreshToken, previously retrieved, is expired
            # authConf is not overrided
            # initial grant_type is password
            if badCredentials \
                    and refreshTokenUsed \
                    and self.__authConf.get('grant_type') == 'password':
                logger.info('Refresh token is expired. Getting new one with password authentication...')

                params = {}
                params['grant_type'] = self.__authConf.get('grant_type')
                params['username'] = self.__authConf.get('username')
                params['password'] = self.__authConf.get('password')

                response, badCredentials, errorMsg = self.__post(
                    myUrl=requestUrl,
                    myHeaders=headers,
                    myParams=params,
                    myData=None,
                    myTimeout=self.getAccessTokenTimeout
                )

            if errorMsg:
                logger.error(f'Token cannot be obtained. Error: {errorMsg}')
                self.accessTokenStatus = 'FAILED'
                self.__accessToken = None
                self.__refreshToken = None
                return False

        self.__accessToken = response['body'].get('access_token')
        self.__refreshToken = response['body'].get('refresh_token')
        if not self.__accessToken:
            self.accessTokenStatus = 'FAILED'
            self.__accessToken = None
            self.__refreshToken = None
            return False

        self.accessTokenStatus = 'OK'
        logger.info('Identity checked')
        return True

    def callDecision(self, moduleID, requestBody, callDecisionTimeout=None):
        """Call SID decision published on MAS
        https://developer.sas.com/apis/rest/DecisionManagement/#execute-a-step

        Parameters
        ----------
        moduleID : string
            Name of MAS module for URL (lowcase requires)
        requestBody : any
            Body of POST message
            https://developer.sas.com/apis/rest/DecisionManagement/#schemastepinput
        callDecisionTimeout : float/tuple
            Timeout. Can be provided as one number (in seconds)
            or tuple with two numbers (connectionTimeout, readTimeout)

        Returns
        -------
        dict
            code : int
                Status code of SAS response.
            body : dict
                Response from SID decision published on MAS
                In case of successful call - https://developer.sas.com/apis/rest/DecisionManagement/#schemastepoutput
        boolean
            True for success, False if failed
        string
            Short error description.
        """

        logger.debug(f'Calling MAS module {moduleID}...')

        if not self.serverReady:
            logger.error('Server instance is not ready to serve requests')
            return {'code': 500, 'body': None}, False, 'Server instance is not ready to serve requests'
        if self.accessTokenStatus == 'FAILED':
            logger.error('Access token is failed. Check logs')
            return {'code': 500, 'body': None}, False, 'Access token status is FAILED. Check logs'

        # Define the content and accept types for the request header.
        headers = {
            'Accept': 'application/vnd.sas.microanalytic.module.step.output+json',
            'Authorization': f'bearer {self.__accessToken}',
            'Content-Type': 'application/vnd.sas.microanalytic.module.step.input+json'
        }

        # Define the request URL.
        requestUrl = '{}/microanalyticScore/modules/{}/steps/execute'.format(
            self.baseUrl,
            moduleID
        )

        # Override default timeout
        if not callDecisionTimeout:
            callDecisionTimeout = self.callDecisionTimeout

        if type(requestBody) in (dict, list):
            requestBodyStr = json.dumps(requestBody)
        else:
            requestBodyStr = str(requestBody)

        # Execute the decision.
        response, badCredentials, errorMsg = self.__post(
            myUrl=requestUrl,
            myHeaders=headers,
            myParams=None,
            myData=requestBodyStr,
            myTimeout=callDecisionTimeout  # TBD. To configure
        )

        # If refresh token required, refresh it and try once again
        if badCredentials:
            logger.info('Some problem with token, refresh it and try again')

            # If getAccessToken was failed, no need to continue
            if not self.getAccessToken():
                return response, False, errorMsg

            # Execute the decision one more time with new headers
            headers['Authorization'] = f'bearer {self.__accessToken}'
            response, badCredentials, errorMsg = self.__post(
                myUrl=requestUrl,
                myHeaders=headers,
                myParams=None,
                myData=requestBodyStr,
                myTimeout=callDecisionTimeout
            )
        elif not response.get('code') or response.get('code') != 201:
            return response, False, errorMsg

        return response, True, None

    def __del__(self):
        try:
            self.__sess.close()
        # Keep it just-in-case, but exclude from coverage
        except Exception:  # pragma: no cover
            pass
