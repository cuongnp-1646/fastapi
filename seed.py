from sqlalchemy.orm import Session

from crud.security import hash_password
from database import SessionLocal
from models.comment import Comment
from models.project import Project
from models.tag import Tag
from models.task import Task, TaskStatus
from models.user import User, UserRole


def get_or_create_user(
    db: Session,
    username: str,
    email: str,
    full_name: str,
    role: UserRole = UserRole.MEMBER,
) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user is not None:
        return user
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("password123"),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_project(
    db: Session, name: str, description: str, owner: User
) -> Project:
    project = db.query(Project).filter(Project.name == name).first()
    if project is not None:
        return project
    project = Project(name=name, description=description, owner_id=owner.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_or_create_task(
    db: Session,
    title: str,
    project: Project,
    assignee: User | None = None,
    status: TaskStatus = TaskStatus.TODO,
    tags: list[Tag] | None = None,
) -> Task:
    task = (
        db.query(Task)
        .filter(Task.title == title, Task.project_id == project.id)
        .first()
    )
    if task is not None:
        return task
    task = Task(
        title=title,
        project_id=project.id,
        assignee_id=assignee.id if assignee else None,
        status=status,
    )
    if tags:
        task.tags = tags
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = db.query(Tag).filter(Tag.name == name).first()
    if tag is not None:
        return tag
    tag = Tag(name=name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def get_or_create_comment(
    db: Session, content: str, task: Task, author: User
) -> Comment:
    comment = (
        db.query(Comment)
        .filter(Comment.content == content, Comment.task_id == task.id)
        .first()
    )
    if comment is not None:
        return comment
    comment = Comment(content=content, task_id=task.id, author_id=author.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def seed() -> None:
    db = SessionLocal()
    try:
        alice = get_or_create_user(db, "alice", "alice@example.com", "Alice Nguyen")
        bob = get_or_create_user(db, "bob", "bob@example.com", "Bob Tran")
        carol = get_or_create_user(db, "carol", "carol@example.com", "Carol Le")
        admin = get_or_create_user(
            db, "admin", "admin@example.com", "Admin User", role=UserRole.ADMIN
        )

        bug_tag = get_or_create_tag(db, "bug")
        feature_tag = get_or_create_tag(db, "feature")
        urgent_tag = get_or_create_tag(db, "urgent")

        website = get_or_create_project(
            db, "Website Redesign", "Revamp the marketing site", alice
        )
        mobile = get_or_create_project(
            db, "Mobile App", "Build the companion mobile app", bob
        )

        design_task = get_or_create_task(
            db,
            "Design homepage",
            website,
            assignee=alice,
            status=TaskStatus.IN_PROGRESS,
            tags=[feature_tag],
        )
        fix_task = get_or_create_task(
            db,
            "Fix login bug",
            website,
            assignee=bob,
            status=TaskStatus.TODO,
            tags=[bug_tag, urgent_tag],
        )
        api_task = get_or_create_task(
            db,
            "Build REST API",
            mobile,
            assignee=carol,
            status=TaskStatus.DONE,
            tags=[feature_tag],
        )

        get_or_create_comment(
            db, "Looks great, ship it!", design_task, author=bob
        )
        get_or_create_comment(
            db, "Reproduced on Safari too.", fix_task, author=carol
        )
        get_or_create_comment(
            db, "API docs are up on the wiki.", api_task, author=alice
        )

        print("Seed data ready:")
        print(
            f"  Users: {alice.username}, {bob.username}, {carol.username}, "
            f"{admin.username} (role=admin, password=password123)"
        )
        print(f"  Projects: {website.name}, {mobile.name}")
        print(f"  Tasks: {design_task.title}, {fix_task.title}, {api_task.title}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
