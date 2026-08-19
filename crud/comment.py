from sqlalchemy.orm import Session

from models.comment import Comment


def get_comment(db: Session, comment_id: int) -> Comment | None:
    return db.get(Comment, comment_id)


def create_comment(db: Session, task_id: int, author_id: int, content: str) -> Comment:
    db_comment = Comment(task_id=task_id, author_id=author_id, content=content)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def update_comment(db: Session, comment: Comment, content: str) -> Comment:
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.commit()
