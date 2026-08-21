from database.dependancy import Datatbase, GetAdmin
from fastapi import APIRouter
from schemas.schema_admin import UserUpdeateAdminModel, UserUpdeateAdminPasswordModel
from services import service_admin
from starlette import status

route = APIRouter()


######user############
@route.get("/users", status_code=status.HTTP_200_OK)
async def get_users(current_user: GetAdmin, db: Datatbase):
    return await service_admin.get_user(db=db)


@route.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(current_user: GetAdmin, user_id: int, db: Datatbase):
    return await service_admin.get_user_id(user_id=user_id, db=db)


@route.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(current_user: GetAdmin, user_id: int, db: Datatbase):
    return await service_admin.delete_user(db=db, user_id=user_id)


@route.put("/users/{user_id}", status_code=status.HTTP_200_OK)
async def updeate_user(
    current_user: GetAdmin,
    user_id: int,
    db: Datatbase,
    user_model: UserUpdeateAdminModel,
):
    return await service_admin.updeate_user(
        db=db, user_id=user_id, user_model=user_model
    )


@route.put("/users/password/{user_id}", status_code=status.HTTP_200_OK)
async def updeate_user_password(
    current_user: GetAdmin,
    user_id: int,
    db: Datatbase,
    password_model: UserUpdeateAdminPasswordModel,
):
    return await service_admin.updeate_password_user(
        db=db, user_id=user_id, password_model=password_model
    )


######project############
@route.get("/projects", status_code=status.HTTP_200_OK)
async def get_projects(current_user: GetAdmin, db: Datatbase):
    return await service_admin.get_projects(db=db)


@route.get("/users/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_id(current_user: GetAdmin, project_id: int, db: Datatbase):
    return await service_admin.get_project_id(project_id=project_id, db=db)


@route.delete("/users/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(current_user: GetAdmin, project_id: int, db: Datatbase):
    return await service_admin.delete_project(db=db, project_id=project_id)


@route.get("/users/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_member(current_user: GetAdmin, project_id: int, db: Datatbase):
    return await service_admin.get_project_member(project_id=project_id, db=db)


######task############
@route.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(current_user: GetAdmin, db: Datatbase):
    return await service_admin.get_tasks(db=db)


@route.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(current_user: GetAdmin, task_id: int, db: Datatbase):
    return await service_admin.get_task_id(task_id=task_id, db=db)


@route.delete("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(current_user: GetAdmin, task_id: int, db: Datatbase):
    return await service_admin.delete_task(db=db, task_id=task_id)


@route.get("/dashboard", status_code=status.HTTP_200_OK)
async def dashboard(current_user: GetAdmin, db: Datatbase):
    return await service_admin.dashboard(db=db)
