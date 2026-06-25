"""Probe the standard BC v2.0 paymentTerms and locations endpoints.

Run from backend/ with: python scripts/smoke_lookups.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # type: ignore
load_dotenv(ROOT / ".env")

from app.services.business_central import BusinessCentralClient  # noqa: E402


def main() -> int:
    client = BusinessCentralClient(
        tenant_id=os.environ["BC_TENANT_ID"],
        client_id=os.environ["BC_CLIENT_ID"],
        client_secret=os.environ["BC_CLIENT_SECRET"],
        environment=os.environ["BC_ENVIRONMENT"],
        company_id=os.environ["BC_COMPANY_ID"],
        mock_mode="off",
    )

    for label, fn in (("paymentTerms", client.list_payment_terms),
                      ("locations", client.list_locations)):
        try:
            rows = fn()
            print(f"{label}: OK, {len(rows)} rows")
            for r in rows[:5]:
                print(f"  {r.get('code'):16} {r.get('displayName')}")
        except Exception as e:
            print(f"{label}: FAILED — {e}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
