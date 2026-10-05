import datetime

from pydantic import BaseModel

from app.models.attendance import AttendanceStatus


class CheckInRequest(BaseModel):
    session_id: int
    submitted_lat: float
    submitted_lng: float


class CheckInResult(BaseModel):
    attendance_id: int
    status: AttendanceStatus
    distance_metres: float
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


class MyAttendanceOut(BaseModel):
    attendance_id: int
    course_code: str
    status: AttendanceStatus
    distance_metres: float
    timestamp: datetime.datetime


class ReportRow(BaseModel):
    attendance_id: int
    student_name: str
    course_code: str
    distance_metres: float
    status: AttendanceStatus
    timestamp: datetime.datetime
