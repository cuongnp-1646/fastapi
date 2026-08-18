from sqlalchemy.orm import Session, joinedload

from models.task import Task, TaskPriority, TaskStatus
from schemas.task import TaskCreate, TaskCreateForProject


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[Task]:
    query = db.query(Task)
    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return list(query.offset(skip).limit(limit).all())


def get_tasks_by_project(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> list[Task]:
    query = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.tags))
        .filter(Task.project_id == project_id)
    )
    if status is not None:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    return list(query.offset(skip).limit(limit).all())


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def create_task_for_project(
    db: Session, project_id: int, task: TaskCreateForProject
) -> Task:
    db_task = Task(**task.model_dump(), project_id=project_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
