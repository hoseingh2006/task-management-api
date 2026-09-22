from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.sql.elements import ColumnElement
from starlette import status

from app.core.enums import (
    ActivityAction,
    ProjectRole,
    ProjectStatus,
    TagScope,
    TaskPriority,
    TaskStatus,
    UserRole,
)
from app.core.security import Password_hash
from app.core.utilities import add_log, calculate_offset, calculate_pages
from app.database.dependency import (
    Database,
)
from app.models.model_project import Project, ProjectMembers
from app.models.model_task import Tag, Task
from app.models.model_user import ActivityLog, User
from app.schemas.schema_admin import (
    TagModel,
    UserUpdateAdminModel,
    UserUpdateAdminPasswordModel,
)


######user############
async def get_user(
    db: Database,
    page: int,
    page_size: int,
    role: UserRole | None = None,
    is_active: bool | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions = []
    if role is not None:
        conditions.append(User.role == role)
    if is_active is not None:
        conditions.append(User.is_active.is_(is_active))
    query = select(User).where(*conditions)
    sort_columns = {
        "id": User.id,
        "username": User.username,
        "firstname": User.first_name,
    }
    sort_column = sort_columns.get(sort_by, User.id)
    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            User.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            User.id.asc(),
        )
    count_query = select(func.count()).select_from(User).where(*conditions)
    total = await db.scalar(count_query) or 0
    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    users = result.all()
    return {
        "items": users,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
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
async def get_projects(
    db: Database,
    page: int,
    page_size: int,
    status: ProjectStatus | None = None,
    is_active: bool | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions = []

    if status is not None:
        conditions.append(Project.status == status)

    if is_active is not None:
        conditions.append(Project.is_active.is_(is_active))

    query = select(Project).where(*conditions)

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
    count_query = select(func.count()).select_from(Project).where(*conditions)

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


async def get_project_member(
    project_id: int,
    db: Database,
    page: int,
    page_size: int,
    role: ProjectRole | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions = [ProjectMembers.project_id == project_id]

    if role is not None:
        conditions.append(ProjectMembers.role == role)
    query = select(ProjectMembers).where(*conditions)

    sort_columns = {
        "id": ProjectMembers.id,
        "user_id": ProjectMembers.user_id,
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
    count_query = select(func.count()).select_from(ProjectMembers).where(*conditions)
    total = await db.scalar(count_query) or 0
    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )

    members = result.all()
    return {
        "items": members,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


######task############
async def get_tasks(
    db: Database,
    page: int,
    page_size: int,
    status: TaskStatus | None = None,
    is_active: bool | None = None,
    priority: TaskPriority | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions = []
    if status is not None:
        conditions.append(Task.status == status)

    if is_active is not None:
        conditions.append(Task.is_active.is_(is_active))
    if priority is not None:
        conditions.append(Task.priority == priority)

    query = select(Task).where(*conditions)

    sort_columns = {
        "id": Task.id,
        "project_id": Task.project_id,
        "due_date": Task.due_date,
        "creator_id": Task.creator_id,
        "title": Task.title,
    }
    sort_column = sort_columns.get(sort_by, Task.id)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            Task.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            Task.id.asc(),
        )
    count_query = select(func.count()).select_from(Task).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    tasks = result.all()
    return {
        "items": tasks,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
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
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.role == UserRole.USER)
    )
    admin_logs = await db.scalar(
        select(func.count())
        .select_from(ActivityLog)
        .where(ActivityLog.role == UserRole.ADMIN)
    )

    task_active = await db.scalar(
        select(func.count()).select_from(Task).where(Task.is_active.is_(True))
    )
    task_deactivate = await db.scalar(
        select(func.count()).select_from(Task).where(Task.is_active.is_(False))
    )
    project_active = await db.scalar(
        select(func.count()).select_from(Project).where(Project.is_active.is_(True))
    )
    project_deactivate = await db.scalar(
        select(func.count()).select_from(Project).where(Project.is_active.is_(False))
    )
    user_active = await db.scalar(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )
    user_deactivate = await db.scalar(
        select(func.count()).select_from(User).where(User.is_active.is_(False))
    )
    admins = await db.scalar(
        select(func.count())
        .select_from(User)
        .where(
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


async def get_all_tag(
    db: Database,
    page: int,
    page_size: int,
    scope: TagScope | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions = []
    if scope is not None:
        conditions.append(Tag.scope == scope)

    query = select(Tag).where(*conditions)

    sort_columns = {
        "id": Tag.id,
        "project_id": Tag.project_id,
        "name": Tag.name,
    }
    sort_column = sort_columns.get(sort_by, Tag.id)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            Tag.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            Tag.id.asc(),
        )
    count_query = select(func.count()).select_from(Tag).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    tags = result.all()
    return {
        "items": tags,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


# async def get_all_project_tag(db: Database, page: int, page_size: int):
#     total = await db.scalar(
#         select(func.count()).select_from(Tag).where(Tag.scope == TagScope.PROJECT)
#     )
#     result_tag = await db.scalars(
#         select(Tag)
#         .where(Tag.scope == TagScope.PROJECT)
#         .order_by(Tag.id)
#         .offset(calculate_offset(page, page_size))
#         .limit(page_size)
#     )
#     tag = result_tag.all()
#     return {
#         "items": tag,
#         "page": page,
#         "page_size": page_size,
#         "total": total,
#         "pages": calculate_pages(total, page_size),  # type: ignore
#     }


# async def get_all_global_tag(db: Database, page: int, page_size: int):
#     total = await db.scalar(
#         select(func.count()).select_from(Tag).where(Tag.scope == TagScope.GLOBAL)
#     )
#     result_tag = await db.scalars(
#         select(Tag)
#         .where(Tag.scope == TagScope.GLOBAL)
#         .order_by(Tag.id)
#         .offset(calculate_offset(page, page_size))
#         .limit(page_size)
#     )
#     tag = result_tag.all()
#     return {
#         "items": tag,
#         "page": page,
#         "page_size": page_size,
#         "total": total,
#         "pages": calculate_pages(total, page_size),  # type: ignore
#     }


async def get_all_tag_with_project(
    db: Database,
    project_id: int,
    page: int,
    page_size: int,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions = [Tag.project_id == project_id]

    query = select(Tag).where(*conditions)

    sort_columns = {
        "id": Tag.id,
        "name": Tag.name,
    }
    sort_column = sort_columns.get(sort_by, Tag.id)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            Tag.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            Tag.id.asc(),
        )
    count_query = select(func.count()).select_from(Tag).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    tags = result.all()
    return {
        "items": tags,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


async def delete_tag_with_id(db: Database, tag_id: int):
    result_tag = await db.scalars(select(Tag).where(Tag.id == tag_id))
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
async def get_subtasks(
    db: Database,
    page: int,
    page_size: int,
    status: TaskStatus | None = None,
    is_active: bool | None = None,
    priority: TaskPriority | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = []

    conditions.append(Task.parent_task_id.is_not(None))
    if status is not None:
        conditions.append(Task.status == status)

    if is_active is not None:
        conditions.append(Task.is_active.is_(is_active))
    if priority is not None:
        conditions.append(Task.priority == priority)

    query = select(Task).where(*conditions)

    sort_columns = {
        "id": Task.id,
        "due_date": Task.due_date,
        "creator_id": Task.creator_id,
        "title": Task.title,
    }
    sort_column = sort_columns.get(sort_by, Task.id)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            Task.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            Task.id.asc(),
        )
    count_query = select(func.count()).select_from(Task).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    tasks = result.all()
    return {
        "items": tasks,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
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
async def get_all_log(
    db: Database,
    page: int,
    page_size: int,
    role: UserRole | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = []

    if role is not None:
        conditions.append(ActivityLog.role == role)

    query = select(ActivityLog).where(*conditions)

    sort_columns = {
        "id": ActivityLog.id,
        "user_id": ActivityLog.user_id,
        "task_id": ActivityLog.task_id,
        "project_id": ActivityLog.project_id,
        "created_at": ActivityLog.created_at,
        "action": ActivityLog.action,
    }
    sort_column = sort_columns.get(sort_by, ActivityLog.created_at)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            ActivityLog.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            ActivityLog.id.asc(),
        )
    count_query = select(func.count()).select_from(ActivityLog).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


# async def get_all_user_log(db: Database, page: int, page_size: int):
#     total = await db.scalar(
#         select(func.count())
#         .select_from(ActivityLog)
#         .where(ActivityLog.role == UserRole.USER)
#     )
#     result = await db.scalars(
#         select(ActivityLog)
#         .where(ActivityLog.role == UserRole.USER)
#         .order_by(ActivityLog.id)
#         .offset(calculate_offset(page, page_size))
#         .limit(page_size)
#     )
#     logs = result.all()
#     return {
#         "items": logs,
#         "page": page,
#         "page_size": page_size,
#         "total": total,
#         "pages": calculate_pages(total, page_size),  # type: ignore
#     }


# async def get_all_admin_log(db: Database, page: int, page_size: int):
#     total = await db.scalar(
#         select(func.count())
#         .select_from(ActivityLog)
#         .where(ActivityLog.role == UserRole.ADMIN)
#     )
#     result = await db.scalars(
#         select(ActivityLog)
#         .where(ActivityLog.role == UserRole.ADMIN)
#         .order_by(ActivityLog.id)
#         .offset(calculate_offset(page, page_size))
#         .limit(page_size)
#     )
#     logs = result.all()
#     return {
#         "items": logs,
#         "page": page,
#         "page_size": page_size,
#         "total": total,
#         "pages": calculate_pages(total, page_size),  # type: ignore
#     }


async def get_log_by_user_id(
    db: Database,
    user_id: int,
    page: int,
    page_size: int,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = [
        ActivityLog.role == UserRole.USER,
        ActivityLog.user_id == user_id,
    ]

    query = select(ActivityLog).where(*conditions)

    sort_columns = {
        "id": ActivityLog.id,
        "task_id": ActivityLog.task_id,
        "project_id": ActivityLog.project_id,
        "created_at": ActivityLog.created_at,
        "action": ActivityLog.action,
    }
    sort_column = sort_columns.get(sort_by, ActivityLog.created_at)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            ActivityLog.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            ActivityLog.id.asc(),
        )
    count_query = select(func.count()).select_from(ActivityLog).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


async def get_log_by_task_id(
    db: Database,
    task_id: int,
    page: int,
    page_size: int,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = [
        ActivityLog.role == UserRole.USER,
        ActivityLog.task_id == task_id,
    ]

    query = select(ActivityLog).where(*conditions)

    sort_columns = {
        "id": ActivityLog.id,
        "user_id": ActivityLog.user_id,
        "project_id": ActivityLog.project_id,
        "created_at": ActivityLog.created_at,
        "action": ActivityLog.action,
    }
    sort_column = sort_columns.get(sort_by, ActivityLog.created_at)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            ActivityLog.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            ActivityLog.id.asc(),
        )
    count_query = select(func.count()).select_from(ActivityLog).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


async def get_log_by_project_id(
    db: Database,
    project_id: int,
    page: int,
    page_size: int,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = [
        ActivityLog.role == UserRole.USER,
        ActivityLog.project_id == project_id,
    ]

    query = select(ActivityLog).where(*conditions)

    sort_columns = {
        "id": ActivityLog.id,
        "user_id": ActivityLog.user_id,
        "task_id": ActivityLog.task_id,
        "created_at": ActivityLog.created_at,
        "action": ActivityLog.action,
    }
    sort_column = sort_columns.get(sort_by, ActivityLog.created_at)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            ActivityLog.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            ActivityLog.id.asc(),
        )
    count_query = select(func.count()).select_from(ActivityLog).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }


async def get_log_by_action(
    db: Database,
    action: str,
    page: int,
    page_size: int,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    conditions: list[ColumnElement[bool]] = [
        ActivityLog.role == UserRole.USER,
        ActivityLog.action == action,
    ]

    query = select(ActivityLog).where(*conditions)

    sort_columns = {
        "id": ActivityLog.id,
        "user_id": ActivityLog.user_id,
        "task_id": ActivityLog.task_id,
        "created_at": ActivityLog.created_at,
        "project_id": ActivityLog.project_id,
    }
    sort_column = sort_columns.get(sort_by, ActivityLog.created_at)

    if sort_order == "desc":
        query = query.order_by(
            sort_column.desc(),
            ActivityLog.id.desc(),
        )
    else:
        query = query.order_by(
            sort_column.asc(),
            ActivityLog.id.asc(),
        )
    count_query = select(func.count()).select_from(ActivityLog).where(*conditions)

    total = await db.scalar(count_query) or 0

    result = await db.scalars(
        query.offset(calculate_offset(page, page_size)).limit(page_size)
    )
    logs = result.all()
    return {
        "items": logs,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": calculate_pages(total, page_size),
    }
