import uuid
import re
from datetime import datetime


# =========================================================
# SHAHEBAZ MOTORS - UTILITY FUNCTIONS
# utils.py (UPDATED - FULL)
# =========================================================


def generate_reference(prefix):
    """
    Generate a unique reference number.

    Example:
    ENQ-12AB345
    REN-ABC1234
    SELL-89XYZ12
    """

    random_part = (
        uuid.uuid4()
        .hex[:7]
        .upper()
    )

    return f"{prefix}-{random_part}"


def current_time():
    """
    Return current date and time
    in ISO format.
    """

    return datetime.now().isoformat(
        timespec="seconds"
    )


def clean_text(value):
    """
    Safely clean user-provided text.
    Returns an empty string if value is None.
    """

    if value is None:
        return ""

    return str(value).strip()


def clean_optional_text(value):
    """
    Clean optional text fields.
    Return None when empty.
    """

    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def safe_int(value, default=None):
    """
    Safely convert a value to integer.
    Returns default when conversion fails.
    """

    try:

        if value is None or value == "":
            return default

        return int(value)

    except (
        TypeError,
        ValueError
    ):

        return default


def safe_float(value, default=None):
    """
    Safely convert a value to float.
    Returns default when conversion fails.
    """

    try:

        if value is None or value == "":
            return default

        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return default


def is_valid_phone(value):
    """
    Check if a phone number is a valid
    10-digit Indian mobile number.

    Valid:
        9876543210
        8888888888

    Invalid:
        1234567890
        98765
        abcdefghij
    """

    if not value:
        return False

    pattern = r"^[6-9]\d{9}$"

    return bool(
        re.match(
            pattern,
            str(value).strip()
        )
    )


def is_valid_email(value):
    """
    Basic email format validation.
    Returns True if format looks correct.
    """

    if not value:
        return False

    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

    return bool(
        re.match(
            pattern,
            str(value).strip()
        )
    )


def is_valid_pincode(value):
    """
    Check if a pincode is a valid
    6-digit Indian pincode.
    """

    if not value:
        return False

    pattern = r"^\d{6}$"

    return bool(
        re.match(
            pattern,
            str(value).strip()
        )
    )


def truncate_text(value, max_length=255):
    """
    Truncate long text to a maximum length.
    Useful to avoid database overflow.
    """

    if value is None:
        return None

    value = str(value).strip()

    if len(value) <= max_length:
        return value

    return value[:max_length]