from fastapi import APIRouter, Form, Query
from fastapi.responses import RedirectResponse

from models.user import UserModel
from services.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, timedelta
from services.google import generate_auth_uri, get_token, get_userinfo
from services.users import get_or_create

router = APIRouter(tags=['Oauth2'])


@router.get('/google', response_description='Oauth via google', response_class=RedirectResponse)
async def oauth_google(redirect_uri: str = 'http://localhost:8000/oauth/google/redirect',
                       state: str | None = Query(None, include_in_schema=False)):
    uri = generate_auth_uri(redirect_uri=redirect_uri,
                            scope=['https://www.googleapis.com/auth/books', 'email', 'profile', 'openid'], state=state)

    return RedirectResponse(uri)


@router.get('/google/redirect', include_in_schema=False)
async def oauth_google_redirect(code: str, redirect_uri: str = 'http://localhost:8000/oauth/google/redirect'):
    return await _oauth_google_redirect(code, redirect_uri)


@router.post('/google/redirect', include_in_schema=False)
async def oauth_google_redirect(code: str = Form(...), redirect_uri: str = Form(...)):
    return await _oauth_google_redirect(code, redirect_uri)


async def _oauth_google_redirect(code: str, redirect_uri: str) -> dict | int:
    access_data, access_data_error = get_token(code, redirect_uri)

    if access_data_error:
        return 400

    userinfo, userinfo_error = get_userinfo(access_data['token_type'], access_data['access_token'])
    if userinfo_error:
        return 400

    new_user = UserModel(google_id=userinfo['id'], name=userinfo['name'], email=userinfo['email'],
                         picture=userinfo['picture'], locale=userinfo['locale'],
                         access_token=access_data['access_token'], refresh_token=access_data['refresh_token'])

    user = await get_or_create(new_user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': str(user.id)}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}
