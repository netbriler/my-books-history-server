from bson import ObjectId
from pydantic import BaseModel, Field

from models.base import PyObjectId


class UserBase(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    google_id: str = Field(..., alias='googleId')
    email: str = Field(...)

    class Config:
        json_encoders = {ObjectId: str}


class UserModel(UserBase):
    access_token: str = Field(...)
    expires_in: int = Field(...)
    scope: str = Field(...)
    refresh_token: str | None = Field(None)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserModelRead(UserBase):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
