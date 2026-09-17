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


# ----------------------------------------------------------------------
# Country defaults for rate estimation when only a country code is known.
# DHL requires BOTH cityName and postalCode for the receiver, but the
# cart and checkout pages only ask for a country. We use the country's
# main commercial hub as a stand-in destination — the returned rate is a
# valid zone-based estimate.
#
# NOTE: these defaults are used ONLY by get_rates() and
# estimate_landing_cost(). validate_address() intentionally does NOT use
# them — see the docstring there for why.
# ----------------------------------------------------------------------
DEFAULT_CITY_BY_COUNTRY = {
    # Africa
    "KE": "Nairobi",       "NG": "Lagos",         "ZA": "Johannesburg",
    "EG": "Cairo",         "TZ": "Dar es Salaam", "UG": "Kampala",
    "GH": "Accra",         "ET": "Addis Ababa",   "MA": "Casablanca",
    "DZ": "Algiers",       "TN": "Tunis",         "LY": "Tripoli",
    "SD": "Khartoum",      "RW": "Kigali",        "ZM": "Lusaka",
    "ZW": "Harare",        "MW": "Lilongwe",      "MZ": "Maputo",
    "AO": "Luanda",        "CM": "Douala",        "CI": "Abidjan",
    "SN": "Dakar",         "MU": "Port Louis",    "MG": "Antananarivo",
    # Americas
    "US": "New York",      "CA": "Toronto",       "MX": "Mexico City",
    "BR": "Sao Paulo",     "AR": "Buenos Aires",  "CL": "Santiago",
    "CO": "Bogota",        "PE": "Lima",          "VE": "Caracas",
    "EC": "Quito",         "UY": "Montevideo",    "PY": "Asuncion",
    "BO": "La Paz",        "CR": "San Jose",      "PA": "Panama City",
    "CU": "Havana",        "DO": "Santo Domingo", "JM": "Kingston",
    # Europe
    "GB": "London",        "DE": "Berlin",        "FR": "Paris",
    "IT": "Rome",          "ES": "Madrid",        "NL": "Amsterdam",
    "BE": "Brussels",      "CH": "Zurich",        "AT": "Vienna",
    "SE": "Stockholm",     "NO": "Oslo",          "DK": "Copenhagen",
    "FI": "Helsinki",      "IE": "Dublin",        "PT": "Lisbon",
    "GR": "Athens",        "PL": "Warsaw",        "CZ": "Prague",
    "RO": "Bucharest",     "HU": "Budapest",      "RU": "Moscow",
    "UA": "Kyiv",          "TR": "Istanbul",      "BG": "Sofia",
    "HR": "Zagreb",        "SK": "Bratislava",    "SI": "Ljubljana",
    "RS": "Belgrade",      "LT": "Vilnius",       "LV": "Riga",
    "EE": "Tallinn",       "IS": "Reykjavik",     "LU": "Luxembourg",
    # Asia
    "CN": "Beijing",       "JP": "Tokyo",         "KR": "Seoul",
    "IN": "Mumbai",        "SG": "Singapore",     "MY": "Kuala Lumpur",
    "TH": "Bangkok",       "VN": "Hanoi",         "PH": "Manila",
    "ID": "Jakarta",       "PK": "Karachi",       "BD": "Dhaka",
    "HK": "Hong Kong",     "TW": "Taipei",        "AE": "Dubai",
    "SA": "Riyadh",        "IL": "Tel Aviv",      "QA": "Doha",
    "KW": "Kuwait City",   "BH": "Manama",        "OM": "Muscat",
    "JO": "Amman",         "LB": "Beirut",        "IQ": "Baghdad",
    "IR": "Tehran",        "AF": "Kabul",         "NP": "Kathmandu",
    "LK": "Colombo",       "MM": "Yangon",        "KH": "Phnom Penh",
    "MN": "Ulaanbaatar",   "KZ": "Almaty",        "UZ": "Tashkent",
    # Oceania
    "AU": "Sydney",        "NZ": "Auckland",      "FJ": "Suva",
    "PG": "Port Moresby",
}


DEFAULT_POSTAL_BY_COUNTRY = {
    # Africa
    "KE": "00100",         "NG": "100001",        "ZA": "2000",
    "EG": "11511",         "TZ": "11101",         "UG": "00100",
    "GH": "GA-100",        "ET": "1000",          "MA": "20000",
    "DZ": "16000",         "TN": "1000",          "LY": "82668",
    "SD": "11111",         "RW": "00100",         "ZM": "10101",
    "ZW": "00263",         "MW": "207201",        "MZ": "1100",
    "AO": "1000",          "CM": "00237",         "CI": "00225",
    "SN": "00221",         "MU": "11324",         "MG": "101",
    # Americas
    "US": "10001",         "CA": "M5V 2T6",       "MX": "06000",
    "BR": "01310-100",     "AR": "C1001",         "CL": "8320000",
    "CO": "110111",        "PE": "15001",         "VE": "1010",
    "EC": "170150",        "UY": "11000",         "PY": "1209",
    "BO": "0001",          "CR": "10101",         "PA": "0801",
    "CU": "10400",         "DO": "10101",         "JM": "00000",
    # Europe
    "GB": "SW1A 1AA",      "DE": "10115",         "FR": "75001",
    "IT": "00118",         "ES": "28001",         "NL": "1011",
    "BE": "1000",          "CH": "8001",          "AT": "1010",
    "SE": "111 22",        "NO": "0150",          "DK": "1050",
    "FI": "00100",         "IE": "D02 X285",      "PT": "1100-148",
    "GR": "105 58",        "PL": "00-001",        "CZ": "110 00",
    "RO": "010011",        "HU": "1011",          "RU": "101000",
    "UA": "01001",         "TR": "34000",         "BG": "1000",
    "HR": "10000",         "SK": "811 01",        "SI": "1000",
    "RS": "11000",         "LT": "01100",         "LV": "1010",
    "EE": "10111",         "IS": "101",           "LU": "1111",
    # Asia
    "CN": "100000",        "JP": "100-0001",      "KR": "03043",
    "IN": "110001",        "SG": "018956",        "MY": "50000",
    "TH": "10110",         "VN": "100000",        "PH": "1000",
    "ID": "10110",         "PK": "44000",         "BD": "1000",
    "HK": "999077",        "TW": "100",           "AE": "00000",
    "SA": "12211",         "IL": "6100001",       "QA": "00000",
    "KW": "13001",         "BH": "00000",         "OM": "100",
    "JO": "11118",         "LB": "1107 2020",     "IQ": "10001",
    "IR": "11155",         "AF": "1001",          "NP": "44600",
    "LK": "00100",         "MM": "11181",         "KH": "120101",
    "MN": "15160",         "KZ": "050000",        "UZ": "100000",
    # Oceania
    "AU": "2000",          "NZ": "1010",          "FJ": "00000",
    "PG": "121",           "NC": "98800",
}


def _resolve_destination(country_code, city, postal_code):
    """
    Return (city, postal_code) with defaults filled in from the country map.

    Used by get_rates() and estimate_landing_cost() — DHL /rates requires
    both values, so when the caller only has a country code (e.g. from the
    cart page) we substitute the country's main commercial hub to obtain
    a valid zone-based estimate.

    Do NOT use this for address validation — the whole point there is to
    check what the user actually typed, not a substituted default.
    """
    cc = (country_code or "").upper()
    if not city:
        city = DEFAULT_CITY_BY_COUNTRY.get(cc) or cc
    if not postal_code:
        postal_code = DEFAULT_POSTAL_BY_COUNTRY.get(cc) or cc
    return city, postal_code


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
                f"DHL POST {path} failed: {resp.status_code} — {resp.text[:300]}",
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
                f"DHL GET {path} failed: {resp.status_code} — {resp.text[:300]}",
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
                f"DHL PATCH {path} failed: {resp.status_code} — {resp.text[:300]}",
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
                f"DHL DELETE {path} failed: {resp.status_code} — {resp.text[:300]}",
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
        # Fill in missing destination details from the country lookup.
        destination_city, destination_postal_code = _resolve_destination(
            destination_country, destination_city, destination_postal_code
        )

        # Shipper block — origin defaults.
        shipper = {
            "countryCode": origin_country.upper(),
            "cityName": origin_city or os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
            "postalCode": origin_postal_code or os.getenv("DHL_ORIGIN_POSTAL", "00100"),
        }

        # Receiver block — always has city + postal now.
        receiver = {
            "countryCode": destination_country.upper(),
            "cityName": destination_city,
            "postalCode": destination_postal_code,
        }

        # Customs only for cross-border shipments.
        is_international = origin_country.upper() != destination_country.upper()

        payload = {
            "customerDetails": {
                "shipperDetails": shipper,
                "receiverDetails": receiver,
            },
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "productCode": "P",
            "localProductCode": "P",
            "valueAddedServices": [],
            "plannedShippingDateAndTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S GMT%z"),
            "unitOfMeasurement": "metric",
            "isCustomsDeclarable": is_international,
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
        """
        DHL Address Validation API — GET /address-validate with query params.

        DHL uses this endpoint to check serviceability (can DHL pick up or
        deliver at this address) and to suggest corrections for city or
        postal code. It is not a full postal-address verification service.

        Required query params:
          type        : "pickup" or "delivery"
          countryCode : ISO 3166-1 alpha-2

        Optional: cityName, postalCode, countyName, addressLine1..3,
        strictValidation.

        IMPORTANT: this method passes ONLY the values the caller provides.
        It does NOT substitute the country-default city/postal from
        DEFAULT_CITY_BY_COUNTRY / DEFAULT_POSTAL_BY_COUNTRY. Those defaults
        are appropriate for rate estimation (where we need any valid
        destination), but for address validation we must check exactly what
        the user typed — otherwise we could falsely "verify" an address
        against a default the user never entered.
        """
        cc = (country_code or "").upper()
        if not cc:
            raise DHLConfigurationError("country_code is required for address validation")

        params = {
            "type": "delivery",
            "countryCode": cc,
            "strictValidation": "false",
        }
        if city_name:
            params["cityName"] = city_name
        if postal_code:
            params["postalCode"] = postal_code
        if address_line1:
            params["addressLine1"] = address_line1

        return self._get("/address-validate", params=params)

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
        # Same default-fill treatment as get_rates.
        destination_city, destination_postal_code = _resolve_destination(
            destination_country, None, None
        )

        payload = {
            "customerDetails": {
                "shipperDetails": {
                    "postalCode": os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                    "cityName": os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                    "countryCode": origin_country.upper(),
                },
                "receiverDetails": {
                    "postalCode": destination_postal_code,
                    "cityName": destination_city,
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
        """Return DHL's country reference list as flat dicts."""
        raw = self._get("/reference-data", params={"datasetName": "country"})

        entries = []
        for block in raw.get("referenceData", []):
            for item in block.get("data", []):
                row = {}
                if isinstance(item, list):
                    for pair in item:
                        attr = pair.get("attribute")
                        val = pair.get("value")
                        if attr:
                            row[attr] = val
                elif isinstance(item, dict):
                    row = item
                if row.get("countryCode"):
                    entries.append(row)

        return entries

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