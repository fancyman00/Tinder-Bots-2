from sqlalchemy.orm import Mapped, mapped_column


class ThaifriendlyAuth:
    """Миксин для аутентификации"""
    __abstract__ = True
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
