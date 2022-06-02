from fastapi import FastAPI, Request
from fastapi.exceptions import StarletteHTTPException, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from data.config import FRONTEND_URL
from routes.auth import router as AuthRouter
from routes.book import router as BookRouter
from routes.bookshelf import router as BookshelveRouter
from routes.user import router as UserRouter
from services.auth import remove_token

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


@app.exception_handler(StarletteHTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    response = JSONResponse({'detail': exc.detail}, status_code=exc.status_code)

    if exc.status_code == 423:
        refresh_token = request.cookies.get('refresh_token')
        if refresh_token:
            await remove_token(refresh_token)

        response.delete_cookie('refresh_token')

    return response


@app.get('/', response_class=RedirectResponse, name='Redirect to frontend', tags=['Frontend'])
def frontend():
    return RedirectResponse(FRONTEND_URL)
