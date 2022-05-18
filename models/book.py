from pydantic import Field

from models.base import PyObjectId, _BaseModel


class BookBase(_BaseModel):
    google_id: str = Field(...)
    title: str = Field(...)
    authors: list[str] = Field([])
    image: str = Field(None)
    bookshelves: list[int] = Field([])


class BookModel(BookBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id', exclude=True)
    user_id: PyObjectId = Field(None)


class BookModelRead(BookBase):
    ...


class BooksResponse(_BaseModel):
    total_items: int = Field(..., alias='totalItems')
    items: list[BookModelRead] = Field(...)
