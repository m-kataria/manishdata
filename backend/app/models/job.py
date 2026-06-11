from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Job(db.Model):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Status: draft, scheduled, in_progress, completed, cancelled
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)

    # External links (filled in when synced from SF/BC)
    sf_opportunity_id: Mapped[str | None] = mapped_column(String(60), index=True)
    bc_sales_order_id: Mapped[str | None] = mapped_column(String(60), index=True)

    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_by = relationship("User")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "jobNumber": self.job_number,
            "title": self.title,
            "customerName": self.customer_name,
            "status": self.status,
            "sfOpportunityId": self.sf_opportunity_id,
            "bcSalesOrderId": self.bc_sales_order_id,
            "scheduledFor": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
