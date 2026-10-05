import datetime

from pydantic import BaseModel, Field

from app.models.session import SessionStatus


class SessionCreate(BaseModel):
    course_code: str
    centre_lat: float
    centre_lng: float
    radius_metres: float = Field(ge=5, le=10)


class SessionOut(BaseModel):
    session_id: int
    course_code: str
    centre_lat: float
    centre_lng: float
    radius_metres: float
    opened_at: datetime.datetime
    closed_at: datetime.datetime | None
    status: SessionStatus

    class Config:
        from_attributes = True


class ActiveSessionOut(BaseModel):
    session_id: int
    course_code: str
    course_title: str
    opened_at: datetime.datetime
