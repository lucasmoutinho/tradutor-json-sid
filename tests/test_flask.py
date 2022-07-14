import pytest
from parameterized import parameterized
from mock import patch

from app import create_app
import os
import sys
import json
import pyjq

from pathlib import Path
from functools import partial

import logging
logger = logging.getLogger('test')


# Mock open function
def mocked_open(fn, *args, **kwargs):
    fn = fn.replace('./conf/jsonschema', './tests/data/test_flask/jsonschema')
    return open(fn, *args, **kwargs)


class testFlaskConfig(object):
    JSON_SORT_KEYS = False
    TESTING = True


class Test_Flask():
    @classmethod
    def setup_class(cls):
        # Standard
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

    @classmethod
    def teardown_class(cls):
        pass

    def define_test_data():
        from tests.data.test_flask.flask_cases import testcases
        from tests.data.test_flask.flask_cases_multirequest \
            import testcases as testcases_multireq
        test_params = []

        for tc in testcases:
            test_params.append([
                tc['name'],
                tc['cfgs'],
                tc['dfltModules'],
                tc['endpoint'],
                tc['method'],
                tc['request'],
                tc['headers'],
                tc['mock_callDecision_return'],
                tc['exp_status_code'],
                tc['exp_json'],
                tc['expected'],
                tc['initFails']
            ])
            
        for tc in testcases_multireq:
            test_params.append([
                tc['name'],
                tc['cfgs'],
                tc['dfltModules'],
                tc['endpoint'],
                tc['method'],
                tc['request'],
                tc['headers'],
                tc['mock_callDecision_return'],
                tc['exp_status_code'],
                tc['exp_json'],
                tc['expected'],
                tc['initFails']
            ])
        return test_params

    def setup_method(self):
        # Re-import app.routes in the next testcases
        try:
            del sys.modules['app.routes']
        except:
            pass
        try:
            del sys.modules['app.cfgs']
        except:
            pass

    def teardown_method(self):
        pass

    @parameterized.expand(define_test_data())
    def test_(
        self,
        name,
        cfgs,
        dfltModules,
        endpoint,
        method,
        request,
        headers,
        mock_callDecision_return,
        exp_status_code,
        exp_json,
        expected,
        initFails
    ):
        
        logger.debug(f'Test_Flask - {name}')

        mock_loadConfFromEnv_patcher = patch('app.loadConfFromEnv')
        mock_loadConfFromEnv = mock_loadConfFromEnv_patcher.start()
        mock_loadConfFromEnv.return_value = (self.massrvconf, dfltModules)

        mock_open_patcher = patch('app.open', new=mocked_open)
        mock_open_patcher.start()

        # Mock appconf
        mock_cfgs_patcher = patch('app.cfgs', new=cfgs)
        mock_cfgs_patcher.start()

        if initFails:

            # Start Flask app
            with pytest.raises(SystemExit):
                app = create_app(testFlaskConfig)

            mock_cfgs_patcher.stop()
            mock_open_patcher.stop()
            mock_loadConfFromEnv_patcher.stop()
        else:
            # Mock it
            # Patch MASServerClass
            from app.lib.masserver import MASServerClass
            # No problems with token
            mock_getAccessToken_patcher = patch.object(MASServerClass, 'getAccessToken')
            mock_getAccessToken_patcher.start()
            mock_accessTokenStatus_patcher = patch.object(MASServerClass, 'accessTokenStatus', new='OK')
            mock_accessTokenStatus_patcher.start()
            # Mock SASResponse
            mock_callDecision_patcher = patch.object(MASServerClass, 'callDecision')
            mock_callDecision = mock_callDecision_patcher.start()
            mock_callDecision.return_value = mock_callDecision_return

            # Start Flask app
            app = create_app(testFlaskConfig)

            # # Mock trace ID
            # mock_traceId_patcher = patch('app.routes.flask.g.get("Trace-Id")', return_value='testId')
            # mock_traceId_patcher.start()

            # Test!
            with app.test_client() as client:
                if method == 'POST':
                    rv = client.post('/'+endpoint, headers=headers, data=request)
                elif method == 'GET':
                    rv = client.get('/'+endpoint+request, headers=headers)
            # print(rv.data)

            # Stopping patchers
            mock_cfgs_patcher.stop()
            mock_callDecision_patcher.stop()
            mock_accessTokenStatus_patcher.stop()
            mock_getAccessToken_patcher.stop()
            mock_open_patcher.stop()
            mock_loadConfFromEnv_patcher.stop()
            # mock_traceId_patcher.stop()

            assert rv.status_code == exp_status_code
            # Compare as string or dict
            if exp_json:
                assert json.loads(rv.data.decode('UTF-8')) == json.loads(expected)
            else:
                assert rv.data.decode('UTF-8') == expected

    # Ignore that token cannot be retrieved
    # Test only status page
    def test_status_page(self):
        
        logger.debug('Test_Flask - test_status_page')

        dfltModules = {}
        mock_loadConfFromEnv_patcher = patch('app.loadConfFromEnv')
        mock_loadConfFromEnv = mock_loadConfFromEnv_patcher.start()
        mock_loadConfFromEnv.return_value = (self.massrvconf, dfltModules)

        # Mock appconf
        from tests.data.default_appconf import cfgs
        cfg = cfgs['test-root-path']
        cfg['INconfigs'][0]['rule'] = pyjq.compile('')
        cfg['OUTconfigs']['params_cfg'][0]['extractRule'] = pyjq.compile('')
        cfg['OUTconfigs']['params_cfg'][0]['transformRule'] = pyjq.compile('')
        mock_cfgs_patcher = patch('app.cfgs', new=cfgs)
        mock_cfgs_patcher.start()

        # Start Flask app
        app = create_app(testFlaskConfig)

        # Test!
        with app.test_client() as client:
            rv = client.get('/')

        mock_cfgs_patcher.stop()
        mock_loadConfFromEnv_patcher.stop()

        expected = {
            'status': {
                'serverReady': True,
                'accessTokenStatus': 'FAILED'
            }
        }
        assert json.loads(rv.data.decode('UTF-8')) == expected
        assert rv.status_code == 200

    # MAS server initialization failed
    def test_servernotready(self):
        
        logger.debug('Test_Flask - test_servernotready')

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
        dfltModules = {}
        mock_loadConfFromEnv_patcher = patch('app.loadConfFromEnv')
        mock_loadConfFromEnv = mock_loadConfFromEnv_patcher.start()
        mock_loadConfFromEnv.return_value = (massrvconf, dfltModules)

        # Mock appconf
        from tests.data.default_appconf import cfgs
        cfgs['test-root-path']['INconfigs'][0]['rule'] = pyjq.compile('')
        mock_cfgs_patcher = patch('app.cfgs', new=cfgs)
        mock_cfgs_patcher.start()

        with pytest.raises(SystemExit):
            app = create_app(testFlaskConfig)

        mock_cfgs_patcher.stop()
        mock_loadConfFromEnv_patcher.stop()

    def test_multipleErrorBody(self):
        from app.routes import createErrorBody

        code = 'CODE_ERROR'
        status = 200
        message = 'Error message'
        errBody = {"errors": [{"Error": "Test"}]}
        errBody = createErrorBody(code, status, message, None, errBody)
        expected = {
            "errors": [
                {
                    "Error": "Test"
                }, 
                {
                    "code": "CODE_ERROR", 
                    "status": 200, 
                    "message": "Error message", 
                    "traceId": None
                }
            ]
        }
        assert errBody == expected
