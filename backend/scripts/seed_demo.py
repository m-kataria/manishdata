"""Seeds the database with realistic demo data for the Nerval ops dashboard.

Idempotent: only runs if the jobs table is empty. Drop the database file to reseed.
"""

import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import InventoryItem, Job, Quote, SyncLog


def utc(offset_minutes: int = 0) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=offset_minutes)


def main() -> None:
    app = create_app()
    with app.app_context():
        if db.session.query(Job).count() > 0:
            print("Already seeded. Skipping (drop nerval_ops.db to reseed).")
            return

        # --- Jobs --------------------------------------------------------------
        jobs = [
            Job(
                job_number="JOB-2026-0148",
                title="Heat Trace Installation — Tank Farm North",
                customer_name="Pioneer Petroleum Ltd.",
                status="in_progress",
                sf_opportunity_id="0066T00000HxA01QAB",
                bc_sales_order_id="SO-001234",
                scheduled_for=utc(-60 * 24 * 2),
                notes="Phase 2 of 3. Cable type: self-regulating 8W/ft.",
            ),
            Job(
                job_number="JOB-2026-0147",
                title="Pipe Insulation Replacement",
                customer_name="Northern Refineries",
                status="scheduled",
                sf_opportunity_id="0066T00000HxB02QAB",
                scheduled_for=utc(60 * 24 * 3),
                notes="Outage window Mar 14-16.",
            ),
            Job(
                job_number="JOB-2026-0146",
                title="Glycol System Recharge — Lift Station 4",
                customer_name="Mountain Energy Coop",
                status="completed",
                bc_sales_order_id="SO-001230",
                scheduled_for=utc(-60 * 24 * 7),
                completed_at=utc(-60 * 24 * 5),
            ),
            Job(
                job_number="JOB-2026-0145",
                title="Site Survey — New Compressor Station",
                customer_name="Cascade Midstream",
                status="completed",
                sf_opportunity_id="0066T00000HxC03QAB",
                scheduled_for=utc(-60 * 24 * 10),
                completed_at=utc(-60 * 24 * 9),
            ),
            Job(
                job_number="JOB-2026-0144",
                title="Emergency Trace Cable Repair",
                customer_name="Pioneer Petroleum Ltd.",
                status="cancelled",
                scheduled_for=utc(-60 * 24 * 12),
                notes="Customer resolved internally before dispatch.",
            ),
            Job(
                job_number="JOB-2026-0143",
                title="Annual Thermostat Calibration",
                customer_name="Boreal Gas Processing",
                status="draft",
                notes="Awaiting customer PO.",
            ),
            Job(
                job_number="JOB-2026-0142",
                title="Heat Trace Commissioning — Phase 1",
                customer_name="Cascade Midstream",
                status="in_progress",
                sf_opportunity_id="0066T00000HxC03QAB",
                bc_sales_order_id="SO-001228",
                scheduled_for=utc(-60 * 24 * 1),
            ),
            Job(
                job_number="JOB-2026-0141",
                title="Insulation Audit — Tank Farm South",
                customer_name="Pioneer Petroleum Ltd.",
                status="scheduled",
                scheduled_for=utc(60 * 24 * 5),
            ),
        ]
        for j in jobs:
            db.session.add(j)

        # --- Quotes ------------------------------------------------------------
        quotes = [
            Quote(
                quote_number="Q-2026-0089",
                customer_name="Pioneer Petroleum Ltd.",
                status="accepted",
                total_amount=Decimal("48250.00"),
                bc_sales_quote_id="SQ-008912",
                sf_opportunity_id="0066T00000HxA01QAB",
                valid_until=utc(60 * 24 * 30),
            ),
            Quote(
                quote_number="Q-2026-0088",
                customer_name="Cascade Midstream",
                status="accepted",
                total_amount=Decimal("127400.00"),
                bc_sales_quote_id="SQ-008910",
                sf_opportunity_id="0066T00000HxC03QAB",
                valid_until=utc(60 * 24 * 45),
            ),
            Quote(
                quote_number="Q-2026-0087",
                customer_name="Northern Refineries",
                status="sent",
                total_amount=Decimal("32100.00"),
                sf_opportunity_id="0066T00000HxB02QAB",
                valid_until=utc(60 * 24 * 14),
            ),
            Quote(
                quote_number="Q-2026-0086",
                customer_name="Boreal Gas Processing",
                status="draft",
                total_amount=Decimal("8950.00"),
            ),
            Quote(
                quote_number="Q-2026-0085",
                customer_name="Mountain Energy Coop",
                status="accepted",
                total_amount=Decimal("14200.00"),
                bc_sales_quote_id="SQ-008902",
                valid_until=utc(-60 * 24 * 2),
            ),
            Quote(
                quote_number="Q-2026-0084",
                customer_name="Atlas Gas & Power",
                status="rejected",
                total_amount=Decimal("76300.00"),
                valid_until=utc(-60 * 24 * 15),
            ),
            Quote(
                quote_number="Q-2026-0083",
                customer_name="Pioneer Petroleum Ltd.",
                status="expired",
                total_amount=Decimal("11800.00"),
                valid_until=utc(-60 * 24 * 35),
            ),
        ]
        for q in quotes:
            db.session.add(q)

        # --- Inventory items ---------------------------------------------------
        items = [
            ("10001", "Heat Trace Cable, Self-Regulating 8W/ft", "FT", "12.40", "2840.50"),
            ("10002", "Heat Trace Cable, Self-Regulating 12W/ft", "FT", "16.80", "1245.00"),
            ("10003", "Pipe Insulation, Fiberglass 2in", "FT", "4.75", "5600.00"),
            ("10004", "Pipe Insulation, Mineral Wool 1in", "FT", "3.20", "1820.00"),
            ("10005", "Glycol Antifreeze, Propylene 55gal", "DR", "485.00", "12.00"),
            ("10006", "Thermostat Controller, Digital", "EA", "245.00", "38.00"),
            ("10007", "End Seal Kit, Heat Trace", "EA", "32.50", "164.00"),
            ("10008", "Power Connection Kit", "EA", "78.00", "92.00"),
            ("10009", "Aluminum Tape, 2in x 150ft", "RL", "18.75", "212.00"),
            ("10010", "Junction Box, Weatherproof 4x4", "EA", "54.00", "47.00"),
            ("10011", "Junction Box, Weatherproof 6x6", "EA", "82.00", "23.00"),
            ("10012", "Ground Fault Protector 30mA", "EA", "165.00", "16.00"),
            ("10013", "Splice Kit, In-Line", "EA", "28.50", "104.00"),
            ("10014", "Insulation Cladding, Aluminum 24in", "FT", "8.90", "780.00"),
            ("10015", "Thermal Sensor RTD PT100", "EA", "94.00", "31.00"),
        ]
        for number, name, uom, price, qty in items:
            db.session.add(
                InventoryItem(
                    bc_item_id=f"item-{number}",
                    item_number=number,
                    display_name=name,
                    base_unit_of_measure=uom,
                    unit_price=Decimal(price),
                    inventory_on_hand=Decimal(qty),
                )
            )

        # --- Sync log entries --------------------------------------------------
        sync_entries = [
            # Most recent BC events
            SyncLog(
                integration="business_central",
                entity="ping",
                status="success",
                started_at=utc(-3),
                completed_at=utc(-3),
                records_synced=0,
            ),
            SyncLog(
                integration="business_central",
                entity="inventory_items",
                status="success",
                started_at=utc(-15),
                completed_at=utc(-14),
                records_synced=15,
            ),
            SyncLog(
                integration="business_central",
                entity="sales_orders",
                status="success",
                started_at=utc(-60 * 2),
                completed_at=utc(-60 * 2 + 1),
                records_synced=23,
            ),
            # Most recent SF events
            SyncLog(
                integration="salesforce",
                entity="ping",
                status="success",
                started_at=utc(-7),
                completed_at=utc(-7),
                records_synced=0,
            ),
            SyncLog(
                integration="salesforce",
                entity="opportunities",
                status="success",
                started_at=utc(-60),
                completed_at=utc(-60 + 1),
                records_synced=12,
            ),
            SyncLog(
                integration="salesforce",
                entity="accounts",
                status="success",
                started_at=utc(-60 * 3),
                completed_at=utc(-60 * 3 + 1),
                records_synced=47,
            ),
            # One historical failure to show the "failed" status badge
            SyncLog(
                integration="business_central",
                entity="customers",
                status="failed",
                started_at=utc(-60 * 24),
                completed_at=utc(-60 * 24),
                records_synced=0,
                error_message="503 Service Unavailable from BC API",
            ),
            SyncLog(
                integration="salesforce",
                entity="contacts",
                status="failed",
                started_at=utc(-60 * 24 * 2),
                completed_at=utc(-60 * 24 * 2),
                records_synced=0,
                error_message="INVALID_SESSION_ID: Session expired or invalid",
            ),
        ]
        for s in sync_entries:
            db.session.add(s)

        db.session.commit()

        counts = {
            "jobs": db.session.query(Job).count(),
            "quotes": db.session.query(Quote).count(),
            "inventory": db.session.query(InventoryItem).count(),
            "sync_log": db.session.query(SyncLog).count(),
        }
        print("Seeded:", counts)


if __name__ == "__main__":
    main()
