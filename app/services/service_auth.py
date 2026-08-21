from fastapi import HTTPException
from database.dependancy import Datatbase
import jwt
from starlette import status
from models.model_user import User
from sqlalchemy import select
from core.security import verify_pass
from datetime import timedelta, datetime, timezone
from core.config import settings


async def check_user(db: Datatbase, username: str, password: str):
    result = await db.scalars(select(User).where(User.username == username))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )
    if verify_pass(user.password_hash, password):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
    )


def create_access_token(
    username: str, user_id: int, time_expire: timedelta = timedelta(minutes=15)
):
    exp = datetime.now(timezone.utc) + time_expire
    payload = {"username": username, "user_id": user_id, "exp": exp}
    encode_jwt = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return encode_jwt
