"""Department and team management."""

from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from database.models import Department, Team


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Department]:
        return self.db.query(Department).filter(Department.is_active == True).all()

    def create(self, name: str, description: str = None) -> Department:
        dept = Department(name=name, description=description)
        self.db.add(dept)
        self.db.commit()
        return dept

    def to_dataframe_rows(self) -> List[Dict]:
        return [{"ID": d.id, "Name": d.name, "Description": d.description or ""} for d in self.get_all()]


class TeamService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Team]:
        return self.db.query(Team).filter(Team.is_active == True).all()

    def create(self, name: str, department_id: int, manager_id: int = None) -> Team:
        team = Team(name=name, department_id=department_id, manager_id=manager_id)
        self.db.add(team)
        self.db.commit()
        return team

    def to_dataframe_rows(self) -> List[Dict]:
        return [
            {"ID": t.id, "Name": t.name, "Department ID": t.department_id, "Manager ID": t.manager_id or ""}
            for t in self.get_all()
        ]
