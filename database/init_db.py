"""Database initialization and seeding."""

import argparse
import random
import uuid
from datetime import datetime, date, time, timedelta

from sqlalchemy.orm import Session

from database.connection import Base, engine, SessionLocal
from database.models import (
    Role, RoleName, Department, Team, User, Project, ProjectMember,
    Task, TaskStatus, ProjectStatus, Priority, Attendance, AttendanceStatus,
    WorkLog, Notification, NotificationType, CalendarEvent, SystemSetting,
    Session as UserSession,
)
from authentication.security import hash_password


def create_tables():
    Base.metadata.create_all(bind=engine)


def seed_roles(db: Session):
    roles = [
        (RoleName.EMPLOYEE, "Standard employee access", {"dashboard": True, "work_logs": True}),
        (RoleName.MANAGER, "Team management access", {"dashboard": True, "team": True, "reports": True}),
        (RoleName.ADMIN, "Full system access", {"all": True}),
    ]
    for name, desc, perms in roles:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name, description=desc, permissions=perms))
    db.commit()


def seed_departments_and_teams(db: Session):
    depts = [
        ("Engineering", "Software development and infrastructure"),
        ("Product", "Product management and design"),
        ("Operations", "Business operations and HR"),
        ("Sales", "Sales and customer success"),
    ]
    dept_objs = []
    for name, desc in depts:
        d = db.query(Department).filter(Department.name == name).first()
        if not d:
            d = Department(name=name, description=desc)
            db.add(d)
            db.flush()
        dept_objs.append(d)
    db.commit()

    teams_data = [
        ("Platform Team", dept_objs[0].id),
        ("Frontend Team", dept_objs[0].id),
        ("Product Strategy", dept_objs[1].id),
        ("HR Operations", dept_objs[2].id),
    ]
    for name, dept_id in teams_data:
        if not db.query(Team).filter(Team.name == name).first():
            db.add(Team(name=name, department_id=dept_id))
    db.commit()
    return dept_objs


def seed_users(db: Session, departments):
    admin_role = db.query(Role).filter(Role.name == RoleName.ADMIN).first()
    manager_role = db.query(Role).filter(Role.name == RoleName.MANAGER).first()
    employee_role = db.query(Role).filter(Role.name == RoleName.EMPLOYEE).first()
    teams = db.query(Team).all()

    users_data = [
        ("ADM001", "admin@workpulse.ai", "admin", "System", "Administrator", admin_role.id, None, None, "Chief Admin"),
        ("MGR001", "manager@workpulse.ai", "manager", "Sarah", "Chen", manager_role.id, departments[0].id, teams[0].id, "Engineering Manager"),
        ("MGR002", "manager2@workpulse.ai", "manager2", "James", "Wilson", manager_role.id, departments[1].id, teams[2].id, "Product Manager"),
        ("EMP001", "john@workpulse.ai", "john", "John", "Anderson", employee_role.id, departments[0].id, teams[0].id, "Senior Developer"),
        ("EMP002", "emma@workpulse.ai", "emma", "Emma", "Rodriguez", employee_role.id, departments[0].id, teams[1].id, "Frontend Developer"),
        ("EMP003", "mike@workpulse.ai", "mike", "Mike", "Thompson", employee_role.id, departments[0].id, teams[0].id, "Backend Developer"),
        ("EMP004", "lisa@workpulse.ai", "lisa", "Lisa", "Park", employee_role.id, departments[1].id, teams[2].id, "Product Analyst"),
        ("EMP005", "david@workpulse.ai", "david", "David", "Kim", employee_role.id, departments[2].id, teams[3].id, "HR Specialist"),
    ]

    created = []
    for emp_id, email, username, fn, ln, role_id, dept_id, team_id, title in users_data:
        if db.query(User).filter(User.email == email).first():
            continue
        user = User(
            employee_id=emp_id,
            email=email,
            username=username,
            password_hash=hash_password("Workpulse@123"),
            first_name=fn,
            last_name=ln,
            role_id=role_id,
            department_id=dept_id,
            team_id=team_id,
            job_title=title,
            hire_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
            is_active=True,
        )
        db.add(user)
        created.append(user)
    db.commit()

    manager = db.query(User).filter(User.email == "manager@workpulse.ai").first()
    if manager:
        for u in db.query(User).filter(User.role_id == employee_role.id, User.team_id == teams[0].id).all():
            u.manager_id = manager.id
        teams[0].manager_id = manager.id
        db.commit()
    return created


def seed_projects_and_tasks(db: Session):
    manager = db.query(User).filter(User.email == "manager@workpulse.ai").first()
    employees = db.query(User).filter(User.email.like("john%") | User.email.like("emma%") | User.email.like("mike%")).all()
    dept = db.query(Department).filter(Department.name == "Engineering").first()

    projects_data = [
        ("Project Alpha", "Acme Corp", 150000, ProjectStatus.IN_PROGRESS, 45, 120, 85),
        ("Project Beta", "TechStart Inc", 80000, ProjectStatus.PLANNING, 10, 200, 25),
        ("Project Gamma", "Global Systems", 220000, ProjectStatus.REVIEW, 78, 300, 210),
        ("Project Delta", "Innovate LLC", 95000, ProjectStatus.IN_PROGRESS, 35, 160, 72),
        ("Project Epsilon", "DataFlow Co", 180000, ProjectStatus.TESTING, 88, 250, 195),
    ]

    statuses = list(TaskStatus)
    priorities = list(Priority)

    for pname, client, budget, status, progress, alloc, consumed in projects_data:
        if db.query(Project).filter(Project.name == pname).first():
            continue
        project = Project(
            name=pname,
            client_name=client,
            budget=budget,
            start_date=date.today() - timedelta(days=random.randint(30, 90)),
            end_date=date.today() + timedelta(days=random.randint(30, 120)),
            deadline=date.today() + timedelta(days=random.randint(15, 60)),
            manager_id=manager.id if manager else None,
            status=status,
            progress_percentage=progress,
            allocated_hours=alloc,
            consumed_hours=consumed,
            department_id=dept.id if dept else None,
        )
        db.add(project)
        db.flush()

        for emp in employees[:3]:
            db.add(ProjectMember(project_id=project.id, user_id=emp.id, allocated_hours=40))

        task_titles = [
            "Requirements Analysis", "UI Design", "API Development",
            "Database Schema", "Unit Testing", "Integration Testing",
            "Documentation", "Code Review", "Deployment Setup",
        ]
        for i, title in enumerate(task_titles[:6]):
            emp = random.choice(employees) if employees else None
            db.add(Task(
                project_id=project.id,
                title=title,
                description=f"Task for {title} on {pname}",
                assignee_id=emp.id if emp else None,
                created_by=manager.id if manager else None,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                start_date=date.today() - timedelta(days=random.randint(1, 20)),
                due_date=date.today() + timedelta(days=random.randint(5, 30)),
                estimated_hours=random.uniform(4, 16),
                actual_hours=random.uniform(2, 12),
                completion_percentage=random.uniform(0, 100),
                kanban_order=i,
            ))
    db.commit()


def seed_attendance_and_worklogs(db: Session):
    employees = db.query(User).join(Role).filter(Role.name == RoleName.EMPLOYEE).all()
    projects = db.query(Project).all()

    for emp in employees:
        for day_offset in range(30):
            d = date.today() - timedelta(days=day_offset)
            if d.weekday() >= 5:
                continue
            if db.query(Attendance).filter(Attendance.user_id == emp.id, Attendance.date == d).first():
                continue

            is_late = random.random() < 0.15
            login_hour = 9 if not is_late else random.randint(9, 11)
            login_min = random.randint(0, 59) if is_late else random.randint(0, 15)
            logout_hour = random.randint(17, 19)
            working = logout_hour - login_hour + random.uniform(0, 0.9)
            overtime = max(0, working - 8)

            status = AttendanceStatus.LATE if is_late else AttendanceStatus.PRESENT
            if random.random() < 0.05:
                status = AttendanceStatus.WORK_FROM_HOME

            db.add(Attendance(
                user_id=emp.id,
                date=d,
                login_time=time(login_hour, login_min),
                logout_time=time(logout_hour, random.randint(0, 59)),
                status=status,
                browser="Chrome",
                device="Desktop",
                ip_address=f"192.168.1.{random.randint(10, 250)}",
                location="Office HQ",
                session_id=str(uuid.uuid4())[:12],
                working_hours=round(working, 2),
                overtime_hours=round(overtime, 2),
                approved=True,
            ))

        for _ in range(random.randint(15, 25)):
            proj = random.choice(projects) if projects else None
            log_date = date.today() - timedelta(days=random.randint(0, 29))
            hours = round(random.uniform(1, 6), 1)
            db.add(WorkLog(
                user_id=emp.id,
                project_id=proj.id if proj else None,
                project_name=proj.name if proj else "Internal",
                task_name=random.choice(["Development", "Testing", "Meeting", "Documentation"]),
                description="Daily work activity",
                priority=random.choice(list(Priority)),
                start_time=datetime.combine(log_date, time(9, 0)),
                end_time=datetime.combine(log_date, time(9 + int(hours), int((hours % 1) * 60))),
                hours_spent=hours,
                completion_percentage=random.uniform(10, 100),
                notes="Completed as planned",
                log_date=log_date,
            ))
    db.commit()


def seed_notifications(db: Session):
    users = db.query(User).limit(5).all()
    types = list(NotificationType)
    messages = [
        ("Late Login Detected", "You logged in after the scheduled start time."),
        ("Task Assigned", "A new task has been assigned to you."),
        ("Deadline Approaching", "Project Alpha deadline is in 3 days."),
        ("Workload Alert", "Your weekly hours exceed the recommended threshold."),
    ]
    for user in users:
        for title, msg in random.sample(messages, min(3, len(messages))):
            db.add(Notification(
                user_id=user.id,
                title=title,
                message=msg,
                notification_type=random.choice(types),
                is_read=random.choice([True, False]),
            ))
    db.commit()


def seed_calendar(db: Session):
    users = db.query(User).limit(5).all()
    for user in users:
        for i in range(5):
            start = datetime.now() + timedelta(days=random.randint(-10, 20), hours=random.randint(9, 15))
            db.add(CalendarEvent(
                user_id=user.id,
                title=random.choice(["Team Standup", "Sprint Review", "Client Meeting", "Project Milestone"]),
                event_type=random.choice(["meeting", "deadline", "leave", "holiday"]),
                start_datetime=start,
                end_datetime=start + timedelta(hours=1),
                color="#6366F1",
            ))
    db.commit()


def seed_settings(db: Session):
    settings = [
        ("company_name", "WORKPULSE AI", "string", "Organization name"),
        ("work_start_time", "09:00", "string", "Standard work start time"),
        ("timezone", "UTC", "string", "System timezone"),
        ("logo_path", "assets/logo.png", "string", "Company logo path"),
    ]
    for key, val, vtype, desc in settings:
        if not db.query(SystemSetting).filter(SystemSetting.key == key).first():
            db.add(SystemSetting(key=key, value=val, value_type=vtype, description=desc))
    db.commit()


def run_seed():
    db = SessionLocal()
    try:
        create_tables()
        seed_roles(db)
        depts = seed_departments_and_teams(db)
        seed_users(db, depts)
        seed_projects_and_tasks(db)
        seed_attendance_and_worklogs(db)
        seed_notifications(db)
        seed_calendar(db)
        seed_settings(db)
        print("Database initialized and seeded successfully.")
        print("Default credentials: admin@workpulse.ai / Workpulse@123")
        print("Manager: manager@workpulse.ai / Workpulse@123")
        print("Employee: john@workpulse.ai / Workpulse@123")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Seed sample data")
    args = parser.parse_args()
    create_tables()
    if args.seed:
        run_seed()
