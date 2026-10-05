from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Enrolment(Base):
    __tablename__ = "enrolments"
    __table_args__ = (UniqueConstraint("student_id", "course_code", name="uq_student_course"),)

    enrolment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    course_code = Column(String, ForeignKey("courses.course_code"), nullable=False)

    student = relationship("User", back_populates="enrolments")
    course = relationship("Course", back_populates="enrolments")
