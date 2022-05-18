from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query, Depends, Form

from models import BooksResponse, UserModel
from services.auth import get_current_active_user
from services.books import search_books, get_book_from_google, get_or_create_book, get_books_by_user_id

router = APIRouter(tags=['Books'])


@router.get('/search', response_model=BooksResponse)
async def search(q: str = Query(...), start_index: int = Query(0, alias='startIndex', ge=0),
                 max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                 print_type: str = Query('books', alias='printType'), projection: str = Query('lite'),
                 current_user: UserModel = Depends(get_current_active_user)):
    books, is_error = search_books(q, start_index, max_results, print_type, projection)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    found_books_ids = list(map(lambda b: b.google_id, books.items))
    # get from the database only found books through the search and not all at once
    external_books = await get_books_by_user_id(current_user.id, found_books_ids)

    result = []
    for item in books.items:
        result.append(next((i for i in external_books if i.google_id == item.google_id), item))

    books.items = result

    return books


@router.post('/{id}/')
async def set_bookshelf(id: str, bookshelves: list[int] = Form(...),
                        current_user: UserModel = Depends(get_current_active_user)):
    book, is_error = get_book_from_google(id)
    book.bookshelves = bookshelves
    book.user_id = ObjectId(current_user.id)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return await get_or_create_book(book)
