# DEVELOPMENT mode

In this mode application is designed to be run on built-in Flask web server in debug mode.

Copy repo on your server (in some directory, lets name it `$DEVPATH`).

---

## Environment

> Skip this section if you already have proper environment

For better dependencies handling you can set up separate Docker image for development and testing purposes. All next steps are described using this approach.  
Docker's configuration file [`etc/flask/Dockerfile`](etc/flask/Dockerfile):

* Image is built on `python:3.8` image.  
* Python packages are installed according to [`requirements.txt`](requirements.txt)  
    See ***Python dependencies*** section in [Settings](docs/SETTINGS.md) for details.
* Create work directory `/main`

Build image and run container via [`start_flask.sh`](start_flask.sh)  
Parameters:

* `-p $PORT` - host machine's port for apps in Docker's container

Launch bash command:  

```bash
cd $DEVPATH
./start_flask.sh -p $PORT
```

This file issues `docker run` command with next parameters:

1. Ports `-p port1:port2`:
    * `port1` - `$PORT`
    * `port2` - internal Docker's port, which accepts requests from and send responses to `port1`. *Default: `8000`*
1. Bind mount a volume
    * `-v $(pwd)/src/jde:/src/jde`  
        Mounts directory with application files.
    * `-v $(pwd)/logs/jde:/logs`  
        Mounts `$DEVPATH/logs/jde` as directory for logs.  
        *`$DEVPATH/logs` is not included in repo as it is empty folder. Docker will create it automatically*
1. Host machine's date and time (read-only)
    * `-v /etc/localtime:/etc/localtime:ro`
1. Load environment variables
    * `--env-file $(pwd)/etc/flask/.env` 
    * `-e SASPASS`

    Directory `etc/flask` should contain `.env` file with necessary parameters in `name=value` pattern. Example:  
    ```bash
    baseUrl=http://XXXXXXX
    oauth_client_id=XXX
    oauth_client_secret=XXX
    grant_type=password
    userId=XXX
    callDecisionTimeoutConnect=XXX
    callDecisionTimeoutRead=XXX
    getAccessTokenTimeoutConnect=XXX
    getAccessTokenTimeoutRead=XXX
    dfltModules=rootPath1:moduleID1,rootPath2:moduleID2
    ```
    See ***Input parameters*** section in [Settings](docs/SETTINGS.md) for details.  
    *This file is not included in repo as it is specific for your Viya env and chosen auth options, you should create it on your own.* 

    Variable `SASPASS` contains sensitive info and is loaded from keyboard.  
1. `imageName` - name of Docker's image, named as `jde_flask:latest`.
1. `/bin/bash` opens Docker container's interactive shell for issuing `python` commans

---

## Flask application

### How to start Flask app on built-in web server

Issue command (with docker container terminal):

```bash
cd src/jde
python jde.py
```

Application is ready to serve requests.

Press `Ctrl+C` to stop the application.
