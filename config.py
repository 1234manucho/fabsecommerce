import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'fabs.db'}").replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    WTF_CSRF_TIME_LIMIT = 1728000  # 20 days in seconds
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    BRAND_NAME = "FABS Trading Global E-Commerce"
    WHATSAPP_KENYA = os.getenv("WHATSAPP_KENYA", "254729004000")
    WHATSAPP_GREECE = os.getenv("WHATSAPP_GREECE", "306949147011")
    CATALOGUE_TOTAL = int(os.getenv("CATALOGUE_TOTAL", "2399976"))
    CATALOGUE_MAX_PAGES = int(os.getenv("CATALOGUE_MAX_PAGES", "999"))
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@fabstrading.com")
    TRADING_EMAIL = os.getenv("TRADING_EMAIL", "trade@fabstrading.com")
    BANK_MID_MODE = os.getenv("BANK_MID_MODE", "sandbox")
    BANK_MID_CHECKOUT_URL = os.getenv("BANK_MID_CHECKOUT_URL", "")
    BANK_MID_MERCHANT_ID = os.getenv("BANK_MID_MERCHANT_ID", "")
    BANK_MID_API_KEY = os.getenv("BANK_MID_API_KEY", "")
    BANK_MID_SIGNING_SECRET = os.getenv("BANK_MID_SIGNING_SECRET", "")
    BANK_MID_WEBHOOK_SECRET = os.getenv("BANK_MID_WEBHOOK_SECRET", "")
    BANK_MID_RETURN_URL = os.getenv("BANK_MID_RETURN_URL", "")
    BANK_MID_CANCEL_URL = os.getenv("BANK_MID_CANCEL_URL", "")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@fabstrading.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")