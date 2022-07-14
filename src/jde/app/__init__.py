import errno
import json
import logging
import logging.config
import os
import sys

from app.lib.utils import checkConf, loadConfFromEnv
from conf.appconf import cfgs
from flask import Flask, g

from jsonschema import Draft7Validator


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVELV_NUM):  # pragma: no cover
        self._log(TRACE_LEVELV_NUM, message, args, **kws)  # pragma: no cover


# Add TRACE logging level
# Before loading logging configuration
TRACE_LEVELV_NUM = 5
logging.addLevelName(TRACE_LEVELV_NUM, 'TRACE')
logging.Logger.trace = trace


def create_app(config_class):
    flaskApp = Flask(__name__)
    flaskApp.config.from_object(config_class)
    flaskApp.app_context().push()

    # Configure logger
    if flaskApp.debug:
        with open('./logconfig.json', 'r') as f:
            log_cfg = json.load(f)
        logging.config.dictConfig(log_cfg)
    # If production - get logger configuration from WSGI
    elif not flaskApp.debug and not flaskApp.testing:
        is_gunicorn = 'gunicorn' in os.environ.get('SERVER_SOFTWARE', '')
        if is_gunicorn:
            wsgi_logger = logging.getLogger('gunicorn.error')
            flaskApp.logger.handlers = wsgi_logger.handlers
            flaskApp.logger.setLevel(wsgi_logger.level)
            flaskApp.logger.propagate = False

    # Load configuration for MAS server and default moduleID
    massrvconf, dfltModules = loadConfFromEnv()
    
    try:
        flaskApp.logger.trace('Loaded configuration:\n{}'.format(
            json.dumps(cfgs, indent=4)
        ))
    except Exception:
        pass
    # try:
        # Password is here!!!
        # flaskApp.logger.trace('MAS Server Configuration:\n{}'.format(
        #     json.dumps(massrvconf, indent=4)
        # ))
    # except Exception:
    #     pass
    flaskApp.logger.trace('Default MAS modules:\n{}'.format(
        json.dumps(dfltModules, indent=4)
    ))

    # Check for proper configuration
    confIsOK = checkConf(cfgs, dfltModules)

    if not confIsOK:
        flaskApp.logger.error('Stopping server due to errors...')
        print('Wrong configuration. Exiting...')
        sys.exit(errno.EINTR)

    # Initialize validators
    validators = {}
    for key in cfgs:
        jsonschemaFile = cfgs[key].get('jsonschemaFile')
        if jsonschemaFile:
            try:
                with open(f'./conf/jsonschema/{jsonschemaFile}', 'r') as f:
                    schema = json.load(f)
                Draft7Validator.check_schema(schema)
                validator = Draft7Validator(schema)
                validators[key] = validator
                flaskApp.logger.debug(
                    f'Validator is loaded successfully for config {key}')
            except Exception:
                flaskApp.logger.error(
                    f'Validator for {key} cannot be created', exc_info=True)
                flaskApp.logger.error('Stopping server due to errors...')
                sys.exit(errno.EINTR)

    # Initialize MAS instance
    from app.lib.masserver import MASServerClass
    mas = MASServerClass(massrvconf)
    flaskApp.logger.trace(
        'MAS Server Instance status.'
        f' serverReady: {mas.serverReady}'
        f', accessTokenStatus: {mas.accessTokenStatus}'
    )

    # If MAS instance was not initialized properly
    # If gunicorn configured as preload_app = True
    # sys.exit stops Gunicorn server
    if not mas.serverReady:
        flaskApp.logger.error(
            'MAS instance was not initialized properly. '
            'Stopping server due to errors...')
        sys.exit(errno.EINTR)

    # Setting Flask global variables
    g.mas = mas
    g.dfltModules = dfltModules
    g.cfgs = cfgs
    g.validators = validators

    from app.routes import bp
    flaskApp.register_blueprint(bp)

    @flaskApp.errorhandler(500)
    def handle_500(e):
        response = e.get_response()

        traceId = getattr(g, 'traceId', None)
        consumerId = getattr(g, 'consumerId', None)
        
        err = {}
        err['code'] = 'INTERNAL_SERVER_ERROR'
        err['status'] = 500
        err['message'] = 'Internal server error occurred'
        err['traceId'] = getattr(g, 'traceId', None)
        errBody = {
            'errors': [
                err
            ]
        }
        response.data = json.dumps(errBody)
        response.content_type = "application/json" 
        response.headers['Trace-Id'] = traceId
        response.headers['Consumer-Id'] = consumerId  

        return response, 500

    return flaskApp
