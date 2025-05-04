from sqlalchemy.orm import Mapped, mapped_column

class Auth:
    is_auth: Mapped[bool] = mapped_column(default=False)
    otp_requested: Mapped[bool] = mapped_column(default=False)