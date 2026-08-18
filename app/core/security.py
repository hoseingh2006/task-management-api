from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from database.dependancy import Datatbase
from fastapi import Depends
import jwt
from starlette import status
from models.model_user import User
from sqlalchemy import select
from core.config import settings

Password_hash = PasswordHash()


def verify_pass(hash_password: str, password: str):
    return Password_hash.verify(password, hash_password)


postgres_pass = settings.database_password
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(db: Datatbase, token: str = Depends(oauth2_scheme)):
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
