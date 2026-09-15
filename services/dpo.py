import os
import requests
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from xml.etree import ElementTree as ET


DPO_API_URL = os.getenv("DPO_API_URL", "https://secure.3gdirectpay.com/API/v6/")
DPO_PAYMENT_URL = os.getenv(
    "DPO_PAYMENT_URL_TEMPLATE",
    "https://secure.3gdirectpay.com/payv3.php?ID={token}",
)
DPO_COMPANY_TOKEN = os.getenv("DPO_COMPANY_TOKEN", "")
DPO_SERVICE_TYPES = [
    s.strip() for s in os.getenv("DPO_SERVICE_TYPES", "").split(",") if s.strip()
]


@dataclass
class DPOCheckoutSession:
    provider_reference: str   # the TransToken
    redirect_url: str         # DPO hosted payment page


class PaymentConfigurationError(Exception):
    pass


class DPOGateway:
    def __init__(self):
        if not DPO_COMPANY_TOKEN:
            raise PaymentConfigurationError("DPO_COMPANY_TOKEN is not set")

    def create_checkout(self, order) -> DPOCheckoutSession:
        redirect_url = f"{os.getenv('PUBLIC_BASE_URL', '').rstrip('/')}/payments/return/{order.id}"
        back_url = f"{os.getenv('PUBLIC_BASE_URL', '').rstrip('/')}/orders/{order.reference}"

        # Services block — use your assigned service types
        services_xml = "".join(
            f"""
            <Service>
              <ServiceType>{st}</ServiceType>
              <ServiceDescription>FABS Trading order {order.reference}</ServiceDescription>
              <ServiceDate>{datetime.now(timezone.utc).strftime('%Y/%m/%d %H:%M')}</ServiceDate>
            </Service>"""
            for st in DPO_SERVICE_TYPES
        )

        amount = Decimal(order.total).quantize(Decimal("0.01"))
        payload = f"""<?xml version="1.0" encoding="utf-8"?>
<API3G>
  <CompanyToken>{DPO_COMPANY_TOKEN}</CompanyToken>
  <Request>createToken</Request>
  <Transaction>
    <PaymentAmount>{amount}</PaymentAmount>
    <PaymentCurrency>{order.currency}</PaymentCurrency>
    <CompanyRef>{order.reference}</CompanyRef>
    <RedirectURL>{redirect_url}</RedirectURL>
    <BackURL>{back_url}</BackURL>
    <CompanyRefUnique>1</CompanyRefUnique>
    <PTL>24</PTL>
    <customerEmail>{order.email}</customerEmail>
    <customerFirstName>{order.full_name}</customerFirstName>
  </Transaction>
  <Services>{services_xml}
  </Services>
</API3G>"""

        response = requests.post(
            DPO_API_URL,
            data=payload.encode("utf-8"),
            headers={
                "Content-Type": "application/xml; charset=utf-8",
                "Accept": "application/xml",
            },
            timeout=20,
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        result = (root.findtext("Result") or "").strip()
        if result != "000":
            explanation = root.findtext("ResultExplanation") or "Unknown DPO error"
            raise PaymentConfigurationError(f"DPO createToken failed: {result} — {explanation}")

        trans_token = root.findtext("TransToken")
        if not trans_token:
            raise PaymentConfigurationError("DPO did not return a TransToken")

        return DPOCheckoutSession(
            provider_reference=trans_token,
            redirect_url=DPO_PAYMENT_URL.format(token=trans_token),
        )

    def verify_token(self, transaction_token: str) -> dict:
        payload = f"""<?xml version="1.0" encoding="utf-8"?>
<API3G>
  <CompanyToken>{DPO_COMPANY_TOKEN}</CompanyToken>
  <Request>verifyToken</Request>
  <TransactionToken>{transaction_token}</TransactionToken>
</API3G>"""

        response = requests.post(
            DPO_API_URL,
            data=payload.encode("utf-8"),
            headers={
                "Content-Type": "application/xml; charset=utf-8",
                "Accept": "application/xml",
            },
            timeout=20,
        )
        response.raise_for_status()
        root = ET.fromstring(response.text)

        return {
            "result": (root.findtext("Result") or "").strip(),
            "explanation": root.findtext("ResultExplanation") or "",
            "customer_name": root.findtext("CustomerName") or "",
            "customer_credit": root.findtext("CustomerCredit") or "",
            "customer_credit_type": root.findtext("CustomerCreditType") or "",
            "transaction_approval": root.findtext("TransactionApproval") or "",
            "transaction_currency": root.findtext("TransactionCurrency") or "",
            "transaction_amount": root.findtext("TransactionAmount") or "",
            "company_ref": root.findtext("CompanyRef") or "",
        }