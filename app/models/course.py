from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    course_code = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    unit = Column(Integer, nullable=False, default=2)
    lecturer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    lecturer = relationship("User", back_populates="courses")
    enrolments = relationship("Enrolment", back_populates="course", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="course", cascade="all, delete-orphan")
