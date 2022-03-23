import base64

import jwt
import redis


def is_user_token_valid(token):
    from application import application

    if application.config['DEBUG']:
        return True

    secret = base64.urlsafe_b64decode(application.config['JWT_SECRET'])
    audience = application.config['JWT_AUDIENCE']
    algorithms = application.config['JWT_ALGORITHM']
    options = {'verify_exp': False}

    try:
        received_token = jwt.decode(
            token,
            secret,
            audience=audience,
            algorithms=algorithms,
            options=options
        )

        amazon_token = jwt.decode(redis.Redis(
            host=application.config['HOLD_WHITELIST_HOST_ADDRESS'],
            port=application.config['HOLD_WHITELIST_HOST_PORT'],
            password=application.config['HOLD_WHITELIST_PASSWORD'],
            ssl=True
        ).get(received_token['username']),
            secret,
            audience=audience,
            algorithms=algorithms)

        return received_token == amazon_token
    except:
        return False
