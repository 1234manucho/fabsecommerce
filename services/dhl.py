# services/dhl.py
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone


DHL_API_KEY = os.getenv("DHL_API_KEY")
DHL_API_SECRET = os.getenv("DHL_API_SECRET")
DHL_ACCOUNT_NUMBER = os.getenv("DHL_ACCOUNT_NUMBER")
DHL_API_BASE_URL = os.getenv("DHL_API_BASE_URL", "https://express.api.dhl.com/mydhlapi/test")


class DHLConfigurationError(Exception):
    pass


class DHLService:
    def __init__(self):
        if not all([DHL_API_KEY, DHL_API_SECRET, DHL_ACCOUNT_NUMBER]):
            raise DHLConfigurationError(
                "DHL_API_KEY, DHL_API_SECRET and DHL_ACCOUNT_NUMBER must be set"
            )

    def _auth(self):
        return HTTPBasicAuth(DHL_API_KEY, DHL_API_SECRET)

    def get_rates(
        self,
        origin_country, destination_country,
        origin_city=None, origin_postal_code=None,
        destination_city=None, destination_postal_code=None,
        weight_kg=1.0, length_cm=30, width_cm=20, height_cm=10,
        declared_value=100.0, currency="USD",
    ):
        url = f"{DHL_API_BASE_URL}/rates"
        payload = {
            "customerDetails": {
                "shipperDetails": {
                    "postalCode": origin_postal_code or "00100",
                    "cityName": origin_city or "Nairobi",
                    "countryCode": origin_country.upper(),
                },
                "receiverDetails": {
                    "postalCode": destination_postal_code or "00000",
                    "cityName": destination_city or "Unknown",
                    "countryCode": destination_country.upper(),
                },
            },
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "productCode": "P",
            "localProductCode": "P",
            "getRateEstimates": True,
            "valueAddedServices": [],
            "plannedShippingDateAndTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
            "unitOfMeasurement": "metric",
            "isCustomsDeclarable": True,
            "monetaryAmount": [
                {"typeCode": "declaredValue", "value": declared_value, "currency": currency}
            ],
            "packages": [
                {
                    "weight": weight_kg,
                    "dimensions": {"length": length_cm, "width": width_cm, "height": height_cm},
                }
            ],
        }
        resp = requests.post(url, json=payload, auth=self._auth(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def create_shipment(self, order_data):
        url = f"{DHL_API_BASE_URL}/shipments"
        payload = {
            "plannedShippingDateAndTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
            "pickup": {"isRequested": False},
            "productCode": "P",
            "localProductCode": "P",
            "getRateEstimates": True,
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "valueAddedServices": [],
            "outputImageProperties": {
                "encodingFormat": "pdf",
                "imageOptions": [{"typeCode": "label", "templateName": "ECOM26_84_001", "isRequested": True}],
            },
            "customerDetails": {
                "shipperDetails": {
                    "postalAddress": {
                        "postalCode": os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                        "cityName": os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                        "countryCode": os.getenv("DHL_ORIGIN_COUNTRY", "KE"),
                        "addressLine1": os.getenv("DHL_ORIGIN_ADDRESS", "FABS Trading Warehouse"),
                        "addressLine2": os.getenv("DHL_ORIGIN_ADDRESS2", ""),
                    },
                    "contactInformation": {
                        "email": os.getenv("DHL_ORIGIN_EMAIL", "shipping@fabstrading.com"),
                        "phone": os.getenv("DHL_ORIGIN_PHONE", "+254700000000"),
                        "companyName": "FABS Trading",
                        "fullName": "FABS Shipping",
                    },
                },
                "receiverDetails": {
                    "postalAddress": {
                        "postalCode": order_data.get("receiver_postal_code", ""),
                        "cityName": order_data.get("receiver_city", ""),
                        "countryCode": order_data.get("receiver_country", ""),
                        "addressLine1": order_data.get("receiver_address_line1", ""),
                        "addressLine2": order_data.get("receiver_address_line2", ""),
                    },
                    "contactInformation": {
                        "email": order_data.get("receiver_email", ""),
                        "phone": order_data.get("receiver_phone", ""),
                        "companyName": order_data.get("receiver_company", ""),
                        "fullName": order_data.get("receiver_full_name", ""),
                    },
                },
            },
            "content": {
                "packages": [{
                    "weight": order_data.get("package_weight_kg", 1.0),
                    "dimensions": {
                        "length": order_data.get("package_length_cm", 30),
                        "width": order_data.get("package_width_cm", 20),
                        "height": order_data.get("package_height_cm", 10),
                    },
                    "description": order_data.get("package_description", "Gaming products"),
                }],
                "isCustomsDeclarable": True,
                "declaredValue": order_data.get("declared_value", 100.0),
                "declaredValueCurrency": order_data.get("currency", "USD"),
                "exportDeclaration": {
                    "lineItems": [{
                        "number": 1,
                        "description": order_data.get("package_description", "Gaming products"),
                        "price": order_data.get("declared_value", 100.0),
                        "quantity": {"value": 1, "unitOfMeasurement": "PCS"},
                        "weight": {
                            "netValue": order_data.get("package_weight_kg", 1.0),
                            "grossValue": order_data.get("package_weight_kg", 1.0),
                        },
                        "manufacturerCountry": os.getenv("DHL_ORIGIN_COUNTRY", "KE"),
                        "exportReasonType": "permanent",
                    }],
                    "invoice": {
                        "number": order_data.get("order_reference", "FABS-ORDER"),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                    },
                },
            },
        }
        resp = requests.post(url, json=payload, auth=self._auth(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def track_shipment(self, tracking_number):
        url = f"{DHL_API_BASE_URL}/shipments/{tracking_number}/tracking"
        resp = requests.get(url, auth=self._auth(), timeout=30)
        resp.raise_for_status()
        return resp.json()