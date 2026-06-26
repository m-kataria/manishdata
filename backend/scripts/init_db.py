"""Creates all tables and seeds the initial admin user. Idempotent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.models import User
from app.models.user import ROLE_ADMIN, ROLE_SUPERADMIN


def _ensure_role_column() -> None:
    """Adds users.role to existing databases that predate the role-based perms."""
    inspector = inspect(db.engine)
    if "users" not in inspector.get_table_names():
        return
    cols = {c["name"] for c in inspector.get_columns("users")}
    if "role" in cols:
        return
    with db.engine.begin() as conn:
        conn.execute(
            text(
                f"ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL "
                f"DEFAULT '{ROLE_ADMIN}'"
            )
        )
    print("Added 'role' column to users (default 'admin').")


def main() -> None:
    app = create_app()
    with app.app_context():
        _ensure_role_column()
        db.create_all()

        admin_username = app.config["INITIAL_ADMIN_USERNAME"]
        admin_password = app.config["INITIAL_ADMIN_PASSWORD"]

        existing = db.session.query(User).filter_by(username=admin_username).first()
        if existing is None:
            admin = User(
                username=admin_username,
                display_name="Admin",
                is_admin=True,
                role=ROLE_SUPERADMIN,
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin user '{admin_username}' (role=superadmin).")
        else:
            print(f"Admin user '{admin_username}' already exists; skipping.")


if __name__ == "__main__":
    main()
