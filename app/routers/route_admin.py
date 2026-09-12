from fastapi import APIRouter
from starlette import status

from app.database.dependency import Database, GetAdmin
from app.schemas.schema_admin import (
    TagModel,
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


######dashboard############
@route.get("/dashboard", status_code=status.HTTP_200_OK)
async def dashboard(current_user: GetAdmin, db: Database):
    return await service_admin.dashboard(db=db)


######Tag############
@route.post("/tag", status_code=status.HTTP_200_OK)
async def create_global_tag(current_user: GetAdmin, tag_model: TagModel, db: Database):
    return await service_admin.create_tag(db=db, tag_model=tag_model)


@route.get("/tag", status_code=status.HTTP_200_OK)
async def get_all_tag(current_user: GetAdmin, db: Database):
    return await service_admin.get_all_tag(db=db)


@route.get("/tag/project", status_code=status.HTTP_200_OK)
async def get_all_project_tag(current_user: GetAdmin, db: Database):
    return await service_admin.get_all_project_tag(db=db)


@route.get("/tag/global", status_code=status.HTTP_200_OK)
async def get_all_global_tag(current_user: GetAdmin, db: Database):
    return await service_admin.get_all_global_tag(db=db)


@route.get("/tag/project/{project_id}", status_code=status.HTTP_200_OK)
async def get_all_tag_by_project(current_user: GetAdmin, db: Database, project_id: int):
    return await service_admin.get_all_tag_with_project(db=db, project_id=project_id)


@route.delete("/tag/{tag_id}", status_code=status.HTTP_200_OK)
async def delete_tag_by_id(current_user: GetAdmin, db: Database, tag_id: int):
    return await service_admin.delete_tag_with_id(db=db, tag_id=tag_id)


@route.put("/tag/{tag_id}", status_code=status.HTTP_200_OK)
async def update_tag_by_id(
    current_user: GetAdmin, db: Database, tag_model: TagModel, tag_id: int
):
    return await service_admin.update_tag_with_id(
        db=db, tag_model=tag_model, tag_id=tag_id
    )


######subtask############
@route.get("/subtask", status_code=status.HTTP_200_OK)
async def get_all_subtasks(current_user: GetAdmin, db: Database):
    return await service_admin.get_subtasks(db=db)


@route.get("/subtask/{task_id}", status_code=status.HTTP_200_OK)
async def get_subtask_by_id(current_user: GetAdmin, db: Database, task_id: int):
    return await service_admin.get_subtask_id(db=db, task_id=task_id)


######subtask############
@route.get("/logs", status_code=status.HTTP_200_OK)
async def get_all_log(current_user: GetAdmin, db: Database):
    return await service_admin.get_all_log(db=db)


@route.get("/logs/user", status_code=status.HTTP_200_OK)
async def get_all_user_log(current_user: GetAdmin, db: Database):
    return await service_admin.get_all_user_log(db=db)


@route.get("/logs/admin", status_code=status.HTTP_200_OK)
async def get_all_admin_log(current_user: GetAdmin, db: Database):
    return await service_admin.get_all_admin_log(db=db)


@route.get("/logs/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_log_by_user_id(current_user: GetAdmin, db: Database, user_id: int):
    return await service_admin.get_log_by_user_id(db=db, user_id=user_id)


@route.get("/logs/user/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_log_by_task_id(current_user: GetAdmin, db: Database, task_id: int):
    return await service_admin.get_log_by_task_id(db=db, task_id=task_id)


@route.get("/logs/user/action/{action}", status_code=status.HTTP_200_OK)
async def get_log_by_action(current_user: GetAdmin, db: Database, action: str):
    return await service_admin.get_log_by_action(db=db, action=action)


@route.get("/logs/user/project/{project_id}", status_code=status.HTTP_200_OK)
async def get_log_by_project_id(current_user: GetAdmin, db: Database, project_id: int):
    return await service_admin.get_log_by_project_id(db=db, project_id=project_id)
