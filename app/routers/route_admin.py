from fastapi import APIRouter, Query
from starlette import status

from app.database.dependency import Database, GetAdmin
from app.models.model_project import ProjectStatus
from app.models.model_task import TagScope, TaskPriority, TaskStatus
from app.schemas.schema_admin import (
    TagModel,
    UserRole,
    UserUpdateAdminModel,
    UserUpdateAdminPasswordModel,
)
from app.services import service_admin

route = APIRouter()


######user############
@route.get("/users", status_code=status.HTTP_200_OK)
async def get_users(
    current_user: GetAdmin,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    role: UserRole | None = None,
    is_active: bool | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_user(
        db=db,
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


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
async def get_projects(
    current_user: GetAdmin,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    status: ProjectStatus | None = None,
    is_active: bool | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_projects(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@route.get("/projects/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_id(current_user: GetAdmin, project_id: int, db: Database):
    return await service_admin.get_project_id(project_id=project_id, db=db)


@route.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(current_user: GetAdmin, project_id: int, db: Database):
    return await service_admin.delete_project(db=db, project_id=project_id)


@route.get("/projects/{project_id}/members", status_code=status.HTTP_200_OK)
async def get_project_member(
    current_user: GetAdmin,
    project_id: int,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
):
    return await service_admin.get_project_member(
        project_id=project_id, db=db, page=page, page_size=page_size
    )


######task############
@route.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(
    current_user: GetAdmin,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    is_active: bool | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_tasks(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
        priority=priority,
    )


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
async def get_all_tag(
    current_user: GetAdmin,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    scope: TagScope | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_all_tag(
        db=db,
        page=page,
        page_size=page_size,
        scope=scope,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# @route.get("/tag/project", status_code=status.HTTP_200_OK)
# async def get_all_project_tag(
#     current_user: GetAdmin,
#     db: Database,
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, le=100, ge=1),
# ):

#     return await service_admin.get_all_project_tag(
#         db=db, page=page, page_size=page_size
#     )


# @route.get("/tag/global", status_code=status.HTTP_200_OK)
# async def get_all_global_tag(
#     current_user: GetAdmin,
#     db: Database,
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, le=100, ge=1),
# ):
#     return await service_admin.get_all_global_tag(db=db, page=page, page_size=page_size)


@route.get("/tag/project/{project_id}", status_code=status.HTTP_200_OK)
async def get_all_tag_by_project(
    current_user: GetAdmin,
    db: Database,
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    scope: TagScope | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_all_tag_with_project(
        db=db,
        project_id=project_id,
        page_size=page_size,
        page=page,
        scope=scope,
        sort_by=sort_by,
        sort_order=sort_order,
    )


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
async def get_all_subtasks(
    current_user: GetAdmin,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    is_active: bool | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_subtasks(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
        priority=priority,
    )


@route.get("/subtask/{task_id}", status_code=status.HTTP_200_OK)
async def get_subtask_by_id(current_user: GetAdmin, db: Database, task_id: int):
    return await service_admin.get_subtask_id(db=db, task_id=task_id)


######logs############
@route.get("/logs", status_code=status.HTTP_200_OK)
async def get_all_log(
    current_user: GetAdmin,
    db: Database,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    role: UserRole | None = None,
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_all_log(
        db=db,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        role=role,
    )


# @route.get("/logs/user", status_code=status.HTTP_200_OK)
# async def get_all_user_log(
#     current_user: GetAdmin,
#     db: Database,
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, le=100, ge=1),
# ):
#     return await service_admin.get_all_user_log(db=db, page=page, page_size=page_size)


# @route.get("/logs/admin", status_code=status.HTTP_200_OK)
# async def get_all_admin_log(
#     current_user: GetAdmin,
#     db: Database,
#     page: int = Query(1, ge=1),
#     page_size: int = Query(20, le=100, ge=1),
# ):
#     return await service_admin.get_all_admin_log(db=db, page=page, page_size=page_size)


@route.get("/logs/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_log_by_user_id(
    current_user: GetAdmin,
    db: Database,
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_log_by_user_id(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@route.get("/logs/task/task/{task_id}", status_code=status.HTTP_200_OK)
async def get_log_by_task_id(
    current_user: GetAdmin,
    db: Database,
    task_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_log_by_task_id(
        db=db,
        task_id=task_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@route.get("/logs/action/action/{action}", status_code=status.HTTP_200_OK)
async def get_log_by_action(
    current_user: GetAdmin,
    db: Database,
    action: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_log_by_action(
        db=db,
        action=action,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@route.get("/logs/project/{project_id}", status_code=status.HTTP_200_OK)
async def get_log_by_project_id(
    current_user: GetAdmin,
    db: Database,
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100, ge=1),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
):
    return await service_admin.get_log_by_project_id(
        db=db,
        project_id=project_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
