from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User, UserRole
from app.models.course import Course
from app.schemas.admin import CreateLecturerRequest, LecturerOut
from app.services.auth_service import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/lecturers", response_model=LecturerOut, status_code=201)
def create_lecturer(
    payload: CreateLecturerRequest,
    db: DBSession = Depends(get_db),
    _admin: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    The only way a lecturer account comes into existence: an admin creates
    it here. There is no self-service /auth/register path for lecturers.
    """
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    lecturer = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.LECTURER,
    )
    db.add(lecturer)
    db.commit()
    db.refresh(lecturer)
    return LecturerOut(
        user_id=lecturer.user_id,
        full_name=lecturer.full_name,
        email=lecturer.email,
        course_count=0,
    )


@router.get("/lecturers", response_model=list[LecturerOut])
def list_lecturers(
    db: DBSession = Depends(get_db), _admin: User = Depends(require_role(UserRole.ADMIN))
):
    rows = (
        db.query(User, func.count(Course.course_code).label("course_count"))
        .outerjoin(Course, Course.lecturer_id == User.user_id)
        .filter(User.role == UserRole.LECTURER)
        .group_by(User.user_id)
        .order_by(User.full_name)
        .all()
    )
    return [
        LecturerOut(
            user_id=u.user_id, full_name=u.full_name, email=u.email, course_count=count
        )
        for u, count in rows
    ]
