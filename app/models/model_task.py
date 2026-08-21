from sqlalchemy import INTEGER, VARCHAR, TEXT, ForeignKey, BOOLEAN
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base
from models.model_project import Project, ProjectMembers
from models.model_task import Task


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    description: Mapped[str] = mapped_column(TEXT)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    assignee_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    project: Mapped["Project"] = relationship(back_populates="tasks")

    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id], back_populates="created_tasks"
    )

    assignee: Mapped["User"] = relationship(
        foreign_keys=[assignee_id], back_populates="assigned_tasks"
    )
