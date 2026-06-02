from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    user_id: int
    course_id: int
    performed_by: int
    created_at: datetime
