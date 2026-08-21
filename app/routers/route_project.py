from database.dependancy import Datatbase, GetUser  # noqa: I001
from fastapi import APIRouter
from schemas.schema_project import (
    ProjectModel,
    ProjectStatusUpdateModel,
    ProjectUpdateModel,
    ProjectMember,
)
from services import service_project
from starlette import status

route = APIRouter()


##########Project Routers##########
@route.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_model: ProjectModel, db: Datatbase, current_user: GetUser
):
    return await service_project.create_project(
        project_model=project_model, db=db, current_user=current_user
    )


@route.get("/", status_code=status.HTTP_200_OK)
async def get_project(current_user: GetUser):
    return await service_project.get_project(current_user)


@route.get("/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_id(current_user: GetUser, project_id: int):
    return await service_project.get_project_id(current_user, project_id)


@route.put("/{project_id}", status_code=status.HTTP_200_OK)
async def update_project(
    project_model: ProjectUpdateModel,
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
):
    return await service_project.update_project(
        project_model=project_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
    )


@route.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(current_user: GetUser, project_id: int):
    return await service_project.delete_project(current_user, project_id)


##########Status Project Routers##########
@route.patch("/{project_id}/status", status_code=status.HTTP_200_OK)
async def update_project_status(
    status_model: ProjectStatusUpdateModel,
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
):
    return await service_project.update_project_status(
        status_model=status_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
    )


##########Member Project Routers##########
@route.post("/{project_id}/member", status_code=status.HTTP_200_OK)
async def project_member(
    member_model: ProjectMember,
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
):
    return await service_project.project_member(
        member_model=member_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
    )


@route.patch("/{project_id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def project_update_member(
    member_model: ProjectMember,
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
    user_id: int,
):
    return await service_project.project_update_member(
        member_model=member_model,
        current_user=current_user,
        db=db,
        project_id=project_id,
        user_id=user_id,
    )


@route.get("/{project_id}/members/", status_code=status.HTTP_200_OK)
async def get_project_members(
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
):
    return await service_project.get_project_members(
        current_user=current_user,
        db=db,
        project_id=project_id,
    )


@route.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_200_OK)
async def project_delete_member(
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
    user_id: int,
):
    return await service_project.project_delete_member(
        current_user=current_user,
        db=db,
        project_id=project_id,
        user_id=user_id,
    )
