from pydantic import BaseModel

class SettingValue(BaseModel):
    value: str | int
    ttl: int | None = None