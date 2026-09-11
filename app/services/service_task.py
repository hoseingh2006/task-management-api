from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload
from starlette import status

from app.database.dependency import (
    Database,
    GetUser,
    calculate_due_time,
    has_dependency_cycle,
)
from app.models.model_project import Project, ProjectMembers, ProjectRole
from app.models.model_task import (
    Tag,
    TagScope,
    Task,
    TaskAssignee,
    TaskDependency,
    TaskLabel,
)
from app.models.model_user import User
from app.schemas.schema_task import (
    TagProjectModel,
    TagTaskModel,
    TaskDependencyDelete,
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

    if (task_model.due_value is None) != (task_model.due_unit is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="due_value and due_unit must be provided together",
        )
    due_time = None

    if task_model.due_value is not None and task_model.due_unit is not None:
        due_time = calculate_due_time(
            value=task_model.due_value, unit=task_model.due_unit
        )

    task = Task(
        title=task_model.title,
        description=task_model.description,
        project_id=project_id,
        due_date=due_time,
        priority=task_model.priority,
        creator_id=current_user.id,
    )

    task.assignees = users

    db.add(task)
    await db.flush()

    tag_ids = set(task_model.tags_id)

    if tag_ids:
        result = await db.scalars(select(Tag).where(Tag.id.in_(tag_ids)))

        tags = result.all()

        if len(tags) != len(tag_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more tags not found",
            )

        for tag in tags:
            if tag.scope == TagScope.PROJECT and tag.project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="One or more tags do not belong to this project",
                )

            db.add(
                TaskLabel(
                    task_id=task.id,
                    tag_id=tag.id,
                )
            )
    dependency_ids = set(task_model.dependency_ids)
    if dependency_ids:
        result = await db.scalars(
            select(Task).where(
                Task.id.in_(dependency_ids),
                Task.is_active.is_(True),
                Task.project_id == project_id,
            )
        )
        dependency_tasks = result.all()
        if len(dependency_tasks) != len(dependency_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more Task are not  of this project",
            )
        for dependency_task in dependency_tasks:
            db.add(
                TaskDependency(task_id=task.id, depends_on_task_id=dependency_task.id)
            )

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
    if task_model.priority is not None:
        task.priority = task_model.priority
    if task_model.due_value is not None and task_model.due_unit is not None:
        due_time = calculate_due_time(
            value=task_model.due_value, unit=task_model.due_unit
        )
        task.due_date = due_time
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

    if task_model.dependency_ids is not None:
        dependency_ids = set(task_model.dependency_ids)

        result = await db.scalars(
            select(Task).where(
                Task.id.in_(dependency_ids),
                Task.is_active.is_(True),
                Task.project_id == project_id,
            )
        )

        dependency_tasks = result.all()

        if len(dependency_tasks) != len(dependency_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more dependency tasks are invalid",
            )

        # خود Task نمی‌تواند dependency خودش باشد
        if task.id in dependency_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A task cannot depend on itself",
            )

        # اول cycle را بررسی کن
        for dependency_task in dependency_tasks:
            cycle_check = await has_dependency_cycle(
                db=db,
                task_id=task.id,
                dependency_id=dependency_task.id,
            )

            if cycle_check:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This dependency would create a cycle",
                )

        # حالا dependencyهای قبلی را حذف کن
        result = await db.scalars(
            select(TaskDependency).where(TaskDependency.task_id == task.id)
        )

        dependencies = result.all()

        for dependency in dependencies:
            await db.delete(dependency)

        # dependencyهای جدید را اضافه کن
        for dependency_task in dependency_tasks:
            db.add(
                TaskDependency(
                    task_id=task.id,
                    depends_on_task_id=dependency_task.id,
                )
            )


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
    if status_model.status is (TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS):
        result = await db.scalars(
            select(Task.status)
            .join(TaskDependency, TaskDependency.depends_on_task_id == Task.id)
            .where(
                TaskDependency.task_id == task.id,
                Task.is_active.is_(True),
            )
        )
        dependency_statuses = result.all()
        if any(status != TaskStatus.COMPLETED for status in dependency_statuses):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="You must complete all dependencies first",
            )

    if status_model.status is TaskStatus.ARCHIVED:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="for archive use delete endpoint"
        )
    task.status = status_model.status
    await db.commit()
    await db.refresh(task)
    return {"message": "successfully update task status "}


##########tag project\task##########
async def create_tag(
    tag_model: TagProjectModel, db: Database, current_user: GetUser, project_id: int
):
    result_project = await db.scalars(
        select(Project).where(
            Project.id == project_id,
            Project.is_active.is_(True),
        )
    )
    project = result_project.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
    result_project_member = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    project_member = result_project_member.first()
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="not find project"
        )
    if project_member.role not in (ProjectRole.OWNER, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have access to create Tag ",
        )
    result_tag = await db.scalars(
        select(Tag).where(
            Tag.project_id == project_id,
            Tag.name == tag_model.name,
        )
    )
    tag = result_tag.first()
    if tag is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="already exists tag in project"
        )
    new_tag = Tag(project_id=project_id, name=tag_model.name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    return {"message": "successfully create Tag"}


async def update_tag(
    tag_model: TagProjectModel,
    db: Database,
    tag_id: int,
    current_user: GetUser,
    project_id: int,
):
    project_member_result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    project_member = project_member_result.first()
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
    if project_member.role not in (ProjectRole.OWNER, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to change",
        )
    tag_result = await db.scalars(
        select(Tag)
        .join(Project, Project.id == Tag.project_id)
        .where(
            Tag.id == tag_id,
            Tag.project_id == project_id,
            Project.is_active.is_(True),
        )
    )
    tag = tag_result.first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in this project",
        )

    tag.name = tag_model.name
    await db.commit()
    return {"message": "update tag successfully"}


async def delete_tag(
    db: Database,
    tag_id: int,
    current_user: GetUser,
    project_id: int,
):
    project_member_result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    project_member = project_member_result.first()
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
    if project_member.role not in (ProjectRole.OWNER, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to change",
        )
    tag_result = await db.scalars(
        select(Tag)
        .join(Project, Project.id == Tag.project_id)
        .where(
            Tag.id == tag_id,
            Tag.project_id == project_id,
            Project.is_active.is_(True),
        )
    )
    tag = tag_result.first()
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in this project",
        )

    await db.delete(tag)
    await db.commit()
    return {"message": "delete tag successfully"}


async def select_all_project_tag(
    db: Database,
    current_user: GetUser,
    project_id: int,
):
    project_member_result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    project_member = project_member_result.first()
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
    tag_result = await db.scalars(
        select(Tag).where(
            or_(
                Tag.project_id == project_id,
                Tag.scope == TagScope.GLOBAL,
            )
        )
    )
    tag = tag_result.all()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found in this project",
        )

    return tag


async def select_all_tag_with_project_task(
    db: Database,
    task_id: int,
    current_user: GetUser,
    project_id: int,
):
    project_member_result = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    project_member = project_member_result.first()
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
    task_result = await db.scalars(
        select(Task).where(
            Task.id == task_id, Task.project_id == project_id, Task.is_active.is_(True)
        )
    )
    task = task_result.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
        )

    return task.tags


##########tag project\task##########
async def add_tags_to_task(
    tag_model: TagTaskModel,
    db: Database,
    current_user: GetUser,
    project_id: int,
    task_id: int,
):
    result_project = await db.scalars(
        select(Project).where(
            Project.id == project_id,
            Project.is_active.is_(True),
        )
    )
    project = result_project.first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
        )

    result_task = await db.scalars(
        select(Task).where(
            Task.id == task_id, Task.project_id == project_id, Task.is_active.is_(True)
        )
    )
    task = result_task.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="task not exists in project",
        )

    result_project_member = await db.scalars(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == current_user.id,
        )
    )
    project_member = result_project_member.first()
    if project_member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project",
        )
    if project_member.role not in (ProjectRole.OWNER, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You dont have access to create Tag ",
        )

    tag_ids = set(tag_model.tags_id)
    if not tag_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tags provided",
        )
    result = await db.scalars(select(Tag).where(Tag.id.in_(tag_ids)))
    tags = result.all()
    if len(tags) != len(tag_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more tags not found",
        )
    for tag in tags:
        if tag.scope == TagScope.PROJECT and tag.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="One or more tags do not belong to this project",
            )
    existing_tags = await db.scalars(
        select(TaskLabel.tag_id).where(
            TaskLabel.task_id == task.id,
            TaskLabel.tag_id.in_(tag_ids),
        )
    )

    existing_tag_ids = set(existing_tags.all())
    for tag in tags:
        if tag.id in existing_tag_ids:
            continue

        db.add(
            TaskLabel(
                task_id=task.id,
                tag_id=tag.id,
            )
        )
    await db.commit()

    return {"message": "successfully create Tag"}


##########subtask##########
async def create_subtask(
    task_model: TaskModel,
    db: Database,
    current_user: GetUser,
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
    result = await db.scalars(
        select(Task).where(
            Task.project_id == project_id, Task.is_active.is_(True), Task.id == task_id
        )
    )
    task = result.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found in this project",
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

    if (task_model.due_value is None) != (task_model.due_unit is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="due_value and due_unit must be provided together",
        )
    due_time = None

    if task_model.due_value is not None and task_model.due_unit is not None:
        due_time = calculate_due_time(
            value=task_model.due_value, unit=task_model.due_unit
        )

    subtask = Task(
        title=task_model.title,
        description=task_model.description,
        project_id=project_id,
        due_date=due_time,
        parent_task_id=task.id,
        priority=task_model.priority,
        creator_id=current_user.id,
    )

    subtask.assignees = users

    db.add(subtask)
    await db.flush()

    tag_ids = set(task_model.tags_id)

    if tag_ids:
        result = await db.scalars(select(Tag).where(Tag.id.in_(tag_ids)))

        tags = result.all()

        if len(tags) != len(tag_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more tags not found",
            )

        for tag in tags:
            if tag.scope == TagScope.PROJECT and tag.project_id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="One or more tags do not belong to this project",
                )

            db.add(
                TaskLabel(
                    task_id=subtask.id,
                    tag_id=tag.id,
                )
            )
    await db.commit()
    await db.refresh(subtask)
    return {
        "message": "Subtask created successfully",
        "task_id": subtask.id,
    }


async def get_subtask_with_task(
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
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    result = await db.scalars(
        select(Task).where(
            Task.project_id == project_id,
            Task.is_active.is_(True),
            Task.parent_task_id == task_id,
        )
    )
    tasks = result.all()
    return tasks


async def update_subtask(
    task_model: TaskUpdateModel,
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
    subtask_id: int,
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
        select(Task).where(
            Task.project_id == project_id,
            Task.id == task_id,
            Task.is_active.is_(True),
        )
    )
    task = result_task.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found",
        )
    result_subtask = await db.scalars(
        select(Task).where(
            Task.project_id == project_id,
            Task.parent_task_id == task_id,
            Task.is_active.is_(True),
            Task.id == subtask_id,
        )
    )
    subtask = result_subtask.first()
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )

    if task_model.title is not None:
        subtask.title = task_model.title
    if task_model.description is not None:
        subtask.description = task_model.description
    if task_model.priority is not None:
        subtask.priority = task_model.priority
    if (task_model.due_value is None) != (task_model.due_unit is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="due_value and due_unit must be provided together",
        )
    if task_model.due_value is not None:
        subtask.due_date = calculate_due_time(
            value=task_model.due_value,
            unit=task_model.due_unit,
        )
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

        subtask.assignees = users
    await db.commit()
    await db.refresh(subtask)
    return {"message": "Subtask updated successfully"}


async def delete_subtask(
    current_user: GetUser,
    db: Database,
    project_id: int,
    task_id: int,
    subtask_id: int,
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
            detail="You don't have permission to delete subtask",
        )
    result_task = await db.scalars(
        select(Task).where(
            Task.project_id == project_id,
            Task.id == task_id,
            Task.is_active.is_(True),
        )
    )
    task = result_task.first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent task not found",
        )
    result_subtask = await db.scalars(
        select(Task).where(
            Task.project_id == project_id,
            Task.parent_task_id == task_id,
            Task.is_active.is_(True),
            Task.id == subtask_id,
        )
    )
    subtask = result_subtask.first()
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subtask not found",
        )
    subtask.is_active = False
    await db.commit()
    return {"message": "Subtask deleted successfully"}


##########task dependency##########
async def get_task_dependency(
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
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    task = await db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id,
            Task.is_active.is_(True),
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if project.role not in (ProjectRole.OWNER, ProjectRole.MANAGER):
        is_assignee = await db.scalar(
            select(TaskAssignee.task_id).where(
                TaskAssignee.task_id == task_id,
                TaskAssignee.user_id == current_user.id,
            )
        )

        if is_assignee is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this task",
            )

    result = await db.scalars(
        select(Task)
        .join(TaskDependency, TaskDependency.depends_on_task_id == Task.id)
        .where(
            TaskDependency.task_id == task_id,
            Task.is_active.is_(True),
        )
    )

    return result.all()


async def delete_task_dependency(
    current_user: GetUser,
    db: Database,
    project_id: int,
    model_dependency: TaskDependencyDelete,
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
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Project not found")
    task = await db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id,
            Task.is_active.is_(True),
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if project.role not in (ProjectRole.OWNER, ProjectRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete depends task",
        )
    task_dependency = set(model_dependency.dependency_ids)
    result = await db.scalars(
        select(TaskDependency).where(
            TaskDependency.depends_on_task_id.in_(task_dependency),
            TaskDependency.task_id == task_id,
        )
    )
    dependencies = result.all()
    for dependency in dependencies:
        await db.delete(dependency)
    await db.commit()
    return {"message": "delete depends tasks successfully"}
