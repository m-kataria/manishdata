"""Creates all tables and seeds the initial admin user. Idempotent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import User


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        admin_username = app.config["INITIAL_ADMIN_USERNAME"]
        admin_password = app.config["INITIAL_ADMIN_PASSWORD"]

        existing = db.session.query(User).filter_by(username=admin_username).first()
        if existing is None:
            admin = User(username=admin_username, display_name="Admin", is_admin=True)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin user '{admin_username}'.")
        else:
            print(f"Admin user '{admin_username}' already exists; skipping.")


if __name__ == "__main__":
    main()
