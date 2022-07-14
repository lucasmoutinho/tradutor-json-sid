testcases = []


# refresh_token_success
def post_new(*args, **kwargs):
    response = {
        'code': 200,
        'body': {
            'access_token': 'any_access_token',
            'refresh_token': 'any_refresh_token'
        }
    }
    return response, False, None


testcases.append(
    {
        'name': 'refresh_token_success',
        'post_new': post_new,
        'authConf': None,
        'exp_result': True,
        'exp_accessTokenStatus': 'OK',
        'exp_accessToken': 'any_access_token',
        'exp_refreshToken': 'any_refresh_token'
    }
)


# Refresh token is failed, get new one with initial configuration
def post_new(*args, **kwargs):
    if kwargs['myParams']['grant_type'] == 'refresh_token':
        response = {
            'code': 401,
            'body': {
                'error': 'unauthorized',
                'error_description': 'Bad credentials'
            }
        }
        return response, True, 'Check your credentials and restart'
    else:
        response = {
            'code': 200,
            'body': {
                'access_token': 'any_access_token',
                'refresh_token': 'any_refresh_token'
            }
        }
        return response, False, None


testcases.append(
    {
        'name': 'refresh_token_fail_then_success',
        'post_new': post_new,
        'authConf': None,
        'exp_result': True,
        'exp_accessTokenStatus': 'OK',
        'exp_accessToken': 'any_access_token',
        'exp_refreshToken': 'any_refresh_token'
    }
)


# Override authConf, grant_type=authorization_code
def post_new(*args, **kwargs):
    response = {
        'code': 200,
        'body': {
            'access_token': 'any_access_token',
            'refresh_token': 'any_refresh_token'
        }
    }
    return response, False, None


testcases.append(
    {
        'name': 'override_code',
        'post_new': post_new,
        'authConf': {'grant_type': 'authorization_code', 'code': 'some_code'},
        'exp_result': True,
        'exp_accessTokenStatus': 'OK',
        'exp_accessToken': 'any_access_token',
        'exp_refreshToken': 'any_refresh_token'
    }
)


# Override authConf, grant_type=refresh_token
def post_new(*args, **kwargs):
    response = {
        'code': 200,
        'body': {
            'access_token': 'any_access_token',
            'refresh_token': 'any_refresh_token'
        }
    }
    return response, False, None


testcases.append(
    {
        'name': 'override_refresh_token',
        'post_new': post_new,
        'authConf': {'grant_type': 'refresh_token', 'refresh_token': 'any_refresh_token'},
        'exp_result': True,
        'exp_accessTokenStatus': 'OK',
        'exp_accessToken': 'any_access_token',
        'exp_refreshToken': 'any_refresh_token'
    }
)


# Imitate HTTPError
def post_new(*args, **kwargs):
    response = {
        'code': 404,
        'body': None
    }
    return response, False, 'HTTPError'


testcases.append(
    {
        'name': 'failed',
        'post_new': post_new,
        'authConf': None,
        'exp_result': False,
        'exp_accessTokenStatus': 'FAILED',
        'exp_accessToken': None,
        'exp_refreshToken': None
    }
)


# Empty token without error
def post_new(*args, **kwargs):
    response = {
        'code': 200,
        'body': {
            'access_token': None,
            'refresh_token': None
        }
    }
    return response, False, None


testcases.append(
    {
        'name': 'empty_token',
        'post_new': post_new,
        'authConf': None,
        'exp_result': False,
        'exp_accessTokenStatus': 'FAILED',
        'exp_accessToken': None,
        'exp_refreshToken': None
    }
)
