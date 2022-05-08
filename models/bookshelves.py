from bson import ObjectId
from pydantic import BaseModel, Field

from models.base import PyObjectId


class BookshelvesModel(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    volume_count: int = Field(0, alias='volumeCount')

    class Config:
        allow_population_by_field_name = True


class BookshelvesModelRead(BookshelvesModel):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
