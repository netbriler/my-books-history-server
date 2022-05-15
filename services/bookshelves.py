import json

import requests

from config import GOOGLE_BOOKS_API_KEY
from models import BookshelvesModel, BookModel, BooksResponse


def get_my_bookshelves(access_token: str) -> set[list[BookshelvesModel] | dict, bool]:
    url = 'https://www.googleapis.com/books/v1/mylibrary/bookshelves'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {'key': GOOGLE_BOOKS_API_KEY}

    response = requests.request('GET', url, headers=headers, params=params).json()
    if 'error' in response:
        return response, True

    bookshelves = []
    for item in response['items']:
        if item['id'] in [1, 5, 6, 7, 8, 9]:
            continue
        bookshelves.append(BookshelvesModel.parse_obj(item))

    return bookshelves, False


def get_bookshelve_books(access_token: str, id: int, start_index: int = None, max_results: int = None,
                         print_type: str = None, projection: str = None) -> set[BooksResponse | dict, bool]:
    url = f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{id}/volumes'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'key': GOOGLE_BOOKS_API_KEY,
        'startIndex': start_index,
        'maxResults': max_results,
        'printType': print_type,
        'projection': projection
    }
    params = dict(filter(lambda i: i[1] is not None, params.items()))

    response = requests.request('GET', url, headers=headers, params=params).json()
    if 'error' in response:
        return response, True

    books = []
    for item in response['items']:
        volume_info = item['volumeInfo']
        books.append(BookModel(
            id=item['id'],
            title=volume_info['title'] if 'title' in volume_info else '',
            authors=volume_info['authors'] if 'authors' in volume_info else [],
            image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
        ))

    return BooksResponse(total_items=response['totalItems'], items=books), False


def add_book_to_bookshelve(access_token: str, bookshelve_id: int, book_id: str):
    url = f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{bookshelve_id}/addVolume'

    payload = json.dumps({
        'volumeId': book_id
    })
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.request('POST', url, headers=headers, data=payload).json()
    if 'error' in response:
        return response, True

    return {'ok': True}, False


def remove_book_from_bookshelve(access_token: str, bookshelve_id: int, book_id: str):
    url = f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{bookshelve_id}/removeVolume'

    payload = json.dumps({
        'volumeId': book_id
    })
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.request('POST', url, headers=headers, data=payload).json()
    if 'error' in response:
        return response, True

    return {'ok': True}, False
