from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import FRONTEND_URL
from routes.auth import router as AuthRouter
from routes.book import router as BookRouter
from routes.bookshelf import router as BookshelveRouter
from routes.user import router as UserRouter

app = FastAPI(title='My Books History')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(AuthRouter, prefix='/oauth')
app.include_router(UserRouter, prefix='/api/v1/user')
app.include_router(BookRouter, prefix='/api/v1/books')
app.include_router(BookshelveRouter, prefix='/api/v1/bookshelves')


@app.get('/', response_class=RedirectResponse, name='Redirect to frontend', tags=['Frontend'])
def frontend():
    return RedirectResponse(FRONTEND_URL)
