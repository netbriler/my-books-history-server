from pydantic import Field

from models.base import _BaseModel
from .user import UserModelRead


class CredentialsResponse(_BaseModel):
    access_token: str = Field(..., alias='accessToken')
    token_type: str = Field(..., alias='tokenType')
    user: UserModelRead
