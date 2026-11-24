"""
OUTPOST AI - Configuration
==========================
Database: Defaults to SQLite for local testing. To use MySQL, set the
DATABASE_URL environment variable or change SQLALCHEMY_DATABASE_URI below.

MySQL example:
    mysql+pymysql://username:password@localhost:3306/outpost_ai
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Database -----------------------------------------------------------
    # Prefer OUTPOST_DATABASE_URL; DATABASE_URL is also accepted for hosts
    # that provide that conventional variable. SQLite remains the local fallback.
    database_url = os.environ.get("OUTPOST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("mysql://"):
        database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)
    elif database_url and database_url.startswith("mariadb://"):
        database_url = database_url.replace("mariadb://", "mysql+pymysql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{os.path.join(BASE_DIR, 'outpost_ai.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Security -----------------------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "local-development-only-change-before-deploy")

    # --- Session ------------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24h

    # --- App ----------------------------------------------------------------
    APP_NAME = "OUTPOST AI"
    APP_TAGLINE = "AI-Powered Freelancer Outreach Platform"
