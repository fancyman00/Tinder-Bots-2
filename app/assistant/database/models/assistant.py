from sqlalchemy.orm import Mapped, mapped_column, relationship
from base.database.dao.database import Base

class Assistant(Base):
    assistant_id: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=True, unique=True)
    bots: Mapped[list["Bot"]] = relationship(
        "Bot", 
        back_populates="assistant", 
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"