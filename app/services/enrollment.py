from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories.audit_log import AuditLogRepository
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository


class EnrollmentService:
    def __init__(self, db: Session) -> None:
        self.enrollments = EnrollmentRepository(db)
        self.courses = CourseRepository(db)
        self.audit_logs = AuditLogRepository(db)

    def enroll(self, student: User, course_id: int) -> Enrollment:
        if student.role != "student":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can enroll")
        course = self.courses.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        if not course.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course is inactive")
        if self.enrollments.get_by_user_and_course(student.id, course_id) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already enrolled in this course")
        if self.courses.count_enrollments(course_id) >= course.capacity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course is full")
        enrollment = self.enrollments.create(student.id, course_id)
        self.audit_logs.create(action="ENROLL", user_id=student.id, course_id=course_id, performed_by=student.id)
        return enrollment

    def deregister(self, student: User, course_id: int) -> None:
        if student.role != "student":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can deregister")
        enrollment = self.enrollments.get_by_user_and_course(student.id, course_id)
        if enrollment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        self.enrollments.delete(enrollment)
        self.audit_logs.create(action="DEREGISTER", user_id=student.id, course_id=course_id, performed_by=student.id)

    def list_all(self, skip: int = 0, limit: int = 100) -> tuple[list[Enrollment], int]:
        return self.enrollments.list_all(skip=skip, limit=limit)

    def list_by_course(self, course_id: int, skip: int = 0, limit: int = 100) -> tuple[list[Enrollment], int]:
        course = self.courses.get_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
        return self.enrollments.list_by_course(course_id, skip=skip, limit=limit)

    def remove_student(self, course_id: int, user_id: int, performed_by: int) -> None:
        enrollment = self.enrollments.get_by_user_and_course(user_id, course_id)
        if enrollment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
        self.enrollments.delete(enrollment)
        self.audit_logs.create(action="ADMIN_REMOVE", user_id=user_id, course_id=course_id, performed_by=performed_by)

    def list_audit_logs(self, skip: int = 0, limit: int = 100) -> tuple[list[AuditLog], int]:
        return self.audit_logs.list_all(skip=skip, limit=limit)