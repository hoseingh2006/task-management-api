from enum import Enum

from database.database import Base
from models.model_project import ProjectMembers
from models.model_task import Task
from sqlalchemy import BOOLEAN, INTEGER, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    first_name: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(250))
    username: Mapped[str] = mapped_column(VARCHAR(250), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(TEXT)
    email: Mapped[str] = mapped_column(VARCHAR(250), index=True, unique=True)
    role: Mapped[UserRole] = mapped_column(UserRole, default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    project_members: Mapped[list["ProjectMembers"]] = relationship(
        back_populates="user"
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        foreign_keys="Task.creator_id", back_populates="creator"
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(
        secondary="task_assignee", back_populates="assignees"
    )
