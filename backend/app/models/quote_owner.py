from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class QuoteOwner(db.Model):
    """Tracks which app user created each BC sales quote.

    BC has its own salesperson code; this table records the local Flask-Login
    user who pressed "create" inside the ops dashboard, which BC does not store.
    """

    __tablename__ = "quote_owners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quote_no: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User")
