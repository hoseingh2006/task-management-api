from fastapi import APIRouter, HTTPException
from database.dependancy import Datatbase
from starlette import status
from schemas.schema_auth import Token
from services.service_auth import create_access_token, check_user
from database.dependancy import FormData

route = APIRouter()


@route.post("/token")
async def login_for_access_token(form_data: FormData, db: Datatbase) -> Token:
    user = await check_user(db, form_data.username, form_data.password)
    token = create_access_token(user.username, user.id)
    if token:
        return Token(access_token=token, token_type="bearer")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="not create token",
    )
