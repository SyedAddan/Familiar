import base64
import hashlib
import hmac
import secrets


PASSWORD_HASH_ITERATIONS = 600_000
PASSWORD_HASH_PREFIX = "pbkdf2_sha256"


def is_password_hash(stored_password: str) -> bool:
    return stored_password.startswith(f"{PASSWORD_HASH_PREFIX}$")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{PASSWORD_HASH_PREFIX}${PASSWORD_HASH_ITERATIONS}${encoded_salt}${encoded_digest}"


def verify_password(password: str, stored_password: str) -> bool:
    if not is_password_hash(stored_password):
        return hmac.compare_digest(password, stored_password)

    try:
        _, iterations, salt, expected = stored_password.split("$", 3)
        salt_bytes = base64.urlsafe_b64decode(salt + "=" * (-len(salt) % 4))
        expected_bytes = base64.urlsafe_b64decode(expected + "=" * (-len(expected) % 4))
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt_bytes, int(iterations)
        )
    except (ValueError, TypeError):
        return False

    return hmac.compare_digest(actual, expected_bytes)
