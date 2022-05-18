from pydantic import Field

from models.base import _BaseModel


class BookshelfModel(_BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    total_items: int = Field(..., alias='totalItems')


class BookshelfModelRead(BookshelfModel):
    ...
