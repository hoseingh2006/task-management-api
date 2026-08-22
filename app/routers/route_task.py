from database.dependancy import Datatbase, GetUser
from fastapi import APIRouter
from schemas.schema_task import (
    TaskModel,
    TaskStatusUpdateModel,
    TaskUpdateModel,
)
from services import service_task
from starlette import status

route = APIRouter()


@route.post("/{project_id}", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_model: TaskModel, db: Datatbase, current_user: GetUser, project_id: int
):
    return await service_task.create_task(
        task_model=task_model, db=db, current_user=current_user, project_id=project_id
    )


@route.get("/{project_id}", status_code=status.HTTP_200_OK)
async def get_tasks(
    current_user: GetUser,
    project_id: int,
    db: Datatbase,
):
    return await service_task.get_tasks(
        current_user=current_user, project_id=project_id, db=db
    )


@route.get("/{project_id}/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_id(
    current_user: GetUser, project_id: int, db: Datatbase, task_id: int
):
    return await service_task.get_task_id(
        current_user=current_user, project_id=project_id, db=db, task_id=task_id
    )


@route.put("/{project_id}/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    task_model: TaskUpdateModel,
    current_user: GetUser,
    db: Datatbase,
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


@route.delete("/{project_id}/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    current_user: GetUser, project_id: int, db: Datatbase, task_id: int
):
    return await service_task.delete_task(
        current_user=current_user, project_id=project_id, db=db, task_id=task_id
    )


@route.patch("/{project_id}/status/{task_id}", status_code=status.HTTP_200_OK)
async def update_task_status(
    status_model: TaskStatusUpdateModel,
    current_user: GetUser,
    db: Datatbase,
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
