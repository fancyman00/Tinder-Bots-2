from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base.database.dao.database import Base

class Match(Base):
    is_deleted: Mapped[bool] = mapped_column(default=False)
    bot_id: Mapped[int] = mapped_column(
        ForeignKey("bots.id", ondelete="CASCADE"),
        nullable=False
    )    
    name: Mapped[str] = mapped_column(nullable=False)
    match_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    age: Mapped[int] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    time: Mapped[str] = mapped_column(nullable=True)

    # Отношение с Bot
    bot: Mapped["Bot"] = relationship("Bot", back_populates="matches") 

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"