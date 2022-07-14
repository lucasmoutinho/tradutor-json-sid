testcases = []


# Success, timeout from initial config, convert request body to string
def post_new(*args, **kwargs):
    return ({'code': 201, 'body': {}}, False, None)


testcases.append(
    {
        'name': 'success',
        'requestBody': {},
        'callDecisionTimeout': None,
        'post_new': post_new,
        'getAccessToken_return_value': None,
        'exp_SASResponse': {'code': 201, 'body': {}},
        'exp_status': True,
        'exp_errorMsg': None
    }
)


# Success, timeout overrided
def post_new(*args, **kwargs):
    return ({'code': 201, 'body': {}}, False, None)


testcases.append(
    {
        'name': 'success_timeout_override',
        'requestBody': {},
        'callDecisionTimeout': 5,
        'post_new': post_new,
        'getAccessToken_return_value': None,
        'exp_SASResponse': {'code': 201, 'body': {}},
        'exp_status': True,
        'exp_errorMsg': None
    }
)


# Success, no convert request body to string
def post_new(*args, **kwargs):
    return ({'code': 201, 'body': {}}, False, None)


testcases.append(
    {
        'name': 'success_request_string',
        'requestBody': '{}',
        'callDecisionTimeout': None,
        'post_new': post_new,
        'getAccessToken_return_value': None,
        'exp_SASResponse': {'code': 201, 'body': {}},
        'exp_status': True,
        'exp_errorMsg': None
    }
)


# Failed, 404
def post_new(*args, **kwargs):
    return ({'code': 404, 'body': None}, False, 'HTTPError')


testcases.append(
    {
        'name': 'fail_404',
        'requestBody': {},
        'callDecisionTimeout': None,
        'post_new': post_new,
        'getAccessToken_return_value': None,
        'exp_SASResponse': {'code': 404, 'body': None},
        'exp_status': False,
        'exp_errorMsg': 'HTTPError'
    }
)


# Imitate token expiration
def post_new(*args, **kwargs):
    if 'SASLogon' in kwargs['myUrl']:
        response = {
            'code': 200,
            'body': {
                'access_token': 'any_access_token',
                'refresh_token': 'any_refresh_token'
            }
        }
        return response, False, None
    else:
        if kwargs['myHeaders']['Authorization'] == 'bearer init_access_token':
            return (
                {
                    'code': 401,
                    'body': {
                        'error': 'unauthorized',
                        'error_description': 'Bad credentials'
                    }
                },
                True,
                'Check your credentials and restart'
            )
        else:
            return ({'code': 201, 'body': {}}, False, None)


testcases.append(
    {
        'name': 'token_expired',
        'requestBody': {},
        'callDecisionTimeout': None,
        'post_new': post_new,
        'getAccessToken_return_value': None,
        'exp_SASResponse': {'code': 201, 'body': {}},
        'exp_status': True,
        'exp_errorMsg': None
    }
)


# Imitate password expiration
def post_new(*args, **kwargs):
    return (
        {
            'code': 401,
            'body': {
                'error': 'unauthorized',
                'error_description': 'Bad credentials'
            }
        },
        True,
        'Check your credentials and restart'
    )


testcases.append(
    {
        'name': 'password_expired',
        'requestBody': {},
        'callDecisionTimeout': None,
        'post_new': post_new,
        'getAccessToken_return_value': None,
        'exp_SASResponse': {
            'code': 401,
            'body': {
                'error': 'unauthorized',
                'error_description': 'Bad credentials'
            }
        },
        'exp_status': False,
        'exp_errorMsg': 'Check your credentials and restart'
    }
)
