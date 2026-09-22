from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.sql.elements import ColumnElement
from starlette import status

from app.core.enums import (
    ActivityAction,
    NotificationType,
    ProjectRole,
    ProjectStatus,
)
from app.core.utilities import add_log, calculate_offset, calculate_pages
from app.database.dependency import Database, GetUser
from app.models.model_project import Project, ProjectMembers
from app.models.model_task import Notification
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
    project_member = ProjectMembers(
        project_id=project_id, user_id=user_id, role=ProjectRole.OWNER
    )
    db.add(project_member)
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


async def get_project(
    current_user: GetUser,
    db: Database,
    page: int,
    page_size: int,
    status: ProjectStatus | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = [
        ProjectMembers.user_id == current_user.id,
        Project.is_active.is_(True),
    ]

    if status is not None:
        conditions.append(Project.status == status)

    query = (
        select(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(*conditions)
    )

    sort_columns = {
        "id": Project.id,
        "name": Project.name,
        "updated_at": Project.updated_at,
    }
    sort_column = sort_columns.get(sort_by, Project.id)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            Project.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            Project.id.asc(),
        )
    count_query = (
        select(func.count())
        .select_from(Project)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(*conditions)
    )

    total = await db.scalar(count_query) or 0
    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    projects = result.all()
    return {
        "items": projects,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


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
    if project.status == status_model.status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project is already in this status",
        )
    project.status = status_model.status
    add_log(
        action=ActivityAction.PROJECT_STATUS_CHANGED,
        description=f"Project '{project.name}' Status was Changed",
        db=db,
        current_user=current_user,
        project_id=project_id,
    )
    result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project.id,
            ProjectMembers.user_id != current_user.id,
        )
    )

    members = result.all()

    for member in members:
        db.add(
            Notification(
                creator_id=current_user.id,
                user_id=member.user_id,
                type=NotificationType.PROJECT_STATUS_CHANGED,
                title=f"Project '{project.name}' status changed",
                message=(
                    f"User '{current_user.username}' changed the project status "
                    f"to '{status_model.status.value}'."
                ),
                project_id=project.id,
            )
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
    project = await db.scalar(
        select(Project).where(Project.id == project_id, Project.is_active.is_(True))
    )
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not Found project")
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

    notification = Notification(
        creator_id=current_user.id,
        user_id=member_model.user_id,
        type=NotificationType.MEMBER_ADDED,
        title=f"User '{current_user.username}'  Change Member Role",
        message=f"User '{current_user.username}' Add Member '{user.username}' To '{member_model.role}' ",
        project_id=project_id,
    )
    db.add(notification)
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
    if member_model.role == ProjectRole.OWNER:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="You Cant Add Two Owner For One Project"
        )
    user = await db.scalar(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    )
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not Found User")
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
    elif role_member.role == ProjectRole.OWNER and user_id == current_user.id:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Owner Cant Change Role For himself"
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

    notification = Notification(
        creator_id=current_user.id,
        user_id=user_id,
        type=NotificationType.MEMBER_ROLE_CHANGED,
        title=f"User '{current_user.username}'  Change Member Role",
        message=f"User '{current_user.username}' Change Member '{user.username}' Role To '{member_model.role}' ",
        project_id=project_id,
    )
    db.add(notification)
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
    elif role_member.role == ProjectRole.OWNER and user_id == current_user.id:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Owner Cant Delete himself"
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
    page: int,
    page_size: int,
    role: ProjectRole | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    member_query = select(ProjectMembers.id).where(
        ProjectMembers.project_id == project_id,
        ProjectMembers.user_id == current_user.id,
    )

    member_id = await db.scalar(member_query)

    if member_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project.",
        )
    conditions: list[ColumnElement[bool]] = [
        ProjectMembers.project_id == project_id,
        Project.is_active.is_(True),
    ]

    if role is not None:
        conditions.append(ProjectMembers.role == role)

    query = (
        select(User.username, ProjectMembers.role)
        .join(User, ProjectMembers.user_id == User.id)
        .join(Project, ProjectMembers.project_id == Project.id)
        .where(*conditions)
    )

    sort_columns = {
        "id": ProjectMembers.id,
        "user_id": ProjectMembers.user_id,
        "username": User.username,
    }
    sort_column = sort_columns.get(sort_by, ProjectMembers.id)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            ProjectMembers.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            ProjectMembers.id.asc(),
        )
    count_query = (
        select(func.count())
        .select_from(ProjectMembers)
        .join(Project, ProjectMembers.project_id == Project.id)
        .where(*conditions)
    )

    total = await db.scalar(count_query) or 0
    result = await db.execute(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )

    list_users = [
        {
            "username": username,
            "role": role,
        }
        for username, role in result.all()
    ]
    return {
        "items": list_users,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }
