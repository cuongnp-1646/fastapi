from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db
from dependencies import (
    get_current_active_user,
    verify_comment_owner,
    verify_task_manager,
)
from models.comment import Comment
from models.task import Task, TaskPriority, TaskStatus
from models.user import User
from notifications import send_comment_notification_email

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


@router.post("/{task_id}/assign", response_model=schemas.Task)
def assign_task(
    assignment: schemas.TaskAssign,
    task: Task = Depends(verify_task_manager),
    db: Session = Depends(get_db),
):
    if crud.get_user(db, assignment.assignee_id) is None:
        raise HTTPException(status_code=404, detail="Assignee not found")
    task.assignee_id = assignment.assignee_id
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/comments", response_model=schemas.Comment, status_code=201)
def create_comment(
    task_id: int,
    comment: schemas.CommentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_comment = crud.create_comment(db, task_id, current_user.id, comment.content)
    if task.assignee_id is not None and task.assignee_id != current_user.id:
        assignee = crud.get_user(db, task.assignee_id)
        if assignee is not None:
            background_tasks.add_task(
                send_comment_notification_email,
                assignee.email,
                task.title,
                current_user.username,
                comment.content,
            )
    return db_comment


@router.put("/{task_id}/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_update: schemas.CommentUpdate,
    comment: Comment = Depends(verify_comment_owner),
    db: Session = Depends(get_db),
):
    return crud.update_comment(db, comment, comment_update.content)


@router.delete("/{task_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    comment: Comment = Depends(verify_comment_owner),
    db: Session = Depends(get_db),
):
    crud.delete_comment(db, comment)
