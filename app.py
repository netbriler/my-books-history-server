from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_SERVERS
from routes.auth import router as AuthRouter
from routes.user import router as UserRouter
from routes.book import router as BookRouter
from routes.bookshelve import router as BookshelveRouter

app = FastAPI(title='My Books History')

if CORS_SERVERS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_SERVERS.split(','),
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

app.include_router(AuthRouter, prefix='/oauth')
app.include_router(UserRouter, prefix='/api/v1/user')
app.include_router(BookRouter, prefix='/api/v1/books')
app.include_router(BookshelveRouter, prefix='/api/v1/bookshelves')
