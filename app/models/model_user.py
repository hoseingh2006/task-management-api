from sqlalchemy import (
    INTEGER,
    VARCHAR,
    TEXT,
)
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base
from models.model_project import Project, ProjectMembers
from models.model_task import Task


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    first_name: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(250))
    username: Mapped[str] = mapped_column(VARCHAR(250), index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(TEXT)
    email: Mapped[str] = mapped_column(VARCHAR(250), index=True, unique=True)
    role: Mapped[str] = mapped_column(VARCHAR(50), default="user")
    project_members: Mapped[list["ProjectMembers"]] = relationship(
        back_populates="user"
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        foreign_keys="Task.creator_id", back_populates="creator"
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(
        foreign_keys="Task.assignee_id", back_populates="assignee"
    )
