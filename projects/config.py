import os
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# SHAHEBAZ MOTORS CONFIGURATION
# config.py (UPDATED - PASSWORD REMOVED)
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "shahebaz_motors.db"
)


# =========================================================
# FLASK SERVER
# =========================================================

HOST = "0.0.0.0"

PORT = 5000

DEBUG = False


# =========================================================
# ADMIN
# =========================================================
# NOTE: ADMIN_PASSWORD hata diya — sirf database se login hoga

ADMIN_USERNAME = os.getenv(
    "SHAHEBAZ_ADMIN_USERNAME",
    "adminn"
)

ADMIN_EMAIL = os.getenv(
    "SHAHEBAZ_ADMIN_EMAIL",
    ""
)

ADMIN_SESSION_TIMEOUT = 3600


# =========================================================
# EMAIL SETTINGS (Brevo SMTP)
# =========================================================

BREVO_SMTP_SERVER = os.getenv(
    "BREVO_SMTP_SERVER",
    "smtp-relay.brevo.com"
)

BREVO_SMTP_PORT = int(
    os.getenv("BREVO_SMTP_PORT", "587")
)

BREVO_SMTP_LOGIN = os.getenv(
    "BREVO_SMTP_LOGIN",
    ""
)

BREVO_SMTP_PASSWORD = os.getenv(
    "BREVO_SMTP_PASSWORD",
    ""
)


# =========================================================
# FILE UPLOADS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif"
}

MAX_UPLOAD_SIZE = 8 * 1024 * 1024


# =========================================================
# SERVICE AREA
# =========================================================

SERVICE_AREA_RADIUS_KM = 100

SERVICE_LATITUDE = 17.6599

SERVICE_LONGITUDE = 75.9064


# =========================================================
# APPLICATION
# =========================================================

APP_NAME = "Shahebaz Motors"

APP_VERSION = "1.0.0"


# =========================================================
# PASSWORD RESET
# =========================================================

RESET_TOKEN_EXPIRY_MINUTES = 15