from os import environ

VARIABLES = {}
VARIABLES['JWT_ALGORITHM'] = environ.get('JWT_ALGORITHM', 'HS256')
VARIABLES['JWT_AUDIENCE'] = environ.get('JWT_AUDIENCE', '414e1927a3884f68abc79f7283837fd1')
VARIABLES['JWT_SECRET'] = environ.get('JWT_SECRET', 'qMCdFDQuF23RV1Y-1Gq9L3cF3VmuFwVbam4fMTdAfpo==')
VARIABLES['WHITELIST_HOST_ADDRESS'] = environ.get('WHITELIST_HOST_ADDRESS', 'hold-whitelist-test.redis.cache.windows.net')
VARIABLES['WHITELIST_HOST_PORT'] = environ.get('WHITELIST_HOST_PORT', '6380')
VARIABLES['WHITELIST_PASSWORD'] = environ.get('WHITELIST_PASSWORD', 'DxGtBgPL35wC6yaBp2tL0qpLmPU6kvnuvPGX3izB4LU=')
VARIABLES['AMQP_URL'] = environ.get('AMQP_URL', "weasel.rmq.cloudamqp.com")
VARIABLES['VIRTUAL_HOST'] = environ.get('VIRTUAL_HOST', "iuvyfpyv")
VARIABLES['VIRTUAL_PASSWD'] = environ.get('VIRTUAL_PASSWD', "XQ08BC5DH36hAQcxXddpS--voEUQRkjx")
VARIABLES['BUDGET_CALCS'] = environ.get('BUDGET_CALCS', "budget_calcs")
VARIABLES['CALC_STATUS'] = environ.get('CALC_STATUS', "calc_status_local")
VARIABLES['CALC_INPUTS'] = environ.get('CALC_INPUTS', "calc_inputs_local")
VARIABLES['SERVER_SHUTDOWN'] = environ.get('SERVER_SHUTDOWN', "werkzeug.server.shutdown")
