from fastapi import APIRouter
from starlette import status

from app.database.dependency import Database, GetAdmin
from app.schemas.schema_admin import (
    UserUpdateAdminModel,
    UserUpdateAdminPasswordModel,
)
from app.services import service_admin

route = APIRouter()


######user############
@route.get("/users", status_code=status.HTTP_200_OK)
async def get_users(current_user: GetAdmin, db: Database):
    return await service_admin.get_user(db=db)


@route.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(current_user: GetAdmin, user_id: int, db: Database):
    return await service_admin.get_user_id(user_id=user_id, db=db)


@route.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(current_user: GetAdmin, user_id: int, db: Database):
    return await service_admin.delete_user(db=db, user_id=user_id)


@route.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    current_user: GetAdmin,
    user_id: int,
    db: Database,
    user_model: UserUpdateAdminModel,
):
    return await service_admin.update_user(
        db=db, user_id=user_id, user_model=user_model
    )


@route.put("/users/password/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_password(
    current_user: GetAdmin,
    user_id: int,
    db: Database,
    password_model: UserUpdateAdminPasswordModel,
):
    return await service_admin.update_password_user(
        db=db, user_id=user_id, password_model=password_model
    )


######project############
@route.get("/projects", status_code=status.HTTP_200_OK)
async def get_projects(current_user: GetAdmin, db: Database):
    return await service_admin.get_projects(db=db)


@route.get("/users/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_id(current_user: GetAdmin, project_id: int, db: Database):
    return await service_admin.get_project_id(project_id=project_id, db=db)


@route.delete("/users/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(current_user: GetAdmin, project_id: int, db: Database):
    return await service_admin.delete_project(db=db, project_id=project_id)


@route.get("/users/{project_id}/members", status_code=status.HTTP_200_OK)
async def get_project_member(current_user: GetAdmin, project_id: int, db: Database):
    return await service_admin.get_project_member(project_id=project_id, db=db)


######task############
@route.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(current_user: GetAdmin, db: Database):
    return await service_admin.get_tasks(db=db)


@route.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(current_user: GetAdmin, task_id: int, db: Database):
    return await service_admin.get_task_id(task_id=task_id, db=db)


@route.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(current_user: GetAdmin, task_id: int, db: Database):
    return await service_admin.delete_task(db=db, task_id=task_id)


@route.get("/dashboard", status_code=status.HTTP_200_OK)
async def dashboard(current_user: GetAdmin, db: Database):
    return await service_admin.dashboard(db=db)
