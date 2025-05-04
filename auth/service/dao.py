from base.database.dao.base import BaseDAO
from service.models import User, Role

class UsersDAO(BaseDAO):
    model = User

class RoleDAO(BaseDAO):
    model = Role
