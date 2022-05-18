from pydantic import Field

from models.base import _BaseModel


class BookshelfModel(_BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    volume_count: int = Field(0, alias='volumeCount')


class BookshelfModelRead(BookshelfModel):
    ...
