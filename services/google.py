from urllib.parse import urlencode

import requests

from config import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET


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


def get_token(code: str, redirect_uri: str, **kwargs) -> set[dict, bool]:
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

    return response, 'error' in response


def get_refreshed_token(refresh_token: str, **kwargs) -> set[dict, bool]:
    url = 'https://accounts.google.com/o/oauth2/token'
    params = {
        'refresh_token': refresh_token,
        'client_id': GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': GOOGLE_OAUTH_CLIENT_SECRET,
        'grant_type': 'refresh_token',
    }
    params.update(kwargs)

    response = requests.request('POST', url, data=params).json()

    return response, 'error' in response


def get_userinfo(access_token: str) -> set[dict, bool]:
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request('GET', 'https://www.googleapis.com/oauth2/v1/userinfo', headers=headers).json()

    return response, 'error' in response


def get_tokeninfo(access_token: str) -> set[dict, bool]:
    params = {
        'access_token': access_token
    }

    response = requests.request('GET', 'https://oauth2.googleapis.com/tokeninfo', params=params).json()

    return response, 'error' in response
