import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrolment import Enrolment
from app.models.session import Session, SessionStatus
from app.schemas.session import SessionCreate, SessionOut, ActiveSessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=201)
def start_session(
    payload: SessionCreate,
    db: DBSession = Depends(get_db),
    lecturer: User = Depends(require_role(UserRole.LECTURER)),
):
    course = db.query(Course).filter(Course.course_code == payload.course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.lecturer_id != lecturer.user_id:
        raise HTTPException(status_code=403, detail="You do not own this course.")

    existing_open = (
        db.query(Session)
        .filter(Session.course_code == payload.course_code, Session.status == SessionStatus.OPEN)
        .first()
    )
    if existing_open:
        raise HTTPException(
            status_code=400,
            detail="This course already has an open session. Close it before starting another.",
        )

    session = Session(
        course_code=payload.course_code,
        centre_lat=payload.centre_lat,
        centre_lng=payload.centre_lng,
        radius_metres=payload.radius_metres,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.patch("/{session_id}/close", response_model=SessionOut)
def close_session(
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

    session.status = SessionStatus.CLOSED
    session.closed_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


@router.get("/active", response_model=list[ActiveSessionOut])
def active_sessions(
    db: DBSession = Depends(get_db), student: User = Depends(require_role(UserRole.STUDENT))
):
    rows = (
        db.query(Session, Course)
        .join(Course, Course.course_code == Session.course_code)
        .join(Enrolment, Enrolment.course_code == Course.course_code)
        .filter(Enrolment.student_id == student.user_id, Session.status == SessionStatus.OPEN)
        .all()
    )
    return [
        ActiveSessionOut(
            session_id=s.session_id,
            course_code=c.course_code,
            course_title=c.title,
            opened_at=s.opened_at,
        )
        for s, c in rows
    ]
