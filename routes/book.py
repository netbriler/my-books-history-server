from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query, Depends, Form, BackgroundTasks

from models import BooksResponse, UserModel, BookModelRead
from services.auth import get_current_active_user
from services.books import search_google_books, get_book_from_google, get_or_create_book, get_books_by_user_id, get_book
from services.synchronization import synchronize_bookshelves_books

router = APIRouter(tags=['Books'])


@router.get('/search', response_model=BooksResponse)
async def search(q: str = Query(...), start_index: int = Query(0, alias='startIndex', ge=0),
                 max_results: int = Query(16, alias='maxResults', ge=1, le=40),
                 print_type: str = Query('books', alias='printType'), projection: str = Query('lite'),
                 current_user: UserModel = Depends(get_current_active_user)):
    books, is_error = search_google_books(q, start_index, max_results, print_type, projection)

    if is_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    found_books_ids = list(map(lambda b: b.google_id, books.items))
    # get from the database only found books through the search and not all at once
    external_books, _ = await get_books_by_user_id(current_user.id, google_ids=found_books_ids,
                                                   limit=max_results, offset=start_index)

    result = []
    for item in books.items:
        result.append(next((i for i in external_books if i.google_id == item.google_id), item))

    books.items = result

    return books


@router.get('/{id}/', response_model=BookModelRead)
async def get_book_by_id(id: str, current_user: UserModel = Depends(get_current_active_user)):
    book = await get_book(current_user.id, id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return book


@router.post('/{id}/setBookshelves', response_model=BookModelRead)
async def set_bookshelves(background_tasks: BackgroundTasks, id: str, bookshelves: list[int] = Form(...),
                          current_user: UserModel = Depends(get_current_active_user)):
    book = await get_book(current_user.id, id)
    old_bookshelves = book.bookshelves
    if not book:
        book, is_error = get_book_from_google(id)
        if is_error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        old_bookshelves = None

    book.bookshelves = bookshelves
    book.user_id = ObjectId(current_user.id)

    new_book = await get_or_create_book(book)

    if background_tasks and old_bookshelves:
        background_tasks.add_task(synchronize_bookshelves_books, old_bookshelves=old_bookshelves, book=new_book,
                                  user=current_user)

    return new_book
