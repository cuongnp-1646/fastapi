from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.bookmark import Bookmark


def get_bookmark(db: Session, user_id: int, task_id: int) -> Bookmark | None:
    return (
        db.query(Bookmark)
        .filter(Bookmark.user_id == user_id, Bookmark.task_id == task_id)
        .first()
    )


def create_bookmark(db: Session, user_id: int, task_id: int) -> Bookmark:
    db_bookmark = Bookmark(user_id=user_id, task_id=task_id)
    db.add(db_bookmark)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(db_bookmark)
    return db_bookmark
