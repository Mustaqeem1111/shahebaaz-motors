import os


# =========================================================
# SHAHEBAZ MOTORS CONFIGURATION
# config.py (UPDATED - PHOTO UPLOAD SUPPORT)
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

DEBUG = True


# =========================================================
# ADMIN
# =========================================================

ADMIN_USERNAME = os.getenv(
    "SHAHEBAZ_ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "SHAHEBAZ_ADMIN_PASSWORD",
    "admin123"
)

ADMIN_SESSION_TIMEOUT = 3600


# =========================================================
# FILE UPLOADS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

# Allowed image extensions (lowercase, without dot)

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif"
}

# Maximum upload size per photo: 8 MB

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