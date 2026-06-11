from flask import Blueprint, jsonify, request
from flask_login import login_required

from ..extensions import db
from ..models.inventory import InventoryItem

bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")


@bp.get("")
@login_required
def list_inventory():
    q = (request.args.get("q") or "").strip()
    query = db.session.query(InventoryItem)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (InventoryItem.item_number.ilike(like)) | (InventoryItem.display_name.ilike(like))
        )
    rows = query.order_by(InventoryItem.item_number).limit(500).all()
    return jsonify([r.to_dict() for r in rows])


@bp.get("/<int:item_id>")
@login_required
def get_item(item_id: int):
    item = db.session.get(InventoryItem, item_id)
    if item is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(item.to_dict())
