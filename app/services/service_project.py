from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.database.dependency import ActivityAction, Database, GetUser, add_log
from app.models.model_project import Project, ProjectMembers, ProjectRole, ProjectStatus
from app.models.model_user import User
from app.schemas.schema_project import (
    ProjectMember,
    ProjectModel,
    ProjectStatusUpdateModel,
    ProjectUpdateMember,
    ProjectUpdateModel,
)


##########Project Routers##########
async def create_project(
    project_model: ProjectModel, db: Database, current_user: GetUser
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
    add_log(
        action=ActivityAction.PROJECT_CREATED,
        description=f"Project '{project_model.name}' was created",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    await db.refresh(project)

    return {"message": "Project created successfully!"}


async def get_project(current_user: GetUser, db: Database):
    projects = await db.scalars(
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.is_active.is_(True),
        )
    )
    return projects.all()


async def get_project_id(current_user: GetUser, db: Database, project_id: int):
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
    db: Database,
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
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="project not found or you are not Owner/Manager",
        )
    if project_model.name:
        project.name = project_model.name
    if project_model.description:
        project.description = project_model.description
    add_log(
        action=ActivityAction.PROJECT_UPDATED,
        description=f"Project '{project.name}' was Updated",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    await db.refresh(project)
    return {"message": "Project updated successfully!"}


async def delete_project(current_user: GetUser, db: Database, project_id: int):
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
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Project not found! or you are not Owner",
        )
    project.is_active = False
    project.status = ProjectStatus.ARCHIVED
    add_log(
        action=ActivityAction.PROJECT_DELETED,
        description=f"Project '{project.name}' was Deleted",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    await db.refresh(project)
    return {"message": "Project deleted successfully!"}


##########Status Project Routers##########
async def update_project_status(
    status_model: ProjectStatusUpdateModel,
    current_user: GetUser,
    db: Database,
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
    add_log(
        action=ActivityAction.PROJECT_STATUS_CHANGED,
        description=f"Project '{project.name}' Status was Changed",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    await db.refresh(project)
    return {"message": "Project status updated successfully!"}


##########Member Project Routers##########
async def project_member(
    member_model: ProjectMember,
    db: Database,
    current_user: GetUser,
    project_id: int,
):
    if member_model.role == ProjectRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A project can only have one owner",
        )

    role_member = await db.scalar(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )

    if role_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if role_member.role not in (
        ProjectRole.OWNER,
        ProjectRole.MANAGER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to add members to this project.",
        )

    user = await db.scalar(select(User).where(User.id == member_model.user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_member = await db.scalar(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == member_model.user_id,
        )
    )

    if existing_member is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this project",
        )

    project_member = ProjectMembers(
        project_id=project_id,
        user_id=member_model.user_id,
        role=member_model.role,
    )

    db.add(project_member)
    add_log(
        action=ActivityAction.MEMBER_ADDED,
        description=f"Project '{project_id}' was Add Member",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    await db.refresh(project_member)

    return {"message": "Project member added successfully!"}


async def project_update_member(
    member_model: ProjectUpdateMember,
    db: Database,
    current_user: GetUser,
    project_id: int,
    user_id: int,
):
    result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    role_member = result.first()
    if role_member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not Found Project")
    if role_member.role != ProjectRole.OWNER:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to add members to this project.",
        )
    result_member = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == user_id,
        )
    )
    member = result_member.first()
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not Found Project")
    member.role = member_model.role
    add_log(
        action=ActivityAction.MEMBER_ROLE_CHANGED,
        description=f"Project '{project_id}' was Member Role Change to '{member.role}' ",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    await db.refresh(member)
    return {"message": "Project member update successfully!"}


async def project_delete_member(
    db: Database,
    current_user: GetUser,
    project_id: int,
    user_id: int,
):
    result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    role_member = result.first()
    if role_member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not Found Project")
    if role_member.role != ProjectRole.OWNER:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to remove members to this project.",
        )

    result_member = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == user_id,
        )
    )
    member = result_member.first()
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not Found Project")
    if member.role == ProjectRole.OWNER:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Project owner cannot be removed.",
        )
    await db.delete(member)
    add_log(
        action=ActivityAction.MEMBER_REMOVED,
        description=f"Project '{project_id}' was Member Deleted '{user_id}' ",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    await db.commit()
    return {"message": " member deleted successfully!"}


async def get_project_members(
    current_user: GetUser,
    db: Database,
    project_id: int,
):
    result_member = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    member = result_member.first()
    if member is None:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project.",
        )

    result = await db.execute(
        select(User.username, ProjectMembers.role)
        .join(User, ProjectMembers.user_id == User.id)
        .join(Project, ProjectMembers.project_id == Project.id)
        .where(
            ProjectMembers.project_id == project_id,
            Project.is_active.is_(True),
        )
    )

    return [
        {
            "username": username,
            "role": role,
        }
        for username, role in result.all()
    ]
