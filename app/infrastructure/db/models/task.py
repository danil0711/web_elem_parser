from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
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

    last_run_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="tasks")

    def should_run(self, now: datetime | None = None) -> bool:
        """
        Проверяет, прошло ли interval секунд с последнего запуска задачи.

        Если задача ещё ни разу не запускалась (last_run_at = None),
        она должна выполниться сразу.
        """
        now = now or datetime.now(timezone.utc)
        if not self.last_run_at:
            return True
        return (now - self.last_run_at).total_seconds() >= self.interval
