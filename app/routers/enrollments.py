from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin_user, get_current_user
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.audit_log import AuditLogRead
from app.schemas.enrollment import EnrollmentRead
from app.schemas.pagination import PaginatedResponse
from app.services.enrollment import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/{course_id}", response_model=EnrollmentRead, status_code=201)
def enroll(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Enrollment:
    return EnrollmentService(db).enroll(current_user, course_id)


@router.delete("/{course_id}", status_code=204)
def deregister(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    EnrollmentService(db).deregister(current_user, course_id)


@admin_router.get("/enrollments", response_model=PaginatedResponse[EnrollmentRead])
def view_all_enrollments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> dict:
    items, total = EnrollmentService(db).list_all(skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@admin_router.get("/courses/{course_id}/enrollments", response_model=PaginatedResponse[EnrollmentRead])
def view_course_enrollments(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> dict:
    items, total = EnrollmentService(db).list_by_course(course_id, skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@admin_router.delete("/courses/{course_id}/enrollments/{user_id}", status_code=204)
def remove_student(
    course_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> None:
    EnrollmentService(db).remove_student(course_id, user_id, performed_by=admin.id)


@admin_router.get("/audit-logs", response_model=PaginatedResponse[AuditLogRead])
def view_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> dict:
    items, total = EnrollmentService(db).list_audit_logs(skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}