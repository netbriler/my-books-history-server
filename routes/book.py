from fastapi import APIRouter, HTTPException, status, Query, Depends

from models import BooksResponse, BookshelvesModelRead, UserModel
from services.auth import get_current_active_user
from services.books import search_books
from services.bookshelves import get_my_bookshelves

router = APIRouter(tags=['Books'])


@router.get('/search', response_model=BooksResponse)
async def search(q: str = Query(...), start_index: int = Query(0, alias='startIndex', ge=0),
                 max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                 print_type: str = Query('books', alias='printType'), projection: str = Query('lite'),
                 _: UserModel = Depends(get_current_active_user)):
    books, is_error = search_books(q, start_index, max_results, print_type, projection)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return books


@router.get('/bookshelves', response_model=list[BookshelvesModelRead])
async def get_bookshelves(current_user: UserModel = Depends(get_current_active_user)):
    bookshelves, is_error = get_my_bookshelves(current_user.access_token)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return bookshelves
