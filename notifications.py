from logging_config import logger


def send_comment_notification_email(
    to_email: str, task_title: str, commenter_username: str, content: str
) -> None:
    logger.info(
        "[email] To: %s | New comment on '%s' by %s: %s",
        to_email,
        task_title,
        commenter_username,
        content,
    )
