from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify
from flask_login import login_required

from ..extensions import db
from ..models.sync_log import SyncLog
from ..services.business_central import build_client_from_config as bc_client
from ..services.salesforce import build_client_from_config as sf_client

bp = Blueprint("integrations", __name__, url_prefix="/api/integrations")


def _last_sync(integration: str) -> dict | None:
    row = (
        db.session.query(SyncLog)
        .filter_by(integration=integration, status="success")
        .order_by(SyncLog.completed_at.desc())
        .first()
    )
    return row.to_dict() if row else None


@bp.get("")
@login_required
def status():
    return jsonify(
        {
            "businessCentral": {
                "configured": bool(current_app.config["BC_TENANT_ID"] and current_app.config["BC_CLIENT_ID"]),
                "lastSync": _last_sync("business_central"),
            },
            "salesforce": {
                "configured": bool(current_app.config["SF_USERNAME"]),
                "lastSync": _last_sync("salesforce"),
            },
        }
    )


@bp.post("/bc/ping")
@login_required
def bc_ping():
    log = SyncLog(integration="business_central", entity="ping", status="started")
    db.session.add(log)
    db.session.commit()

    result = bc_client(current_app.config).ping()
    if result.get("connected"):
        log.mark_success()
    else:
        log.mark_failed(result.get("message") or result.get("reason") or "unknown")
    db.session.commit()

    result["syncLogId"] = log.id
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return jsonify(result), (200 if result.get("connected") else 502)


@bp.post("/sf/ping")
@login_required
def sf_ping():
    log = SyncLog(integration="salesforce", entity="ping", status="started")
    db.session.add(log)
    db.session.commit()

    result = sf_client(current_app.config).ping()
    if result.get("connected"):
        log.mark_success()
    else:
        log.mark_failed(result.get("message") or result.get("reason") or "unknown")
    db.session.commit()

    result["syncLogId"] = log.id
    result["timestamp"] = datetime.now(timezone.utc).isoformat()
    return jsonify(result), (200 if result.get("connected") else 502)


@bp.get("/sync-log")
@login_required
def sync_log_list():
    rows = (
        db.session.query(SyncLog)
        .order_by(SyncLog.started_at.desc())
        .limit(50)
        .all()
    )
    return jsonify([r.to_dict() for r in rows])
