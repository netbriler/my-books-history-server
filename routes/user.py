from fastapi import APIRouter, Depends

from models import UserModel, UserModelRead
from services.auth import get_current_active_user
from services.google_bookshelves import GoogleBookshelvesService

router = APIRouter(tags=['User'])


@router.get('/me/', response_model=UserModelRead)
async def get_current_user(current_user: UserModel = Depends(get_current_active_user)):
    service = await GoogleBookshelvesService.create(current_user)
    bookshelves, is_error = service.get_my_bookshelves()

    user = UserModelRead(**current_user.dict())
    user.bookshelves = bookshelves if not is_error else []

    return user
