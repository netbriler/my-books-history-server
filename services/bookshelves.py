import requests

from config import GOOGLE_BOOKS_API_KEY
from models import BookshelvesModel


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
