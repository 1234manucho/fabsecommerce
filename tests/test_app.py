import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("WTF_CSRF_ENABLED", "false")

from app import create_app
from config import Config
from models import db
from seed import seed_catalogue


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


def test_public_pages_and_catalogue():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all(); seed_catalogue()
        client = app.test_client()
        assert client.get("/").status_code == 200
        assert b"FABS Trading" in client.get("/").data
        assert client.get("/games").status_code == 200
        final_page = client.get("/games?page=999")
        assert final_page.status_code == 200
        assert b"PAGE 999 OF 999" in final_page.data
        assert b"2,399,976" in final_page.data
        assert b"+254 729 004 000" in client.get("/").data
        assert b"+30 694 914 7011" in client.get("/").data
        assert client.get("/commodities").status_code == 200
        for path in ["/industries", "/logistics", "/quality", "/sustainability", "/partners", "/investors", "/careers", "/digital-delivery", "/corporate-sales", "/news", "/news/hosted-checkout-security"]:
            assert client.get(path).status_code == 200
        assert client.get("/health").json["status"] == "ok"


def test_quote_submission():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all(); seed_catalogue()
        client = app.test_client()
        response = client.post("/request-quote", data={"company_name":"FABS Test Buyer","contact_name":"Test Person","email":"test@example.com","phone":"+254700000000","incorporation_country":"Kenya","commodity_id":"1","grade":"60/70","quantity":"500 MT","delivery_country":"Kenya","destination":"Mombasa","incoterm":"CIF","confirm":"y"})
        assert response.status_code == 200
        assert b"RFQ RECEIVED" in response.data


def test_game_inquiry_submission():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all(); seed_catalogue()
        client = app.test_client()
        response = client.post("/games/hologate-vr-arcade/inquiry", data={"product_id":"1","full_name":"Test Buyer","company":"Buyer Limited","email":"buyer@example.com","phone":"+254700000000","country":"Kenya","quantity":"1 Set (MOQ)","destination":"Nairobi","requirements":"Commercial VR venue installation and operator training.","confirm":"y"})
        assert response.status_code == 200
        assert b"INQUIRY RECEIVED" in response.data
        assert b"FABS-INQ-" in response.data
