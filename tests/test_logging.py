
import pytest
# from parameterized import parameterized
from mock import patch, mock_open

import logging.config
import json
import sys

from app import create_app

import logging
from .loadLogConf import loadLogConf
logger = logging.getLogger('test')


class Test_Logging():

    @classmethod
    def setup_class(cls):
        # Mock appconf
        from tests.data.default_appconf import cfgs
        cls.mock_cfgs_patcher = patch('app.cfgs', new=cfgs)
        cls.mock_cfgs_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_cfgs_patcher.stop()

    def test_debug_logging(self):
        logger.debug(f'Test_Logging - debug')

        environ = {
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
            'dfltModules': ''
        }
        mock_environ_patcher = patch.dict('os.environ', environ)
        mock_environ_patcher.start()

        # Flask production config
        class Config(object):
            JSON_SORT_KEYS = False
            DEBUG = True

        # Start Flask app
        # Mock original logconfig.json with empty configuration
        m = mock_open(
            read_data='{"version": 1, "disable_existing_loggers": false}')

        with patch('app.open', m):
            create_app(Config)

        mock_environ_patcher.stop()

    def test_gunicorn_logging(self):
        logger.debug(f'Test_Logging - gunicorn')

        environ = {
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
            'dfltModules': '',
            'SERVER_SOFTWARE': 'gunicorn'
        }
        mock_environ_patcher = patch.dict('os.environ', environ)
        mock_environ_patcher.start()

        # Configure gunicorn.error logger
        with open('./tests/gunicorn_logconfig.json', 'r') as f:
            log_cfg = json.load(f)
        logging.config.dictConfig(log_cfg)

        # Flask production config
        class Config(object):
            JSON_SORT_KEYS = False

        # Start Flask app
        create_app(Config)

        mock_environ_patcher.stop()

    def teardown_method(self):
        # Re-import app.routes in the next testcases
        # del sys.modules['app.routes']

        loadLogConf(loggingReload=True)
