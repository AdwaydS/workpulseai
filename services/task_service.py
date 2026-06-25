"""Task management service."""

from typing import List, Optional, Dict

from sqlalchemy.orm import Session, joinedload

from database.models import Task, TaskStatus, Priority, User
from services.notification_service import NotificationService


class TaskService:
    KANBAN_COLUMNS = [
        TaskStatus.BACKLOG,
        TaskStatus.TODO,
        TaskStatus.IN_PROGRESS,
        TaskStatus.REVIEW,
        TaskStatus.TESTING,
        TaskStatus.COMPLETED,
    ]

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def get_by_project(self, project_id: int) -> List[Task]:
        return (
            self.db.query(Task)
            .filter(Task.project_id == project_id)
            .options(joinedload(Task.assignee))
            .order_by(Task.kanban_order)
            .all()
        )

    def get_user_tasks(self, user_id: int) -> List[Task]:
        return (
            self.db.query(Task)
            .filter(Task.assignee_id == user_id)
            .options(joinedload(Task.project))
            .order_by(Task.due_date)
            .all()
        )

    def get_kanban_board(self, project_id: int) -> Dict[str, List[Task]]:
        tasks = self.get_by_project(project_id)
        board = {col.value: [] for col in self.KANBAN_COLUMNS}
        for task in tasks:
            key = task.status.value if hasattr(task.status, 'value') else str(task.status)
            if key in board:
                board[key].append(task)
        return board

    def create(self, data: dict) -> Task:
        task = Task(**data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        if task.assignee_id:
            self.notifications.create_task_assignment(task.assignee_id, task.title)
        return task

    def update_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            if status == TaskStatus.COMPLETED:
                task.completion_percentage = 100
            self.db.commit()
            self.db.refresh(task)
        return task

    def update_progress(self, task_id: int, percentage: float) -> Optional[Task]:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.completion_percentage = min(100, max(0, percentage))
            if task.completion_percentage >= 100:
                task.status = TaskStatus.COMPLETED
            self.db.commit()
        return task

    def assign(self, task_id: int, user_id: int) -> Optional[Task]:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.assignee_id = user_id
            self.notifications.create_task_assignment(user_id, task.title)
            self.db.commit()
        return task

    def to_dataframe_rows(self, project_id: int = None) -> List[Dict]:
        q = self.db.query(Task).options(joinedload(Task.assignee), joinedload(Task.project))
        if project_id:
            q = q.filter(Task.project_id == project_id)
        rows = []
        for t in q.all():
            rows.append({
                "ID": t.id,
                "Project": t.project.name if t.project else "",
                "Title": t.title,
                "Assignee": t.assignee.full_name if t.assignee else "",
                "Status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                "Priority": t.priority.value if hasattr(t.priority, 'value') else str(t.priority),
                "Due Date": t.due_date.isoformat() if t.due_date else "",
                "Est. Hours": t.estimated_hours,
                "Actual Hours": t.actual_hours,
                "Completion %": t.completion_percentage,
            })
        return rows
