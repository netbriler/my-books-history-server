from fastapi import APIRouter, HTTPException, status, Query

from models import BooksResponse
from services.books import search_books

router = APIRouter(tags=['Books'])


@router.get('/search', response_model=BooksResponse)
async def search(q: str = Query(...), start_index: int = Query(0, alias='startIndex', ge=0),
                 max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                 print_type: str = Query('books', alias='printType'), projection: str = Query('lite')):
    books, is_error = search_books(q, start_index, max_results, print_type, projection)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return books
