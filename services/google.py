from typing import NamedTuple
from urllib.parse import urlencode

import requests

from data.config import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET
from exceptions import GoogleCodeTokenError, GoogleTokenError
from models import UserCredentialsModel, UserModel
from services.users import update_user_credentials


class Token(NamedTuple):
    access_token: str
    refresh_token: str = None


class Tokeninfo(NamedTuple):
    sub: str
    scope: str
    exp: int
    email: str


def generate_auth_uri(redirect_uri: str, scope: list[str] = None, state: str = None, **kwargs: dict[str, str]) -> str:
    if scope is None:
        scope = ['https://www.googleapis.com/auth/books', 'email', 'profile', 'openid']

    url = 'https://accounts.google.com/o/oauth2/v2/auth?'
    params = {
        'client_id': GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scope),
        'response_type': 'code',
        'access_type': 'offline',
        'include_granted_scopes': 'true'
    }
    if state:
        params['state'] = state

    params.update(kwargs)

    return url + urlencode(params)


def get_token(code: str, redirect_uri: str, **kwargs) -> Token:
    url = 'https://accounts.google.com/o/oauth2/token'
    params = {
        'code': code,
        'client_id': GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': GOOGLE_OAUTH_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'access_type': 'offline',
        'grant_type': 'authorization_code',
    }
    params.update(kwargs)

    response = requests.request('POST', url, data=params).json()
    if 'error' in response:
        raise GoogleCodeTokenError(response)

    return Token(access_token=response['access_token'],
                 refresh_token=response['refresh_token'] if 'refresh_token' in response else None)


def get_refreshed_token(refresh_token: str, **kwargs) -> Token:
    url = 'https://accounts.google.com/o/oauth2/token'
    params = {
        'refresh_token': refresh_token,
        'client_id': GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': GOOGLE_OAUTH_CLIENT_SECRET,
        'grant_type': 'refresh_token',
    }
    params.update(kwargs)

    response = requests.request('POST', url, data=params).json()

    if 'error' in response:
        raise GoogleTokenError(response)

    return Token(access_token=response['access_token'],
                 refresh_token=response['refresh_token'] if 'refresh_token' in response else None)


async def refresh_user_tokens(user: UserModel) -> UserModel:
    access_data = get_refreshed_token(user.credentials.refresh_token)
    tokeninfo = get_tokeninfo(access_data.access_token)

    user_credentials = UserCredentialsModel(
        access_token=access_data.access_token,
        refresh_token=access_data.refresh_token if access_data.refresh_token else user.credentials.refresh_token,
        expires_in=tokeninfo.exp, scope=tokeninfo.scope,
    )

    return await update_user_credentials(user.id, user_credentials)


def get_tokeninfo(access_token: str) -> Tokeninfo:
    params = {
        'access_token': access_token
    }

    response = requests.request('GET', 'https://oauth2.googleapis.com/tokeninfo', params=params).json()

    if 'error' in response:
        raise GoogleTokenError(response)

    return Tokeninfo(scope=response['scope'], exp=response['exp'], sub=response['sub'], email=response['email'])
