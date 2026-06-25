"""User management service."""

from typing import List, Optional, Dict

from sqlalchemy.orm import Session, joinedload

from database.models import User, Role, Department, Team, RoleName
from authentication.security import hash_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, active_only: bool = True) -> List[User]:
        q = self.db.query(User).options(joinedload(User.role), joinedload(User.department), joinedload(User.team))
        if active_only:
            q = q.filter(User.is_active == True)
        return q.order_by(User.first_name).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.role), joinedload(User.department), joinedload(User.team))
            .filter(User.id == user_id)
            .first()
        )

    def get_team_members(self, team_id: int) -> List[User]:
        return (
            self.db.query(User)
            .filter(User.team_id == team_id, User.is_active == True)
            .options(joinedload(User.role))
            .all()
        )

    def get_by_role(self, role: RoleName) -> List[User]:
        return (
            self.db.query(User)
            .join(Role)
            .filter(Role.name == role, User.is_active == True)
            .all()
        )

    def create(self, data: dict) -> User:
        user = User(
            employee_id=data["employee_id"],
            email=data["email"],
            username=data["username"],
            password_hash=hash_password(data.get("password", "Workpulse@123")),
            first_name=data["first_name"],
            last_name=data["last_name"],
            role_id=data["role_id"],
            department_id=data.get("department_id"),
            team_id=data.get("team_id"),
            manager_id=data.get("manager_id"),
            job_title=data.get("job_title"),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: int, data: dict) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        for k, v in data.items():
            if k == "password":
                user.password_hash = hash_password(v)
            elif hasattr(user, k) and k != "password_hash":
                setattr(user, k, v)
        self.db.commit()
        return user

    def deactivate(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False

    def get_org_stats(self) -> Dict:
        total = self.db.query(User).filter(User.is_active == True).count()
        employees = self.get_by_role(RoleName.EMPLOYEE)
        return {
            "total_employees": total,
            "active_employees": total,
            "employees": len(employees),
            "managers": len(self.get_by_role(RoleName.MANAGER)),
            "admins": len(self.get_by_role(RoleName.ADMIN)),
        }

    def to_dataframe_rows(self) -> List[Dict]:
        rows = []
        for u in self.get_all(active_only=False):
            rows.append({
                "Employee ID": u.employee_id,
                "Email": u.email,
                "Username": u.username,
                "First Name": u.first_name,
                "Last Name": u.last_name,
                "Role": u.role.name.value if u.role else "",
                "Department": u.department.name if u.department else "",
                "Team": u.team.name if u.team else "",
                "Job Title": u.job_title or "",
                "Active": u.is_active,
            })
        return rows

    def import_from_rows(self, rows: List[Dict]) -> int:
        roles = {r.name.value: r.id for r in self.db.query(Role).all()}
        depts = {d.name: d.id for d in self.db.query(Department).all()}
        count = 0
        for row in rows:
            email = row.get("Email") or row.get("email")
            if not email or self.db.query(User).filter(User.email == email).first():
                continue
            role_name = str(row.get("Role", "employee")).lower()
            self.create({
                "employee_id": row.get("Employee ID") or f"EMP{count:03d}",
                "email": email,
                "username": row.get("Username") or email.split("@")[0],
                "first_name": row.get("First Name", "New"),
                "last_name": row.get("Last Name", "User"),
                "role_id": roles.get(role_name, roles.get("employee", 1)),
                "department_id": depts.get(row.get("Department")),
                "job_title": row.get("Job Title"),
                "password": row.get("Password", "Workpulse@123"),
            })
            count += 1
        return count
