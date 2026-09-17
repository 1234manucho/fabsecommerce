from datetime import datetime, timezone
from decimal import Decimal
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(180))
    phone = db.Column(db.String(40))
    country = db.Column(db.String(90))
    role = db.Column(db.String(30), default="customer", nullable=False)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, value): self.password_hash = generate_password_hash(value)
    def check_password(self, value): return check_password_hash(self.password_hash, value)
    @property
    def is_admin(self): return self.role == "admin"


class Address(TimestampMixin, db.Model):
    """Saved shipping address belonging to a user — used at checkout."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    label = db.Column(db.String(80), default="Home", nullable=False)
    full_name = db.Column(db.String(140), nullable=False)
    company = db.Column(db.String(180))
    phone = db.Column(db.String(40))
    country = db.Column(db.String(90), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    address_line1 = db.Column(db.String(200), nullable=False)
    address_line2 = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False, nullable=False, index=True)

    user = db.relationship("User", backref=db.backref("addresses", cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "full_name": self.full_name,
            "company": self.company or "",
            "phone": self.phone or "",
            "country": self.country,
            "city": self.city,
            "postal_code": self.postal_code,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2 or "",
            "is_default": bool(self.is_default),
        }


class Game(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    edition = db.Column(db.String(100), default="Standard Edition", nullable=False)
    region = db.Column(db.String(100), default="Global", nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    compare_price = db.Column(db.Numeric(12, 2))
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    trailer_url = db.Column(db.Text)
    minimum_order = db.Column(db.String(80), default="1 Piece (MOQ)", nullable=False)
    supplier = db.Column(db.String(180), default="FABS Verified Supplier", nullable=False)
    photo_source = db.Column(db.String(180), default="Supplier product media", nullable=False)
    stock_count = db.Column(db.Integer, default=0, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # --- Shipping dimensions (used for DHL rate quotes & shipments) ---
    weight_kg = db.Column(db.Float, default=1.0, nullable=True)
    length_cm = db.Column(db.Float, default=30.0, nullable=True)
    width_cm = db.Column(db.Float, default=20.0, nullable=True)
    height_cm = db.Column(db.Float, default=10.0, nullable=True)
    hs_code = db.Column(db.String(20), nullable=True)

    @property
    def discount_percent(self):
        if not self.compare_price or self.compare_price <= self.price: return 0
        return round((1 - Decimal(self.price) / Decimal(self.compare_price)) * 100)


class Commodity(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    name = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    grade = db.Column(db.String(180), nullable=False)
    minimum_order = db.Column(db.String(80), nullable=False)
    unit = db.Column(db.String(60), default="Metric tonne", nullable=False)
    incoterms = db.Column(db.String(120), default="FOB · CFR · CIF", nullable=False)
    description = db.Column(db.Text, nullable=False)
    applications = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Order(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    email = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(140), nullable=False)
    country = db.Column(db.String(90), nullable=False)
    currency = db.Column(db.String(3), default="USD", nullable=False)
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(30), default="pending", index=True, nullable=False)
    payment_status = db.Column(db.String(30), default="unpaid", index=True, nullable=False)
    payment_reference = db.Column(db.String(180))

    # --- Shipping / recipient details (collected at checkout) ---
    company = db.Column(db.String(180), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    address_line1 = db.Column(db.String(200), nullable=True)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)

    # --- DHL shipping state ---
    shipping_status = db.Column(db.String(50), default="pending", nullable=True, index=True)
    dhl_tracking_number = db.Column(db.String(100), nullable=True, index=True)
    dhl_label_url = db.Column(db.String(500), nullable=True)
    dhl_shipment_id = db.Column(db.String(100), nullable=True)
    shipping_cost = db.Column(db.Numeric(12, 2), nullable=True)
    shipping_currency = db.Column(db.String(3), nullable=True)
    shipped_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # --- Package dimensions snapshot (frozen at shipment time) ---
    package_weight_kg = db.Column(db.Float, nullable=True)
    package_length_cm = db.Column(db.Float, nullable=True)
    package_width_cm = db.Column(db.Float, nullable=True)
    package_height_cm = db.Column(db.Float, nullable=True)

    user = db.relationship("User", backref="orders")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False, index=True)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    platform = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    game = db.relationship("Game")


class PaymentTransaction(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False, index=True)
    provider = db.Column(db.String(80), default="bank_mid", nullable=False)
    provider_reference = db.Column(db.String(180), unique=True, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(30), default="initiated", nullable=False)
    masked_pan = db.Column(db.String(30))
    card_brand = db.Column(db.String(30))
    response_code = db.Column(db.String(40))
    raw_status = db.Column(db.String(80))
    order = db.relationship("Order", backref="payments")


class DigitalEntitlement(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(db.Integer, db.ForeignKey("order_item.id"), unique=True, nullable=False)
    delivery_status = db.Column(db.String(30), default="pending", nullable=False)
    encrypted_payload = db.Column(db.Text)
    delivered_at = db.Column(db.DateTime(timezone=True))
    order_item = db.relationship("OrderItem")


class Quote(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    company_name = db.Column(db.String(180), nullable=False)
    contact_name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    incorporation_country = db.Column(db.String(90), nullable=False)
    commodity_id = db.Column(db.Integer, db.ForeignKey("commodity.id"), nullable=False)
    grade = db.Column(db.String(180), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    delivery_country = db.Column(db.String(90), nullable=False)
    destination = db.Column(db.String(140), nullable=False)
    incoterm = db.Column(db.String(10), nullable=False)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(40), default="submitted", index=True, nullable=False)
    assigned_to = db.Column(db.String(140))
    user = db.relationship("User", backref="quotes")
    commodity = db.relationship("Commodity")


class ContactMessage(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, nullable=False)
    full_name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(180))
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="new", nullable=False)


class GameInquiry(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(40), unique=True, index=True, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    full_name = db.Column(db.String(140), nullable=False)
    company = db.Column(db.String(180), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    country = db.Column(db.String(90), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(160), nullable=False)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(40), default="submitted", index=True, nullable=False)
    game = db.relationship("Game", backref="inquiries")
    user = db.relationship("User", backref="game_inquiries")


class WebhookEvent(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(80), nullable=False)
    event_id = db.Column(db.String(180), unique=True, index=True, nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    signature_valid = db.Column(db.Boolean, default=False, nullable=False)
    payload_hash = db.Column(db.String(64), nullable=False)
    processed = db.Column(db.Boolean, default=False, nullable=False)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    action = db.Column(db.String(120), nullable=False)
    entity_type = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.String(80))
    ip_address = db.Column(db.String(80))
    detail = db.Column(db.Text)