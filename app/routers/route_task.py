from fastapi import APIRouter
from starlette import status

from app.database.dependency import Database, GetUser
from app.schemas.schema_task import (
    TagProjectModel,
    TagTaskModel,
    TaskModel,
    TaskStatusUpdateModel,
    TaskUpdateModel,
)
from app.services import service_task

route = APIRouter()


##########Task Routers##########
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


##########Status task Routers##########
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


##########tag project\task##########
@route.post("/tag", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_model: TagProjectModel, db: Database, current_user: GetUser, project_id: int
):
    return await service_task.create_tag(
        tag_model=tag_model, db=db, current_user=current_user, project_id=project_id
    )


@route.put("/tag/{tag_id}", status_code=status.HTTP_200_OK)
async def update_tag(
    tag_model: TagProjectModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    tag_id: int,
):
    return await service_task.update_tag(
        tag_model=tag_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
        tag_id=tag_id,
    )


@route.delete("/tag/{tag_id}", status_code=status.HTTP_200_OK)
async def delete_tag(current_user: GetUser, project_id: int, db: Database, tag_id: int):
    return await service_task.delete_tag(
        current_user=current_user, project_id=project_id, db=db, tag_id=tag_id
    )


@route.get("/tag", status_code=status.HTTP_200_OK)
async def get_all_project_tag(
    current_user: GetUser,
    project_id: int,
    db: Database,
):
    return await service_task.select_all_project_tag(
        current_user=current_user, project_id=project_id, db=db
    )


@route.get("/tag/{task_id}", status_code=status.HTTP_200_OK)
async def get_all_project_tag_with_task(
    current_user: GetUser,
    project_id: int,
    db: Database,
    task_id: int,
):
    return await service_task.select_all_tag_with_project_task(
        current_user=current_user,
        project_id=project_id,
        db=db,
        task_id=task_id,
    )


##########tag project\task##########
@route.post("/tag/{task_id}", status_code=status.HTTP_201_CREATED)
async def add_tags_to_task(
    tag_model: TagTaskModel,
    task_id: int,
    db: Database,
    current_user: GetUser,
    project_id: int,
):
    return await service_task.add_tags_to_task(
        tag_model=tag_model,
        db=db,
        current_user=current_user,
        project_id=project_id,
        task_id=task_id,
    )


##########subtask##########
@route.post("/subtask/{task_id}", status_code=status.HTTP_201_CREATED)
async def create_subtask(
    task_model: TaskModel,
    db: Database,
    task_id: int,
    current_user: GetUser,
    project_id: int,
):
    return await service_task.create_subtask(
        task_model=task_model,
        db=db,
        task_id=task_id,
        current_user=current_user,
        project_id=project_id,
    )


@route.get("/subtask/{task_id}", status_code=status.HTTP_200_OK)
async def get_subtask_with_task(
    current_user: GetUser,
    project_id: int,
    db: Database,
    task_id: int,
):
    return await service_task.get_subtask_with_task(
        current_user=current_user,
        project_id=project_id,
        db=db,
        task_id=task_id,
    )


@route.put("/subtask/{task_id}/{subtask_id}", status_code=status.HTTP_200_OK)
async def update_subtask(
    task_model: TaskUpdateModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
    subtask_id: int,
):
    return await service_task.update_subtask(
        task_model=task_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
        task_id=task_id,
        subtask_id=subtask_id,
    )


@route.delete("/subtask/{task_id}/{subtask_id}", status_code=status.HTTP_200_OK)
async def delete_subtask(
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
    subtask_id: int,
):
    return await service_task.delete_subtask(
        current_user=current_user,
        db=db,
        project_id=project_id,
        task_id=task_id,
        subtask_id=subtask_id,
    )
