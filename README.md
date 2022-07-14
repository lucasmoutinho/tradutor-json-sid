# JSON Data Extractor - JDE (draft name)

This application is web-server that stands between any calling system and MicroAnalyticService (MAS) microservice of SAS Viya. It serves as reverse proxy. Direct your calling system to this application instead of Viya.  

What exactly it does:

1. receives requests from calling system via REST API
1. extracts data from the request body
1. converts it to SAS style
1. calls module published on MAS (decision, ruleset, model, custom module, etc.) via SAS REST API
1. extracts data from SAS response
1. transforms it to needed format/structure (and even merge it with original request if needed)
1. replies back to calling system using created response message

SAS provides its own REST API, but JDE is useful in the next cases:

* flatten multi-nested structures into SAS datagrids
* process data that is more than 10485760 symbols (~10MB)
    > SAS datagrid format requires much less size for the same data in comparison with key-value pair

Technologies:

* [Flask](https://palletsprojects.com/p/flask/) app
  * lightweight WSGI web application framework
  * enough functionality, well-documented, large community

* [Gunicorn](https://gunicorn.org/) is used as WSGI
  * “Flask’s built-in server is not suitable for production” ([source](https://flask.palletsprojects.com/en/1.1.x/deploying/))
  * Python WSGI HTTP Server for UNIX, pre-fork worker model

* Adopted to be run in [Docker](https://docs.docker.com)
  * Resolves dependencies
  * Easy to deploy

Python modules for JSON processing:

* [jq](https://pypi.org/project/jq/) - is a Python bindings for [jq](http://stedolan.github.io/jq/).
  * command-line JSON processor
  * provides ability to make very flexible solution
  * Very useful tool for commands' development - <https://jqplay.org/>

> For the full list of dependencies see ***Python dependencies*** section in [Settings](docs/SETTINGS.md).

## Pre-requisites

* Linux OS machine (RHEL/CentOS are preferred, other were not tested)
* Docker installed, user should have right to build docker images and run containers
* Access to Internet or access to Docker and pip offline repositories

## Getting started

Application can be run in two modes:

* Flask application on built-in web server in debug mode  
This is used for development and testing.

> For installation, configuration and usage guidance see [DEVELOPMENT](docs/DEVELOPMENT.md)  

* Using Gunicorn  
Preparation of Docker container with Flask application running on Gunicorn server as WSGI.

> For installation, configuration and usage guidance see [GUNICORN](docs/GUNICORN.md)

Application is covered by unit and integration tests (powered by `unittest`), please see [TESTING](docs/TESTING.md)

## JSON processing

JDE transforms original message to SAS format, and process SAS output based on configuration set in [`src/jde/conf/appconf.py`](src/jde/conf/appconf.py) file.  

> Application is designed to work only with messages with JSON payload or arguments from URL.  

> For details see ***Documentation for `appconf.py`*** section in [Settings](docs/SETTINGS.md).  

Steps of transformation:

1. **Caller** -- *(msg1)* --> **JDE**  
  JDE receives the original message from caller system. Message can be validated according to supplied JSON schema.
1. **JDE** -- *(msg2)* --> **SAS**  
  *msg2* should have format that is acceptable by SAS.
  JDE transforms *msg1* to *msg2* based on `INconfigs` variable - it creates input parameters for SAS one by one, create datagrid from key-value if needed and so on.
1. **SAS** -- *(msg3)* --> **JDE**  
  JDE receives response from SAS.
1. **JDE** -- *(msg4)* --> **Caller**  
  JDE transforms *msg3* and merge it with *msg1* based on `OUTconfigs` variable. These steps are applied for parameters from SAS output one-by-one:
      1. extract
      1. rename datagrid columns if needed
      1. transform datagrid to key-value
      1. transform
      1. transform msg1
      1. merge

These steps can be repeated if `multiRequest` option was chosen.  