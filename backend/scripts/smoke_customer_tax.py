"""One-off smoke test for the NRV Ops Customer Tax API page.

Confirms the freshly-deployed nrv-ops-customer-tax extension is reachable and
exposes the expected fields. Read-only — does not modify any customer.

Run from backend/ with: python scripts/smoke_customer_tax.py
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # type: ignore
load_dotenv(ROOT / ".env")

from app.services.business_central import BusinessCentralClient, BusinessCentralError  # noqa: E402

import requests  # noqa: E402


def main() -> int:
    client = BusinessCentralClient(
        tenant_id=os.environ["BC_TENANT_ID"],
        client_id=os.environ["BC_CLIENT_ID"],
        client_secret=os.environ["BC_CLIENT_SECRET"],
        environment=os.environ["BC_ENVIRONMENT"],
        company_id=os.environ["BC_COMPANY_ID"],
        mock_mode="off",
    )
    token = client._get_token()
    url = (
        f"{client.BASE}/{client.tenant_id}/{client.environment}"
        f"{client.NRV_OPS_API_ROUTE}/companies({client.company_id})/customerTax?$top=3"
    )
    print(f"GET {url}")
    res = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=30,
    )
    print(f"  status: {res.status_code}")
    if not res.ok:
        print(f"  body  : {res.text[:600]}")
        return 1

    payload = res.json()
    rows = payload.get("value", [])
    print(f"  rows  : {len(rows)}")
    if rows:
        sample = rows[0]
        keys = sorted(sample.keys())
        print(f"  keys  : {keys}")
        for k in ("id", "number", "displayName", "taxLiable", "taxAreaCode", "paymentTermsCode", "locationCode"):
            print(f"    {k:18} = {sample.get(k)!r}")
        missing = [k for k in ("taxLiable", "taxAreaCode", "paymentTermsCode", "locationCode") if k not in sample]
        if missing:
            print(f"  MISSING fields: {missing}")
            return 2
        print("  OK — endpoint exposes taxLiable + taxAreaCode")
    else:
        print("  OK — endpoint responded but returned 0 customer rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
