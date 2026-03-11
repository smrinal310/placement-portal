# Placement Portal

A full-stack campus placement management web application built for the **AppDev 2** course at IIT Madras BS Degree program.

The platform connects three roles - **Students**, **Companies**, and an **Admin** - on a single portal to streamline the entire campus recruitment lifecycle.

## Features

- **Students** - Register, build a profile, upload resumes, browse eligible placement drives, apply, and track application status in real time
- **Companies** - Register, create placement drives with eligibility criteria, manage applicants, and update interview/selection status
- **Admin** - Approve/reject company registrations and placement drives, manage student and company accounts, view placement statistics, and generate monthly reports
- **Notifications** - In-app notification system for application status updates
- **Background Jobs** - Daily interview reminder emails and monthly placement report generation via Celery + Redis
- **Exports** - Async CSV export of application data

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vue Router, Pinia, Axios, Vite |
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT-Extended |
| Database | SQLite |
| Cache | Redis (via Flask-Caching) |
| Task Queue | Celery + Redis |
| Email | Flask-Mail (MailHog for local dev) |

## Project Structure

```
placement-portal/
├── client/          # Vue 3 frontend SPA
└── server/          # Flask REST API backend
```

## Quick Start

### Prerequisites

- [Bun](https://bun.sh) (frontend)
- [uv](https://github.com/astral-sh/uv) (backend Python package manager)
- [Redis](https://redis.io) running on `localhost:6379`

### Run both services

```bash
# Terminal 1 – backend
cd server
make install
make run

# Terminal 2 – frontend
cd client
make install
make run

# Terminal 3 – Celery worker (for background jobs)
cd server
make celery-worker

# Terminal 4 – Celery beat scheduler (for periodic tasks)
cd server
make celery-beat
```

The frontend dev server runs on **http://localhost:5173** and the backend API on **http://localhost:5000**.

## Environment Variables

Copy `.env.example` to `.env` in `server/` and set:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `a-random-secret-key` | Flask secret key |
| `JWT_SECRET_KEY` | `jwt-secret-key` | JWT signing key |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///database.db` | Database URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL (cache + Celery) |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | Comma-separated CORS origins |
| `DEBUG` | `false` | Enable Flask debug mode |
