import json

from fastapi import APIRouter, Form, Query, HTTPException, status, Cookie, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse, Response

from data.config import SERVER_URL, FRONTEND_URL
from exceptions import GoogleTokenError, GoogleCodeTokenError
from models import UserModel, CredentialsResponse, UserModelRead, UserCredentialsModel
from services.auth import is_token_exits, remove_token, get_current_user, create_tokens, REFRESH_TOKEN_EXPIRE_MINUTES
from services.google import generate_auth_uri, get_token, get_tokeninfo
from services.synchronization import synchronize_books, synchronize_user
from services.users import update_or_create_user
from utils.misc.logging import logger

router = APIRouter(tags=['Oauth2'])


@router.get('/google', response_description='Oauth via google', response_class=RedirectResponse)
async def oauth_google(redirect_uri: str = f'{SERVER_URL}/oauth/google/redirect',
                       state: str | None = Query(None, include_in_schema=False)):
    uri = generate_auth_uri(redirect_uri=redirect_uri,
                            scope=['https://www.googleapis.com/auth/books',
                                   'https://www.googleapis.com/auth/userinfo.email',
                                   'https://www.googleapis.com/auth/userinfo.profile', 'openid'], state=state)

    return RedirectResponse(uri)


@router.get('/google/redirect', include_in_schema=False)
async def oauth_google_redirect(background_tasks: BackgroundTasks, code: str, scope: str,
                                redirect_uri: str = f'{SERVER_URL}/oauth/google/redirect'):
    # If user have not given permission to manage google books
    if 'https://www.googleapis.com/auth/books' not in scope:
        return await oauth_google(redirect_uri)

    return await _oauth_google_redirect(code, redirect_uri, background_tasks=background_tasks,
                                        redirect_to_frontend=True)


@router.post('/google/redirect', include_in_schema=False, response_model=CredentialsResponse,
             description='Oauth2 for swagger docs')
async def oauth_google_redirect_swagger(background_tasks: BackgroundTasks, code: str = Form(...),
                                        redirect_uri: str = Form(...), swagger: bool = Query(False)):
    return await _oauth_google_redirect(code, redirect_uri, background_tasks=background_tasks, swagger=swagger)


async def _oauth_google_redirect(code: str, redirect_uri: str, background_tasks: BackgroundTasks = None,
                                 swagger=False, redirect_to_frontend=False) -> JSONResponse:
    try:
        access_data = get_token(code, redirect_uri)
        tokeninfo = get_tokeninfo(access_data.access_token)
    except (GoogleTokenError, GoogleCodeTokenError) as e:
        logger.error(f'{type(e).__name__} {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    user_credentials = UserCredentialsModel(access_token=access_data.access_token,
                                            refresh_token=access_data.refresh_token,
                                            scope=tokeninfo.scope, expires_in=tokeninfo.exp)
    new_user = UserModel(google_id=tokeninfo.sub, email=tokeninfo.email, credentials=user_credentials)
    user = await update_or_create_user(new_user)

    access_token, refresh_token = await create_tokens({'sub': str(user.id)}, {'sub': str(user.id)})
    response_content = {'accessToken': access_token,
                        'user': jsonable_encoder(UserModelRead.parse_obj(jsonable_encoder(user))),
                        'tokenType': 'Bearer'}

    # Snake case for swagger docs
    if swagger:
        response_content['access_token'] = access_token

    if redirect_to_frontend:
        uri = FRONTEND_URL + '/oauth2-redirect.html#' + json.dumps(response_content)
        response = RedirectResponse(uri)
    else:
        response = JSONResponse(content=response_content)

    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True,
                        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60)  # convert minutes to seconds

    if background_tasks:
        background_tasks.add_task(synchronize_user, user=user)
        background_tasks.add_task(synchronize_books, user=user)

    return response


@router.get('/refresh', response_model=CredentialsResponse)
async def oauth_refresh_token(refresh_token: str = Cookie(...)):
    if not await is_token_exits(refresh_token):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    current_user = await get_current_user(refresh_token)

    await remove_token(refresh_token)

    access_token, refresh_token = await create_tokens({'sub': str(current_user.id)}, {'sub': str(current_user.id)})
    response = JSONResponse(
        content={'accessToken': access_token,
                 'user': jsonable_encoder(UserModelRead.parse_obj(current_user)),
                 'tokenType': 'Bearer'}
    )
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True,
                        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60)  # convert minutes to seconds

    return response


@router.get('/logout')
async def logout(refresh_token: str = Cookie(None)):
    if refresh_token:
        await remove_token(refresh_token)

    response = Response(status_code=200)
    response.delete_cookie('refresh_token')

    return response
