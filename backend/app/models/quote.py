from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Quote(db.Model):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quote_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Status: draft, sent, accepted, rejected, expired
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)

    total_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="CAD", nullable=False)

    bc_sales_quote_id: Mapped[str | None] = mapped_column(String(60), index=True)
    sf_opportunity_id: Mapped[str | None] = mapped_column(String(60), index=True)

    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"))
    job = relationship("Job", backref="quotes")

    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

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
            "quoteNumber": self.quote_number,
            "customerName": self.customer_name,
            "status": self.status,
            "totalAmount": float(self.total_amount) if self.total_amount is not None else None,
            "currency": self.currency,
            "bcSalesQuoteId": self.bc_sales_quote_id,
            "sfOpportunityId": self.sf_opportunity_id,
            "jobId": self.job_id,
            "validUntil": self.valid_until.isoformat() if self.valid_until else None,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }
