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
    NRV_OPS_API_ROUTE = "/api/nrv/ops/v1.0"

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

    def list_payment_terms(self) -> list[dict[str, Any]]:
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.MOCK_PAYMENT_TERMS
        rows = self._get("paymentTerms", "$orderby=code")
        return [
            {
                "id": r.get("id"),
                "code": r.get("code", ""),
                "displayName": r.get("displayName", ""),
                "dueDateCalculation": r.get("dueDateCalculation", ""),
            }
            for r in rows
        ]

    def list_locations(self) -> list[dict[str, Any]]:
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.MOCK_LOCATIONS
        rows = self._get("locations", "$orderby=code")
        return [
            {
                "id": r.get("id"),
                "code": r.get("code", ""),
                "displayName": r.get("displayName", ""),
            }
            for r in rows
        ]

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

    def get_item_open_orders(
        self,
        item_no: str,
        variant_code: str = "",
        location_code: str = "",
    ) -> dict[str, Any]:
        """For one SKU (item + optional variant + optional location), return the open
        sales orders and open purchase orders that still have quantity outstanding
        (ordered - shipped/received > 0). Used by the inventory page so users can
        click 'On SO' / 'On PO' and see which docs contribute to the count.

        Returns {salesOrders: [...], purchaseOrders: [...]} with each row carrying
        the order number, party name, quantity outstanding, requested/expected date,
        and variant/location codes resolved from GUIDs.
        """
        if self.use_mock():
            return {"salesOrders": [], "purchaseOrders": []}

        token = self._get_token()
        session = requests.Session()
        session.headers["Authorization"] = f"Bearer {token}"

        from concurrent.futures import ThreadPoolExecutor

        # Lookup tables for variant + location code resolution.
        def fetch_variants() -> dict[str, str]:
            esc = item_no.replace(chr(39), chr(39) + chr(39))
            url = self._url(
                "itemVariants",
                f"$filter=itemNumber eq '{esc}'&$select=id,code",
            )
            r = session.get(url, timeout=20)
            return {v["id"]: v.get("code", "") for v in r.json().get("value", [])} if r.ok else {}

        def fetch_locations() -> dict[str, str]:
            r = session.get(self._url("locations", "$select=id,code"), timeout=20)
            return {l["id"]: l.get("code", "") for l in r.json().get("value", [])} if r.ok else {}

        def fetch_sales() -> list[dict[str, Any]]:
            r = session.get(
                self._url(
                    "salesOrders",
                    "$expand=salesOrderLines"
                    "&$select=number,customerName,customerNumber,status,orderDate,requestedDeliveryDate"
                    "&$top=500",
                ),
                timeout=60,
            )
            return r.json().get("value", []) if r.ok else []

        def fetch_purch() -> list[dict[str, Any]]:
            r = session.get(
                self._url(
                    "purchaseOrders",
                    "$expand=purchaseOrderLines"
                    "&$select=number,vendorName,vendorNumber,status,orderDate"
                    "&$top=500",
                ),
                timeout=60,
            )
            return r.json().get("value", []) if r.ok else []

        with ThreadPoolExecutor(max_workers=4) as ex:
            f_vars = ex.submit(fetch_variants)
            f_locs = ex.submit(fetch_locations)
            f_so = ex.submit(fetch_sales)
            f_po = ex.submit(fetch_purch)
            variant_code_by_id = f_vars.result()
            location_code_by_id = f_locs.result()
            sales = f_so.result()
            purch = f_po.result()

        want_variant = (variant_code or "").strip()
        want_location = (location_code or "").strip()

        out_so: list[dict[str, Any]] = []
        for so in sales:
            for line in (so.get("salesOrderLines") or []):
                if (line.get("lineObjectNumber") or "") != item_no:
                    continue
                line_variant = variant_code_by_id.get(line.get("itemVariantId") or "", "")
                line_location = location_code_by_id.get(line.get("locationId") or "", "")
                if want_variant and line_variant != want_variant:
                    continue
                if want_location and line_location != want_location:
                    continue
                qty = float(line.get("quantity") or 0)
                shipped = float(line.get("shippedQuantity") or 0)
                outstanding = qty - shipped
                if outstanding <= 0:
                    continue
                requested = so.get("requestedDeliveryDate") or ""
                if (not requested) or requested.startswith("0001"):
                    requested = line.get("shipmentDate") or ""
                out_so.append({
                    "orderNumber": so.get("number"),
                    "customerNumber": so.get("customerNumber"),
                    "customerName": so.get("customerName"),
                    "status": so.get("status"),
                    "orderDate": so.get("orderDate"),
                    "requestedDeliveryDate": requested,
                    "variantCode": variant_code_by_id.get(line.get("itemVariantId") or "", ""),
                    "locationCode": location_code_by_id.get(line.get("locationId") or "", ""),
                    "quantity": qty,
                    "shippedQuantity": shipped,
                    "outstanding": outstanding,
                    "unitOfMeasureCode": line.get("unitOfMeasureCode"),
                })

        out_po: list[dict[str, Any]] = []
        for po in purch:
            for line in (po.get("purchaseOrderLines") or []):
                if (line.get("lineObjectNumber") or "") != item_no:
                    continue
                line_variant = variant_code_by_id.get(line.get("itemVariantId") or "", "")
                line_location = location_code_by_id.get(line.get("locationId") or "", "")
                if want_variant and line_variant != want_variant:
                    continue
                if want_location and line_location != want_location:
                    continue
                qty = float(line.get("quantity") or 0)
                received = float(line.get("receivedQuantity") or 0)
                outstanding = qty - received
                if outstanding <= 0:
                    continue
                out_po.append({
                    "orderNumber": po.get("number"),
                    "vendorNumber": po.get("vendorNumber"),
                    "vendorName": po.get("vendorName"),
                    "status": po.get("status"),
                    "orderDate": po.get("orderDate"),
                    "variantCode": variant_code_by_id.get(line.get("itemVariantId") or "", ""),
                    "locationCode": location_code_by_id.get(line.get("locationId") or "", ""),
                    "quantity": qty,
                    "receivedQuantity": received,
                    "outstanding": outstanding,
                    "unitOfMeasureCode": line.get("unitOfMeasureCode"),
                })

        out_so.sort(key=lambda x: (x.get("orderNumber") or ""))
        out_po.sort(key=lambda x: (x.get("orderNumber") or ""))
        return {"salesOrders": out_so, "purchaseOrders": out_po}

    def list_items_for_pricing(self, q: str = "") -> list[dict[str, Any]]:
        """Returns lightweight item list for the pricing-page picker.
        BC OData rejects OR across distinct fields, so search is done client-side:
        we pull a wide unfiltered set and filter in Python on number+displayName.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.search_items(q)

        # Without a search term, show the first 1000 items by number. Users
        # searching for items beyond this window should use the search box.
        if not q:
            items = self._get(
                "items",
                "$top=1000&$orderby=number&$select=id,number,displayName,baseUnitOfMeasureCode",
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
        # both number and displayName. Return all matches (cap at 500 for UI sanity).
        items = self._get(
            "items",
            "$top=10000&$orderby=number&$select=id,number,displayName,baseUnitOfMeasureCode",
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
            for i in matched[:500]
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

    def get_sales_quote_by_number(self, number: str) -> dict[str, Any] | None:
        """Fetch a single sales quote header by its document number (e.g. SQ1000081)."""
        if self.use_mock():
            from . import _bc_mock
            quotes = _bc_mock.list_sales_quotes(q=number, status="", top=1)
            return quotes[0] if quotes else None
        esc = number.replace("'", "''")
        rows = self._get("salesQuotes", f"$filter=number eq '{esc}'&$top=1")
        return rows[0] if rows else None

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
        self,
        customer_id: str,
        document_date: str | None = None,
        valid_until: str | None = None,
    ) -> dict[str, Any]:
        """POST to standard /salesQuotes — returns the created draft quote header."""
        if self.use_mock():
            raise BusinessCentralError("Quote creation requires live BC connection")
        token = self._get_token()
        url = self._url("salesQuotes")
        payload: dict[str, Any] = {"customerId": customer_id}
        if document_date:
            payload["documentDate"] = document_date
        if valid_until:
            payload["validUntilDate"] = valid_until
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
        # NRV's salesQuoteLines POST does not auto-assign lineNo, so without one
        # BC defaults to 0 and fails on the second insert with
        # Internal_EntityWithSameKeyExists. Compute the next lineNo client-side
        # using BC's standard 10000-step. Callers in tight loops can skip the
        # extra list call by passing 'lineNo' on `line` directly.
        if "lineNo" not in payload:
            if "lineNo" in line and line["lineNo"]:
                payload["lineNo"] = line["lineNo"]
            else:
                try:
                    existing = self.list_quote_lines(document_number)
                    next_no = max((int(l.get("lineNo") or 0) for l in existing), default=0) + 10000
                    payload["lineNo"] = next_no
                except BusinessCentralError:
                    payload["lineNo"] = 10000
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

    def clone_quote_lines(self, source_no: str, dest_no: str) -> dict[str, Any]:
        """Replicate every sales-quote line from source_no into dest_no, including
        ATO assembly components. For each source line:
          1. Create the dest line with ATA=0 so BC doesn't auto-create an
             assembly order with the item's BOM defaults.
          2. If the source line had ATA>0, set ATA on the dest line — BC then
             creates an assembly order populated with BOM defaults.
          3. Wipe those defaults and replace with the source's actual ATO
             components so the destination matches the source exactly.

        Returns a small report: { lines_copied, ato_lines_copied, warnings }.
        """
        if self.use_mock():
            raise BusinessCentralError("Copy requires live BC connection")

        from concurrent.futures import ThreadPoolExecutor, as_completed

        source_lines = self.list_quote_lines(source_no)
        if not source_lines:
            return {"lines_copied": 0, "ato_lines_copied": 0, "warnings": []}

        warnings: list[str] = []
        ato_copied = 0
        created_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []

        # Precompute the starting lineNo on the destination so we don't refetch
        # existing lines before every insert (one BC call instead of N).
        try:
            existing_dest = self.list_quote_lines(dest_no)
            next_line_no = max(
                (int(l.get("lineNo") or 0) for l in existing_dest), default=0
            ) + 10000
        except BusinessCentralError:
            next_line_no = 10000

        for src in source_lines:
            payload: dict[str, Any] = {
                "lineType": src.get("lineType") or "Item",
                "qtyToAssembleToOrder": 0,
                "lineNo": next_line_no,
            }
            next_line_no += 10000
            for k in ("itemNo", "variantCode", "locationCode", "description",
                     "quantity", "unitOfMeasureCode", "unitPrice", "lineDiscountPct"):
                v = src.get(k)
                if v not in (None, ""):
                    payload[k] = v
            try:
                dest = self.create_quote_line(dest_no, payload)
                created_pairs.append((src, dest))
            except BusinessCentralError as e:
                warnings.append(
                    f"line item={src.get('itemNo','?')} lineNo={src.get('lineNo','?')}: {e}"
                )

        for src, dest in created_pairs:
            src_ata = src.get("qtyToAssembleToOrder") or 0
            if not src_ata or src_ata <= 0:
                continue
            try:
                self.update_quote_line(
                    dest["systemId"], {"qtyToAssembleToOrder": src_ata}
                )
            except BusinessCentralError as e:
                warnings.append(
                    f"PATCH ATA on dest line {dest.get('itemNo')}: {e}"
                )
                continue

            src_ato = self.list_ato_lines_for_quote_line(source_no, src["lineNo"])
            src_components = src_ato.get("lines") or []
            if not src_components:
                continue

            dest_ato = self.list_ato_lines_for_quote_line(dest_no, dest["lineNo"])
            asm_type = dest_ato.get("assemblyDocType")
            asm_no = dest_ato.get("assemblyDocNo")
            if not asm_type or not asm_no:
                warnings.append(
                    f"dest line {dest.get('itemNo')}: no assembly order created"
                )
                continue

            # Wipe BOM defaults in parallel. delete_ato_line is independent per id.
            defaults = dest_ato.get("lines") or []
            if defaults:
                def _delete(line_id: str) -> Exception | None:
                    try:
                        self.delete_ato_line(line_id)
                        return None
                    except Exception as e:
                        try:
                            self.update_ato_line(line_id, {"quantityPer": 0})
                            return None
                        except Exception as e2:
                            return e2
                with ThreadPoolExecutor(max_workers=8) as ex:
                    list(ex.map(_delete, [d["systemId"] for d in defaults]))

            # Pre-assign lineNos for the new components so we can POST them in
            # parallel (BC defaults lineNo to 0, which collides on concurrent inserts).
            comp_payloads: list[dict[str, Any]] = []
            for idx, sl in enumerate(src_components):
                comp_payloads.append({
                    "itemNo": sl.get("itemNo"),
                    "variantCode": sl.get("variantCode") or "",
                    "locationCode": sl.get("locationCode") or "",
                    "description": sl.get("description"),
                    "quantityPer": sl.get("quantityPer"),
                    "unitOfMeasureCode": sl.get("unitOfMeasureCode"),
                    "lineType": sl.get("lineType") or "Item",
                    "lineNo": (idx + 1) * 10000,
                })

            def _add(payload: dict[str, Any]) -> tuple[str | None, str | None]:
                try:
                    self.add_ato_line(asm_type, asm_no, payload)
                    return (None, None)
                except Exception as e:
                    return (payload.get("itemNo"), str(e))

            with ThreadPoolExecutor(max_workers=8) as ex:
                for item_no, err in ex.map(_add, comp_payloads):
                    if err:
                        warnings.append(f"ATO component item={item_no}: {err}")
                    else:
                        ato_copied += 1

        return {
            "lines_copied": len(created_pairs),
            "ato_lines_copied": ato_copied,
            "warnings": warnings,
        }

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
        # BC treats 'quantity' as read-only on both POST and PATCH for this endpoint —
        # it is computed from quantityPer × parent sales line quantity. The writable
        # field is 'quantityPer'. Sales quotes here all have parent qty=1, so a
        # caller-supplied 'quantity' maps 1:1 to quantityPer.
        incoming = dict(line)
        if "quantityPer" not in incoming and "quantity" in incoming:
            incoming["quantityPer"] = incoming["quantity"]
        payload = {
            "documentType": assembly_doc_type,
            "documentNo": assembly_doc_no,
            **{
                k: v
                for k, v in incoming.items()
                if k in ("lineType", "itemNo", "variantCode", "locationCode",
                         "description", "quantityPer", "unitOfMeasureCode")
                and v not in (None, "")
            },
        }
        if "itemNo" in payload and "lineType" not in payload:
            payload["lineType"] = "Item"
        # NRV's assemblyLines POST does not auto-assign lineNo; without one BC
        # defaults to 0 and fails on the second insert with
        # Internal_EntityWithSameKeyExists. Mirror the salesQuoteLines fix.
        # Hot-loop callers can supply 'lineNo' on `line` to skip the list call.
        if incoming.get("lineNo"):
            payload["lineNo"] = incoming["lineNo"]
        else:
            try:
                existing = self._nrv_get(
                    "assemblyLines",
                    f"$filter=documentType eq '{assembly_doc_type}' and documentNo eq '{assembly_doc_no.replace(chr(39), chr(39) * 2)}'",
                )
                next_no = max((int(l.get("lineNo") or 0) for l in existing), default=0) + 10000
                payload["lineNo"] = next_no
            except BusinessCentralError:
                payload["lineNo"] = 10000
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
        # BC's assemblyLines treats 'quantity' as read-only; quantityPer is the
        # writable field. Translate so callers that send {quantity: N} still work.
        body = dict(patch)
        if "quantity" in body and "quantityPer" not in body:
            body["quantityPer"] = body.pop("quantity")
        else:
            body.pop("quantity", None)
        res = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "If-Match": "*",
            },
            json=body,
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
        logger.info("DELETE assembly line url=%s", url)
        res = requests.delete(
            url,
            headers={"Authorization": f"Bearer {token}", "If-Match": "*"},
            timeout=20,
        )
        if not res.ok:
            logger.warning(
                "DELETE assembly line failed status=%s body=%s url=%s",
                res.status_code,
                res.text[:1000],
                url,
            )
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

    def get_customer_by_number(self, number: str) -> dict[str, Any] | None:
        """Fetch a single customer (with NRV custom fields) by its number."""
        if self.use_mock():
            from . import _bc_mock
            customers = _bc_mock.list_customers(q=number, top=1)
            return customers[0] if customers else None
        esc = number.replace("'", "''")
        try:
            rows = self._nrv_get("customers", f"$filter=number eq '{esc}'&$top=1")
        except BusinessCentralError as e:
            if "404" in str(e):
                rows = self._get("customers", f"$filter=number eq '{esc}'&$top=1")
            else:
                raise
        return rows[0] if rows else None

    def update_customer(self, system_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        """PATCH a customer via the NRV custom endpoint. Falls back to standard
        api/v2.0 if NRV returns 404 (older AL extension)."""
        if self.use_mock():
            raise BusinessCentralError("Customer edits require live BC connection")
        token = self._get_token()
        url = self._nrv_url(f"customers({system_id})")
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
        if res.status_code == 404:
            std_url = self._url(f"customers({system_id})")
            res = requests.patch(
                std_url,
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
                f"PATCH customer failed: {res.status_code} {res.text[:300]}"
            )
        return res.json() if res.text else {}

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

        tax_area = (payload.get("taxAreaCode") or "").strip()
        payment_terms = (payload.get("paymentTermsCode") or "").strip()
        location = (payload.get("locationCode") or "").strip()
        tax_liable_raw = payload.get("taxLiable")
        tax_liable_provided = tax_liable_raw is not None
        tax_liable = bool(tax_liable_raw)
        customer_system_id = new_customer.get("id") if new_customer else None
        if customer_system_id and (
            tax_area or payment_terms or location or tax_liable_provided
        ):
            try:
                self._patch_customer_extras(
                    customer_system_id,
                    tax_area_code=tax_area,
                    tax_liable=tax_liable,
                    tax_liable_provided=tax_liable_provided,
                    payment_terms_code=payment_terms,
                    location_code=location,
                    token=token,
                )
                try:
                    term = created_no.replace("'", "''")
                    rows = self._get("customers", f"$filter=number eq '{term}'&$top=1")
                    if rows:
                        new_customer = rows[0]
                except Exception:
                    pass
            except BusinessCentralError as e:
                logger.warning(
                    "Customer %s created but customerTax PATCH failed (extension installed?): %s",
                    created_no,
                    e,
                )

        return {"createdNo": created_no, "customer": new_customer}

    def _patch_customer_extras(
        self,
        customer_system_id: str,
        *,
        tax_area_code: str = "",
        tax_liable: bool = False,
        tax_liable_provided: bool = False,
        payment_terms_code: str = "",
        location_code: str = "",
        token: str | None = None,
    ) -> None:
        """PATCH the nrv-ops customerTax API page to set any combination of
        Tax Liable, Tax Area Code, Payment Terms Code, and Location Code on
        an existing Customer. Only non-empty / explicitly-provided fields are
        included in the body so we never overwrite template defaults blindly.
        """
        body: dict[str, Any] = {}
        if tax_liable_provided:
            body["taxLiable"] = tax_liable
        if tax_area_code:
            body["taxAreaCode"] = tax_area_code
        if payment_terms_code:
            body["paymentTermsCode"] = payment_terms_code
        if location_code:
            body["locationCode"] = location_code
        if not body:
            return

        if token is None:
            token = self._get_token()
        url = (
            f"{self.BASE}/{self.tenant_id}/{self.environment}{self.NRV_OPS_API_ROUTE}"
            f"/companies({self.company_id})/customerTax({customer_system_id})"
        )
        res = requests.patch(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "If-Match": "*",
            },
            json=body,
            timeout=30,
        )
        if not res.ok:
            raise BusinessCentralError(
                f"customerTax PATCH failed: {res.status_code} {res.text[:300]}"
            )

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

        # 3b. SKU inventory rows for this item (NRV custom). One row per
        #     (variant × location); sum across locations to get on-hand per variant.
        sku_rows = self._nrv_get(
            "skuInventory",
            f"$filter=itemNo eq '{term}'",
        )
        inv_by_variant: dict[str, float] = {}
        for s in sku_rows:
            vc = s.get("variantCode") or ""
            inv_by_variant[vc] = inv_by_variant.get(vc, 0.0) + float(s.get("inventory") or 0)

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
                    "inventory": inv_by_variant.get(vc) if vc in inv_by_variant else None,
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


    def list_variant_pricing_rows(
        self, q: str = "", location: str = "", top: int = 2000
    ) -> dict[str, Any]:
        """Flat list of (item × variant × location) rows with prices across all
        customer price groups. Mirrors the inventory page shape so users can see
        per-location stock alongside the group prices.
        Returns { priceGroups: [...], rows: [...], locations: [...] }.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.list_variant_pricing_rows(q=q, location=location, top=top)

        # 1. SKU rows (item × variant × location) with descriptions already joined.
        # Don't forward q to the SKU layer so variantDescription is also searchable;
        # we re-apply the filter at row-build time.
        skus = self.list_sku_inventory(q="", location=location, top=top)
        if not skus:
            return {"priceGroups": [], "rows": [], "locations": []}

        # 2. Customer price groups (column headers).
        groups = self._nrv_get("customerPriceGroups", "$orderby=code")

        # 3. Prices for just the items in scope. Chunk OR-clauses to keep URLs sane.
        unique_items = sorted({(s.get("itemNo") or "") for s in skus if s.get("itemNo")})
        esc = lambda n: n.replace(chr(39), chr(39) + chr(39))
        CHUNK = 80

        def fetch_chunk(endpoint: str, has_status: bool, chunk: list[str]) -> list[dict[str, Any]]:
            if not chunk:
                return []
            ors = " or ".join(f"itemNo eq '{esc(n)}'" for n in chunk)
            filt = f"({ors})"
            if has_status:
                filt = f"{filt} and status eq 'Active'"
            return self._nrv_get(endpoint, f"$filter={filt}")

        prices: list[dict[str, Any]] = []
        for i in range(0, len(unique_items), CHUNK):
            prices.extend(fetch_chunk("itemPrices", True, unique_items[i : i + CHUNK]))
        if not prices:
            for i in range(0, len(unique_items), CHUNK):
                prices.extend(fetch_chunk("salesPrices", False, unique_items[i : i + CHUNK]))

        price_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
        for p in prices:
            key = (
                p.get("itemNo") or "",
                p.get("variantCode") or "",
                p.get("customerPriceGroup") or "",
            )
            price_by_key[key] = p

        # 4. Build rows — one per SKU (item × variant × location).
        term = q.lower() if q else ""
        out_rows: list[dict[str, Any]] = []
        for s in skus:
            item_no = s.get("itemNo") or ""
            variant_code = s.get("variantCode") or ""
            location_code = s.get("locationCode") or ""
            item_desc = s.get("itemDescription") or ""
            variant_desc = s.get("variantDescription") or ""
            if term:
                hay = " ".join(
                    [
                        item_no,
                        item_desc,
                        variant_code,
                        variant_desc,
                        location_code,
                    ]
                ).lower()
                if term not in hay:
                    continue
            row_prices = []
            for g in groups:
                p = price_by_key.get((item_no, variant_code, g["code"]))
                row_prices.append(
                    {
                        "groupCode": g["code"],
                        "groupDescription": g.get("description") or g["code"],
                        "unitPrice": float(p["unitPrice"]) if p else None,
                        "currency": (p or {}).get("currencyCode") or "CAD",
                    }
                )
            out_rows.append(
                {
                    "itemNo": item_no,
                    "itemDescription": item_desc,
                    "variantCode": variant_code,
                    "variantDescription": variant_desc,
                    "locationCode": location_code,
                    "unitOfMeasure": s.get("unitOfMeasure") or "",
                    "inventory": float(s.get("inventory") or 0) or None,
                    "qtyOnSalesOrder": float(s.get("qtyOnSalesOrder") or 0),
                    "prices": row_prices,
                }
            )

        out_rows.sort(
            key=lambda r: (r["itemNo"], r["variantCode"], r["locationCode"])
        )
        locations = sorted({r["locationCode"] for r in out_rows if r["locationCode"]})

        return {"priceGroups": groups, "rows": out_rows, "locations": locations}


    def get_component_prices(
        self,
        customer_number: str,
        components: list[dict[str, str]],
    ) -> dict[str, Any]:
        """For a customer + a list of (itemNo, variantCode), returns the
        customer's price group plus a unit price per component looked up from
        itemPrices (modern) or salesPrices (legacy). Used by the ATO modal so
        the user sees what each component would cost for the quote's customer.
        Falls back from variant-specific price to base price if no variant row.
        """
        if self.use_mock():
            from . import _bc_mock
            return _bc_mock.get_component_prices(customer_number, components)

        if not components:
            return {"priceGroup": None, "currency": None, "prices": []}

        term = customer_number.replace("'", "''")
        try:
            customers = self._nrv_get(
                "customers", f"$filter=number eq '{term}'&$top=1"
            )
        except BusinessCentralError as e:
            if "404" in str(e):
                customers = self._get(
                    "customers", f"$filter=number eq '{term}'&$top=1"
                )
            else:
                raise

        empty_prices = [
            {
                "itemNo": c.get("itemNo", ""),
                "variantCode": c.get("variantCode", "") or "",
                "unitPrice": None,
            }
            for c in components
        ]
        if not customers:
            return {"priceGroup": None, "currency": None, "prices": empty_prices}
        price_group = (customers[0].get("customerPriceGroup") or "").strip()
        if not price_group:
            return {"priceGroup": None, "currency": None, "prices": empty_prices}

        unique_items = sorted({c.get("itemNo", "") for c in components if c.get("itemNo")})
        if not unique_items:
            return {"priceGroup": price_group, "currency": None, "prices": empty_prices}

        # Match the established pattern from get_pricing_matrix: filter only by
        # itemNo at the OData layer, then match customerPriceGroup in Python.
        # The NRV AL extension's salesPrices entity does not reliably handle a
        # combined `customerPriceGroup eq 'X' and (itemNo eq 'A' or itemNo eq 'B')`
        # filter — returns 0 rows even when data exists.
        item_clauses = " or ".join(
            f"itemNo eq '{i.replace(chr(39), chr(39) * 2)}'" for i in unique_items
        )
        filter_expr = f"({item_clauses})"

        prices = self._nrv_get(
            "itemPrices", f"$filter={filter_expr} and status eq 'Active'"
        )
        if not prices:
            prices = self._nrv_get("salesPrices", f"$filter={filter_expr}")

        prices = [
            p for p in prices if (p.get("customerPriceGroup") or "") == price_group
        ]

        by_key: dict[tuple[str, str], float] = {}
        for p in prices:
            key = (p.get("itemNo", ""), p.get("variantCode") or "")
            if key in by_key:
                continue
            try:
                by_key[key] = float(p["unitPrice"])
            except (TypeError, ValueError, KeyError):
                pass

        currency = next(
            (p.get("currencyCode") for p in prices if p.get("currencyCode")), None
        )

        out: list[dict[str, Any]] = []
        for c in components:
            item_no = c.get("itemNo", "")
            variant = c.get("variantCode", "") or ""
            unit = by_key.get((item_no, variant))
            if unit is None and variant:
                unit = by_key.get((item_no, ""))
            out.append({"itemNo": item_no, "variantCode": variant, "unitPrice": unit})

        return {"priceGroup": price_group, "currency": currency, "prices": out}


def build_client_from_config(config) -> BusinessCentralClient:
    return BusinessCentralClient(
        tenant_id=config["BC_TENANT_ID"],
        client_id=config["BC_CLIENT_ID"],
        client_secret=config["BC_CLIENT_SECRET"],
        environment=config["BC_ENVIRONMENT"],
        company_id=config["BC_COMPANY_ID"],
        mock_mode=config.get("BC_MOCK_MODE", "auto"),
    )
