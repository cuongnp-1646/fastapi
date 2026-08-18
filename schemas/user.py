from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.user import UserRole
from schemas.project import ProjectWithTasks
from schemas.task import Task


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    role: UserRole
    created_at: datetime


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    password: str | None = None


class UserProfile(User):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    projects: list[ProjectWithTasks] = []
    assigned_tasks: list[Task] = Field(default_factory=list, validation_alias="tasks")
