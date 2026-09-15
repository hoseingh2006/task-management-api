from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from starlette import status

from app.core.security import Password_hash
from app.database.dependency import (
    ActivityAction,
    Database,
    add_log,
    calculate_offset,
    calculate_pages,
)
from app.models.model_project import Project, ProjectMembers
from app.models.model_task import Tag, TagScope, Task
from app.models.model_user import ActivityLog, User
from app.schemas.schema_admin import (
    TagModel,
    UserRole,
    UserUpdateAdminModel,
    UserUpdateAdminPasswordModel,
)


######user############
async def get_user(db: Database, page: int, page_size: int):
    total = await db.scalar(select(func.count()).select_from(User))
    result = await db.scalars(
        select(User)
        .order_by(User.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    users = result.all()
    return {
        "items": users,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_user_id(user_id: int, db: Database):
    result = await db.scalars(select(User).where(User.id == user_id))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


async def delete_user(
    db: Database,
    user_id: int,
):
    result = await db.scalars(select(User).where(User.id == user_id))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await db.delete(user)
    add_log(
        action=ActivityAction.USER_DELETED,
        description=f"User '{user.username}' was  Deleted  ",
        db=db,
        role=UserRole.ADMIN,
    )
    await db.commit()
    return {"massage": "successfully deleted!"}


async def update_user(db: Database, user_id: int, user_model: UserUpdateAdminModel):
    result = await db.scalars(select(User).where(User.id == user_id))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user_model.email is not None:
        user.email = user_model.email
    if user_model.username is not None:
        user.username = user_model.username
    if user_model.first_name is not None:
        user.first_name = user_model.first_name
    if user_model.last_name is not None:
        user.last_name = user_model.last_name
    if user_model.is_active is not None:
        user.is_active = user_model.is_active
    if user_model.role is not None:
        user.role = user_model.role
    add_log(
        action=ActivityAction.USER_UPDATED,
        description=f"User '{user.username}' was  Updated  ",
        db=db,
        role=UserRole.ADMIN,
    )
    await db.commit()
    await db.refresh(user)
    return user


async def update_password_user(
    db: Database, user_id: int, password_model: UserUpdateAdminPasswordModel
):
    result = await db.scalars(select(User).where(User.id == user_id))
    user = result.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.password_hash = Password_hash.hash(password_model.password)
    add_log(
        action=ActivityAction.USER_UPDATED,
        description=f"User '{user.username}' was  Updated Password  ",
        db=db,
        role=UserRole.ADMIN,
    )
    await db.commit()
    await db.refresh(user)
    return {"massage": "successfully change password!"}


######project############
async def get_projects(db: Database, page: int, page_size: int):
    total = await db.scalar(select(func.count()).select_from(Project))
    result = await db.scalars(
        select(Project)
        .order_by(Project.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    projects = result.all()
    return {
        "items": projects,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_project_id(project_id: int, db: Database):
    result = await db.scalars(select(Project).where(Project.id == project_id))
    project = result.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


async def delete_project(
    db: Database,
    project_id: int,
):
    result = await db.scalars(select(Project).where(Project.id == project_id))
    project = result.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
        )
    add_log(
        action=ActivityAction.PROJECT_DELETED,
        description=f"Project '{project.name}' was  Deleted  ",
        db=db,
        role=UserRole.ADMIN,
        project_id=project_id,
    )
    await db.delete(project)
    await db.commit()
    return {"massage": "successfully deleted!"}


async def get_project_member(project_id: int, db: Database, page: int, page_size: int):
    total = await db.scalar(
        select(func.count())
        .select_from(ProjectMembers)
        .where(ProjectMembers.project_id == project_id)
    )

    result = await db.scalars(
        select(ProjectMembers)
        .options(selectinload(ProjectMembers.user))
        .where(ProjectMembers.project_id == project_id)
        .order_by(ProjectMembers.user_id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )

    members = result.all()
    return {
        "items": members,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


######task############
async def get_tasks(db: Database, page: int, page_size: int):
    total = await db.scalar(select(func.count()).select_from(Task))
    result = await db.scalars(
        select(Task)
        .order_by(Task.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    tasks = result.all()
    return {
        "items": tasks,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_task_id(task_id: int, db: Database):
    result = await db.scalars(select(Task).where(Task.id == task_id))
    task = result.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


async def delete_task(
    db: Database,
    task_id: int,
):
    result = await db.scalars(select(Task).where(Task.id == task_id))
    task = result.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await db.delete(task)
    add_log(
        action=ActivityAction.TASK_DELETED,
        description=f"Task '{task.title}' was  Deleted  ",
        db=db,
        role=UserRole.ADMIN,
        task_id=task_id,
    )
    await db.commit()
    return {"massage": "successfully deleted!"}


######dashboard############
async def dashboard(db: Database):
    user_logs = await db.scalar(
        select(func.count(ActivityLog.id).where(ActivityLog.role == UserRole.USER))
    )
    admin_logs = await db.scalar(
        select(func.count(ActivityLog.id).where(ActivityLog.role == UserRole.ADMIN))
    )

    task_active = await db.scalar(
        select(func.count(Task.id)).where(Task.is_active.is_(True))
    )
    task_deactivate = await db.scalar(
        select(func.count(Task.id)).where(Task.is_active.is_(False))
    )
    project_active = await db.scalar(
        select(func.count(Project.id)).where(Project.is_active.is_(True))
    )
    project_deactivate = await db.scalar(
        select(func.count(Project.id)).where(Project.is_active.is_(False))
    )
    user_active = await db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    )
    user_deactivate = await db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(False))
    )
    admins = await db.scalar(
        select(func.count(User.id)).where(
            User.role == UserRole.ADMIN,
            User.is_active.is_(True),
        )
    )
    return {
        "task_active": task_active,
        "task_deactivate": task_deactivate,
        "project_active": project_active,
        "project_deactivate": project_deactivate,
        "user_active": user_active,
        "user_deactivate": user_deactivate,
        "admins": admins,
        "admin_logs": admin_logs,
        "user_logs": user_logs,
    }


######Tag############
async def create_tag(tag_model: TagModel, db: Database):
    result_tag = await db.scalars(
        select(Tag.id).where(Tag.name == tag_model.name, Tag.scope == TagScope.GLOBAL)
    )
    tag = result_tag.first()
    if tag is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="this tag already exists"
        )
    new_tag = Tag(name=tag_model.name, scope=TagScope.GLOBAL)
    db.add(new_tag)
    add_log(
        action=ActivityAction.TAG_CREATED,
        description=f"Global Tag '{tag_model.name}' was  Created  ",
        db=db,
        role=UserRole.ADMIN,
    )
    await db.commit()
    return {"message": "successfully create GLOBAL Tag"}


async def get_all_tag(db: Database, page: int, page_size: int):
    total = await db.scalar(select(func.count()).select_from(Tag))
    result_tag = await db.scalars(
        select(Tag)
        .order_by(Tag.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    tag = result_tag.all()
    return {
        "items": tag,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_all_project_tag(db: Database, page: int, page_size: int):
    total = await db.scalar(
        select(func.count()).select_from(Tag).where(Tag.scope == TagScope.PROJECT)
    )
    result_tag = await db.scalars(
        select(Tag)
        .where(Tag.scope == TagScope.PROJECT)
        .order_by(Tag.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    tag = result_tag.all()
    return {
        "items": tag,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_all_global_tag(db: Database, page: int, page_size: int):
    total = await db.scalar(
        select(func.count()).select_from(Tag).where(Tag.scope == TagScope.GLOBAL)
    )
    result_tag = await db.scalars(
        select(Tag)
        .where(Tag.scope == TagScope.GLOBAL)
        .order_by(Tag.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    tag = result_tag.all()
    return {
        "items": tag,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_all_tag_with_project(
    db: Database, project_id: int, page: int, page_size: int
):
    total = await db.scalar(
        select(func.count()).select_from(Tag).where(Tag.project_id == project_id)
    )
    result_tag = await db.scalars(
        select(Tag)
        .where(Tag.project_id == project_id)
        .order_by(Tag.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    tag = result_tag.all()
    return {
        "items": tag,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def delete_tag_with_id(db: Database, tag_id: int):
    result_tag = await db.scalars(
        select(Tag).where(Tag.id == tag_id, Tag.scope == TagScope.GLOBAL)
    )
    tag = result_tag.first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    add_log(
        action=ActivityAction.TAG_DELETED,
        description=f"Global Tag '{tag.name}' was  Deleted  ",
        db=db,
        role=UserRole.ADMIN,
    )
    await db.delete(tag)

    await db.commit()
    return {"message": "Tag deleted successfully!"}


async def update_tag_with_id(db: Database, tag_model: TagModel, tag_id: int):
    result_tag = await db.scalars(
        select(Tag.id).where(
            Tag.name == tag_model.name, Tag.scope == TagScope.GLOBAL, Tag.id != tag_id
        )
    )
    tag = result_tag.first()
    if tag is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="this tag already exists"
        )
    result_tag = await db.scalars(
        select(Tag).where(Tag.scope == TagScope.GLOBAL, Tag.id == tag_id)
    )
    tag = result_tag.first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not find this tag"
        )
    if tag_model.name is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not passed requirement fields",
        )
    tag.name = tag_model.name
    add_log(
        action=ActivityAction.TAG_UPDATED,
        description=f"Global Tag '{tag.name}' was  Updated  ",
        db=db,
        role=UserRole.ADMIN,
    )
    await db.commit()
    return {"message": "update tag is successfully!"}


######subtask############
async def get_subtasks(db: Database, page: int, page_size: int):
    total = await db.scalar(
        select(func.count()).select_from(Task).where(Task.parent_task_id.is_not(None))
    )
    result = await db.scalars(
        select(Task)
        .where(Task.parent_task_id.is_not(None))
        .order_by(Task.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    tasks = result.all()
    return {
        "items": tasks,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_subtask_id(task_id: int, db: Database):
    result = await db.scalars(
        select(Task).where(Task.id == task_id, Task.parent_task_id.is_not(None))
    )
    task = result.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


######Activity Log############
async def get_all_log(db: Database, page: int, page_size: int):
    total = await db.scalar(select(func.count()).select_from(ActivityLog))
    result = await db.scalars(
        select(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_all_user_log(db: Database, page: int, page_size: int):
    total = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.role == UserRole.USER)
    )
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.role == UserRole.USER)
        .order_by(ActivityLog.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_all_admin_log(db: Database, page: int, page_size: int):
    total = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.role == UserRole.ADMIN)
    )
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.role == UserRole.ADMIN)
        .order_by(ActivityLog.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_log_by_user_id(db: Database, user_id: int, page: int, page_size: int):
    total = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.role == UserRole.USER, ActivityLog.user_id == user_id)
    )
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.role == UserRole.USER, ActivityLog.user_id == user_id)
        .order_by(ActivityLog.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_log_by_task_id(db: Database, task_id: int, page: int, page_size: int):
    total = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.task_id == task_id)
    )
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.task_id == task_id)
        .order_by(ActivityLog.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_log_by_project_id(
    db: Database, project_id: int, page: int, page_size: int
):
    total = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.project_id == project_id)
    )
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.project_id == project_id)
        .order_by(ActivityLog.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }


async def get_log_by_action(db: Database, action: str, page: int, page_size: int):
    total = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.action == action)
    )
    result = await db.scalars(
        select(ActivityLog)
        .where(ActivityLog.action == action)
        .order_by(ActivityLog.id)
        .offset(calculate_offset(page, page_size))
        .limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),  # type: ignore
    }
