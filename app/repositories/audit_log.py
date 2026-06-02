from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, action: str, user_id: int, course_id: int, performed_by: int) -> AuditLog:
        log = AuditLog(
            action=action,
            user_id=user_id,
            course_id=course_id,
            performed_by=performed_by,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_all(self, skip: int = 0, limit: int = 100) -> tuple[list[AuditLog], int]:
        total = int(self.db.scalar(select(func.count(AuditLog.id))) or 0)
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total
