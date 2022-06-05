from fastapi import APIRouter, Depends, HTTPException, status

from exceptions import GoogleGetBookshelvesError
from models import UserModel, UserModelRead
from services.auth import get_current_active_user
from services.google_bookshelves import GoogleBookshelvesService
from utils.misc.logging import logger

router = APIRouter(tags=['User'])


@router.get('/me/', response_model=UserModelRead)
async def get_current_user(current_user: UserModel = Depends(get_current_active_user)):
    return UserModelRead(**current_user.dict())
