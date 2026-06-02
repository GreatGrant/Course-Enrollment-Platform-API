from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.schemas.course import CourseCreate, CourseUpdate


class CourseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _not_deleted(self):
        return Course.deleted_at.is_(None)

    def list_active(self, skip: int = 0, limit: int = 100) -> tuple[list[Course], int]:
        base = select(Course).where(Course.is_active.is_(True), self._not_deleted())
        total = int(self.db.scalar(select(func.count()).select_from(base.subquery())) or 0)
        stmt = base.order_by(Course.id).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def list_all(self) -> list[Course]:
        return list(self.db.scalars(select(Course).where(self._not_deleted()).order_by(Course.id)).all())

    def get_by_id(self, course_id: int) -> Course | None:
        course = self.db.get(Course, course_id)
        if course is not None and course.deleted_at is not None:
            return None
        return course

    def get_by_code(self, code: str) -> Course | None:
        return self.db.scalar(select(Course).where(Course.code == code))

    def create(self, data: CourseCreate) -> Course:
        course = Course(
            title=data.title,
            code=data.code.upper(),
            capacity=data.capacity,
            is_active=data.is_active,
        )
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Course, data: CourseUpdate) -> Course:
        if data.title is not None:
            course.title = data.title
        if data.code is not None:
            course.code = data.code.upper()
        if data.capacity is not None:
            course.capacity = data.capacity
        if data.is_active is not None:
            course.is_active = data.is_active
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        course.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    def count_enrollments(self, course_id: int) -> int:
        stmt = select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)
        return int(self.db.scalar(stmt) or 0)