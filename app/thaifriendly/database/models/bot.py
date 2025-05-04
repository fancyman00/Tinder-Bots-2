from bot.database.models.bot import Bot
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class ThaifriendlyBot(Bot):
    __tablename__ = 'thaifriendly_bots'
    __table_args__ = {'extend_existing': True}  
    id: Mapped[int] = mapped_column(ForeignKey("bots.id", ondelete="CASCADE"), primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)

    __mapper_args__ = {
        'polymorphic_identity': 'Thaifriendly',
        "polymorphic_load": "selectin",
    }

    def __repr__(self):
        return f"<ThaiFriendlyBot {self.name}>"
