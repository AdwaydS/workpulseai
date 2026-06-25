# WORKPULSE AI

**Intelligent Workload Tracking, Attendance Monitoring & Workforce Analytics Platform**

A production-grade enterprise SaaS workforce management system built with Streamlit, FastAPI, PostgreSQL, and SQLAlchemy. Designed for organizations with 10,000+ employees.

![WORKPULSE AI](assets/logo.png)

---

## Features

| Module | Capabilities |
|--------|-------------|
| **Authentication** | JWT tokens, bcrypt password hashing, RBAC (Employee / Manager / Admin) |
| **Attendance** | Auto login/logout tracking, IP/device/browser capture, status management, approvals |
| **Work Logs** | Project/task time tracking, priority levels, completion tracking |
| **Projects** | Full lifecycle management, budget, hours allocation, progress tracking |
| **Tasks & Kanban** | 6-column drag board (Backlog → Completed) |
| **Dashboards** | Role-specific KPI dashboards with real-time metrics |
| **Analytics** | 10+ interactive charts (Plotly): trends, heatmaps, Gantt, radar, treemap |
| **AI Insights** | Burnout detection, deadline risk, utilization analysis |
| **Reports** | Export to **PDF**, **Excel**, **CSV** |
| **Excel Import/Export** | Bulk import users, projects, work logs with downloadable templates |
| **Notifications** | Real-time alerts with badge counter |
| **Calendar** | Events, deadlines, meetings, leave, milestones |
| **Audit Log** | Full activity tracking for compliance |

---

## Architecture

```
workpulse-ai/
├── app.py                  # Streamlit main application
├── api/main.py             # FastAPI REST API
├── authentication/         # JWT & auth services
├── database/               # SQLAlchemy models & init
├── services/               # Business logic layer
├── analytics/              # Analytics engine
├── ai_engine/              # AI workforce insights
├── reports/                # PDF/Excel report generation
├── dashboard/              # Role-based dashboards
├── views/                  # UI page modules
├── components/             # Reusable UI components
├── styles/                 # Premium CSS theme
├── assets/                 # Logo & static assets
├── migrations/             # Alembic migrations
├── tests/                  # Unit tests
├── docker-compose.yml      # Full stack deployment
└── requirements.txt
```

**Design Patterns:** Clean Architecture, Service Layer, Repository (SQLAlchemy ORM), SOLID principles.

---

## Quick Start (Docker — Recommended)

### Prerequisites
- Docker & Docker Compose
- Git

### Steps

```bash
cd workpulse-ai

# Copy environment config
copy .env.example .env

# Start all services (PostgreSQL + Redis + API + Streamlit)
docker-compose up --build
```

| Service | URL |
|---------|-----|
| **Streamlit App** | http://localhost:8501 |
| **FastAPI Docs** | http://localhost:8000/docs |
| **PostgreSQL** | localhost:5432 |

Database is auto-initialized with sample data on first startup.

---

## Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- PostgreSQL 16+

### Setup

```bash
cd workpulse-ai
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

copy .env.example .env
# Edit DATABASE_URL in .env

# Initialize database with seed data
python -m database.init_db --seed

# Terminal 1: API
uvicorn api.main:app --reload --port 8000

# Terminal 2: Streamlit
streamlit run app.py
```

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@workpulse.ai | Workpulse@123 |
| **Manager** | manager@workpulse.ai | Workpulse@123 |
| **Employee** | john@workpulse.ai | Workpulse@123 |

---

## Logo

Your CAP AI logo is included at `assets/logo.png`. Replace this file to use a custom logo — it appears on the login screen, sidebar, and PDF reports.

---

## Excel Import / Export

Every data table supports:
- **Export** to Excel (.xlsx) or CSV
- **Import** from Excel/CSV with validation
- **Downloadable templates** for Users, Projects, Work Logs

Admin can generate multi-sheet Excel exports with all organizational data from the Reports page.

---

## Database Schema

| Table | Purpose |
|-------|---------|
| users | Employee accounts |
| roles | RBAC roles |
| departments | Organization departments |
| teams | Team groupings |
| attendance | Daily attendance records |
| sessions | Login/logout sessions |
| projects | Project management |
| project_members | Project team assignments |
| tasks | Task tracking |
| work_logs | Work activity logs |
| notifications | Alert system |
| reports | Generated report metadata |
| audit_logs | Compliance audit trail |
| calendar_events | Calendar module |
| system_settings | Configuration |

---

## Security

- JWT authentication with configurable expiry
- bcrypt password hashing
- Role-based access control (RBAC)
- Session tracking with IP/device logging
- Audit logging for all critical actions
- CORS configuration
- XSRF protection (Streamlit built-in)

**Production checklist:**
1. Change `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`
2. Use HTTPS reverse proxy (nginx/traefik)
3. Enable PostgreSQL SSL
4. Set `DEBUG=false`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/auth/login` | Authenticate |
| GET | `/api/users/me` | Current user |
| GET | `/api/notifications` | User notifications |
| GET | `/api/attendance/today` | Today's attendance |

Full API docs at `/docs` when API is running.

---

## Testing

```bash
pytest tests/ -v
```

---

## Scalability (10,000+ Employees)

- PostgreSQL connection pooling (20 connections, 40 overflow)
- Indexed columns on all query-heavy fields
- Service-layer architecture for horizontal scaling
- Redis-ready for caching and notification queues
- Docker Compose with separate API and app containers
- Alembic migrations for zero-downtime schema changes

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Custom CSS, Plotly, ECharts |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose), bcrypt |
| Export | Pandas, OpenPyXL, ReportLab |
| Deploy | Docker, Docker Compose |

---

## License

Proprietary — WORKPULSE AI © 2026
