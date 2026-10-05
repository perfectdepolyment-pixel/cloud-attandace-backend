from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User, UserRole
from app.models.session import Session, SessionStatus
from app.models.enrolment import Enrolment
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.attendance import CheckInRequest, CheckInResult, MyAttendanceOut
from app.services.geofencing import is_within_geofence

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/checkin", response_model=CheckInResult, status_code=201)
def check_in(
    payload: CheckInRequest,
    db: DBSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.STUDENT)),
):
    session = db.query(Session).filter(Session.session_id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.status != SessionStatus.OPEN:
        raise HTTPException(status_code=400, detail="This session is closed.")

    enrolled = (
        db.query(Enrolment)
        .filter(Enrolment.student_id == student.user_id, Enrolment.course_code == session.course_code)
        .first()
    )
    if not enrolled:
        raise HTTPException(status_code=403, detail="You are not enrolled in this course.")

    # A PRESENT record is final and idempotent — return it rather than
    # creating a duplicate. A prior REJECTED attempt may retry (e.g. after
    # moving closer to the lecturer), so it does not block a new attempt.
    already_present = (
        db.query(Attendance)
        .filter(
            Attendance.session_id == session.session_id,
            Attendance.student_id == student.user_id,
            Attendance.status == AttendanceStatus.PRESENT,
        )
        .first()
    )
    if already_present:
        return already_present

    status_value, distance = is_within_geofence(
        session.centre_lat, session.centre_lng, payload.submitted_lat, payload.submitted_lng, session.radius_metres
    )

    record = Attendance(
        session_id=session.session_id,
        student_id=student.user_id,
        submitted_lat=payload.submitted_lat,
        submitted_lng=payload.submitted_lng,
        distance_metres=distance,
        status=AttendanceStatus(status_value),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/me", response_model=list[MyAttendanceOut])
def my_attendance(
    db: DBSession = Depends(get_db), student: User = Depends(require_role(UserRole.STUDENT))
):
    rows = (
        db.query(Attendance, Session)
        .join(Session, Session.session_id == Attendance.session_id)
        .filter(Attendance.student_id == student.user_id)
        .order_by(Attendance.timestamp.desc())
        .all()
    )
    return [
        MyAttendanceOut(
            attendance_id=a.attendance_id,
            course_code=s.course_code,
            status=a.status,
            distance_metres=a.distance_metres,
            timestamp=a.timestamp,
        )
        for a, s in rows
    ]
