from exceptions import GoogleAddToBookshelfError, GoogleRemoveFromBookshelfError
from models import UserModel, BookModel
from services.books import get_or_create_book
from services.google_bookshelves import GoogleBookshelvesService
from utils.misc.logging import logger


async def synchronize_books(user: UserModel):
    service = await GoogleBookshelvesService.create(user)
    books = service.get_all_bookshelf_books()

    for book in books:
        book.user_id = user.id
        await get_or_create_book(book)


async def synchronize_bookshelves_books(user: UserModel, old_bookshelves: list, book: BookModel):
    old_bookshelves = set(old_bookshelves) if old_bookshelves else set()
    new_bookshelves = set(book.bookshelves)

    # Find difference between old and new bookshelves
    to_delete = old_bookshelves.difference(new_bookshelves)
    to_add = new_bookshelves.difference(old_bookshelves)

    service = await GoogleBookshelvesService.create(user)

    for id in to_delete:
        try:
            service.remove_book_from_bookshelf(id, book.google_id)
        except GoogleRemoveFromBookshelfError as e:
            logger.error(f'{type(e).__name__} {e}')

    for id in to_add:
        try:
            service.add_book_to_bookshelf(id, book.google_id)
        except GoogleAddToBookshelfError as e:
            logger.error(f'{type(e).__name__} {e}')
