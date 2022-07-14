testcases = []

# No configuration
testcases.append(
    {
        'name': 'no_conf',
        'massrvconf': None,
        'errorMsg': 'No server configuration provided'
    }
)

# Bad configuration
testcases.append(
    {
        'name': 'bad_conf',
        'massrvconf': ['host', 'port'],
        'errorMsg': 'Provided server configuration is not dictionary'
    }
)

# No baseUrl
massrvconf = {
    # 'baseUrl': 'http://your-viya-instance.sas.com',
    'oauth_client_id': 'oauth_client_id',
    'oauth_client_secret': 'oauth_client_secret',
    'grant_type': 'password',
    'username': 'dummy',
    'password': 'pwd',
    'callDecisionTimeout': (10, 10),
    'getAccessTokenTimeout': (10, 10)
}
testcases.append(
    {
        'name': 'no_baseUrl',
        'massrvconf': massrvconf,
        'errorMsg': '>> baseUrl << is missing in server configuration'
    }
)

# Invalid grant_type
massrvconf = {
    'baseUrl': 'http://your-viya-instance.sas.com',
    'oauth_client_id': 'oauth_client_id',
    'oauth_client_secret': 'oauth_client_secret',
    'grant_type': 'invalid',
    'username': 'dummy',
    'password': 'pwd',
    'callDecisionTimeout': (10, 10),
    'getAccessTokenTimeout': (10, 10)
}
testcases.append(
    {
        'name': 'invalid_grant_type',
        'massrvconf': massrvconf,
        'errorMsg': 'grant_type >> invalid << is not permitted'
    }
)

# grant_type=authorization_code, no code
massrvconf = {
    'baseUrl': 'http://your-viya-instance.sas.com',
    'oauth_client_id': 'oauth_client_id',
    'oauth_client_secret': 'oauth_client_secret',
    'grant_type': 'authorization_code',
    'callDecisionTimeout': (10, 10),
    'getAccessTokenTimeout': (10, 10)
}
testcases.append(
    {
        'name': 'authorization_code_missing_param',
        'massrvconf': massrvconf,
        'errorMsg': '>> code << is missing in server configuration (required for grant_type authorization_code)'
    }
)

# grant_type=password, no username
massrvconf = {
    'baseUrl': 'http://your-viya-instance.sas.com',
    'oauth_client_id': 'oauth_client_id',
    'oauth_client_secret': 'oauth_client_secret',
    'grant_type': 'password',
    'callDecisionTimeout': (10, 10),
    'getAccessTokenTimeout': (10, 10)
}
testcases.append(
    {
        'name': 'password_missing_param',
        'massrvconf': massrvconf,
        'errorMsg': '>> username << is missing in server configuration (required for grant_type password)'
    }
)

# grant_type=refresh_token, no refresh_token
massrvconf = {
    'baseUrl': 'http://your-viya-instance.sas.com',
    'oauth_client_id': 'oauth_client_id',
    'oauth_client_secret': 'oauth_client_secret',
    'grant_type': 'refresh_token',
    'callDecisionTimeout': (10, 10),
    'getAccessTokenTimeout': (10, 10)
}
testcases.append(
    {
        'name': 'refresh_token_missing_param',
        'massrvconf': massrvconf,
        'errorMsg': '>> refresh_token << is missing in server configuration (required for grant_type refresh_token)'
    }
)
