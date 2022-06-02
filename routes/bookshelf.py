from fastapi import APIRouter, HTTPException, status, Depends, Query

from exceptions import GoogleGetBookshelvesError
from models import BookshelfModelRead, UserModel, BooksResponse
from services.auth import get_current_active_user
from services.books import get_books_by_user_id
from services.google_bookshelves import GoogleBookshelvesService
from utils.misc.logging import logger

router = APIRouter(tags=['Bookshelves'])


@router.get('/', response_model=list[BookshelfModelRead])
async def get_bookshelves(current_user: UserModel = Depends(get_current_active_user)):
    service = await GoogleBookshelvesService.create(current_user)

    try:
        bookshelves = service.get_my_bookshelves()
    except GoogleGetBookshelvesError as e:
        logger.error(f'{type(e).__name__} {e}')
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='Lose permission to manage google books')

    return bookshelves


@router.get('/{id}/', response_model=BooksResponse)
async def get_books(id: int, start_index: int = Query(0, alias='startIndex', ge=0),
                    max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                    current_user: UserModel = Depends(get_current_active_user)):
    books, total_items = await get_books_by_user_id(current_user.id, bookshelves=[id],
                                                    limit=max_results, offset=start_index)

    return BooksResponse(items=books, total_items=total_items)
