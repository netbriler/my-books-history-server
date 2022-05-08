import requests

from config import GOOGLE_BOOKS_API_KEY
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
            id=item['id'],
            title=volume_info['title'] if 'title' in volume_info else '',
            authors=volume_info['authors'] if 'authors' in volume_info else [],
            image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
        ))

    return BooksResponse(total_items=response['totalItems'], items=books), False


def get_my_bookshelves(access_token: str) -> set[dict, bool]:
    url = 'https://www.googleapis.com/books/v1/mylibrary/bookshelves'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request('GET', url, headers=headers).json()

    bookshelves = []
    for item in response['items']:
        volume_info = item['volumeInfo']
        books.append(BookModel(
            id=item['id'],
            title=volume_info['title'] if 'title' in volume_info else '',
            authors=volume_info['authors'] if 'authors' in volume_info else [],
            image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
        ))

    return response, 'error' in response

