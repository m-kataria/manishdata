from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db

ROLE_SUPERADMIN = "superadmin"
ROLE_ADMIN = "admin"
ALLOWED_ROLES = (ROLE_SUPERADMIN, ROLE_ADMIN)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ROLE_ADMIN, server_default=ROLE_ADMIN
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )
    job_title: Mapped[str | None] = mapped_column(String(80))
    reports_to: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_superadmin(self) -> bool:
        return self.role == ROLE_SUPERADMIN

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name,
            "isAdmin": self.is_admin,
            "role": self.role,
            "isActive": self.is_active,
            "jobTitle": self.job_title,
            "reportsTo": self.reports_to,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
