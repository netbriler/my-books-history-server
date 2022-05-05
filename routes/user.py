from fastapi import APIRouter, Depends

from models.user import UserModel, UserModelRead
from services.auth import get_current_active_user

router = APIRouter(tags=['User'])


@router.get('/me/', response_model=UserModelRead)
async def get_current_user(current_user: UserModel = Depends(get_current_active_user)):
    return current_user
