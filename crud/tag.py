from sqlalchemy.orm import Session

from models.tag import Tag


def get_tags(db: Session, skip: int = 0, limit: int = 100) -> list[Tag]:
    return list(db.query(Tag).offset(skip).limit(limit).all())
