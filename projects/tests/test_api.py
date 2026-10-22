# =========================================================
# SHAHEBAZ MOTORS - API ENDPOINT TESTS
# tests/test_api.py
# =========================================================

import os
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["FLASK_ENV"] = "testing"
os.environ["FLASK_DEBUG"] = "False"

from app import app


# =========================================================
# PYTEST FIXTURES
# =========================================================

@pytest.fixture
def client():
    """Create a test client."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def admin_token(client):
    """Get admin authentication token."""
    response = client.post("/api/admin/login", json={
        "username": "adminn",
        "password": "Shahebaz@Motors2026!"
    })
    data = response.get_json()
    if data and data.get("success"):
        return data.get("token")
    return None


# =========================================================
# TEST: API INDEX
# =========================================================

def test_api_index(client):
    """Test /api endpoint returns welcome message."""
    response = client.get("/api")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)
    assert len(data["endpoints"]) > 0


# =========================================================
# TEST: HEALTH ENDPOINT
# =========================================================

def test_health_check(client):
    """Test health endpoint details."""
    response = client.get("/api/health")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert data["service"] == "Shahebaz Motors API"
    assert "database" in data


# =========================================================
# TEST: VEHICLES - GET (Public)
# =========================================================

def test_get_all_vehicles(client):
    """Test getting all vehicles."""
    response = client.get("/api/vehicles")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "vehicles" in data
    assert "count" in data
    assert isinstance(data["vehicles"], list)
    assert data["count"] == len(data["vehicles"])


def test_get_vehicles_with_photos_array(client):
    """Test that vehicles include photos array."""
    response = client.get("/api/vehicles")
    data = response.get_json()
    
    for vehicle in data["vehicles"]:
        assert "photos" in vehicle
        assert isinstance(vehicle["photos"], list)


def test_vehicles_2wheeler_filter(client):
    """Test 2WHEELER category filter."""
    response = client.get("/api/vehicles?category=2WHEELER")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    
    # Verify all vehicles are 2WHEELER
    for vehicle in data["vehicles"]:
        assert vehicle["category"] == "2WHEELER"


def test_vehicles_4wheeler_filter(client):
    """Test 4WHEELER category filter."""
    response = client.get("/api/vehicles?category=4WHEELER")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    
    for vehicle in data["vehicles"]:
        assert vehicle["category"] == "4WHEELER"


def test_vehicles_available_filter(client):
    """Test AVAILABLE status filter."""
    response = client.get("/api/vehicles?status=AVAILABLE")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True


def test_vehicles_sold_filter(client):
    """Test SOLD status filter."""
    response = client.get("/api/vehicles?status=SOLD")
    assert response.status_code == 200


def test_vehicle_detail_endpoint(client):
    """Test getting single vehicle detail."""
    # First get all vehicles
    list_response = client.get("/api/vehicles")
    list_data = list_response.get_json()
    
    if list_data["count"] > 0:
        vehicle_id = list_data["vehicles"][0]["id"]
        
        response = client.get(f"/api/vehicles/{vehicle_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        assert "vehicle" in data
        assert data["vehicle"]["id"] == vehicle_id


# =========================================================
# TEST: VEHICLES - POST (Admin Only)
# =========================================================

def test_add_vehicle_requires_auth(client):
    """Test adding vehicle requires admin authentication."""
    response = client.post("/api/vehicles", json={
        "vehicle_name": "Test Vehicle",
        "category": "2WHEELER"
    })
    
    assert response.status_code == 401


def test_add_vehicle_with_auth(client, admin_token):
    """Test adding vehicle with valid admin token."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.post(
        "/api/vehicles",
        json={
            "vehicle_name": "Test Vehicle Pytest",
            "category": "2WHEELER",
            "brand": "Test",
            "model": "TestModel",
            "year": 2020,
            "price": 50000,
            "status": "AVAILABLE"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["success"] is True
    assert "vehicle" in data


def test_add_vehicle_missing_name(client, admin_token):
    """Test adding vehicle without name."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.post(
        "/api/vehicles",
        json={"category": "2WHEELER"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400


def test_add_vehicle_missing_category(client, admin_token):
    """Test adding vehicle without category."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.post(
        "/api/vehicles",
        json={"vehicle_name": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400


# =========================================================
# TEST: ENQUIRIES - POST
# =========================================================

def test_enquiry_valid_data(client):
    """Test enquiry with valid data."""
    response = client.post("/api/enquiries", json={
        "customer_name": "API Test User",
        "phone": "9876543210",
        "city": "Solapur",
        "vehicle_name": "Test Bike",
        "vehicle_price": 50000,
        "enquiry_type": "PURCHASE",
        "message": "API test message"
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["success"] is True
    assert "reference" in data
    assert data["reference"].startswith("ENQ-")


def test_enquiry_without_name(client):
    """Test enquiry without customer name."""
    response = client.post("/api/enquiries", json={
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


def test_enquiry_without_phone(client):
    """Test enquiry without phone."""
    response = client.post("/api/enquiries", json={
        "customer_name": "Test User"
    })
    
    assert response.status_code == 400


def test_enquiry_reference_is_unique(client):
    """Test enquiry references are unique."""
    refs = []
    
    for i in range(3):
        response = client.post("/api/enquiries", json={
            "customer_name": f"Test User {i}",
            "phone": "9876543210"
        })
        data = response.get_json()
        refs.append(data["reference"])
    
    # All references should be unique
    assert len(refs) == len(set(refs))


# =========================================================
# TEST: ENQUIRIES - GET (Admin Only)
# =========================================================

def test_get_enquiries_requires_auth(client):
    """Test listing enquiries requires auth."""
    response = client.get("/api/enquiries")
    assert response.status_code == 401


def test_get_enquiries_with_auth(client, admin_token):
    """Test listing enquiries with auth."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.get(
        "/api/enquiries",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "enquiries" in data
    assert "count" in data


def test_update_enquiry_status(client, admin_token):
    """Test updating enquiry status."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    # Create an enquiry
    create_response = client.post("/api/enquiries", json={
        "customer_name": "Status Test",
        "phone": "9876543210"
    })
    
    # Get enquiries to find the ID
    list_response = client.get(
        "/api/enquiries",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    enquiries = list_response.get_json()["enquiries"]
    
    if len(enquiries) > 0:
        enquiry_id = enquiries[0]["id"]
        
        # Update status
        update_response = client.put(
            f"/api/enquiries/{enquiry_id}",
            json={"status": "CONTACTED"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert update_response.status_code == 200
        assert update_response.get_json()["success"] is True


def test_update_enquiry_invalid_status(client, admin_token):
    """Test updating enquiry with invalid status."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.put(
        "/api/enquiries/1",
        json={"status": "INVALID_STATUS_XYZ"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 400


# =========================================================
# TEST: SELL VEHICLE - POST
# =========================================================

def test_sell_vehicle_valid(client):
    """Test valid sell vehicle request."""
    response = client.post("/api/sell-vehicle", json={
        "seller_name": "Test Seller",
        "phone": "9876543210",
        "city": "Solapur",
        "vehicle_type": "Two Wheeler",
        "brand": "Honda",
        "model": "Activa",
        "year": 2020,
        "condition": "Good",
        "expected_price": 50000
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data["success"] is True
    assert data["reference"].startswith("SELL-")


def test_sell_vehicle_without_name(client):
    """Test sell without seller name."""
    response = client.post("/api/sell-vehicle", json={
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


def test_sell_vehicle_without_phone(client):
    """Test sell without phone."""
    response = client.post("/api/sell-vehicle", json={
        "seller_name": "Test Seller"
    })
    
    assert response.status_code == 400


# =========================================================
# TEST: SELL VEHICLE - GET (Admin Only)
# =========================================================

def test_get_sell_requests_requires_auth(client):
    """Test sell requests list requires auth."""
    response = client.get("/api/sell-vehicle")
    assert response.status_code == 401


def test_get_sell_requests_with_auth(client, admin_token):
    """Test sell requests list with auth."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.get(
        "/api/sell-vehicle",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "requests" in data


# =========================================================
# TEST: RENTAL REQUEST - POST
# =========================================================

def test_rental_request_valid(client):
    """Test valid rental request."""
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


def test_rental_without_vehicle(client):
    """Test rental without vehicle."""
    response = client.post("/api/rental-request", json={
        "pickupDate": "2026-11-01",
        "returnDate": "2026-11-05",
        "customerName": "Test",
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


def test_rental_without_dates(client):
    """Test rental without dates."""
    response = client.post("/api/rental-request", json={
        "vehicle": "Honda Activa",
        "customerName": "Test",
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


def test_rental_return_before_pickup(client):
    """Test rental with return before pickup."""
    response = client.post("/api/rental-request", json={
        "vehicle": "Honda Activa",
        "pickupDate": "2026-11-05",
        "returnDate": "2026-11-01",
        "customerName": "Test",
        "phone": "9876543210"
    })
    
    assert response.status_code == 400


# =========================================================
# TEST: RENTAL - GET (Admin Only)
# =========================================================

def test_get_rentals_requires_auth(client):
    """Test rentals list requires auth."""
    response = client.get("/api/rental-request")
    assert response.status_code == 401


def test_get_rentals_with_auth(client, admin_token):
    """Test rentals list with auth."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.get(
        "/api/rental-request",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "requests" in data


# =========================================================
# TEST: ADMIN LOGIN
# =========================================================

def test_admin_login_success(client):
    """Test valid admin login."""
    response = client.post("/api/admin/login", json={
        "username": "adminn",
        "password": "Shahebaz@Motors2026!"
    })
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data
    assert len(data["token"]) > 20


def test_admin_login_invalid_password(client):
    """Test admin login with invalid password."""
    response = client.post("/api/admin/login", json={
        "username": "adminn",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_admin_login_invalid_username(client):
    """Test admin login with invalid username."""
    response = client.post("/api/admin/login", json={
        "username": "not_admin",
        "password": "Shahebaz@Motors2026!"
    })
    
    assert response.status_code == 401


def test_admin_logout(client, admin_token):
    """Test admin logout."""
    if not admin_token:
        pytest.skip("Admin login failed")
    
    response = client.post(
        "/api/admin/logout",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    assert response.get_json()["success"] is True


# =========================================================
# TEST: INVALID TOKEN
# =========================================================

def test_invalid_token_rejected(client):
    """Test invalid token is rejected."""
    response = client.get(
        "/api/enquiries",
        headers={"Authorization": "Bearer fake_token_xyz"}
    )
    
    assert response.status_code == 401


def test_missing_token_rejected(client):
    """Test missing token is rejected."""
    response = client.get("/api/enquiries")
    assert response.status_code == 401


# =========================================================
# TEST: ERROR RESPONSES
# =========================================================

def test_404_on_wrong_endpoint(client):
    """Test 404 for wrong API endpoint."""
    response = client.get("/api/wrong-endpoint-xyz")
    assert response.status_code == 404


def test_405_on_wrong_method(client):
    """Test method not allowed."""
    response = client.delete("/api/health")
    assert response.status_code == 405


# =========================================================
# TEST: RESPONSE FORMAT
# =========================================================

def test_all_api_responses_are_json(client):
    """Test all API responses are JSON."""
    endpoints = [
        "/api/health",
        "/api/vehicles",
        "/api/dashboard"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.content_type.startswith("application/json")


def test_api_response_has_success_field(client):
    """Test API responses have success field."""
    response = client.get("/api/health")
    data = response.get_json()
    assert "success" in data


# =========================================================
# TEST: SEARCH & FILTER
# =========================================================

def test_vehicles_search_by_category_2w(client):
    """Test 2-wheeler category search."""
    response = client.get("/api/vehicles?category=2WHEELER")
    data = response.get_json()
    
    for vehicle in data["vehicles"]:
        assert vehicle["category"] == "2WHEELER"


def test_vehicles_search_by_category_3w(client):
    """Test 3-wheeler category search."""
    response = client.get("/api/vehicles?category=3WHEELER")
    assert response.status_code == 200


def test_combined_category_and_status_filter(client):
    """Test combined category and status filter."""
    response = client.get("/api/vehicles?category=2WHEELER&status=AVAILABLE")
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["success"] is True