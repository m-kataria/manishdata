import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _normalize_db_url(url: str) -> str:
    # Railway provides postgres:// — SQLAlchemy 2.x needs postgresql+psycopg:// for psycopg3.
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///nerval_ops.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    SESSION_COOKIE_SAMESITE = "None" if os.environ.get("FLASK_ENV") == "production" else "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True

    BC_TENANT_ID = os.environ.get("BC_TENANT_ID", "")
    BC_CLIENT_ID = os.environ.get("BC_CLIENT_ID", "")
    BC_CLIENT_SECRET = os.environ.get("BC_CLIENT_SECRET", "")
    BC_ENVIRONMENT = os.environ.get("BC_ENVIRONMENT", "Production")
    BC_COMPANY_ID = os.environ.get("BC_COMPANY_ID", "")
    # 'auto' = mock when creds look like placeholders, real otherwise.
    # 'on' = always mock. 'off' = always real (errors if creds missing).
    BC_MOCK_MODE = os.environ.get("BC_MOCK_MODE", "auto").lower()

    SF_USERNAME = os.environ.get("SF_USERNAME", "")
    SF_PASSWORD = os.environ.get("SF_PASSWORD", "")
    SF_SECURITY_TOKEN = os.environ.get("SF_SECURITY_TOKEN", "")
    SF_DOMAIN = os.environ.get("SF_DOMAIN", "login")

    INITIAL_ADMIN_USERNAME = os.environ.get("INITIAL_ADMIN_USERNAME", "admin")
    INITIAL_ADMIN_PASSWORD = os.environ.get("INITIAL_ADMIN_PASSWORD", "change-me")
