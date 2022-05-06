from pydantic import Field, BaseModel


class BookModel(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    authors: list[str] = Field([])
    published_date: str = Field(..., alias='publishedDate')
    image: str = Field(None)

    class Config:
        allow_population_by_field_name = True


class BooksResponse(BaseModel):
    total_items: int = Field(..., alias='totalItems')
    items: list[BookModel] = Field(...)

    class Config:
        allow_population_by_field_name = True
