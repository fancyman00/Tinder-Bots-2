from typing import Optional

from pydantic import BaseModel


class MatchCreate(BaseModel):
    bot_id: int
    match_id: str
    name: str
    gender: Optional[str] = None
    age: Optional[int | str] = None
    city: Optional[str] = None
    time: Optional[str] = None