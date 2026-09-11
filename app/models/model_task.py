from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import (
    BOOLEAN,
    INTEGER,
    TEXT,
    VARCHAR,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TaskStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"
    EXPIRE = "expire"
    ARCHIVED = "archived"


class TimeUnit(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TagScope(str, Enum):
    PROJECT = "project"
    GLOBAL = "global"


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    description: Mapped[str] = mapped_column(TEXT)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.ACTIVE
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority), default=TaskPriority.LOW
    )
    due_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(tz=timezone.utc) + timedelta(weeks=4)
    )
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    tags: Mapped[list["Tag"]] = relationship(
        secondary="task_labels", back_populates="tasks"
    )
    assignees: Mapped[list["User"]] = relationship(  # type: ignore  # noqa: F821
        secondary="task_assignee", back_populates="assigned_tasks"
    )
    project: Mapped["Project"] = relationship(back_populates="tasks")  # type: ignore  # noqa: F821

    creator: Mapped["User"] = relationship(  # type: ignore  # noqa: F821
        foreign_keys=[creator_id], back_populates="created_tasks"
    )
    parent_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=True,
    )

    parent_task: Mapped["Task | None"] = relationship(
        "Task",
        remote_side="Task.id",
        back_populates="subtasks",
    )

    subtasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="parent_task",
        cascade="all, delete-orphan",
    )


class TaskAssignee(Base):
    __tablename__ = "task_assignee"

    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class TaskLabel(Base):
    __tablename__ = "task_labels"
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), primary_key=True)


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    scope: Mapped[TagScope] = mapped_column(
        SQLEnum(TagScope), default=TagScope.PROJECT, nullable=False
    )
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("project.id"), nullable=True
    )
    project: Mapped["Project|None"] = relationship(back_populates="tags")  # type: ignore  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="tags",
        secondary="task_labels",
    )
    __table_args__ = (UniqueConstraint("project_id", "name"),)


class TaskDependency(Base):
    __tablename__ = "task_dependency"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True,
    )

    depends_on_task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True,
    )


class TaskComment(Base):
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    content: Mapped[str] = mapped_column(TEXT)
    creator_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("user.id"))
    task_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("task.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(BOOLEAN, server_default="True")
