from models.model_user import UserRole
from pydantic import BaseModel


class UserUpdeateAdminModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserUpdeateAdminPasswordModel(BaseModel):
    password: str
