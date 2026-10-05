import enum
import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class SessionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, ForeignKey("courses.course_code"), nullable=False)
    centre_lat = Column(Float, nullable=False)
    centre_lng = Column(Float, nullable=False)
    radius_metres = Column(Float, nullable=False)
    opened_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.OPEN, nullable=False)

    course = relationship("Course", back_populates="sessions")
    attendance_records = relationship("Attendance", back_populates="session", cascade="all, delete-orphan")
