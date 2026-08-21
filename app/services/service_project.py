from database.dependancy import Datatbase, GetUser
from fastapi import HTTPException
from models.model_project import Project, ProjectMembers, ProjectRole
from schemas.schema_project import (
    ProjectModel,
    ProjectUpdateModel,
    ProjectStatusUpdateModel,
)
from sqlalchemy import select
from starlette import status


async def create_project(
    project_model: ProjectModel, db: Datatbase, current_user: GetUser
):
    data = project_model.model_dump()
    project = Project(**data)
    db.add(project)
    await db.flush()
    project_id = project.id
    user_id = current_user.id
    project_ember = ProjectMembers(
        project_id=project_id, user_id=user_id, role=ProjectRole.OWNER
    )
    db.add(project_ember)
    await db.commit()
    await db.refresh(project)

    return {"message": "Project created successfully!"}


async def get_project(current_user: GetUser, db: Datatbase):
    projects = await db.scalars(
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.is_active.is_(True),
        )
    )
    return projects.all()


async def get_project_id(current_user: GetUser, db: Datatbase, project_id: int):
    result = await db.scalars(
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.id == project_id,
            Project.is_active.is_(True),
        )
    )
    project = result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found!")
    return project


async def update_project(
    project_model: ProjectUpdateModel,
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
):
    result = await db.scalars(
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.id == project_id,
            ProjectMembers.role.in_([ProjectRole.OWNER, ProjectRole.MANAGER]),
            Project.is_active.is_(True),
        )
    )
    project = result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="project not found!")
    if project_model.name:
        project.name = project_model.name
    if project_model.description:
        project.description = project_model.description
    await db.commit()
    await db.refresh(project)
    return {"message": "Project updated successfully!"}


async def update_project_status(
    status_model: ProjectStatusUpdateModel,
    current_user: GetUser,
    db: Datatbase,
    project_id: int,
):
    result = await db.scalars(
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.id == project_id,
            ProjectMembers.role.in_([ProjectRole.OWNER, ProjectRole.MANAGER]),
            Project.is_active.is_(True),
        )
    )
    project = result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="project not found!")
    project.status = status_model.status
    await db.commit()
    await db.refresh(project)
    return {"message": "Project status updated successfully!"}


async def delete_project(current_user: GetUser, db: Datatbase, project_id: int):
    result = await db.scalars(
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.id == project_id,
            ProjectMembers.role == ProjectRole.OWNER,
            Project.is_active.is_(True),
        )
    )
    project = result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found!")
    project.is_active = False
    await db.commit()
    await db.refresh(project)
    return {"message": "Project deleted successfully!"}
