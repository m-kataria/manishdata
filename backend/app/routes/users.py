"""User management endpoints, restricted to superadmin."""

from flask import Blueprint, jsonify, request
from flask_login import current_user

from ..extensions import db
from ..models.user import ALLOWED_ROLES, ROLE_ADMIN, ROLE_SUPERADMIN, User
from ..utils.auth_decorators import superadmin_required

bp = Blueprint("users", __name__, url_prefix="/api/users")


def _count_active_superadmins(exclude_id: int | None = None) -> int:
    q = db.session.query(User).filter(
        User.role == ROLE_SUPERADMIN, User.is_active.is_(True)
    )
    if exclude_id is not None:
        q = q.filter(User.id != exclude_id)
    return q.count()


@bp.get("")
@superadmin_required
def list_users():
    show_inactive = request.args.get("include_inactive", "").lower() in ("1", "true")
    q = db.session.query(User)
    if not show_inactive:
        q = q.filter(User.is_active.is_(True))
    users = q.order_by(User.id).all()
    return jsonify([u.to_dict() for u in users])


@bp.post("")
@superadmin_required
def create_user():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    display_name = (data.get("displayName") or "").strip() or None
    role = (data.get("role") or ROLE_ADMIN).strip()

    if not username:
        return jsonify({"error": "username required"}), 400
    if not password:
        return jsonify({"error": "password required"}), 400
    if role not in ALLOWED_ROLES:
        return jsonify({"error": f"role must be one of {list(ALLOWED_ROLES)}"}), 400

    existing = db.session.query(User).filter_by(username=username).first()
    if existing is not None:
        return jsonify({"error": "username already taken"}), 409

    user = User(
        username=username,
        display_name=display_name or username,
        is_admin=True,
        role=role,
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@bp.patch("/<int:user_id>")
@superadmin_required
def update_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "not found"}), 404

    data = request.get_json(silent=True) or {}
    changed = False

    if "displayName" in data:
        user.display_name = (data["displayName"] or "").strip() or None
        changed = True

    if "password" in data and data["password"]:
        user.set_password(data["password"])
        changed = True

    if "role" in data:
        new_role = (data["role"] or "").strip()
        if new_role not in ALLOWED_ROLES:
            return jsonify({"error": f"role must be one of {list(ALLOWED_ROLES)}"}), 400
        if new_role != user.role:
            if user.id == current_user.id:
                return jsonify({"error": "cannot change your own role"}), 400
            if (
                user.role == ROLE_SUPERADMIN
                and new_role != ROLE_SUPERADMIN
                and _count_active_superadmins(exclude_id=user.id) == 0
            ):
                return jsonify({"error": "cannot demote the last superadmin"}), 400
            user.role = new_role
            changed = True

    if "isActive" in data:
        new_active = bool(data["isActive"])
        if new_active != user.is_active:
            if user.id == current_user.id and not new_active:
                return jsonify({"error": "cannot deactivate your own account"}), 400
            if (
                not new_active
                and user.role == ROLE_SUPERADMIN
                and _count_active_superadmins(exclude_id=user.id) == 0
            ):
                return jsonify({"error": "cannot deactivate the last superadmin"}), 400
            user.is_active = new_active
            changed = True

    if changed:
        db.session.commit()
    return jsonify(user.to_dict())


@bp.delete("/<int:user_id>")
@superadmin_required
def delete_user(user_id: int):
    """Soft-delete: sets is_active=False. Preserves quote_owners audit trail."""
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "not found"}), 404
    if user.id == current_user.id:
        return jsonify({"error": "cannot delete your own account"}), 400
    if not user.is_active:
        return ("", 204)
    if (
        user.role == ROLE_SUPERADMIN
        and _count_active_superadmins(exclude_id=user.id) == 0
    ):
        return jsonify({"error": "cannot delete the last superadmin"}), 400

    user.is_active = False
    db.session.commit()
    return ("", 204)
