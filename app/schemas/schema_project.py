from pydantic import BaseModel

from app.core.enums import ProjectRole, ProjectStatus


class ProjectModel(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdateModel(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectStatusUpdateModel(BaseModel):
    status: ProjectStatus


class ProjectMember(BaseModel):
    user_id: int
    role: ProjectRole


class ProjectUpdateMember(BaseModel):
    role: ProjectRole
