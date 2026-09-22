from datetime import datetime

from sqlalchemy import BOOLEAN, INTEGER, TEXT, VARCHAR, DateTime, ForeignKey, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ActivityAction, UserRole
from app.database.database import Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    first_name: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(250))
    username: Mapped[str] = mapped_column(VARCHAR(250), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(TEXT)
    email: Mapped[str] = mapped_column(VARCHAR(250), index=True, unique=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
    )
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    project_members: Mapped[list["ProjectMembers"]] = relationship(  # type: ignore  # noqa: F821
        back_populates="user",
        passive_deletes=True,
    )
    created_tasks: Mapped[list["Task"]] = relationship(  # type: ignore  # noqa: F821
        foreign_keys="Task.creator_id",
        back_populates="creator",
        passive_deletes=True,
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(  # type: ignore  # noqa: F821
        secondary="task_assignee",
        back_populates="assignees",
        passive_deletes=True,
    )


class ActivityLog(Base):
    __tablename__ = "activity_log"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
    )
    action: Mapped[ActivityAction] = mapped_column(SQLEnum(ActivityAction), index=True)
    description: Mapped[str] = mapped_column(TEXT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id", ondelete="CASCADE"), nullable=True
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"), nullable=True
    )
