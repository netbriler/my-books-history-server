from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from config import JWT_SECRET
from db import db
from models.user import UserModel

SECRET_KEY = JWT_SECRET
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 120


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None


oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl='/oauth/google/redirect', authorizationUrl='/oauth/google',
                                              description='__Leave blank credentials__')


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


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
        token_data = TokenData(id=id)
    except JWTError as e:
        print(e)
        raise credentials_exception
    user = await db['users'].find_one({'_id': ObjectId(token_data.id)})
    if user is None:
        raise credentials_exception
    return UserModel(**user)


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)):
    return current_user
