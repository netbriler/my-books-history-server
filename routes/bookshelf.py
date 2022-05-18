from fastapi import APIRouter, HTTPException, status, Depends, Query, Form

from models import BookshelfModelRead, UserModel, BooksResponse
from services.auth import get_current_active_user
from services.bookshelves import BookshelvesService

router = APIRouter(tags=['Bookshelves'])


@router.get('/', response_model=list[BookshelfModelRead])
async def get_bookshelves(current_user: UserModel = Depends(get_current_active_user)):
    service = await BookshelvesService.create(current_user)
    bookshelves, is_error = service.get_my_bookshelves()

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return bookshelves


@router.get('/{id}/', response_model=BooksResponse)
async def get_books(id: int, start_index: int = Query(0, alias='startIndex', ge=0),
                    max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                    print_type: str = Query('books', alias='printType'), projection: str = Query('lite'),
                    current_user: UserModel = Depends(get_current_active_user)):
    service = await BookshelvesService.create(current_user)
    books, is_error = service.get_bookshelf_books(id, start_index, max_results, print_type, projection)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return books
