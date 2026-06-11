"""Smoke-test every new v1.0.4.0 endpoint."""

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
nrv = f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/Production/api/nrv/icc/v1.0/companies({company})"


def check(label: str, url: str, params: str = ""):
    full = f"{url}{params}"
    try:
        r = requests.get(full, headers=hdr, timeout=30)
        if r.ok:
            try:
                n = len(r.json().get("value", []))
                print(f"  OK {label:30} HTTP {r.status_code} · {n} row(s)")
            except Exception:
                print(f"  OK {label:30} HTTP {r.status_code} · (non-list)")
        else:
            print(f"  FAIL {label:30} HTTP {r.status_code}")
            print(f"      {r.text[:200]}")
    except Exception as e:
        print(f"  FAIL {label:30} ERROR: {e}")


print("=== NRV custom endpoints ===")
check("customers", f"{nrv}/customers", "?$top=1")
check("customerTemplates", f"{nrv}/customerTemplates")
check("dimensionValues CUST CATEGORY", f"{nrv}/dimensionValues", "?$filter=dimensionCode eq 'CUST CATEGORY'")
check("dimensionValues BUSINESS TYPE", f"{nrv}/dimensionValues", "?$filter=dimensionCode eq 'BUSINESS TYPE'")
check("salesQuoteLines", f"{nrv}/salesQuoteLines", "?$top=1")
check("assemblyLines", f"{nrv}/assemblyLines", "?$top=1")
check("atoLinks", f"{nrv}/atoLinks", "?$top=1")
check("customerPriceGroups", f"{nrv}/customerPriceGroups")
check("skuInventory (existing)", f"{nrv}/skuInventory", "?$top=1")

print()
print("=== Detail check: customers now include dims + price group? ===")
r = requests.get(f"{nrv}/customers?$top=3", headers=hdr, timeout=20).json()
for c in r.get("value", []):
    print(f"  {c.get('number','')[:20]:20} priceGroup={c.get('customerPriceGroup','')!r:20} "
          f"custCategory={c.get('custCategory','')!r:14} businessType={c.get('businessType','')!r}")
