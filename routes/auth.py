from fastapi import APIRouter, Form, Query, HTTPException, status, Cookie
from fastapi.responses import RedirectResponse, JSONResponse

from models.user import UserModel
from schemas import Credentials
from services.auth import is_token_exits, remove_token, get_current_user, create_tokens
from services.google import generate_auth_uri, get_token, get_userinfo
from services.users import get_or_create

router = APIRouter(tags=['Oauth2'])


@router.get('/google', response_description='Oauth via google', response_class=RedirectResponse)
async def oauth_google(redirect_uri: str = 'http://localhost:8000/oauth/google/redirect',
                       state: str | None = Query(None, include_in_schema=False)):
    uri = generate_auth_uri(redirect_uri=redirect_uri,
                            scope=['https://www.googleapis.com/auth/books', 'email', 'profile', 'openid'], state=state)

    return RedirectResponse(uri)


@router.get('/google/redirect', include_in_schema=False, response_model=Credentials)
async def oauth_google_redirect(code: str, redirect_uri: str = 'http://localhost:8000/oauth/google/redirect'):
    return await _oauth_google_redirect(code, redirect_uri)


@router.post('/google/redirect', include_in_schema=False, response_model=Credentials)
async def oauth_google_redirect(code: str = Form(...), redirect_uri: str = Form(...)):
    return await _oauth_google_redirect(code, redirect_uri)


async def _oauth_google_redirect(code: str, redirect_uri: str) -> dict | int:
    access_data, access_data_error = get_token(code, redirect_uri)

    if access_data_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    userinfo, userinfo_error = get_userinfo(access_data['token_type'], access_data['access_token'])
    if userinfo_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    new_user = UserModel(google_id=userinfo['id'], name=userinfo['name'], email=userinfo['email'],
                         picture=userinfo['picture'], locale=userinfo['locale'],
                         access_token=access_data['access_token'], refresh_token=access_data['refresh_token'])

    user = await get_or_create(new_user)

    access_token, refresh_token = await create_tokens({'sub': str(user.id)}, {'sub': str(user.id)})

    response = JSONResponse(
        content={'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}
    )
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)

    return response


@router.post('/refresh', response_model=Credentials)
async def oauth_google_redirect(refresh_token: str = Cookie(...)):
    if not await is_token_exits(refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    current_user = await get_current_user(refresh_token)

    await remove_token(refresh_token)

    access_token, refresh_token = await create_tokens({'sub': str(current_user.id)}, {'sub': str(current_user.id)})

    response = JSONResponse(
        content={'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer'}
    )
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)

    return response
