# Placement Portal - Backend

Flask REST API backend for the Placement Portal. Handles authentication, business logic, background jobs, and email notifications.

## Tech Stack

- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM (SQLite in dev, configurable via env var)
- **Flask-JWT-Extended** - JWT authentication and role-based authorization
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-Mail** - Email notifications
- **Flask-Caching + Redis** - Server-side response caching
- **Celery + Redis** - Async task queue and scheduled jobs
- **uv** - Python package manager

## Project Structure

```
server/
├── main.py                  # Application entry point, Celery instance
├── pyproject.toml           # Dependencies (uv)
├── scripts/
│   └── seed_db.py           # Database seeding script
├── static/
│   └── templates/           # Jinja2 email and report templates
│   └── uploads/             # Uploaded resumes, logos, exports
└── src/
    ├── __init__.py          # App factory (create_app)
    ├── config.py            # Config from environment variables
    ├── constants.py         # Enum definitions (roles, statuses)
    ├── models.py            # SQLAlchemy models
    ├── apis/
    │   ├── auth.py          # /auth - login, logout
    │   ├── admin.py         # /api/admin - dashboard, approvals, reports
    │   ├── company.py       # /api/company - drives, applications
    │   └── student.py       # /api/student - profile, drives, apply
    ├── helpers/
    │   ├── auth.py          # JWT-based role decorators
    │   ├── cache.py         # Cache helpers and invalidation
    │   ├── cel_helper.py    # Celery task utility functions
    │   ├── email.py         # Email sending helpers
    │   ├── student_helpers.py # Eligibility checks
    │   └── utils.py         # Generic response helpers
    └── jobs/
        ├── celery_app.py    # Celery app factory
        └── tasks.py         # Async and scheduled tasks
```

## Setup

### Prerequisites

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv)
- Redis running on `localhost:6379`

### Install dependencies

```bash
uv sync
# or: make install
```

### Environment variables

Create a `.env` file in `server/`:

```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
SQLALCHEMY_DATABASE_URI=sqlite:///database.db
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=http://localhost:5173
DEBUG=true
PORT=5000

# Mail (use MailHog locally)
MAIL_SERVER=localhost
MAIL_PORT=1025
```

### Run the dev server

```bash
uv run python main.py
# or: make run
```

API runs on **http://localhost:5000**.

### Celery worker (background jobs)

```bash
make celery-worker
```

### Celery beat scheduler (periodic tasks)

```bash
make celery-beat
```

### MailHog (local email testing)

```bash
make mailhog
```

Exposes SMTP on port 1025 and the MailHog web UI on **http://localhost:8025**.

### Seed the database

```bash
make populate
```

### Lint / format

```bash
make lint     # ruff check --fix
make format   # ruff format
```

## API Overview

| Prefix | Description |
|---|---|
| `POST /auth/login` | Authenticate, receive JWT |
| `POST /auth/logout` | Invalidate session |
| `/api/student/*` | Student profile, drives, applications, notifications |
| `/api/company/*` | Company profile, drives, applicant management |
| `/api/admin/*` | User management, approvals, statistics, reports |

All protected endpoints require `Authorization: Bearer <token>` header.

## Scheduled Tasks (Celery Beat)

| Task | Schedule |
|---|---|
| `send_daily_interview_reminders` | Daily - emails students about tomorrow's interviews |
| `send_monthly_placement_report` | Monthly - generates and emails a placement statistics report |
