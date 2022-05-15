from fastapi import APIRouter, HTTPException, status, Depends, Query, Form

from models import BookshelvesModelRead, UserModel, BooksResponse
from services.auth import get_current_active_user
from services.bookshelves import get_my_bookshelves, get_bookshelve_books, add_book_to_bookshelve, \
    remove_book_from_bookshelve

router = APIRouter(tags=['Bookshelves'])


@router.get('/', response_model=list[BookshelvesModelRead])
async def get_bookshelves(current_user: UserModel = Depends(get_current_active_user)):
    bookshelves, is_error = get_my_bookshelves(current_user.access_token)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return bookshelves


@router.get('/{id}/', response_model=BooksResponse)
async def get_books(id: int, start_index: int = Query(0, alias='startIndex', ge=0),
                    max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                    print_type: str = Query('books', alias='printType'), projection: str = Query('lite'),
                    current_user: UserModel = Depends(get_current_active_user)):
    books, is_error = get_bookshelve_books(current_user.access_token, id,
                                           start_index, max_results, print_type, projection)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return books


@router.post('/{id}/')
async def add_book(id: int, book_id: str = Form(..., alias='bookId'),
                   current_user: UserModel = Depends(get_current_active_user)):
    response, is_error = add_book_to_bookshelve(current_user.access_token, id, book_id)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return response


@router.delete('/{id}/')
async def remove_book(id: int, book_id: str = Form(..., alias='bookId'),
                      current_user: UserModel = Depends(get_current_active_user)):
    response, is_error = remove_book_from_bookshelve(current_user.access_token, id, book_id)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return response
