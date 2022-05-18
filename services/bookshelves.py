import json
import time

import requests

from config import GOOGLE_BOOKS_API_KEY
from models import BookshelfModel, BookModel, BooksResponse, UserModel, UserCredentialsModel
from services.google import get_refreshed_token, get_tokeninfo
from services.users import update_user_credentials


class BookshelvesService:
    @classmethod
    async def create(cls, user: UserModel):
        self = BookshelvesService()
        self.user = user
        if user.credentials.expires_in <= int(time.time()) + 5:
            access_data, access_data_error = get_refreshed_token(user.credentials.refresh_token)
            tokeninfo, tokeninfo_error = get_tokeninfo(access_data['access_token'])

            user_credentials = UserCredentialsModel(
                access_token=access_data['access_token'],
                refresh_token=access_data['refresh_token'] if 'refresh_token' in access_data
                else user.credentials.refresh_token,
                expires_in=tokeninfo['exp'], scope=tokeninfo['scope'],
            )
            new_user = await update_user_credentials(user.id, user_credentials)
            self.user = new_user
        return self

    def get_my_bookshelves(self) -> set[list[BookshelfModel] | dict, bool]:
        url = 'https://www.googleapis.com/books/v1/mylibrary/bookshelves'
        headers = {
            'Authorization': f'Bearer {self.user.credentials.access_token}'
        }
        params = {'key': GOOGLE_BOOKS_API_KEY}

        response = requests.request('GET', url, headers=headers, params=params).json()
        if 'error' in response:
            return response, True

        bookshelves = []
        for item in response['items']:
            if item['id'] in [1, 5, 6, 7, 8, 9]:
                continue
            bookshelves.append(BookshelfModel.parse_obj(item))

        return bookshelves, False

    def get_bookshelf_books(self, id: int, start_index: int = None, max_results: int = None,
                            print_type: str = None, projection: str = None) -> set[BooksResponse | dict, bool]:
        url = f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{id}/volumes'
        headers = {
            'Authorization': f'Bearer {self.user.credentials.access_token}'
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
        if response['totalItems'] == 0:
            return BooksResponse(total_items=response['totalItems'], items=[]), False

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

    def add_book_to_bookshelf(self, bookshelf_id: int, book_id: str):
        url = f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{bookshelf_id}/addVolume'

        payload = json.dumps({
            'volumeId': book_id
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.user.credentials.access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.request('POST', url, headers=headers, data=payload).json()
        if 'error' in response:
            return response, True

        return {'ok': True}, False

    def remove_book_from_bookshelf(self, bookshelf_id: int, book_id: str):
        url = f'https://www.googleapis.com/books/v1/mylibrary/bookshelves/{bookshelf_id}/removeVolume'

        payload = json.dumps({
            'volumeId': book_id
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.user.credentials.access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.request('POST', url, headers=headers, data=payload).json()
        if 'error' in response:
            return response, True

        return {'ok': True}, False
