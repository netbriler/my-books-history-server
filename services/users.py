from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument

from utils.db import db
from models import UserModel, UserCredentialsModel


async def get_user_by_id(id: str) -> UserModel | None:
    user = await db['users'].find_one({'_id': ObjectId(id)})
    return UserModel.parse_obj(user) if user else None


async def get_user_by_google_id(google_id: str) -> UserModel | None:
    user = await db['users'].find_one({'google_id': google_id})
    return UserModel.parse_obj(user) if user else None


async def update_or_create_user(user: UserModel) -> UserModel:
    new_user = await db['users'].find_one_and_update({'google_id': user.google_id},
                                                     {'$set': jsonable_encoder(user, exclude=['id'], exclude_none=True,
                                                                               exclude_unset=True)},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return UserModel.parse_obj(new_user)


async def update_user_credentials(id: str, credentials: UserCredentialsModel) -> UserModel:
    new_user = await db['users'].find_one_and_update({'_id': ObjectId(id)},
                                                     {'$set': {'credentials': credentials.dict()}},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return UserModel.parse_obj(new_user)
