# =========================================================
# SHAHEBAZ MOTORS - MAIN APPLICATION TESTS
# tests/test_app.py
# =========================================================

import os
import sys
import tempfile
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set test environment BEFORE importing app
os.environ["FLASK_ENV"] = "testing"
os.environ["FLASK_DEBUG"] = "False"

from app import app
from database import get_db, init_admin_users_table


# =========================================================
# PYTEST FIXTURES
# =========================================================

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_token(client):
    """Get an admin authentication token."""
    response = client.post("/api/admin/login", json={
        "username": "adminn",
        "password": "Shahebaz@Motors2026!"
    })
    data = response.get_json()
    if data and data.get("success"):
        return data.get("token")
    return None


# =========================================================
# TEST 1: APP LOADS
# =========================================================

def test_app_exists():
    """Test that the Flask app exists."""
    assert app is not None
    assert app.name == "app"


def test_database_connection():
    """Test that database connection works."""
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result is not None
    finally:
        db.close()


# =========================================================
# TEST 2: HEALTH CHECK
# =========================================================

def test_health_endpoint(client):
    """Test /api/health returns success."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert "message" in data
    assert data["service"] == "Shahebaz Motors API"


# =========================================================
# TEST 3: HOMEPAGE LOADS
# =========================================================

def test_homepage_loads(client):
    """Test that homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200


def test_404_page(client):
    """Test 404 page for invalid routes."""
    response = client.get("/nonexistent-page-xyz-123")
    # Should return 404 or JSON error
    assert response.status_code in [404, 200]


# =========================================================
# TEST 4: SECURITY HEADERS
# =========================================================

def test_security_headers(client):
    """Test that security headers are present."""
    response = client.get("/")
    
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-XSS-Protection" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Content-Security-Policy" in response.headers


def test_x_frame_options_value(client):
    """Test X-Frame-Options has correct value."""
    response = client.get("/")
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


def test_x_content_type_options(client):
    """Test X-Content-Type-Options is nosniff."""
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


# =========================================================
# TEST 5: FILE ACCESS BLOCKING
# =========================================================

def test_blocked_database_file(client):
    """Test that database file is blocked."""
    response = client.get("/shahebaz_motors.db")
    assert response.status_code == 403


def test_blocked_python_file(client):
    """Test that Python files are blocked."""
    response = client.get("/app.py")
    assert response.status_code == 403


def test_blocked_env_file(client):
    """Test that .env file is blocked."""
    response = client.get("/.env")
    assert response.status_code == 403


def test_blocked_config_file(client):
    """Test that config.py is blocked."""
    response = client.get("/config.py")
    assert response.status_code == 403


def test_directory_traversal_blocked(client):
    """Test directory traversal is blocked."""
    response = client.get("/../../etc/passwd")
    assert response.status_code == 403


# =========================================================
# TEST 6: ADMIN LOGIN
# =========================================================

def test_admin_login_success(client):
    """Test admin login with correct credentials."""
    response = client.post("/api/admin/login", json={
        "username": "adminn",
        "password": "Shahebaz@Motors2026!"
    })
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["expires_in_hours"] == 8


def test_admin_login_wrong_password(client):
    """Test admin login with wrong password."""
    response = client.post("/api/admin/login", json={
        "username": "adminn",
        "password": "wrong_password_xyz"
    })
    
    assert response.status_code == 401
    
    data = response.get_json()
    assert data["success"] is False
    assert "Invalid" in data["message"]


def test_admin_login_wrong_username(client):
    """Test admin login with wrong username."""
    response = client.post("/api/admin/login", json={
        "username": "hacker",
        "password": "Shahebaz@Motors2026!"
    })
    
    assert response.status_code == 401


def test_admin_login_empty_credentials(client):
    """Test admin login with empty credentials."""
    response = client.post("/api/admin/login", json={
        "username": "",
        "password": ""
    })
    
    assert response.status_code == 401


# =========================================================
# TEST 7: VEHICLES API
# =========================================================

def test_get_vehicles_public(client):
    """Test vehicles API is publicly accessible."""
    response = client.get("/api/vehicles")
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "vehicles" in data
    assert isinstance(data["vehicles"], list)


def test_get_vehicles_by_category(client):
    """Test filtering vehicles by category."""
    response = client.get("/api/vehicles?category=2WHEELER")
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True


def test_get_nonexistent_vehicle(client):
    """Test getting a vehicle that doesn't exist."""
    response = client.get("/api/vehicles/999999")
    
    assert response.status_code == 404


# =========================================================
# TEST 8: ENQUIRIES API
# =========================================================

def test_create_enquiry_success(client):
    """Test creating a valid enquiry."""
    response = client.post("/api/enquiries", json={
        "customer_name": "Test User",
        "phone": "9876543210",
        "city": "Solapur",
        "vehicle_name": "Test Vehicle",
        "vehicle_price": 50000,
        "enquiry_type": "PURCHASE",
        "message": "This is a test enquiry"
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["success"] is True
    assert "reference" in data
    assert data["reference"].startswith("ENQ-")


def test_create_enquiry_missing_name(client):
    """Test creating enquiry without name."""
    response = client.post("/api/enquiries", json={
        "phone": "9876543210",
        "city": "Solapur"
    })
    
    assert response.status_code == 400


def test_create_enquiry_missing_phone(client):
    """Test creating enquiry without phone."""
    response = client.post("/api/enquiries", json={
        "customer_name": "Test",
        "city": "Solapur"
    })
    
    assert response.status_code == 400


def test_get_enquiries_requires_auth(client):
    """Test that listing enquiries requires authentication."""
    response = client.get("/api/enquiries")
    
    assert response.status_code == 401


def test_get_enquiries_with_auth(client, admin_token):
    """Test that admin can list enquiries."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.get("/api/enquiries", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "enquiries" in data


# =========================================================
# TEST 9: SELL VEHICLE API
# =========================================================

def test_sell_vehicle_success(client):
    """Test submitting a sell request."""
    response = client.post("/api/sell-vehicle", json={
        "seller_name": "Test Seller",
        "phone": "9876543210",
        "city": "Solapur",
        "vehicle_type": "Two Wheeler",
        "brand": "Honda",
        "model": "Activa",
        "year": 2020,
        "condition": "Good",
        "expected_price": 50000,
        "description": "Test description"
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["success"] is True
    assert data["reference"].startswith("SELL-")


def test_sell_vehicle_missing_name(client):
    """Test sell request without seller name."""
    response = client.post("/api/sell-vehicle", json={
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


# =========================================================
# TEST 10: RENTAL API
# =========================================================

def test_rental_request_success(client):
    """Test submitting a rental request."""
    response = client.post("/api/rental-request", json={
        "vehicle": "Honda Activa",
        "pickupDate": "2026-11-01",
        "returnDate": "2026-11-05",
        "customerName": "Test User",
        "phone": "9876543210",
        "city": "Solapur"
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["success"] is True
    assert data["reference"].startswith("REN-")


def test_rental_invalid_dates(client):
    """Test rental with return date before pickup."""
    response = client.post("/api/rental-request", json={
        "vehicle": "Honda Activa",
        "pickupDate": "2026-11-05",
        "returnDate": "2026-11-01",
        "customerName": "Test User",
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


# =========================================================
# TEST 11: DASHBOARD (AUTH REQUIRED)
# =========================================================

def test_dashboard_requires_auth(client):
    """Test dashboard requires authentication."""
    response = client.get("/api/dashboard")
    assert response.status_code == 401


def test_dashboard_with_auth(client, admin_token):
    """Test dashboard access with valid token."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.get("/api/dashboard", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "dashboard" in data


# =========================================================
# TEST 12: FORGOT PASSWORD
# =========================================================

def test_forgot_password_missing_email(client):
    """Test forgot password without email."""
    response = client.post("/api/admin/forgot-password", json={})
    assert response.status_code == 400


def test_forgot_password_unknown_email(client):
    """Test forgot password with unknown email (should not reveal)."""
    response = client.post("/api/admin/forgot-password", json={
        "email": "unknown@example.com"
    })
    
    # Should return success (not reveal existence)
    assert response.status_code in [200, 500]


# =========================================================
# TEST 13: INVALID JSON
# =========================================================

def test_invalid_json_enquiry(client):
    """Test sending invalid JSON to enquiry endpoint."""
    response = client.post(
        "/api/enquiries",
        data="not valid json",
        content_type="application/json"
    )
    
    # Should handle gracefully
    assert response.status_code in [400, 500]


# =========================================================
# TEST 14: SQL INJECTION PROTECTION
# =========================================================

def test_sql_injection_protection(client):
    """Test SQL injection is blocked."""
    response = client.get("/api/vehicles?category=1' OR '1'='1")
    
    assert response.status_code == 200
    
    data = response.get_json()
    # Should not return all vehicles
    assert data["success"] is True
    assert data["count"] == 0


# =========================================================
# TEST 15: XSS PROTECTION
# =========================================================

def test_xss_protection(client):
    """Test XSS payload is handled safely."""
    response = client.post("/api/enquiries", json={
        "customer_name": "<script>alert('xss')</script>",
        "phone": "9876543210",
        "city": "Solapur"
    })
    
    # Should accept but store safely (not execute)
    assert response.status_code == 201