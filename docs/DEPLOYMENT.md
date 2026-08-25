# Deployment and Operations

## Recommended production topology

- HTTPS reverse proxy / managed web service
- Gunicorn Flask application
- Managed PostgreSQL
- Object storage for approved trade documents
- Transactional email service
- Secrets in the host's secret manager
- Central logs, error reporting and uptime monitoring

## First deployment

1. Create PostgreSQL and set `DATABASE_URL`.
2. Set all non-empty secrets from `.env.example` in the host dashboard.
3. Deploy and run `flask --app app init-db` once.
4. Confirm `/health`, catalogue pages and administrator authentication.
5. Keep `BANK_MID_MODE=sandbox` through bank user-acceptance testing.
6. Change to the bank-approved production values only after sign-off.

## Release discipline

- Back up the database before schema migrations.
- Separate development, staging and production credentials.
- Review logs for secrets and personal data.
- Restrict administrator access and rotate credentials.
- Reconcile successful provider transactions against paid FABS orders daily.
