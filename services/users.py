from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument

from db import db
from models import UserModel


async def get_user_by_id(id: str) -> UserModel | None:
    user = await db['users'].find_one({'_id': ObjectId(id)})
    return UserModel(**user) if user else None


async def get_or_create(user: UserModel) -> UserModel:
    new_user = await db['users'].find_one_and_update({'google_id': user.google_id},
                                                     {'$set': jsonable_encoder(user, exclude=['id'], exclude_none=True,
                                                                               exclude_unset=True)},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return UserModel.parse_obj(new_user)


async def update_user_credentials(id: str, access_token: str, refresh_token: str, expires_in: int) -> UserModel:
    new_user = await db['users'].find_one_and_update({'_id': ObjectId(id)},
                                                     {'$set': {'access_token': access_token,
                                                               'refresh_token': refresh_token,
                                                               'expires_in': expires_in}},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return UserModel.parse_obj(new_user)
