from sqlalchemy.orm import Mapped, mapped_column, relationship
from assistant.database.models.assistant import Assistant
from match.database.models.match import Match
from bot.database.models.auth import Auth
from base.database.dao.database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property


class Bot(Auth, Base):
    __tablename__ = 'bots'
    
    is_active: Mapped[bool] = mapped_column(default=False)
    instructions: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    lookingfor: Mapped[str] = mapped_column(nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    matches: Mapped[list["Match"]] = relationship(
        "Match", back_populates="bot", cascade="all, delete-orphan", lazy="selectin"
    )
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistants.id", ondelete="SET NULL"), nullable=True)
    assistant: Mapped["Assistant"] = relationship("Assistant", back_populates="bots", lazy="selectin")
    latitude: Mapped[float] = mapped_column(default=12.9333, nullable=False)
    longitude: Mapped[float] = mapped_column(default=100.883, nullable=False)
    proxy: Mapped[str] = mapped_column(nullable=True)
    @hybrid_property
    def match_count(self) -> int:
        return (
            len([match for match in self.matches if not match.is_deleted])
            if self.matches
            else 0
        )
    type: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'Bot',
        'passive_deletes': 'all',
    }

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
