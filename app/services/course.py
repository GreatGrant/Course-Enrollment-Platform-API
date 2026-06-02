from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.repositories.course import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    def __init__(self, db: Session) -> None:
        self.courses = CourseRepository(db)

    def list_active(self, skip: int = 0, limit: int = 100) -> tuple[list[Course], int]:
        return self.courses.list_active(skip=skip, limit=limit)

    def get_public(self, course_id: int) -> Course:
        course = self.courses.get_by_id(course_id)
        if course is None or not course.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return course

    def create(self, data: CourseCreate) -> Course:
        if self.courses.get_by_code(data.code.upper()) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")
        return self.courses.create(data)

    def update(self, course_id: int, data: CourseUpdate) -> Course:
        course = self.courses.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if data.code is not None:
            existing = self.courses.get_by_code(data.code.upper())
            if existing is not None and existing.id != course.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")
        return self.courses.update(course, data)

    def delete(self, course_id: int) -> None:
        course = self.courses.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        self.courses.delete(course)

    def set_status(self, course_id: int, is_active: bool) -> Course:
        course = self.courses.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        course.is_active = is_active
        return self.courses.update(course, CourseUpdate())