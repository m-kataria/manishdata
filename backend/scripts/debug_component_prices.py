"""Walks the component-price lookup step-by-step so we can see which step
returns nothing. Edit CUSTOMER_NO and SAMPLE_ITEM_NOS to match a real quote
you're testing on, then run:

    python scripts/debug_component_prices.py
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # type: ignore
load_dotenv(ROOT / ".env")

from app.services.business_central import BusinessCentralClient  # noqa: E402

# >>> EDIT THESE TWO <<<
CUSTOMER_NO = "ICC-CUS-1001"
SAMPLE_ITEM_NOS = ["PIR-PANELS"]  # one or two component itemNos from your ATO bundle


def main() -> int:
    c = BusinessCentralClient(
        tenant_id=os.environ["BC_TENANT_ID"],
        client_id=os.environ["BC_CLIENT_ID"],
        client_secret=os.environ["BC_CLIENT_SECRET"],
        environment=os.environ["BC_ENVIRONMENT"],
        company_id=os.environ["BC_COMPANY_ID"],
        mock_mode="off",
    )

    print(f"\n[1] Customer lookup: {CUSTOMER_NO}")
    term = CUSTOMER_NO.replace("'", "''")
    try:
        rows = c._nrv_get("customers", f"$filter=number eq '{term}'&$top=1")
        print(f"    NRV endpoint OK, {len(rows)} row(s)")
    except Exception as e:
        print(f"    NRV endpoint failed: {e}")
        rows = c._get("customers", f"$filter=number eq '{term}'&$top=1")
        print(f"    Standard endpoint, {len(rows)} row(s)")
    if not rows:
        print("    NO MATCHING CUSTOMER. Check CUSTOMER_NO.")
        return 1
    cust = rows[0]
    pg = cust.get("customerPriceGroup")
    print(f"    customerPriceGroup field: {pg!r}")
    print(f"    all available keys      : {sorted(cust.keys())}")
    if not pg:
        print("\n    >>> Customer has NO price group set in BC. That's why every row is '—'.")
        return 0

    print(f"\n[2] itemPrices for group {pg!r} + first sample item")
    item_no = SAMPLE_ITEM_NOS[0].replace("'", "''")
    pg_esc = pg.replace("'", "''")
    flt = f"itemNo eq '{item_no}' and customerPriceGroup eq '{pg_esc}' and status eq 'Active'"
    try:
        rows = c._nrv_get("itemPrices", f"$filter={flt}")
        print(f"    rows: {len(rows)}")
        for r in rows[:5]:
            print(f"      itemNo={r.get('itemNo')!r} variant={r.get('variantCode')!r} price={r.get('unitPrice')!r} group={r.get('customerPriceGroup')!r}")
    except Exception as e:
        print(f"    itemPrices FAILED: {e}")

    print(f"\n[3] itemPrices for first item, ALL groups (no group filter)")
    flt = f"itemNo eq '{item_no}' and status eq 'Active'"
    try:
        rows = c._nrv_get("itemPrices", f"$filter={flt}")
        print(f"    rows: {len(rows)}")
        groups_seen = sorted({r.get("customerPriceGroup") or "(empty)" for r in rows})
        print(f"    groups in itemPrices for this item: {groups_seen}")
        for r in rows[:5]:
            print(f"      variant={r.get('variantCode')!r} price={r.get('unitPrice')!r} group={r.get('customerPriceGroup')!r}")
    except Exception as e:
        print(f"    FAILED: {e}")

    print(f"\n[4] salesPrices (legacy) for first item")
    try:
        rows = c._nrv_get("salesPrices", f"$filter=itemNo eq '{item_no}'")
        print(f"    rows: {len(rows)}")
        for r in rows[:5]:
            print(f"      variant={r.get('variantCode')!r} price={r.get('unitPrice')!r} group={r.get('customerPriceGroup')!r}")
    except Exception as e:
        print(f"    FAILED: {e}")

    print(f"\n[5] Combined OR-filter test (the actual production query)")
    item_clauses = " or ".join(
        f"itemNo eq '{i.replace(chr(39), chr(39) * 2)}'" for i in SAMPLE_ITEM_NOS
    )
    flt = f"customerPriceGroup eq '{pg_esc}' and ({item_clauses})"
    print(f"    filter: {flt}")
    try:
        rows = c._nrv_get("itemPrices", f"$filter={flt} and status eq 'Active'")
        print(f"    itemPrices rows: {len(rows)}")
        for r in rows[:10]:
            print(f"      itemNo={r.get('itemNo')!r} variant={r.get('variantCode')!r} price={r.get('unitPrice')!r}")
    except Exception as e:
        print(f"    itemPrices OR-filter FAILED: {e}")

    print(f"\n[6] Full client call: get_component_prices()")
    components = [{"itemNo": i, "variantCode": ""} for i in SAMPLE_ITEM_NOS]
    result = c.get_component_prices(CUSTOMER_NO, components)
    print(f"    result: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
