"""Project management service."""

from datetime import date
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session, joinedload

from database.models import Project, ProjectMember, ProjectStatus, User, Task


class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, active_only: bool = True) -> List[Project]:
        q = self.db.query(Project).options(joinedload(Project.members))
        if active_only:
            q = q.filter(Project.is_active == True)
        return q.order_by(Project.updated_at.desc()).all()

    def get_by_id(self, project_id: int) -> Optional[Project]:
        return (
            self.db.query(Project)
            .options(joinedload(Project.members), joinedload(Project.tasks))
            .filter(Project.id == project_id)
            .first()
        )

    def get_user_projects(self, user_id: int) -> List[Project]:
        return (
            self.db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == user_id, Project.is_active == True)
            .all()
        )

    def create(self, data: dict) -> Project:
        project = Project(**data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id: int, data: dict) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        for k, v in data.items():
            if hasattr(project, k):
                setattr(project, k, v)
        self.db.commit()
        self.db.refresh(project)
        return project

    def add_member(self, project_id: int, user_id: int, allocated_hours: float = 0):
        if not self.db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        ).first():
            self.db.add(ProjectMember(project_id=project_id, user_id=user_id, allocated_hours=allocated_hours))
            self.db.commit()

    def get_project_stats(self) -> Dict[str, Any]:
        projects = self.get_all()
        return {
            "total": len(projects),
            "in_progress": sum(1 for p in projects if p.status == ProjectStatus.IN_PROGRESS),
            "completed": sum(1 for p in projects if p.status == ProjectStatus.COMPLETED),
            "delayed": sum(1 for p in projects if p.status == ProjectStatus.DELAYED),
            "avg_progress": round(sum(p.progress_percentage for p in projects) / max(len(projects), 1), 1),
        }

    def get_gantt_data(self) -> List[Dict]:
        projects = self.get_all()
        data = []
        for p in projects:
            if p.start_date and p.deadline:
                data.append({
                    "Task": p.name,
                    "Start": p.start_date.isoformat(),
                    "Finish": (p.deadline or p.end_date or p.start_date).isoformat(),
                    "Progress": p.progress_percentage,
                    "Status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                })
        return data

    def to_dataframe_rows(self) -> List[Dict]:
        rows = []
        for p in self.get_all(active_only=False):
            rows.append({
                "ID": p.id,
                "Project Name": p.name,
                "Client": p.client_name or "",
                "Budget": p.budget or 0,
                "Start Date": p.start_date.isoformat() if p.start_date else "",
                "End Date": p.end_date.isoformat() if p.end_date else "",
                "Deadline": p.deadline.isoformat() if p.deadline else "",
                "Status": p.status.value if hasattr(p.status, 'value') else str(p.status),
                "Progress %": p.progress_percentage,
                "Allocated Hours": p.allocated_hours,
                "Consumed Hours": p.consumed_hours,
            })
        return rows

    def import_from_rows(self, rows: List[Dict]) -> int:
        count = 0
        status_map = {s.value: s for s in ProjectStatus}
        for row in rows:
            name = row.get("Project Name") or row.get("name")
            if not name:
                continue
            existing = self.db.query(Project).filter(Project.name == name).first()
            status_str = str(row.get("Status", "not_started")).lower().replace(" ", "_")
            status = status_map.get(status_str, ProjectStatus.NOT_STARTED)
            data = {
                "name": name,
                "client_name": row.get("Client") or row.get("client_name"),
                "budget": float(row.get("Budget", 0) or 0),
                "status": status,
                "progress_percentage": float(row.get("Progress %", 0) or 0),
                "allocated_hours": float(row.get("Allocated Hours", 0) or 0),
                "consumed_hours": float(row.get("Consumed Hours", 0) or 0),
            }
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
            else:
                self.db.add(Project(**data))
            count += 1
        self.db.commit()
        return count
