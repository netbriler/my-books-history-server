from bson import ObjectId
from pydantic import BaseModel, Field

from models.base import PyObjectId


class UserBase(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    google_id: str = Field(...)
    name: str = Field(...)
    email: str = Field(...)
    picture: str = Field(...)
    locale: str = Field('en')

    class Config:
        json_encoders = {ObjectId: str}


class UserModel(UserBase):
    access_token: str = Field(...)
    refresh_token: str = Field(...)


class UserModelRead(UserBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
