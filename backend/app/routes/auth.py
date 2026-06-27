from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db
from ..models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    user = db.session.query(User).filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401
    if not user.is_active:
        return jsonify({"error": "account disabled"}), 403

    login_user(user, remember=True)
    return jsonify(user.to_dict())


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"ok": True})


@bp.get("/me")
def me():
    if not current_user.is_authenticated:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(current_user.to_dict())


@bp.post("/change-password")
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    current = data.get("currentPassword") or ""
    new = data.get("newPassword") or ""

    if not current or not new:
        return jsonify({"error": "current and new password required"}), 400
    if len(new) < 8:
        return jsonify({"error": "new password must be at least 8 characters"}), 400
    if not current_user.check_password(current):
        return jsonify({"error": "current password is incorrect"}), 401
    if current == new:
        return jsonify({"error": "new password must be different"}), 400

    current_user.set_password(new)
    db.session.commit()
    return jsonify({"ok": True})
