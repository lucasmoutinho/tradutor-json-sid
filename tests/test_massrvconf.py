import pytest
from parameterized import parameterized
from mock import patch

import os

from app.lib.utils import loadConfFromEnv

import logging
logger = logging.getLogger('test')

# Testing conf.massrvconf.loadConfFromEnv
# Mock environment variables
class Test_massrvconf():
    @classmethod
    def setup_class(cls):
        cls._environ = dict(os.environ)

    @classmethod
    def teardown_class(cls):
        os.environ.clear()
        os.environ.update(cls._environ)

    def define_test_data():
        test_params = []
        test_params.append([
            'all_env',
            {
                'baseUrl': 'http://your-viya-instance.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'userId': 'dummy',
                'SASPASS': 'pwd',
                'callDecisionTimeoutConnect': '10',
                'callDecisionTimeoutRead': '10',
                'getAccessTokenTimeoutConnect': '10',
                'getAccessTokenTimeoutRead': '10',
                'dfltModules': 'rootPath:moduleId'
            },
            {
                'baseUrl': 'http://your-viya-instance.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'username': 'dummy',
                'password': 'pwd',
                'callDecisionTimeout': (10, 10),
                'getAccessTokenTimeout': (10, 10)
            },
            {'rootPath' : 'moduleId'}
        ])
        test_params.append([
            'no_timeout',
            {
                'baseUrl': 'http://your-viya-instance2.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'userId': 'dummy',
                'SASPASS': 'pwd',
                'dfltModules': 'rootPath:moduleId'
            },
            {
                'baseUrl': 'http://your-viya-instance2.sas.com',
                'oauth_client_id': 'oauth_client_id',
                'oauth_client_secret': 'oauth_client_secret',
                'grant_type': 'password',
                'username': 'dummy',
                'password': 'pwd',
                'callDecisionTimeout': (None, None),
                'getAccessTokenTimeout': (None, None)
            },
            {'rootPath' : 'moduleId'}
        ])

        return test_params

    @parameterized.expand(define_test_data())
    def test_(self, name, environ, exp_massrvconf, exp_moduleID):
        os.environ.clear()
        mock_environ_patcher = patch.dict('src.jde.app.lib.utils.os.environ', environ)
        mock_environ_patcher.start()

        massrvconf, dfltModules = loadConfFromEnv()

        mock_environ_patcher.stop()

        assert massrvconf == exp_massrvconf
        assert dfltModules == exp_moduleID
