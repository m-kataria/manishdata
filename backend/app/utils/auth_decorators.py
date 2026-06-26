from functools import wraps

from flask import jsonify
from flask_login import current_user, login_required


def superadmin_required(view):
    """Restricts a view to users with role='superadmin'. Returns 403 otherwise."""

    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_superadmin:
            return jsonify({"error": "forbidden", "reason": "superadmin_required"}), 403
        return view(*args, **kwargs)

    return wrapped
