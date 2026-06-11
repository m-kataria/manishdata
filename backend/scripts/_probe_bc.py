"""One-off: confirm legacy Sales Price endpoint now returns ICC pricing."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from app.config import Config

tenant = Config.BC_TENANT_ID
company = Config.BC_COMPANY_ID
tok = requests.post(
    f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
    data={
        "grant_type": "client_credentials",
        "client_id": Config.BC_CLIENT_ID,
        "client_secret": Config.BC_CLIENT_SECRET,
        "scope": "https://api.businesscentral.dynamics.com/.default",
    },
).json()["access_token"]
hdr = {"Authorization": f"Bearer {tok}"}
base = f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/Production"


def get(path):
    r = requests.get(f"{base}{path}", headers=hdr, timeout=30)
    return r.status_code, (r.json() if r.status_code < 400 else r.text[:400])


print("=== salesPrices (new legacy endpoint) ===")
s, j = get(f"/api/nrv/icc/v1.0/companies({company})/salesPrices?$top=20")
print(f"  HTTP {s}, rows: {len(j.get('value', [])) if isinstance(j, dict) else 'N/A'}")
if isinstance(j, dict) and j.get("value"):
    for row in j["value"][:8]:
        print(
            f"  group={row['customerPriceGroup']:15} item={row['itemNo']:15} "
            f"variant={row.get('variantCode',''):8} ${row['unitPrice']} {row.get('currencyCode','')} "
            f"uom={row.get('unitOfMeasureCode','')}"
        )
elif isinstance(j, str):
    print(f"  error body: {j}")

print("\n=== items that actually have salesPrices ===")
s, j = get(f"/api/nrv/icc/v1.0/companies({company})/salesPrices?$top=100&$select=itemNo")
if isinstance(j, dict) and j.get("value"):
    items_with_prices = sorted({r["itemNo"] for r in j["value"]})
    print(f"  distinct items with pricing: {len(items_with_prices)}")
    print(f"  first few: {items_with_prices[:10]}")
