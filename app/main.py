from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, courses, sessions, attendance, reports, admin

# Import models so their tables register on Base.metadata before create_all.
from app.models import user, course, enrolment, session, attendance as attendance_model  # noqa: F401

app = FastAPI(
    title="Cloud Attendance Management System API",
    description="Moshood Abiola Polytechnic — Department of Computer Science",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # For a student project, auto-creating tables keeps setup simple.
    # Swap for Alembic migrations if the schema needs to evolve in production.
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(sessions.router)
app.include_router(attendance.router)
app.include_router(reports.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
