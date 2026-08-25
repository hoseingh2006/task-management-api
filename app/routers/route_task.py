from fastapi import APIRouter
from starlette import status

from app.database.dependency import Database, GetUser
from app.schemas.schema_task import (
    TaskModel,
    TaskStatusUpdateModel,
    TaskUpdateModel,
)
from app.services import service_task

route = APIRouter()


@route.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_model: TaskModel, db: Database, current_user: GetUser, project_id: int
):
    return await service_task.create_task(
        task_model=task_model, db=db, current_user=current_user, project_id=project_id
    )


@route.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(
    current_user: GetUser,
    project_id: int,
    db: Database,
):
    return await service_task.get_tasks(
        current_user=current_user, project_id=project_id, db=db
    )


@route.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(
    current_user: GetUser, project_id: int, db: Database, task_id: int
):
    return await service_task.get_task_id(
        current_user=current_user, project_id=project_id, db=db, task_id=task_id
    )


@route.put("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    task_model: TaskUpdateModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
):
    return await service_task.update_task(
        task_model=task_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
        task_id=task_id,
    )


@route.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    current_user: GetUser, project_id: int, db: Database, task_id: int
):
    return await service_task.delete_task(
        current_user=current_user, project_id=project_id, db=db, task_id=task_id
    )


@route.patch("/status/{task_id}", status_code=status.HTTP_200_OK)
async def update_task_status(
    status_model: TaskStatusUpdateModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
):
    return await service_task.update_task_status(
        status_model=status_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
        task_id=task_id,
    )
