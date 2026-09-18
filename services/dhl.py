# services/dhl.py
import os
import re
import unicodedata
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone


DHL_API_KEY = os.getenv("DHL_API_KEY")
DHL_API_SECRET = os.getenv("DHL_API_SECRET")
DHL_ACCOUNT_NUMBER = os.getenv("DHL_ACCOUNT_NUMBER")
DHL_API_BASE_URL = (
    os.getenv("DHL_API_BASE_URL")
    or os.getenv("DHL_API_BASE")
    or "https://express.api.dhl.com/mydhlapi/test"
).rstrip("/")

DEFAULT_TIMEOUT = 30


# ======================================================================
# TRACKING — status code mapping
# ======================================================================
TRACKING_STATUS_MAP = {
    "pre-transit": "pre-transit",
    "pretransit":  "pre-transit",
    "transit":     "transit",
    "delivered":   "delivered",
    "failure":     "failure",
    "exception":   "failure",
    "unknown":     "unknown",
}


DEFAULT_CITY_BY_COUNTRY = {
    "KE": "Nairobi",       "NG": "Lagos",         "ZA": "Johannesburg",
    "EG": "Cairo",         "TZ": "Dar es Salaam", "UG": "Kampala",
    "GH": "Accra",         "ET": "Addis Ababa",   "MA": "Casablanca",
    "DZ": "Algiers",       "TN": "Tunis",         "LY": "Tripoli",
    "SD": "Khartoum",      "RW": "Kigali",        "ZM": "Lusaka",
    "ZW": "Harare",        "MW": "Lilongwe",      "MZ": "Maputo",
    "AO": "Luanda",        "CM": "Douala",        "CI": "Abidjan",
    "SN": "Dakar",         "MU": "Port Louis",    "MG": "Antananarivo",
    "US": "New York",      "CA": "Toronto",       "MX": "Mexico City",
    "BR": "Sao Paulo",     "AR": "Buenos Aires",  "CL": "Santiago",
    "CO": "Bogota",        "PE": "Lima",          "VE": "Caracas",
    "EC": "Quito",         "UY": "Montevideo",    "PY": "Asuncion",
    "BO": "La Paz",        "CR": "San Jose",      "PA": "Panama City",
    "CU": "Havana",        "DO": "Santo Domingo", "JM": "Kingston",
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
    "AU": "Sydney",        "NZ": "Auckland",      "FJ": "Suva",
    "PG": "Port Moresby",
}


DEFAULT_POSTAL_BY_COUNTRY = {
    "KE": "00100",         "NG": "100001",        "ZA": "2000",
    "EG": "11511",         "TZ": "11101",         "UG": "00100",
    "GH": "GA-100",        "ET": "1000",          "MA": "20000",
    "DZ": "16000",         "TN": "1000",          "LY": "82668",
    "SD": "11111",         "RW": "00100",         "ZM": "10101",
    "ZW": "00263",         "MW": "207201",        "MZ": "1100",
    "AO": "1000",          "CM": "00237",         "CI": "00225",
    "SN": "00221",         "MU": "11324",         "MG": "101",
    "US": "10001",         "CA": "M5V 2T6",       "MX": "06000",
    "BR": "01310-100",     "AR": "C1001",         "CL": "8320000",
    "CO": "110111",        "PE": "15001",         "VE": "1010",
    "EC": "170150",        "UY": "11000",         "PY": "1209",
    "BO": "0001",          "CR": "10101",         "PA": "0801",
    "CU": "10400",         "DO": "10101",         "JM": "00000",
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
    "AU": "2000",          "NZ": "1010",          "FJ": "00000",
    "PG": "121",           "NC": "98800",
}


DEFAULT_PHONE_FALLBACK = os.getenv("DHL_FALLBACK_PHONE", "+254729004000")


# DHL requires ISO-3166 alpha-2 country codes.  Checkout data can contain
# common names or non-standard aliases (for example ``UK``), so every public
# DHL operation passes through one normaliser before a payload is sent.
ISO_ALPHA2_COUNTRY_CODES = frozenset("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ
BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ
CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ
DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR
GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY
HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP
KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY
MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ
NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY
QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ
TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ
VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split())


COUNTRY_CODE_ALIASES = {
    # Frequently entered non-standard codes.
    "UK": "GB",
    "EL": "GR",
    "UAE": "AE",
    "KSA": "SA",
    "DRC": "CD",
    # Common ISO-3 values seen in imported address data.
    "KEN": "KE", "USA": "US", "GBR": "GB", "ARE": "AE",
    "ZAF": "ZA", "NGA": "NG", "UGA": "UG", "TZA": "TZ",
    "GHA": "GH", "ETH": "ET", "RWA": "RW", "CAN": "CA",
    "AUS": "AU", "NZL": "NZ", "CHN": "CN", "HKG": "HK",
    "IND": "IN", "SGP": "SG", "DEU": "DE", "FRA": "FR",
    "ITA": "IT", "ESP": "ES", "NLD": "NL", "CHE": "CH",
    "SWE": "SE", "NOR": "NO", "DNK": "DK", "FIN": "FI",
    "IRL": "IE", "PRT": "PT", "GRC": "GR", "POL": "PL",
    "CZE": "CZ", "ROU": "RO", "HUN": "HU", "TUR": "TR",
    "JPN": "JP", "KOR": "KR", "SAU": "SA", "QAT": "QA",
    "BHR": "BH", "OMN": "OM", "KWT": "KW",
    # Country names commonly used by FABS buyers.
    "KENYA": "KE",
    "UNITED STATES": "US",
    "UNITED STATES OF AMERICA": "US",
    "U S": "US",
    "U S A": "US",
    "UNITED KINGDOM": "GB",
    "GREAT BRITAIN": "GB",
    "BRITAIN": "GB",
    "ENGLAND": "GB",
    "SCOTLAND": "GB",
    "WALES": "GB",
    "NORTHERN IRELAND": "GB",
    "UNITED ARAB EMIRATES": "AE",
    "SOUTH AFRICA": "ZA",
    "NIGERIA": "NG",
    "UGANDA": "UG",
    "TANZANIA": "TZ",
    "UNITED REPUBLIC OF TANZANIA": "TZ",
    "GHANA": "GH",
    "ETHIOPIA": "ET",
    "RWANDA": "RW",
    "CANADA": "CA",
    "AUSTRALIA": "AU",
    "NEW ZEALAND": "NZ",
    "CHINA": "CN",
    "HONG KONG": "HK",
    "INDIA": "IN",
    "SINGAPORE": "SG",
    "GERMANY": "DE",
    "FRANCE": "FR",
    "ITALY": "IT",
    "SPAIN": "ES",
    "NETHERLANDS": "NL",
    "SWITZERLAND": "CH",
    "JAPAN": "JP",
    "SOUTH KOREA": "KR",
    "REPUBLIC OF KOREA": "KR",
    "SAUDI ARABIA": "SA",
    "COTE D IVOIRE": "CI",
    "IVORY COAST": "CI",
    "DEMOCRATIC REPUBLIC OF THE CONGO": "CD",
    "DEMOCRATIC REPUBLIC OF CONGO": "CD",
    "REPUBLIC OF THE CONGO": "CG",
}


def normalize_country_code(value, field_name="country"):
    """Return a validated DHL/ISO alpha-2 country code.

    Accepts ISO-2, common ISO-3 values, country names, and labelled values such
    as ``US - United States`` or ``United Kingdom (UK)``.  Non-standard ``UK``
    is converted to the DHL-compatible code ``GB``.
    """
    raw = str(value or "").strip()
    if not raw:
        raise DHLConfigurationError(f"{field_name} is required")

    ascii_value = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    token = re.sub(r"[^A-Z0-9]+", " ", ascii_value.upper()).strip()
    compact = token.replace(" ", "")

    for candidate in (token, compact):
        code = COUNTRY_CODE_ALIASES.get(candidate, candidate)
        if code in ISO_ALPHA2_COUNTRY_CODES:
            return code

    # Handle labelled select values such as "US - United States" and
    # "United Kingdom (UK)" without accepting an arbitrary invalid code.
    parts = token.split()
    for candidate in (parts[0] if parts else "", parts[-1] if parts else ""):
        code = COUNTRY_CODE_ALIASES.get(candidate, candidate)
        if code in ISO_ALPHA2_COUNTRY_CODES:
            return code

    raise DHLConfigurationError(
        f"{field_name} must be a valid ISO-3166 alpha-2 country code "
        f"(for example KE, US or GB); got {raw!r}"
    )


def _dhl_now(hours_ahead=2):
    """
    Return a DHL-compliant planned shipping datetime string.

    DHL requires:
      - ISO-8601 with an offset formatted as +HH:MM (colon required)
      - A time in the near future

    Example output: '2026-09-17T14:30:00 GMT+00:00'
    """
    dt = datetime.now(timezone.utc) + timedelta(hours=hours_ahead)
    offset = dt.strftime("%z")                     # "+0000"
    offset_colon = offset[:3] + ":" + offset[3:]   # "+00:00"
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + " GMT" + offset_colon


def _resolve_destination(country_code, city, postal_code):
    cc = normalize_country_code(country_code, "destination country")
    if not city:
        city = DEFAULT_CITY_BY_COUNTRY.get(cc) or cc
    if not postal_code:
        postal_code = DEFAULT_POSTAL_BY_COUNTRY.get(cc) or cc
    return city, postal_code


def _parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    text = str(value).strip().replace(" GMT", "").replace("Z", "+00:00")

    if re.fullmatch(r"\d{14}", text):
        try:
            return datetime.strptime(text, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    try:
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _clean_payload(value):
    """
    Recursively remove empty values from a payload before sending it to DHL.

    DHL rejects empty strings even for optional fields:
        addressLine2: "" -> "expected minLength: 1, actual: 0"
    """
    if isinstance(value, dict):
        cleaned = {}
        for k, v in value.items():
            v2 = _clean_payload(v)
            if v2 is None:
                continue
            if isinstance(v2, str) and not v2.strip():
                continue
            if isinstance(v2, (list, dict)) and len(v2) == 0:
                continue
            cleaned[k] = v2
        return cleaned

    if isinstance(value, list):
        return [_clean_payload(v) for v in value]

    return value


class DHLConfigurationError(Exception):
    pass


class DHLAPIError(Exception):
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class DHLService:

    def __init__(self):
        if not all([DHL_API_KEY, DHL_API_SECRET, DHL_ACCOUNT_NUMBER]):
            raise DHLConfigurationError(
                "DHL_API_KEY, DHL_API_SECRET and DHL_ACCOUNT_NUMBER must be set"
            )

    @classmethod
    def is_configured(cls):
        return all([DHL_API_KEY, DHL_API_SECRET, DHL_ACCOUNT_NUMBER])

    def _auth(self):
        return HTTPBasicAuth(DHL_API_KEY, DHL_API_SECRET)

    def _post(self, path, payload):
        url = f"{DHL_API_BASE_URL}{path}"
        payload = _clean_payload(payload)
        resp = requests.post(
            url,
            json=payload,
            auth=self._auth(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        if not resp.ok:
            raise DHLAPIError(
                f"DHL POST {path} failed: {resp.status_code} — {resp.text[:500]}",
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
                f"DHL GET {path} failed: {resp.status_code} — {resp.text[:500]}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    def _patch(self, path, payload):
        url = f"{DHL_API_BASE_URL}{path}"
        payload = _clean_payload(payload)
        resp = requests.patch(
            url,
            json=payload,
            auth=self._auth(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=DEFAULT_TIMEOUT,
        )
        if not resp.ok:
            raise DHLAPIError(
                f"DHL PATCH {path} failed: {resp.status_code} — {resp.text[:500]}",
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
                f"DHL DELETE {path} failed: {resp.status_code} — {resp.text[:500]}",
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
        product_code=None, local_product_code=None,
    ):
        origin_country = normalize_country_code(origin_country, "origin country")
        destination_country = normalize_country_code(
            destination_country, "destination country"
        )
        destination_city, destination_postal_code = _resolve_destination(
            destination_country, destination_city, destination_postal_code
        )

        shipper = {
            "countryCode": origin_country.upper(),
            "cityName": origin_city or os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
            "postalCode": origin_postal_code or os.getenv("DHL_ORIGIN_POSTAL", "00100"),
        }
        receiver = {
            "countryCode": destination_country.upper(),
            "cityName": destination_city,
            "postalCode": destination_postal_code,
        }

        is_international = origin_country.upper() != destination_country.upper()

        payload = {
            "customerDetails": {
                "shipperDetails": shipper,
                "receiverDetails": receiver,
            },
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "valueAddedServices": [],
            "plannedShippingDateAndTime": _dhl_now(hours_ahead=2),
            "unitOfMeasurement": "metric",
            "isCustomsDeclarable": is_international,
            "packages": [
                {
                    "weight": weight_kg,
                    "dimensions": {"length": length_cm, "width": width_cm, "height": height_cm},
                }
            ],
        }
        if is_international:
            payload["monetaryAmount"] = [{
                "typeCode": "declaredValue",
                "value": declared_value,
                "currency": str(currency or "USD").upper(),
            }]

        # Omitting product codes asks DHL Rating to return every product that
        # is actually available for this account, route, date and package.
        # A code can still be supplied by callers that want to quote one
        # specific product.
        if product_code:
            payload["productCode"] = str(product_code).strip().upper()
            payload["localProductCode"] = str(
                local_product_code or product_code
            ).strip().upper()

        return self._post("/rates", payload)

    @staticmethod
    def _select_rate_product(rate_result, preferred_product=None, preferred_local=None):
        """Return an account-eligible (global code, local code) rate product."""
        products = rate_result.get("products", []) if isinstance(rate_result, dict) else []
        products = [
            product for product in products
            if isinstance(product, dict)
            and (product.get("productCode") or product.get("localProductCode"))
        ]

        if not products:
            return None

        # Prefer products tied to the customer's DHL agreement.  Some Rating
        # responses may also contain public products that the payer account is
        # not enabled to purchase.
        agreement_products = [
            product for product in products
            if product.get("isCustomerAgreement") is True
        ]
        candidates = agreement_products or products

        preferred_product = str(preferred_product or "").strip().upper()
        preferred_local = str(preferred_local or "").strip().upper()

        for product in candidates:
            global_code = str(product.get("productCode") or "").strip().upper()
            local_code = str(
                product.get("localProductCode") or global_code
            ).strip().upper()
            global_matches = not preferred_product or global_code == preferred_product
            local_matches = not preferred_local or local_code == preferred_local
            if (preferred_product or preferred_local) and global_matches and local_matches:
                return global_code, local_code

        selected = candidates[0]
        global_code = str(
            selected.get("productCode") or selected.get("localProductCode")
        ).strip().upper()
        local_code = str(
            selected.get("localProductCode") or global_code
        ).strip().upper()
        return global_code, local_code

    # ==================================================================
    # 2. CREATE SHIPMENT
    # ==================================================================
    def create_shipment(self, order_data):
        order_data = dict(order_data or {})
        order_data["receiver_country"] = normalize_country_code(
            order_data.get("receiver_country"), "receiver_country"
        )
        self._validate_create_shipment_payload(order_data)

        shipper_phone = os.getenv("DHL_ORIGIN_PHONE") or DEFAULT_PHONE_FALLBACK
        shipper_email = os.getenv("DHL_ORIGIN_EMAIL", "shipping@fabstrading.com")
        shipper_company = os.getenv("DHL_ORIGIN_COMPANY", "FABS Trading Global E-Commerce")
        shipper_contact = os.getenv("DHL_ORIGIN_CONTACT", "FABS Shipping")

        receiver_phone = order_data.get("receiver_phone") or DEFAULT_PHONE_FALLBACK
        receiver_email = order_data.get("receiver_email") or "no-reply@fabstrading.com"
        receiver_name = str(order_data.get("receiver_full_name") or "Receiver").strip()
        # DHL requires companyName even when the consignee is an individual.  An
        # empty value would otherwise be removed by _clean_payload(), producing
        # a 422 "required key [companyName] not found" response.
        receiver_company = str(order_data.get("receiver_company") or "").strip()
        if not receiver_company:
            receiver_company = receiver_name

        origin_country = normalize_country_code(
            os.getenv("DHL_ORIGIN_COUNTRY", "KE"), "DHL_ORIGIN_COUNTRY"
        )
        destination_country = order_data["receiver_country"]
        is_international = origin_country != destination_country

        package_desc = order_data.get("package_description") or "Gaming products"
        order_reference = str(
            order_data.get("order_reference") or "FABS-ORDER"
        ).strip()
        weight = float(order_data.get("package_weight_kg") or 1.0)
        declared_value = float(order_data.get("declared_value") or 100.0)
        currency = (order_data.get("currency") or "USD").upper()

        package_block = {
            "weight": weight,
            "dimensions": {
                "length": float(order_data.get("package_length_cm") or 30.0),
                "width":  float(order_data.get("package_width_cm") or 20.0),
                "height": float(order_data.get("package_height_cm") or 10.0),
            },
            "description": package_desc,
        }

        preferred_product = (
            order_data.get("product_code")
            or os.getenv("DHL_PRODUCT_CODE")
            or ("P" if is_international else "N")
        )
        preferred_local_product = (
            order_data.get("local_product_code")
            or os.getenv("DHL_LOCAL_PRODUCT_CODE")
            or None
        )

        try:
            rate_result = self.get_rates(
                origin_country=origin_country,
                destination_country=destination_country,
                origin_city=os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                origin_postal_code=os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                destination_city=order_data.get("receiver_city"),
                destination_postal_code=order_data.get("receiver_postal_code"),
                weight_kg=weight,
                length_cm=package_block["dimensions"]["length"],
                width_cm=package_block["dimensions"]["width"],
                height_cm=package_block["dimensions"]["height"],
                declared_value=declared_value,
                currency=currency,
            )
        except DHLAPIError as exc:
            error_text = f"{exc} {exc.response_body or ''}".lower()
            if "1001" in error_text or "410138" in error_text:
                raise DHLConfigurationError(
                    "DHL has no shipping product enabled for "
                    f"{origin_country} to {destination_country} on this payer account. "
                    "Ask DHL to enable the required route/product or use an eligible account."
                ) from exc
            raise

        selected_product = self._select_rate_product(
            rate_result,
            preferred_product=preferred_product,
            preferred_local=preferred_local_product,
        )
        if not selected_product:
            raise DHLConfigurationError(
                "DHL Rating returned no available shipping product for "
                f"{origin_country} to {destination_country}. "
                "Verify the destination, package details and DHL account permissions."
            )
        product_code, local_product_code = selected_product

        content_block = {
            "packages": [package_block],
            "isCustomsDeclarable": is_international,
            "description": package_desc,
            "unitOfMeasurement": "metric",
            "declaredValue": declared_value,
            "declaredValueCurrency": currency,
        }

        if is_international:
            content_block["incoterm"] = order_data.get("incoterm", "DAP")
            content_block["exportDeclaration"] = {
                "lineItems": [{
                    "number": 1,
                    "description": package_desc,
                    "price": declared_value,
                    "quantity": {"value": 1, "unitOfMeasurement": "PCS"},
                    "weight": {
                        "netValue": weight,
                        "grossValue": weight,
                    },
                    "manufacturerCountry": origin_country,
                    "exportReasonType": "permanent",
                }],
                "invoice": {
                    "number": order_reference,
                    "date": datetime.now(timezone.utc).date().isoformat(),
                },
            }

        # A DHL-generated commercial invoice is customs documentation.  Asking
        # for it on a domestic shipment (where no exportDeclaration is valid)
        # triggers DHL error 7032.  Keep labels/waybills for every shipment and
        # request the invoice only for customs-declarable shipments.
        image_options = [
            {"typeCode": "label", "templateName": "ECOM26_84_001", "isRequested": True},
            {"typeCode": "waybillDoc", "isRequested": True},
        ]
        if is_international:
            image_options.append({
                "typeCode": "invoice",
                "templateName": "COMMERCIAL_INVOICE_P_10",
                "isRequested": True,
            })

        payload = {
            "plannedShippingDateAndTime": _dhl_now(hours_ahead=2),
            "pickup": {"isRequested": False},
            "productCode": product_code,
            "localProductCode": local_product_code,
            "accounts": [{"typeCode": "shipper", "number": DHL_ACCOUNT_NUMBER}],
            "valueAddedServices": order_data.get("value_added_services", []),
            "outputImageProperties": {
                "encodingFormat": "pdf",
                "imageOptions": image_options,
            },
            "customerDetails": {
                "shipperDetails": {
                    "postalAddress": {
                        "postalCode": os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                        "cityName": os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                        "countryCode": origin_country,
                        "addressLine1": os.getenv("DHL_ORIGIN_ADDRESS", "FABS Trading Warehouse"),
                        "addressLine2": os.getenv("DHL_ORIGIN_ADDRESS2", ""),
                    },
                    "contactInformation": {
                        "email": shipper_email,
                        "phone": shipper_phone,
                        "companyName": shipper_company,
                        "fullName": shipper_contact,
                    },
                },
                "receiverDetails": {
                    "postalAddress": {
                        "postalCode": order_data.get("receiver_postal_code", ""),
                        "cityName": order_data.get("receiver_city", ""),
                        "countryCode": destination_country,
                        "addressLine1": order_data.get("receiver_address_line1", ""),
                        "addressLine2": order_data.get("receiver_address_line2", ""),
                    },
                    "contactInformation": {
                        "email": receiver_email,
                        "phone": receiver_phone,
                        "companyName": receiver_company,
                        "fullName": receiver_name,
                    },
                },
            },
            "content": content_block,
        }

        return self._post("/shipments", payload)

    @staticmethod
    def _validate_create_shipment_payload(order_data):
        required = {
            "receiver_full_name": "Receiver full name",
            "receiver_address_line1": "Receiver address line 1",
            "receiver_city": "Receiver city",
            "receiver_postal_code": "Receiver postal code",
            "receiver_country": "Receiver country (ISO-2)",
        }
        missing = [label for key, label in required.items() if not order_data.get(key)]

        if missing:
            raise DHLConfigurationError(
                "Missing required shipment fields: " + ", ".join(missing)
            )

        normalize_country_code(order_data.get("receiver_country"), "receiver_country")

        try:
            weight = float(order_data.get("package_weight_kg") or 0)
            if weight <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise DHLConfigurationError("package_weight_kg must be a positive number")

    # ==================================================================
    # 3. TRACK SHIPMENT (normalised)
    # ==================================================================
    def track_shipment(self, tracking_number):
        """
        Fetch DHL tracking for a shipment and return a NORMALISED dict.

        If DHL has no events yet (which is normal for a label that was just
        created and hasn't been picked up), returns an 'unknown' status with
        an empty event list instead of raising.

        This is important because DHL returns 404 "No data found" for any
        tracking number that exists in their system but has no physical scan.
        """
        try:
            raw = self.track_shipment_raw(tracking_number)
        except DHLAPIError as exc:
            # DHL returns 404 "No data found" until the first scan happens.
            if exc.status_code == 404:
                return self._empty_tracking(tracking_number, raw={
                    "info": "No tracking events yet — shipment has not been scanned by DHL.",
                })
            raise

        return self._normalise_tracking(tracking_number, raw)

    def track_shipment_raw(self, tracking_number):
        return self._get(f"/shipments/{tracking_number}/tracking")

    def _normalise_tracking(self, tracking_number, raw):
        if not isinstance(raw, dict):
            return self._empty_tracking(tracking_number, raw)

        shipments = raw.get("shipments") or []
        if isinstance(shipments, dict):
            shipments = [shipments]
        shipment = shipments[0] if shipments else {}

        status_block = shipment.get("status") or {}
        city, country = self._extract_location(status_block.get("location"))

        raw_code = (status_block.get("statusCode") or status_block.get("status") or "").strip()
        canonical = TRACKING_STATUS_MAP.get(raw_code.lower(), raw_code.lower() or "unknown")

        normalised_events = []
        for ev in shipment.get("events") or []:
            if not isinstance(ev, dict):
                continue
            ev_city, ev_country = self._extract_location(ev.get("location"))
            ev_code = (ev.get("statusCode") or ev.get("typeCode") or "").strip()
            normalised_events.append({
                "timestamp":      ev.get("timestamp") or ev.get("date"),
                "status_code":    ev_code,
                "status":         ev.get("status") or ev.get("typeCode") or ev_code,
                "description":    ev.get("description") or ev.get("remark") or "",
                "location":       ev_city,
                "country":        ev_country,
                "raw":            ev,
            })

        return {
            "tracking_number":    shipment.get("id") or tracking_number,
            "status":             canonical,
            "status_code":        raw_code or canonical,
            "description":        status_block.get("description") or status_block.get("status") or "",
            "location":           city,
            "country":            country,
            "estimated_delivery": shipment.get("estimatedTimeOfDelivery") or shipment.get("estimatedDelivery"),
            "events":             normalised_events,
            "raw":                raw,
        }

    @staticmethod
    def _extract_location(block):
        if not isinstance(block, dict):
            return "", ""
        addr = block.get("address") or {}
        city = (
            addr.get("addressLocality")
            or addr.get("cityName")
            or block.get("cityName")
            or ""
        )
        country = (
            addr.get("countryCode")
            or block.get("countryCode")
            or ""
        )
        return str(city).strip(), str(country).upper().strip()

    @staticmethod
    def _empty_tracking(tracking_number, raw=None):
        return {
            "tracking_number":    tracking_number,
            "status":             "unknown",
            "status_code":        "",
            "description":        "",
            "location":           "",
            "country":            "",
            "estimated_delivery": None,
            "events":             [],
            "raw":                raw or {},
        }

    # ==================================================================
    # 4. ELECTRONIC PROOF OF DELIVERY (ePOD)
    # ==================================================================
    def get_proof_of_delivery(self, tracking_number):
        return self._get(f"/shipments/{tracking_number}/proof-of-delivery")

    # ==================================================================
    # 5. CREATE PICKUP
    # ==================================================================
    def create_pickup(self, pickup_data):
        shipper_phone = os.getenv("DHL_ORIGIN_PHONE") or DEFAULT_PHONE_FALLBACK
        shipper_email = os.getenv("DHL_ORIGIN_EMAIL", "shipping@fabstrading.com")
        shipper_company = os.getenv("DHL_ORIGIN_COMPANY", "FABS Trading Global E-Commerce")
        shipper_contact = os.getenv("DHL_ORIGIN_CONTACT", "FABS Shipping")

        origin_country = normalize_country_code(
            os.getenv("DHL_ORIGIN_COUNTRY", "KE"), "DHL_ORIGIN_COUNTRY"
        )

        payload = {
            "plannedPickupDateAndTime": pickup_data.get(
                "planned_pickup_date", _dhl_now(hours_ahead=4)
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
                        "countryCode": origin_country,
                        "addressLine1": os.getenv("DHL_ORIGIN_ADDRESS", "FABS Trading Warehouse"),
                        "addressLine2": os.getenv("DHL_ORIGIN_ADDRESS2", ""),
                    },
                    "contactInformation": {
                        "email": shipper_email,
                        "phone": shipper_phone,
                        "companyName": shipper_company,
                        "fullName": shipper_contact,
                    },
                },
                "pickupDetails": {
                    "postalAddress": {
                        "postalCode": os.getenv("DHL_ORIGIN_POSTAL", "00100"),
                        "cityName": os.getenv("DHL_ORIGIN_CITY", "Nairobi"),
                        "countryCode": origin_country,
                        "addressLine1": os.getenv("DHL_ORIGIN_ADDRESS", "FABS Trading Warehouse"),
                    },
                    "contactInformation": {
                        "email": shipper_email,
                        "phone": shipper_phone,
                        "companyName": shipper_company,
                        "fullName": shipper_contact,
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
        cc = normalize_country_code(country_code, "country_code")

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
    # 8. LANDING COST
    # ==================================================================
    def estimate_landing_cost(
        self,
        origin_country, destination_country,
        weight_kg=1.0, length_cm=30, width_cm=20, height_cm=10,
        declared_value=100.0, currency="USD",
        is_customs_declarable=True,
    ):
        origin_country = normalize_country_code(origin_country, "origin country")
        destination_country = normalize_country_code(
            destination_country, "destination country"
        )
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
            "plannedShippingDateAndTime": _dhl_now(hours_ahead=2),
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
            params["countryCode"] = normalize_country_code(country_code, "country_code")
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
        return self._get(
            f"/shipments/{shipment_tracking_number}/documents",
            params={"typeCode": doc_type, "encodingFormat": "pdf"},
        )

    # ==================================================================
    # 12. COUNTRY REFERENCE LIST
    # ==================================================================
    def list_countries(self):
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
    # 13. SERVICE POINT FINDER
    # ==================================================================
    def find_service_points(self, country_code, city=None, postal_code=None, radius_km=10):
        params = {
            "countryCode": normalize_country_code(country_code, "country_code"),
            "radius": radius_km,
        }
        if city:
            params["city"] = city
        if postal_code:
            params["postalCode"] = postal_code
        return self._get("/servicepoints", params=params)