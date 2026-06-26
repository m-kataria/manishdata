from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from flask_login import current_user

from ..extensions import db
from ..models.inventory import InventoryItem
from ..models.quote_owner import QuoteOwner
from ..models.sync_log import SyncLog
from ..models.user import User
from ..services.business_central import BusinessCentralError, build_client_from_config
from ..utils.auth_decorators import superadmin_required

bp = Blueprint("bc", __name__, url_prefix="/api/bc")


def _client():
    return build_client_from_config(current_app.config)


@bp.get("/customers")
@login_required
def get_customers():
    q = request.args.get("q", "")
    top = int(request.args.get("top", 200))
    try:
        return jsonify(_client().list_customers(q=q, top=top))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/customers/<number>")
@login_required
def get_customer(number: str):
    try:
        c = _client().get_customer_by_number(number)
        if c is None:
            return jsonify({"error": "customer not found"}), 404
        return jsonify(c)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.patch("/customers/<system_id>")
@login_required
def patch_customer(system_id: str):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(_client().update_customer(system_id, data))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/customer-templates")
@login_required
def customer_templates():
    try:
        return jsonify(_client().list_customer_templates())
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/payment-terms")
@login_required
def payment_terms():
    try:
        return jsonify(_client().list_payment_terms())
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/locations")
@login_required
def locations():
    try:
        return jsonify(_client().list_locations())
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/dimension-values")
@login_required
def dimension_values():
    code = request.args.get("code", "").strip()
    try:
        return jsonify(_client().list_dimension_values(code))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/customers")
@login_required
def create_customer():
    data = request.get_json(silent=True) or {}
    template_system_id = data.get("templateSystemId")
    if not template_system_id:
        return jsonify({"error": "templateSystemId is required"}), 400
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    try:
        result = _client().create_customer_from_template(template_system_id, data)
        return jsonify(result), 201
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/inventory-items")
@login_required
def get_inventory_items():
    try:
        return jsonify(_client().get_inventory_items(top=int(request.args.get("top", 100))))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/sales-orders")
@login_required
def post_sales_order():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customerId")
    if not customer_id:
        return jsonify({"error": "customerId required"}), 400
    try:
        result = _client().post_sales_order(
            customer_id=customer_id,
            external_doc_no=data.get("externalDocumentNumber"),
        )
        return jsonify(result), 201
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/sales-orders")
@login_required
def sales_orders_list():
    q = request.args.get("q", "")
    status = request.args.get("status", "")
    top = int(request.args.get("top", 200))
    try:
        return jsonify(_client().list_sales_orders(q=q, status=status, top=top))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/sales-orders/<order_id>")
@login_required
def sales_order_detail(order_id: str):
    try:
        result = _client().get_sales_order(order_id)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@bp.get("/sales-orders/<order_id>/pdf")
@login_required
def sales_order_pdf(order_id: str):
    from flask import Response

    try:
        pdf_bytes, filename = _client().get_sales_order_pdf(order_id)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@bp.post("/sales-quotes/<quote_id>/make-order")
@login_required
def make_order(quote_id: str):
    try:
        return jsonify(_client().make_order_from_quote(quote_id)), 201
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/sales-quotes")
@login_required
def create_sales_quote():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customerId")
    if not customer_id:
        return jsonify({"error": "customerId required"}), 400
    try:
        result = _client().create_sales_quote(
            customer_id=customer_id,
            document_date=data.get("documentDate"),
            valid_until=data.get("validUntil"),
        )
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502

    quote_no = (result.get("number") or "").strip()
    if quote_no:
        try:
            existing = db.session.query(QuoteOwner).filter_by(quote_no=quote_no).first()
            if existing is None:
                db.session.add(QuoteOwner(quote_no=quote_no, user_id=current_user.id))
                db.session.commit()
        except Exception:
            db.session.rollback()
    return jsonify(result), 201


@bp.get("/sales-quotes/<quote_no>/header")
@login_required
def get_sales_quote_header(quote_no: str):
    try:
        q = _client().get_sales_quote_by_number(quote_no)
        if q is None:
            return jsonify({"error": "quote not found"}), 404
        return jsonify(q)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/sales-quotes/<quote_no>/lines")
@login_required
def get_sales_quote_lines(quote_no: str):
    try:
        return jsonify(_client().list_quote_lines(quote_no))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/sales-quotes/<quote_no>/lines")
@login_required
def create_sales_quote_line(quote_no: str):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(_client().create_quote_line(quote_no, data)), 201
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/sales-quotes/<dest_no>/copy-from")
@login_required
def copy_quote_lines(dest_no: str):
    data = request.get_json(silent=True) or {}
    source_no = (data.get("sourceQuoteNo") or "").strip()
    if not source_no:
        return jsonify({"error": "sourceQuoteNo required"}), 400
    if source_no == dest_no:
        return jsonify({"error": "source and destination must differ"}), 400
    try:
        return jsonify(_client().clone_quote_lines(source_no, dest_no))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.patch("/quote-lines/<line_id>")
@login_required
def patch_quote_line(line_id: str):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(_client().update_quote_line(line_id, data))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.delete("/quote-lines/<line_id>")
@superadmin_required
def delete_quote_line(line_id: str):
    try:
        _client().delete_quote_line(line_id)
        return ("", 204)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/sales-quotes/<quote_no>/lines/<int:line_no>/ato-lines")
@login_required
def get_ato_lines(quote_no: str, line_no: int):
    try:
        return jsonify(_client().list_ato_lines_for_quote_line(quote_no, line_no))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/ato-lines")
@login_required
def add_ato_line():
    data = request.get_json(silent=True) or {}
    asm_type = data.get("assemblyDocType")
    asm_no = data.get("assemblyDocNo")
    if not asm_type or not asm_no:
        return jsonify({"error": "assemblyDocType + assemblyDocNo required"}), 400
    try:
        return jsonify(_client().add_ato_line(asm_type, asm_no, data)), 201
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.patch("/ato-lines/<line_id>")
@login_required
def patch_ato_line(line_id: str):
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(_client().update_ato_line(line_id, data))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.delete("/ato-lines/<line_id>")
@superadmin_required
def delete_ato_line_route(line_id: str):
    try:
        _client().delete_ato_line(line_id)
        return ("", 204)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/sales-quotes")
@login_required
def sales_quotes_list():
    q = request.args.get("q", "")
    status = request.args.get("status", "")
    top = int(request.args.get("top", 200))
    try:
        quotes = _client().list_sales_quotes(q=q, status=status, top=top)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502

    # "Created by" surfaces BC's salesperson code (what BC's UI shows). For
    # quotes created through this app where BC's salesperson isn't set yet,
    # fall back to the local QuoteOwner record.
    numbers = [qq.get("number") for qq in quotes if qq.get("number")]
    app_owner_by_no: dict[str, str] = {}
    if numbers:
        try:
            rows = (
                db.session.query(QuoteOwner, User)
                .join(User, QuoteOwner.user_id == User.id)
                .filter(QuoteOwner.quote_no.in_(numbers))
                .all()
            )
            for owner, user in rows:
                name = (user.display_name or user.username or "").strip()
                if name:
                    app_owner_by_no[owner.quote_no] = name
        except Exception:
            app_owner_by_no = {}

    for qq in quotes:
        bc_salesperson = (qq.get("salesperson") or "").strip()
        if bc_salesperson:
            qq["createdBy"] = bc_salesperson
        else:
            qq["createdBy"] = app_owner_by_no.get(qq.get("number") or "")
    return jsonify(quotes)


@bp.get("/sales-quotes/<quote_id>")
@login_required
def sales_quote_detail(quote_id: str):
    try:
        result = _client().get_sales_quote(quote_id)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502
    if result is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@bp.get("/sales-quotes/<quote_id>/pdf")
@login_required
def sales_quote_pdf(quote_id: str):
    """Streams the BC-rendered Sales Quote PDF straight to the browser."""
    from flask import Response

    try:
        pdf_bytes, filename = _client().get_sales_quote_pdf(quote_id)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@bp.get("/sku-inventory")
@login_required
def sku_inventory():
    """Flat SKU listing mirroring BC's Stockkeeping Units page."""
    q = request.args.get("q", "")
    location = request.args.get("location", "")
    top = int(request.args.get("top", 500))
    try:
        return jsonify(_client().list_sku_inventory(q=q, location=location, top=top))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/item-open-orders")
@login_required
def item_open_orders():
    """Returns open SOs + open POs that contribute to a SKU's On SO / On PO."""
    item_no = (request.args.get("itemNo") or "").strip()
    variant_code = (request.args.get("variant") or "").strip()
    location_code = (request.args.get("location") or "").strip()
    if not item_no:
        return jsonify({"error": "itemNo required"}), 400
    try:
        return jsonify(
            _client().get_item_open_orders(
                item_no, variant_code=variant_code, location_code=location_code
            )
        )
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/items-search")
@login_required
def items_search():
    q = request.args.get("q", "")
    try:
        return jsonify(_client().list_items_for_pricing(q=q))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/customer-price-groups")
@login_required
def customer_price_groups():
    try:
        return jsonify(_client().get_customer_price_groups())
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/pricing-rows")
@login_required
def pricing_rows():
    q = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    try:
        return jsonify(_client().list_variant_pricing_rows(q=q, location=location))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/pricing-matrix")
@login_required
def pricing_matrix():
    item_no = request.args.get("itemNo", "").strip()
    if not item_no:
        return jsonify({"error": "itemNo required"}), 400
    try:
        result = _client().get_pricing_matrix(item_no)
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502
    if result is None:
        return jsonify({"error": "item not found"}), 404
    return jsonify(result)


@bp.post("/component-prices")
@login_required
def component_prices():
    data = request.get_json(silent=True) or {}
    customer_no = (data.get("customerNumber") or "").strip()
    components = data.get("components") or []
    if not customer_no:
        return jsonify({"error": "customerNumber required"}), 400
    try:
        return jsonify(_client().get_component_prices(customer_no, components))
    except BusinessCentralError as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/sync/inventory")
@login_required
def sync_inventory():
    """Pulls inventory items from BC, upserts into the local cache, logs the run."""
    log = SyncLog(integration="business_central", entity="inventory_items", status="started")
    db.session.add(log)
    db.session.commit()

    try:
        items = _client().get_inventory_items(top=1000)
    except Exception as e:
        log.mark_failed(str(e))
        db.session.commit()
        return jsonify({"error": str(e), "syncLogId": log.id}), 502

    count = 0
    for raw in items:
        bc_id = raw.get("id")
        existing = (
            db.session.query(InventoryItem).filter_by(bc_item_id=bc_id).first()
            if bc_id
            else None
        )
        if existing is None:
            existing = InventoryItem(
                bc_item_id=bc_id,
                item_number=raw.get("number", ""),
                display_name=raw.get("displayName", ""),
            )
            db.session.add(existing)
        existing.item_number = raw.get("number", existing.item_number)
        existing.display_name = raw.get("displayName", existing.display_name)
        existing.base_unit_of_measure = raw.get("baseUnitOfMeasureCode")
        existing.unit_price = raw.get("unitPrice")
        existing.inventory_on_hand = raw.get("inventory")
        existing.last_synced_at = datetime.now(timezone.utc)
        count += 1

    log.mark_success(records=count)
    db.session.commit()
    return jsonify({"syncedRecords": count, "syncLogId": log.id})
