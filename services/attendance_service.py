"""Attendance service."""

from datetime import date, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database.models import Attendance, AttendanceStatus, User, Role, RoleName


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_today(self, user_id: int) -> Optional[Attendance]:
        return (
            self.db.query(Attendance)
            .filter(Attendance.user_id == user_id, Attendance.date == date.today())
            .first()
        )

    def get_user_attendance(self, user_id: int, start: date, end: date) -> List[Attendance]:
        return (
            self.db.query(Attendance)
            .filter(Attendance.user_id == user_id, Attendance.date >= start, Attendance.date <= end)
            .order_by(Attendance.date.desc())
            .all()
        )

    def get_team_attendance(self, team_id: int, target_date: date = None) -> List[Attendance]:
        target_date = target_date or date.today()
        return (
            self.db.query(Attendance)
            .join(User)
            .filter(User.team_id == team_id, Attendance.date == target_date)
            .options(joinedload(Attendance.user))
            .all()
        )

    def get_weekly_hours(self, user_id: int) -> float:
        start = date.today() - timedelta(days=date.today().weekday())
        result = (
            self.db.query(func.sum(Attendance.working_hours))
            .filter(Attendance.user_id == user_id, Attendance.date >= start)
            .scalar()
        )
        return float(result or 0)

    def get_monthly_hours(self, user_id: int) -> float:
        start = date.today().replace(day=1)
        result = (
            self.db.query(func.sum(Attendance.working_hours))
            .filter(Attendance.user_id == user_id, Attendance.date >= start)
            .scalar()
        )
        return float(result or 0)

    def get_attendance_stats(self, user_id: int = None, team_id: int = None) -> Dict[str, Any]:
        q = self.db.query(Attendance)
        if user_id:
            q = q.filter(Attendance.user_id == user_id)
        elif team_id:
            q = q.join(User).filter(User.team_id == team_id)

        month_start = date.today().replace(day=1)
        q = q.filter(Attendance.date >= month_start)
        records = q.all()

        total = len(records)
        if total == 0:
            return {"present": 0, "late": 0, "absent": 0, "wfh": 0, "percentage": 0}

        present = sum(1 for r in records if r.status in (AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.WORK_FROM_HOME))
        return {
            "present": present,
            "late": sum(1 for r in records if r.status == AttendanceStatus.LATE),
            "absent": sum(1 for r in records if r.status == AttendanceStatus.ABSENT),
            "wfh": sum(1 for r in records if r.status == AttendanceStatus.WORK_FROM_HOME),
            "percentage": round(present / total * 100, 1),
            "total_hours": sum(r.working_hours for r in records),
            "overtime_hours": sum(r.overtime_hours for r in records),
        }

    def approve_attendance(self, attendance_id: int, approver_id: int) -> bool:
        att = self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if att:
            att.approved = True
            att.approved_by = approver_id
            return True
        return False

    def mark_status(self, user_id: int, status: AttendanceStatus, target_date: date = None):
        target_date = target_date or date.today()
        att = (
            self.db.query(Attendance)
            .filter(Attendance.user_id == user_id, Attendance.date == target_date)
            .first()
        )
        if att:
            att.status = status
        else:
            self.db.add(Attendance(user_id=user_id, date=target_date, status=status))
        self.db.commit()

    def get_attendance_report_data(self, start: date, end: date, department_id: int = None) -> List[Dict]:
        q = (
            self.db.query(Attendance, User)
            .join(User)
            .filter(Attendance.date >= start, Attendance.date <= end)
        )
        if department_id:
            q = q.filter(User.department_id == department_id)

        rows = []
        for att, user in q.all():
            rows.append({
                "Employee ID": user.employee_id,
                "Name": user.full_name,
                "Date": att.date.isoformat(),
                "Login": str(att.login_time) if att.login_time else "",
                "Logout": str(att.logout_time) if att.logout_time else "",
                "Status": att.status.value if hasattr(att.status, 'value') else str(att.status),
                "Working Hours": att.working_hours,
                "Overtime": att.overtime_hours,
                "Approved": att.approved,
            })
        return rows
