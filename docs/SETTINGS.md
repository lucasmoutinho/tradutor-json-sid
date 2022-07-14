# Settings

## Input parameters

Currently parameters for MAS server instance (`app.lib.masserver.MASServerClass`) are loaded from environment variables (configured in [`src/jde/conf/massrvconf.py`](jde/conf/massrvconf.py)).  
Application expects these parameters (and few other) passed into as environment variables:

* `baseUrl` - URL of SAS Viya instance
* `oauth_client_id`, `oauth_client_secret`, `grant_type`, `userId`, `SASPASS` - see [Authentication](#authentication) for details
* `callDecisionTimeoutConnect` and `callDecisionTimeoutRead` - connect and read timeout for calling MAS module respectively
* `getAccessTokenTimeoutConnect` and `getAccessTokenTimeoutRead` - connect and read timeout for token retrieval respectively
* `dfltModules` - default moduleID for rootPath  
    It must follow the next pattern:  
    `rootPath1:moduleID1,rootPath2:moduleID2,...`

---
---

## <a name="python_dependencies"></a>Python dependencies

Python modules in Docker image are installed by `pip` using file with requirements - [`requirements.txt`](requirements.txt). For safety and reliability all modules and their versions are fixed here.

In case if you'd like to upgrade all or some of modules, you need to update this file. 

---
---

## Flask

Flask requires special class for configuration on the moment of creation. Class is provided differently based on mode:  

* Development - already in [`src/jde/conf/flaskconf.py`](src/jde/conf/flaskconf.py)
* Testing - is overridden directly in tests
* Production - copy from `./etc/gunicorn/$MODE/flaskconf.py` to `src/jde/conf` on the moment of building the image

---
---

## Logging

Three modes of logging:

1. **Flask**  
    Loaded in [`src/jde/app/__init__.py`](src/jde/app/__init__.py) from [logconfig.json](src/jde/logconfig.json)
1. **Gunicorn**  
    Loaded in [`gunicorn_config.py`](etc/gunicorn/dev/gunicorn_config.py) from [`gunicorn_logconfig.json`](etc/gunicorn/dev/gunicorn_logconfig.json).  
    Then flask's logger is reconfigured based on `gunicorn.error' logger.
1. **Testing**  
    Loaded in [`tests/__init__.py`](tests/__init__.py) from [logconfig.json](tests/logconfig.json)

---
---

## <a name="gunicorn"></a>Gunicorn

Gunicorn is configured via special file - `gunicorn_config.py`  
Change this file for:

* logging configuration (format for `gunicorn.access` should be here);
* approach for workers' management;
* various activities that can be done in Gunicorn's server hooks;
* any other options that Gunicorn provides.

> Documentation is available [here](http://docs.gunicorn.org/en/stable/settings.html).  
> Tune `worker_class`, `workers`, `threads`, `keepalive` and others for better performance. More details are [here](http://docs.gunicorn.org/en/stable/design.html).

Logging is configured via separate YAML file - `gunicorn_logconfig.json`  
Change this file for:

* log files' path;
* log level (modify it for `gunicorn.error` logger);
* format for `gunicorn.error` logger.

---
---

## <a name="authentication"></a>Authentication

SAS uses OAuth authentication option, it means that every application, that is going to use SAS REST API, should has its client and access token.
See doc [here](https://developer.sas.com/reference/auth).

### Client

Client should be registered in Viya with desired `authorized_grant_types`. *Currently supported only `password`* .  
At the moment of Docker container's start, these environment variables should be set:

* `oauth_client_id` = client_id
* `oauth_client_secret` = client_secret

They can be set via `srvconfig.sh`. Example:

```bash
oauth_client_id=jde_id
oauth_client_secret=top_secret
```

### Tokens

Current approach is that application can retrieve tokens directly from Viya using username/password. They should be provided at the moment of application's start. Tokens are retrieved by application at the moment of start, after that it is available for each worker via Flask's `g`.

Next runtime environment variables should be provided for Docker:

* `grant_type` = 'password'
* `userId` = some Viya user's name
* `SASPASS` = its' password

They can be set via `.env` or input from keyboard.

There are two tokens:

* `access_token` - used for SAS REST API
* `refresh_token` - used for refresh `access_token` when it is expired.

Token has limited live time. How expiration is handled:

1. App receives 401 error using `access_token`
2. It tries to get the new one using `refresh_token` and `grant_type: refresh_token`. It is much faster than retrieval token by username/password.
3. If successful, update `access_token` and continue processing requests
4. If not, app tries to get new `access_token` and `refresh_token` in the same manner as it happens when worker is restarted.
5. If successful, update `access_token` and `refresh_token` and continue processing requests
6. If not, appropriate message is sent to log, app stops processing the requests.

> **TBD**  
> Approach described above has several caveats:
> * current design fully supports only `grant_type: password`
> * security issue - username/password are stored in app and even are not encrypted
> * user with rights for `docker inspect` command is able to see password.
>
> What could be done in order to avoid storing username/password :
> * add new POST endpoint for updating credentials. External secured service with access to credential store calls it and provides new `code` or `refresh_token`. This option requires application to be able to share data between workers (i.e. [memcached](https://memcached.org/)). Not clear how this service will know when to call it...  
> * *\[PREFERRED\]* add any external source of `code` or `refresh_token` (depends on particular architecture, web-service is preferred). It is supposed, that these parameters could be provided by some external secured service with access to credential store.
> * in case if `grant_type: password` option is chosen, password should be provided in more reliable way. Highly depends on customer's architecture.

---
---

## Documentation for `appconf.py`

Use this documentation in order to create your configuration of JSON message processing.  
It is python code file that should be placed either in `src/jde/conf/appconf.py` or provided via `-a` option for Gunicorn.  

> If any mandatory variables are missing, or unknown variables are present, or there is type mismatch - JDE will not be started (refer to [`utils.py`](src/jde/app/lib/utils.py)).

> Power of [jq](https://github.com/stedolan/jq) is used there, please check documentation for writing new rules or modifying the existing one.

It must contain main variable `cfgs` of `list` type, that is imported in application.  
Each entry is responsible for configuration for one endpoint, they are of `dict` type with attributes:

| Attribute                 | Type   | Description                                                |
|---------------------------|--------|------------------------------------------------------------|
| `method`                  | `str`  | Can be 'POST' or 'GET' only <br> if 'POST', request data is taken from request body <br> if 'GET', request data is taken from URL parameters|
| `argsConvertTypes`        | `dict` | List of input parameters with types in which these params should be converted | 
| `moduleIdHeader`          | `bool` | If True, get moduleId from header `Module-ID` | 
| `dfltSuccessResponseCode` | `int`  | Default Success Response Code                                |
| `dfltErrorResponseCode`   | `int`  | Default Error Response Code                                |
| `useSASResponseCode`      | `bool` | Flag. Set it True to take response codes from SAS response |
| `multiRequest`            | `bool` | Flag. Set it True in case if one request to JDE is suggested to produce multiple requests to SAS     |
| `multiRequestSettings`    | `dict` | Configuration for multiple requests to SAS <br> Details are below                 |
| `INconfigs`               | `list` | Configuration for parsing of input message <br> Details are below                |
| `OUTconfigs`              | `dict` | Configuration for construction of the output message <br> Details are below       |
| `jsonschemaFile`          | `str`  | Name of file with schema in `conf/jsonschema` directory                |
| `requiredProperties`      | `dict`  | Dictionary with required attributes to validate an input message. If empty, validation is performed against the JSON schema with separate type checking. The dictionary key is used in an error message and the value in an error code.          |
---

### **INconfigs**  

This attribute is the list of configurations for every parameter in input for SAS.  
Each entry is of `dict` type with attributes:
| Attribute     | Type | Description                                                                 |
|---------------|------|-----------------------------------------------------------------------------|
| `name`          | `str`  | Name of parameter provided to SAS                                           |
| `rule`          | `str`  | `jq` filter rule for extracting the dataGrid                                |
| `type`          | `str`  | 'datagrid'/'data' <br> **datagrid**: extracted data will be converted to SAS dataGrid. <br> **data** : every extracted parameter will be threated separately                                                           |
| `defaultType`   | `str`  | Default SAS datatype <br> *Only for type='data'*                                                        |
| `dataTypes`     | `dict` | Specify SAS datatype for each parameter (if differs from defaultType) <br> *Only for type='data'*       |
| `newNames`      | `dict` | Specify name for each parameter that SAS expects (if differs from original) |
| `addUnderscore` | `int`  | **0** : keep name as is <br> **1** : add '\_' at the end for each variable name <br> **2** : add '\_' at the end for each variable name, except newNames (only for type='data')                                                       |

Example:
```python
root = {}
root['name'] = 'data from root'
root['rule'] = '[del(.creditFacilities) | to_entries[] | with_entries(if .key == "key" then .key = "name" else . end)]'
root['type'] = 'data'
root['defaultType'] = 'string'
root['dataTypes'] = {'debtRecovery': 'decimal', 'watchStatus': 'decimal'}
root['newNames'] = {'debtRecovery': 'debtRecovery_', 'watchStatus': 'watchStatus_'}
root['addUnderscore'] = 2
INconfigs.append(root)
```

---

### **OUTconfigs**  

Attributes:  
| Attribute         | Type | Description                                                   |
|-------------------|------|---------------------------------------------------------------|
| `mode`              | `str`  | Mode of merging source and destination JSONs <br> **a2b** : Merge from JSON-a to JSON-b <br> **a2a** : Merge from JSON-a to JSON-a <br> **b2a** : Merge from JSON-b to JSON-a <br> **a2custom** : Merge from JSON-a to custom destination                 |
| `customDest`        | `dict` | Custom destination JSON message                               |
| `destTransformRule` | `str`  | `jq` filter. Rule how to transform base response            |
| `params_cfg`        | `list` | List of configurations for every parameter in output from SAS |

<br>  

`params_cfg` describes how parameter from SAS output should be embedded into the output message.  
Configuration for one parameter is of `dict` type with attributes:
| Attribute        | Type | Description                                               |
|------------------|------|-----------------------------------------------------------|
| `parameterName`    | `str`  | Name of parameter(s) that are extracted from SAS output <br> Used for logging only, no logic applied  |
| `parameterType`    | `str`  | 'datagrid'/'data'  <br> **datagrid**: extracted data will be converted to SAS dataGrid. <br> **data** : every extracted parameter will be threated separately                                        |
| `extractRule`      | `str`  | `jq` filter. Rule how to extract data from SAS output <br> If empty, whole message is used    |
| `renameColDict`    | `dict` | Only for datagrids <br> key - name in datagrid. value - name that should be in response                                       |
| `transformRule`    | `str`  | `jq` filter. Rule how to transform extracted data <br> If empty, request transformation step is missed <br> For type='data', if renaming is required add this filter for each parameter: <br> `map(if .name == "oldName" then .name = "newName" else . end)`        |
| `reqTransformRule` | `str`  | `jq` filter. Rule how to transform original input message <br> If empty, request transformation step is missed |
| `mergeRule`        | `dict` |  `path`: `list`: list of tokens (string) in request, that provides hierarchical address of place, where SAS data should be embedded to <br> `keyAttr`: `string`: name of parameter, which is used for joining the request and SAS data. Taken from request                                                         |

---

### **multiRequestSettings**   

Allows to customize the ordering and merging of data between requests.  
It consists of:
* `sortSettings` : `dict`  
    Configuration for sorting of request entries.  
    If empty or not provided: keep original order.  
    Must contain the 'sortAttr' attribute for customize order.  
    Element keys can be:  

    | Attribute | Type | Description                                                    |
    |-----------|------|----------------------------------------------------------------|
    | `sortAttr`  | `str`  | Attribute on root level, which is used for sorting            |
    | `datefmt`   | `str`  | Apply date format to retrieved value if needed. Not mandatory |
    | `direction` | `str`  | 'asc' / 'desc'. Not mandatory. If empty : 'asc'                     |

* `mergeSettings` : `dict`  
    This attribute has the same structure as `OUTconfigs` except one extra attribute:  

    * `validationRule` : `str`  
        Use this `jq` filter for validation of source JSON.  Filter should return `int` value. 0 means error, others - ok.  
        For example:  
        `if .result.resultCode == "OK" then 1 else 0 end`

* `inputSettings` : `str`  
    `jq` filter. Rule how to get array from original request body  

* `outputSettings` : `str`  
    `jq` filter. Rule how to put array to response body
