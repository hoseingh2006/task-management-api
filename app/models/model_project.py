from datetime import datetime
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


class ProjectRole(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(250), index=True)
    description: Mapped[str] = mapped_column(TEXT, nullable=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    members: Mapped[list["ProjectMembers"]] = relationship(back_populates="project")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")


class ProjectMembers(Base):
    __tablename__ = "project_members"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    role: Mapped[ProjectRole] = mapped_column(
        SQLEnum(ProjectRole),
        default=ProjectRole.MEMBER,
    )
    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="project_members")
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)
