import json
import time

import requests
from fastapi import HTTPException, status

from data.config import GOOGLE_BOOKS_API_KEY
from exceptions import GoogleTokenError, GoogleGetBookshelvesError, GoogleGetBookshelfError, GoogleAddToBookshelfError, \
    GoogleRemoveFromBookshelfError
from models import BookshelfModel, BookModel, UserModel
from services.google import refresh_user_tokens
from utils.misc.logging import logger


class GoogleBookshelvesService:
    DEFAULT_SKIP_BOOKSHELVES = [1, 5, 6, 7, 8, 9]

    @classmethod
    async def create(cls, user: UserModel):
        self = GoogleBookshelvesService()
        self.user = user
        if user.credentials.expires_in <= int(time.time()) + 5:
            logger.error(f'Try refresh user tokens, {user.id=}')
            try:
                new_user = await refresh_user_tokens(user)
            except GoogleTokenError as e:
                logger.error(f'{type(e).__name__} {e}')
                raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='Lose permission to manage google books')

            self.user = new_user
        return self

    def get_my_bookshelves(self, skip_bookshelves=None) -> list[BookshelfModel]:
        if skip_bookshelves is None:
            skip_bookshelves = self.DEFAULT_SKIP_BOOKSHELVES
        url = 'https://www.googleapis.com/books/v1/mylibrary/bookshelves'
        headers = {
            'Authorization': f'Bearer {self.user.credentials.access_token}'
        }
        params = {'key': GOOGLE_BOOKS_API_KEY}

        response = requests.request('GET', url, headers=headers, params=params).json()
        if 'error' in response:
            raise GoogleGetBookshelvesError(response)

        bookshelves = []
        for item in response['items']:
            if item['id'] in skip_bookshelves:
                continue
            bookshelves.append(BookshelfModel(id=item['id'], title=item['title'], total_items=item['volumeCount']))

        return bookshelves

    def get_bookshelf_books(self, id: int, start_index: int = None, max_results: int = None,
                            print_type: str = 'books', projection: str = 'lite') -> list[BookModel]:
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
            raise GoogleGetBookshelfError(response)
        if response['totalItems'] == 0:
            return []

        books = []
        for item in response['items']:
            volume_info = item['volumeInfo']
            books.append(BookModel(
                google_id=item['id'],
                title=volume_info['title'] if 'title' in volume_info else '',
                authors=volume_info['authors'] if 'authors' in volume_info else [],
                image=volume_info['imageLinks']['thumbnail'] if volume_info['readingModes']['image'] else None,
            ))

        return books

    def get_all_bookshelf_books(self) -> list[BookModel]:
        bookshelves = self.get_my_bookshelves()

        total_books = {}
        for bookshelf in bookshelves:
            start_index = 0
            while start_index < bookshelf.total_items:
                books = self.get_bookshelf_books(bookshelf.id, start_index, max_results=40)

                for book in books:
                    if book.google_id not in total_books:
                        book.bookshelves = [bookshelf.id]
                        total_books[book.google_id] = book
                    else:
                        total_books[book.google_id].bookshelves.append(bookshelf.id)

                start_index += 40

        return total_books.values()

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
            raise GoogleAddToBookshelfError(response)

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
            raise GoogleRemoveFromBookshelfError(response)
