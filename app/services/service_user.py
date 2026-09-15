from fastapi import HTTPException
from starlette import status

from app.core.security import Password_hash, verify_pass
from app.database.dependency import ActivityAction, Database, GetUser, add_log
from app.models.model_user import User
from app.schemas.schema_user import UpdateUserModel, UserModel, UserPasswordModel


async def create_user(user_model: UserModel, db: Database):
    data = user_model.model_dump()
    data["password_hash"] = Password_hash.hash(data.pop("password"))
    user = User(**data)
    db.add(user)
    add_log(
        action=ActivityAction.USER_CREATED,
        description=f"User '{user_model.first_name}' was Created",
        db=db,
    )
    await db.commit()
    await db.refresh(user)
    return {"massage": "create user successfully!"}


async def update_user(user_model: UpdateUserModel, db: Database, current_user: GetUser):
    if user_model.first_name is not None:
        current_user.first_name = user_model.first_name
    if user_model.last_name is not None:
        current_user.last_name = user_model.last_name
    if user_model.email is not None:
        current_user.email = user_model.email
    if user_model.username is not None:
        current_user.username = user_model.username
    add_log(
        action=ActivityAction.USER_UPDATED,
        description=f"User '{current_user.first_name}' was updated profile",
        db=db,
        current_user=current_user,
    )
    await db.commit()
    await db.refresh(current_user)
    return {"massage": "successfully updated!"}


async def get_user(current_user: GetUser):
    return {
        "UserName": current_user.username,
        "FirstName": current_user.first_name,
        "LastName": current_user.last_name,
        "Email": current_user.email,
    }


async def update_password(
    password_model: UserPasswordModel, db: Database, current_user: GetUser
):
    if verify_pass(current_user.password_hash, password_model.old_password):
        current_user.password_hash = Password_hash.hash(password_model.new_password)
        add_log(
            action=ActivityAction.USER_UPDATED,
            description=f"User '{current_user.first_name}' was updated Password",
            db=db,
            current_user=current_user,
        )
        await db.commit()
        await db.refresh(current_user)

        return {"massage": "successfully password updated!"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="password wrong!",
    )
