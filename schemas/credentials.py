from pydantic import BaseModel


class Credentials(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
