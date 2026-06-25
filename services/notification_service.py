"""Notification service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from database.models import Notification, NotificationType


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM,
        link: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Notification:
        n = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            metadata_json=metadata,
        )
        self.db.add(n)
        return n

    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        q = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            q = q.filter(Notification.is_read == False)
        return q.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread_count(self, user_id: int) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read == False)
            .count()
        )

    def mark_read(self, notification_id: int, user_id: int) -> bool:
        n = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user_id)
            .first()
        )
        if n:
            n.is_read = True
            return True
        return False

    def mark_all_read(self, user_id: int):
        self.db.query(Notification).filter(
            Notification.user_id == user_id, Notification.is_read == False
        ).update({"is_read": True})

    def create_late_login_notification(self, user_id: int):
        self.create(
            user_id,
            "Late Login Detected",
            "You logged in after the scheduled start time today.",
            NotificationType.LATE_LOGIN,
        )

    def create_task_assignment(self, user_id: int, task_title: str):
        self.create(
            user_id,
            "New Task Assigned",
            f"You have been assigned: {task_title}",
            NotificationType.TASK_ASSIGNMENT,
        )

    def create_deadline_notification(self, user_id: int, project_name: str, days_left: int):
        self.create(
            user_id,
            "Deadline Approaching",
            f"{project_name} deadline is in {days_left} days.",
            NotificationType.DEADLINE_APPROACHING,
        )

    def create_workload_alert(self, user_id: int, hours: float):
        self.create(
            user_id,
            "Workload Overload",
            f"You have logged {hours:.1f} hours this week. Consider workload balance.",
            NotificationType.WORKLOAD_OVERLOAD,
        )
