"""Audit logging service."""

from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from database.models import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        user_id: Optional[int],
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(entry)

    def get_logs(self, limit: int = 100, user_id: Optional[int] = None):
        q = self.db.query(AuditLog).order_by(AuditLog.created_at.desc())
        if user_id:
            q = q.filter(AuditLog.user_id == user_id)
        return q.limit(limit).all()
