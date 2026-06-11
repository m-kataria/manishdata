"""Mock data for the BC pricing matrix demo. Used when BC_MOCK_MODE resolves to True.

Shape mirrors what the real NRV ICC custom API endpoints return — so swapping mock for
live data requires zero changes in the route or frontend code.
"""

from __future__ import annotations

from typing import Any

MOCK_PRICE_GROUPS: list[dict[str, Any]] = [
    {"code": "CONTRACTOR", "description": "Contractor"},
    {"code": "ENDUSER", "description": "End User"},
    {"code": "WHOLESALE", "description": "Wholesale"},
]

# Each item: number, displayName, baseUoM, variants
MOCK_ITEMS: list[dict[str, Any]] = [
    {
        "id": "item-10001",
        "number": "10001",
        "displayName": "Heat Trace Cable, Self-Regulating",
        "baseUnitOfMeasure": "FT",
        "variants": [
            {"code": "5W", "description": "5 Watts/ft @ 50°F", "_basePrice": 8.50},
            {"code": "8W", "description": "8 Watts/ft @ 50°F", "_basePrice": 12.40},
            {"code": "12W", "description": "12 Watts/ft @ 50°F", "_basePrice": 16.80},
        ],
    },
    {
        "id": "item-10002",
        "number": "10002",
        "displayName": "Pipe Insulation, Fiberglass",
        "baseUnitOfMeasure": "FT",
        "variants": [
            {"code": "1IN", "description": "1 inch wall thickness", "_basePrice": 3.20},
            {"code": "2IN", "description": "2 inch wall thickness", "_basePrice": 4.75},
        ],
    },
    {
        "id": "item-10003",
        "number": "10003",
        "displayName": "Glycol Antifreeze, Propylene",
        "baseUnitOfMeasure": "GAL",
        "variants": [
            {"code": "5GAL", "description": "5 gallon pail", "_basePrice": 58.00},
            {"code": "55GAL", "description": "55 gallon drum", "_basePrice": 485.00},
        ],
    },
    {
        "id": "item-10004",
        "number": "10004",
        "displayName": "Thermostat Controller, Digital",
        "baseUnitOfMeasure": "EA",
        "variants": [
            {"code": "STD", "description": "Standard", "_basePrice": 245.00},
        ],
    },
    {
        "id": "item-10005",
        "number": "10005",
        "displayName": "Junction Box, Weatherproof",
        "baseUnitOfMeasure": "EA",
        "variants": [
            {"code": "4X4", "description": "4 inch × 4 inch", "_basePrice": 54.00},
            {"code": "6X6", "description": "6 inch × 6 inch", "_basePrice": 82.00},
        ],
    },
    {
        "id": "item-10006",
        "number": "10006",
        "displayName": "End Seal Kit, Heat Trace",
        "baseUnitOfMeasure": "EA",
        "variants": [
            {"code": "STD", "description": "Standard", "_basePrice": 32.50},
        ],
    },
    {
        "id": "item-10007",
        "number": "10007",
        "displayName": "Power Connection Kit",
        "baseUnitOfMeasure": "EA",
        "variants": [
            {"code": "STD", "description": "Standard", "_basePrice": 78.00},
        ],
    },
    {
        "id": "item-10008",
        "number": "10008",
        "displayName": "Aluminum Foil Tape",
        "baseUnitOfMeasure": "RL",
        "variants": [
            {"code": "2IN", "description": "2 inch × 150 ft roll", "_basePrice": 18.75},
            {"code": "3IN", "description": "3 inch × 150 ft roll", "_basePrice": 26.40},
        ],
    },
]


# Multiplier applied to base price for each customer price group
_GROUP_MULTIPLIERS = {
    "CONTRACTOR": 0.78,
    "ENDUSER": 1.00,
    "WHOLESALE": 0.65,
}


def list_items() -> list[dict[str, Any]]:
    """Lightweight list (no variants/prices)."""
    return [
        {
            "id": i["id"],
            "number": i["number"],
            "displayName": i["displayName"],
            "baseUnitOfMeasure": i["baseUnitOfMeasure"],
            "variantCount": len(i["variants"]),
        }
        for i in MOCK_ITEMS
    ]


def search_items(q: str) -> list[dict[str, Any]]:
    q = (q or "").strip().lower()
    if not q:
        return list_items()
    return [
        i
        for i in list_items()
        if q in i["number"].lower() or q in i["displayName"].lower()
    ]


MOCK_CUSTOMERS = [
    {
        "id": "mock-c-001",
        "number": "C00100",
        "displayName": "Mock Customer One",
        "phoneNumber": "555-0100",
        "email": "one@example.com",
        "city": "Edmonton",
        "currencyCode": "CAD",
        "customerPriceGroup": "CONTRACTOR",
    },
]

MOCK_CUSTOMER_TEMPLATES = [
    {"systemId": "mock-tmpl-1", "code": "CONTRACTOR", "description": "Contractor template",
     "customerPriceGroup": "CONTRACTOR", "paymentTermsCode": "30D"},
    {"systemId": "mock-tmpl-2", "code": "WHOLESALE", "description": "Wholesale template",
     "customerPriceGroup": "WHOLESALE", "paymentTermsCode": "NET30"},
    {"systemId": "mock-tmpl-3", "code": "END USER", "description": "End user / walk-in",
     "customerPriceGroup": "END USER", "paymentTermsCode": "COD"},
]


def list_customers(q: str = "", top: int = 200) -> list[dict[str, Any]]:
    rows = MOCK_CUSTOMERS[:]
    if q:
        term = q.lower()
        rows = [r for r in rows if term in r["number"].lower() or term in r["displayName"].lower()]
    return rows[:top]


def list_customer_templates() -> list[dict[str, Any]]:
    return MOCK_CUSTOMER_TEMPLATES[:]


MOCK_DIMENSION_VALUES = {
    "CUST CATEGORY": [
        {"code": "CONTRACTOR", "name": "Contractor"},
        {"code": "DISTRIBUTOR", "name": "Distributor"},
        {"code": "END USER", "name": "End User"},
        {"code": "WHOLESALE", "name": "Wholesale"},
    ],
    "BUSINESS TYPE": [
        {"code": "BANQUET HALL", "name": "Banquet Hall"},
        {"code": "CONTRACTOR", "name": "Contractor"},
        {"code": "ENGINEERING CO", "name": "Engineering Company"},
        {"code": "FOOD BANK", "name": "Food Bank"},
        {"code": "GAS STATION", "name": "Gas Station"},
        {"code": "GC", "name": "General Contractor"},
        {"code": "GENERAL CONTRACTOR", "name": "General Contractor"},
        {"code": "GROCERY STORE", "name": "Grocery Store"},
        {"code": "HOTEL", "name": "Hotel"},
        {"code": "MEAT SHOP", "name": "Meat Shop"},
        {"code": "RESTAURANT", "name": "Restaurant"},
        {"code": "STORE", "name": "Store"},
        {"code": "WHOLESALE", "name": "Wholesale"},
    ],
}


def list_dimension_values(dimension_code: str) -> list[dict[str, Any]]:
    rows = MOCK_DIMENSION_VALUES.get(dimension_code.upper(), [])
    return [
        {"dimensionCode": dimension_code.upper(), "code": r["code"], "name": r["name"]}
        for r in rows
    ]


def create_customer_from_template(template_system_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "createdNo": "C-MOCK-NEW",
        "customer": {
            "id": "mock-new",
            "number": "C-MOCK-NEW",
            "displayName": payload.get("name", ""),
            "phoneNumber": payload.get("phoneNo", ""),
            "email": payload.get("email", ""),
            "currencyCode": "CAD",
        },
    }


MOCK_SALES_QUOTES = [
    {
        "id": "mock-q-001",
        "number": "SQ1000001",
        "documentDate": "2026-05-13",
        "validUntilDate": "2026-06-12",
        "status": "Draft",
        "customerNumber": "ICC-CUS-1007",
        "customerName": "Zee Jay Mechanical",
        "sellToName": "Zee Jay Mechanical",
        "salesperson": "KIRANVIR",
        "totalAmountIncludingTax": 18803.76,
        "totalAmountExcludingTax": 17908.34,
        "currencyCode": "CAD",
        "shortcutDimension1Code": "CONTRACTOR",
    },
    {
        "id": "mock-q-002",
        "number": "SQ1000002",
        "documentDate": "2026-05-22",
        "validUntilDate": "2026-06-21",
        "status": "Open",
        "customerNumber": "ICC-CUS-1012",
        "customerName": "Northern Refineries",
        "sellToName": "Northern Refineries",
        "salesperson": "MANISH",
        "totalAmountIncludingTax": 4250.00,
        "totalAmountExcludingTax": 4047.62,
        "currencyCode": "CAD",
        "shortcutDimension1Code": "WHOLESALE",
    },
]


def list_sales_quotes(q: str = "", status: str = "", top: int = 200) -> list[dict[str, Any]]:
    rows = MOCK_SALES_QUOTES[:]
    if status:
        rows = [r for r in rows if r["status"] == status]
    if q:
        term = q.lower()
        rows = [
            r
            for r in rows
            if term in r["number"].lower()
            or term in r.get("customerNumber", "").lower()
            or term in r.get("sellToName", "").lower()
        ]
    return rows[:top]


def get_sales_quote(quote_id: str) -> dict[str, Any] | None:
    row = next((r for r in MOCK_SALES_QUOTES if r["id"] == quote_id), None)
    if not row:
        return None
    return {
        **row,
        "lines": [
            {
                "id": f"{quote_id}-line-1",
                "description": "Indoor split medium temperature room W6 X D8 X H8",
                "quantity": 1,
                "unitPrice": row["totalAmountExcludingTax"],
                "amountExcludingTax": row["totalAmountExcludingTax"],
                "amountIncludingTax": row["totalAmountIncludingTax"],
            }
        ],
    }


MOCK_SALES_ORDERS = [
    {
        "id": "mock-o-001",
        "number": "SO1000050",
        "orderDate": "2026-05-30",
        "requestedDeliveryDate": "2026-06-14",
        "status": "Open",
        "customerNumber": "ICC-CUS-1007",
        "customerName": "Zee Jay Mechanical",
        "shipToName": "Zee Jay Mechanical",
        "salesperson": "KIRANVIR",
        "totalAmountIncludingTax": 28450.00,
        "totalAmountExcludingTax": 27095.24,
        "currencyCode": "CAD",
        "shortcutDimension1Code": "CONTRACTOR",
    },
    {
        "id": "mock-o-002",
        "number": "SO1000051",
        "orderDate": "2026-06-02",
        "requestedDeliveryDate": "2026-06-20",
        "status": "Released",
        "customerNumber": "ICC-CUS-1012",
        "customerName": "Northern Refineries",
        "shipToName": "Northern Refineries",
        "salesperson": "MANISH",
        "totalAmountIncludingTax": 9120.50,
        "totalAmountExcludingTax": 8686.19,
        "currencyCode": "CAD",
        "shortcutDimension1Code": "WHOLESALE",
    },
]


def list_sales_orders(q: str = "", status: str = "", top: int = 200) -> list[dict[str, Any]]:
    rows = MOCK_SALES_ORDERS[:]
    if status:
        rows = [r for r in rows if r["status"] == status]
    if q:
        term = q.lower()
        rows = [
            r for r in rows
            if term in r["number"].lower()
            or term in r.get("customerNumber", "").lower()
            or term in r.get("shipToName", "").lower()
        ]
    return rows[:top]


def get_sales_order(order_id: str) -> dict[str, Any] | None:
    row = next((r for r in MOCK_SALES_ORDERS if r["id"] == order_id), None)
    if not row:
        return None
    return {**row, "lines": []}


def list_sku_inventory_flat(q: str = "", location: str = "", top: int = 500) -> list[dict[str, Any]]:
    """Flat mock SKU rows mirroring the live BC sku-inventory shape."""
    rows: list[dict[str, Any]] = []
    locations = ["MAIN", "BRANCH-2"]
    seed = 1
    for item in MOCK_ITEMS:
        for v in item["variants"]:
            for loc in locations:
                seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
                qty = seed % 5000
                rows.append(
                    {
                        "id": f"{item['number']}-{v['code']}-{loc}",
                        "itemNo": item["number"],
                        "itemDescription": item["displayName"],
                        "variantCode": v["code"],
                        "variantDescription": v["description"],
                        "unitOfMeasure": item.get("baseUnitOfMeasure", ""),
                        "locationCode": loc,
                        "replenishmentSystem": "Purchase",
                        "inventory": float(qty),
                        "qtyOnSalesOrder": float((seed >> 8) % 50),
                        "qtyOnPurchOrder": float((seed >> 16) % 200),
                        "reorderPoint": 10.0,
                    }
                )
    if q:
        term = q.lower()
        rows = [
            r
            for r in rows
            if term in r["itemNo"].lower()
            or term in r["variantCode"].lower()
            or term in r["itemDescription"].lower()
            or term in r["variantDescription"].lower()
        ]
    if location:
        rows = [r for r in rows if r["locationCode"] == location]
    rows.sort(key=lambda r: r["inventory"], reverse=True)
    return rows[:top]


def get_pricing_matrix(item_no: str) -> dict[str, Any] | None:
    item = next((i for i in MOCK_ITEMS if i["number"] == item_no), None)
    if item is None:
        return None

    variants_out: list[dict[str, Any]] = []
    for v in item["variants"]:
        base = v["_basePrice"]
        prices = [
            {
                "groupCode": g["code"],
                "groupDescription": g["description"],
                "unitPrice": round(base * _GROUP_MULTIPLIERS[g["code"]], 2),
                "currency": "CAD",
            }
            for g in MOCK_PRICE_GROUPS
        ]
        variants_out.append(
            {
                "code": v["code"],
                "description": v["description"],
                "prices": prices,
            }
        )

    return {
        "item": {
            "id": item["id"],
            "number": item["number"],
            "displayName": item["displayName"],
            "baseUnitOfMeasure": item["baseUnitOfMeasure"],
        },
        "priceGroups": MOCK_PRICE_GROUPS,
        "variants": variants_out,
    }
