from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.security import ALGORITHM, SECRET_KEY, oauth2_scheme
from app.database.database import LocalSession
from app.models.model_task import TaskDependency, TimeUnit
from app.models.model_user import ActivityLog, User, UserRole


async def get_db():
    async with LocalSession() as db:
        yield db


Database = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(db: Database, token: str = Depends(oauth2_scheme)):
    try:
        decode_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_token.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.scalars(select(User).where(User.id == user_id))

    user = result.first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
GetUser = Annotated[User, Depends(get_current_user)]


async def check_admin(current_user: GetUser):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="you are not admin"
        )
    return current_user


GetAdmin = Annotated[User, Depends(check_admin)]


def calculate_due_time(value: int, unit: TimeUnit):
    time_now = datetime.now(tz=timezone.utc)
    if unit == TimeUnit.MINUTES:
        due_time = timedelta(minutes=value)
    elif unit == TimeUnit.HOURS:
        due_time = timedelta(hours=value)
    elif unit == TimeUnit.DAYS:
        due_time = timedelta(days=value)
    elif unit == TimeUnit.WEEKS:
        due_time = timedelta(weeks=value)
    elif unit == TimeUnit.MONTHS:
        months = 4 * value
        due_time = timedelta(weeks=months)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    time = time_now + due_time
    return time


##########task dependency##########
async def has_dependency_cycle(
    db: Database,
    task_id: int,
    dependency_id: int,
) -> bool:

    visited: set[int] = set()
    stack: list[int] = [dependency_id]

    while stack:
        current_id = stack.pop()

        if current_id == task_id:
            return True

        if current_id in visited:
            continue

        visited.add(current_id)

        result = await db.scalars(
            select(TaskDependency.depends_on_task_id).where(
                TaskDependency.task_id == current_id
            )
        )

        stack.extend(result.all())

    return False


class ActivityAction(StrEnum):
    # Project
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_STATUS_CHANGED = "project_status_changed"

    # Task
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_STATUS_CHANGED = "task_status_changed"

    # Subtask
    SUBTASK_CREATED = "subtask_created"
    SUBTASK_UPDATED = "subtask_updated"
    SUBTASK_DELETED = "subtask_deleted"
    SUBTASK_STATUS_CHANGED = "subtask_status_changed"

    # Tag
    TAG_CREATED = "tag_created"
    TAG_UPDATED = "tag_updated"
    TAG_DELETED = "tag_deleted"

    # Comment
    COMMENT_CREATED = "comment_created"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"

    # User
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"

    # Project Member
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_CHANGED = "member_role_changed"

    # Task relations
    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"

    # Tag relations
    TAG_ADDED_TO_TASK = "tag_added_to_task"
    TAG_REMOVED_FROM_TASK = "tag_removed_from_task"

    # Dependency
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_UPDATED = "dependency_updated"
    DEPENDENCY_REMOVED = "dependency_removed"


async def add_log(
    action: ActivityAction,
    description: str,
    db: Database,
    current_user: GetUser | None = None,
    project_id: int | None = None,
    task_id: int | None = None,
    role: UserRole | None = None,
):
    if current_user is None:
        activity = ActivityLog(
            action=action,
            description=description,
            project_id=project_id,
            task_id=task_id,
            role=role,
        )
    else:
        activity = ActivityLog(
            action=action,
            description=description,
            user_id=current_user.id,
            project_id=project_id,
            task_id=task_id,
            role=role,
        )

    db.add(activity)
