<<<<<<< HEAD
"""PSP routing by currency, method, and region."""
=======
"""
AFM PSP Router — Currency & Region Based Routing
Includes MTN MoMo and Orange Money for African corridors
"""

from decimal import Decimal
>>>>>>> origin_afm/main

from config.config import get_settings
from config.exceptions import PaymentError, CurrencyNotSupportedError
from payment_hub.models import PSPType

settings = get_settings()


class PSPRouter:
<<<<<<< HEAD
    CURRENCY_PSP_MAP = {
        "XOF": [PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
        "XAF": [PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
        "NGN": [PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
        "KES": [PSPType.KORA, PSPType.FINCRA],
        "GHS": [PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
=======
    """
    Routes payments to the appropriate PSP based on:
    - Currency (XOF, XAF, NGN, KES, GHS, ZAR, USD, EUR, GBP)
    - Payment method (mobile_money, card, bank_transfer)
    - Region (west_africa, east_africa, south_africa, international)
    """

    # Currency → supported PSPs (including mobile money operators)
    CURRENCY_PSP_MAP = {
        "XOF": [PSPType.MTN_MOMO, PSPType.ORANGE_MONEY, PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
        "XAF": [PSPType.MTN_MOMO, PSPType.ORANGE_MONEY, PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
        "NGN": [PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
        "KES": [PSPType.MTN_MOMO, PSPType.KORA, PSPType.FINCRA],
        "GHS": [PSPType.MTN_MOMO, PSPType.KORA, PSPType.FINCRA, PSPType.FLUTTERWAVE],
>>>>>>> origin_afm/main
        "ZAR": [PSPType.FINCRA, PSPType.STRIPE],
        "USD": [PSPType.FINCRA, PSPType.STRIPE],
        "EUR": [PSPType.FINCRA, PSPType.STRIPE],
        "GBP": [PSPType.FINCRA, PSPType.STRIPE],
    }

<<<<<<< HEAD
    REGION_PSP_PRIORITY = {
        "west_africa": [PSPType.KORA, PSPType.FLUTTERWAVE, PSPType.FINCRA],
        "east_africa": [PSPType.KORA, PSPType.FINCRA],
        "south_africa": [PSPType.FINCRA, PSPType.STRIPE],
=======
    METHOD_PSP_MAP = {
        "mobile_money": [PSPType.MTN_MOMO, PSPType.ORANGE_MONEY, PSPType.KORA, PSPType.FLUTTERWAVE],
        "card": [PSPType.FLUTTERWAVE, PSPType.STRIPE, PSPType.FINCRA],
        "bank_transfer": [PSPType.KORA, PSPType.FINCRA, PSPType.STRIPE],
        "ussd": [PSPType.KORA, PSPType.FLUTTERWAVE],
    }

    REGION_PSP_PRIORITY = {
        "west_africa": [PSPType.MTN_MOMO, PSPType.ORANGE_MONEY, PSPType.KORA, PSPType.FLUTTERWAVE, PSPType.FINCRA],
        "east_africa": [PSPType.MTN_MOMO, PSPType.KORA, PSPType.FINCRA],
        "south_africa": [PSPType.FINCRA, PSPType.STRIPE],
        "central_africa": [PSPType.MTN_MOMO, PSPType.ORANGE_MONEY, PSPType.KORA],
>>>>>>> origin_afm/main
        "international": [PSPType.STRIPE, PSPType.FINCRA],
    }

    @classmethod
<<<<<<< HEAD
    def select_psp(cls, currency: str, method: str | None = None, region: str = "west_africa", amount: str | None = None) -> PSPType:
        currency = currency.upper()
=======
    def select_psp(
        cls,
        currency: str,
        method: str = "mobile_money",
        region: str = "west_africa",
        amount: Decimal | None = None,
    ) -> PSPType:
        currency = currency.upper()
        method = method.lower()

>>>>>>> origin_afm/main
        if currency not in cls.CURRENCY_PSP_MAP:
            raise CurrencyNotSupportedError(f"Currency {currency} not supported")

        available = cls.CURRENCY_PSP_MAP[currency]
<<<<<<< HEAD
        priority = cls.REGION_PSP_PRIORITY.get(region, cls.REGION_PSP_PRIORITY["international"])

        candidates = [psp for psp in priority if psp in available]

        if not candidates:
            raise PaymentError(f"No PSP available for {currency} in {region}")

=======

        if method in cls.METHOD_PSP_MAP:
            method_psps = cls.METHOD_PSP_MAP[method]
            available = [psp for psp in available if psp in method_psps]

        priority = cls.REGION_PSP_PRIORITY.get(region, cls.REGION_PSP_PRIORITY["international"])
        candidates = [psp for psp in priority if psp in available]

        if not candidates:
            raise PaymentError(f"No PSP available for {currency} in {region} with method {method}")

        # 🔴 FIX: In development, skip credential check — simulation mode
        settings = get_settings()
        if settings.is_development:
            return candidates[0]  # Return first candidate without credential check

        # Production: Check API key availability
>>>>>>> origin_afm/main
        for psp in candidates:
            if cls._has_credentials(psp):
                return psp

        raise PaymentError(f"No PSP with valid credentials for {currency}")

    @classmethod
    def _has_credentials(cls, psp: PSPType) -> bool:
        settings = get_settings()
        cred_map = {
            PSPType.KORA: settings.kora_api_key and settings.kora_secret_key,
            PSPType.FINCRA: settings.fincra_api_key and settings.fincra_secret_key,
            PSPType.FLUTTERWAVE: settings.flutterwave_public_key and settings.flutterwave_secret_key,
            PSPType.STRIPE: settings.stripe_publishable_key and settings.stripe_secret_key,
<<<<<<< HEAD
=======
            # 🔴 FIX: MTN MoMo / Orange Money are routed through Kora or
            # Flutterwave (see payment_service._call_psp_api). The old
            # check only looked at *public* keys (kora_api_key /
            # flutterwave_public_key), which don't determine whether the
            # actual API call can authenticate — that requires the
            # matching *secret* key. Mismatched checks let a transaction
            # look "routable" while the real call had no usable
            # credentials and fell back to a simulated success.
            PSPType.MTN_MOMO: bool(settings.kora_secret_key) or bool(settings.flutterwave_secret_key),
            PSPType.ORANGE_MONEY: bool(settings.kora_secret_key) or bool(settings.flutterwave_secret_key),
>>>>>>> origin_afm/main
        }
        return bool(cred_map.get(psp))


psp_router = PSPRouter()
