from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.task import TaskPriority, TaskStatus
from schemas.comment import Comment as CommentSchema


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: int
    assignee_id: int | None = None


class TaskCreateForProject(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None


class TaskAssign(BaseModel):
    assignee_id: int


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    project_id: int
    assignee_id: int | None
    created_at: datetime
    comments: list[CommentSchema] = []
