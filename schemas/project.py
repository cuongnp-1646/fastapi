from datetime import datetime

from pydantic import BaseModel, ConfigDict

from schemas.task import Task


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    owner_id: int


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime


class ProjectWithTasks(Project):
    tasks: list[Task] = []
