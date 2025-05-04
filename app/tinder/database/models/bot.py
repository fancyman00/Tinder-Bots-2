from bot.database.models.bot import Bot
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class TinderBot(Bot):
    __tablename__ = 'tinder_bots'
    __table_args__ = {'extend_existing': True}  
    id: Mapped[int] = mapped_column(ForeignKey("bots.id", ondelete="CASCADE"), primary_key=True)
    phone_number: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    dob: Mapped[str] = mapped_column(nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'Tinder',
        "polymorphic_load": "selectin",
    }

    def __repr__(self):
        return f"<TinderBot {self.name}>"