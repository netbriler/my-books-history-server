import requests
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument

from config import GOOGLE_BOOKS_API_KEY
from db import db
from models import BookModel, BooksResponse


def search_books(query: str, start_index: int = None, max_results: int = None, print_type: str = None,
                 projection: str = None) -> set[BooksResponse | dict, bool]:
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

    books = []
    for item in response['items']:
        volume_info = item['volumeInfo']
        books.append(BookModel(
            google_id=item['id'],
            title=volume_info['title'] if 'title' in volume_info else '',
            authors=volume_info['authors'] if 'authors' in volume_info else [],
            image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
        ))

    return BooksResponse(total_items=response['totalItems'], items=books), False


def get_book_from_google(id: str) -> set[BookModel, bool]:
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


async def get_all_by_user_id(id: str) -> list[BookModel] | None:
    books = []
    cursor = db['books'].find({'user_id': str(id)})

    for document in await cursor.to_list(length=await db['books'].count_documents({'user_id': str(id)})):
        books.append(document)

    return [BookModel(**book) for book in books] if books else None


async def get_or_create_book(book: BookModel) -> BookModel:
    new_book = await db['books'].find_one_and_update({'google_id': book.google_id},
                                                     {'$set': jsonable_encoder(book, exclude=['id'], exclude_none=True,
                                                                               exclude_unset=True)},
                                                     return_document=ReturnDocument.AFTER, upsert=True)

    return BookModel.parse_obj(new_book)
