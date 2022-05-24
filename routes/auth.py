from fastapi import APIRouter, Form, Query, HTTPException, status, Cookie, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse, JSONResponse, Response

from config import SERVER_URL, FRONTEND_URL
from models import UserModel, CredentialsResponse, UserModelRead, UserCredentialsModel
from services.auth import is_token_exits, remove_token, get_current_user, create_tokens, REFRESH_TOKEN_EXPIRE_MINUTES
from services.google import generate_auth_uri, get_token, get_tokeninfo
from services.synchronization import synchronize_books
from services.users import get_or_create

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

    resource = await _oauth_google_redirect(code, redirect_uri, background_tasks=background_tasks)

    # If user have not given permission to manage google books
    if 'https://www.googleapis.com/auth/books' not in scope:
        return await oauth_google(redirect_uri)

    uri = FRONTEND_URL + '/oauth2-redirect.html#' + resource.body.decode('utf-8')
    return RedirectResponse(uri)


@router.post('/google/redirect', include_in_schema=False, response_model=CredentialsResponse,
             description='Oauth2 for swagger docs')
async def oauth_google_redirect_swagger(background_tasks: BackgroundTasks, code: str = Form(...),
                                        redirect_uri: str = Form(...), swagger: bool = Query(False)):
    return await _oauth_google_redirect(code, redirect_uri, background_tasks=background_tasks, swagger=swagger)


async def _oauth_google_redirect(code: str, redirect_uri: str, background_tasks: BackgroundTasks = None,
                                 swagger=False) -> JSONResponse:
    access_data, access_data_error = get_token(code, redirect_uri)

    if access_data_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    tokeninfo, tokeninfo_error = get_tokeninfo(access_data['access_token'])
    if tokeninfo_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    user_credentials = UserCredentialsModel(access_token=access_data['access_token'],
                                            refresh_token=access_data['refresh_token']
                                            if 'refresh_token' in access_data else None,
                                            scope=tokeninfo['scope'], expires_in=tokeninfo['exp'])
    new_user = UserModel(google_id=tokeninfo['sub'], email=tokeninfo['email'], credentials=user_credentials)

    user = await get_or_create(new_user)

    access_token, refresh_token = await create_tokens({'sub': str(user.id)}, {'sub': str(user.id)})

    response_content = {'accessToken': access_token,
                        'user': jsonable_encoder(UserModelRead.parse_obj(jsonable_encoder(user))),
                        'tokenType': 'Bearer'}

    # Snake case for swagger docs
    if swagger:
        response_content['access_token'] = access_token

    response = JSONResponse(content=response_content)
    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True,
                        max_age=REFRESH_TOKEN_EXPIRE_MINUTES)

    if background_tasks:
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
                        max_age=REFRESH_TOKEN_EXPIRE_MINUTES)

    return response


@router.get('/logout')
async def logout(refresh_token: str = Cookie(None)):
    if refresh_token:
        await remove_token(refresh_token)

    return Response(status_code=200)
