from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class SyncLog(db.Model):
    """Tracks pulls from each integration so the UI can show 'last synced X minutes ago'."""

    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # 'business_central' or 'salesforce'
    integration: Mapped[str] = mapped_column(String(40), nullable=False, index=True)

    # 'customers', 'sales_orders', 'inventory_items', 'accounts', 'opportunities', 'contacts', 'ping', ...
    entity: Mapped[str] = mapped_column(String(60), nullable=False, index=True)

    # 'started', 'success', 'failed'
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "integration": self.integration,
            "entity": self.entity,
            "status": self.status,
            "startedAt": self.started_at.isoformat(),
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "recordsSynced": self.records_synced,
            "errorMessage": self.error_message,
        }

    def mark_success(self, records: int = 0) -> None:
        self.status = "success"
        self.completed_at = datetime.now(timezone.utc)
        self.records_synced = records

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = error[:2000]
