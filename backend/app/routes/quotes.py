from flask import Blueprint, jsonify, request
from flask_login import login_required

from ..extensions import db
from ..models.quote import Quote

bp = Blueprint("quotes", __name__, url_prefix="/api/quotes")


@bp.get("")
@login_required
def list_quotes():
    status = request.args.get("status")
    query = db.session.query(Quote)
    if status:
        query = query.filter(Quote.status == status)
    rows = query.order_by(Quote.created_at.desc()).limit(200).all()
    return jsonify([q.to_dict() for q in rows])


@bp.post("")
@login_required
def create_quote():
    data = request.get_json(silent=True) or {}
    required = {"quoteNumber", "customerName"}
    missing = required - set(data.keys())
    if missing:
        return jsonify({"error": f"missing fields: {sorted(missing)}"}), 400

    quote = Quote(
        quote_number=data["quoteNumber"],
        customer_name=data["customerName"],
        status=data.get("status", "draft"),
        total_amount=data.get("totalAmount"),
        currency=data.get("currency", "CAD"),
        bc_sales_quote_id=data.get("bcSalesQuoteId"),
        sf_opportunity_id=data.get("sfOpportunityId"),
        job_id=data.get("jobId"),
        notes=data.get("notes"),
    )
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 201


@bp.get("/<int:quote_id>")
@login_required
def get_quote(quote_id: int):
    quote = db.session.get(Quote, quote_id)
    if quote is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(quote.to_dict())
