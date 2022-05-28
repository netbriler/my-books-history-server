import json
import time

import requests
from fastapi import HTTPException, status

from config import GOOGLE_BOOKS_API_KEY
from models import BookshelfModel, BookModel, UserModel, UserCredentialsModel
from services.google import get_refreshed_token, get_tokeninfo
from services.users import update_user_credentials


class GoogleBookshelvesService:
    DEFAULT_SKIP_BOOKSHELVES = [1, 5, 6, 7, 8, 9]

    @classmethod
    async def create(cls, user: UserModel):
        self = GoogleBookshelvesService()
        self.user = user
        if user.credentials.expires_in <= int(time.time()) + 5:
            access_data, access_data_error = get_refreshed_token(user.credentials.refresh_token)
            if access_data_error:
                raise HTTPException(status_code=status.HTTP_423_LOCKED)

            tokeninfo, tokeninfo_error = get_tokeninfo(access_data['access_token'])
            if tokeninfo_error:
                raise HTTPException(status_code=status.HTTP_423_LOCKED)

            user_credentials = UserCredentialsModel(
                access_token=access_data['access_token'],
                refresh_token=access_data['refresh_token'] if 'refresh_token' in access_data
                else user.credentials.refresh_token,
                expires_in=tokeninfo['exp'], scope=tokeninfo['scope'],
            )
            new_user = await update_user_credentials(user.id, user_credentials)
            self.user = new_user
        return self

    def get_my_bookshelves(self, skip_bookshelves=None) -> tuple[list[BookshelfModel] | dict, bool]:
        if skip_bookshelves is None:
            skip_bookshelves = self.DEFAULT_SKIP_BOOKSHELVES
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
            if item['id'] in skip_bookshelves:
                continue
            bookshelves.append(BookshelfModel(id=item['id'], title=item['title'], total_items=item['volumeCount']))

        return bookshelves, False

    def get_bookshelf_books(self, id: int, start_index: int = None, max_results: int = None,
                            print_type: str = 'books', projection: str = 'lite') -> tuple[BookModel | dict, bool]:
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
            return [], False

        books = []
        for item in response['items']:
            volume_info = item['volumeInfo']
            books.append(BookModel(
                google_id=item['id'],
                title=volume_info['title'] if 'title' in volume_info else '',
                authors=volume_info['authors'] if 'authors' in volume_info else [],
                image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
            ))

        return books, False

    def get_all_bookshelf_books(self) -> list[BookModel]:
        bookshelves, is_error = self.get_my_bookshelves()
        if is_error:
            return bookshelves, True

        total_books = {}
        for bookshelf in bookshelves:
            start_index = 0
            while start_index < bookshelf.total_items:
                books, is_error = self.get_bookshelf_books(bookshelf.id, start_index, max_results=40)
                if is_error:
                    return books, True

                for book in books:
                    if book.google_id not in total_books:
                        book.bookshelves = [bookshelf.id]
                        total_books[book.google_id] = book
                    else:
                        total_books[book.google_id].bookshelves.append(bookshelf.id)

                start_index += 40

        return total_books.values(), False

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
