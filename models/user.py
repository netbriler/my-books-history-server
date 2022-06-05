from pydantic import Field

from models.base import PyObjectId, _BaseModel
from models.bookshelf import BookshelfModelRead


class UserBase(_BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    google_id: str = Field(..., alias='googleId')
    email: str | None = Field(None)
    name: str | None = Field(None)
    picture: str | None = Field(None)
    locale: str | None = Field(None)

    bookshelves: list[BookshelfModelRead] = Field(
        [BookshelfModelRead(id=0, title='Favorites'), BookshelfModelRead(id=3, title='Reading now'),
         BookshelfModelRead(id=2, title='To read'), BookshelfModelRead(id=4, title='Have read')]
    )


class UserCredentialsModel(_BaseModel):
    access_token: str = Field(...)
    expires_in: int = Field(...)
    scope: str | None = Field(None)
    refresh_token: str | None = Field(None)


class UserModel(UserBase):
    credentials: UserCredentialsModel = Field(...)


class UserModelRead(UserBase):
    ...
