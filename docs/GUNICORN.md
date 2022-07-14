# Run Flask app on Gunicorn

## Prepare configuration

Configuration files are loaded from directory in `$DEVPATH/etc/gunicorn`. Create it with some valid name, let's name it `dev` (as this directory is in repo for example).
> **Tip.** You can have configurations for different environments like Development and Production, with files in `dev` and `prod` directories respectively.

Configuration files (see ***Gunicorn*** section in [Settings](docs/SETTINGS.md) for details):

1. Gunicorn config file: [`gunicorn_config.py`](etc/gunicorn/dev/gunicorn_config.py) 
1. File with log configuration: [`gunicorn_logconfig.json`](etc/gunicorn/dev/gunicorn_logconfig.json) 
1. File with server-specific variables: `.env`.  
    *This file is not included in repo as it is specific for your Viya env and chosen auth options, you should create it on your own.*  
    Example of `.env`:

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
1. File with Flask configuration class: [`flaskconf.py`](etc/gunicorn/dev/flaskconf.py)

Build image and run container via [`start_gunicorn.sh`](start_gunicorn.sh).  
Parameters:

* `-m $MODE` - mode. It is used as version of Docker image and path for config files. Ensure that all necessary files are located at `./etc/gunicorn/$MODE`
* `-p $PORT` - host machine's port for apps in Docker's container
* `-a $APPCONF` - Path to file that overrides ./jde/conf/appconf.py. Keep it empty to use existing

Launch bash command:  

```bash
cd $DEVPATH
./start_gunicorn.sh -m dev -p $PORT [-a $APPCONF]
```

Run of [`start_gunicorn.sh`](start_gunicorn.sh) issues `docker build` and `docker run` commands.  
`docker build` is working according to the [`Dockerfile`](etc/gunicorn/Dockerfile):

* Image is built on `python:3.8` image.
* Python packages are installed according to `requirements.txt`.  
See ***Python dependencies*** section in [Settings](docs/SETTINGS.md) for details.
* Copy Gunicorn configuration file
* Create work directory `/main` and copy content of `$DEVPATH` there.
* Copy `flaskconf.py` in `src/jde/conf`

`docker run` does the following:

1. Set up port redirect:
    * `port1` - `$PORT`
    * `port2` - internal Docker's port, which accepts requests from and send responses to `port1`. *Default: `8000`*
1. Set up environment variables  
    * `--env-file $ENVFILE` 
    * `-e SASPASS`

    Variable `SASPASS` contains sensitive info and is loaded from keyboard.  
    See ***Input parameters*** section in [Settings](docs/SETTINGS.md) for details.
1. Bind mount a volume for:
    * Directory for logs `logs/jde/gunicorn/logs_$DTTM`  
        `$DTTM` is timestamp of app start in format `%Y-%m-%d_%H-%M-%S`  
        *`$DEVPATH/logs` is not included in repo as it is empty folder. Docker will create it automatically*
    * Gunicorn logging configuration
1. Override default `src/jde/conf/appconf.py` if needed
1. Apply host machine's date and time to Docker image
1. Define the name of Docker's image. In this case - `jde_gunicorn:dev`

Here you build image named `imageName` and start Docker container listening on port `port1`.
Commands to check:  

```bash
docker images  # list of all images
docker container ps  # list of running containers
```

In case of successful run you will see next messages (details may differ in your case) via `gunicorn.error` logger (according to your `gunicorn_logconfig.json`):
```bash
[2020-10-25 06:47:09,027] [INFO    ] [1 ] [app.lib.masserver   ] [masserver ] Server instance initialization is successful
[2020-10-25 06:47:09,027] [INFO    ] [1 ] [app.lib.masserver   ] [masserver ] Retrieving access token...
[2020-10-25 06:47:09,027] [INFO    ] [1 ] [app.lib.masserver   ] [masserver ] Use initial authConf
[2020-10-25 06:47:09,028] [DEBUG   ] [1 ] [app.lib.masserver   ] [masserver ] Sending POST request to SAS...
[2020-10-25 06:47:10,693] [DEBUG   ] [1 ] [app.lib.masserver   ] [masserver ] SAS response status code: 200. Time: 1665.782ms
[2020-10-25 06:47:10,694] [INFO    ] [1 ] [app.lib.masserver   ] [masserver ] Identity checked
[2020-10-25 06:47:10,931] [INFO    ] [1 ] [gunicorn.error      ] [glogging  ] Starting gunicorn 20.0.4
[2020-10-25 06:47:10,932] [DEBUG   ] [1 ] [gunicorn.error      ] [glogging  ] Arbiter booted
[2020-10-25 06:47:10,932] [INFO    ] [1 ] [gunicorn.error      ] [glogging  ] Listening at: http://0.0.0.0:8000 (1)
[2020-10-25 06:47:10,932] [INFO    ] [1 ] [gunicorn.error      ] [glogging  ] Using worker: sync
[2020-10-25 06:47:10,937] [INFO    ] [14] [gunicorn.error      ] [glogging  ] Booting worker with pid: 14
[2020-10-25 06:47:10,942] [INFO    ] [14] [gunicorn.error      ] [gunicorn_config] <Worker 14> is ready to serve requests
[2020-10-25 06:47:11,032] [INFO    ] [15] [gunicorn.error      ] [glogging  ] Booting worker with pid: 15
[2020-10-25 06:47:11,037] [INFO    ] [15] [gunicorn.error      ] [gunicorn_config] <Worker 15> is ready to serve requests
[2020-10-25 06:47:11,045] [DEBUG   ] [1 ] [gunicorn.error      ] [glogging  ] 2 workers
```

Application is ready to serve requests.

Press `Ctrl+C` to stop the container.

---

## How-to-use

JDE provides REST API, it expects request data in JSON and returns results in JSON for successful messages and simple text for errors.  
Method, JSON format of request and response are not fixed and depends only on configuration.

Endpoint:
* `/{rootPath}`

MAS module ID is determined by `dfltModules` by default. Also, it can be overriden from request header `Module-ID`.

Request:

```http
POST /{rootPath} HTTP/1.1
Content-Type: application/json
Host: {docker-server-hostname}:{port1}

{<some valid request>}
```

Response (in case of success):

```http
HTTP/1.1 201 CREATED
Server: gunicorn/20.0.4
Date: Mon, 30 Mar 2020 10:44:18 GMT
Connection: close
Content-Type: application/json
Content-Length: 2144

{<some valid response>}
```

Each request info is logged via `gunicorn.access` logger (according to your `gunicorn_logconfig.json`).
