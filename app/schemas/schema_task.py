from pydantic import BaseModel, Field

from app.models.model_task import TaskPriority, TaskStatus, TimeUnit


class TaskModel(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority | None = None
    due_unit: TimeUnit | None = None
    due_value: int | None = None
    tags_id: list[int] = Field(default_factory=list)
    assignee_ids: list[int] = Field(default_factory=list)
    dependency_ids: list[int] = Field(default_factory=list)


class TagProjectModel(BaseModel):
    name: str


class TagTaskModel(BaseModel):
    tags_id: list[int]


class TaskDependencyDelete(BaseModel):
    dependency_ids: list[int]


class TaskUpdateModel(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    due_unit: TimeUnit | None = None
    due_value: int | None = None
    assignee_ids: list[int] | None = None
    dependency_ids: list[int] | None = None


class TaskStatusUpdateModel(BaseModel):
    status: TaskStatus


class TaskCommentModel(BaseModel):
    content: str
