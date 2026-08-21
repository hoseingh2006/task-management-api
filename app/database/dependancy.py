from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import LocalSession
from fastapi.security import OAuth2PasswordRequestForm
from core.security import get_current_user
from models.model_user import User, UserRole
from starlette import status
from fastapi import HTTPException


async def get_db():
    async with LocalSession() as db:
        yield db


Datatbase = Annotated[AsyncSession, Depends(get_db)]
FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
GetUser = Annotated[User, Depends(get_current_user)]


async def check_admin(current_user: GetUser):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="you are not admin"
        )
    return current_user


GetAdmin = Annotated[User, Depends(check_admin)]
