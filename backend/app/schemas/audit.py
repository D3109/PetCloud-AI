from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogOut(BaseModel):
    id: int
    actor_user_id: int | None = None
    actor_email: str | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    detail: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
