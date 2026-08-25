from pydantic import BaseModel


class UserModel(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str


class UpdateUserModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: str | None = None


class UserPasswordModel(BaseModel):
    new_password: str
    old_password: str
