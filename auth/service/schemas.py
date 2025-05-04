import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator, computed_field
from service.utils import get_password_hash


class EmailModel(BaseModel):
    username: str = Field(description="Username")
    model_config = ConfigDict(from_attributes=True)


class UserBase(EmailModel):
    pass

class UpdateRole(BaseModel):
    role_id: int

class SUserRegister(UserBase):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль")

    @model_validator(mode="after")
    def check_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        self.password = get_password_hash(self.password)  # хешируем пароль до сохранения в базе данных
        return self

class ChangePassword(SUserRegister):
    old_password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")

class SUserAddDB(UserBase):
    password: str = Field(min_length=5, description="Пароль в формате HASH-строки")


class SUserAuth(EmailModel):
    password: str = Field(min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class RoleModel(BaseModel):
    id: int = Field(description="Идентификатор роли")
    name: str = Field(description="Название роли")
    model_config = ConfigDict(from_attributes=True)


class SUserInfo(UserBase):
    id: int = Field(description="Идентификатор пользователя")
    role: RoleModel = Field(exclude=True)

    @computed_field
    def role_name(self) -> str:
        return self.role.name

    @computed_field
    def role_id(self) -> int:
        return self.role.id
