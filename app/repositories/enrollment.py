from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment


class EnrollmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, enrollment_id: int) -> Enrollment | None:
        return self.db.get(Enrollment, enrollment_id)

    def get_by_user_and_course(self, user_id: int, course_id: int) -> Enrollment | None:
        stmt = select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
        return self.db.scalar(stmt)

    def create(self, user_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def delete(self, enrollment: Enrollment) -> None:
        self.db.delete(enrollment)
        self.db.commit()

    def list_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Enrollment], int]:
        total = int(self.db.scalar(select(func.count(Enrollment.id))) or 0)
        stmt = select(Enrollment).order_by(Enrollment.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def list_by_course(self, course_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Enrollment], int]:
        base = select(Enrollment).where(Enrollment.course_id == course_id)
        total = int(self.db.scalar(select(func.count()).select_from(base.subquery())) or 0)
        stmt = base.order_by(Enrollment.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def count_for_course(self, course_id: int) -> int:
        stmt = select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)
        return int(self.db.scalar(stmt) or 0)