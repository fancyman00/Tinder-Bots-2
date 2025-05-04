from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class LogBase(BaseModel):
    level: str = Field(..., example="INFO", description="Уровень логирования")
    message: str = Field(..., example="Test message", description="Текст сообщения")
    module: Optional[str] = Field(None, example="app.main", description="Название модуля")
    func_name: Optional[str] = Field(None, example="my_function", description="Имя функции")
    line_no: Optional[int] = Field(None, example=42, description="Номер строки")
    exception: Optional[str] = Field(None, example="Traceback...", description="Текст исключения")

class LogCreate(LogBase):
    pass

class LogUpdate(LogBase):
    pass

class LogResponse(LogBase):
    id: int = Field(..., example=1, description="Уникальный идентификатор записи")
    timestamp: datetime

    class Config:
        from_attributes = True  # Enable ORM mode