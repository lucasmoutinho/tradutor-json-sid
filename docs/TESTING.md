# TESTING mode

This mode is designed to run test cases via `pytest`.

## Environment

> Skip this section if you already have proper environment

Environment's set up is similar to development (see [DEVELOPMENT](docs/DEVELOPMENT.md)):

```bash
cd $DEVPATH
./start_test.sh -m
```

> Use option `-m` for writing custom pytest commands

## Testing

Located in directory [`tests`](tests).  

Tests were created in order to test:

* [jsonfunc.py](src/jde/app/lib/jsonfunc.py)  
    Data is located in `tests/data/test_jsonfunc`
* [sasdgfunc.py](src/jde/app/lib/sasdgfunc.py)  
* [utils.py](src/jde/app/lib/utils.py)
    Data is located in `tests/data/test_utils`  
* [masserver.py](src/jde/app/lib/masserver.py)  
    Data is located in `tests/data/test_masserver`
* [massrvconf.py](src/jde/conf/massrvconf.py)  
* full Flask application  
    Data is located in `tests/data/test_flask`
* loading of log configuration  

How to run tests (with docker container's terminal):

```bash
# Run all tests without details
python -m pytest
pytest
pytest --rootdir=tests
# Run all tests with details
pytest -sv --rootdir=tests
# Run only one group of tests
pytest tests/test_utils.py
```

> You have to run tests from `/main` working directory

> You can use default command `python -m pytest` just simply launching `start_test.sh` with `-m` option

> Since `tests` directory is outside of main app's directory, `main/src/jde` directory is appended to `PYTHONPATH` in [`__init__.py`](tests/__init__.py).

### Logging

Logging is configured in [`__init__.py`](tests/__init__.py) via [`logconfig.json`](tests/logconfig.json) file. The idea is that logs are written to `stdout`/`stderr` only. They are suppressed by default, and in case if needed can be shown with `-s` option.  
[`test_logging.py`](tests/test_logging.py) runs log configuration in [`src/jde/app/__init__.py`](src/jde/app/__init__.py), so logging needs to be reloaded for further tests.

### Coverage

Get coverage percentage running these commands:  
```bash
coverage run -m pytest --rootdir=tests
coverage report -m
```