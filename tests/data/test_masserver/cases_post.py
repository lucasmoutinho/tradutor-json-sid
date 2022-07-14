import requests

testcases = []

# Timeout
testcases.append(
    {
        'name': 'Timeout',
        'status_code': 408,
        'text': '',
        'json_return_value': '',
        'side_effect': requests.exceptions.Timeout(),
        'exp_response': {'code': 408, 'body': None},
        'exp_badCredentials': False,
        'exp_errorMsg': 'Timeout'
    }
)

# ConnectionError
testcases.append(
    {
        'name': 'ConnectionError',
        'status_code': None,
        'text': '',
        'json_return_value': '',
        'side_effect': requests.exceptions.ConnectionError(),
        'exp_response': {'code': None, 'body': None},
        'exp_badCredentials': False,
        'exp_errorMsg': 'ConnectionError'
    }
)

# HTTPError - 401
testcases.append(
    {
        'name': 'HTTPError_401',
        'status_code': 401,
        'text': '',
        'json_return_value': '',
        'side_effect': requests.exceptions.HTTPError(),
        'exp_response': {'code': 401, 'body': None},
        'exp_badCredentials': True,
        'exp_errorMsg': 'Check your credentials and restart'
    }
)

# HTTPError - not 401
testcases.append(
    {
        'name': 'HTTPError_not_401',
        'status_code': 404,
        'text': '',
        'json_return_value': '',
        'side_effect': requests.exceptions.HTTPError(),
        'exp_response': {'code': 404, 'body': None},
        'exp_badCredentials': False,
        'exp_errorMsg': 'HTTPError'
    }
)


class CustomError(Exception):
    pass


# Unknown
testcases.append(
    {
        'name': 'Unknown',
        'status_code': None,
        'text': '',
        'json_return_value': '',
        'side_effect': CustomError(),
        'exp_response': {'code': None, 'body': None},
        'exp_badCredentials': False,
        'exp_errorMsg': 'Unknown'
    }
)

# Success
testcases.append(
    {
        'name': 'success',
        'status_code': 201,
        'text': '',
        'json_return_value': {'access_token': 'some_access_token'},
        'side_effect': None,
        'exp_response': {'code': 201, 'body': {'access_token': 'some_access_token'}},
        'exp_badCredentials': False,
        'exp_errorMsg': None
    }
)
