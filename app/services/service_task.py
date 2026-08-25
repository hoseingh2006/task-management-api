from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from app.database.dependency import Database, GetUser
from app.models.model_project import Project, ProjectMembers, ProjectRole
from app.models.model_task import Task, TaskAssignee
from app.models.model_user import User
from app.schemas.schema_task import (
    TaskModel,
    TaskStatus,
    TaskStatusUpdateModel,
    TaskUpdateModel,
)


##########Task Routers##########
async def create_task(
    task_model: TaskModel,
    db: Database,
    current_user: GetUser,
    project_id: int,
):
    # 1. Project
    result = await db.scalars(
        select(Project).where(
            Project.id == project_id,
            Project.is_active.is_(True),
        )
    )

    project = result.first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # 2. Permission
    result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )

    member = result.first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    if member.role not in (
        ProjectRole.OWNER,
        ProjectRole.MANAGER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create task",
        )

    # 3. Validate assignees
    assignee_ids = set(task_model.assignee_ids)

    if assignee_ids:
        result = await db.scalars(
            select(ProjectMembers).where(
                ProjectMembers.project_id == project_id,
                ProjectMembers.user_id.in_(assignee_ids),
            )
        )

        members = result.all()

        if len(members) != len(assignee_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more assignees are not members of this project",
            )

        users = await db.scalars(select(User).where(User.id.in_(assignee_ids)))

        users = users.all()
    else:
        users = []

    # 4. Create Task
    task = Task(
        title=task_model.title,
        description=task_model.description,
        project_id=project_id,
        creator_id=current_user.id,
    )

    task.assignees = users

    db.add(task)

    await db.commit()
    await db.refresh(task)

    return {
        "message": "Task created successfully!",
        "task_id": task.id,
    }


async def get_tasks(current_user: GetUser, db: Database, project_id: int):
    project_result = await db.execute(
        select(Project.id, ProjectMembers.role)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.is_active.is_(True),
            Project.id == project_id,
        )
    )
    project = project_result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not found project")
    if project.role in (ProjectRole.OWNER, ProjectRole.MANAGER):
        tasks = await db.scalars(
            select(Task).where(
                Task.project_id == project.id,
            )
        )
        return tasks.all()
    user_task = await db.scalars(
        select(Task)
        .join(TaskAssignee, Task.id == TaskAssignee.task_id)
        .where(
            Task.project_id == project_id,
            TaskAssignee.user_id == current_user.id,
            Task.is_active.is_(True),
        )
    )
    return user_task.all()


async def get_task_id(
    current_user: GetUser, db: Database, project_id: int, task_id: int
):
    project_result = await db.execute(
        select(Project.id, ProjectMembers.role)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.is_active.is_(True),
            Project.id == project_id,
        )
    )
    project = project_result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not found project")
    if project.role in (
        ProjectRole.OWNER,
        ProjectRole.MANAGER,
        ProjectRole.VIEWER,
    ):
        result = await db.scalars(
            select(Task).where(Task.project_id == project.id, Task.id == task_id)
        )
        task = result.first()
        if task is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not find task")

        return task
    result = await db.scalars(
        select(Task)
        .join(TaskAssignee, Task.id == TaskAssignee.task_id)
        .where(
            Task.project_id == project_id,
            TaskAssignee.user_id == current_user.id,
            Task.id == task_id,
        )
    )
    task = result.first()
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not find task")
    return task


async def update_task(
    task_model: TaskUpdateModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
):
    # 1. Project
    result = await db.scalars(
        select(Project).where(
            Project.id == project_id,
            Project.is_active.is_(True),
        )
    )

    project = result.first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # 2. Permission
    result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )

    member = result.first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )

    if member.role not in (
        ProjectRole.OWNER,
        ProjectRole.MANAGER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create task",
        )
    result_task = await db.scalars(
        select(Task)
        .options(selectinload(Task.assignees))
        .where(
            Task.project_id == project_id,
            Task.id == task_id,
        )
    )
    task = result_task.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task not found",
        )
    if task_model.title is not None:
        task.title = task_model.title
    if task_model.description is not None:
        task.description = task_model.description
    if task_model.assignee_ids is not None:
        assignee_ids = set(task_model.assignee_ids)
        if assignee_ids:
            result = await db.scalars(
                select(ProjectMembers).where(
                    ProjectMembers.project_id == project_id,
                    ProjectMembers.user_id.in_(assignee_ids),
                )
            )

            members = result.all()

            if len(members) != len(assignee_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more assignees are not members of this project",
                )

            users = await db.scalars(select(User).where(User.id.in_(assignee_ids)))

            users = users.all()
        else:
            users = []

        task.assignees = users
    await db.commit()
    await db.refresh(task)
    return {"massage": "successfully updated "}


async def delete_task(
    current_user: GetUser, db: Database, project_id: int, task_id: int
):
    project_result = await db.execute(
        select(Project.id, ProjectMembers.role)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.is_active.is_(True),
            Project.id == project_id,
        )
    )
    project = project_result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not found project")
    if project.role in (
        ProjectRole.OWNER,
        ProjectRole.MANAGER,
    ):
        result = await db.scalars(
            select(Task).where(Task.project_id == project_id, Task.id == task_id)
        )
        task = result.first()
        if task is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not find task")

        task.is_active = False
        task.status = TaskStatus.ARCHIVED
        await db.commit()
        return {"massage": "delete successfully!"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete task",
        )


##########Status task Routers##########
async def update_task_status(
    status_model: TaskStatusUpdateModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
):
    project_result = await db.execute(
        select(Project.id, ProjectMembers.role)
        .join(ProjectMembers, Project.id == ProjectMembers.project_id)
        .where(
            ProjectMembers.user_id == current_user.id,
            Project.is_active.is_(True),
            Project.id == project_id,
        )
    )
    project = project_result.first()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not found project")
    if project.role in (ProjectRole.OWNER, ProjectRole.MANAGER):
        result = await db.scalars(
            select(Task).where(
                Task.project_id == project_id,
                Task.id == task_id,
                Task.is_active.is_(True),
            )
        )
    elif project.role == ProjectRole.MEMBER:  # MEMBER
        result = await db.scalars(
            select(Task)
            .join(TaskAssignee, Task.id == TaskAssignee.task_id)
            .where(
                Task.project_id == project_id,
                Task.id == task_id,
                TaskAssignee.user_id == current_user.id,
                Task.is_active.is_(True),
            )
        )
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update task status",
        )
    task = result.first()
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Not find task")
    if status_model.status in (TaskStatus.COMPLETED, TaskStatus.ACTIVE):
        task.status = status_model.status
        await db.commit()
        await db.refresh(task)
        return {"message": "successfully update task status "}
    else:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="for archive use delete endpoint"
        )
