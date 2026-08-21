from database.dependancy import Datatbase
from models.model_user import User
from models.model_project import Project, ProjectMembers
from models.model_task import Task
from schemas.schema_admin import UserRole
from fastapi import HTTPException
from starlette import status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from schemas.schema_admin import UserUpdeateAdminModel, UserUpdeateAdminPasswordModel
from core.security import Password_hash


######user############
async def get_user(db: Datatbase):
    resualt = await db.scalars(select(User))
    users = resualt.all()
    return users


async def get_user_id(user_id: int, db: Datatbase):
    resualt = await db.scalars(select(User).where(User.id == user_id))
    user = resualt.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


async def delete_user(
    db: Datatbase,
    user_id: int,
):
    resualt = await db.scalars(select(User).where(User.id == user_id))
    user = resualt.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await db.delete(user)
    await db.commit()
    return {"massage": "sucessfully deleted!"}


async def updeate_user(db: Datatbase, user_id: int, user_model: UserUpdeateAdminModel):
    resualt = await db.scalars(select(User).where(User.id == user_id))
    user = resualt.first()
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
        user_model.role = user_model.role
    await db.commit()
    await db.refresh(user)
    return user


async def updeate_password_user(
    db: Datatbase, user_id: int, password_model: UserUpdeateAdminPasswordModel
):
    resualt = await db.scalars(select(User).where(User.id == user_id))
    user = resualt.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.password_hash = Password_hash.hash(password_model.password)
    return {"massage": "sucessfully change password!"}


######project############
async def get_projects(db: Datatbase):
    resualt = await db.scalars(select(Project))
    projects = resualt.all()
    return projects


async def get_project_id(project_id: int, db: Datatbase):
    resualt = await db.scalars(select(Project).where(Project.id == project_id))
    project = resualt.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


async def delete_project(
    db: Datatbase,
    project_id: int,
):
    resualt = await db.scalars(select(Project).where(Project.id == project_id))
    project = resualt.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="project not found"
        )
    await db.delete(project)
    await db.commit()
    return {"massage": "sucessfully deleted!"}


async def get_project_member(project_id: int, db: Datatbase):
    resualt = await db.scalars(
        select(Project)
        .options(selectinload(Project.members).selectinload(ProjectMembers.user))
        .where(Project.id == project_id)
    )
    project = resualt.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project.members


######task############
async def get_tasks(db: Datatbase):
    resualt = await db.scalars(select(Task))
    tasks = resualt.all()
    return tasks


async def get_task_id(task_id: int, db: Datatbase):
    resualt = await db.scalars(select(Task).where(Task.id == task_id))
    task = resualt.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


async def delete_task(
    db: Datatbase,
    task_id: int,
):
    resualt = await db.scalars(select(Task).where(Task.id == task_id))
    task = resualt.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await db.delete(task)
    await db.commit()
    return {"massage": "sucessfully deleted!"}


async def dashboard(db: Datatbase):
    task_active = await db.scalar(select(func.count(Task.is_active == True)))
    task_deactive = await db.scalar(select(func.count(Task.is_active == False)))
    project_active = await db.scalar(select(func.count(Project.is_active == True)))
    project_deactive = await db.scalar(select(func.count(Project.is_active == False)))
    user_active = await db.scalar(select(func.count(User.is_active == True)))
    user_deactive = await db.scalar(select(func.count(User.is_active == False)))
    admins = await db.scalar(select(func.count(User.role == UserRole.ADMIN)))
    return {
        "task_active": task_active,
        "task_deactive": task_deactive,
        "project_active": project_active,
        "project_deactive": project_deactive,
        "user_active": user_active,
        "user_deactive": user_deactive,
        "admins": admins,
    }
