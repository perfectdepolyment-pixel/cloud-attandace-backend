"""
Seeds sample STUDENT accounts (and optionally enrols them in existing courses).
Safe to run repeatedly: students whose email already exists are skipped.

Usage (from the project root):
    python -m app.scripts.seed_students
    python -m app.scripts.seed_students --enrol     # also enrol in every existing course
    python -m app.scripts.seed_students --count 20  # add generated extra students

Optional env var:
    STUDENT_PASSWORD   password given to all seeded students (default: Student@123)
"""
import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal, Base, engine
from app.models import user, course, enrolment, session, attendance  # noqa: F401  (register tables)
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.enrolment import Enrolment
from app.services.auth_service import hash_password

DEFAULT_STUDENTS = [
    ("Adebayo Oluwaseun", "adebayo.oluwaseun@student.test"),
    ("Chinwe Okafor", "chinwe.okafor@student.test"),
    ("Ibrahim Musa", "ibrahim.musa@student.test"),
    ("Fatimah Yusuf", "fatimah.yusuf@student.test"),
    ("Tunde Bakare", "tunde.bakare@student.test"),
]


def main():
    parser = argparse.ArgumentParser(description="Seed student accounts.")
    parser.add_argument("--enrol", action="store_true", help="enrol seeded students in all existing courses")
    parser.add_argument("--count", type=int, default=0, help="extra generated students (student1@student.test, ...)")
    args = parser.parse_args()

    password = os.environ.get("STUDENT_PASSWORD", "Student@123")
    students = list(DEFAULT_STUDENTS) + [
        (f"Test Student {i}", f"student{i}@student.test") for i in range(1, args.count + 1)
    ]

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        password_hash = hash_password(password)  # hash once; bcrypt is slow
        created, seeded = 0, []
        for full_name, email in students:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                seeded.append(existing)
                continue
            student = User(full_name=full_name, email=email, password_hash=password_hash, role=UserRole.STUDENT)
            db.add(student)
            seeded.append(student)
            created += 1
        db.commit()
        print(f"Students created: {created}, already existed: {len(students) - created}.")

        if args.enrol:
            courses = db.query(Course).all()
            if not courses:
                print("No courses exist yet - skipping enrolment.")
            else:
                added = 0
                for s in seeded:
                    for c in courses:
                        exists = db.query(Enrolment).filter(
                            Enrolment.student_id == s.user_id,
                            Enrolment.course_code == c.course_code,
                        ).first()
                        if not exists:
                            db.add(Enrolment(student_id=s.user_id, course_code=c.course_code))
                            added += 1
                db.commit()
                print(f"Enrolments added: {added} across {len(courses)} course(s).")

        print(f"Login with any seeded email and password: {password}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
