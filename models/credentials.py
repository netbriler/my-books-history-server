from pydantic import BaseModel, Field

from .user import UserModelRead


class CredentialsResponse(BaseModel):
    access_token: str = Field(..., alias='accessToken')
    token_type: str = Field(..., alias='tokenType')
    user: UserModelRead

    class Config:
        allow_population_by_field_name = True
