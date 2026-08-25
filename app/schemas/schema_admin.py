from pydantic import BaseModel

from app.models.model_user import UserRole


class UserUpdateAdminModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserUpdateAdminPasswordModel(BaseModel):
    password: str
