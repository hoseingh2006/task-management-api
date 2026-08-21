from database.database import Base
from models.model_project import Project
from models.model_user import User
from sqlalchemy import BOOLEAN, INTEGER, TEXT, VARCHAR, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TaskStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    description: Mapped[str] = mapped_column(TEXT)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.ACTIVE
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    assignees: Mapped[list["User"]] = relationship(
        secondary="task_assignee", back_populates="assigned_tasks"
    )
    project: Mapped["Project"] = relationship(back_populates="tasks")

    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id], back_populates="created_tasks"
    )


class TaskAssignee(Base):
    __tablename__ = "task_assignee"

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
