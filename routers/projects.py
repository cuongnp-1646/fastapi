from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if crud.get_user(db, project.owner_id) is None:
        raise HTTPException(status_code=404, detail="Owner not found")
    return crud.create_project(db, project)


@router.get("/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_projects(db, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.get("/{project_id}/tasks", response_model=list[schemas.Task])
def read_project_tasks(
    project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    if crud.get_project(db, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_tasks_by_project(db, project_id, skip=skip, limit=limit)


@router.post("/{project_id}/tasks", response_model=schemas.Task)
def create_project_task(
    project_id: int, task: schemas.TaskCreateForProject, db: Session = Depends(get_db)
):
    if crud.get_project(db, project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if task.assignee_id is not None and crud.get_user(db, task.assignee_id) is None:
        raise HTTPException(status_code=404, detail="Assignee not found")
    return crud.create_task_for_project(db, project_id, task)
