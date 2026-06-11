from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db


class InventoryItem(db.Model):
    """Local cache of BC inventory items. Refreshed via the BC integration."""

    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bc_item_id: Mapped[str | None] = mapped_column(String(60), unique=True, index=True)
    item_number: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    base_unit_of_measure: Mapped[str | None] = mapped_column(String(20))

    unit_price: Mapped[float | None] = mapped_column(Numeric(12, 2))
    inventory_on_hand: Mapped[float | None] = mapped_column(Numeric(14, 4))

    last_synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "bcItemId": self.bc_item_id,
            "itemNumber": self.item_number,
            "displayName": self.display_name,
            "baseUnitOfMeasure": self.base_unit_of_measure,
            "unitPrice": float(self.unit_price) if self.unit_price is not None else None,
            "inventoryOnHand": float(self.inventory_on_hand) if self.inventory_on_hand is not None else None,
            "lastSyncedAt": self.last_synced_at.isoformat(),
        }
