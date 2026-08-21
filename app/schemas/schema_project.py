from pydantic import BaseModel
from models.model_project import ProjectStatus


class ProjectModel(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdateModel(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectStatusUpdateModel(BaseModel):
    status: ProjectStatus
