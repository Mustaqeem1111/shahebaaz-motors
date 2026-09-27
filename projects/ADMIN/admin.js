/* =========================================================
   SHAHEBAZ MOTORS
   ADMIN.JS (UPDATED - SELL REQUEST PHOTOS + DELETE)
   AUTH + DASHBOARD + VEHICLES + ENQUIRIES MANAGEMENT
========================================================= */

const API_BASE = "/api";
const ADMIN_TOKEN_KEY = "shahebaz_admin_token";

/* =========================================================
   AUTHENTICATION HELPERS
========================================================= */

function getAdminToken() {
    return localStorage.getItem(ADMIN_TOKEN_KEY) || "";
}

function setAdminToken(token) {
    if (token) {
        localStorage.setItem(ADMIN_TOKEN_KEY, token);
    }
}

function clearAdminToken() {
    localStorage.removeItem(ADMIN_TOKEN_KEY);
}

function isAdminLoggedIn() {
    return !!getAdminToken();
}

async function apiRequest(url, options = {}) {
    const token = getAdminToken();
    const headers = {
        ...(options.headers || {})
    };

    // Only set JSON content-type if not FormData
    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    const data = await response.json().catch(() => ({}));

    if (response.status === 401) {
        clearAdminToken();
        if (!window.location.pathname.endsWith("login.html")) {
            window.location.href = "login.html";
        }
        throw new Error(data.message || "Admin authentication required.");
    }

    if (!response.ok) {
        throw new Error(data.message || `Request failed (${response.status})`);
    }

    return data;
}

async function adminLogin(username, password) {
    const result = await apiRequest(`${API_BASE}/admin/login`, {
        method: "POST",
        body: JSON.stringify({ username, password })
    });

    if (!result.success || !result.token) {
        throw new Error(result.message || "Login failed.");
    }

    setAdminToken(result.token);
    return result;
}

async function adminLogout() {
    try {
        if (getAdminToken()) {
            await fetch(`${API_BASE}/admin/logout`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${getAdminToken()}`
                }
            });
        }
    } catch (error) {
        console.error("Logout error:", error);
    }

    clearAdminToken();
    window.location.href = "login.html";
}

function protectAdminPage() {
    if (!isAdminLoggedIn()) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

/* =========================================================
   DASHBOARD
========================================================= */

async function loadDashboard() {
    try {
        const result = await apiRequest(`${API_BASE}/dashboard`);

        if (!result.success) {
            throw new Error(result.message || "Unable to load dashboard.");
        }

        const dashboard = result.dashboard || {};

        setText("totalVehicles", dashboard.total_vehicles ?? 0);
        setText("availableVehicles", dashboard.available_vehicles ?? 0);
        setText("soldVehicles", dashboard.sold_vehicles ?? 0);
        setText("rentalVehicles", dashboard.rental_vehicles ?? 0);
        setText("newEnquiries", dashboard.new_enquiries ?? 0);
        setText("newSellRequests", dashboard.new_sell_requests ?? 0);
        setText("newRentalRequests", dashboard.new_rental_requests ?? 0);

        setText("inventoryAvailable", dashboard.available_vehicles ?? 0);
        setText("inventorySold", dashboard.sold_vehicles ?? 0);
        setText("inventoryRental", dashboard.rental_vehicles ?? 0);

        await loadRecentEnquiries();

    } catch (error) {
        console.error("Dashboard error:", error);
        showDashboardError();
    }
}

async function loadRecentEnquiries() {
    const table = document.getElementById("recentEnquiries");
    if (!table) return;

    table.innerHTML = `
        <tr>
            <td colspan="6" class="table-loading">Loading enquiries...</td>
        </tr>
    `;

    try {
        const result = await apiRequest(`${API_BASE}/enquiries`);
        const enquiries = Array.isArray(result.enquiries) ? result.enquiries : [];

        if (!enquiries.length) {
            table.innerHTML = `
                <tr>
                    <td colspan="6" class="table-loading">No enquiries yet.</td>
                </tr>
            `;
            return;
        }

        const recent = enquiries.slice(0, 10);
        table.innerHTML = recent.map(enquiry => {
            const reference = enquiry.reference || "—";
            const customer = enquiry.customer_name || "—";
            const vehicle = enquiry.vehicle_name || "—";
            const city = enquiry.city || "—";
            const status = String(enquiry.status || "NEW").toUpperCase();
            const date = formatDate(enquiry.created_at);
            const statusClass = status.toLowerCase();

            return `
                <tr>
                    <td><strong>${escapeHtml(reference)}</strong></td>
                    <td>${escapeHtml(customer)}</td>
                    <td>${escapeHtml(vehicle)}</td>
                    <td>${escapeHtml(city)}</td>
                    <td><span class="status-badge status-${statusClass}">${escapeHtml(formatEnquiryStatus(status))}</span></td>
                    <td>${escapeHtml(date)}</td>
                </tr>
            `;
        }).join("");

    } catch (error) {
        table.innerHTML = `
            <tr>
                <td colspan="6" class="table-loading">Unable to load enquiries.</td>
            </tr>
        `;
    }
}

function showDashboardError() {
    ["totalVehicles", "availableVehicles", "soldVehicles", "newEnquiries"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = "—";
    });
}

/* =========================================================
   ENQUIRIES MANAGEMENT
========================================================= */

let allEnquiries = [];

async function initializeEnquiriesPage() {
    const table = document.getElementById("enquiriesTable");
    if (!table) return;

    await loadEnquiries();

    document.getElementById("searchEnquiries")?.addEventListener("input", renderEnquiries);
    document.getElementById("statusFilter")?.addEventListener("change", renderEnquiries);
    document.getElementById("refreshEnquiries")?.addEventListener("click", loadEnquiries);

    document.getElementById("closeEnquiryModal")?.addEventListener("click", closeEnquiryModal);
    document.getElementById("modalCloseButton")?.addEventListener("click", closeEnquiryModal);
    document.querySelector("#enquiryModal .admin-modal-overlay")?.addEventListener("click", closeEnquiryModal);
}

async function loadEnquiries() {
    const table = document.getElementById("enquiriesTable");
    if (table) {
        table.innerHTML = `<tr><td colspan="10" class="table-loading">Loading enquiries...</td></tr>`;
    }

    try {
        const result = await apiRequest(`${API_BASE}/enquiries`);
        allEnquiries = Array.isArray(result.enquiries) ? result.enquiries : [];

        setText("totalEnquiries", allEnquiries.length);
        setText("newCount", allEnquiries.filter(e => String(e.status || "").toUpperCase() === "NEW").length);
        setText("contactedCount", allEnquiries.filter(e => String(e.status || "").toUpperCase() === "CONTACTED").length);
        setText("closedCount", allEnquiries.filter(e => ["COMPLETED", "CANCELLED"].includes(String(e.status || "").toUpperCase())).length);

        renderEnquiries();
    } catch (error) {
        if (table) {
            table.innerHTML = `<tr><td colspan="10" class="table-loading">Failed to load enquiries.</td></tr>`;
        }
    }
}

function renderEnquiries() {
    const table = document.getElementById("enquiriesTable");
    if (!table) return;

    const search = (document.getElementById("searchEnquiries")?.value || "").toLowerCase().trim();
    const filter = (document.getElementById("statusFilter")?.value || "ALL").toUpperCase();

    const filtered = allEnquiries.filter(item => {
        const searchStr = `${item.reference || ""} ${item.customer_name || ""} ${item.phone || ""} ${item.vehicle_name || ""} ${item.city || ""}`.toLowerCase();
        const matchesSearch = !search || searchStr.includes(search);
        const matchesStatus = filter === "ALL" || String(item.status || "").toUpperCase() === filter;
        return matchesSearch && matchesStatus;
    });

    if (!filtered.length) {
        table.innerHTML = `<tr><td colspan="10" class="table-loading">No enquiries found.</td></tr>`;
        return;
    }

    table.innerHTML = filtered.map(item => {
        const status = String(item.status || "NEW").toUpperCase();
        const statusClass = status.toLowerCase();

        return `
            <tr>
                <td><strong>${escapeHtml(item.reference || "—")}</strong></td>
                <td>${escapeHtml(item.customer_name || "—")}</td>
                <td>${escapeHtml(item.phone || "—")}</td>
                <td>${escapeHtml(item.city || "—")}</td>
                <td>${escapeHtml(item.vehicle_name || "—")}</td>
                <td>${formatPrice(item.vehicle_price)}</td>
                <td>${escapeHtml(item.enquiry_type || "PURCHASE")}</td>
                <td><span class="status-badge status-${statusClass}">${escapeHtml(formatEnquiryStatus(status))}</span></td>
                <td>${formatDate(item.created_at)}</td>
                <td>
                    <button type="button" class="admin-button secondary" onclick="viewEnquiry(${item.id})">View</button>
                </td>
            </tr>
        `;
    }).join("");
}

window.viewEnquiry = function(id) {
    const item = allEnquiries.find(e => Number(e.id) === Number(id));
    if (!item) return;

    const modalRef = document.getElementById("modalReference");
    const details = document.getElementById("enquiryDetails");
    const modal = document.getElementById("enquiryModal");

    if (modalRef) modalRef.textContent = item.reference || "Enquiry";
    if (details) {
        const currentStatus = String(item.status || "").toUpperCase();
        const statusOptions = ["NEW", "CONTACTED", "FOLLOW_UP", "RESERVED", "COMPLETED", "CANCELLED"];

        details.innerHTML = `
            <div class="detail-row"><span>Customer:</span><strong>${escapeHtml(item.customer_name || "—")}</strong></div>
            <div class="detail-row"><span>Phone:</span><strong>${escapeHtml(item.phone || "—")}</strong></div>
            <div class="detail-row"><span>City:</span><strong>${escapeHtml(item.city || "—")}</strong></div>
            <div class="detail-row"><span>Vehicle:</span><strong>${escapeHtml(item.vehicle_name || "—")}</strong></div>
            <div class="detail-row"><span>Price:</span><strong>${formatPrice(item.vehicle_price)}</strong></div>
            <div class="detail-message"><span>Message:</span><p>${escapeHtml(item.message || "No message provided.")}</p></div>
            <div class="detail-status" style="margin-top: 15px;">
                <label>Update Status:</label>
                <select id="updateEnquiryStatusSelect" class="admin-select" style="margin: 8px 0; width: 100%;">
                    ${statusOptions.map(st => `
                        <option value="${st}" ${currentStatus === st ? "selected" : ""}>${formatEnquiryStatus(st)}</option>
                    `).join("")}
                </select>
                <button type="button" class="admin-button" style="width: 100%;" onclick="submitEnquiryStatusUpdate(${item.id})">Update Status</button>
            </div>
        `;
    }

    if (modal) {
        modal.classList.add("active");
        modal.setAttribute("aria-hidden", "false");
    }
};

window.submitEnquiryStatusUpdate = async function(id) {
    const select = document.getElementById("updateEnquiryStatusSelect");
    if (!select) return;

    try {
        await apiRequest(`${API_BASE}/enquiries/${id}`, {
            method: "PUT",
            body: JSON.stringify({ status: select.value })
        });
        closeEnquiryModal();
        await loadEnquiries();
    } catch (error) {
        alert(error.message || "Failed to update status.");
    }
};

function closeEnquiryModal() {
    const modal = document.getElementById("enquiryModal");
    if (modal) {
        modal.classList.remove("active");
        modal.setAttribute("aria-hidden", "true");
    }
}

/* =========================================================
   VEHICLES MANAGEMENT
========================================================= */

let allVehicles = [];
let editingVehicleId = null;
let selectedPhotoFiles = [];
let existingPhotos = [];

function $(id) {
    return document.getElementById(id);
}

async function loadVehicles() {
    const table = $("vehiclesTable");
    if (table) {
        table.innerHTML = `<tr><td colspan="9" class="table-loading">Loading vehicles...</td></tr>`;
    }

    try {
        const data = await apiRequest(`${API_BASE}/vehicles`);
        allVehicles = Array.isArray(data.vehicles) ? data.vehicles : [];
        updateStatistics();
        applyFilters();
    } catch (error) {
        if (table) {
            table.innerHTML = `<tr><td colspan="9" class="table-loading">Failed to load vehicles.</td></tr>`;
        }
    }
}

function updateStatistics() {
    setText("totalVehicles", allVehicles.length);
    setText("availableVehicles", allVehicles.filter(v => String(v.status || "").toUpperCase() === "AVAILABLE").length);
    setText("soldVehicles", allVehicles.filter(v => String(v.status || "").toUpperCase() === "SOLD").length);
    setText("rentalVehicles", allVehicles.filter(v => String(v.status || "").toUpperCase() === "RENTAL").length);
}

function applyFilters() {
    const search = $("vehicleSearch")?.value.trim().toLowerCase() || "";
    const category = $("categoryFilter")?.value || "";
    const status = $("vehicleStatusFilter")?.value || "";

    const filteredVehicles = allVehicles.filter(vehicle => {
        const name = String(vehicle.vehicle_name || "").toLowerCase();
        const brand = String(vehicle.brand || "").toLowerCase();
        const model = String(vehicle.model || "").toLowerCase();
        const vCat = String(vehicle.category || "").toUpperCase();
        const vStatus = String(vehicle.status || "").toUpperCase();

        const searchMatch = !search || name.includes(search) || brand.includes(search) || model.includes(search);
        const categoryMatch = !category || vCat === category.toUpperCase();
        const statusMatch = !status || vStatus === status.toUpperCase();

        return searchMatch && categoryMatch && statusMatch;
    });

    renderVehicles(filteredVehicles);
}

function getVehiclePrimaryPhoto(vehicle) {
    if (Array.isArray(vehicle.photos) && vehicle.photos.length > 0) {
        return vehicle.photos[0].photo_url;
    }
    return vehicle.image || "";
}

function renderVehicles(vehicles) {
    const table = $("vehiclesTable");
    if (!table) return;

    if (!vehicles.length) {
        table.innerHTML = `<tr><td colspan="9" class="table-loading">No vehicles found.</td></tr>`;
        return;
    }

    table.innerHTML = vehicles.map(vehicle => {
        const id = vehicle.id ?? "";
        const name = vehicle.vehicle_name || "Unnamed Vehicle";
        const category = formatCategory(vehicle.category);
        const brand = vehicle.brand || "—";
        const model = vehicle.model || "—";
        const year = vehicle.year || "—";
        const price = formatPrice(vehicle.price);
        const status = String(vehicle.status || "AVAILABLE").toUpperCase();
        const photo = getVehiclePrimaryPhoto(vehicle);

        const photoCell = photo
            ? `<img src="${escapeHtml(photo)}" alt="Vehicle" class="vehicle-thumb">`
            : `<div class="vehicle-thumb-placeholder">📷</div>`;

        return `
            <tr>
                <td>${photoCell}</td>
                <td><strong>${escapeHtml(name)}</strong></td>
                <td>${escapeHtml(category)}</td>
                <td>${escapeHtml(brand)} / ${escapeHtml(model)}</td>
                <td>${escapeHtml(String(year))}</td>
                <td>${escapeHtml(price)}</td>
                <td><span class="status-badge status-${status.toLowerCase()}">${escapeHtml(formatStatus(status))}</span></td>
                <td>
                    <button type="button" class="admin-button secondary vehicle-edit-button" data-id="${id}">Edit</button>
                    <button type="button" class="admin-button danger vehicle-delete-button" data-id="${id}">Delete</button>
                </td>
            </tr>
        `;
    }).join("");
}

function openAddVehicleModal() {
    editingVehicleId = null;
    selectedPhotoFiles = [];
    existingPhotos = [];

    const modal = $("vehicleModal");
    const form = $("vehicleForm");

    if (!modal || !form) return;

    form.reset();
    setText("vehicleModalTitle", "Add Vehicle");
    if ($("vehicleId")) $("vehicleId").value = "";
    if ($("saveVehicle")) $("saveVehicle").textContent = "Save Vehicle";
    clearFormError();
    renderPhotoPreview();

    modal.setAttribute("aria-hidden", "false");
    modal.classList.add("active");
}

async function openEditVehicleModal(vehicleId) {
    try {
        const data = await apiRequest(`${API_BASE}/vehicles/${vehicleId}`);
        if (!data.success || !data.vehicle) {
            throw new Error(data.message || "Vehicle not found.");
        }

        const vehicle = data.vehicle;
        editingVehicleId = vehicle.id;
        selectedPhotoFiles = [];
        existingPhotos = Array.isArray(vehicle.photos) ? vehicle.photos.slice() : [];

        setValue("vehicleId", vehicle.id);
        setValue("vehicleName", vehicle.vehicle_name);
        setValue("category", vehicle.category);
        setValue("brand", vehicle.brand);
        setValue("model", vehicle.model);
        setValue("year", vehicle.year);
        setValue("fuelType", vehicle.fuel_type);
        setValue("transmission", vehicle.transmission);
        setValue("seats", vehicle.seats);
        setValue("mileage", vehicle.mileage);
        setValue("engine", vehicle.engine);
        setValue("price", vehicle.price);
        setValue("rentalPrice", vehicle.rental_price);
        setValue("status", vehicle.status || "AVAILABLE");
        setValue("description", vehicle.description);

        setText("vehicleModalTitle", "Edit Vehicle");
        if ($("saveVehicle")) $("saveVehicle").textContent = "Update Vehicle";
        clearFormError();
        renderPhotoPreview();

        const modal = $("vehicleModal");
        if (modal) {
            modal.setAttribute("aria-hidden", "false");
            modal.classList.add("active");
        }
    } catch (error) {
        alert(error.message || "Unable to load vehicle.");
    }
}

function closeVehicleModal() {
    const modal = $("vehicleModal");
    if (!modal) return;
    modal.setAttribute("aria-hidden", "true");
    modal.classList.remove("active");
    editingVehicleId = null;
    selectedPhotoFiles = [];
    existingPhotos = [];
    clearFormError();
}

function setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value ?? "";
}

function clearFormError() {
    const el = $("vehicleFormError");
    if (el) el.textContent = "";
}

function showFormError(msg) {
    const el = $("vehicleFormError");
    if (el) el.textContent = msg;
}

function getVehicleFormData() {
    return {
        vehicle_name: $("vehicleName")?.value.trim() || "",
        category: $("category")?.value || "",
        brand: $("brand")?.value.trim() || "",
        model: $("model")?.value.trim() || "",
        year: $("year")?.value ? Number($("year").value) : null,
        fuel_type: $("fuelType")?.value || "",
        transmission: $("transmission")?.value || "",
        seats: $("seats")?.value ? Number($("seats").value) : null,
        mileage: $("mileage")?.value.trim() || "",
        engine: $("engine")?.value.trim() || "",
        price: $("price")?.value ? Number($("price").value) : null,
        rental_price: $("rentalPrice")?.value ? Number($("rentalPrice").value) : null,
        status: $("status")?.value || "AVAILABLE",
        description: $("description")?.value.trim() || ""
    };
}

/* =========================================================
   PHOTO HANDLING (VEHICLES)
========================================================= */

function initializePhotoUpload() {
    const photoInput = $("vehiclePhotos");
    if (!photoInput) return;

    photoInput.addEventListener("change", () => {
        const newFiles = Array.from(photoInput.files);

        const totalCount = existingPhotos.length + selectedPhotoFiles.length + newFiles.length;
        if (totalCount > 4) {
            alert("Maximum 4 photos allowed per vehicle.");
            photoInput.value = "";
            return;
        }

        for (const file of newFiles) {
            if (file.size > 8 * 1024 * 1024) {
                alert(`File "${file.name}" is larger than 8MB. Please select a smaller file.`);
                photoInput.value = "";
                return;
            }
        }

        selectedPhotoFiles = [...selectedPhotoFiles, ...newFiles];
        photoInput.value = "";
        renderPhotoPreview();
    });
}

function renderPhotoPreview() {
    const preview = $("photoPreviewGrid");
    if (!preview) return;

    preview.innerHTML = "";

    existingPhotos.forEach((photo, index) => {
        const wrapper = document.createElement("div");
        wrapper.className = "photo-preview-item";

        const img = document.createElement("img");
        img.src = photo.photo_url || photo;
        img.alt = "Vehicle photo";

        const badge = document.createElement("span");
        badge.className = "photo-preview-badge";
        badge.textContent = index === 0 ? "MAIN" : `#${index + 1}`;

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "photo-preview-remove";
        removeBtn.innerHTML = "×";
        removeBtn.title = "Remove this photo";

        removeBtn.addEventListener("click", () => {
            existingPhotos.splice(index, 1);
            renderPhotoPreview();
        });

        wrapper.appendChild(img);
        wrapper.appendChild(badge);
        wrapper.appendChild(removeBtn);
        preview.appendChild(wrapper);
    });

    selectedPhotoFiles.forEach((file, index) => {
        if (!file.type.startsWith("image/")) return;

        const reader = new FileReader();

        reader.onload = event => {
            const wrapper = document.createElement("div");
            wrapper.className = "photo-preview-item";

            const img = document.createElement("img");
            img.src = event.target.result;
            img.alt = "New photo";

            const totalIndex = existingPhotos.length + index;
            const badge = document.createElement("span");
            badge.className = "photo-preview-badge";
            badge.textContent = totalIndex === 0 ? "MAIN" : `#${totalIndex + 1}`;

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "photo-preview-remove";
            removeBtn.innerHTML = "×";
            removeBtn.title = "Remove this photo";

            removeBtn.addEventListener("click", () => {
                selectedPhotoFiles.splice(index, 1);
                renderPhotoPreview();
            });

            wrapper.appendChild(img);
            wrapper.appendChild(badge);
            wrapper.appendChild(removeBtn);
            preview.appendChild(wrapper);
        };

        reader.readAsDataURL(file);
    });
}

/* =========================================================
   SAVE VEHICLE
========================================================= */

async function saveVehicle(event) {
    event.preventDefault();
    clearFormError();

    const data = getVehicleFormData();
    if (!data.vehicle_name || !data.category) {
        showFormError("Vehicle name and category are required.");
        return;
    }

    const button = $("saveVehicle");
    if (button) {
        button.disabled = true;
        button.textContent = editingVehicleId ? "Updating..." : "Saving...";
    }

    try {
        const formData = new FormData();

        Object.keys(data).forEach(key => {
            const value = data[key];
            if (value !== null && value !== undefined) {
                formData.append(key, value);
            }
        });

        selectedPhotoFiles.forEach(file => {
            formData.append("photos", file);
        });

        if (editingVehicleId && existingPhotos.length > 0) {
            const keepUrls = existingPhotos.map(p => p.photo_url || p);
            formData.append("keep_photos", JSON.stringify(keepUrls));
        } else if (editingVehicleId) {
            formData.append("keep_photos", JSON.stringify([]));
        }

        if (editingVehicleId) {
            await apiRequest(`${API_BASE}/vehicles/${editingVehicleId}`, {
                method: "PUT",
                body: formData
            });
        } else {
            await apiRequest(`${API_BASE}/vehicles`, {
                method: "POST",
                body: formData
            });
        }

        closeVehicleModal();
        await loadVehicles();
        if ($("recentEnquiries")) await loadDashboard();

    } catch (error) {
        showFormError(error.message || "Unable to save vehicle.");
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = editingVehicleId ? "Update Vehicle" : "Save Vehicle";
        }
    }
}

async function deleteVehicle(vehicleId) {
    if (!confirm("Are you sure you want to delete this vehicle?\n\nThis will also delete all photos permanently.")) return;

    try {
        await apiRequest(`${API_BASE}/vehicles/${vehicleId}`, { method: "DELETE" });
        await loadVehicles();
        if ($("recentEnquiries")) await loadDashboard();
    } catch (error) {
        alert(error.message || "Unable to delete vehicle.");
    }
}

/* =========================================================
   LOGIN PAGE
========================================================= */

function initializeLoginPage() {
    const form = document.getElementById("adminLoginForm");
    if (!form) return;

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const username = document.getElementById("adminUsername")?.value.trim() || "";
        const password = document.getElementById("adminPassword")?.value || "";
        const button = document.getElementById("loginButton");
        const error = document.getElementById("loginError");

        if (error) {
            error.textContent = "";
            error.style.display = "none";
        }

        if (!username || !password) {
            if (error) {
                error.textContent = "Please enter your username and password.";
                error.style.display = "block";
            }
            return;
        }

        if (button) {
            button.disabled = true;
            button.textContent = "Signing in...";
        }

        try {
            await adminLogin(username, password);
            window.location.href = "dashboard.html";
        } catch (err) {
            if (error) {
                error.textContent = err.message || "Unable to login.";
                error.style.display = "block";
            }
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = "Login to Admin Panel";
            }
        }
    });
}

/* =========================================================
   FORMATTERS & HELPERS
========================================================= */

function formatCategory(category) {
    switch (String(category || "").toUpperCase()) {
        case "2WHEELER": return "2 Wheeler";
        case "3WHEELER": return "3 Wheeler";
        case "4WHEELER": return "4 Wheeler";
        default: return category || "—";
    }
}

function formatStatus(status) {
    switch (String(status || "").toUpperCase()) {
        case "AVAILABLE": return "Available";
        case "SOLD": return "Sold";
        case "RENTAL": return "Rental";
        case "INACTIVE": return "Inactive";
        default: return status || "—";
    }
}

function formatEnquiryStatus(status) {
    switch (String(status || "").toUpperCase()) {
        case "NEW": return "New";
        case "CONTACTED": return "Contacted";
        case "FOLLOW_UP": return "Follow Up";
        case "RESERVED": return "Reserved";
        case "COMPLETED": return "Completed";
        case "CANCELLED": return "Cancelled";
        default: return status || "—";
    }
}

function formatPrice(price) {
    if (price === null || price === undefined || price === "") return "—";
    const number = Number(price);
    return Number.isNaN(number) ? String(price) : "₹" + number.toLocaleString("en-IN");
}

function formatDate(value) {
    if (!value) return "—";
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return String(value);

    const day = String(date.getDate()).padStart(2, "0");
    const month = date.toLocaleDateString("en-IN", { month: "short" });
    const year = date.getFullYear();

    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    return `${day} ${month} ${year}, ${hours}:${minutes}`;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? 0;
}

/* =========================================================
   INIT
========================================================= */

function initializeAdmin() {
    initializeLoginPage();

    const isLoginPage = window.location.pathname.toLowerCase().endsWith("login.html");

    if (!isLoginPage) {
        if (!protectAdminPage()) return;

        if ($("recentEnquiries")) loadDashboard();
        if ($("vehiclesTable")) {
            loadVehicles();
            initializePhotoUpload();
        }
    }

    $("addVehicleButton")?.addEventListener("click", openAddVehicleModal);
    $("vehicleSearch")?.addEventListener("input", applyFilters);
    $("categoryFilter")?.addEventListener("change", applyFilters);
    $("vehicleStatusFilter")?.addEventListener("change", applyFilters);
    $("refreshVehicles")?.addEventListener("click", loadVehicles);
    $("closeVehicleModal")?.addEventListener("click", closeVehicleModal);
    $("cancelVehicle")?.addEventListener("click", closeVehicleModal);
    $("vehicleForm")?.addEventListener("submit", saveVehicle);
    $("logoutButton")?.addEventListener("click", adminLogout);

    document.querySelector("#vehicleModal .admin-modal-overlay")?.addEventListener("click", closeVehicleModal);

    $("vehiclesTable")?.addEventListener("click", event => {
        const editBtn = event.target.closest(".vehicle-edit-button");
        if (editBtn) openEditVehicleModal(editBtn.dataset.id);

        const deleteBtn = event.target.closest(".vehicle-delete-button");
        if (deleteBtn) deleteVehicle(deleteBtn.dataset.id);
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeVehicleModal();
            closeEnquiryModal();
        }
    });
}

document.addEventListener("DOMContentLoaded", initializeAdmin);