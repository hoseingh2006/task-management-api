from enum import Enum


class ProjectRole(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


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


class NotificationType(str, Enum):
    MENTION = "mention"

    TASK_ASSIGNED = "task_assigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_UPDATED = "task_updated"

    COMMENT_CREATED = "comment_created"

    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_CHANGED = "member_role_changed"

    PROJECT_STATUS_CHANGED = "project_status_changed"

    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_REMOVED = "dependency_removed"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ActivityAction(str, Enum):
    # Project
    PROJECT_CREATED = "project_created"
    PROJECT_UPDATED = "project_updated"
    PROJECT_DELETED = "project_deleted"
    PROJECT_STATUS_CHANGED = "project_status_changed"

    # Task
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_STATUS_CHANGED = "task_status_changed"

    # Subtask
    SUBTASK_CREATED = "subtask_created"
    SUBTASK_UPDATED = "subtask_updated"
    SUBTASK_DELETED = "subtask_deleted"
    SUBTASK_STATUS_CHANGED = "subtask_status_changed"

    # Tag
    TAG_CREATED = "tag_created"
    TAG_UPDATED = "tag_updated"
    TAG_DELETED = "tag_deleted"

    # Comment
    COMMENT_CREATED = "comment_created"
    COMMENT_UPDATED = "comment_updated"
    COMMENT_DELETED = "comment_deleted"

    # User
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"

    # Project Member
    MEMBER_ADDED = "member_added"
    MEMBER_REMOVED = "member_removed"
    MEMBER_ROLE_CHANGED = "member_role_changed"

    # Task relations
    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"

    # Tag relations
    TAG_ADDED_TO_TASK = "tag_added_to_task"
    TAG_REMOVED_FROM_TASK = "tag_removed_from_task"

    # Dependency
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_UPDATED = "dependency_updated"
    DEPENDENCY_REMOVED = "dependency_removed"
