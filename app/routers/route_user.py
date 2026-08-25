from fastapi import APIRouter
from starlette import status

from app.database.dependency import Database, GetUser
from app.schemas.schema_user import UpdateUserModel, UserModel, UserPasswordModel
from app.services import service_user

route = APIRouter()


@route.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_model: UserModel, db: Database):

    return await service_user.create_user(user_model=user_model, db=db)


@route.get("/", status_code=status.HTTP_200_OK)
async def get_personal(current_user: GetUser):
    return await service_user.get_user(current_user)


@route.put("/", status_code=status.HTTP_200_OK)
async def update_personal(
    current_user: GetUser, user_model: UpdateUserModel, db: Database
):
    return await service_user.update_user(
        user_model=user_model, db=db, current_user=current_user
    )


@route.put("/password", status_code=status.HTTP_200_OK)
async def update_password(
    current_user: GetUser, pass_model: UserPasswordModel, db: Database
):
    return await service_user.update_password(
        password_model=pass_model, db=db, current_user=current_user
    )
