import pytest
from parameterized import parameterized
from mock import Mock, patch

import os
import sys

from app.lib.masserver import MASServerClass

import logging
logger = logging.getLogger('test')


# Testing MASServerClass.__init__
class Test_init():

    def define_test_data():
        from tests.data.test_masserver.cases_init import testcases

        test_params = []
        for tc in testcases:
            test_params.append([tc['name'], tc['massrvconf'], tc['errorMsg']])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(self, name, massrvconf, exp_errorMsg):

        mas = MASServerClass(massrvconf)
        # print(mas.errorMsg)

        assert mas.serverReady == False
        assert mas.errorMsg == exp_errorMsg

    def test_init_token_failed(self):

        mock_post_patcher = patch.object(MASServerClass, 'getAccessToken')
        mock_post = mock_post_patcher.start()

        mock_post.side_effect = Exception

        massrvconf = {
            'baseUrl': 'http://your-viya-instance.sas.com',
            'oauth_client_id': 'oauth_client_id',
            'oauth_client_secret': 'oauth_client_secret',
            'grant_type': 'password',
            'username': 'dummy',
            'password': 'pwd',
            'callDecisionTimeout': (10, 10),
            'getAccessTokenTimeout': (10, 10)
        }
        mas = MASServerClass(massrvconf)

        mock_post_patcher.stop()

        assert mas.serverReady == True
        assert mas.accessTokenStatus == 'FAILED'


# Testing MASServerClass.__post
# Patch post method of requests.Session

class Test_post():
    @classmethod
    def setup_class(cls):
        cls.mock_post_patcher = patch(
            'app.lib.masserver.requests.Session.post', autospec=True)
        cls.mock_post = cls.mock_post_patcher.start()

        # Ignore results of initial token retrieval, server should be ready
        massrvconf = {
            'baseUrl': 'http://your-viya-instance.sas.com',
            'oauth_client_id': 'oauth_client_id',
            'oauth_client_secret': 'oauth_client_secret',
            'grant_type': 'password',
            'username': 'dummy',
            'password': 'pwd',
            'callDecisionTimeout': (10, 10),
            'getAccessTokenTimeout': (10, 10)
        }
        cls.mas = MASServerClass(massrvconf)

    @classmethod
    def teardown_class(cls):
        cls.mock_post_patcher.stop()

    def define_test_data():
        from tests.data.test_masserver.cases_post import testcases

        test_params = []
        for tc in testcases:
            test_params.append([
                tc['name'],
                tc['status_code'],
                tc['text'],
                tc['json_return_value'],
                tc['side_effect'],
                tc['exp_response'],
                tc['exp_badCredentials'],
                tc['exp_errorMsg'],
            ])
        print('test_params')

        return test_params

    @parameterized.expand(define_test_data())
    def test_(
        self, name, status_code, text, json_return_value, side_effect,
        exp_response, exp_badCredentials, exp_errorMsg
    ):
        # def test_none():
        self.mock_post.return_value.status_code = status_code
        self.mock_post.return_value.text = text
        self.mock_post.return_value.json.return_value = json_return_value
        self.mock_post.return_value.raise_for_status = Mock(
            side_effect=side_effect)

        # Provide any params
        myUrl = ''
        myHeaders = {}
        myParams = {}
        myData = ''
        myTimeout = 10
        response, badCredentials, errorMsg = self.mas._MASServerClass__post(
            myUrl, myHeaders, myParams, myData, myTimeout
        )

        assert response == exp_response
        assert badCredentials == exp_badCredentials
        assert errorMsg == exp_errorMsg


# Testing MASServerClass.getAccessToken
# Patch MASServerClass.__post, replace it by function
class Test_getAccessToken():
    @classmethod
    def setup_class(cls):

        # Make initial token retrieval successful
        def post_new(*args, **kwargs):
            # print(kwargs['myUrl'])
            response = {
                'code': 200,
                'body': {
                    'access_token': 'init_access_token',
                    'refresh_token': 'init_refresh_token'
                }
            }
            return response, False, None

        mock_post_patcher = patch.object(
            MASServerClass,
            '_MASServerClass__post',
            new=post_new
        )
        mock_post_patcher.start()

        massrvconf = {
            'baseUrl': 'http://your-viya-instance.sas.com',
            'oauth_client_id': 'oauth_client_id',
            'oauth_client_secret': 'oauth_client_secret',
            'grant_type': 'password',
            'username': 'dummy',
            'password': 'pwd',
            'callDecisionTimeout': (10, 10),
            'getAccessTokenTimeout': (10, 10)
        }
        cls.mas = MASServerClass(massrvconf)

        mock_post_patcher.stop()

    @classmethod
    def teardown_class(cls):
        pass

    def define_test_data():
        from tests.data.test_masserver.cases_getAccessToken import testcases

        test_params = []
        for tc in testcases:
            test_params.append([
                tc['name'],
                tc['post_new'],
                tc['authConf'],
                tc['exp_result'],
                tc['exp_accessTokenStatus'],
                tc['exp_accessToken'],
                tc['exp_refreshToken']
            ])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(
        self, name, post_new, authConf, exp_result,
        exp_accessTokenStatus, exp_accessToken, exp_refreshToken
    ):

        mock_post_patcher = patch.object(
            MASServerClass, '_MASServerClass__post', new=post_new)
        mock_post_patcher.start()

        result = self.mas.getAccessToken(authConf)

        mock_post_patcher.stop()

        assert result == exp_result
        assert self.mas.accessTokenStatus == exp_accessTokenStatus
        assert self.mas._MASServerClass__accessToken == exp_accessToken
        assert self.mas._MASServerClass__refreshToken == exp_refreshToken

    def test_get_when_not_ready(self):

        massrvconf = {
            'baseUrl': 'http://your-viya-instance.sas.com',
            'oauth_client_id': 'oauth_client_id',
            'oauth_client_secret': 'oauth_client_secret',
            # 'grant_type': 'password',
            'username': 'dummy',
            'password': 'pwd',
            'callDecisionTimeout': (10, 10),
            'getAccessTokenTimeout': (10, 10)
        }
        mas = MASServerClass(massrvconf)

        result = mas.getAccessToken()

        assert result == False
        assert mas.accessTokenStatus == None
        assert mas._MASServerClass__accessToken == None
        assert mas._MASServerClass__refreshToken == None


# Testing MASServerClass.callDecision
# Patch MASServerClass.__post, replace it by function
class Test_callDecision():
    @classmethod
    def setup_class(cls):

        # Make initial token retrieval successful
        def post_new(*args, **kwargs):
            # print(kwargs['myUrl'])
            response = {
                'code': 200,
                'body': {
                    'access_token': 'init_access_token',
                    'refresh_token': 'init_refresh_token'
                }
            }
            return response, False, None

        mock_post_patcher = patch.object(
            MASServerClass, '_MASServerClass__post', new=post_new)
        mock_post_patcher.start()

        cls.massrvconf = {
            'baseUrl': 'http://your-viya-instance.sas.com',
            'oauth_client_id': 'oauth_client_id',
            'oauth_client_secret': 'oauth_client_secret',
            'grant_type': 'password',
            'username': 'dummy',
            'password': 'pwd',
            'callDecisionTimeout': (10, 10),
            'getAccessTokenTimeout': (10, 10)
        }
        cls.mas = MASServerClass(cls.massrvconf)

        mock_post_patcher.stop()

    @classmethod
    def teardown_class(cls):
        pass

    def define_test_data():
        from tests.data.test_masserver.cases_callDecision import testcases

        test_params = []
        for tc in testcases:
            test_params.append([
                tc['name'],
                tc['requestBody'],
                tc['callDecisionTimeout'],
                tc['post_new'],
                tc['getAccessToken_return_value'],
                tc['exp_SASResponse'],
                tc['exp_status'],
                tc['exp_errorMsg']
            ])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(
        self, name, requestBody, callDecisionTimeout, post_new,
        getAccessToken_return_value, exp_SASResponse, exp_status, exp_errorMsg
    ):

        mock_post_patcher = patch.object(
            MASServerClass, '_MASServerClass__post', new=post_new)
        mock_post_patcher.start()

        moduleID = 'moduleID'
        SASResponse, status, errorMsg = self.mas.callDecision(
            moduleID=moduleID,
            requestBody=requestBody,
            callDecisionTimeout=callDecisionTimeout
        )

        mock_post_patcher.stop()

        assert SASResponse == exp_SASResponse
        assert status == exp_status
        assert errorMsg == exp_errorMsg

    def test_when_not_ready(self):

        massrvconf = {
            'baseUrl': 'http://your-viya-instance.sas.com',
            'oauth_client_id': 'oauth_client_id',
            'oauth_client_secret': 'oauth_client_secret',
            # 'grant_type': 'password',
            'username': 'dummy',
            'password': 'pwd',
            'callDecisionTimeout': (10, 10),
            'getAccessTokenTimeout': (10, 10)
        }
        mas = MASServerClass(massrvconf)

        # input params do not matter
        SASResponse, status, errorMsg = mas.callDecision('', '')

        assert SASResponse == {'code': 500, 'body': None}
        assert status == False
        assert errorMsg == 'Server instance is not ready to serve requests'

    def test_init_token_failed(self):

        mock_post_patcher = patch.object(MASServerClass, 'getAccessToken')
        mock_post = mock_post_patcher.start()

        mock_post.side_effect = Exception

        mas = MASServerClass(self.massrvconf)

        mock_post_patcher.stop()

        # input params do not matter
        SASResponse, status, errorMsg = mas.callDecision('', '')

        assert SASResponse == {'code': 500, 'body': None}
        assert status == False
        assert errorMsg == 'Access token status is FAILED. Check logs'
