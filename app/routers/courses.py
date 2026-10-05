from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrolment import Enrolment
from app.schemas.course import CourseCreate, CourseOut, EnrolRequest

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseOut, status_code=201)
def create_course(
    payload: CourseCreate,
    db: DBSession = Depends(get_db),
    lecturer: User = Depends(require_role(UserRole.LECTURER)),
):
    if db.query(Course).filter(Course.course_code == payload.course_code).first():
        raise HTTPException(status_code=400, detail="A course with this code already exists.")

    course = Course(
        course_code=payload.course_code,
        title=payload.title,
        unit=payload.unit,
        lecturer_id=lecturer.user_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[CourseOut])
def list_courses(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role == UserRole.LECTURER:
        return db.query(Course).filter(Course.lecturer_id == user.user_id).all()

    if user.role == UserRole.STUDENT:
        return (
            db.query(Course)
            .join(Enrolment, Enrolment.course_code == Course.course_code)
            .filter(Enrolment.student_id == user.user_id)
            .all()
        )

    # Admins see every course, for visibility into departmental load.
    return db.query(Course).all()


@router.post("/{course_code}/enrol", status_code=201)
def enrol_student(
    course_code: str,
    payload: EnrolRequest,
    db: DBSession = Depends(get_db),
    lecturer: User = Depends(require_role(UserRole.LECTURER)),
):
    course = db.query(Course).filter(Course.course_code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    if course.lecturer_id != lecturer.user_id:
        raise HTTPException(status_code=403, detail="You do not own this course.")

    student = db.query(User).filter(
        User.email == payload.student_email, User.role == UserRole.STUDENT
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="No student account found with that email.")

    already = (
        db.query(Enrolment)
        .filter(Enrolment.student_id == student.user_id, Enrolment.course_code == course_code)
        .first()
    )
    if already:
        raise HTTPException(status_code=400, detail="This student is already enrolled.")

    enrolment = Enrolment(student_id=student.user_id, course_code=course_code)
    db.add(enrolment)
    db.commit()
    return {"detail": f"Enrolled {student.full_name} in {course_code}."}
