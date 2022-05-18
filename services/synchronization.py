from services.books import get_or_create_book
from services.google_bookshelves import GoogleBookshelvesService


async def synchronize_books(user):
    service = await GoogleBookshelvesService.create(user)
    books, is_error = service.get_all_bookshelf_books()
    if is_error:
        return

    for book in books:
        book.user_id = user.id
        await get_or_create_book(book)
