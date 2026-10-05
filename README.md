# Cloud Attendance Management System — Backend

FastAPI backend for the Department of Computer Science, Moshood Abiola
Polytechnic. Serves the unified `attendance-app` React frontend across
three roles: STUDENT, LECTURER, ADMIN.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in DATABASE_URL and JWT_SECRET_KEY
```

For local development without PostgreSQL installed, you can point
`DATABASE_URL` at SQLite instead: `sqlite:///./dev.db`. Switch to a real
PostgreSQL URL for anything beyond local testing — Chapter Three specifies
PostgreSQL as the data tier.

## Create the first admin account

There is no self-service admin signup. Run:

```bash
python -m scripts.seed_admin
```

This prompts for a name, email and password, creates the tables if they
don't exist yet, and inserts the admin. Sign in with those details at
`/admin/login` in the frontend.

## Run the API

```bash
uvicorn app.main:app --reload
```

API at http://localhost:8000, interactive docs at http://localhost:8000/docs.
Tables are created automatically on startup (`Base.metadata.create_all`) —
no separate migration step needed for this project's scope.

## Run tests

```bash
pytest
```

`tests/test_geofencing.py` checks the Haversine distance function in
isolation with known coordinate pairs, before it's ever wired to the API —
matching the testing approach described in Chapter Three.

## Role model

| Role     | Created by                              | Can do                                                         |
|----------|-------------------------------------------|------------------------------------------------------------------|
| ADMIN    | `scripts/seed_admin.py` (first one only, by hand) | Create/list lecturer accounts (`/admin/lecturers`)         |
| LECTURER | An admin, via `POST /admin/lecturers`     | Create courses, enrol students, start/close sessions, view reports |
| STUDENT  | Self-service, via `POST /auth/register`   | View active sessions, check in, view own attendance history       |

There is deliberately **no** self-service path to become a LECTURER or
ADMIN — `/auth/register` always creates a STUDENT, matching the frontend's
"student is the default/main login" design.

## Endpoint summary

See `backend-documentation.md` (in the project root, delivered earlier) for
the full endpoint reference — it has been updated to include the `/admin/*`
routes and the ADMIN role. Quick reference:

```
POST   /auth/register            student self-registration
POST   /auth/login                any role

GET    /courses                   role-scoped list
POST   /courses                   lecturer
POST   /courses/{code}/enrol      lecturer

POST   /sessions                  lecturer — start, with GPS + 5-10m radius
PATCH  /sessions/{id}/close       lecturer
GET    /sessions/active           student

POST   /attendance/checkin        student — geofence check via Haversine
GET    /attendance/me             student

GET    /reports/session/{id}      lecturer
GET    /reports/course/{code}     lecturer
GET    /reports/student/{id}      lecturer

POST   /admin/lecturers           admin — create a lecturer account
GET    /admin/lecturers           admin — list lecturers + course counts

GET    /health                    liveness check
```

## Notes on design decisions

- **Retry after rejection:** a student's first check-in attempt can be
  REJECTED (too far) without blocking a second attempt after moving closer —
  only a PRESENT record is treated as final and returned idempotently on
  a repeat call.
- **One open session per course:** starting a new session while one is
  already open for that course is rejected, avoiding ambiguous geofence
  reference points.
- **Ownership checks:** a lecturer can only manage/report on courses and
  sessions they created; students can only check in to sessions for
  courses they're enrolled in.
