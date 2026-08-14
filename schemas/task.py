from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    project_id: int
    assignee_id: int | None = None


class TaskCreateForProject(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    assignee_id: int | None = None


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    project_id: int
    assignee_id: int | None
    created_at: datetime
