from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

from ..services.salesforce import SalesforceError, build_client_from_config

bp = Blueprint("sf", __name__, url_prefix="/api/sf")


def _client():
    return build_client_from_config(current_app.config)


@bp.get("/accounts")
@login_required
def get_accounts():
    try:
        return jsonify(_client().get_accounts(limit=int(request.args.get("limit", 100))))
    except SalesforceError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/opportunities")
@login_required
def get_opportunities():
    try:
        return jsonify(_client().get_opportunities(limit=int(request.args.get("limit", 100))))
    except SalesforceError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@bp.get("/contacts")
@login_required
def get_contacts():
    try:
        return jsonify(_client().get_contacts(limit=int(request.args.get("limit", 100))))
    except SalesforceError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@bp.post("/leads")
@login_required
def create_lead():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify(_client().create_lead(data)), 201
    except SalesforceError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 502
