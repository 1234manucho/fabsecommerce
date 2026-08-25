import hashlib
import hmac
import json
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from flask import current_app, url_for


class PaymentConfigurationError(RuntimeError):
    pass


@dataclass
class CheckoutSession:
    provider_reference: str
    redirect_url: str


class BankMIDGateway:
    """Hosted-checkout adapter.

    This application never accepts PAN/CVV data. The adapter creates a signed
    server-to-server session and redirects the browser to the acquiring bank.
    Adapt `create_checkout` field names to the selected bank's API contract.
    """

    def __init__(self):
        config = current_app.config
        self.mode = config["BANK_MID_MODE"]
        self.checkout_url = config["BANK_MID_CHECKOUT_URL"].rstrip("/")
        self.merchant_id = config["BANK_MID_MERCHANT_ID"]
        self.api_key = config["BANK_MID_API_KEY"]
        self.signing_secret = config["BANK_MID_SIGNING_SECRET"]
        self.webhook_secret = config["BANK_MID_WEBHOOK_SECRET"]

    def create_checkout(self, order):
        if self.mode == "sandbox" and not self.checkout_url:
            return CheckoutSession(
                provider_reference=f"sandbox-{order.reference}",
                redirect_url=url_for("payment_mock", order_id=order.id, _external=True),
            )
        if not all([self.checkout_url, self.merchant_id, self.api_key, self.signing_secret]):
            raise PaymentConfigurationError("The bank MID hosted-checkout credentials are incomplete.")
        payload = {
            "merchant_id": self.merchant_id,
            "merchant_reference": order.reference,
            "amount": f"{order.total:.2f}",
            "currency": order.currency,
            "customer": {"name": order.full_name, "email": order.email},
            "return_url": current_app.config["BANK_MID_RETURN_URL"] or url_for("payment_return", order_id=order.id, _external=True),
            "cancel_url": current_app.config["BANK_MID_CANCEL_URL"] or url_for("order_detail", reference=order.reference, _external=True),
            "webhook_url": url_for("bank_webhook", _external=True),
        }
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
        signature = hmac.new(self.signing_secret.encode(), body, hashlib.sha256).hexdigest()
        response = requests.post(
            urljoin(self.checkout_url + "/", "checkout/sessions"),
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "X-Signature": signature},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return CheckoutSession(provider_reference=data["transaction_reference"], redirect_url=data["redirect_url"])

    def verify_webhook(self, raw_body: bytes, provided_signature: str) -> bool:
        if not self.webhook_secret: return self.mode == "sandbox"
        expected = hmac.new(self.webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, provided_signature or "")
