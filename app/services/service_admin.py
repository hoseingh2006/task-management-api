from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from starlette import status

from app.core.security import Password_hash
from app.database.dependency import Database
from app.models.model_project import Project, ProjectMembers
from app.models.model_task import Task
from app.models.model_user import User
from app.schemas.schema_admin import (
    UserRole,
    UserUpdateAdminModel,
    UserUpdateAdminPasswordModel,
)


######user############
async def get_user(db: Database):
    result = await db.scalars(select(User))
    users = result.all()
    return users


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
    await db.commit()
    await db.refresh(user)
    return {"massage": "successfully change password!"}


######project############
async def get_projects(db: Database):
    result = await db.scalars(select(Project))
    projects = result.all()
    return projects


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
    await db.delete(project)
    await db.commit()
    return {"massage": "successfully deleted!"}


async def get_project_member(project_id: int, db: Database):
    result = await db.scalars(
        select(Project)
        .options(selectinload(Project.members).selectinload(ProjectMembers.user))
        .where(Project.id == project_id)
    )
    project = result.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    project_member = []
    for i in project.members:
        if i.user_id is not None:
            project_member.append(i)
    return project_member


######task############
async def get_tasks(db: Database):
    result = await db.scalars(select(Task))
    tasks = result.all()
    return tasks


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
    await db.commit()
    return {"massage": "successfully deleted!"}


async def dashboard(db: Database):
    task_active = await db.scalar(
        select(func.count(Task.id)).where(Task.is_active == True)
    )
    task_deactivate = await db.scalar(
        select(func.count(Task.id)).where(Task.is_active == True)
    )
    project_active = await db.scalar(
        select(func.count(Project.id)).where(Project.is_active == True)
    )
    project_deactivate = await db.scalar(
        select(func.count(Project.id)).where(Project.is_active == False)
    )
    user_active = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    user_deactivate = await db.scalar(
        select(func.count(User.id)).where(User.is_active == False)
    )
    admins = await db.scalar(select(func.count(User.role == UserRole.ADMIN)))
    return {
        "task_active": task_active,
        "task_deactivate": task_deactivate,
        "project_active": project_active,
        "project_deactivate": project_deactivate,
        "user_active": user_active,
        "user_deactivate": user_deactivate,
        "admins": admins,
    }
