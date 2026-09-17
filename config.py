import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    # ============================================================
    # CORE
    # ============================================================
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'fabs.db'}",
    ).replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    WTF_CSRF_TIME_LIMIT = 1728000  # 20 days in seconds

    # ============================================================
    # SESSIONS & COOKIES
    # ============================================================
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    # ============================================================
    # BRAND & CONTACT
    # ============================================================
    BRAND_NAME = "FABS Trading Global E-Commerce"
    WHATSAPP_KENYA = os.getenv("WHATSAPP_KENYA", "254729004000")
    WHATSAPP_GREECE = os.getenv("WHATSAPP_GREECE", "306949147011")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@fabstrading.com")
    TRADING_EMAIL = os.getenv("TRADING_EMAIL", "trade@fabstrading.com")

    # ============================================================
    # CATALOGUE
    # ============================================================
    CATALOGUE_TOTAL = int(os.getenv("CATALOGUE_TOTAL", "2399976"))
    CATALOGUE_MAX_PAGES = int(os.getenv("CATALOGUE_MAX_PAGES", "999"))

    # ============================================================
    # PAYMENTS — BANK MID / DPO
    # ============================================================
    BANK_MID_MODE = os.getenv("BANK_MID_MODE", "sandbox")
    BANK_MID_CHECKOUT_URL = os.getenv("BANK_MID_CHECKOUT_URL", "")
    BANK_MID_MERCHANT_ID = os.getenv("BANK_MID_MERCHANT_ID", "")
    BANK_MID_API_KEY = os.getenv("BANK_MID_API_KEY", "")
    BANK_MID_SIGNING_SECRET = os.getenv("BANK_MID_SIGNING_SECRET", "")
    BANK_MID_WEBHOOK_SECRET = os.getenv("BANK_MID_WEBHOOK_SECRET", "")
    BANK_MID_RETURN_URL = os.getenv("BANK_MID_RETURN_URL", "")
    BANK_MID_CANCEL_URL = os.getenv("BANK_MID_CANCEL_URL", "")

    # ============================================================
    # ADMIN
    # ============================================================
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@fabstrading.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    # ============================================================
    # DHL EXPRESS — SHIPPING & TRACKING
    # ============================================================
    # --- Auth ---
    DHL_API_KEY = os.getenv("DHL_API_KEY", "")
    DHL_API_SECRET = os.getenv("DHL_API_SECRET", "")
    DHL_API_BASE = os.getenv(
        "DHL_API_BASE",
        "https://express.api.dhl.com/mydhlapi",
    )

    # --- Origin (Nairobi warehouse) ---
    DHL_ORIGIN_COUNTRY = os.getenv("DHL_ORIGIN_COUNTRY", "KE")
    DHL_ORIGIN_CITY = os.getenv("DHL_ORIGIN_CITY", "Nairobi")
    DHL_ORIGIN_POSTAL = os.getenv("DHL_ORIGIN_POSTAL", "00100")
    DHL_ORIGIN_ADDRESS = os.getenv("DHL_ORIGIN_ADDRESS", "")
    DHL_ORIGIN_COMPANY = os.getenv(
        "DHL_ORIGIN_COMPANY",
        "FABS Trading Global E-Commerce",
    )
    DHL_ORIGIN_PHONE = os.getenv("DHL_ORIGIN_PHONE", "+254729004000")
    DHL_ORIGIN_EMAIL = os.getenv(
        "DHL_ORIGIN_EMAIL",
        "logistics@fabstrading.com",
    )

    # --- Push API (tracking webhooks) ---
    # Register this URL in the DHL developer portal:
    #     https://your-domain.com/webhooks/dhl/tracking
    DHL_WEBHOOK_SECRET = os.getenv("DHL_WEBHOOK_SECRET", "")
    DHL_WEBHOOK_ENABLED = (
        os.getenv("DHL_WEBHOOK_ENABLED", "true").lower() == "true"
    )

    # --- On-demand refresh throttle (seconds) ---
    # Public /track traffic re-uses a cached status for this long before
    # calling the DHL API again. Prevents quota burn from crawlers.
    DHL_TRACK_REFRESH_SECONDS = int(
        os.getenv("DHL_TRACK_REFRESH_SECONDS", "300")
    )

    # ============================================================
    # FEATURE FLAGS
    # ============================================================
    # Show the "Track shipment" panel to customers on order pages.
    TRACKING_PUBLIC_ENABLED = (
        os.getenv("TRACKING_PUBLIC_ENABLED", "true").lower() == "true"
    )