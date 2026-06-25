"""Authentication service."""

from datetime import datetime, date, time
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session, joinedload

from authentication.security import (
    verify_password, hash_password, create_access_token,
    create_refresh_token, generate_session_id, TokenResponse,
)
from database.models import User, Role, Session as UserSession, Attendance, AttendanceStatus
from config.settings import get_settings
from services.audit_service import AuditService
from services.notification_service import NotificationService

settings = get_settings()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)

    def authenticate(
        self,
        email: str,
        password: str,
        ip_address: str = None,
        browser: str = None,
        device: str = None,
        location: str = None,
    ) -> Optional[TokenResponse]:
        user = (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.email == email, User.is_active == True)
            .first()
        )
        if not user or not verify_password(password, user.password_hash):
            return None

        session_id = generate_session_id()
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name.value,
            "session_id": session_id,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        session = UserSession(
            user_id=user.id,
            session_id=session_id,
            ip_address=ip_address,
            browser=browser,
            device=device,
            location=location,
            login_time=datetime.utcnow(),
            is_active=True,
        )
        self.db.add(session)

        user.last_login = datetime.utcnow()
        self._record_attendance_login(user, session_id, ip_address, browser, device, location)
        self.audit.log(user.id, "login", "user", user.id, {"session_id": session_id}, ip_address)
        self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user={**self._user_dict(user), "session_id": session_id},
        )

    def logout(self, user_id: int, session_id: str) -> bool:
        session = (
            self.db.query(UserSession)
            .filter(UserSession.user_id == user_id, UserSession.session_id == session_id, UserSession.is_active == True)
            .first()
        )
        if not session:
            return False

        now = datetime.utcnow()
        session.logout_time = now
        session.is_active = False
        duration = (now - session.login_time).total_seconds() / 60
        session.duration_minutes = round(duration, 2)

        attendance = (
            self.db.query(Attendance)
            .filter(Attendance.user_id == user_id, Attendance.date == date.today())
            .first()
        )
        if attendance:
            attendance.logout_time = now.time()
            attendance.working_hours = round(duration / 60, 2)
            attendance.overtime_hours = max(0, round(attendance.working_hours - settings.standard_work_hours, 2))

        self.audit.log(user_id, "logout", "user", user_id, {"session_id": session_id})
        self.db.commit()
        return True

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.role), joinedload(User.department), joinedload(User.team))
            .filter(User.id == user_id)
            .first()
        )

    def _record_attendance_login(self, user, session_id, ip, browser, device, location):
        today = date.today()
        attendance = (
            self.db.query(Attendance)
            .filter(Attendance.user_id == user.id, Attendance.date == today)
            .first()
        )
        now = datetime.utcnow()
        work_start = datetime.combine(today, time(settings.work_start_hour, settings.work_start_minute))
        late_minutes = (now - work_start).total_seconds() / 60
        status = AttendanceStatus.PRESENT
        if late_minutes > settings.late_threshold_minutes:
            status = AttendanceStatus.LATE
            self.notifications.create_late_login_notification(user.id)

        if not attendance:
            attendance = Attendance(
                user_id=user.id,
                date=today,
                login_time=now.time(),
                status=status,
                browser=browser,
                device=device,
                ip_address=ip,
                location=location,
                session_id=session_id,
            )
            self.db.add(attendance)
        else:
            attendance.login_time = now.time()
            attendance.status = status
            attendance.session_id = session_id

    def _user_dict(self, user: User) -> Dict[str, Any]:
        return {
            "id": user.id,
            "employee_id": user.employee_id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role.name.value,
            "department_id": user.department_id,
            "team_id": user.team_id,
            "job_title": user.job_title,
            "avatar_url": user.avatar_url,
        }

    def create_user(self, data: dict) -> User:
        user = User(
            employee_id=data["employee_id"],
            email=data["email"],
            username=data["username"],
            password_hash=hash_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            role_id=data.get("role_id", 1),
            department_id=data.get("department_id"),
            team_id=data.get("team_id"),
            job_title=data.get("job_title"),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
