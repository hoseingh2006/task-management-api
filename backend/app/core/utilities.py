import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.core.enums import ActivityAction, TimeUnit, UserRole
from app.database.dependency import Database, GetUser
from app.models.model_task import TaskDependency
from app.models.model_user import ActivityLog


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


def add_log(
    action: ActivityAction,
    description: str,
    db: Database,
    current_user: GetUser | None = None,
    project_id: int | None = None,
    task_id: int | None = None,
    role: UserRole = UserRole.USER,
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


##########mentions comment##########
def find_mentions(text):
    pattern = r"@([A-Za-z0-9_]+)"
    return set(re.findall(pattern, text))


def calculate_offset(page: int, page_size: int) -> int:
    return (page - 1) * page_size


def calculate_pages(total: int, page_size: int) -> int:
    return (total + page_size - 1) // page_size
