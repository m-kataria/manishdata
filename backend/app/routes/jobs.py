from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from ..extensions import db
from ..models.job import Job

bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


@bp.get("")
@login_required
def list_jobs():
    status = request.args.get("status")
    query = db.session.query(Job)
    if status:
        query = query.filter(Job.status == status)
    jobs = query.order_by(Job.created_at.desc()).limit(200).all()
    return jsonify([j.to_dict() for j in jobs])


@bp.post("")
@login_required
def create_job():
    data = request.get_json(silent=True) or {}
    required = {"jobNumber", "title", "customerName"}
    missing = required - set(data.keys())
    if missing:
        return jsonify({"error": f"missing fields: {sorted(missing)}"}), 400

    job = Job(
        job_number=data["jobNumber"],
        title=data["title"],
        customer_name=data["customerName"],
        status=data.get("status", "draft"),
        notes=data.get("notes"),
        sf_opportunity_id=data.get("sfOpportunityId"),
        bc_sales_order_id=data.get("bcSalesOrderId"),
        created_by_id=current_user.id,
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201


@bp.get("/<int:job_id>")
@login_required
def get_job(job_id: int):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "not_found"}), 404
    return jsonify(job.to_dict())


@bp.patch("/<int:job_id>")
@login_required
def update_job(job_id: int):
    job = db.session.get(Job, job_id)
    if job is None:
        return jsonify({"error": "not_found"}), 404

    data = request.get_json(silent=True) or {}
    for field, attr in [
        ("title", "title"),
        ("customerName", "customer_name"),
        ("status", "status"),
        ("notes", "notes"),
        ("sfOpportunityId", "sf_opportunity_id"),
        ("bcSalesOrderId", "bc_sales_order_id"),
    ]:
        if field in data:
            setattr(job, attr, data[field])
    db.session.commit()
    return jsonify(job.to_dict())
