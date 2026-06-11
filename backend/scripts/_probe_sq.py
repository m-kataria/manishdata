"""Find the correct BC URL to download a sales quote PDF."""

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
base = f"https://api.businesscentral.dynamics.com/v2.0/{tenant}/Production/api/v2.0/companies({company})"

q = requests.get(f"{base}/salesQuotes?$top=1", headers=hdr).json()
qid = q["value"][0]["id"]
print(f"Probing PDF for quote {qid[:8]}...")

# 1. Get the pdfDocument metadata with the mediaReadLink
meta = requests.get(f"{base}/salesQuotes({qid})/pdfDocument", headers=hdr).json()
read_link = meta.get("pdfDocumentContent@odata.mediaReadLink")
print(f"\nmediaReadLink: {read_link}")

# 2. Try the canonical OData media link
for path in [
    f"{base}/salesQuotes({qid})/pdfDocument/pdfDocumentContent",
    f"{base}/salesQuotes({qid})/pdfDocument(pdfDocumentContent)",
    read_link,
]:
    if not path:
        continue
    print(f"\n--- GET {path[:90]}... ---")
    r = requests.get(path, headers=hdr, timeout=60)
    print(f"  HTTP {r.status_code}, content-type={r.headers.get('content-type')}, bytes={len(r.content)}")
    if r.status_code >= 400:
        print(f"  body: {r.text[:200]}")
    elif r.headers.get("content-type", "").startswith("application/pdf"):
        with open("/tmp/test_sq.pdf", "wb") as f:
            f.write(r.content)
        print(f"  PDF saved to /tmp/test_sq.pdf")
        break
