from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import math
import secrets
import uuid
import json

from config import (
    DATABASE_PATH,
    UPLOAD_FOLDER as CONFIG_UPLOAD_FOLDER,
    SERVICE_AREA_RADIUS_KM,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_UPLOAD_SIZE
)

from database import get_db

from utils import (
    generate_reference,
    current_time,
    clean_text,
    clean_optional_text,
    safe_int,
    safe_float
)


# =========================================================
# SHAHEBAZ MOTORS BACKEND
# app.py (UPDATED - SELL REQUEST PHOTOS + DELETE)
# =========================================================

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE * 4

CORS(
    app,
    supports_credentials=True
)


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE = DATABASE_PATH

UPLOAD_FOLDER = CONFIG_UPLOAD_FOLDER

SERVICE_RADIUS_KM = SERVICE_AREA_RADIUS_KM

SOLAPUR_LATITUDE = 17.6599
SOLAPUR_LONGITUDE = 75.9064

MAX_PHOTOS_PER_VEHICLE = 4
MAX_PHOTOS_PER_SELL_REQUEST = 4


# =========================================================
# ENSURE UPLOAD FOLDER EXISTS
# =========================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# ADMIN AUTHENTICATION
# =========================================================

ADMIN_USERNAME = os.getenv(
    "SHAHEBAZ_ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "SHAHEBAZ_ADMIN_PASSWORD",
    "admin123"
)

ADMIN_TOKENS = set()


def get_admin_token():
    authorization = request.headers.get(
        "Authorization",
        ""
    )

    if not authorization.startswith("Bearer "):
        return None

    return authorization[7:].strip()


def is_admin_authenticated():
    token = get_admin_token()

    return (
        token is not None
        and token in ADMIN_TOKENS
    )


def admin_required():
    if not is_admin_authenticated():
        return jsonify({
            "success": False,
            "message": "Admin authentication required."
        }), 401

    return None


# =========================================================
# HELPERS
# =========================================================

def row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def is_allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def save_uploaded_photo(file):
    if not file or not file.filename:
        return None

    if not is_allowed_file(file.filename):
        return None

    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_UPLOAD_SIZE:
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    filepath = os.path.join(UPLOAD_FOLDER, unique_name)

    file.save(filepath)

    return f"/uploads/{unique_name}"


def delete_photo_file(photo_url):
    if not photo_url:
        return

    filename = os.path.basename(photo_url)

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.isfile(filepath):
        try:
            os.remove(filepath)
        except OSError:
            pass


# ---------- VEHICLE PHOTOS ----------

def get_vehicle_photos(vehicle_id, db=None):
    close_db = False
    if db is None:
        db = get_db()
        close_db = True

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT id, photo_url, display_order
            FROM vehicle_photos
            WHERE vehicle_id = ?
            ORDER BY display_order ASC, id ASC
        """, (vehicle_id,))

        photos = [dict(row) for row in cursor.fetchall()]

        return photos

    finally:
        if close_db:
            db.close()


def attach_photos_to_vehicle(vehicle, db=None):
    if vehicle is None:
        return None

    vehicle["photos"] = get_vehicle_photos(vehicle["id"], db)

    if vehicle["photos"]:
        vehicle["image"] = vehicle["photos"][0]["photo_url"]
    else:
        vehicle["image"] = vehicle.get("image") or ""

    return vehicle


# ---------- SELL REQUEST PHOTOS ----------

def get_sell_request_photos(request_id, db=None):
    close_db = False
    if db is None:
        db = get_db()
        close_db = True

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT id, photo_url, display_order
            FROM sell_request_photos
            WHERE request_id = ?
            ORDER BY display_order ASC, id ASC
        """, (request_id,))

        photos = [dict(row) for row in cursor.fetchall()]

        return photos

    finally:
        if close_db:
            db.close()


def attach_photos_to_sell_request(sell_request, db=None):
    if sell_request is None:
        return None

    sell_request["photos"] = get_sell_request_photos(sell_request["id"], db)

    return sell_request


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    db = get_db()

    cursor = db.cursor()

    try:

        # ---------- VEHICLES ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_name TEXT NOT NULL,
                category TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                year INTEGER,
                fuel_type TEXT,
                transmission TEXT,
                seats INTEGER,
                mileage TEXT,
                engine TEXT,
                price REAL,
                rental_price REAL,
                description TEXT,
                image TEXT,
                status TEXT DEFAULT 'AVAILABLE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # ---------- VEHICLE PHOTOS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL,
                photo_url TEXT NOT NULL,
                display_order INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY(vehicle_id)
                    REFERENCES vehicles(id)
                    ON DELETE CASCADE
            )
        """)

        # ---------- ENQUIRIES ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                city TEXT,
                pincode TEXT,
                vehicle_id INTEGER,
                vehicle_name TEXT,
                vehicle_price REAL,
                enquiry_type TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'NEW',
                service_area_valid INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY(vehicle_id)
                    REFERENCES vehicles(id)
            )
        """)

        # ---------- SELL REQUESTS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sell_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE NOT NULL,
                seller_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                city TEXT,
                pincode TEXT,
                vehicle_type TEXT,
                vehicle_name TEXT,
                brand TEXT,
                model TEXT,
                year INTEGER,
                condition TEXT,
                expected_price REAL,
                description TEXT,
                photo_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'NEW',
                service_area_valid INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        # ---------- SELL REQUEST PHOTOS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sell_request_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                photo_url TEXT NOT NULL,
                display_order INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY(request_id)
                    REFERENCES sell_requests(id)
                    ON DELETE CASCADE
            )
        """)

        # ---------- RENTAL REQUESTS ----------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rental_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT UNIQUE NOT NULL,
                vehicle TEXT NOT NULL,
                rate REAL,
                pickup_date TEXT NOT NULL,
                return_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                city TEXT,
                message TEXT,
                status TEXT DEFAULT 'NEW',
                service_area_valid INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        db.commit()

    finally:
        db.close()


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance_km(latitude, longitude):

    earth_radius = 6371.0

    lat1 = math.radians(SOLAPUR_LATITUDE)
    lon1 = math.radians(SOLAPUR_LONGITUDE)

    lat2 = math.radians(float(latitude))
    lon2 = math.radians(float(longitude))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


def is_within_service_area(latitude, longitude):

    try:
        distance = calculate_distance_km(latitude, longitude)

        return (
            distance <= SERVICE_RADIUS_KM,
            round(distance, 2)
        )

    except (ValueError, TypeError):
        return (False, None)


# =========================================================
# STATIC FILE SERVING
# =========================================================

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# =========================================================
# FRONTEND FILE ROUTES
# =========================================================

@app.route("/", methods=["GET"])
def serve_home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>", methods=["GET"])
def serve_frontend(filename):

    file_path = os.path.join(BASE_DIR, filename)

    if os.path.isfile(file_path):
        return send_from_directory(BASE_DIR, filename)

    return jsonify({
        "success": False,
        "message": "Page not found."
    }), 404


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "message": "Shahebaz Motors backend is running.",
        "service": "Shahebaz Motors API",
        "database": os.path.basename(DATABASE)
    })


# =========================================================
# API HOME
# =========================================================

@app.route("/api", methods=["GET"])
def api_home():

    return jsonify({
        "success": True,
        "message": "Welcome to Shahebaz Motors API.",
        "version": "1.0.0",
        "endpoints": [
            "/api/health",
            "/api/admin/login",
            "/api/admin/logout",
            "/api/dashboard",
            "/api/vehicles",
            "/api/enquiries",
            "/api/sell-vehicle",
            "/api/rental-request",
            "/api/service-area"
        ]
    })


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True) or {}

    username = clean_text(data.get("username"))
    password = data.get("password", "")

    if (
        username != ADMIN_USERNAME
        or password != ADMIN_PASSWORD
    ):
        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    token = secrets.token_urlsafe(32)

    ADMIN_TOKENS.add(token)

    return jsonify({
        "success": True,
        "message": "Admin login successful.",
        "token": token
    })


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():

    token = get_admin_token()

    if token:
        ADMIN_TOKENS.discard(token)

    return jsonify({
        "success": True,
        "message": "Admin logged out successfully."
    })


# =========================================================
# SERVICE AREA
# =========================================================

@app.route("/api/service-area", methods=["POST"])
def service_area():

    data = request.get_json(silent=True) or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "success": False,
            "message": "Latitude and longitude are required."
        }), 400

    valid, distance = is_within_service_area(latitude, longitude)

    return jsonify({
        "success": True,
        "within_service_area": valid,
        "distance_km": distance,
        "service_radius_km": SERVICE_RADIUS_KM,
        "service_location": "Solapur, Maharashtra"
    })


# =========================================================
# GET VEHICLES
# =========================================================

@app.route("/api/vehicles", methods=["GET"])
def get_vehicles():

    db = get_db()

    try:
        category = request.args.get("category")
        status = request.args.get("status")

        query = "SELECT * FROM vehicles WHERE 1 = 1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY id DESC"

        cursor = db.cursor()
        cursor.execute(query, params)

        vehicles = [
            row_to_dict(row)
            for row in cursor.fetchall()
        ]

        for vehicle in vehicles:
            attach_photos_to_vehicle(vehicle, db)

        return jsonify({
            "success": True,
            "count": len(vehicles),
            "vehicles": vehicles
        })

    finally:
        db.close()


# =========================================================
# GET SINGLE VEHICLE
# =========================================================

@app.route("/api/vehicles/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id):

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT * FROM vehicles WHERE id = ?
        """, (vehicle_id,))

        vehicle = cursor.fetchone()

        if vehicle is None:
            return jsonify({
                "success": False,
                "message": "Vehicle not found."
            }), 404

        vehicle_dict = row_to_dict(vehicle)
        attach_photos_to_vehicle(vehicle_dict, db)

        return jsonify({
            "success": True,
            "vehicle": vehicle_dict
        })

    finally:
        db.close()


# =========================================================
# ADD VEHICLE
# =========================================================

@app.route("/api/vehicles", methods=["POST"])
def add_vehicle():

    auth_error = admin_required()
    if auth_error:
        return auth_error

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form.to_dict()
        files = request.files.getlist("photos")
    else:
        data = request.get_json(silent=True) or {}
        files = []

    vehicle_name = clean_text(data.get("vehicle_name"))
    category = clean_text(data.get("category"))

    if not vehicle_name:
        return jsonify({
            "success": False,
            "message": "Vehicle name is required."
        }), 400

    if not category:
        return jsonify({
            "success": False,
            "message": "Vehicle category is required."
        }), 400

    now = current_time()
    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO vehicles (
                vehicle_name, category, brand, model, year,
                fuel_type, transmission, seats, mileage, engine,
                price, rental_price, description, image, status,
                created_at, updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            vehicle_name,
            category,
            clean_optional_text(data.get("brand")),
            clean_optional_text(data.get("model")),
            safe_int(data.get("year")),
            clean_optional_text(data.get("fuel_type")),
            clean_optional_text(data.get("transmission")),
            safe_int(data.get("seats")),
            clean_optional_text(data.get("mileage")),
            clean_optional_text(data.get("engine")),
            safe_float(data.get("price")),
            safe_float(data.get("rental_price")),
            clean_optional_text(data.get("description")),
            None,
            clean_text(data.get("status", "AVAILABLE")).upper(),
            now,
            now
        ))

        vehicle_id = cursor.lastrowid

        saved_photos = []
        for index, file in enumerate(files):
            if index >= MAX_PHOTOS_PER_VEHICLE:
                break
            photo_url = save_uploaded_photo(file)
            if photo_url:
                saved_photos.append((photo_url, index + 1))

        for photo_url, order in saved_photos:
            cursor.execute("""
                INSERT INTO vehicle_photos (
                    vehicle_id, photo_url, display_order, created_at
                )
                VALUES (?, ?, ?, ?)
            """, (vehicle_id, photo_url, order, now))

        if saved_photos:
            cursor.execute("""
                UPDATE vehicles SET image = ? WHERE id = ?
            """, (saved_photos[0][0], vehicle_id))

        db.commit()

        cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
        vehicle = cursor.fetchone()
        vehicle_dict = row_to_dict(vehicle)
        attach_photos_to_vehicle(vehicle_dict, db)

        return jsonify({
            "success": True,
            "message": "Vehicle added successfully.",
            "vehicle": vehicle_dict
        }), 201

    finally:
        db.close()


# =========================================================
# UPDATE VEHICLE
# =========================================================

@app.route("/api/vehicles/<int:vehicle_id>", methods=["PUT"])
def update_vehicle(vehicle_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form.to_dict()
        files = request.files.getlist("photos")
    else:
        data = request.get_json(silent=True) or {}
        files = []

    allowed_fields = [
        "vehicle_name", "category", "brand", "model", "year",
        "fuel_type", "transmission", "seats", "mileage", "engine",
        "price", "rental_price", "description", "status"
    ]

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
        existing = cursor.fetchone()

        if existing is None:
            return jsonify({
                "success": False,
                "message": "Vehicle not found."
            }), 404

        updates = []
        values = []

        integer_fields = {"year", "seats"}
        float_fields = {"price", "rental_price"}

        for field in allowed_fields:
            if field not in data:
                continue

            updates.append(f"{field} = ?")

            if field in integer_fields:
                values.append(safe_int(data[field]))
            elif field in float_fields:
                values.append(safe_float(data[field]))
            elif field == "status":
                values.append(clean_text(data[field]).upper())
            else:
                values.append(clean_optional_text(data[field]))

        updates.append("updated_at = ?")
        values.append(current_time())
        values.append(vehicle_id)

        if len(updates) > 1:
            query = f"UPDATE vehicles SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)

        # ---------- PHOTO HANDLING ----------
        keep_photos_raw = data.get("keep_photos", None)
        keep_urls = []

        if keep_photos_raw:
            try:
                keep_urls = json.loads(keep_photos_raw)
            except Exception:
                keep_urls = []

        cursor.execute("""
            SELECT id, photo_url FROM vehicle_photos WHERE vehicle_id = ?
        """, (vehicle_id,))

        current_photos = [dict(row) for row in cursor.fetchall()]

        for photo in current_photos:
            if photo["photo_url"] not in keep_urls:
                delete_photo_file(photo["photo_url"])
                cursor.execute(
                    "DELETE FROM vehicle_photos WHERE id = ?",
                    (photo["id"],)
                )

        cursor.execute(
            "SELECT COUNT(*) FROM vehicle_photos WHERE vehicle_id = ?",
            (vehicle_id,)
        )
        current_count = cursor.fetchone()[0]

        for file in files:
            if current_count >= MAX_PHOTOS_PER_VEHICLE:
                break
            photo_url = save_uploaded_photo(file)
            if photo_url:
                current_count += 1
                cursor.execute("""
                    INSERT INTO vehicle_photos (
                        vehicle_id, photo_url, display_order, created_at
                    )
                    VALUES (?, ?, ?, ?)
                """, (vehicle_id, photo_url, current_count, current_time()))

        cursor.execute("""
            SELECT id FROM vehicle_photos
            WHERE vehicle_id = ?
            ORDER BY display_order ASC, id ASC
        """, (vehicle_id,))

        photo_ids = [row[0] for row in cursor.fetchall()]

        for idx, pid in enumerate(photo_ids):
            cursor.execute(
                "UPDATE vehicle_photos SET display_order = ? WHERE id = ?",
                (idx + 1, pid)
            )

        cursor.execute("""
            SELECT photo_url FROM vehicle_photos
            WHERE vehicle_id = ?
            ORDER BY display_order ASC, id ASC
            LIMIT 1
        """, (vehicle_id,))

        first_photo = cursor.fetchone()

        if first_photo:
            cursor.execute(
                "UPDATE vehicles SET image = ? WHERE id = ?",
                (first_photo[0], vehicle_id)
            )
        else:
            cursor.execute(
                "UPDATE vehicles SET image = NULL WHERE id = ?",
                (vehicle_id,)
            )

        db.commit()

        cursor.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))
        vehicle = cursor.fetchone()
        vehicle_dict = row_to_dict(vehicle)
        attach_photos_to_vehicle(vehicle_dict, db)

        return jsonify({
            "success": True,
            "message": "Vehicle updated successfully.",
            "vehicle": vehicle_dict
        })

    finally:
        db.close()


# =========================================================
# DELETE VEHICLE
# =========================================================

@app.route("/api/vehicles/<int:vehicle_id>", methods=["DELETE"])
def delete_vehicle(vehicle_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("SELECT id FROM vehicles WHERE id = ?", (vehicle_id,))
        vehicle = cursor.fetchone()

        if vehicle is None:
            return jsonify({
                "success": False,
                "message": "Vehicle not found."
            }), 404

        cursor.execute(
            "SELECT photo_url FROM vehicle_photos WHERE vehicle_id = ?",
            (vehicle_id,)
        )
        photos = cursor.fetchall()

        for photo in photos:
            delete_photo_file(photo[0])

        cursor.execute(
            "DELETE FROM vehicle_photos WHERE vehicle_id = ?",
            (vehicle_id,)
        )
        cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))

        db.commit()

        return jsonify({
            "success": True,
            "message": "Vehicle deleted successfully."
        })

    finally:
        db.close()


# =========================================================
# CREATE ENQUIRY
# =========================================================

@app.route("/api/enquiries", methods=["POST"])
def create_enquiry():

    data = request.get_json(silent=True) or {}

    customer_name = data.get("customer_name") or data.get("customerName")
    phone = data.get("phone")
    city = data.get("city")
    pincode = data.get("pincode")
    vehicle_id = data.get("vehicle_id")
    vehicle_name = data.get("vehicle_name") or data.get("vehicle")
    vehicle_price = data.get("vehicle_price")
    enquiry_type = data.get("enquiry_type", "PURCHASE")
    message = data.get("message")

    customer_name = clean_text(customer_name)
    phone = clean_text(phone)

    if not customer_name:
        return jsonify({
            "success": False,
            "message": "Customer name is required."
        }), 400

    if not phone:
        return jsonify({
            "success": False,
            "message": "Phone number is required."
        }), 400

    reference = generate_reference("ENQ")
    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO enquiries (
                reference, customer_name, phone, city, pincode,
                vehicle_id, vehicle_name, vehicle_price, enquiry_type,
                message, status, service_area_valid, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reference,
            customer_name,
            phone,
            clean_optional_text(city),
            clean_optional_text(pincode),
            safe_int(vehicle_id),
            clean_optional_text(vehicle_name),
            safe_float(vehicle_price),
            clean_text(enquiry_type).upper(),
            clean_optional_text(message),
            "NEW",
            1,
            current_time()
        ))

        db.commit()

        return jsonify({
            "success": True,
            "message": "Enquiry received successfully.",
            "reference": reference
        }), 201

    finally:
        db.close()


# =========================================================
# GET ENQUIRIES
# =========================================================

@app.route("/api/enquiries", methods=["GET"])
def get_enquiries():

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()
        status = request.args.get("status")

        if status:
            cursor.execute("""
                SELECT * FROM enquiries
                WHERE status = ?
                ORDER BY id DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT * FROM enquiries
                ORDER BY id DESC
            """)

        enquiries = [row_to_dict(row) for row in cursor.fetchall()]

        return jsonify({
            "success": True,
            "count": len(enquiries),
            "enquiries": enquiries
        })

    finally:
        db.close()


# =========================================================
# UPDATE ENQUIRY STATUS
# =========================================================

@app.route("/api/enquiries/<int:enquiry_id>", methods=["PUT"])
def update_enquiry(enquiry_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    status = clean_text(data.get("status")).upper()

    allowed_statuses = [
        "NEW", "CONTACTED", "FOLLOW_UP",
        "RESERVED", "COMPLETED", "CANCELLED"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid enquiry status."
        }), 400

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            "UPDATE enquiries SET status = ? WHERE id = ?",
            (status, enquiry_id)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Enquiry not found."
            }), 404

        db.commit()

        return jsonify({
            "success": True,
            "message": "Enquiry status updated."
        })

    finally:
        db.close()


# =========================================================
# CREATE SELL VEHICLE REQUEST (with photos)
# =========================================================

@app.route("/api/sell-vehicle", methods=["POST"])
def sell_vehicle():

    if request.content_type and "multipart/form-data" in request.content_type:
        data = request.form.to_dict()
        files = request.files.getlist("photos")
    else:
        data = request.get_json(silent=True) or {}
        files = []

    seller_name = (
        data.get("seller_name")
        or data.get("sellerName")
        or data.get("customerName")
    )
    phone = data.get("phone")

    seller_name = clean_text(seller_name)
    phone = clean_text(phone)

    if not seller_name:
        return jsonify({
            "success": False,
            "message": "Seller name is required."
        }), 400

    if not phone:
        return jsonify({
            "success": False,
            "message": "Phone number is required."
        }), 400

    reference = generate_reference("SELL")
    now = current_time()
    db = get_db()

    try:
        cursor = db.cursor()

        # Save photos first to count
        saved_photos = []
        for index, file in enumerate(files):
            if index >= MAX_PHOTOS_PER_SELL_REQUEST:
                break
            photo_url = save_uploaded_photo(file)
            if photo_url:
                saved_photos.append((photo_url, index + 1))

        cursor.execute("""
            INSERT INTO sell_requests (
                reference, seller_name, phone, email, city, pincode,
                vehicle_type, vehicle_name, brand, model, year,
                condition, expected_price, description, photo_count,
                status, service_area_valid, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reference,
            seller_name,
            phone,
            clean_optional_text(data.get("email")),
            clean_optional_text(data.get("city")),
            clean_optional_text(data.get("pincode")),
            clean_optional_text(data.get("vehicle_type")),
            clean_optional_text(data.get("vehicle_name")),
            clean_optional_text(data.get("brand")),
            clean_optional_text(data.get("model")),
            safe_int(data.get("year")),
            clean_optional_text(data.get("condition")),
            safe_float(data.get("expected_price")),
            clean_optional_text(data.get("description")),
            len(saved_photos),
            "NEW",
            1,
            now
        ))

        request_id = cursor.lastrowid

        # Insert photos
        for photo_url, order in saved_photos:
            cursor.execute("""
                INSERT INTO sell_request_photos (
                    request_id, photo_url, display_order, created_at
                )
                VALUES (?, ?, ?, ?)
            """, (request_id, photo_url, order, now))

        db.commit()

        return jsonify({
            "success": True,
            "message": "Vehicle selling request received.",
            "reference": reference
        }), 201

    finally:
        db.close()


# =========================================================
# GET SELL REQUESTS
# =========================================================

@app.route("/api/sell-vehicle", methods=["GET"])
def get_sell_requests():

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT * FROM sell_requests ORDER BY id DESC
        """)

        requests = [row_to_dict(row) for row in cursor.fetchall()]

        # Attach photos
        for req in requests:
            attach_photos_to_sell_request(req, db)

        return jsonify({
            "success": True,
            "count": len(requests),
            "requests": requests
        })

    finally:
        db.close()


# =========================================================
# GET SINGLE SELL REQUEST
# =========================================================

@app.route("/api/sell-vehicle/<int:request_id>", methods=["GET"])
def get_sell_request(request_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM sell_requests WHERE id = ?",
            (request_id,)
        )

        req = cursor.fetchone()

        if req is None:
            return jsonify({
                "success": False,
                "message": "Sell request not found."
            }), 404

        req_dict = row_to_dict(req)
        attach_photos_to_sell_request(req_dict, db)

        return jsonify({
            "success": True,
            "request": req_dict
        })

    finally:
        db.close()


# =========================================================
# UPDATE SELL REQUEST STATUS
# =========================================================

@app.route("/api/sell-vehicle/<int:request_id>", methods=["PUT"])
def update_sell_request(request_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    status = clean_text(data.get("status")).upper()

    allowed_statuses = ["NEW", "CONTACTED", "REVIEWED", "APPROVED", "REJECTED"]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid sell request status."
        }), 400

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            "UPDATE sell_requests SET status = ? WHERE id = ?",
            (status, request_id)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Sell request not found."
            }), 404

        db.commit()

        return jsonify({
            "success": True,
            "message": "Sell request status updated."
        })

    finally:
        db.close()


# =========================================================
# DELETE SELL REQUEST (NEW)
# =========================================================

@app.route("/api/sell-vehicle/<int:request_id>", methods=["DELETE"])
def delete_sell_request(request_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            "SELECT id FROM sell_requests WHERE id = ?",
            (request_id,)
        )

        req = cursor.fetchone()

        if req is None:
            return jsonify({
                "success": False,
                "message": "Sell request not found."
            }), 404

        # Delete photo files from disk
        cursor.execute(
            "SELECT photo_url FROM sell_request_photos WHERE request_id = ?",
            (request_id,)
        )

        photos = cursor.fetchall()

        for photo in photos:
            delete_photo_file(photo[0])

        # Delete from DB
        cursor.execute(
            "DELETE FROM sell_request_photos WHERE request_id = ?",
            (request_id,)
        )
        cursor.execute(
            "DELETE FROM sell_requests WHERE id = ?",
            (request_id,)
        )

        db.commit()

        return jsonify({
            "success": True,
            "message": "Sell request deleted successfully."
        })

    finally:
        db.close()


# =========================================================
# CREATE RENTAL REQUEST
# =========================================================

@app.route("/api/rental-request", methods=["POST"])
def rental_request():

    data = request.get_json(silent=True) or {}

    vehicle = clean_text(data.get("vehicle"))
    pickup_date = data.get("pickupDate") or data.get("pickup_date")
    return_date = data.get("returnDate") or data.get("return_date")
    customer_name = data.get("customerName") or data.get("customer_name")
    phone = clean_text(data.get("phone"))

    customer_name = clean_text(customer_name)

    if not vehicle:
        return jsonify({
            "success": False,
            "message": "Vehicle is required."
        }), 400

    if not pickup_date:
        return jsonify({
            "success": False,
            "message": "Pickup date is required."
        }), 400

    if not return_date:
        return jsonify({
            "success": False,
            "message": "Return date is required."
        }), 400

    if not customer_name:
        return jsonify({
            "success": False,
            "message": "Customer name is required."
        }), 400

    if not phone:
        return jsonify({
            "success": False,
            "message": "Phone number is required."
        }), 400

    if str(return_date) < str(pickup_date):
        return jsonify({
            "success": False,
            "message": "Return date cannot be before pickup date."
        }), 400

    reference = generate_reference("REN")
    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO rental_requests (
                reference, vehicle, rate, pickup_date, return_date,
                customer_name, phone, city, message, status,
                service_area_valid, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reference,
            vehicle,
            safe_float(data.get("rate")),
            str(pickup_date),
            str(return_date),
            customer_name,
            phone,
            clean_optional_text(data.get("city")),
            clean_optional_text(data.get("message")),
            "NEW",
            1,
            current_time()
        ))

        db.commit()

        return jsonify({
            "success": True,
            "message": "Rental request received.",
            "reference": reference
        }), 201

    finally:
        db.close()


# =========================================================
# GET RENTAL REQUESTS
# =========================================================

@app.route("/api/rental-request", methods=["GET"])
def get_rental_requests():

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("""
            SELECT * FROM rental_requests ORDER BY id DESC
        """)

        requests = [row_to_dict(row) for row in cursor.fetchall()]

        return jsonify({
            "success": True,
            "count": len(requests),
            "requests": requests
        })

    finally:
        db.close()


# =========================================================
# UPDATE RENTAL REQUEST
# =========================================================

@app.route("/api/rental-request/<int:request_id>", methods=["PUT"])
def update_rental_request(request_id):

    auth_error = admin_required()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}
    status = clean_text(data.get("status")).upper()

    allowed_statuses = [
        "NEW", "CONTACTED", "CONFIRMED",
        "ACTIVE", "COMPLETED", "CANCELLED"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid rental status."
        }), 400

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            "UPDATE rental_requests SET status = ? WHERE id = ?",
            (status, request_id)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "success": False,
                "message": "Rental request not found."
            }), 404

        db.commit()

        return jsonify({
            "success": True,
            "message": "Rental request status updated."
        })

    finally:
        db.close()


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    auth_error = admin_required()
    if auth_error:
        return auth_error

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total_vehicles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'AVAILABLE'")
        available_vehicles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'SOLD'")
        sold_vehicles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'RENTAL'")
        rental_vehicles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM enquiries WHERE status = 'NEW'")
        new_enquiries = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sell_requests WHERE status = 'NEW'")
        new_sell_requests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM rental_requests WHERE status = 'NEW'")
        new_rental_requests = cursor.fetchone()[0]

        return jsonify({
            "success": True,
            "dashboard": {
                "total_vehicles": total_vehicles,
                "available_vehicles": available_vehicles,
                "sold_vehicles": sold_vehicles,
                "rental_vehicles": rental_vehicles,
                "new_enquiries": new_enquiries,
                "new_sell_requests": new_sell_requests,
                "new_rental_requests": new_rental_requests
            }
        })

    finally:
        db.close()


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "API endpoint not found."
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "message": "HTTP method not allowed."
    }), 405


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        "success": False,
        "message": "File too large. Maximum 8MB per photo."
    }), 413


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "Internal server error."
    }), 500


# =========================================================
# START SERVER
# =========================================================

initialize_database()


if __name__ == "__main__":

    print()
    print("==========================================")
    print("       SHAHEBAZ MOTORS BACKEND")
    print("==========================================")
    print("Server: http://127.0.0.1:5000")
    print("Health: http://127.0.0.1:5000/api/health")
    print("Database: shahebaz_motors.db")
    print("Uploads: ./uploads/")
    print("Admin Login: /api/admin/login")
    print("==========================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )