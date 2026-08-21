from database.dependancy import Datatbase, FormData
from fastapi import APIRouter, HTTPException
from schemas.schema_auth import Token
from services.service_auth import check_user, create_access_token
from starlette import status

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
