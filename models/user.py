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
        schema_extra = {
            'example': {
                '_id': '6272cadfg234234ddfg32ef',
                'google_id': '104567567324242523333',
                'name': 'Briler',
                'email': 'netbriler@gmail.com',
                'picture': 'https://lh3.googleusercontent.com/a-/AOh14GjqUeRFM_a6zjxyNADWH7pq-Zjb4yzSpTPp0Nixtg=s96-c',
                'locale': 'en'
            }
        }
