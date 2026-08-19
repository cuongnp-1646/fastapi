from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

import crud
from database import get_db
from models.comment import Comment
from models.project import Project
from models.task import Task
from models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = crud.decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def verify_admin_role(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    return current_user


def verify_project_manager(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Project:
    project = crud.get_project(db, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    if current_user.id != project.owner_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner or an admin can perform this action",
        )
    return project


def verify_task_manager(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Task:
    task = crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    project = crud.get_project(db, task.project_id)
    if current_user.id != project.owner_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the project owner or an admin can perform this action",
        )
    return task


def verify_comment_owner(
    task_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Comment:
    comment = crud.get_comment(db, comment_id)
    if comment is None or comment.task_id != task_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if current_user.id == comment.author_id or current_user.role == UserRole.ADMIN:
        return comment
    task = crud.get_task(db, task_id)
    if task is not None:
        project = crud.get_project(db, task.project_id)
        if current_user.id == project.owner_id:
            return comment
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only the comment author, the project owner, or an admin can perform this action",
    )
