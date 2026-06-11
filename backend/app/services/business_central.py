"""Business Central OAuth 2.0 + OData v4 client.

OAuth client credentials (S2S) flow via MSAL. All BC URLs follow the v2.0 API pattern:
  https://api.businesscentral.dynamics.com/v2.0/{tenant}/{env}/api/v2.0/companies({id})/{entity}

Real BC tenants need an Entra ID app registration with the scope
  https://api.businesscentral.dynamics.com/.default
and the corresponding BC user "App Access Control" entry pointing at the app's client ID.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class BusinessCentralError(RuntimeError):
    pass


class BusinessCentralClient:
    SCOPE = "https://api.businesscentral.dynamics.com/.default"
    BASE = "https://api.businesscentral.dynamics.com/v2.0"
    NRV_API_ROUTE = "/api/nrv/icc/v1.0"

    # When credential values start with this prefix, we treat them as placeholders.
    PLACEHOLDER_PREFIXES = ("demo-", "your-", "xxx", "placeholder", "REPLACE", "")

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        environment: str,
        company_id: str,
        mock_mode: str = "auto",
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.environment = environment
        self.company_id = company_id
        self.mock_mode = mock_mode
        self._token: str | None = None

    def _is_placeholder(self, value: str) -> bool:
        v = (value or "").strip().lower()
        if not v:
            return True
        return any(v.startswith(p.lower()) for p in self.PLACEHOLDER_PREFIXES if p)

    def use_mock(self) -> bool:
        if self.mock_mode == "on":
            return True
        if self.mock_mode == "off":
            return False
        # auto
        return any(
            self._is_placeholder(v)
            for v in (self.tenant_id, self.client_id, self.client_secret)
        )

    # --- helpers -------------------------------------------------------------

    def _credentials_present(self) -> bool:
        return all(
            [self.tenant_id, self.client_id, self.client_secret, self.environment]
        )

    def _get_token(self) -> str:
        if self._token:
            return self._token
        if not self._credentials_present():
            raise BusinessCentralError("BC credentials not configured")

        # Lazy import so the package isn't required for the app to boot.
        import msal

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority,
        )
        result = app.acquire_token_for_client(scopes=[self.SCOPE])
        if "access_token" not in result:
            raise BusinessCentralError(
                f"Token request failed: {result.get('error_description') or result}"
            )
        self._token = result["access_token"]
        return self._token

    def _url(self, entity: str, query: str = "") -> str:
        if not self.company_id:
            raise BusinessCentralError("BC_COMPANY_ID not configured")
        suffix = f"?{query}" if query else ""
        return (
            f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
            f"/companies({self.company_id})/{entity}{suffix}"
        )

    def _get(self, entity: str, query: str = "") -> list[dict[str, Any]]:
        token = self._get_token()
        url = self._url(entity, query)
        res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
        if res.status_code >= 400:
            raise BusinessCentralError(f"GET {entity} failed: {res.status_code} {res.text[:200]}")
        return res.json().get("value", [])

    def _post(self, entity: str, payload: dict[str, Any]) -> dict[str, Any]:
        token = self._get_token()
        url = self._url(entity)
        res = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        if res.status_code >= 400:
            raise BusinessCentralError(f"POST {entity} failed: {res.status_code} {res.text[:200]}")
        return res.json()

    # --- public API ----------------------------------------------------------

    def ping(self) -> dict[str, Any]:
        """Returns connection status without raising. Used by the integrations page."""
        if not self._credentials_present():
            return {
                "connected": False,
                "reason": "credentials_missing",
                "message": "Set BC_TENANT_ID, BC_CLIENT_ID, BC_CLIENT_SECRET, BC_ENVIRONMENT in .env",
            }
        try:
            self._get_token()
        except Exception as e:
            return {"connected": False, "reason": "auth_failed", "message": str(e)}

        if not self.company_id:
            return {
                "connected": True,
                "reason": "no_company_selected",
                "message": "Token acquired but BC_COMPANY_ID not set; data calls will fail",
            }
        try:
            companies = requests.get(
                f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0/companies",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=10,
            )
            companies.raise_for_status()
        except Exception as e:
            return {"connected": False, "reason": "api_unreachable", "message": str(e)}

        return {
            "connected": True,
            "tenant": self.tenant_id,
            "environment": self.environment,
            "companyId": self.company_id,
        }

    def get_customers(self, top: int = 100) -> list[dict[str, Any]]:
        return self._get("customers", f"$top={top}")

    def get_sales_orders(self, top: int = 100) -> list[dict[str, Any]]:
        return self._get("salesOrders", f"$top={top}")

    def get_inventory_items(self, top: int = 100) -> list[dict[str, Any]]:
        return self._get("items", f"$top={top}")

    def post_sales_order(self, customer_id: str, external_doc_no: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"customerId": customer_id}
        if external_doc_no:
            payload["externalDocumentNumber"] = external_doc_no
        return self._post("salesOrders", payload)

    # --- Custom NRV API helpers (require the NRV ICC Lookup AL extension) ----

    def _nrv_url(self, entity: str, query: str = "") -> str:
        if not self.company_id:
            raise BusinessCentralError("BC_COMPANY_ID not configured")
        suffix = f"?{query}" if query else ""
        return (
            f"{self.BASE}/{self.tenant_id}/{self.environment}{self.NRV_API_ROUTE}"
            f"/companies({self.company_id})/{entity}{suffix}"
        )

    def _nrv_get(self, entity: str, query: str = "") -> list[dict[str, Any]]:
        token = self._get_token()
        res = requests.get(
            self._nrv_url(entity, query),
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        if res.status_code >= 400:
            raise BusinessCentralError(
                f"NRV GET {entity} failed: {res.status_code} {res.text[:200]}"
            )
        rows = res.json().get("value", [])
        # Alias systemId → id so NRV custom endpoints look the same as standard
        # BC api/v2.0 to frontend code.
        for row in rows:
            if "systemId" in row and "id" not in row:
                row["id"] = row["systemId"]
        return rows

    def list_sku_inventory(
        self,
        q: str = "",
        location: str = "",
        top: int = 500,
    ) -> list[dict[str, Any]]:
        """Flat SKU listing mirroring BC's Stockkeeping Units page.

        Each row = one SKU (item × variant × location). Joined with Item.displayName for
        the item description column and Item Variant.description for the variant
        description column. Sorted by inventory descending.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_sku_inventory_flat(q=q, location=location, top=top)

        # 1. Fetch SKUs (NRV custom).
        # BC's contains() filter is slow (~5s per call) and OR across distinct fields
        # is rejected. Fastest path: pull a wide unfiltered set ONCE (~1.5s), then
        # filter/sort in Python. Server-side filter only when narrowing by location,
        # which is a single-field equality (cheap).
        needs_python_search = bool(q)
        # Search needs a wider net; cap at 1000 to keep BC roundtrip under ~5s.
        fetch_top = max(top, 1000) if needs_python_search else top

        query_parts = [f"$top={fetch_top}"]
        if location:
            loc = location.replace(chr(39), chr(39) + chr(39))
            query_parts.insert(0, f"$filter=locationCode eq '{loc}'")
        if not needs_python_search:
            # Default sort: alphabetical by item number then variant code.
            # The frontend lets the user toggle inventory sort client-side.
            query_parts.append("$orderby=itemNo,variantCode")

        skus = self._nrv_get("skuInventory", "&".join(query_parts))

        if needs_python_search:
            term = q.lower()
            skus = [
                s
                for s in skus
                if term in (s.get("itemNo") or "").lower()
                or term in (s.get("variantCode") or "").lower()
                or term in (s.get("description") or "").lower()
            ]
            skus.sort(key=lambda r: ((r.get("itemNo") or ""), (r.get("variantCode") or "")))
            skus = skus[:top]

        if not skus:
            return []

        # 2. Batch lookup item displayName + UoM and itemVariants for description joins.
        # BC OData doesn't support `in (...)`; use chained `or` clauses instead.
        unique_items = sorted({s["itemNo"] for s in skus if s.get("itemNo")})
        item_desc: dict[str, str] = {}
        item_uom: dict[str, str] = {}
        variant_desc: dict[tuple[str, str], str] = {}

        if unique_items:
            esc = lambda n: n.replace(chr(39), chr(39) + chr(39))

            def chunked(seq, size):
                for i in range(0, len(seq), size):
                    yield seq[i : i + size]

            from concurrent.futures import ThreadPoolExecutor

            token = self._get_token()
            session = requests.Session()
            session.headers["Authorization"] = f"Bearer {token}"

            def fetch_items(chunk):
                clause = " or ".join(f"number eq '{esc(n)}'" for n in chunk)
                url = self._url(
                    "items",
                    f"$filter={clause}&$select=number,displayName,baseUnitOfMeasureCode&$top={len(chunk)}",
                )
                r = session.get(url, timeout=20)
                if r.ok:
                    return r.json().get("value", [])
                return []

            def fetch_variants(chunk):
                clause = " or ".join(f"itemNumber eq '{esc(n)}'" for n in chunk)
                url = self._url(
                    "itemVariants",
                    f"$filter={clause}&$select=itemNumber,code,description&$top=2000",
                )
                r = session.get(url, timeout=20)
                if r.ok:
                    return r.json().get("value", [])
                return []

            chunks = list(chunked(unique_items, 30))
            with ThreadPoolExecutor(max_workers=min(8, len(chunks) * 2)) as ex:
                items_futures = [ex.submit(fetch_items, c) for c in chunks]
                vars_futures = [ex.submit(fetch_variants, c) for c in chunks]
                for f in items_futures:
                    for i in f.result():
                        item_desc[i["number"]] = i.get("displayName", "")
                        item_uom[i["number"]] = i.get("baseUnitOfMeasureCode", "")
                for f in vars_futures:
                    for v in f.result():
                        variant_desc[(v["itemNumber"], v["code"])] = v.get("description", "")

        # 4. Merge into output rows
        out: list[dict[str, Any]] = []
        for s in skus:
            item_no = s.get("itemNo", "")
            var_code = s.get("variantCode") or ""
            out.append(
                {
                    "id": s.get("systemId"),
                    "itemNo": item_no,
                    "itemDescription": item_desc.get(item_no, s.get("description", "")),
                    "variantCode": var_code,
                    "variantDescription": variant_desc.get((item_no, var_code), ""),
                    "unitOfMeasure": item_uom.get(item_no, ""),
                    "locationCode": s.get("locationCode", ""),
                    "replenishmentSystem": s.get("replenishmentSystem", ""),
                    "inventory": float(s.get("inventory") or 0),
                    "qtyOnSalesOrder": float(s.get("qtyOnSalesOrder") or 0),
                    "qtyOnPurchOrder": float(s.get("qtyOnPurchOrder") or 0),
                    "reorderPoint": float(s.get("reorderPoint") or 0),
                }
            )
        return out

    def list_items_for_pricing(self, q: str = "") -> list[dict[str, Any]]:
        """Returns lightweight item list for the pricing-page picker.
        BC OData rejects OR across distinct fields, so search is done client-side:
        we pull a wide unfiltered set and filter in Python on number+displayName.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.search_items(q)

        # Without a search term, only show the first 50 items by number to keep
        # the picker fast on initial load.
        if not q:
            items = self._get(
                "items",
                "$top=50&$orderby=number&$select=id,number,displayName,baseUnitOfMeasureCode",
            )
            return [
                {
                    "id": i.get("id"),
                    "number": i.get("number"),
                    "displayName": i.get("displayName"),
                    "baseUnitOfMeasure": i.get("baseUnitOfMeasureCode"),
                    "variantCount": None,
                }
                for i in items
            ]

        # Search path: pull a wide set, filter case-insensitively in Python on
        # both number and displayName, then trim back to 50 matches.
        items = self._get(
            "items",
            "$top=2000&$orderby=number&$select=id,number,displayName,baseUnitOfMeasureCode",
        )
        term = q.lower()
        matched = [
            i
            for i in items
            if term in (i.get("number") or "").lower()
            or term in (i.get("displayName") or "").lower()
        ]
        return [
            {
                "id": i.get("id"),
                "number": i.get("number"),
                "displayName": i.get("displayName"),
                "baseUnitOfMeasure": i.get("baseUnitOfMeasureCode"),
                "variantCount": None,
            }
            for i in matched[:50]
        ]

    def list_sales_quotes(
        self,
        q: str = "",
        status: str = "",
        top: int = 200,
    ) -> list[dict[str, Any]]:
        """Returns recent sales quotes for the current company.

        Optional client-side filter on q (matches number, customerNumber, sellToName)
        and server-side filter on status (Draft/Open/Released/...).
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_sales_quotes(q=q, status=status, top=top)

        # No $select — BC's salesQuote schema varies (e.g. sellToName doesn't exist
        # on some tenants). Pulling the full payload is fine for the list view since
        # the quote count is typically small.
        parts = [f"$top={top}", "$orderby=documentDate desc"]
        if status:
            esc = status.replace("'", "''")
            parts.insert(0, f"$filter=status eq '{esc}'")
        quotes = self._get("salesQuotes", "&".join(parts))

        if q:
            term = q.lower()
            quotes = [
                qq
                for qq in quotes
                if term in (qq.get("number") or "").lower()
                or term in (qq.get("customerNumber") or "").lower()
                or term in (qq.get("shipToName") or qq.get("customerName") or "").lower()
            ]
        return quotes

    def make_order_from_quote(self, quote_id: str) -> dict[str, Any]:
        """Calls BC's standard `Microsoft.NAV.makeOrder` bound action on a sales quote.
        Robust to BC variants that return:
          - 201 with the new salesOrder JSON body
          - 204 No Content with a Location header pointing to the new order
          - 200 with empty body (some BC versions)
        """
        if self.use_mock():
            raise BusinessCentralError("Make Order requires live BC connection")
        token = self._get_token()
        url = self._url(f"salesQuotes({quote_id})/Microsoft.NAV.makeOrder")
        res = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"makeOrder failed: {res.status_code} {res.text[:300]}"
            )

        # 1. If BC returned the order entity inline, use it.
        if res.content:
            try:
                payload = res.json()
                if isinstance(payload, dict) and payload.get("number"):
                    return payload
            except Exception:
                pass

        # 2. If Location header is present, dereference it.
        location = res.headers.get("Location") or res.headers.get("location") or ""
        if location:
            try:
                loc_res = requests.get(
                    location,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=20,
                )
                if loc_res.ok and loc_res.content:
                    return loc_res.json()
            except Exception:
                pass

        # 3. Fall back: find the salesOrder that was most recently created.
        #    BC creates it within the same transaction so the newest entry by
        #    lastModifiedDateTime is almost certainly the right one.
        try:
            recent = self._get(
                "salesOrders",
                "$top=1&$orderby=lastModifiedDateTime desc",
            )
            if recent:
                return recent[0]
        except Exception:
            pass

        # Truly nothing returned — but conversion likely happened.
        return {
            "id": "",
            "number": "",
            "message": "Order created in BC but the new order details were not returned by the API. Check the Orders tab.",
        }

    def create_sales_quote(
        self, customer_id: str, document_date: str | None = None
    ) -> dict[str, Any]:
        """POST to standard /salesQuotes — returns the created draft quote header."""
        if self.use_mock():
            raise BusinessCentralError("Quote creation requires live BC connection")
        token = self._get_token()
        url = self._url("salesQuotes")
        payload: dict[str, Any] = {"customerId": customer_id}
        if document_date:
            payload["documentDate"] = document_date
        res = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"POST salesQuotes failed: {res.status_code} {res.text[:300]}"
            )
        return res.json()

    def list_quote_lines(self, document_number: str) -> list[dict[str, Any]]:
        """Lines for one quote via NRV custom endpoint (includes qtyToAssembleToOrder)."""
        if self.use_mock():
            return []
        esc = document_number.replace("'", "''")
        return self._nrv_get(
            "salesQuoteLines",
            f"$filter=documentNumber eq '{esc}'&$orderby=lineNo",
        )

    def create_quote_line(
        self, document_number: str, line: dict[str, Any]
    ) -> dict[str, Any]:
        if self.use_mock():
            raise BusinessCentralError("Quote line ops require live BC connection")
        token = self._get_token()
        url = self._nrv_url("salesQuoteLines")
        payload: dict[str, Any] = {"documentNumber": document_number}
        for k in (
            "lineType", "itemNo", "variantCode", "locationCode",
            "description", "quantity", "qtyToAssembleToOrder",
            "unitOfMeasureCode", "unitPrice", "lineDiscountPct",
        ):
            if k in line and line[k] not in (None, ""):
                payload[k] = line[k]
        # Default lineType to Item if itemNo provided and lineType missing
        if "itemNo" in payload and "lineType" not in payload:
            payload["lineType"] = "Item"
        res = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"POST quote line failed: {res.status_code} {res.text[:300]}"
            )
        return res.json()

    def update_quote_line(self, line_system_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        if self.use_mock():
            raise BusinessCentralError("Quote line ops require live BC connection")
        token = self._get_token()
        url = self._nrv_url(f"salesQuoteLines({line_system_id})")
        res = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "If-Match": "*",
            },
            json=patch,
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"PATCH quote line failed: {res.status_code} {res.text[:300]}"
            )
        return res.json() if res.text else {}

    def delete_quote_line(self, line_system_id: str) -> None:
        if self.use_mock():
            return
        token = self._get_token()
        url = self._nrv_url(f"salesQuoteLines({line_system_id})")
        res = requests.delete(
            url,
            headers={"Authorization": f"Bearer {token}", "If-Match": "*"},
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"DELETE quote line failed: {res.status_code} {res.text[:300]}"
            )

    def list_ato_lines_for_quote_line(
        self, quote_doc_no: str, line_no: int
    ) -> dict[str, Any]:
        """Returns ATO sub-components for a sales quote line.
        Shape: {'assemblyDocType': '...', 'assemblyDocNo': '...', 'lines': [...]}.
        Empty lines list if no ATO link exists.
        """
        if self.use_mock():
            return {"assemblyDocType": "", "assemblyDocNo": "", "lines": []}
        esc_doc = quote_doc_no.replace("'", "''")
        links = self._nrv_get(
            "atoLinks",
            f"$filter=documentType eq 'Quote' and documentNo eq '{esc_doc}' "
            f"and documentLineNo eq {int(line_no)}",
        )
        if not links:
            return {"assemblyDocType": "", "assemblyDocNo": "", "lines": []}
        link = links[0]
        asm_type = link.get("assemblyDocType", "")
        asm_no = link.get("assemblyDocNo", "")
        if not asm_no:
            return {"assemblyDocType": asm_type, "assemblyDocNo": "", "lines": []}
        esc_asm_no = asm_no.replace("'", "''")
        esc_asm_type = asm_type.replace("'", "''")
        lines = self._nrv_get(
            "assemblyLines",
            f"$filter=documentType eq '{esc_asm_type}' and documentNo eq '{esc_asm_no}'"
            f"&$orderby=lineNo",
        )
        return {
            "assemblyDocType": asm_type,
            "assemblyDocNo": asm_no,
            "lines": lines,
        }

    def add_ato_line(
        self,
        assembly_doc_type: str,
        assembly_doc_no: str,
        line: dict[str, Any],
    ) -> dict[str, Any]:
        if self.use_mock():
            raise BusinessCentralError("ATO line ops require live BC connection")
        token = self._get_token()
        url = self._nrv_url("assemblyLines")
        payload = {
            "documentType": assembly_doc_type,
            "documentNo": assembly_doc_no,
            **{
                k: v
                for k, v in line.items()
                if k in ("lineType", "itemNo", "variantCode", "locationCode",
                         "description", "quantity", "quantityPer", "unitOfMeasureCode")
                and v not in (None, "")
            },
        }
        if "itemNo" in payload and "lineType" not in payload:
            payload["lineType"] = "Item"
        res = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"POST assembly line failed: {res.status_code} {res.text[:300]}"
            )
        return res.json()

    def update_ato_line(self, line_system_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        if self.use_mock():
            raise BusinessCentralError("ATO line ops require live BC connection")
        token = self._get_token()
        url = self._nrv_url(f"assemblyLines({line_system_id})")
        res = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "If-Match": "*",
            },
            json=patch,
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"PATCH assembly line failed: {res.status_code} {res.text[:300]}"
            )
        return res.json() if res.text else {}

    def delete_ato_line(self, line_system_id: str) -> None:
        if self.use_mock():
            return
        token = self._get_token()
        url = self._nrv_url(f"assemblyLines({line_system_id})")
        res = requests.delete(
            url,
            headers={"Authorization": f"Bearer {token}", "If-Match": "*"},
            timeout=20,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"DELETE assembly line failed: {res.status_code} {res.text[:300]}"
            )

    def get_sales_quote(self, quote_id: str) -> dict[str, Any] | None:
        """Returns one sales quote with its line items."""
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.get_sales_quote(quote_id)

        try:
            token = self._get_token()
            base = (
                f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
                f"/companies({self.company_id})/salesQuotes({quote_id})"
            )
            session = requests.Session()
            session.headers["Authorization"] = f"Bearer {token}"
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor(max_workers=2) as ex:
                fq = ex.submit(session.get, base, timeout=20)
                fl = ex.submit(session.get, f"{base}/salesQuoteLines?$top=200", timeout=20)
                q_res = fq.result()
                l_res = fl.result()
            if q_res.status_code == 404:
                return None
            if not q_res.ok:
                raise BusinessCentralError(f"GET quote failed: {q_res.status_code} {q_res.text[:200]}")
            quote = q_res.json()
            quote["lines"] = l_res.json().get("value", []) if l_res.ok else []
            return quote
        except BusinessCentralError:
            raise
        except Exception as e:
            raise BusinessCentralError(str(e))

    def get_sales_quote_pdf(self, quote_id: str) -> tuple[bytes, str]:
        """Streams the BC-rendered Sales Quote PDF. Returns (bytes, filename)."""
        if self.use_mock():
            raise BusinessCentralError("PDF download requires live BC connection")

        token = self._get_token()
        # 1. Get quote metadata for filename + verify it exists
        q_url = (
            f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
            f"/companies({self.company_id})/salesQuotes({quote_id})?$select=number"
        )
        qr = requests.get(q_url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
        if qr.status_code == 404:
            raise BusinessCentralError("Quote not found")
        if not qr.ok:
            raise BusinessCentralError(f"GET quote failed: {qr.status_code}")
        number = qr.json().get("number", quote_id)

        # 2. Stream the rendered PDF
        pdf_url = (
            f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
            f"/companies({self.company_id})/salesQuotes({quote_id})"
            "/pdfDocument/pdfDocumentContent"
        )
        pr = requests.get(
            pdf_url, headers={"Authorization": f"Bearer {token}"}, timeout=90
        )
        if not pr.ok:
            raise BusinessCentralError(
                f"PDF render failed: {pr.status_code} {pr.text[:200]}"
            )
        return pr.content, f"{number}.pdf"

    def list_sales_orders(
        self,
        q: str = "",
        status: str = "",
        top: int = 200,
    ) -> list[dict[str, Any]]:
        """Returns recent sales orders. Default behavior: caller passes status='Open'
        to mirror BC's 'Open Sales Orders' list page."""
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_sales_orders(q=q, status=status, top=top)

        parts = [f"$top={top}", "$orderby=orderDate desc"]
        if status:
            esc = status.replace("'", "''")
            parts.insert(0, f"$filter=status eq '{esc}'")
        orders = self._get("salesOrders", "&".join(parts))

        if q:
            term = q.lower()
            orders = [
                o
                for o in orders
                if term in (o.get("number") or "").lower()
                or term in (o.get("customerNumber") or "").lower()
                or term in (o.get("shipToName") or o.get("customerName") or "").lower()
            ]
        return orders

    def get_sales_order(self, order_id: str) -> dict[str, Any] | None:
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.get_sales_order(order_id)

        try:
            token = self._get_token()
            base = (
                f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
                f"/companies({self.company_id})/salesOrders({order_id})"
            )
            session = requests.Session()
            session.headers["Authorization"] = f"Bearer {token}"
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor(max_workers=2) as ex:
                fo = ex.submit(session.get, base, timeout=20)
                fl = ex.submit(session.get, f"{base}/salesOrderLines?$top=200", timeout=20)
                o_res = fo.result()
                l_res = fl.result()
            if o_res.status_code == 404:
                return None
            if not o_res.ok:
                raise BusinessCentralError(f"GET order failed: {o_res.status_code} {o_res.text[:200]}")
            order = o_res.json()
            order["lines"] = l_res.json().get("value", []) if l_res.ok else []
            return order
        except BusinessCentralError:
            raise
        except Exception as e:
            raise BusinessCentralError(str(e))

    def get_sales_order_pdf(self, order_id: str) -> tuple[bytes, str]:
        if self.use_mock():
            raise BusinessCentralError("PDF download requires live BC connection")

        token = self._get_token()
        meta_url = (
            f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
            f"/companies({self.company_id})/salesOrders({order_id})?$select=number"
        )
        mr = requests.get(meta_url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
        if mr.status_code == 404:
            raise BusinessCentralError("Order not found")
        if not mr.ok:
            raise BusinessCentralError(f"GET order failed: {mr.status_code}")
        number = mr.json().get("number", order_id)

        pdf_url = (
            f"{self.BASE}/{self.tenant_id}/{self.environment}/api/v2.0"
            f"/companies({self.company_id})/salesOrders({order_id})"
            "/pdfDocument/pdfDocumentContent"
        )
        pr = requests.get(
            pdf_url, headers={"Authorization": f"Bearer {token}"}, timeout=90
        )
        if not pr.ok:
            raise BusinessCentralError(
                f"PDF render failed: {pr.status_code} {pr.text[:200]}"
            )
        return pr.content, f"{number}.pdf"

    def list_customers(self, q: str = "", top: int = 200) -> list[dict[str, Any]]:
        """Returns customers. Prefers the NRV custom /customers endpoint (exposes
        Customer Price Group + other card fields the standard api/v2.0 omits).
        Falls back to the standard /customers endpoint if the AL extension version
        with NRV customers isn't installed yet — degrades gracefully without 404.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_customers(q=q, top=top)
        fetch_top = max(top, 1000) if q else top
        # Try NRV custom endpoint first
        try:
            customers = self._nrv_get("customers", f"$top={fetch_top}&$orderby=number")
        except BusinessCentralError as e:
            if "404" in str(e):
                # AL extension v1.0.5.0+ not installed yet — fall back to standard endpoint.
                # Price Group column will be empty until the extension is upgraded.
                customers = self._get("customers", f"$top={fetch_top}&$orderby=number")
            else:
                raise
        if q:
            term = q.lower()
            customers = [
                c
                for c in customers
                if term in (c.get("number") or "").lower()
                or term in (c.get("displayName") or "").lower()
                or term in (c.get("phoneNumber") or "").lower()
                or term in (c.get("email") or "").lower()
            ]
            customers = customers[:top]
        return customers

    def list_customer_templates(self) -> list[dict[str, Any]]:
        """Returns BC customer templates via the NRV custom API."""
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_customer_templates()
        return self._nrv_get("customerTemplates", "$orderby=code")

    def list_dimension_values(self, dimension_code: str) -> list[dict[str, Any]]:
        """Returns the valid values for a given BC dimension (e.g. 'CUST CATEGORY')."""
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_dimension_values(dimension_code)
        if not dimension_code:
            return []
        try:
            escaped = dimension_code.replace("'", "''")
            return self._nrv_get(
                "dimensionValues",
                f"$filter=dimensionCode eq '{escaped}'&$orderby=code",
            )
        except BusinessCentralError as e:
            # Extension not installed yet — degrade gracefully (empty dropdown).
            if "404" in str(e):
                return []
            raise

    def create_customer_from_template(
        self, template_system_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Invokes the bound createCustomer action on the customerTemplates entity.
        BC creates the customer, applies template defaults, then overrides with payload.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.create_customer_from_template(template_system_id, payload)

        token = self._get_token()
        action_url = (
            f"{self.BASE}/{self.tenant_id}/{self.environment}{self.NRV_API_ROUTE}"
            f"/companies({self.company_id})/customerTemplates({template_system_id})"
            "/Microsoft.NAV.createCustomer"
        )
        body = {
            "name": payload.get("name", ""),
            "addressLine1": payload.get("addressLine1", ""),
            "addressLine2": payload.get("addressLine2", ""),
            "city": payload.get("city", ""),
            "county": payload.get("county", ""),
            "postCode": payload.get("postCode", ""),
            "countryRegionCode": payload.get("countryRegionCode", ""),
            "phoneNo": payload.get("phoneNo", ""),
            "email": payload.get("email", ""),
            "contactName": payload.get("contactName", ""),
            "custCategory": payload.get("custCategory", ""),
            "businessType": payload.get("businessType", ""),
        }
        res = requests.post(
            action_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=30,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"createCustomer action failed: {res.status_code} {res.text[:300]}"
            )
        result = res.json()
        created_no = result.get("value") or result.get("CreatedNo") or ""

        new_customer: dict[str, Any] = {}
        if created_no:
            try:
                term = created_no.replace("'", "''")
                rows = self._get("customers", f"$filter=number eq '{term}'&$top=1")
                if rows:
                    new_customer = rows[0]
            except Exception:
                pass
        return {"createdNo": created_no, "customer": new_customer}

    def get_customer_price_groups(self) -> list[dict[str, Any]]:
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.MOCK_PRICE_GROUPS
        return self._nrv_get("customerPriceGroups", "$orderby=code")

    def get_pricing_matrix(self, item_no: str) -> dict[str, Any] | None:
        """For a given item, returns variants × customer-price-groups crosstab.
        Shape:
          { item, priceGroups: [...], variants: [{code, description, prices: [{groupCode, unitPrice, ...}]}] }
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.get_pricing_matrix(item_no)

        # 1. Resolve the item itself (standard endpoint)
        term = item_no.replace("'", "''")
        items = self._get("items", f"$filter=number eq '{term}'&$top=1")
        if not items:
            return None
        item = items[0]

        # 2. Variants (standard endpoint, filtered by parent)
        variants_raw = self._get(
            "itemVariants",
            f"$filter=itemNumber eq '{term}'&$orderby=code",
        )

        # 3. Customer price groups (NRV custom)
        groups = self._nrv_get("customerPriceGroups", "$orderby=code")

        # 4. Try MODERN Price List Line first (only populated if BC tenant has
        #    "New Sales Pricing Experience" enabled).
        prices = self._nrv_get(
            "itemPrices",
            f"$filter=itemNo eq '{term}' and status eq 'Active'",
        )

        # 5. Fall back to LEGACY Sales Price (table 7002) if modern returned nothing.
        #    The legacy endpoint has no 'status' field; otherwise the shape matches.
        if not prices:
            prices = self._nrv_get(
                "salesPrices",
                f"$filter=itemNo eq '{term}'",
            )

        # 5. Build crosstab: for each variant (plus a synthetic 'base' if any non-variant prices)
        #    and each group, find the matching price row.
        variant_codes = [v.get("code", "") for v in variants_raw]
        # If item has no variants, use a single empty-string variant
        if not variant_codes:
            variant_codes = [""]

        def find_price(variant_code: str, group_code: str) -> dict[str, Any] | None:
            return next(
                (
                    p
                    for p in prices
                    if (p.get("variantCode") or "") == variant_code
                    and p.get("customerPriceGroup") == group_code
                ),
                None,
            )

        variants_out: list[dict[str, Any]] = []
        for vc in variant_codes:
            description = next(
                (v.get("description") for v in variants_raw if v.get("code") == vc),
                "Base item" if vc == "" else vc,
            )
            row_prices = []
            for g in groups:
                p = find_price(vc, g["code"])
                row_prices.append(
                    {
                        "groupCode": g["code"],
                        "groupDescription": g.get("description") or g["code"],
                        "unitPrice": float(p["unitPrice"]) if p else None,
                        "currency": (p or {}).get("currencyCode") or "CAD",
                    }
                )
            variants_out.append(
                {
                    "code": vc,
                    "description": description,
                    "prices": row_prices,
                }
            )

        return {
            "item": {
                "id": item.get("id"),
                "number": item.get("number"),
                "displayName": item.get("displayName"),
                "baseUnitOfMeasure": item.get("baseUnitOfMeasureCode"),
            },
            "priceGroups": groups,
            "variants": variants_out,
        }


def build_client_from_config(config) -> BusinessCentralClient:
    return BusinessCentralClient(
        tenant_id=config["BC_TENANT_ID"],
        client_id=config["BC_CLIENT_ID"],
        client_secret=config["BC_CLIENT_SECRET"],
        environment=config["BC_ENVIRONMENT"],
        company_id=config["BC_COMPANY_ID"],
        mock_mode=config.get("BC_MOCK_MODE", "auto"),
    )
