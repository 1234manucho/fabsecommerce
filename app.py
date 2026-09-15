import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from forms import CheckoutForm, ContactForm, GameForm, GameInquiryForm, LoginForm, RegisterForm
from models import AuditLog, ContactMessage, DigitalEntitlement, Game, GameInquiry, Order, OrderItem, PaymentTransaction, User, WebhookEvent, db
from seed import seed_catalogue
from services.payment import BankMIDGateway, PaymentConfigurationError

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
DEFAULT_USD_KES_RATE = Decimal("130.00")
CATALOGUE_PAGE_SIZE = 8


def _positive_decimal(value, default=DEFAULT_USD_KES_RATE):
    """Return a positive finite Decimal or a safe fallback value."""

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
        converted = (amount * app.config["USD_KES_RATE"]).quantize(
            Decimal("1")
        )
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
        if not current_user.is_admin: abort(403)
        return view(*args, **kwargs)
    return wrapped


def audit(action, entity_type, entity_id=None, detail=None):
    db.session.add(AuditLog(actor_user_id=current_user.id if current_user.is_authenticated else None, action=action, entity_type=entity_type, entity_id=str(entity_id) if entity_id else None, ip_address=request.headers.get("CF-Connecting-IP", request.remote_addr), detail=detail))


def register_routes(app):
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
        total_pages = max(
            1,
            (catalogue_total + CATALOGUE_PAGE_SIZE - 1)
            // CATALOGUE_PAGE_SIZE,
        )
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
            inquiry_record = GameInquiry(reference=make_reference("INQ"), game_id=game.id, user_id=current_user.id if current_user.is_authenticated else None, full_name=form.full_name.data, company=form.company.data, email=form.email.data.lower(), phone=form.phone.data, country=form.country.data, quantity=form.quantity.data, destination=form.destination.data, requirements=form.requirements.data)
            db.session.add(inquiry_record)
            audit("game_inquiry_submitted", "game_inquiry", detail=inquiry_record.reference)
            db.session.commit()
            return render_template("inquiry_success.html", inquiry=inquiry_record, game=game)
        return render_template("game_inquiry.html", form=form, game=None)

    @app.post("/cart/add/<int:game_id>")
    def add_to_cart(game_id):
        Game.query.filter_by(id=game_id, is_active=True).first_or_404()
        cart = session.get("cart", [])
        if game_id not in cart:
            cart.append(game_id)
        session["cart"] = cart
        session.modified = True

        # AJAX callers (from the games page basket) get JSON; form submissions get a redirect.
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
        total = sum((item.price for item in items), Decimal("0.00"))
        form = CheckoutForm()
        if current_user.is_authenticated and request.method == "GET":
            form.full_name.data = current_user.full_name
            form.email.data = current_user.email
            form.country.data = current_user.country
        if form.validate_on_submit():
            order = Order(
                reference=make_reference("GM"),
                user_id=current_user.id if current_user.is_authenticated else None,
                email=form.email.data.lower(),
                full_name=form.full_name.data,
                country=form.country.data,
                currency=app.config.get("BASE_CURRENCY", "USD"),
                subtotal=total,
                total=total,
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
        return render_template("checkout.html", form=form, items=items, total=total)

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
            checkout_session = BankMIDGateway().create_checkout(order)
        except PaymentConfigurationError as exc:
            app.logger.error("Payment configuration: %s", exc)
            flash("Secure card checkout is not configured. Please contact support with your order reference.", "danger")
            return redirect(url_for("order_detail", reference=order.reference))
        transaction = PaymentTransaction(order_id=order.id, provider_reference=checkout_session.provider_reference, amount=order.total, currency=order.currency)
        order.payment_reference = checkout_session.provider_reference
        db.session.add(transaction)
        audit("payment_started", "order", order.id, checkout_session.provider_reference)
        db.session.commit()
        return redirect(checkout_session.redirect_url)

    @app.route("/payments/mock/<int:order_id>", methods=["GET", "POST"])
    def payment_mock(order_id):
        if app.config["BANK_MID_MODE"] != "sandbox": abort(404)
        order = Order.query.get_or_404(order_id)
        if request.method == "POST":
            outcome = request.form.get("outcome")
            transaction = PaymentTransaction.query.filter_by(order_id=order.id).order_by(PaymentTransaction.id.desc()).first()
            if transaction is None:
                abort(404)
            if outcome == "approve":
                order.payment_status, order.status = "paid", "processing"
                transaction.status = "approved"
                for item in order.items: db.session.add(DigitalEntitlement(order_item_id=item.id, delivery_status="pending"))
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
        return redirect(url_for("order_detail", reference=Order.query.get_or_404(order_id).reference))

    @app.post("/webhooks/bank-mid")
    @csrf.exempt
    def bank_webhook():
        raw = request.get_data()
        signature = request.headers.get("X-Signature", "")
        gateway = BankMIDGateway()
        if not gateway.verify_webhook(raw, signature): abort(401)
        data = request.get_json(silent=True) or {}
        event_id = str(data.get("event_id", ""))
        if not event_id: abort(400)
        if WebhookEvent.query.filter_by(event_id=event_id).first(): return jsonify({"received": True, "duplicate": True})
        event = WebhookEvent(provider="bank_mid", event_id=event_id, event_type=str(data.get("event_type", "unknown")), signature_valid=True, payload_hash=hashlib.sha256(raw).hexdigest())
        db.session.add(event)
        transaction = PaymentTransaction.query.filter_by(provider_reference=data.get("transaction_reference")).first()
        if transaction:
            status = str(data.get("status", "")).lower()
            transaction.status = "approved" if status in {"approved","paid","success"} else "declined" if status in {"declined","failed"} else "pending"
            transaction.raw_status = status
            transaction.response_code = str(data.get("response_code", ""))[:40]
            transaction.masked_pan = str(data.get("masked_pan", ""))[:30]
            transaction.card_brand = str(data.get("card_brand", ""))[:30]
            if transaction.status == "approved":
                transaction.order.payment_status, transaction.order.status = "paid", "processing"
                existing_item_ids = {row.order_item_id for row in DigitalEntitlement.query.join(OrderItem).filter(OrderItem.order_id == transaction.order_id).all()}
                for item in transaction.order.items:
                    if item.id not in existing_item_ids:
                        db.session.add(DigitalEntitlement(order_item_id=item.id, delivery_status="pending"))
            elif transaction.status == "declined":
                transaction.order.payment_status, transaction.order.status = "failed", "payment_failed"
            event.processed = True
        db.session.commit()
        return jsonify({"received": True})

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

    @app.get("/commodities")
    def commodities():
        return redirect(url_for("games"), code=301)

    @app.get("/commodities/<slug>")
    def commodity_detail(slug):
        return redirect(url_for("games"), code=301)

    @app.route("/request-quote", methods=["GET", "POST"])
    def request_quote():
        # Preserve old bookmarks while ensuring every quotation starts from the
        # gaming-only inquiry workflow.
        return redirect(url_for("inquiry"), code=303 if request.method == "POST" else 302)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        form = ContactForm()
        if form.validate_on_submit():
            message = ContactMessage(reference=make_reference("CS"), full_name=form.full_name.data, email=form.email.data.lower(), company=form.company.data, subject=form.subject.data, message=form.message.data)
            db.session.add(message); db.session.commit()
            flash(f"Message received. Your reference is {message.reference}.", "success")
            return redirect(url_for("contact"))
        return render_template("contact.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated: return redirect(url_for("account"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter(db.func.lower(User.email) == form.email.data.lower()).first()
            if user and user.is_active_account and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data); audit("login", "user", user.id); db.session.commit()
                return redirect(url_for("admin_dashboard" if user.is_admin else "account"))
            flash("Invalid email or password.", "danger")
        return render_template("login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated: return redirect(url_for("account"))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter(db.func.lower(User.email) == form.email.data.lower()).first():
                flash("An account already exists for that email.", "danger")
            else:
                user = User(full_name=form.full_name.data, email=form.email.data.lower(), company=form.company.data, phone=form.phone.data, country=form.country.data)
                user.set_password(form.password.data); db.session.add(user); db.session.commit(); login_user(user)
                return redirect(url_for("account"))
        return render_template("register.html", form=form)

    @app.post("/logout")
    @login_required
    def logout():
        logout_user(); flash("You have signed out.", "info"); return redirect(url_for("index"))

    @app.get("/account")
    @login_required
    def account():
        return render_template("account.html", orders=Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all(), quotes=[], inquiries=GameInquiry.query.filter_by(user_id=current_user.id).order_by(GameInquiry.created_at.desc()).all())

    @app.get("/about")
    def about(): return render_template("content.html", eyebrow="Company", title="A focused global gaming-commerce company.", lead="FABS Trading connects customers, retailers and entertainment operators with gaming products through a structured digital marketplace.", sections=[("Gaming product marketplace","Explore tabletop, arcade, redemption, racing, sports and immersive gaming products across practical price and MOQ ranges."),("Commercial procurement","Submit a documented enquiry for product configuration, quantity, delivery, installation and after-sales requirements."),("One governance standard","Finance, risk, technology, payment security and customer protection are managed as shared controls across the business.")])

    @app.get("/how-it-works")
    def how_it_works(): return render_template("content.html", eyebrow="Customer journey", title="A structured gaming procurement workflow.", lead="Browse verified gaming products, request commercial terms and complete secure payment through the approved checkout flow.", sections=[("Discover","Compare active gaming products, platforms, specifications, prices and minimum order quantities."),("Request a quotation","Select a game, confirm the required quantity and provide your delivery and configuration requirements."),("Review and fulfilment","Approve the final quotation, complete secure payment and track fulfilment with the FABS Trading team.")])

    @app.get("/compliance")
    def compliance(): return render_template("content.html", eyebrow="Governance", title="Controls proportionate to every gaming transaction.", lead="Risk-based customer controls, KYB, sanctions review, payment security and documented commercial approvals.", sections=[("Cardholder data boundary","FABS uses hosted or tokenised checkout and does not store raw card numbers or CVV data."),("Gaming commerce controls","Product, customer, authority, destination, payment and fulfilment information may be reviewed before approval.")])

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
        if not article: abort(404)
        return render_template("news_article.html", slug=slug, article=article)

    @app.get("/support")
    def support(): return render_template("support.html")

    @app.get("/terms")
    def terms(): return render_template("policy.html", title="Terms of use", policy="terms")

    @app.get("/privacy")
    def privacy(): return render_template("policy.html", title="Privacy notice", policy="privacy")

    @app.get("/refunds")
    def refunds(): return render_template("policy.html", title="Refund and cancellation policy", policy="refunds")

    @app.get("/admin")
    @admin_required
    def admin_dashboard():
        return render_template("admin/dashboard.html", stats={"orders":Order.query.count(),"paid":Order.query.filter_by(payment_status="paid").count(),"quotes":0,"inquiries":GameInquiry.query.count(),"users":User.query.filter_by(role="customer").count()}, orders=Order.query.order_by(Order.created_at.desc()).limit(8).all(), quotes=[])

    @app.get("/admin/orders")
    @admin_required
    def admin_orders(): return render_template("admin/orders.html", orders=Order.query.order_by(Order.created_at.desc()).all())

    @app.get("/admin/quotes")
    @admin_required
    def admin_quotes(): return redirect(url_for("admin_inquiries"), code=302)

    @app.get("/admin/inquiries")
    @admin_required
    def admin_inquiries(): return render_template("admin/inquiries.html", inquiries=GameInquiry.query.order_by(GameInquiry.created_at.desc()).all())

    @app.post("/admin/inquiries/<int:inquiry_id>/status")
    @admin_required
    def admin_inquiry_status(inquiry_id):
        inquiry = GameInquiry.query.get_or_404(inquiry_id)
        allowed = {"submitted", "reviewing", "quoted", "negotiating", "won", "closed"}
        status = request.form.get("status")
        if status not in allowed: abort(400)
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
        form=GameForm()
        if form.validate_on_submit():
            game=Game(); form.populate_obj(game); db.session.add(game); audit("game_created","game",detail=game.slug); db.session.commit(); flash("Game created.","success"); return redirect(url_for("admin_dashboard"))
        return render_template("admin/game_form.html",form=form,title="Add game")

    @app.get("/health")
    def health(): return jsonify({"status":"ok","service":"fabs-trading"})


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
    def not_found(_): return render_template("error.html",code=404,title="Page not found",message="The page you requested is not available."),404
    @app.errorhandler(403)
    def forbidden(_): return render_template("error.html",code=403,title="Access restricted",message="You do not have permission to view this area."),403
    @app.errorhandler(500)
    def server_error(_): db.session.rollback(); return render_template("error.html",code=500,title="We could not complete that request",message="Please try again or contact support."),500


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")