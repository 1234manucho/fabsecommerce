from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    EmailField,
    HiddenField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    URL,
)


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegisterForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=140)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    company = StringField("Company", validators=[Optional(), Length(max=180)])
    phone = StringField("Phone", validators=[Optional(), Length(max=40)])
    country = StringField("Country", validators=[Optional(), Length(max=90)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=10, max=128)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


class CheckoutForm(FlaskForm):
    # ---- Customer details ----
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=140)])
    email     = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    country   = StringField(
        "Country code (ISO-2)",
        validators=[DataRequired(), Length(min=2, max=2)],
    )

    # ---- Delivery address ----
    company       = StringField("Company (optional)", validators=[Optional(), Length(max=180)])
    phone         = StringField("Phone / WhatsApp", validators=[Optional(), Length(max=40)])
    address_line1 = StringField("Address line 1", validators=[DataRequired(), Length(max=200)])
    address_line2 = StringField("Address line 2 (optional)", validators=[Optional(), Length(max=200)])
    city          = StringField("City", validators=[DataRequired(), Length(max=100)])
    postal_code   = StringField("Postal code", validators=[DataRequired(), Length(max=20)])

    # ---- Pay for someone else / gift (NEW) ----
    pay_for_other = BooleanField("I'm paying for someone else / This is a gift")
    recipient_relationship = SelectField(
        "Relationship to you",
        choices=[
            ("", "— Select —"),
            ("family",           "Family member"),
            ("friend",           "Friend"),
            ("partner",          "Partner / Spouse"),
            ("colleague",        "Colleague"),
            ("client",           "Client"),
            ("business_partner", "Business partner"),
            ("employee",         "Employee"),
            ("gift",             "Gift recipient"),
            ("other",            "Other"),
        ],
        validators=[Optional()],
    )
    recipient_full_name = StringField(
        "Recipient full name",
        validators=[Optional(), Length(max=140)],
    )
    recipient_phone = StringField(
        "Recipient phone",
        validators=[Optional(), Length(max=40)],
    )
    recipient_email = EmailField(
        "Recipient email",
        validators=[Optional(), Email(), Length(max=255)],
    )
    recipient_company = StringField(
        "Recipient company",
        validators=[Optional(), Length(max=180)],
    )
    gift_message = TextAreaField(
        "Gift message or special instructions",
        validators=[Optional(), Length(max=280)],
    )
    hide_prices_on_slip = BooleanField("Hide prices on the packing slip")

    # ---- Shipping (DHL) ----
    shipping_quote = HiddenField()   # JSON string posted from the frontend

    # ---- Terms + submit ----
    accept_terms = BooleanField(
        "I accept the terms and fulfilment conditions",
        validators=[DataRequired()],
    )
    submit = SubmitField("Continue to secure payment")


class ContactForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=140)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    company = StringField("Company", validators=[Optional(), Length(max=180)])
    subject = SelectField(
        "Subject",
        choices=[
            ("game_support", "Gaming product and order support"),
            ("bulk_order", "Bulk gaming quotation"),
            ("integration", "Merchant and payment integration"),
            ("compliance", "Compliance"),
            ("general", "General enquiry"),
        ],
        validators=[DataRequired()],
    )
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=4000)])
    submit = SubmitField("Send message")


class GameInquiryForm(FlaskForm):
    product_id = SelectField("Gaming product", coerce=int, validators=[DataRequired()])
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=140)])
    company = StringField("Company name", validators=[DataRequired(), Length(max=180)])
    email = EmailField("Business email", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("Phone / WhatsApp", validators=[DataRequired(), Length(max=40)])
    country = StringField("Country", validators=[DataRequired(), Length(max=90)])
    quantity = StringField("Required quantity", validators=[DataRequired(), Length(max=80)])
    destination = StringField("Delivery destination", validators=[DataRequired(), Length(max=160)])
    requirements = TextAreaField(
        "Game model, configuration and specifications",
        validators=[Optional(), Length(max=4000)],
    )
    confirm = BooleanField(
        "I confirm that this is a genuine commercial gaming inquiry",
        validators=[DataRequired()],
    )
    submit = SubmitField("Request gaming quotation")


class GameForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=180)])
    slug = StringField("Slug", validators=[DataRequired(), Length(max=160)])
    genre = StringField("Genre", validators=[DataRequired(), Length(max=100)])
    platform = StringField("Platform", validators=[DataRequired(), Length(max=100)])
    edition = StringField("Edition", validators=[DataRequired(), Length(max=100)])
    region = StringField("Region", validators=[DataRequired(), Length(max=100)])
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)
    compare_price = DecimalField("Compare price", validators=[Optional(), NumberRange(min=0)], places=2)
    stock_count = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("Image URL", validators=[DataRequired(), URL(), Length(max=2000)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=20)])

    # ---- Shipping dimensions (used for DHL rate quotes) ----
    weight_kg = DecimalField(
        "Weight (kg)",
        validators=[Optional(), NumberRange(min=0)],
        places=2,
    )
    length_cm = DecimalField(
        "Length (cm)",
        validators=[Optional(), NumberRange(min=0)],
        places=1,
    )
    width_cm = DecimalField(
        "Width (cm)",
        validators=[Optional(), NumberRange(min=0)],
        places=1,
    )
    height_cm = DecimalField(
        "Height (cm)",
        validators=[Optional(), NumberRange(min=0)],
        places=1,
    )
    hs_code = StringField("HS code (customs)", validators=[Optional(), Length(max=20)])

    is_featured = BooleanField("Featured")
    is_active = BooleanField("Active")
    submit = SubmitField("Save game")