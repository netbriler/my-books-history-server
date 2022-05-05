from datetime import datetime, timedelta

import aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt

from config import JWT_SECRET, REDIS_URL
from models.user import UserModel
from services.users import get_user_by_id

SECRET_KEY = JWT_SECRET
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 120
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 days

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl='/oauth/google/redirect', authorizationUrl='/oauth/google',
                                              description='__Leave blank credentials__')


async def create_tokens(access_data: dict, refresh_data: dict) -> set[str, str]:
    access_data.update({'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    access_token = jwt.encode(access_data, SECRET_KEY, algorithm=ALGORITHM)

    refresh_data.update({'exp': datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)})
    refresh_token = jwt.encode(refresh_data, SECRET_KEY, algorithm=ALGORITHM)

    await save_token(refresh_token, 'white', REFRESH_TOKEN_EXPIRE_MINUTES * 60)  # convert minutes to seconds

    return access_token, refresh_token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get('sub')
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    return current_user


async def save_token(token: str, value: str, ex: int):
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    await redis.set(token, value, ex=ex)

    await redis.close()


async def remove_token(token: str):
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    await redis.delete(token)

    await redis.close()


async def is_token_exits(token: str):
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    result = await redis.exists(token)

    await redis.close()

    return result
