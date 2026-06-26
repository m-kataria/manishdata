"""Add or update an app user.

Usage:
    python scripts/add_user.py <username> --display "Brad" --password "..."
    python scripts/add_user.py brad --display "Brad" --password "secret123" --admin
    python scripts/add_user.py mn --password "..." --role superadmin

Roles: 'superadmin' (can delete) or 'admin' (everything except delete).
--admin is kept for back-compat: it sets is_admin=True and, if --role is not
given for a new user, defaults the role to 'admin'.

If the user exists, --display/--password/--role update it; --admin toggles
is_admin. A password is required when creating a new user. Run from the
backend/ directory.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models import User
from app.models.user import ALLOWED_ROLES, ROLE_ADMIN


def main() -> int:
    parser = argparse.ArgumentParser(description="Add or update an app user.")
    parser.add_argument("username", help="Login username (e.g. 'brad')")
    parser.add_argument("--display", dest="display_name",
                        help="Display name shown in 'Created by ... using ICC App'")
    parser.add_argument("--password", help="Password (required for new users)")
    parser.add_argument("--admin", action="store_true", help="Set is_admin=True")
    parser.add_argument("--no-admin", dest="no_admin", action="store_true",
                        help="Remove is_admin flag if currently set")
    parser.add_argument("--role", choices=ALLOWED_ROLES,
                        help="Role: superadmin (can delete) or admin (no delete)")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        user = db.session.query(User).filter_by(username=args.username).first()

        if user is None:
            if not args.password:
                print(f"error: --password is required to create user '{args.username}'",
                      file=sys.stderr)
                return 2
            user = User(
                username=args.username,
                display_name=args.display_name or args.username.capitalize(),
                is_admin=bool(args.admin),
                role=args.role or ROLE_ADMIN,
            )
            user.set_password(args.password)
            db.session.add(user)
            db.session.commit()
            print(f"Created user '{user.username}' (display='{user.display_name}', "
                  f"is_admin={user.is_admin}, role={user.role}).")
            return 0

        changes: list[str] = []
        if args.display_name and args.display_name != user.display_name:
            changes.append(f"display_name: {user.display_name!r} -> {args.display_name!r}")
            user.display_name = args.display_name
        if args.password:
            user.set_password(args.password)
            changes.append("password updated")
        if args.admin and not user.is_admin:
            user.is_admin = True
            changes.append("is_admin -> True")
        if args.no_admin and user.is_admin:
            user.is_admin = False
            changes.append("is_admin -> False")
        if args.role and args.role != user.role:
            changes.append(f"role: {user.role!r} -> {args.role!r}")
            user.role = args.role

        if changes:
            db.session.commit()
            print(f"Updated user '{user.username}': " + "; ".join(changes))
        else:
            print(f"User '{user.username}' already matches; nothing to do.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
