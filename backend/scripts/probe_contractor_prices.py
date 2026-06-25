"""Probes itemPrices + salesPrices for the CONTRACTOR customer price group.
No user input needed — answers: does the NRV API expose any prices for this group?

Run: python scripts/probe_contractor_prices.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # type: ignore
load_dotenv(ROOT / ".env")

from app.services.business_central import BusinessCentralClient  # noqa: E402

GROUP = "CONTRACTOR"


def main() -> int:
    c = BusinessCentralClient(
        tenant_id=os.environ["BC_TENANT_ID"],
        client_id=os.environ["BC_CLIENT_ID"],
        client_secret=os.environ["BC_CLIENT_SECRET"],
        environment=os.environ["BC_ENVIRONMENT"],
        company_id=os.environ["BC_COMPANY_ID"],
        mock_mode="off",
    )

    print(f"\n[A] customerPriceGroups — does '{GROUP}' exist?")
    try:
        groups = c._nrv_get("customerPriceGroups", "$orderby=code")
        codes = [g.get("code") for g in groups]
        print(f"    {len(groups)} groups: {codes}")
        if GROUP not in codes:
            close = [c for c in codes if c and GROUP.lower() in c.lower()]
            print(f"    !!! '{GROUP}' NOT in list. Close matches: {close}")
    except Exception as e:
        print(f"    FAILED: {e}")
        return 1

    print(f"\n[B] itemPrices filtered by customerPriceGroup eq '{GROUP}' (modern, top 20)")
    try:
        rows = c._nrv_get(
            "itemPrices",
            f"$filter=customerPriceGroup eq '{GROUP}' and status eq 'Active'&$top=20",
        )
        print(f"    rows: {len(rows)}")
        for r in rows[:10]:
            print(f"      itemNo={r.get('itemNo')!r} variant={r.get('variantCode')!r} price={r.get('unitPrice')!r} status={r.get('status')!r}")
    except Exception as e:
        print(f"    FAILED: {e}")

    print(f"\n[B2] itemPrices same filter WITHOUT status clause (top 20)")
    try:
        rows = c._nrv_get(
            "itemPrices",
            f"$filter=customerPriceGroup eq '{GROUP}'&$top=20",
        )
        print(f"    rows: {len(rows)}")
        for r in rows[:5]:
            print(f"      itemNo={r.get('itemNo')!r} variant={r.get('variantCode')!r} price={r.get('unitPrice')!r} status={r.get('status')!r}")
    except Exception as e:
        print(f"    FAILED: {e}")

    print(f"\n[C] salesPrices (legacy) filtered by customerPriceGroup eq '{GROUP}' (top 20)")
    try:
        rows = c._nrv_get(
            "salesPrices",
            f"$filter=customerPriceGroup eq '{GROUP}'&$top=20",
        )
        print(f"    rows: {len(rows)}")
        for r in rows[:10]:
            print(f"      itemNo={r.get('itemNo')!r} variant={r.get('variantCode')!r} price={r.get('unitPrice')!r}")
    except Exception as e:
        print(f"    FAILED (group filter): {e}")
        print("    Trying without group filter (may not be supported as OData $filter)…")
        try:
            rows = c._nrv_get("salesPrices", "$top=20")
            print(f"    salesPrices top 20 rows (unfiltered): {len(rows)}")
            groups_in_data = sorted({r.get("customerPriceGroup") for r in rows})
            print(f"    customerPriceGroup values in those rows: {groups_in_data}")
            for r in rows[:5]:
                print(f"      itemNo={r.get('itemNo')!r} variant={r.get('variantCode')!r} price={r.get('unitPrice')!r} group={r.get('customerPriceGroup')!r}")
        except Exception as e2:
            print(f"    Unfiltered also failed: {e2}")

    print(f"\n[D] Sample itemPrices unfiltered (top 5) — to see what shape rows have")
    try:
        rows = c._nrv_get("itemPrices", "$top=5")
        for r in rows:
            print(f"    keys: {sorted(r.keys())}")
            print(f"    row : {r}")
            break
    except Exception as e:
        print(f"    FAILED: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
