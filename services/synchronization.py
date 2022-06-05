from exceptions import GoogleAddToBookshelfError, GoogleRemoveFromBookshelfError, GoogleGetBookshelvesError, GoogleGetUserinfoError
from models import UserModel, BookModel
from services.books import get_or_create_book
from services.google import get_userinfo
from services.google_bookshelves import GoogleBookshelvesService
from services.users import update_or_create_user
from utils.misc.logging import logger


async def synchronize_user(user: UserModel):
    service = await GoogleBookshelvesService.create(user)
    try:
        bookshelves = service.get_my_bookshelves()
        user.bookshelves = bookshelves
    except GoogleGetBookshelvesError as e:
        logger.error(f'{type(e).__name__} {e}')

    try:
        userinfo = get_userinfo(service.user.credentials.access_token)
        user.email = userinfo.email
        user.name = userinfo.name
        user.picture = userinfo.picture
        user.locale = userinfo.locale
    except GoogleGetUserinfoError as e:
        logger.error(f'{type(e).__name__} {e}')

    await update_or_create_user(user)


async def synchronize_books(user: UserModel):
    service = await GoogleBookshelvesService.create(user)
    try:
        books = service.get_all_bookshelf_books()
    except GoogleGetBookshelvesError as e:
        logger.error(f'{type(e).__name__} {e}')
        return

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
