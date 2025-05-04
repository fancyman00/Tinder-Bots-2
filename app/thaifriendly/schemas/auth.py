from pydantic import BaseModel


class AuthThaifriendly(BaseModel):
    email: str

