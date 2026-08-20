def send_comment_notification_email(
    to_email: str, task_title: str, commenter_username: str, content: str
) -> None:
    print(
        f"[email] To: {to_email} | New comment on '{task_title}' "
        f"by {commenter_username}: {content}"
    )
