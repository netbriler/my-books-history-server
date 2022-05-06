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
                                                     {'$set': jsonable_encoder(user, exclude=['id'])},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return UserModel.parse_obj(new_user)
