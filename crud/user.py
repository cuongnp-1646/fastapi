from sqlalchemy.orm import Session, joinedload

from crud.security import hash_password
from models.project import Project
from models.user import User
from schemas.user import UserCreate


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_profile(db: Session, username: str) -> User | None:
    return (
        db.query(User)
        .options(
            joinedload(User.projects).joinedload(Project.tasks),
            joinedload(User.tasks),
        )
        .filter(User.username == username)
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return list(db.query(User).offset(skip).limit(limit).all())


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
