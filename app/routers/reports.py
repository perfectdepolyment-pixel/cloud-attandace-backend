from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.session import Session
from app.models.attendance import Attendance
from app.schemas.attendance import ReportRow

router = APIRouter(prefix="/reports", tags=["reports"])


def _row(attendance: Attendance, course_code: str, student_name: str) -> ReportRow:
    return ReportRow(
        attendance_id=attendance.attendance_id,
        student_name=student_name,
        course_code=course_code,
        distance_metres=attendance.distance_metres,
        status=attendance.status,
        timestamp=attendance.timestamp,
    )


@router.get("/session/{session_id}", response_model=list[ReportRow])
def session_report(
    session_id: int,
    db: DBSession = Depends(get_db),
    lecturer: User = Depends(require_role(UserRole.LECTURER)),
):
    session = db.query(Session).filter(Session.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    course = db.query(Course).filter(Course.course_code == session.course_code).first()
    if course.lecturer_id != lecturer.user_id:
        raise HTTPException(status_code=403, detail="You do not own this session.")

    rows = (
        db.query(Attendance, User)
        .join(User, User.user_id == Attendance.student_id)
        .filter(Attendance.session_id == session_id)
        .order_by(Attendance.timestamp.desc())
        .all()
    )
    return [_row(a, session.course_code, u.full_name) for a, u in rows]


@router.get("/course/{course_code}", response_model=list[ReportRow])
def course_report(
    course_code: str,
    db: DBSession = Depends(get_db),
    lecturer: User = Depends(require_role(UserRole.LECTURER)),
):
    course = db.query(Course).filter(Course.course_code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.lecturer_id != lecturer.user_id:
        raise HTTPException(status_code=403, detail="You do not own this course.")

    rows = (
        db.query(Attendance, User, Session)
        .join(User, User.user_id == Attendance.student_id)
        .join(Session, Session.session_id == Attendance.session_id)
        .filter(Session.course_code == course_code)
        .order_by(Attendance.timestamp.desc())
        .all()
    )
    return [_row(a, course_code, u.full_name) for a, u, _s in rows]


@router.get("/student/{student_id}", response_model=list[ReportRow])
def student_report(
    student_id: int,
    db: DBSession = Depends(get_db),
    lecturer: User = Depends(require_role(UserRole.LECTURER)),
):
    rows = (
        db.query(Attendance, User, Session, Course)
        .join(User, User.user_id == Attendance.student_id)
        .join(Session, Session.session_id == Attendance.session_id)
        .join(Course, Course.course_code == Session.course_code)
        .filter(Attendance.student_id == student_id, Course.lecturer_id == lecturer.user_id)
        .order_by(Attendance.timestamp.desc())
        .all()
    )
    return [_row(a, c.course_code, u.full_name) for a, u, _s, c in rows]
