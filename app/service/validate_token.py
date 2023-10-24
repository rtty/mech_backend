import base64
import json
from typing import Dict

import jwt
import requests
from django.conf import settings

from app.service.jwksutils import \
    rsa_pem_from_jwk  # <-- this module contains the piece of code described previously

# https://robertoprevato.github.io/Validating-JWT-Bearer-tokens-from-Azure-AD-in-Python/

jwks = {}

valid_audiences = []  # id of the application prepared previously
issuer = 'https://sts.windows.net/9885457a-2026-4e2c-a47e-32ff52ea0b8d/'


class InvalidAuthorizationToken(Exception):
    def __init__(self, details: str) -> None:
        super().__init__('Invalid authorization token: ' + details)


def get_unverified_header(token: str) -> Dict[str, str]:
    jwts = token.split('.')
    try:
        return json.loads(base64.b64decode(jwts[0] + '==').decode('utf-8'))
    except UnicodeDecodeError:
        raise InvalidAuthorizationToken('decode error')


def get_jwt_value(token, key):
    headers = get_unverified_header(token)  # jwt.get_unverified_header(token)
    if not headers:
        raise InvalidAuthorizationToken('missing headers')
    try:
        return headers[key]
    except KeyError:
        raise InvalidAuthorizationToken('missing ' + key)


def get_kid(token: str) -> str:
    headers = get_unverified_header(token)  # jwt.get_unverified_header(token)
    if not headers:
        raise InvalidAuthorizationToken('missing headers')
    try:
        return headers['kid']
    except KeyError:
        raise InvalidAuthorizationToken('missing kid')


def get_alg(token: str) -> str:
    headers = get_unverified_header(token)  # jwt.get_unverified_header(token)
    if not headers:
        raise InvalidAuthorizationToken('missing headers')
    try:
        return headers['alg']
    except KeyError:
        raise InvalidAuthorizationToken('missing alg')


def get_jwk(kid: str):
    for jwk in jwks['keys']:
        if jwk['kid'] == kid:
            return jwk
    raise InvalidAuthorizationToken('kid not recognized')


def get_public_key(token: str):
    return rsa_pem_from_jwk(get_jwk(get_kid(token)))


def validate_jwt(jwt_to_validate: str):
    init_azure_ad(settings.AZURE_TENANT_ID, settings.AZURE_CLIENT_ID)
    alg = get_alg(jwt_to_validate)  # RS256
    public_key = get_public_key(jwt_to_validate)

    jwt_decoded = jwt.decode(
        jwt_to_validate,
        public_key,
        verify=True,
        algorithms=[alg],
        audience=valid_audiences,
        issuer=issuer,
    )

    # do what you wish with decoded token:
    # if we get here, the JWT is validated
    return jwt_decoded


def init_well_known_config(urlWellKnown: str) -> None:
    if not jwks.get('keys'):
        # get the well known info & get the public keys
        resp = requests.get(url=urlWellKnown)
        well_known_openid_config_data = resp.json()
        jwks_uri = well_known_openid_config_data['jwks_uri']
        # get the discovery keys
        resp = requests.get(url=jwks_uri)
        jwks.update(resp.json())


def init_azure_ad(tenantId: str, clientId: str) -> None:
    global issuer
    global valid_audiences
    issuer = 'https://sts.windows.net/' + tenantId + '/'
    valid_audiences.append(clientId)
    init_well_known_config(
        'https://login.microsoftonline.com/' + tenantId + '/v2.0/.well-known/openid-configuration'
    )
