"""Analytics and dashboard data service."""

from datetime import date, timedelta
from typing import Dict, List, Any

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database.models import (
    User, Attendance, AttendanceStatus, WorkLog, Project, Task,
    Department, Role, RoleName, ProjectStatus,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def productivity_trend(self, user_id: int = None, days: int = 30) -> pd.DataFrame:
        start = date.today() - timedelta(days=days)
        q = (
            self.db.query(WorkLog.log_date, func.sum(WorkLog.hours_spent))
            .filter(WorkLog.log_date >= start)
        )
        if user_id:
            q = q.filter(WorkLog.user_id == user_id)
        q = q.group_by(WorkLog.log_date).order_by(WorkLog.log_date)
        rows = q.all()
        return pd.DataFrame({"Date": [r[0] for r in rows], "Hours": [float(r[1] or 0) for r in rows]})

    def attendance_trend(self, days: int = 30) -> pd.DataFrame:
        start = date.today() - timedelta(days=days)
        rows = (
            self.db.query(Attendance.date, func.count(Attendance.id))
            .filter(Attendance.date >= start, Attendance.status != AttendanceStatus.ABSENT)
            .group_by(Attendance.date)
            .order_by(Attendance.date)
            .all()
        )
        return pd.DataFrame({"Date": [r[0] for r in rows], "Present": [r[1] for r in rows]})

    def hours_distribution(self, user_id: int = None) -> pd.DataFrame:
        q = self.db.query(WorkLog.project_name, func.sum(WorkLog.hours_spent))
        if user_id:
            q = q.filter(WorkLog.user_id == user_id)
        rows = q.group_by(WorkLog.project_name).all()
        return pd.DataFrame({
            "Project": [r[0] or "Unassigned" for r in rows],
            "Hours": [float(r[1] or 0) for r in rows],
        })

    def team_performance_radar(self, team_id: int) -> Dict[str, float]:
        members = self.db.query(User).filter(User.team_id == team_id).all()
        if not members:
            return {}
        member_ids = [m.id for m in members]
        total_hours = self.db.query(func.sum(WorkLog.hours_spent)).filter(WorkLog.user_id.in_(member_ids)).scalar() or 0
        completed_tasks = self.db.query(Task).filter(Task.assignee_id.in_(member_ids), Task.completion_percentage >= 100).count()
        total_tasks = max(self.db.query(Task).filter(Task.assignee_id.in_(member_ids)).count(), 1)
        attendance_rate = self._team_attendance_rate(member_ids)
        return {
            "Productivity": min(100, total_hours / max(len(members), 1) * 2),
            "Task Completion": completed_tasks / total_tasks * 100,
            "Attendance": attendance_rate,
            "Collaboration": min(100, len(members) * 15),
            "Quality": min(100, 70 + completed_tasks * 2),
            "Efficiency": min(100, attendance_rate * 0.8 + completed_tasks / total_tasks * 20),
        }

    def _team_attendance_rate(self, user_ids: List[int]) -> float:
        month_start = date.today().replace(day=1)
        total = self.db.query(Attendance).filter(
            Attendance.user_id.in_(user_ids), Attendance.date >= month_start
        ).count()
        present = self.db.query(Attendance).filter(
            Attendance.user_id.in_(user_ids),
            Attendance.date >= month_start,
            Attendance.status != AttendanceStatus.ABSENT,
        ).count()
        return round(present / max(total, 1) * 100, 1)

    def employee_ranking(self, limit: int = 10) -> pd.DataFrame:
        month_start = date.today().replace(day=1)
        rows = (
            self.db.query(User.first_name, User.last_name, func.sum(WorkLog.hours_spent))
            .join(WorkLog, WorkLog.user_id == User.id)
            .filter(WorkLog.log_date >= month_start)
            .group_by(User.id, User.first_name, User.last_name)
            .order_by(func.sum(WorkLog.hours_spent).desc())
            .limit(limit)
            .all()
        )
        return pd.DataFrame({
            "Employee": [f"{r[0]} {r[1]}" for r in rows],
            "Hours": [float(r[2] or 0) for r in rows],
            "Rank": list(range(1, len(rows) + 1)),
        })

    def resource_utilization(self) -> pd.DataFrame:
        rows = []
        for dept in self.db.query(Department).all():
            users = self.db.query(User).filter(User.department_id == dept.id).count()
            hours = (
                self.db.query(func.sum(WorkLog.hours_spent))
                .join(User)
                .filter(User.department_id == dept.id)
                .scalar() or 0
            )
            rows.append({"Department": dept.name, "Employees": users, "Hours": float(hours), "Utilization": min(100, hours / max(users * 160, 1) * 100)})
        return pd.DataFrame(rows)

    def department_comparison(self) -> pd.DataFrame:
        return self.resource_utilization()

    def workload_heatmap(self, team_id: int = None) -> pd.DataFrame:
        start = date.today() - timedelta(days=28)
        q = self.db.query(User.first_name, WorkLog.log_date, WorkLog.hours_spent).join(WorkLog)
        if team_id:
            q = q.filter(User.team_id == team_id)
        q = q.filter(WorkLog.log_date >= start)
        rows = q.all()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["Employee", "Date", "Hours"])
        df["Day"] = pd.to_datetime(df["Date"]).dt.day_name()
        return df.pivot_table(index="Employee", columns="Day", values="Hours", aggfunc="sum", fill_value=0)

    def calculate_productivity_score(self, user_id: int) -> float:
        week_start = date.today() - timedelta(days=7)
        hours = self.db.query(func.sum(WorkLog.hours_spent)).filter(
            WorkLog.user_id == user_id, WorkLog.log_date >= week_start
        ).scalar() or 0
        tasks_done = self.db.query(Task).filter(
            Task.assignee_id == user_id, Task.completion_percentage >= 100
        ).count()
        att = self.db.query(Attendance).filter(
            Attendance.user_id == user_id, Attendance.date >= week_start,
            Attendance.status != AttendanceStatus.ABSENT
        ).count()
        score = min(100, (hours / 40 * 40) + (tasks_done * 5) + (att * 3))
        return round(score, 1)

    def org_health_score(self) -> float:
        total_users = self.db.query(User).filter(User.is_active == True).count()
        if total_users == 0:
            return 0
        month_start = date.today().replace(day=1)
        attendance = self.db.query(Attendance).filter(
            Attendance.date >= month_start, Attendance.status != AttendanceStatus.ABSENT
        ).count()
        total_att = max(self.db.query(Attendance).filter(Attendance.date >= month_start).count(), 1)
        projects_on_track = self.db.query(Project).filter(
            Project.status.in_([ProjectStatus.IN_PROGRESS, ProjectStatus.COMPLETED])
        ).count()
        total_projects = max(self.db.query(Project).count(), 1)
        return round((attendance / total_att * 50) + (projects_on_track / total_projects * 50), 1)
