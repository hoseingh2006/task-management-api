from pydantic import BaseModel, Field

from app.models.model_task import TaskStatus


class TaskModel(BaseModel):
    title: str
    description: str | None = None
    assignee_ids: list[int] = Field(default_factory=list)


class TaskUpdateModel(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_ids: list[int] | None = None


class TaskStatusUpdateModel(BaseModel):
    status: TaskStatus
