from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    if crud.get_project(db, task.project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if task.assignee_id is not None and crud.get_user(db, task.assignee_id) is None:
        raise HTTPException(status_code=404, detail="Assignee not found")
    return crud.create_task(db, task)


@router.get("/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tasks(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
