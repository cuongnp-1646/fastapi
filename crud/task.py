from sqlalchemy.orm import Session, joinedload

from models.task import Task
from schemas.task import TaskCreate, TaskCreateForProject


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return list(db.query(Task).offset(skip).limit(limit).all())


def get_tasks_by_project(
    db: Session, project_id: int, skip: int = 0, limit: int = 100
) -> list[Task]:
    return list(
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.tags))
        .filter(Task.project_id == project_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


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
