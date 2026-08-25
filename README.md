# FABS Trading Global E-Commerce — Flask Application

A production-structured Flask marketplace for commercial gaming equipment, arcade systems, immersive VR, racing simulators, tabletop manufacturing and institutional commodity sourcing.

## Included

- Responsive multi-page Flask/Jinja frontend using HTML, Tailwind CSS, inline CSS and inline JavaScript.
- Five-image moving hero with an animated global sourcing network and self-hosted rotating globe media.
- Self-hosted, authentic product and venue photographs for homepage and core gaming catalogue listings.
- Marketplace filters, MOQ, supplier profiles, indicative wholesale pricing and pagination through page 999.
- Product detail pages and structured gaming inquiry forms with traceable FABS references.
- Session cart, customer registration/login, account portal, checkout and sandbox bank-MID workflow.
- Commodity catalogue and detailed RFQ workflow.
- Administrator dashboard for orders, payments, gaming inquiries, commodity RFQs and catalogue creation.
- SQLAlchemy models for users, products, inquiries, orders, payments, entitlements, messages, webhooks and audit logs.
- SQLite for local development and PostgreSQL support for production.
- Dual-office floating WhatsApp contact for Kenya and Greece.
- Render Blueprint, Dockerfile, Procfile, health endpoint and automated tests.

## Project structure

```text
app.py                  Flask factory, routes, admin and API/webhook flows
models.py               SQLAlchemy database models
forms.py                Validated Flask-WTF forms
config.py               Environment-driven configuration
seed.py                 Gaming and commodity catalogue seed data
services/payment.py     Hosted bank-MID adapter and sandbox flow
templates/              Responsive Jinja pages
static/                 CSS, JavaScript, logo, partner marks and product media
tests/                   Functional application tests
.env                    Local development configuration
.env.example            Production environment template
requirements.txt        Python dependencies
render.yaml             Render deployment blueprint
Dockerfile              Container deployment
Procfile                Gunicorn process definition
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run --debug
```

Open `http://127.0.0.1:5000`.

The included development `.env` uses:

- Admin email: `admin@fabstrading.com`
- Admin password: `ChangeThisBeforeProduction!`

Change the secret key and administrator password before any public deployment.

## Test

```bash
pip install pytest
PYTHONPATH=. pytest -q
```

The tests verify the homepage, catalogue, page 999, public content routes, WhatsApp contacts, commodity RFQ and gaming inquiry storage.

## Production deployment

### Render

1. Upload the folder to a private Git repository.
2. In Render, create a Blueprint from `render.yaml`.
3. Replace the generated/default admin password and add the approved payment-provider values.
4. Confirm the PostgreSQL database is attached through `DATABASE_URL`.
5. Register `/webhooks/bank-mid` with the acquiring bank or gateway.

### Docker

```bash
docker build -t fabs-trading .
docker run --env-file .env -p 10000:10000 fabs-trading
```

## Payment boundary

The application does not collect or store raw card numbers or CVV values. `services/payment.py` creates a hosted-checkout session and reconciles the signed result through an idempotent webhook. The default `BANK_MID_MODE=sandbox` provides a safe approval/decline simulator until official acquiring-bank credentials and field mappings are supplied.

## Before production

- Replace all example secrets and credentials.
- Use PostgreSQL and managed backups.
- Connect a transactional email provider.
- Complete acquiring-bank integration and PCI scope confirmation.
- Confirm product-media rights, supplier contracts and final commercial terms.
- Add database migrations for future schema changes.
- Run security, load, payment-reconciliation and fulfilment tests.
