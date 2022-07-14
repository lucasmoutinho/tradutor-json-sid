from app import create_app
# Config for Flask
from conf.flaskconf import Config
from flask import g


flaskApp = create_app(Config)

# For debugging
if __name__ == "__main__":

    # Checking log levels
    flaskApp.logger.debug('------------ Checking log levels ------------')
    flaskApp.logger.trace('check: trace message')
    flaskApp.logger.debug('check: debug message')
    flaskApp.logger.info('check: info message')
    flaskApp.logger.warning('check: warn message')
    flaskApp.logger.error('check: error message')
    flaskApp.logger.critical('check: critical message')
    flaskApp.logger.debug('------------ Checking log levels ------------')

    flaskApp.run(host="0.0.0.0", port=8000, debug=True)

