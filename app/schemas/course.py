from pydantic import BaseModel, EmailStr


class CourseCreate(BaseModel):
    course_code: str
    title: str
    unit: int = 2


class CourseOut(BaseModel):
    course_code: str
    title: str
    unit: int
    lecturer_id: int

    class Config:
        from_attributes = True


class EnrolRequest(BaseModel):
    student_email: EmailStr
