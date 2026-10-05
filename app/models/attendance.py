import enum
import datetime

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    REJECTED = "REJECTED"


class Attendance(Base):
    __tablename__ = "attendance"
    # No unique constraint on (session_id, student_id): a student who is
    # first REJECTED (out of range) is allowed to move closer and retry.
    # The router treats an existing PRESENT record as final and idempotent.

    attendance_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    submitted_lat = Column(Float, nullable=False)
    submitted_lng = Column(Float, nullable=False)
    distance_metres = Column(Float, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records")
