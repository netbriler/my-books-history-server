from fastapi import FastAPI

from routes.auth import router as AuthRouter
from routes.user import router as UserRouter
from routes.book import router as BookRouter

app = FastAPI(title='Test')

app.include_router(AuthRouter, prefix='/oauth')
app.include_router(UserRouter, prefix='/api/v1/user')
app.include_router(BookRouter, prefix='/api/v1/books')
