from fastapi import APIRouter, HTTPException
from schemas.schema_user import UserModel, UpdeateUserModel, UserPasswordModel
from database.dependancy import Datatbase
from starlette import status
from services import service_user
from database.dependancy import GetUser

route = APIRouter()


@route.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_model: UserModel, db: Datatbase):

    return await service_user.create_user(user_model=user_model, db=db)


@route.get("/", status_code=status.HTTP_200_OK)
async def get_personal(current_user: GetUser):
    return await service_user.get_user(current_user)


@route.put("/", status_code=status.HTTP_200_OK)
async def updeate_personal(
    current_user: GetUser, user_model: UpdeateUserModel, db: Datatbase
):
    return await service_user.updeate_user(
        user_model=user_model, db=db, current_user=current_user
    )


@route.put("/password", status_code=status.HTTP_200_OK)
async def updeate_password(
    current_user: GetUser, pass_model: UserPasswordModel, db: Datatbase
):
    return await service_user.updeate_password(
        password_model=pass_model, db=db, current_user=current_user
    )
