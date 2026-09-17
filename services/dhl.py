# services/dhl.py
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone


DHL_API_KEY = os.getenv("DHL_API_KEY")
DHL_API_SECRET = os.getenv("DHL_API_SECRET")
DHL_ACCOUNT_NUMBER = os.getenv("DHL_ACCOUNT_NUMBER")
DHL_API_BASE_URL = os.getenv("DHL_API_BASE_URL", "https://express.api.dhl.com/mydhlapi/test")

DEFAULT_TIMEOUT = 30


class DHLConfigurationError(Exception):
    pass


class DHLAPIError(Exception):
    """Raised when the DHL API returns a non-2xx response."""
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class DHLService:
    """
    DHL Express MyDHL API client.

    Covers:
      1. Rate quote
      2. Create shipment
      3. Track shipment
      4. Electronic proof of delivery (ePOD)
      5. Create pickup
      6. Cancel pickup
      7. Validate address
      8. Landing cost (duties & taxes estimate)
      9. List products (services)
      10. Update shipment
      11. Download shipment documents
      13. Country reference list
      14. Service point finder
    """

    def __init__(self):
        if not all([DHL_API_KEY, DHL_API_SECRET, DHL_ACCOUNT_NUMBER]):
            raise DHLConfigurationError(
                "DHL_API_KEY, DHL_API_SECRET and DHL_ACCOUNT_NUMBER must be set"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _auth(self):
        return HTTPBasicAuth(DHL_API_KEY, DHL_API_SECRET)

    def _post(self, path, payload):
        url = f"{DHL_API_BASE_URL}{path}"
        resp = requests.post(
            url,
            json=payload,
            auth=self._auth(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        if not resp.ok:
            raise DHLAPIError(
                f"DHL POST {path} failed: {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    def _get(self, path, params=None):
        url = f"{DHL_API_BASE_URL}{path}"
        resp = requests.get(
            url,
            params=params,
            auth=self._auth(),
            headers={"Accept": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        if not resp.ok:
            raise DHLAPIError(
                f"DHL GET {path} failed: {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    def _patch(self, path, payload):
        url = f"{DHL_API_BASE_URL}{path}"
        resp = requests.patch(
            url,
            json=payload,
            auth=self._auth(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        if not resp.ok:
            raise DHLAPIError(
                f"DHL PATCH {path} failed: {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    def _delete(self, path):
        url = f"{DHL_API_BASE_URL}{path}"
        resp = requests.delete(
            url,
            auth=self._auth(),
            headers={"Accept": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        if not resp.ok:
            raise DHLAPIError(
                f"DHL DELETE {path} failed: {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    # ==================================================================
    # 1. RATE QUOTE
    # ==================================================================
    def get_rates(
        self,
        origin_country, destination_country,
        origin_city=None, origin_postal_code=None,
        destination_city=None, destination_postal_code=None,
        weight_kg=1.0, length_cm=30, width_cm=20, height_cm=10,
        declared_value=100.0, currency="USD",
    ):
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
        return self._post("/rates", payload)

    # ==================================================================
    # 2. CREATE SHIPMENT
    # ==================================================================
    def create_shipment(self, order_data):
        payload = {
            "plannedShippingDateAndTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
            "pickup": {"isRequested": False},
            "productCode": order_data.get("product_code", "P"),
            "localProductCode": order_data.get("product_code", "P"),
            "getRateEstimates": True,
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "valueAddedServices": order_data.get("value_added_services", []),
            "outputImageProperties": {
                "encodingFormat": "pdf",
                "imageOptions": [
                    {"typeCode": "label", "templateName": "ECOM26_84_001", "isRequested": True},
                    {"typeCode": "invoice", "isRequested": True},
                    {"typeCode": "waybillDoc", "isRequested": True},
                ],
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
        return self._post("/shipments", payload)

    # ==================================================================
    # 3. TRACK SHIPMENT
    # ==================================================================
    def track_shipment(self, tracking_number):
        return self._get(f"/shipments/{tracking_number}/tracking")

    # ==================================================================
    # 4. ELECTRONIC PROOF OF DELIVERY (ePOD)
    # ==================================================================
    def get_proof_of_delivery(self, tracking_number):
        """Return signed delivery proof, receiver name, delivery image URL."""
        return self._get(f"/shipments/{tracking_number}/proof-of-delivery")

    # ==================================================================
    # 5. CREATE PICKUP
    # ==================================================================
    def create_pickup(self, pickup_data):
        """
        pickup_data keys:
          planned_pickup_date, close_time, ready_time,
          weight_kg, length_cm, width_cm, height_cm, pieces
        """
        payload = {
            "plannedPickupDateAndTime": pickup_data.get(
                "planned_pickup_date",
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
            ),
            "closeTime": pickup_data.get("close_time", "18:00"),
            "location": "reception",
            "locationType": "business",
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
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
                        "fullName": os.getenv("DHL_ORIGIN_CONTACT", "FABS Shipping"),
                    },
                },
                "pickupDetails": {
                    "postalAddress": {
                        "postalCode": os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                        "cityName": os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                        "countryCode": os.getenv("DHL_ORIGIN_COUNTRY", "KE"),
                        "addressLine1": os.getenv("DHL_ORIGIN_ADDRESS", "FABS Trading Warehouse"),
                    },
                    "contactInformation": {
                        "email": os.getenv("DHL_ORIGIN_EMAIL", "shipping@fabstrading.com"),
                        "phone": os.getenv("DHL_ORIGIN_PHONE", "+254700000000"),
                        "companyName": "FABS Trading",
                        "fullName": os.getenv("DHL_ORIGIN_CONTACT", "FABS Shipping"),
                    },
                },
            },
            "shipmentDetails": [{
                "productCode": "P",
                "localProductCode": "P",
                "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
                "packages": [{
                    "weight": pickup_data.get("weight_kg", 1.0),
                    "dimensions": {
                        "length": pickup_data.get("length_cm", 30),
                        "width": pickup_data.get("width_cm", 20),
                        "height": pickup_data.get("height_cm", 10),
                    },
                    "pieces": pickup_data.get("pieces", 1),
                }],
            }],
        }
        return self._post("/pickups", payload)

    # ==================================================================
    # 6. CANCEL PICKUP
    # ==================================================================
    def cancel_pickup(self, dispatch_confirmation_number):
        return self._delete(f"/pickups/{dispatch_confirmation_number}")

    # ==================================================================
    # 7. ADDRESS VALIDATION
    # ==================================================================
    def validate_address(self, country_code, city_name=None, postal_code=None, address_line1=None):
        payload = {
            "type": "pickup",
            "countryCode": country_code.upper(),
            "cityName": city_name,
            "postalCode": postal_code,
            "addressLine1": address_line1,
            "strictValidation": False,
        }
        return self._post("/address-validate", payload)

    # ==================================================================
    # 8. LANDING COST (Duties & Taxes estimate)
    # ==================================================================
    def estimate_landing_cost(
        self,
        origin_country, destination_country,
        weight_kg=1.0, length_cm=30, width_cm=20, height_cm=10,
        declared_value=100.0, currency="USD",
        is_customs_declarable=True,
    ):
        payload = {
            "customerDetails": {
                "shipperDetails": {
                    "postalCode": os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                    "cityName": os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                    "countryCode": origin_country.upper(),
                },
                "receiverDetails": {
                    "postalCode": "00000",
                    "cityName": "Unknown",
                    "countryCode": destination_country.upper(),
                },
            },
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "productCode": "P",
            "localProductCode": "P",
            "plannedShippingDateAndTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
            "unitOfMeasurement": "metric",
            "isCustomsDeclarable": is_customs_declarable,
            "currency": currency,
            "packages": [{
                "weight": weight_kg,
                "dimensions": {"length": length_cm, "width": width_cm, "height": height_cm},
            }],
            "content": {
                "packages": [{
                    "typeCode": "box",
                    "weight": weight_kg,
                    "dimensions": {"length": length_cm, "width": width_cm, "height": height_cm},
                }],
                "isCustomsDeclarable": is_customs_declarable,
                "declaredValue": declared_value,
                "declaredValueCurrency": currency,
            },
        }
        return self._post("/landing-cost", payload)

    # ==================================================================
    # 9. PRODUCT CODE LIST
    # ==================================================================
    def list_products(self, country_code=None, account_number=None):
        params = {
            "accountNumber": account_number or DHL_ACCOUNT_NUMBER,
        }
        if country_code:
            params["countryCode"] = country_code.upper()
        return self._get("/products", params=params)

    # ==================================================================
    # 10. UPDATE SHIPMENT
    # ==================================================================
    def update_shipment(self, shipment_tracking_number, update_payload):
        return self._patch(f"/shipments/{shipment_tracking_number}", update_payload)

    # ==================================================================
    # 11. DOWNLOAD SHIPMENT DOCUMENTS
    # ==================================================================
    def get_shipment_documents(self, shipment_tracking_number, doc_type="label"):
        """doc_type: 'label' | 'invoice' | 'waybillDoc' | 'receipt'"""
        return self._get(
            f"/shipments/{shipment_tracking_number}/documents",
            params={"typeCode": doc_type, "encodingFormat": "pdf"},
        )

    # ==================================================================
    # 13. COUNTRY REFERENCE LIST
    # ==================================================================
    def list_countries(self):
        return self._get("/reference-data/countries")

    # ==================================================================
    # 14. SERVICE POINT FINDER
    # ==================================================================
    def find_service_points(self, country_code, city=None, postal_code=None, radius_km=10):
        params = {
            "countryCode": country_code.upper(),
            "radius": radius_km,
        }
        if city:
            params["city"] = city
        if postal_code:
            params["postalCode"] = postal_code
        return self._get("/servicepoints", params=params)