from pydantic import Field

from models.base import PyObjectId, _BaseModel
from models.bookshelf import BookshelfModel


class UserBase(_BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    google_id: str = Field(..., alias='googleId')
    email: str = Field(...)


class UserCredentialsModel(_BaseModel):
    access_token: str = Field(...)
    expires_in: int = Field(...)
    scope: str | None = Field(None)
    refresh_token: str | None = Field(None)


class UserModel(UserBase):
    credentials: UserCredentialsModel = Field(...)


class UserModelRead(UserBase):
    bookshelves: list[BookshelfModel] = Field([])
