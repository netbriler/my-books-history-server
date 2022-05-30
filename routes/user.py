import logging

from fastapi import APIRouter, Depends, HTTPException, status

from models import UserModel, UserModelRead
from services.auth import get_current_active_user
from services.google_bookshelves import GoogleBookshelvesService

router = APIRouter(tags=['User'])


@router.get('/me/', response_model=UserModelRead)
async def get_current_user(current_user: UserModel = Depends(get_current_active_user)):
    service = await GoogleBookshelvesService.create(current_user)
    bookshelves, is_error = service.get_my_bookshelves()

    if is_error:
        logging.error(f'{current_user=} {bookshelves=}')
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='Lose permission to manage google books')

    user = UserModelRead(**current_user.dict())
    user.bookshelves = bookshelves if not is_error else []

    return user
