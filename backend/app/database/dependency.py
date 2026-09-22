from typing import Annotated

import jwt
from app.core.enums import UserRole
from app.core.security import ALGORITHM, SECRET_KEY, oauth2_scheme
from app.database.database import LocalSession
from app.models.model_user import User
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


async def get_db():
    async with LocalSession() as db:
        yield db


Database = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(db: Database, token: str = Depends(oauth2_scheme)):
    try:
        decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_token.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.scalars(select(User).where(User.id == user_id))

    user = result.first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
GetUser = Annotated[User, Depends(get_current_user)]


async def check_admin(current_user: GetUser):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="you are not admin"
        )
    return current_user


GetAdmin = Annotated[User, Depends(check_admin)]
