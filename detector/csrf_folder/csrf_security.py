import hmac
import hashlib
from secrets import token_hex
from django.conf import settings


class CSRFSecurity:

    @staticmethod
    def generate_csrf_token():
        random_token = token_hex(32)

        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            random_token.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{random_token}.{signature}"

    @staticmethod
    def verify_csrf_token(token: str):
        if not token:
            return False

        try:
            random_token, signature = token.split(".")
        except ValueError:
            return False

        expected_signature = hmac.new(
            settings.SECRET_KEY.encode(),
            random_token.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)