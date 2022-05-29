import requests
from bson import ObjectId
from pymongo import ReturnDocument

from config import GOOGLE_BOOKS_API_KEY
from db import db
from models import BookModel, BooksResponse, BookModelRead


def search_google_books(query: str, start_index: int = None, max_results: int = None, print_type: str = None,
                        projection: str = None) -> tuple[BooksResponse | dict, bool]:
    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': query,
        'key': GOOGLE_BOOKS_API_KEY,
        'startIndex': start_index,
        'maxResults': max_results,
        'printType': print_type,
        'projection': projection
    }
    params = dict(filter(lambda i: i[1] is not None, params.items()))

    response = requests.request('GET', url, params=params).json()
    if 'error' in response:
        return response, True

    if not response['totalItems']:
        return BooksResponse(total_items=response['totalItems'], items=[]), False

    books = []
    for item in response['items']:
        volume_info = item['volumeInfo']
        books.append(BookModelRead(
            google_id=item['id'],
            title=volume_info['title'] if 'title' in volume_info else '',
            authors=volume_info['authors'] if 'authors' in volume_info else [],
            image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
        ))

    return BooksResponse(total_items=response['totalItems'], items=books), False


def get_book_from_google(id: str) -> tuple[BookModel | dict, bool]:
    url = f'https://www.googleapis.com/books/v1/volumes/{id}/'
    params = {
        'key': GOOGLE_BOOKS_API_KEY,
    }

    response = requests.request('GET', url, params=params).json()
    if 'error' in response:
        return response, True

    volume_info = response['volumeInfo']
    book = BookModel(
        google_id=response['id'],
        title=volume_info['title'] if 'title' in volume_info else '',
        authors=volume_info['authors'] if 'authors' in volume_info else [],
        image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
    )

    return book, False


async def get_books_by_user_id(user_id: ObjectId, bookshelves: list[int] = None,
                               google_ids: list[str] = None, limit: int = None,
                               offset: int = 0) -> tuple[list[BookModelRead], int]:
    query = {'user_id': user_id}

    if bookshelves:
        query['bookshelves'] = {'$in': bookshelves}

    if google_ids:
        query['google_id'] = {'$in': google_ids}

    total_items = await db['books'].count_documents(query)

    if google_ids:
        length = len(google_ids)
    elif not limit:
        length = total_items
    else:
        length = limit

    books = []
    for document in await db['books'].find(query).skip(offset).limit(limit).to_list(length=length):
        books.append(document)

    return [BookModelRead(**book) for book in books] if books else [], total_items


async def get_book(user_id: ObjectId, book_id: str) -> BookModel | None:
    book = await db['books'].find_one({'user_id': user_id, 'google_id': book_id})
    return BookModel.parse_obj(book) if book else None


async def get_or_create_book(book: BookModel) -> BookModel:
    new_book = await db['books'].find_one_and_update({'google_id': book.google_id, 'user_id': book.user_id},
                                                     {'$set': book.dict()},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return BookModel.parse_obj(new_book)
