import enum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    LECTURER = "LECTURER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    courses = relationship("Course", back_populates="lecturer")
    enrolments = relationship("Enrolment", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")
