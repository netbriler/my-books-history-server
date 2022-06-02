from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import GoogleGetBookshelvesError
from models import UserModel, UserModelRead
from services.auth import get_current_active_user
from services.google_bookshelves import GoogleBookshelvesService
from utils.misc.logging import logger

router = APIRouter(tags=['User'])


@router.get('/me/', response_model=UserModelRead)
async def get_current_user(current_user: UserModel = Depends(get_current_active_user)):
    service = await GoogleBookshelvesService.create(current_user)

    try:
        bookshelves = service.get_my_bookshelves()
    except GoogleGetBookshelvesError as e:
        logger.error(f'{type(e).__name__} {e}')
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail='Lose permission to manage google books')

    user = UserModelRead(**current_user.dict())
    user.bookshelves = bookshelves

    return user
