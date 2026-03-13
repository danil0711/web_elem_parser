from datetime import datetime, timedelta, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    selector = Column(String, nullable=False)
    interval = Column(Integer, default=600)  # в секундах
    condition = Column(String, nullable=True)  # условие для алерта, опционально
    duration = Column(
        Integer, nullable=True
    )  # сколько task должна работать, в секундах
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    next_run_at = Column(DateTime(timezone=True), nullable=False)

    last_run_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tasks")

    __table_args__ = (
        Index("idx_tasks_active_next_run", "is_active", "next_run_at"),
    )


    def schedule_next_run(self, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)

        self.last_run_at = now
        self.next_run_at = now + timedelta(seconds=self.interval)
