from pydantic import BaseModel

class ActivateBot(BaseModel):
    is_active: bool = True

class UpdateGender(BaseModel):
    gender: str