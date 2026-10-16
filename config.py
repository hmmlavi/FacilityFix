"""Configuration: secrets and persistent runtime data stay outside source control."""
import os
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Config:
    ALLOW_PREVIEW_EMBED = os.environ.get('FACILITYFIX_PREVIEW') == '1'
    SECRET_KEY = os.environ.get('FACILITYFIX_SECRET_KEY')
    DATABASE = str(ROOT / 'instance' / 'facilityfix.sqlite3')
    UPLOAD_FOLDER = str(ROOT / 'uploads')
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # Multipart overhead above the 2 MiB photo cap.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('FACILITYFIX_HTTPS') == '1'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
