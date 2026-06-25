"""Calendar service."""

from datetime import datetime, date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from database.models import CalendarEvent, Task, Project


class CalendarService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_events(self, user_id: int, start: date = None, end: date = None) -> List[CalendarEvent]:
        q = self.db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
        if start:
            q = q.filter(CalendarEvent.start_datetime >= datetime.combine(start, datetime.min.time()))
        if end:
            q = q.filter(CalendarEvent.start_datetime <= datetime.combine(end, datetime.max.time()))
        return q.order_by(CalendarEvent.start_datetime).all()

    def create(self, data: dict) -> CalendarEvent:
        event = CalendarEvent(**data)
        self.db.add(event)
        self.db.commit()
        return event

    def get_month_events(self, user_id: int, year: int, month: int) -> List[dict]:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        events = self.get_user_events(user_id, start, end)
        task_deadlines = (
            self.db.query(Task)
            .filter(Task.assignee_id == user_id, Task.due_date >= start, Task.due_date <= end)
            .all()
        )

        result = []
        for e in events:
            result.append({
                "title": e.title,
                "start": e.start_datetime.isoformat(),
                "end": e.end_datetime.isoformat() if e.end_datetime else e.start_datetime.isoformat(),
                "type": e.event_type,
                "color": e.color or "#6366F1",
            })
        for t in task_deadlines:
            result.append({
                "title": f"Due: {t.title}",
                "start": t.due_date.isoformat(),
                "type": "deadline",
                "color": "#EF4444",
            })
        return result
