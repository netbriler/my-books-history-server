from bson import ObjectId
from pydantic import Field, BaseModel

from models.base import PyObjectId


class BookModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    google_id: str = Field(...)
    title: str = Field(...)
    authors: list[str] = Field([])
    image: str = Field(None)
    bookshelves: list[int] = Field([])
    user_id: PyObjectId = Field(None)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BooksResponse(BaseModel):
    total_items: int = Field(..., alias='totalItems')
    items: list[BookModel] = Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
