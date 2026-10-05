from pydantic import BaseModel, EmailStr, Field


class CreateLecturerRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class LecturerOut(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    course_count: int

    class Config:
        from_attributes = True
