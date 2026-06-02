from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.user import User
from app.schemas.course import CourseCreate, CourseRead, CourseStatusUpdate, CourseUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.course import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=PaginatedResponse[CourseRead])
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> dict:
    items, total = CourseService(db).list_active(skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)) -> CourseRead:
    return CourseService(db).get_public(course_id)


@router.post("", response_model=CourseRead, status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)) -> CourseRead:
    return CourseService(db).create(payload)


@router.put("/{course_id}", response_model=CourseRead)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)) -> CourseRead:
    return CourseService(db).update(course_id, payload)


@router.patch("/{course_id}/status", response_model=CourseRead)
def toggle_course(course_id: int, payload: CourseStatusUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)) -> CourseRead:
    return CourseService(db).set_status(course_id, payload.is_active)


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin_user)) -> None:
    CourseService(db).delete(course_id)