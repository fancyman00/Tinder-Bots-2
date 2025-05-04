from sqlalchemy.orm import Mapped, mapped_column
from base.database.dao.database import Base
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime


class Log(Base):
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    level: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)
    module: Mapped[str] = mapped_column(String(100))
    func_name: Mapped[str] = mapped_column(String(100))
    line_no: Mapped[int] = mapped_column(Integer)
    exception: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
