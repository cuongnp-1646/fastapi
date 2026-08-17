from sqlalchemy.orm import Session, joinedload

from crud.security import hash_password, verify_password
from models.project import Project
from models.user import User
from schemas.user import UserCreate, UserUpdate


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


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    db_user = db.get(User, user_id)
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        db_user.hashed_password = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user
