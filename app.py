import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, abort, flash, jsonify, redirect, render_template,
    request, session, url_for,
)
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user,
)
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from forms import (
    CheckoutForm, ContactForm, GameForm, GameInquiryForm, LoginForm, RegisterForm,
)
from models import (
    Address, AuditLog, ContactMessage, DigitalEntitlement, Game, GameInquiry,
    Order, OrderItem, PaymentTransaction, Quote, User, WebhookEvent, db,
)
from seed import seed_catalogue
from services.dpo import DPOGateway, PaymentConfigurationError
from services.dhl import DHLService, DHLConfigurationError, DHLAPIError

MEDIA_PAGES = {
    "industries": {"eyebrow":"Gaming categories", "title":"Gaming products for retail, leisure and commercial venues.", "lead":"FABS connects buyers with carefully presented tabletop, arcade, redemption, racing, sports and immersive gaming products.", "image":"https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1800&q=85", "sections":[("Arcade & redemption","Coin-operated, prize, shooting and interactive cabinets for entertainment venues."),("Racing & simulation","Driving, sports and motion-based simulators for high-engagement experiences."),("Tabletop & recreation","Board, card, educational and recreational games for retail and group use.")]},
    "logistics": {"eyebrow":"Gaming delivery", "title":"Every gaming order follows a documented delivery plan.", "lead":"Product configuration, packing, freight, delivery milestones and destination handover are confirmed before fulfilment.", "image":"https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1800&q=85", "sections":[("Order readiness","Confirm model, cabinet, voltage, accessories, quantity and packing requirements."),("Delivery visibility","Track preparation, dispatch and arrival against the agreed fulfilment plan."),("Controlled handover","Verify the delivered gaming product, accessories and supporting documentation.")]},
    "quality": {"eyebrow":"Gaming quality", "title":"Specifications before purchase.", "lead":"Gaming products are reviewed against their model, configuration, condition, compatibility and intended commercial use.", "image":"https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1800&q=85", "sections":[("Product verification","Confirm the title, model, platform, cabinet and technical configuration."),("Supplier evidence","Review available product media, specifications, warranty and supplier information."),("After-sales planning","Define installation, spare-parts and support expectations before approval.")]},
    "sustainability": {"eyebrow":"Responsible gaming commerce", "title":"Better product decisions create longer service life.", "lead":"FABS supports documented product selection, practical order quantities and responsible equipment lifecycle planning.", "image":"https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1800&q=85", "sections":[("Right-sized orders","Match quantities and specifications to the buyer's real operating requirements."),("Durability review","Consider product construction, serviceability and available support."),("Lifecycle planning","Plan maintenance, accessories and responsible replacement of gaming equipment.")]},
    "partners": {"eyebrow":"Gaming partnerships", "title":"A gaming network built around clear responsibilities.", "lead":"Publishers, manufacturers, venue operators, payment providers and fulfilment partners support the FABS gaming marketplace.", "image":"https://images.unsplash.com/photo-1521737711867-e3b97375f902?auto=format&fit=crop&w=1800&q=85", "sections":[("Gaming ecosystem","Publishers, manufacturers and suppliers supporting the product catalogue."),("Venue ecosystem","Arcades, entertainment centres, retailers and corporate buyers."),("Payment ecosystem","Approved providers supporting secure checkout and transaction reconciliation.")]},
    "investors": {"eyebrow":"Investor information", "title":"A scalable gaming-commerce platform.", "lead":"FABS combines a structured gaming catalogue, commercial enquiries, secure checkout and managed fulfilment.", "image":"https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1800&q=85", "sections":[("Gaming marketplace","Search, product discovery, quotation, account and order-management capabilities."),("Commercial workflow","Product enquiries, supplier confirmation, checkout and fulfilment."),("Shared controls","Finance, risk, data, access management and customer support.")]},
    "careers": {"eyebrow":"Careers", "title":"Build gaming commerce that earns confidence.", "lead":"We value people who make gaming discovery, purchasing and fulfilment dependable for every buyer.", "image":"https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1800&q=85", "sections":[("Technology & product","Build reliable catalogue, account, quotation and checkout experiences."),("Gaming operations","Translate product requirements into controlled sourcing and fulfilment."),("Risk & customer trust","Strengthen verification, service quality and issue resolution.")]},
    "digital-delivery": {"eyebrow":"FABS Games", "title":"From checkout to your next world.", "lead":"Compatibility checks before payment and activation guidance after authorisation.", "image":"https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1800&q=85", "video":"https://videos.pexels.com/video-files/7774512/7774512-uhd_3840_2160_30fps.mp4", "sections":[("Confirm compatibility","Review platform, edition, region and activation requirements."),("Authorise securely","Card entry occurs on the approved bank-hosted checkout."),("Access fulfilment","Verified orders receive delivery instructions online.")]},
    "corporate-sales": {"eyebrow":"Corporate gaming sales", "title":"Gaming products for managed programmes and venues.", "lead":"A structured enquiry route for arcades, entertainment centres, retailers, incentives and organised events.", "image":"https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1800&q=85", "sections":[("Define the requirement","Identify the audience, venue, product mix, quantity, timing and budget."),("Confirm availability","Review gaming product specifications, supplier availability and regional requirements."),("Document fulfilment","Agree delivery, installation, support and exception-handling responsibilities.")]},
}

NEWS_ARTICLES = {
    "gaming-venue-buyers-guide": ("Gaming insight", "Choosing the right products for an entertainment venue", "Match the game category, audience, floor space, power requirements, budget and support plan before placing an order.", "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1800&q=85"),
    "hosted-checkout-security": ("Payments", "Why hosted checkout matters", "A bank-hosted page separates sensitive card capture from the merchant application and returns a signed transaction result.", "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=1800&q=85"),
    "digital-game-compatibility": ("Digital", "Buying the correct game edition", "Check the platform, device generation, edition, region and activation method before payment.", "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=1800&q=85"),
}

load_dotenv()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
DEFAULT_USD_KES_RATE = Decimal("130.00")
CATALOGUE_PAGE_SIZE = 8

DEFAULT_SHIP_ORIGIN_COUNTRY = os.getenv("DHL_ORIGIN_COUNTRY", "KE")
DEFAULT_SHIP_ORIGIN_CITY = os.getenv("DHL_ORIGIN_CITY", "Nairobi")
DEFAULT_SHIP_ORIGIN_POSTAL = os.getenv("DHL_ORIGIN_POSTAL", "00100")


def _positive_decimal(value, default=DEFAULT_USD_KES_RATE):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default
    return number if number.is_finite() and number > 0 else default


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Sign in to continue."

    usd_kes_rate = _positive_decimal(
        app.config.get("USD_KES_RATE", os.getenv("USD_KES_RATE", "130.00"))
    ).quantize(Decimal("0.01"))
    app.config["USD_KES_RATE"] = usd_kes_rate

    @app.template_filter("money_usd")
    def money_usd(value):
        amount = _positive_decimal(value, Decimal("0.00"))
        return f"US$ {amount:,.2f}"

    @app.template_filter("money_kes")
    def money_kes(value):
        amount = _positive_decimal(value, Decimal("0.00"))
        converted = (amount * app.config["USD_KES_RATE"]).quantize(Decimal("1"))
        return f"KES {converted:,.0f}"

    @app.template_filter("usd_to_kes")
    def usd_to_kes(value):
        amount = _positive_decimal(value, Decimal("0.00"))
        return (amount * app.config["USD_KES_RATE"]).quantize(Decimal("1"))

    @app.context_processor
    def inject_globals():
        cart_ids = session.get("cart", [])
        return {
            "brand_name": app.config["BRAND_NAME"],
            "cart_count": len(cart_ids),
            "current_year": datetime.now().year,
            "support_email": app.config["SUPPORT_EMAIL"],
            "whatsapp_kenya": app.config["WHATSAPP_KENYA"],
            "whatsapp_greece": app.config["WHATSAPP_GREECE"],
            "usd_kes_rate": app.config["USD_KES_RATE"],
            "primary_display_currency": "KES",
            "secondary_display_currency": "USD",
        }

    register_routes(app)
    register_cli(app)
    register_errors(app)
    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def make_reference(prefix):
    return f"FABS-{prefix}-{datetime.now(timezone.utc):%y%m%d}-{secrets.token_hex(3).upper()}"


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def audit(action, entity_type, entity_id=None, detail=None):
    db.session.add(AuditLog(
        actor_user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        ip_address=request.headers.get("CF-Connecting-IP", request.remote_addr),
        detail=detail,
    ))


def _compute_order_shipping_dims(order) -> dict:
    total_weight = 0.0
    max_length = 0.0
    max_width = 0.0
    total_height = 0.0

    for item in order.items:
        game = getattr(item, "game", None)
        weight = float(getattr(game, "weight_kg", None) or 1.0)
        length = float(getattr(game, "length_cm", None) or 30.0)
        width  = float(getattr(game, "width_cm", None) or 20.0)
        height = float(getattr(game, "height_cm", None) or 10.0)

        qty = int(item.quantity or 1)
        total_weight += weight * qty
        max_length = max(max_length, length)
        max_width  = max(max_width, width)
        total_height += height * qty

    return {
        "weight_kg": round(total_weight or 1.0, 2),
        "length_cm": round(max_length or 30.0, 1),
        "width_cm":  round(max_width or 20.0, 1),
        "height_cm": round(total_height or 10.0, 1),
    }


def _compute_cart_shipping_dims(items) -> dict:
    total_weight = 0.0
    max_length = 30.0
    max_width = 20.0
    total_height = 0.0
    declared_value = 0.0

    for game in items:
        qty = 1
        weight = float(getattr(game, "weight_kg", None) or 1.0)
        length = float(getattr(game, "length_cm", None) or 30.0)
        width  = float(getattr(game, "width_cm", None) or 20.0)
        height = float(getattr(game, "height_cm", None) or 10.0)

        total_weight += weight * qty
        max_length = max(max_length, length)
        max_width  = max(max_width, width)
        total_height += height * qty
        declared_value += float(game.price or 0)

    return {
        "weight_kg": round(total_weight or 1.0, 2),
        "length_cm": round(max_length, 1),
        "width_cm":  round(max_width, 1),
        "height_cm": round(total_height or 10.0, 1),
        "declared_value": round(declared_value or 100.0, 2),
    }


# ============ FIX: Friendly handling for DHL "unquotable destination" ============
# DHL returns 400 / 420505 for destinations it cannot quote from our origin
# (e.g. unmapped codes like AG, or domestic KE). These are informational, not
# server errors, so we surface a friendly message with a 200 response. This
# pairs with the amber "is-info" styling added to the shipping widgets in
# cart.html, games.html and game_detail.html.
#
# Markers broadened to catch the wider set of DHL rejection messages:
#   - "420505: The destination location is invalid"
#   - "no products available"
#   - "no services available"
_DHL_UNQUOTABLE_MARKERS = (
    "420505",
    "destination location is invalid",
    "no products available",
    "no services available",
)


def _is_dhl_unquotable(exc) -> bool:
    """True when a DHLAPIError is the 'destination not servable' case."""
    blob = f"{exc} {getattr(exc, 'response_body', '') or ''}".lower()
    return any(marker in blob for marker in _DHL_UNQUOTABLE_MARKERS)


def _friendly_shipping_fallback(country_code: str) -> str:
    """Friendly plain-text message for destinations DHL cannot quote."""
    code = (country_code or "").strip().upper()
    if code == DEFAULT_SHIP_ORIGIN_COUNTRY:
        return "Domestic Kenya delivery — quoted separately."
    return "Shipping to this destination is quoted on request."
# ===============================================================================


def register_routes(app):
    # ================================================================
    # PUBLIC PAGES
    # ================================================================
    @app.get("/")
    def index():
        featured = (
            Game.query.filter_by(is_active=True)
            .order_by(Game.is_featured.desc(), Game.price.asc(), Game.id.asc())
            .limit(CATALOGUE_PAGE_SIZE)
            .all()
        )
        return render_template("index.html", games=featured, commodities=[])

    @app.get("/games")
    def games():
        query = request.args.get("q", "").strip()
        platform = request.args.get("platform", "").strip()
        category = request.args.get("category", "").strip()
        try:
            page = max(1, int(request.args.get("page", "1")))
        except (TypeError, ValueError):
            page = 1
        products = Game.query.filter_by(is_active=True)
        if query:
            products = products.filter(
                db.or_(
                    Game.title.ilike(f"%{query}%"),
                    Game.genre.ilike(f"%{query}%"),
                    Game.supplier.ilike(f"%{query}%"),
                )
            )
        if platform:
            products = products.filter(Game.platform.ilike(f"%{platform}%"))
        if category:
            products = products.filter(Game.genre.ilike(f"%{category}%"))

        catalogue_total = products.count()
        total_pages = max(1, (catalogue_total + CATALOGUE_PAGE_SIZE - 1) // CATALOGUE_PAGE_SIZE)
        page = min(page, total_pages)
        catalogue = (
            products.order_by(Game.price.asc(), Game.id.asc())
            .offset((page - 1) * CATALOGUE_PAGE_SIZE)
            .limit(CATALOGUE_PAGE_SIZE)
            .all()
        )
        return render_template(
            "games.html",
            games=catalogue,
            query=query,
            platform=platform,
            category=category,
            page=page,
            total_pages=total_pages,
            catalogue_total=catalogue_total,
        )

    @app.get("/games/<slug>")
    def game_detail(slug):
        return render_template("game_detail.html", game=Game.query.filter_by(slug=slug, is_active=True).first_or_404())

    @app.route("/games/<slug>/inquiry", methods=["GET", "POST"])
    def game_inquiry(slug):
        game = Game.query.filter_by(slug=slug, is_active=True).first_or_404()
        form = GameInquiryForm()
        form.product_id.choices = [(game.id, game.title)]
        if request.method == "GET":
            form.product_id.data = game.id
            form.quantity.data = game.minimum_order
            if current_user.is_authenticated:
                form.full_name.data = current_user.full_name
                form.company.data = current_user.company
                form.email.data = current_user.email
                form.phone.data = current_user.phone
                form.country.data = current_user.country
        if form.validate_on_submit():
            inquiry = GameInquiry(
                reference=make_reference("INQ"),
                game_id=game.id,
                user_id=current_user.id if current_user.is_authenticated else None,
                full_name=form.full_name.data,
                company=form.company.data,
                email=form.email.data.lower(),
                phone=form.phone.data,
                country=form.country.data,
                quantity=form.quantity.data,
                destination=form.destination.data,
                requirements=form.requirements.data,
            )
            db.session.add(inquiry)
            audit("game_inquiry_submitted", "game_inquiry", detail=inquiry.reference)
            db.session.commit()
            return render_template("inquiry_success.html", inquiry=inquiry, game=game)
        return render_template("game_inquiry.html", form=form, game=game)

    @app.route("/inquiry", methods=["GET", "POST"])
    def inquiry():
        products = Game.query.filter_by(is_active=True).order_by(Game.title).all()
        form = GameInquiryForm()
        form.product_id.choices = [(item.id, item.title) for item in products]
        requested_slug = request.args.get("product")
        if request.method == "GET":
            selected = next((item for item in products if item.slug == requested_slug), products[0] if products else None)
            if selected:
                form.product_id.data = selected.id
                form.quantity.data = selected.minimum_order
            if current_user.is_authenticated:
                form.full_name.data = current_user.full_name
                form.company.data = current_user.company
                form.email.data = current_user.email
                form.phone.data = current_user.phone
                form.country.data = current_user.country
        if form.validate_on_submit():
            game = Game.query.filter_by(id=form.product_id.data, is_active=True).first_or_404()
            inquiry_record = GameInquiry(
                reference=make_reference("INQ"),
                game_id=game.id,
                user_id=current_user.id if current_user.is_authenticated else None,
                full_name=form.full_name.data,
                company=form.company.data,
                email=form.email.data.lower(),
                phone=form.phone.data,
                country=form.country.data,
                quantity=form.quantity.data,
                destination=form.destination.data,
                requirements=form.requirements.data,
            )
            db.session.add(inquiry_record)
            audit("game_inquiry_submitted", "game_inquiry", detail=inquiry_record.reference)
            db.session.commit()
            return render_template("inquiry_success.html", inquiry=inquiry_record, game=game)
        return render_template("game_inquiry.html", form=form, game=None)

    # ================================================================
    # CART
    # ================================================================
    @app.post("/cart/add/<int:game_id>")
    def add_to_cart(game_id):
        Game.query.filter_by(id=game_id, is_active=True).first_or_404()
        cart = session.get("cart", [])
        if game_id not in cart:
            cart.append(game_id)
        session["cart"] = cart
        session.modified = True

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"status": "ok", "cart_count": len(cart)})

        flash("Game added to your cart.", "success")
        return redirect(url_for("cart"))

    @app.post("/cart/remove/<int:game_id>")
    def remove_from_cart(game_id):
        session["cart"] = [item for item in session.get("cart", []) if item != game_id]
        flash("Item removed.", "info")
        return redirect(url_for("cart"))

    @app.get("/cart")
    def cart():
        items = (
            Game.query.filter(
                Game.id.in_(session.get("cart", []) or [-1]),
                Game.is_active.is_(True),
            )
            .order_by(Game.price.asc(), Game.id.asc())
            .all()
        )
        total = sum((item.price for item in items), Decimal("0.00"))
        return render_template("cart.html", items=items, total=total)

    # ================================================================
    # CHECKOUT
    # ================================================================
    @app.route("/checkout", methods=["GET", "POST"])
    def checkout():
        items = (
            Game.query.filter(
                Game.id.in_(session.get("cart", []) or [-1]),
                Game.is_active.is_(True),
            )
            .order_by(Game.price.asc(), Game.id.asc())
            .all()
        )
        if not items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("games"))

        subtotal = sum((item.price for item in items), Decimal("0.00"))

        form = CheckoutForm()
        if current_user.is_authenticated and request.method == "GET":
            form.full_name.data = current_user.full_name
            form.email.data = current_user.email
            form.country.data = (current_user.country or "").strip()
            form.company.data = current_user.company
            form.phone.data = current_user.phone

        if form.validate_on_submit():
            shipping_cost = Decimal("0.00")
            shipping_currency = "USD"
            raw_quote = (form.shipping_quote.data or "").strip()
            if raw_quote:
                try:
                    parsed = json.loads(raw_quote)
                    shipping_cost = Decimal(str(parsed.get("cost_usd") or 0)).quantize(Decimal("0.01"))
                    shipping_currency = "USD"
                except (json.JSONDecodeError, InvalidOperation, TypeError, ValueError):
                    app.logger.warning("Invalid shipping_quote payload: %r", raw_quote)
                    shipping_cost = Decimal("0.00")

            grand_total = (subtotal + shipping_cost).quantize(Decimal("0.01"))

            order = Order(
                reference=make_reference("GM"),
                user_id=current_user.id if current_user.is_authenticated else None,
                email=form.email.data.lower(),
                full_name=form.full_name.data,
                country=(form.country.data or "").upper(),
                currency=app.config.get("BASE_CURRENCY", "USD"),
                subtotal=subtotal,
                total=grand_total,
                company=(form.company.data or None),
                phone=(form.phone.data or None),
                address_line1=(form.address_line1.data or None),
                address_line2=(form.address_line2.data or None),
                city=(form.city.data or None),
                postal_code=(form.postal_code.data or None),
                shipping_cost=shipping_cost if shipping_cost > 0 else None,
                shipping_currency=shipping_currency if shipping_cost > 0 else None,
                shipping_status="pending",
            )
            db.session.add(order)
            db.session.flush()

            for item in items:
                order.items.append(
                    OrderItem(
                        game_id=item.id,
                        title=item.title,
                        platform=item.platform,
                        unit_price=item.price,
                        quantity=1,
                    )
                )

            audit("order_created", "order", order.id, order.reference)
            db.session.commit()

            session.pop("cart", None)
            session["last_order_reference"] = order.reference
            return redirect(url_for("start_payment", order_id=order.id))

        return render_template("checkout.html", form=form, items=items, total=subtotal)

    # ================================================================
    # DHL SHIPPING — RATE QUOTES
    # ================================================================
    @app.post("/api/shipping/rates")
    def api_shipping_rates():
        data = request.get_json(silent=True) or {}
        country = (data.get("country") or "").strip().upper()
        if not country:
            return jsonify({"error": "country is required"}), 400

        # ============ FIX: short-circuit domestic origin ============
        # DHL does not quote domestic Kenya delivery through the
        # international rates API. Return the friendly message before
        # calling DHL so we avoid a guaranteed-to-fail API request and
        # a false-positive error log entry.
        if country == DEFAULT_SHIP_ORIGIN_COUNTRY:
            app.logger.info(
                "Domestic origin destination %s — returning friendly message", country
            )
            return jsonify({
                "products": [],
                "message": _friendly_shipping_fallback(country),
            }), 200
        # =============================================================

        try:
            service = DHLService()
        except DHLConfigurationError as exc:
            app.logger.error("DHL configuration: %s", exc)
            return jsonify({"error": "Shipping rates are temporarily unavailable."}), 503

        try:
            result = service.get_rates(
                origin_country=DEFAULT_SHIP_ORIGIN_COUNTRY,
                origin_city=DEFAULT_SHIP_ORIGIN_CITY,
                origin_postal_code=DEFAULT_SHIP_ORIGIN_POSTAL,
                destination_country=country,
                destination_city=(data.get("city") or "").strip() or None,
                destination_postal_code=(data.get("postal_code") or "").strip() or None,
                weight_kg=float(data.get("weight_kg") or 1.0),
                length_cm=float(data.get("length_cm") or 30.0),
                width_cm=float(data.get("width_cm") or 20.0),
                height_cm=float(data.get("height_cm") or 10.0),
                declared_value=float(data.get("declared_value") or 100.0),
                currency=(data.get("currency") or "USD").upper(),
            )
        # ============ FIX: DHLAPIError with friendly fallback ============
        except DHLAPIError as exc:
            if _is_dhl_unquotable(exc):
                app.logger.info(
                    "DHL cannot quote destination %s — returning friendly message", country
                )
                return jsonify({
                    "products": [],
                    "message": _friendly_shipping_fallback(country),
                }), 200
            app.logger.exception("DHL rate lookup failed: %s", exc)
            return jsonify({"error": "Could not fetch shipping rates."}), 502
        # =================================================================
        except Exception as exc:
            app.logger.exception("DHL rate lookup failed: %s", exc)
            return jsonify({"error": "Could not fetch shipping rates."}), 502

        if not result:
            return jsonify({"error": "No rates returned by DHL."}), 502

        return jsonify(result)

    @app.get("/api/shipping/rates/cart")
    def api_shipping_rates_for_cart():
        country = (request.args.get("country") or "").strip().upper()
        if not country:
            return jsonify({"error": "country is required"}), 400

        # ============ FIX: short-circuit domestic origin ============
        # Same reasoning as the POST endpoint: KE→KE is not quotable
        # through DHL's international rates API.
        if country == DEFAULT_SHIP_ORIGIN_COUNTRY:
            app.logger.info(
                "Domestic origin cart destination %s — returning friendly message", country
            )
            return jsonify({
                "products": [],
                "message": _friendly_shipping_fallback(country),
            }), 200
        # =============================================================

        items = (
            Game.query.filter(
                Game.id.in_(session.get("cart", []) or [-1]),
                Game.is_active.is_(True),
            )
            .all()
        )
        if not items:
            return jsonify({"error": "Cart is empty."}), 400

        dims = _compute_cart_shipping_dims(items)

        try:
            service = DHLService()
            result = service.get_rates(
                origin_country=DEFAULT_SHIP_ORIGIN_COUNTRY,
                origin_city=DEFAULT_SHIP_ORIGIN_CITY,
                origin_postal_code=DEFAULT_SHIP_ORIGIN_POSTAL,
                destination_country=country,
                weight_kg=dims["weight_kg"],
                length_cm=dims["length_cm"],
                width_cm=dims["width_cm"],
                height_cm=dims["height_cm"],
                declared_value=dims["declared_value"],
                currency="USD",
            )
        except DHLConfigurationError as exc:
            app.logger.error("DHL configuration: %s", exc)
            return jsonify({"error": "Shipping rates are temporarily unavailable."}), 503
        # ============ FIX: DHLAPIError with friendly fallback ============
        except DHLAPIError as exc:
            if _is_dhl_unquotable(exc):
                app.logger.info(
                    "DHL cannot quote cart destination %s — returning friendly message", country
                )
                return jsonify({
                    "products": [],
                    "message": _friendly_shipping_fallback(country),
                }), 200
            app.logger.exception("DHL cart rates failed: %s", exc)
            return jsonify({"error": "Could not fetch shipping rates."}), 502
        # =================================================================
        except Exception as exc:
            app.logger.exception("DHL cart rates failed: %s", exc)
            return jsonify({"error": "Could not fetch shipping rates."}), 502

        if not result:
            return jsonify({"error": "No rates returned by DHL."}), 502

        return jsonify(result)

    # ================================================================
    # DHL SHIPPING — EXTENDED APIs
    # ================================================================
    @app.get("/api/shipping/<tracking_number>/pod")
    def api_proof_of_delivery(tracking_number):
        try:
            result = DHLService().get_proof_of_delivery(tracking_number)
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL ePOD failed: %s", exc)
            return jsonify({"error": "Could not fetch proof of delivery."}), 502
        return jsonify(result)

    @app.post("/api/shipping/validate-address")
    def api_validate_address():
        data = request.get_json(silent=True) or {}
        country = (data.get("country") or "").strip().upper()
        if not country:
            return jsonify({"error": "country is required"}), 400
        try:
            result = DHLService().validate_address(
                country_code=country,
                city_name=(data.get("city") or "").strip() or None,
                postal_code=(data.get("postal_code") or "").strip() or None,
                address_line1=(data.get("address_line1") or "").strip() or None,
            )
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL address validation failed: %s", exc)
            return jsonify({"error": "Could not validate address."}), 502
        return jsonify(result)

    @app.post("/api/shipping/landing-cost")
    def api_landing_cost():
        data = request.get_json(silent=True) or {}
        country = (data.get("country") or "").strip().upper()
        if not country:
            return jsonify({"error": "country is required"}), 400
        try:
            result = DHLService().estimate_landing_cost(
                origin_country=DEFAULT_SHIP_ORIGIN_COUNTRY,
                destination_country=country,
                weight_kg=float(data.get("weight_kg") or 1.0),
                length_cm=float(data.get("length_cm") or 30.0),
                width_cm=float(data.get("width_cm") or 20.0),
                height_cm=float(data.get("height_cm") or 10.0),
                declared_value=float(data.get("declared_value") or 100.0),
                currency=(data.get("currency") or "USD").upper(),
            )
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL landing cost failed: %s", exc)
            return jsonify({"error": "Could not estimate landing cost."}), 502
        return jsonify(result)

    @app.get("/api/shipping/landing-cost/cart")
    def api_landing_cost_for_cart():
        country = (request.args.get("country") or "").strip().upper()
        if not country:
            return jsonify({"error": "country is required"}), 400

        items = (
            Game.query.filter(
                Game.id.in_(session.get("cart", []) or [-1]),
                Game.is_active.is_(True),
            )
            .all()
        )
        if not items:
            return jsonify({"error": "Cart is empty."}), 400

        dims = _compute_cart_shipping_dims(items)

        try:
            result = DHLService().estimate_landing_cost(
                origin_country=DEFAULT_SHIP_ORIGIN_COUNTRY,
                destination_country=country,
                weight_kg=dims["weight_kg"],
                length_cm=dims["length_cm"],
                width_cm=dims["width_cm"],
                height_cm=dims["height_cm"],
                declared_value=dims["declared_value"],
                currency="USD",
            )
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL cart landing cost failed: %s", exc)
            return jsonify({"error": "Could not estimate landing cost."}), 502
        return jsonify(result)

    @app.get("/api/shipping/products")
    def api_shipping_products():
        country = (request.args.get("country") or DEFAULT_SHIP_ORIGIN_COUNTRY).strip().upper()
        try:
            result = DHLService().list_products(country_code=country)
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL product list failed: %s", exc)
            return jsonify({"error": "Could not fetch products."}), 502
        return jsonify(result)

    @app.get("/api/shipping/<tracking_number>/documents")
    def api_shipping_documents(tracking_number):
        doc_type = (request.args.get("type") or "label").strip()
        try:
            result = DHLService().get_shipment_documents(tracking_number, doc_type=doc_type)
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL document download failed: %s", exc)
            return jsonify({"error": "Could not fetch documents."}), 502
        return jsonify(result)

    @app.get("/api/shipping/countries")
    def api_shipping_countries():
        try:
            result = DHLService().list_countries()
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL countries list failed: %s", exc)
            return jsonify({"error": "Could not fetch countries."}), 502
        return jsonify(result)

    @app.get("/api/shipping/service-points")
    def api_service_points():
        country = (request.args.get("country") or "").strip().upper()
        if not country:
            return jsonify({"error": "country is required"}), 400
        try:
            result = DHLService().find_service_points(
                country_code=country,
                city=request.args.get("city"),
                postal_code=request.args.get("postal_code"),
                radius_km=int(request.args.get("radius") or 10),
            )
        except DHLConfigurationError:
            return jsonify({"error": "DHL not configured."}), 503
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL service point search failed: %s", exc)
            return jsonify({"error": "Could not search service points."}), 502
        return jsonify(result)

    # ================================================================
    # DHL SHIPPING — ADMIN
    # ================================================================
    @app.post("/admin/orders/<int:order_id>/create-shipment")
    @admin_required
    def admin_create_shipment(order_id):
        order = Order.query.get_or_404(order_id)

        if getattr(order, "dhl_tracking_number", None):
            flash("A shipment already exists for this order.", "warning")
            return redirect(url_for("admin_orders"))

        address_line1 = getattr(order, "address_line1", None)
        city = getattr(order, "city", None)
        postal_code = getattr(order, "postal_code", None)

        if not (address_line1 and city and postal_code):
            flash("Order is missing shipping address details. Add them before creating a shipment.", "danger")
            return redirect(url_for("admin_orders"))

        dims = _compute_order_shipping_dims(order)

        order_data = {
            "order_reference": order.reference,
            "receiver_full_name": order.full_name,
            "receiver_email": order.email,
            "receiver_phone": getattr(order, "phone", None) or "+254700000000",
            "receiver_company": getattr(order, "company", None) or "",
            "receiver_address_line1": address_line1,
            "receiver_address_line2": getattr(order, "address_line2", None) or "",
            "receiver_city": city,
            "receiver_postal_code": postal_code,
            "receiver_country": (order.country or "").upper(),
            "package_weight_kg": dims["weight_kg"],
            "package_length_cm": dims["length_cm"],
            "package_width_cm": dims["width_cm"],
            "package_height_cm": dims["height_cm"],
            "declared_value": float(order.total or 0),
            "currency": order.currency or "USD",
            "package_description": "Gaming products",
        }

        try:
            service = DHLService()
            result = service.create_shipment(order_data)
        except DHLConfigurationError as exc:
            app.logger.error("DHL configuration: %s", exc)
            flash("DHL is not configured. Contact support.", "danger")
            return redirect(url_for("admin_orders"))
        except DHLAPIError as exc:
            app.logger.exception("DHL create shipment failed: %s", exc)
            flash(f"DHL error: {exc}", "danger")
            return redirect(url_for("admin_orders"))
        except Exception as exc:
            app.logger.exception("DHL create shipment failed: %s", exc)
            flash("Could not create DHL shipment. Check the logs for details.", "danger")
            return redirect(url_for("admin_orders"))

        tracking_number = None
        label_url = None

        if result:
            tracking_number = result.get("shipmentTrackingNumber") or result.get("trackingNumber")
            documents = result.get("documents") or []
            if documents:
                label_url = documents[0].get("url") or documents[0].get("content")

        if tracking_number:
            order.dhl_tracking_number = tracking_number
            order.dhl_label_url = label_url
            order.shipping_status = "created"
            order.shipped_at = datetime.now(timezone.utc)
            order.package_weight_kg = dims["weight_kg"]
            order.package_length_cm = dims["length_cm"]
            order.package_width_cm = dims["width_cm"]
            order.package_height_cm = dims["height_cm"]

            audit("dhl_shipment_created", "order", order.id, tracking_number)
            db.session.commit()
            flash(f"DHL shipment created. Tracking: {tracking_number}", "success")
        else:
            flash("DHL did not return a tracking number. Check the API response.", "danger")

        return redirect(url_for("admin_orders"))

    @app.get("/admin/orders/<int:order_id>/tracking")
    @admin_required
    def admin_order_tracking(order_id):
        order = Order.query.get_or_404(order_id)
        tracking_number = getattr(order, "dhl_tracking_number", None)

        if not tracking_number:
            return jsonify({"error": "No tracking number for this order."}), 404

        try:
            service = DHLService()
            result = service.track_shipment(tracking_number)
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL tracking failed: %s", exc)
            return jsonify({"error": "Could not fetch tracking info."}), 502

        if not result:
            return jsonify({"error": "No tracking data."}), 502

        return jsonify(result)

    @app.post("/admin/orders/<int:order_id>/request-pickup")
    @admin_required
    def admin_request_pickup(order_id):
        order = Order.query.get_or_404(order_id)
        if not getattr(order, "dhl_tracking_number", None):
            flash("Create the DHL shipment first.", "warning")
            return redirect(url_for("admin_orders"))

        dims = _compute_order_shipping_dims(order)
        try:
            result = DHLService().create_pickup({
                "planned_pickup_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
                "close_time": "18:00",
                "weight_kg": dims["weight_kg"],
                "length_cm": dims["length_cm"],
                "width_cm": dims["width_cm"],
                "height_cm": dims["height_cm"],
                "pieces": 1,
            })
            pickup_id = None
            if isinstance(result, dict):
                nums = result.get("dispatchConfirmationNumbers") or []
                pickup_id = nums[0] if nums else result.get("dispatchConfirmationNumber")
            if pickup_id:
                audit("dhl_pickup_requested", "order", order.id, pickup_id)
                db.session.commit()
                flash(f"DHL pickup requested. Confirmation: {pickup_id}", "success")
            else:
                flash("Pickup created but no confirmation ID returned.", "warning")
        except DHLAPIError as exc:
            app.logger.exception("DHL pickup failed")
            flash(f"Pickup failed: {exc}", "danger")
        except Exception as exc:
            app.logger.exception("DHL pickup failed: %s", exc)
            flash("Could not request pickup. See logs.", "danger")
        return redirect(url_for("admin_orders"))

    @app.post("/admin/pickups/<pickup_id>/cancel")
    @admin_required
    def admin_cancel_pickup(pickup_id):
        try:
            DHLService().cancel_pickup(pickup_id)
            audit("dhl_pickup_cancelled", "pickup", pickup_id)
            db.session.commit()
            flash(f"Pickup {pickup_id} cancelled.", "success")
        except DHLAPIError as exc:
            app.logger.exception("DHL cancel pickup failed")
            flash(f"Cancel failed: {exc}", "danger")
        except Exception as exc:
            app.logger.exception("DHL cancel pickup failed: %s", exc)
            flash("Could not cancel pickup. See logs.", "danger")
        return redirect(url_for("admin_orders"))

    @app.post("/admin/orders/<int:order_id>/update-shipment")
    @admin_required
    def admin_update_shipment(order_id):
        order = Order.query.get_or_404(order_id)
        if not getattr(order, "dhl_tracking_number", None):
            return jsonify({"error": "No DHL tracking number."}), 400
        update_data = request.get_json(silent=True) or {}
        try:
            result = DHLService().update_shipment(order.dhl_tracking_number, update_data)
            audit("dhl_shipment_updated", "order", order.id, order.dhl_tracking_number)
            db.session.commit()
        except DHLAPIError as exc:
            return jsonify({"error": str(exc), "detail": exc.response_body}), exc.status_code or 502
        except Exception as exc:
            app.logger.exception("DHL shipment update failed: %s", exc)
            return jsonify({"error": "Could not update shipment."}), 502
        return jsonify(result)

    # ================================================================
    # PAYMENTS (DPO)
    # ================================================================
    @app.get("/payments/start/<int:order_id>")
    def start_payment(order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id:
            if not current_user.is_authenticated:
                abort(403)
            if order.user_id != current_user.id and not current_user.is_admin:
                abort(403)
        elif session.get("last_order_reference") != order.reference:
            abort(403)

        try:
            checkout_session = DPOGateway().create_checkout(order)
        except PaymentConfigurationError as exc:
            app.logger.error("DPO configuration: %s", exc)
            flash("Secure card checkout is temporarily unavailable. Please contact support with your order reference.", "danger")
            return redirect(url_for("order_detail", reference=order.reference))
        except Exception as exc:
            app.logger.exception("DPO createToken failed: %s", exc)
            flash("We could not reach the payment provider. Please try again or contact support.", "danger")
            return redirect(url_for("order_detail", reference=order.reference))

        transaction = PaymentTransaction(
            order_id=order.id,
            provider_reference=checkout_session.provider_reference,
            amount=order.total,
            currency=order.currency,
        )
        order.payment_reference = checkout_session.provider_reference
        db.session.add(transaction)
        audit("payment_started", "order", order.id, checkout_session.provider_reference)
        db.session.commit()
        return redirect(checkout_session.redirect_url)

    @app.route("/payments/mock/<int:order_id>", methods=["GET", "POST"])
    def payment_mock(order_id):
        if app.config.get("BANK_MID_MODE", "live") != "sandbox":
            abort(404)
        order = Order.query.get_or_404(order_id)
        if request.method == "POST":
            outcome = request.form.get("outcome")
            transaction = PaymentTransaction.query.filter_by(order_id=order.id).order_by(PaymentTransaction.id.desc()).first()
            if transaction is None:
                abort(404)
            if outcome == "approve":
                order.payment_status, order.status = "paid", "processing"
                transaction.status = "approved"
                for item in order.items:
                    db.session.add(DigitalEntitlement(order_item_id=item.id, delivery_status="pending"))
                flash("Sandbox payment approved. The order is ready for fulfilment.", "success")
            else:
                order.payment_status, order.status = "failed", "payment_failed"
                transaction.status = "declined"
                flash("Sandbox payment declined.", "danger")
            audit("sandbox_payment_result", "order", order.id, outcome)
            db.session.commit()
            return redirect(url_for("order_detail", reference=order.reference))
        return render_template("payment_mock.html", order=order)

    @app.get("/payments/return/<int:order_id>")
    def payment_return(order_id):
        order = Order.query.get_or_404(order_id)

        trans_token = (
            request.args.get("TransactionToken")
            or request.args.get("TransToken")
            or order.payment_reference
        )
        if not trans_token:
            flash("Missing payment reference. Please check your order status.", "warning")
            return redirect(url_for("order_detail", reference=order.reference))

        try:
            result = DPOGateway().verify_token(trans_token)
        except Exception as exc:
            app.logger.exception("DPO verifyToken failed: %s", exc)
            flash("We could not verify the payment yet. Please check your order shortly.", "warning")
            return redirect(url_for("order_detail", reference=order.reference))

        transaction = PaymentTransaction.query.filter_by(provider_reference=trans_token).first()
        if transaction is None:
            flash("Payment record not found for this order.", "danger")
            return redirect(url_for("order_detail", reference=order.reference))

        approved = result.get("result") == "000" and bool(result.get("transaction_approval"))

        if approved:
            order.payment_status, order.status = "paid", "processing"
            transaction.status = "approved"
            transaction.raw_status = result.get("result", "")
            transaction.response_code = (result.get("transaction_approval") or "")[:40]
            transaction.masked_pan = (result.get("customer_credit") or "")[:30]
            transaction.card_brand = (result.get("customer_credit_type") or "")[:30]

            existing_item_ids = {
                row.order_item_id
                for row in DigitalEntitlement.query.join(OrderItem)
                .filter(OrderItem.order_id == order.id)
                .all()
            }
            for item in order.items:
                if item.id not in existing_item_ids:
                    db.session.add(
                        DigitalEntitlement(order_item_id=item.id, delivery_status="pending")
                    )

            audit("payment_verified", "order", order.id, trans_token)
            flash("Payment approved. Your order is now being processed.", "success")
        else:
            order.payment_status, order.status = "failed", "payment_failed"
            transaction.status = "declined"
            transaction.raw_status = result.get("result", "")
            audit("payment_failed", "order", order.id, result.get("explanation", ""))
            flash("Payment was not approved. Please try again or contact support.", "danger")

        db.session.commit()
        return redirect(url_for("order_detail", reference=order.reference))

    @app.post("/webhooks/dpo")
    @csrf.exempt
    def dpo_webhook():
        raw = request.get_data()
        payload = request.form.to_dict() or (request.get_json(silent=True) or {})
        trans_token = payload.get("TransactionToken") or payload.get("TransToken")
        approval = payload.get("CCDapproval") or payload.get("TransactionApproval")

        if not trans_token:
            return jsonify({"status": "ignored", "reason": "no token"}), 400

        existing_event = WebhookEvent.query.filter_by(event_id=trans_token).first()
        if existing_event:
            return jsonify({"status": "duplicate"})

        event = WebhookEvent(
            provider="dpo",
            event_id=trans_token,
            event_type="payment_notification",
            signature_valid=True,
            payload_hash=hashlib.sha256(raw).hexdigest(),
        )
        db.session.add(event)

        transaction = PaymentTransaction.query.filter_by(provider_reference=trans_token).first()
        if transaction:
            if approval:
                transaction.status = "approved"
                transaction.order.payment_status, transaction.order.status = "paid", "processing"
                existing_item_ids = {
                    row.order_item_id
                    for row in DigitalEntitlement.query.join(OrderItem)
                    .filter(OrderItem.order_id == transaction.order_id)
                    .all()
                }
                for item in transaction.order.items:
                    if item.id not in existing_item_ids:
                        db.session.add(
                            DigitalEntitlement(order_item_id=item.id, delivery_status="pending")
                        )
            event.processed = True

        db.session.commit()
        return jsonify({"status": "ok"})

    # ================================================================
    # ORDERS
    # ================================================================
    @app.get("/orders/<reference>")
    def order_detail(reference):
        order = Order.query.filter_by(reference=reference).first_or_404()
        if order.user_id:
            if not current_user.is_authenticated:
                abort(403)
            if order.user_id != current_user.id and not current_user.is_admin:
                abort(403)
        elif session.get("last_order_reference") != order.reference:
            abort(403)
        return render_template("order_detail.html", order=order)

    # ================================================================
    # LEGACY REDIRECTS
    # ================================================================
    @app.get("/commodities")
    def commodities():
        return redirect(url_for("games"), code=301)

    @app.get("/commodities/<slug>")
    def commodity_detail(slug):
        return redirect(url_for("games"), code=301)

    @app.route("/request-quote", methods=["GET", "POST"])
    def request_quote():
        return redirect(url_for("inquiry"), code=303 if request.method == "POST" else 302)

    # ================================================================
    # CONTACT / AUTH
    # ================================================================
    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            message = ContactMessage(
                reference=make_reference("CS"),
                full_name=form.full_name.data,
                email=form.email.data.lower(),
                company=form.company.data,
                subject=form.subject.data,
                message=form.message.data,
            )
            db.session.add(message)
            db.session.commit()
            flash(f"Message received. Your reference is {message.reference}.", "success")
            return redirect(url_for("contact"))
        return render_template("contact.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("account"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter(db.func.lower(User.email) == form.email.data.lower()).first()
            if user and user.is_active_account and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                audit("login", "user", user.id)
                db.session.commit()
                return redirect(url_for("admin_dashboard" if user.is_admin else "account"))
            flash("Invalid email or password.", "danger")
        return render_template("login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("account"))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter(db.func.lower(User.email) == form.email.data.lower()).first():
                flash("An account already exists for that email.", "danger")
            else:
                user = User(
                    full_name=form.full_name.data,
                    email=form.email.data.lower(),
                    company=form.company.data,
                    phone=form.phone.data,
                    country=form.country.data,
                )
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for("account"))
        return render_template("register.html", form=form)

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have signed out.", "info")
        return redirect(url_for("index"))

    # ================================================================
    # ACCOUNT + ADDRESS BOOK
    # ================================================================
    @app.get("/account")
    @login_required
    def account():
        addresses = (
            Address.query
            .filter_by(user_id=current_user.id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
            .all()
        )
        return render_template(
            "account.html",
            addresses=addresses,
            orders=Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all(),
            quotes=Quote.query.filter_by(user_id=current_user.id).order_by(Quote.created_at.desc()).all(),
            inquiries=GameInquiry.query.filter_by(user_id=current_user.id).order_by(GameInquiry.created_at.desc()).all(),
        )

    @app.post("/account/addresses/new")
    @login_required
    def address_create():
        label          = (request.form.get("label") or "Home").strip()[:80] or "Home"
        full_name      = (request.form.get("full_name") or "").strip()
        company        = (request.form.get("company") or "").strip() or None
        phone          = (request.form.get("phone") or "").strip() or None
        country        = (request.form.get("country") or "").strip().upper()
        city           = (request.form.get("city") or "").strip()
        postal_code    = (request.form.get("postal_code") or "").strip()
        address_line1  = (request.form.get("address_line1") or "").strip()
        address_line2  = (request.form.get("address_line2") or "").strip() or None
        is_default     = request.form.get("is_default") == "on"

        if not (full_name and country and city and postal_code and address_line1):
            flash("Please fill in the required address fields.", "danger")
            return redirect(url_for("account") + "#addresses")

        existing_count = Address.query.filter_by(user_id=current_user.id).count()
        if existing_count == 0:
            is_default = True

        if is_default:
            Address.query.filter_by(user_id=current_user.id).update({"is_default": False})

        db.session.add(Address(
            user_id=current_user.id,
            label=label, full_name=full_name, company=company, phone=phone,
            country=country, city=city, postal_code=postal_code,
            address_line1=address_line1, address_line2=address_line2,
            is_default=is_default,
        ))
        audit("address_created", "address", detail=label)
        db.session.commit()
        flash("Address saved.", "success")
        return redirect(url_for("account") + "#addresses")

    @app.post("/account/addresses/<int:address_id>/edit")
    @login_required
    def address_update(address_id):
        address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()

        address.label         = (request.form.get("label") or address.label).strip()[:80] or "Home"
        address.full_name     = (request.form.get("full_name") or address.full_name).strip()
        address.company       = (request.form.get("company") or "").strip() or None
        address.phone         = (request.form.get("phone") or "").strip() or None
        address.country       = (request.form.get("country") or address.country).strip().upper()
        address.city          = (request.form.get("city") or address.city).strip()
        address.postal_code   = (request.form.get("postal_code") or address.postal_code).strip()
        address.address_line1 = (request.form.get("address_line1") or address.address_line1).strip()
        address.address_line2 = (request.form.get("address_line2") or "").strip() or None

        if request.form.get("is_default") == "on":
            Address.query.filter_by(user_id=current_user.id).update({"is_default": False})
            address.is_default = True

        audit("address_updated", "address", address_id, address.label)
        db.session.commit()
        flash("Address updated.", "success")
        return redirect(url_for("account") + "#addresses")

    @app.post("/account/addresses/<int:address_id>/delete")
    @login_required
    def address_delete(address_id):
        address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
        was_default = address.is_default
        label = address.label
        db.session.delete(address)

        if was_default:
            remaining = Address.query.filter_by(user_id=current_user.id).order_by(Address.created_at.desc()).first()
            if remaining:
                remaining.is_default = True

        audit("address_deleted", "address", address_id, label)
        db.session.commit()
        flash("Address removed.", "info")
        return redirect(url_for("account") + "#addresses")

    @app.post("/account/addresses/<int:address_id>/default")
    @login_required
    def address_set_default(address_id):
        address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
        Address.query.filter_by(user_id=current_user.id).update({"is_default": False})
        address.is_default = True
        audit("address_default_changed", "address", address_id, address.label)
        db.session.commit()
        flash("Default address updated.", "success")
        return redirect(url_for("account") + "#addresses")

    @app.get("/api/account/addresses")
    @login_required
    def api_list_addresses():
        addresses = (
            Address.query
            .filter_by(user_id=current_user.id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
            .all()
        )
        return jsonify([a.to_dict() for a in addresses])

    # ================================================================
    # STATIC CONTENT PAGES
    # ================================================================
    @app.get("/about")
    def about():
        return render_template("content.html", eyebrow="Company", title="A focused global gaming-commerce company.", lead="FABS Trading connects customers, retailers and entertainment operators with gaming products through a structured digital marketplace.", sections=[("Gaming product marketplace","Explore tabletop, arcade, redemption, racing, sports and immersive gaming products across practical price and MOQ ranges."),("Commercial procurement","Submit a documented enquiry for product configuration, quantity, delivery, installation and after-sales requirements."),("One governance standard","Finance, risk, technology, payment security and customer protection are managed as shared controls across the business.")])

    @app.get("/how-it-works")
    def how_it_works():
        return render_template("content.html", eyebrow="Customer journey", title="A structured gaming procurement workflow.", lead="Browse verified gaming products, request commercial terms and complete secure payment through the approved checkout flow.", sections=[("Discover","Compare active gaming products, platforms, specifications, prices and minimum order quantities."),("Request a quotation","Select a game, confirm the required quantity and provide your delivery and configuration requirements."),("Review and fulfilment","Approve the final quotation, complete secure payment and track fulfilment with the FABS Trading team.")])

    @app.get("/compliance")
    def compliance():
        return render_template("content.html", eyebrow="Governance", title="Controls proportionate to every gaming transaction.", lead="Risk-based customer controls, KYB, sanctions review, payment security and documented commercial approvals.", sections=[("Cardholder data boundary","FABS uses hosted or tokenised checkout and does not store raw card numbers or CVV data."),("Gaming commerce controls","Product, customer, authority, destination, payment and fulfilment information may be reviewed before approval.")])

    @app.get("/<page_name>")
    def media_page(page_name):
        if page_name not in MEDIA_PAGES:
            abort(404)
        return render_template("media_content.html", page=MEDIA_PAGES[page_name])

    @app.get("/news")
    def news():
        return render_template("news.html", articles=NEWS_ARTICLES)

    @app.get("/news/<slug>")
    def news_article(slug):
        article = NEWS_ARTICLES.get(slug)
        if not article:
            abort(404)
        return render_template("news_article.html", slug=slug, article=article)

    @app.get("/support")
    def support():
        return render_template("support.html")

    @app.get("/terms")
    def terms():
        return render_template("policy.html", title="Terms of use", policy="terms")

    @app.get("/privacy")
    def privacy():
        return render_template("policy.html", title="Privacy notice", policy="privacy")

    @app.get("/refunds")
    def refunds():
        return render_template("policy.html", title="Refund and cancellation policy", policy="refunds")

    # ================================================================
    # ADMIN
    # ================================================================
    @app.get("/admin")
    @admin_required
    def admin_dashboard():
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        pending_shipment = Order.query.filter(
            Order.payment_status == "paid",
            Order.shipping_status.in_([None, "pending"]),
        ).count()

        shipped_week = Order.query.filter(
            Order.shipped_at.isnot(None),
            Order.shipped_at >= week_ago,
        ).count()

        recent_shipments = (
            Order.query
            .filter(Order.dhl_tracking_number.isnot(None))
            .order_by(Order.created_at.desc())
            .limit(6)
            .all()
        )

        recent_inquiries = (
            GameInquiry.query
            .order_by(GameInquiry.created_at.desc())
            .limit(6)
            .all()
        )

        stats = {
            "orders":           Order.query.count(),
            "paid":             Order.query.filter_by(payment_status="paid").count(),
            "pending_shipment": pending_shipment,
            "shipped_week":     shipped_week,
            "inquiries":        GameInquiry.query.count(),
            "quotes":           Quote.query.count() if Quote else 0,
            "users":            User.query.filter_by(role="customer").count(),
        }

        return render_template(
            "admin/dashboard.html",
            stats=stats,
            orders=Order.query.order_by(Order.created_at.desc()).limit(8).all(),
            quotes=Quote.query.order_by(Quote.created_at.desc()).limit(6).all() if Quote else [],
            shipments=recent_shipments,
            inquiries=recent_inquiries,
        )

    @app.get("/admin/orders")
    @admin_required
    def admin_orders():
        return render_template("admin/orders.html", orders=Order.query.order_by(Order.created_at.desc()).all())

    @app.get("/admin/quotes")
    @admin_required
    def admin_quotes():
        return redirect(url_for("admin_inquiries"), code=302)

    @app.get("/admin/inquiries")
    @admin_required
    def admin_inquiries():
        return render_template("admin/inquiries.html", inquiries=GameInquiry.query.order_by(GameInquiry.created_at.desc()).all())

    @app.post("/admin/inquiries/<int:inquiry_id>/status")
    @admin_required
    def admin_inquiry_status(inquiry_id):
        inquiry = GameInquiry.query.get_or_404(inquiry_id)
        allowed = {"submitted", "reviewing", "quoted", "negotiating", "won", "closed"}
        status = request.form.get("status")
        if status not in allowed:
            abort(400)
        inquiry.status = status
        audit("game_inquiry_status_changed", "game_inquiry", inquiry.id, status)
        db.session.commit()
        flash("Inquiry status updated.", "success")
        return redirect(url_for("admin_inquiries"))

    @app.post("/admin/quotes/<int:quote_id>/status")
    @admin_required
    def admin_quote_status(quote_id):
        return redirect(url_for("admin_inquiries"), code=303)

    @app.route("/admin/games/new", methods=["GET", "POST"])
    @admin_required
    def admin_game_new():
        form = GameForm()
        if form.validate_on_submit():
            game = Game()
            form.populate_obj(game)
            db.session.add(game)
            audit("game_created", "game", detail=game.slug)
            db.session.commit()
            flash("Game created.", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("admin/game_form.html", form=form, title="Add game")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "fabs-trading"})


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        seed_catalogue()

        email = app.config["ADMIN_EMAIL"].lower()
        password = app.config["ADMIN_PASSWORD"]
        admin = User.query.filter(db.func.lower(User.email) == email).first()

        if admin is None and password:
            admin = User(
                full_name="FABS Administrator",
                email=email,
                role="admin",
            )
            admin.set_password(password)
            db.session.add(admin)
        elif admin is not None and admin.role != "admin":
            admin.role = "admin"

        db.session.commit()
        print("Database initialised and catalogue seeded.")


def register_errors(app):
    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, title="Page not found", message="The page you requested is not available."), 404

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("error.html", code=403, title="Access restricted", message="You do not have permission to view this area."), 403

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        return render_template("error.html", code=500, title="We could not complete that request", message="Please try again or contact support."), 500


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")