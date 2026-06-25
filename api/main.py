"""FastAPI application."""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config.settings import get_settings
from database.connection import get_db
from authentication.security import LoginRequest, decode_token
from authentication.auth_service import AuthService
from services.attendance_service import AttendanceService
from services.notification_service import NotificationService

settings = get_settings()
app = FastAPI(title="WORKPULSE AI API", version="1.0.0", docs_url="/docs")
security = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token_data = decode_token(credentials.credentials)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = AuthService(db).get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/health")
def health():
    return {"status": "healthy", "app": settings.app_name}


@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    auth = AuthService(db)
    result = auth.authenticate(request.email, request.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result


@app.post("/api/auth/logout")
def logout(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return {"success": True}


@app.get("/api/users/me")
def get_me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role_name,
    }


@app.get("/api/notifications")
def get_notifications(user=Depends(get_current_user), db: Session = Depends(get_db)):
    svc = NotificationService(db)
    notifs = svc.get_user_notifications(user.id)
    return [{"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read} for n in notifs]


@app.get("/api/attendance/today")
def today_attendance(user=Depends(get_current_user), db: Session = Depends(get_db)):
    att = AttendanceService(db).get_today(user.id)
    if not att:
        return {"status": "not_marked"}
    return {
        "date": att.date.isoformat(),
        "login_time": str(att.login_time),
        "status": att.status.value if hasattr(att.status, "value") else str(att.status),
        "working_hours": att.working_hours,
    }
