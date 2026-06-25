"""Work log service."""

from datetime import date, timedelta
from typing import List, Optional, Dict

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import WorkLog, Priority


class WorkLogService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> WorkLog:
        log = WorkLog(**data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_user_logs(self, user_id: int, start: date = None, end: date = None) -> List[WorkLog]:
        q = self.db.query(WorkLog).filter(WorkLog.user_id == user_id)
        if start:
            q = q.filter(WorkLog.log_date >= start)
        if end:
            q = q.filter(WorkLog.log_date <= end)
        return q.order_by(WorkLog.log_date.desc()).all()

    def get_today_hours(self, user_id: int) -> float:
        result = (
            self.db.query(func.sum(WorkLog.hours_spent))
            .filter(WorkLog.user_id == user_id, WorkLog.log_date == date.today())
            .scalar()
        )
        return float(result or 0)

    def get_weekly_hours(self, user_id: int) -> float:
        start = date.today() - timedelta(days=date.today().weekday())
        result = (
            self.db.query(func.sum(WorkLog.hours_spent))
            .filter(WorkLog.user_id == user_id, WorkLog.log_date >= start)
            .scalar()
        )
        return float(result or 0)

    def get_distribution(self, user_id: int) -> Dict[str, float]:
        start = date.today() - timedelta(days=30)
        logs = self.get_user_logs(user_id, start=start)
        dist = {}
        for log in logs:
            key = log.project_name or "Unassigned"
            dist[key] = dist.get(key, 0) + log.hours_spent
        return dist

    def to_dataframe_rows(self, user_id: int = None) -> List[Dict]:
        q = self.db.query(WorkLog)
        if user_id:
            q = q.filter(WorkLog.user_id == user_id)
        rows = []
        for log in q.order_by(WorkLog.log_date.desc()).all():
            rows.append({
                "Date": log.log_date.isoformat(),
                "Project": log.project_name or "",
                "Task": log.task_name or "",
                "Description": log.description or "",
                "Priority": log.priority.value if hasattr(log.priority, 'value') else str(log.priority),
                "Hours": log.hours_spent,
                "Completion %": log.completion_percentage,
                "Notes": log.notes or "",
            })
        return rows

    def import_from_rows(self, user_id: int, rows: List[Dict]) -> int:
        priority_map = {p.value: p for p in Priority}
        count = 0
        for row in rows:
            log_date_str = row.get("Date") or row.get("date")
            if not log_date_str:
                continue
            try:
                log_date = date.fromisoformat(str(log_date_str)[:10])
            except ValueError:
                continue
            priority_str = str(row.get("Priority", "medium")).lower()
            self.create({
                "user_id": user_id,
                "project_name": row.get("Project") or row.get("project_name"),
                "task_name": row.get("Task") or row.get("task_name"),
                "description": row.get("Description") or row.get("description"),
                "priority": priority_map.get(priority_str, Priority.MEDIUM),
                "hours_spent": float(row.get("Hours", 0) or 0),
                "completion_percentage": float(row.get("Completion %", 0) or 0),
                "notes": row.get("Notes") or row.get("notes"),
                "log_date": log_date,
            })
            count += 1
        return count
