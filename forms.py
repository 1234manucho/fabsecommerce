from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, EmailField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, URL


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
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=140)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    country = StringField("Country", validators=[DataRequired(), Length(max=90)])
    accept_terms = BooleanField("I accept the terms and digital fulfilment conditions", validators=[DataRequired()])
    submit = SubmitField("Continue to secure payment")


class QuoteForm(FlaskForm):
    company_name = StringField("Company legal name", validators=[DataRequired(), Length(max=180)])
    company_website = StringField("Company website", validators=[Optional(), URL(), Length(max=255)])
    contact_name = StringField("Contact person", validators=[DataRequired(), Length(max=140)])
    email = EmailField("Business email", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("Phone / WhatsApp", validators=[DataRequired(), Length(max=40)])
    incorporation_country = StringField("Country of incorporation", validators=[DataRequired(), Length(max=90)])
    commodity_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    grade = StringField("Required grade", validators=[DataRequired(), Length(max=180)])
    quantity = StringField("Quantity", validators=[DataRequired(), Length(max=80)])
    delivery_country = StringField("Delivery country", validators=[DataRequired(), Length(max=90)])
    destination = StringField("Destination port / city", validators=[DataRequired(), Length(max=140)])
    incoterm = SelectField("Preferred incoterm", choices=[("EXW","EXW"),("FOB","FOB"),("CFR","CFR"),("CIF","CIF")], validators=[DataRequired()])
    requirements = TextAreaField("Additional specifications", validators=[Optional(), Length(max=4000)])
    confirm = BooleanField("I confirm the information is accurate", validators=[DataRequired()])
    submit = SubmitField("Submit request for quotation")


class ContactForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(max=140)])
    email = EmailField("Email address", validators=[DataRequired(), Email(), Length(max=255)])
    company = StringField("Company", validators=[Optional(), Length(max=180)])
    subject = SelectField("Subject", choices=[("game_support","Game order support"),("commodity","Commodity enquiry"),("integration","Merchant and bank integration"),("compliance","Compliance"),("general","General enquiry")], validators=[DataRequired()])
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
    requirements = TextAreaField("Product specifications", validators=[Optional(), Length(max=4000)])
    confirm = BooleanField("I confirm that this is a genuine commercial inquiry", validators=[DataRequired()])
    submit = SubmitField("Send inquiry")


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
    is_featured = BooleanField("Featured")
    is_active = BooleanField("Active")
    submit = SubmitField("Save game")
