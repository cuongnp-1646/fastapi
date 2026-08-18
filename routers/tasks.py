from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db
from dependencies import get_current_active_user
from models.task import TaskPriority, TaskStatus
from models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    if crud.get_project(db, task.project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if task.assignee_id is not None and crud.get_user(db, task.assignee_id) is None:
        raise HTTPException(status_code=404, detail="Assignee not found")
    return crud.create_task(db, task)


@router.get("/", response_model=list[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_tasks(db, skip=skip, limit=limit, status=status, priority=priority)


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.post("/{task_id}/bookmark", response_model=schemas.Bookmark, status_code=201)
def bookmark_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if crud.get_task(db, task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if crud.get_bookmark(db, current_user.id, task_id) is not None:
        raise HTTPException(status_code=400, detail="Task already bookmarked")
    try:
        return crud.create_bookmark(db, current_user.id, task_id)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Task already bookmarked")
