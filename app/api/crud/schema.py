# api/crud/task.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl, field_serializer
from typing import Optional

class TaskBase(BaseModel):
    
    url: HttpUrl
    selector: str
    interval: int = 600
    condition: Optional[str] = None
    duration: Optional[int] = None
    

class TaskCreate(TaskBase):
    pass

class TaskRead(BaseModel):
    id: int
    user_id: UUID           
    is_active: bool
    created_at: datetime
    last_run_at: Optional[datetime] = None
    url: HttpUrl
    selector: str
    interval: int
    condition: Optional[str] = None
    duration: Optional[int] = None

    class Config:
        from_attributes = True

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime, **kwargs):
        return v.isoformat()  # автоматически отдаёт строку JSON
    
    @field_serializer("last_run_at")
    def serialize_last_run_at(self, v: Optional[datetime], **kwargs):
        return v.isoformat() if v else None