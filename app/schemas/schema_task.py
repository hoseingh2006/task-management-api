from pydantic import BaseModel

from app.models.model_task import TaskStatus


class TaskModel(BaseModel):
    title: str
    description: str | None = None


class TaskUpdateModel(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskStatusUpdateModel(BaseModel):
    status: TaskStatus
