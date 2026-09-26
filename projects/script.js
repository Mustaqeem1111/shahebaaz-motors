/* =========================================================
   SHAHEBAZ MOTORS
   GLOBAL JAVASCRIPT (UPDATED - SELL FORM PHOTO UPLOAD)
   BACKEND CONNECTED VERSION
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       BACKEND API
    ===================================================== */

    const API_BASE_URL = "http://127.0.0.1:5000/api";

    /* =====================================================
       INTEREST MODAL ELEMENTS
    ===================================================== */

    const interestModal = document.getElementById("interestModal");
    const interestOverlay = document.getElementById("interestOverlay");
    const closeInterestModal = document.getElementById("closeInterestModal");
    const interestForm = document.getElementById("interestForm");
    const successClose = document.getElementById("successClose");

    const selectedVehicleName = document.getElementById("selectedVehicleName");
    const selectedVehiclePrice = document.getElementById("selectedVehiclePrice");
    const leadVehicle = document.getElementById("leadVehicle");
    const leadPrice = document.getElementById("leadPrice");
    const leadReference = document.getElementById("leadReference");

    const interestFormContainer = document.getElementById("interestFormContainer");
    const interestSuccess = document.getElementById("interestSuccess");

    /* =====================================================
       VEHICLE GRID LOADING (DYNAMIC)
    ===================================================== */

    const vehicleGrid = document.getElementById("vehicleGrid");
    const listingLoading = document.getElementById("listingLoading");
    const noResults = document.getElementById("noResults");

    if (vehicleGrid) {
        loadVehiclesFromBackend();
    }

    async function loadVehiclesFromBackend() {
        const category = vehicleGrid.dataset.category || "ALL";

        if (listingLoading) listingLoading.hidden = false;
        if (noResults) noResults.hidden = true;

        try {
            let url = `${API_BASE_URL}/vehicles`;
            const params = [];

            if (category && category !== "ALL") {
                params.push(`category=${encodeURIComponent(category)}`);
            }

            params.push(`status=AVAILABLE`);

            if (params.length) {
                url += "?" + params.join("&");
            }

            const response = await fetch(url);
            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.message || "Failed to load vehicles.");
            }

            const vehicles = Array.isArray(result.vehicles) ? result.vehicles : [];

            renderVehicleCards(vehicles);

        } catch (error) {
            console.error("Vehicle loading error:", error);

            if (vehicleGrid) {
                vehicleGrid.innerHTML = "";
            }

            if (noResults) {
                noResults.hidden = false;
                const h3 = noResults.querySelector("h3");
                const p = noResults.querySelector("p");
                if (h3) h3.textContent = "Unable to load vehicles";
                if (p) p.textContent = "Please make sure the backend is running.";
            }
        } finally {
            if (listingLoading) listingLoading.hidden = true;
        }
    }

    function renderVehicleCards(vehicles) {
        if (!vehicleGrid) return;

        if (!vehicles.length) {
            vehicleGrid.innerHTML = "";
            if (noResults) noResults.hidden = false;
            return;
        }

        if (noResults) noResults.hidden = true;

        vehicleGrid.innerHTML = vehicles.map(vehicle => createVehicleCard(vehicle)).join("");
    }

    function createVehicleCard(vehicle) {
        const id = vehicle.id || "";
        const name = vehicle.vehicle_name || "Unnamed Vehicle";
        const brand = vehicle.brand || "";
        const model = vehicle.model || "";
        const year = vehicle.year || "";
        const price = vehicle.price;
        const fuel = vehicle.fuel_type || "";
        const status = String(vehicle.status || "AVAILABLE").toUpperCase();
        const category = String(vehicle.category || "").toUpperCase();
        const mileage = vehicle.mileage || "";

        let photoUrl = "";
        if (Array.isArray(vehicle.photos) && vehicle.photos.length > 0) {
            photoUrl = vehicle.photos[0].photo_url;
        } else if (vehicle.image) {
            photoUrl = vehicle.image;
        }

        if (photoUrl && photoUrl.startsWith("/uploads/")) {
            photoUrl = `http://127.0.0.1:5000${photoUrl}`;
        }

        const imgSrc = photoUrl || "https://via.placeholder.com/400x300/e8eaec/949aa1?text=No+Photo";

        let categoryBadge = "VEHICLE";
        if (category === "2WHEELER") categoryBadge = "TWO WHEELER";
        else if (category === "3WHEELER") categoryBadge = "THREE WHEELER";
        else if (category === "4WHEELER") categoryBadge = "FOUR WHEELER";

        let statusBadge = "FEATURED";
        if (status === "SOLD") statusBadge = "SOLD";
        else if (status === "RENTAL") statusBadge = "RENTAL";
        else if (status === "AVAILABLE") statusBadge = "AVAILABLE";

        let subtitle = model || "";
        if (brand && model) subtitle = `${brand} ${model}`;
        else if (brand) subtitle = brand;

        const specYear = year ? `
            <span>
                <i class="far fa-calendar"></i>
                ${escapeHtml(String(year))}
            </span>
        ` : "";

        const specMileage = mileage ? `
            <span>
                <i class="fas fa-road"></i>
                ${escapeHtml(String(mileage))}
            </span>
        ` : "";

        const specFuel = fuel ? `
            <span>
                <i class="fas fa-gas-pump"></i>
                ${escapeHtml(String(fuel))}
            </span>
        ` : "";

        const filterCategory = `${category.replace("WHEELER", "").toLowerCase()} ${fuel.toLowerCase()}`;

        const priceDisplay = formatPrice(price);

        return `
            <article
                class="vehicle-card"
                data-vehicle="${escapeHtml(name)}"
                data-category="${escapeHtml(filterCategory)}"
            >
                <div class="vehicle-image">

                    <img
                        src="${escapeHtml(imgSrc)}"
                        alt="${escapeHtml(name)}"
                        loading="lazy"
                        onerror="this.src='https://via.placeholder.com/400x300/e8eaec/949aa1?text=No+Photo'"
                    >

                    <span class="vehicle-tag">${escapeHtml(statusBadge)}</span>

                    <button
                        class="favorite-btn"
                        type="button"
                        aria-label="Add ${escapeHtml(name)} to favorites"
                    >
                        <i class="far fa-heart"></i>
                    </button>

                    <span class="vehicle-category-badge">${escapeHtml(categoryBadge)}</span>

                </div>

                <div class="vehicle-info">

                    <div class="vehicle-title-row">

                        <div>
                            <h3>${escapeHtml(name)}</h3>
                            <span>${escapeHtml(subtitle)}</span>
                        </div>

                        <strong class="vehicle-price">${escapeHtml(priceDisplay)}</strong>

                    </div>

                    <div class="vehicle-specs">
                        ${specYear}
                        ${specMileage}
                        ${specFuel}
                    </div>

                    <button
                        class="interest-btn"
                        type="button"
                        data-vehicle="${escapeHtml(name)}"
                        data-price="${Number(price) || 0}"
                    >
                        I'm Interested
                        <i class="fas fa-arrow-right"></i>
                    </button>

                </div>
            </article>
        `;
    }

    /* =====================================================
       INTEREST BUTTON - EVENT DELEGATION
    ===================================================== */

    document.addEventListener("click", event => {
        const btn = event.target.closest(".interest-btn");
        if (!btn) return;

        event.preventDefault();

        const vehicle = btn.dataset.vehicle || "";
        const price = btn.dataset.price || "0";

        if (selectedVehicleName) selectedVehicleName.textContent = vehicle;
        if (selectedVehiclePrice) {
            selectedVehiclePrice.textContent = "₹" + Number(price).toLocaleString("en-IN");
        }
        if (leadVehicle) leadVehicle.value = vehicle;
        if (leadPrice) leadPrice.value = price;

        if (interestFormContainer) interestFormContainer.style.display = "";
        if (interestSuccess) {
            interestSuccess.hidden = true;
            interestSuccess.classList.remove("active");
        }

        if (interestForm) interestForm.reset();
        if (leadVehicle) leadVehicle.value = vehicle;
        if (leadPrice) leadPrice.value = price;

        if (interestModal) {
            interestModal.classList.add("active");
            interestModal.setAttribute("aria-hidden", "false");
        }

        document.body.classList.add("modal-open");
    });

    /* =====================================================
       FAVORITE BUTTON
    ===================================================== */

    document.addEventListener("click", event => {
        const btn = event.target.closest(".favorite-btn");
        if (!btn) return;

        event.preventDefault();
        event.stopPropagation();

        btn.classList.toggle("active");

        const icon = btn.querySelector("i");
        if (icon) {
            if (btn.classList.contains("active")) {
                icon.classList.remove("far");
                icon.classList.add("fas");
            } else {
                icon.classList.remove("fas");
                icon.classList.add("far");
            }
        }

        const vehicleCard = btn.closest(".vehicle-card");
        if (vehicleCard) {
            const vehicleName = vehicleCard.querySelector("h3")?.textContent.trim();
            if (vehicleName) saveFavorite(vehicleName);
        }
    });

    /* =====================================================
       CLOSE INTEREST MODAL
    ===================================================== */

    function closeInterestModalWindow() {
        if (interestModal) {
            interestModal.classList.remove("active");
            interestModal.setAttribute("aria-hidden", "true");
        }
        document.body.classList.remove("modal-open");
    }

    if (closeInterestModal) closeInterestModal.addEventListener("click", closeInterestModalWindow);
    if (interestOverlay) interestOverlay.addEventListener("click", closeInterestModalWindow);
    if (successClose) successClose.addEventListener("click", closeInterestModalWindow);

    /* =====================================================
       VEHICLE INTEREST FORM - BACKEND
    ===================================================== */

    if (interestForm) {
        interestForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const name = document.getElementById("customerName")?.value.trim();
            const phone = document.getElementById("customerPhone")?.value.trim();
            const city = document.getElementById("customerCity")?.value.trim();
            const contactMethod = document.getElementById("contactMethod")?.value || "Phone";
            const message = document.getElementById("customerMessage")?.value.trim() || "";
            const vehicle = document.getElementById("leadVehicle")?.value || "";
            const price = document.getElementById("leadPrice")?.value || 0;

            if (!name || !phone || !city) {
                alert("Please fill all required fields.");
                return;
            }

            if (!/^[6-9]\d{9}$/.test(phone)) {
                alert("Please enter a valid 10-digit mobile number.");
                return;
            }

            const submitButton = document.getElementById("submitInterest");

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            }

            try {
                const response = await fetch(`${API_BASE_URL}/enquiries`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        customer_name: name,
                        phone: phone,
                        city: city,
                        vehicle_name: vehicle,
                        vehicle_price: Number(price),
                        enquiry_type: "PURCHASE",
                        message: `Preferred contact: ${contactMethod}. ${message}`
                    })
                });

                const result = await response.json();

                if (!response.ok || !result.success) {
                    throw new Error(result.message || "Failed to submit enquiry.");
                }

                if (leadReference) {
                    leadReference.textContent = "Reference: " + (result.reference || "Submitted Successfully");
                }

                if (interestFormContainer) interestFormContainer.style.display = "none";

                if (interestSuccess) {
                    interestSuccess.hidden = false;
                    interestSuccess.classList.add("active");
                }

                console.log("Enquiry saved successfully:", result.reference);

            } catch (error) {
                console.error("Enquiry backend error:", error);
                alert("Unable to connect to the server. Please make sure the backend is running.");

                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Send Enquiry';
                }
            }
        });
    }

    /* =====================================================
       GLOBAL ELEMENTS
    ===================================================== */

    const menuBtn = document.getElementById("menuBtn");
    const sideNav = document.getElementById("sideNav");
    const overlay = document.getElementById("overlay");

    function openMenu() {
        if (sideNav) sideNav.classList.add("active");
        if (overlay) overlay.classList.add("active");
        document.body.classList.add("menu-open");
    }

    function closeMenu() {
        if (sideNav) sideNav.classList.remove("active");
        if (overlay) overlay.classList.remove("active");
        document.body.classList.remove("menu-open");
    }

    if (menuBtn) {
        menuBtn.addEventListener("click", () => {
            if (sideNav.classList.contains("active")) {
                closeMenu();
            } else {
                openMenu();
            }
        });
    }

    if (overlay) overlay.addEventListener("click", closeMenu);

    document.querySelectorAll(".nav-item").forEach(item => {
        item.addEventListener("click", () => closeMenu());
    });

    /* =====================================================
       CURRENT YEAR
    ===================================================== */

    const currentYearEl = document.getElementById("currentYear");
    if (currentYearEl) currentYearEl.textContent = new Date().getFullYear();

    /* =====================================================
       VEHICLE SEARCH + FILTER
    ===================================================== */

    const vehicleSearch = document.getElementById("vehicleSearch");
    const filterToggle = document.getElementById("filterToggle");
    const filterPanel = document.getElementById("filterPanel");
    const filterChips = document.querySelectorAll("[data-filter]");

    let activeFilter = "all";

    if (filterToggle && filterPanel) {
        filterToggle.addEventListener("click", () => {
            filterPanel.classList.toggle("open");
        });
    }

    filterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            filterChips.forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            activeFilter = chip.dataset.filter || "all";
            applyVehicleFilters();
        });
    });

    if (vehicleSearch) {
        vehicleSearch.addEventListener("input", applyVehicleFilters);
    }

    function applyVehicleFilters() {
        if (!vehicleGrid) return;

        const search = vehicleSearch ? vehicleSearch.value.trim().toLowerCase() : "";

        const cards = vehicleGrid.querySelectorAll(".vehicle-card");
        let visibleCount = 0;

        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const category = (card.dataset.category || "").toLowerCase();

            const searchMatch = !search || text.includes(search);

            const filterMatch =
                activeFilter === "all" ||
                category.split(" ").includes(activeFilter);

            if (searchMatch && filterMatch) {
                card.style.display = "";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        if (noResults) noResults.hidden = visibleCount !== 0;
    }

    /* =====================================================
       FAVORITES
    ===================================================== */

    function saveFavorite(vehicleName) {
        let favorites = JSON.parse(localStorage.getItem("shahebazFavorites") || "[]");

        if (favorites.includes(vehicleName)) {
            favorites = favorites.filter(item => item !== vehicleName);
        } else {
            favorites.push(vehicleName);
        }

        localStorage.setItem("shahebazFavorites", JSON.stringify(favorites));
    }

    /* =====================================================
       RENTAL SEARCH
    ===================================================== */

    const rentalSearch = document.getElementById("rentalSearch");
    const rentalGrid = document.getElementById("rentalGrid");
    const rentalNoResults = document.getElementById("rentalNoResults");

    if (rentalSearch && rentalGrid) {
        rentalSearch.addEventListener("input", filterRentalVehicles);
    }

    function filterRentalVehicles() {
        if (!rentalGrid) return;

        const search = rentalSearch ? rentalSearch.value.trim().toLowerCase() : "";

        const activeRentalFilter =
            document.querySelector("[data-rental-filter].active")?.dataset.rentalFilter || "all";

        const cards = rentalGrid.querySelectorAll(".rental-card");
        let visibleCount = 0;

        cards.forEach(card => {
            const name = (card.dataset.rentalName || card.textContent).toLowerCase();
            const category = (card.dataset.rentalCategory || "").toLowerCase();

            const searchMatch = !search || name.includes(search);
            const filterMatch =
                activeRentalFilter === "all" ||
                category.split(" ").includes(activeRentalFilter);

            if (searchMatch && filterMatch) {
                card.style.display = "";
                visibleCount++;
            } else {
                card.style.display = "none";
            }
        });

        if (rentalNoResults) rentalNoResults.hidden = visibleCount !== 0;
    }

    /* =====================================================
       RENTAL FILTER PANEL + CHIPS
    ===================================================== */

    const rentalFilterToggle = document.getElementById("rentalFilterToggle");
    const rentalFilterPanel = document.getElementById("rentalFilterPanel");

    if (rentalFilterToggle && rentalFilterPanel) {
        rentalFilterToggle.addEventListener("click", () => {
            rentalFilterPanel.classList.toggle("open");
        });
    }

    const rentalFilterChips = document.querySelectorAll("[data-rental-filter]");

    rentalFilterChips.forEach(chip => {
        chip.addEventListener("click", () => {
            rentalFilterChips.forEach(item => item.classList.remove("active"));
            chip.classList.add("active");
            filterRentalVehicles();
        });
    });

    /* =====================================================
       RENTAL MODAL
    ===================================================== */

    const rentalModal = document.getElementById("rentalModal");
    const rentalModalOverlay = document.getElementById("rentalModalOverlay");
    const closeRentalModalButton = document.getElementById("closeRentalModal");
    const rentalSuccessClose = document.getElementById("rentalSuccessClose");

    function openRentalModal(vehicleName, rate) {
        if (!rentalModal) return;

        const vehicleNameElement = document.getElementById("rentalVehicleName");
        const vehicleRateElement = document.getElementById("rentalVehicleRate");
        const vehicleInput = document.getElementById("rentalVehicleInput");
        const rateInput = document.getElementById("rentalRateInput");

        const formContainer = document.getElementById("rentalFormContainer");
        const successBox = document.getElementById("rentalSuccess");

        if (formContainer) formContainer.hidden = false;
        if (successBox) {
            successBox.hidden = true;
            successBox.classList.remove("active");
        }

        if (vehicleNameElement) vehicleNameElement.textContent = vehicleName;
        if (vehicleRateElement) {
            vehicleRateElement.textContent = "₹" + Number(rate || 0).toLocaleString("en-IN") + "/day";
        }
        if (vehicleInput) vehicleInput.value = vehicleName;
        if (rateInput) rateInput.value = rate || "";

        rentalModal.classList.add("active");
        rentalModal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");

        setMinimumRentalDate();
    }

    function closeRentalModal() {
        if (!rentalModal) return;

        rentalModal.classList.remove("active");
        rentalModal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");
    }

    window.closeRentalModal = closeRentalModal;

    if (rentalModalOverlay) rentalModalOverlay.addEventListener("click", closeRentalModal);
    if (closeRentalModalButton) closeRentalModalButton.addEventListener("click", closeRentalModal);
    if (rentalSuccessClose) rentalSuccessClose.addEventListener("click", closeRentalModal);

    /* =====================================================
       RENTAL VEHICLE BUTTONS
    ===================================================== */

    const rentalButtons = document.querySelectorAll(".rental-interest-btn");

    rentalButtons.forEach(button => {
        button.addEventListener("click", () => {
            const vehicle = button.dataset.rentalVehicle || "Selected Vehicle";
            const rate = button.dataset.rentalRate || "0";
            openRentalModal(vehicle, rate);
        });
    });

    /* =====================================================
       RENTAL DATES
    ===================================================== */

    const rentalStartDate = document.getElementById("rentalStartDate");
    const rentalEndDate = document.getElementById("rentalEndDate");

    function getTodayDate() {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, "0");
        const day = String(today.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    function setMinimumRentalDate() {
        const today = getTodayDate();
        if (rentalStartDate) rentalStartDate.min = today;
        if (rentalEndDate) rentalEndDate.min = today;
    }

    if (rentalStartDate) {
        rentalStartDate.addEventListener("change", () => {
            if (!rentalEndDate) return;
            rentalEndDate.min = rentalStartDate.value;
            if (rentalEndDate.value && rentalEndDate.value < rentalStartDate.value) {
                rentalEndDate.value = "";
            }
        });
    }

    /* =====================================================
       RENTAL FORM - BACKEND
    ===================================================== */

    const rentalForm = document.getElementById("rentalForm");

    if (rentalForm) {
        rentalForm.addEventListener("submit", async event => {
            event.preventDefault();

            const start = rentalStartDate?.value;
            const end = rentalEndDate?.value;

            if (!start || !end) {
                showFormMessage(rentalForm, "Please select pickup and return dates.", "error");
                return;
            }

            if (end < start) {
                showFormMessage(rentalForm, "Return date cannot be before pickup date.", "error");
                return;
            }

            if (!validateForm(rentalForm)) {
                showFormMessage(rentalForm, "Please fill all required details.", "error");
                return;
            }

            const submitButton = document.getElementById("rentalSubmit");
            setButtonLoading(submitButton, true);

            try {
                const formData = new FormData(rentalForm);

                const rentalData = {
                    vehicle: document.getElementById("rentalVehicleInput")?.value || "",
                    rate: document.getElementById("rentalRateInput")?.value || 0,
                    pickup_date: start,
                    return_date: end,
                    customer_name: formData.get("customerName") || "",
                    phone: formData.get("phone") || "",
                    city: formData.get("city") || "",
                    message: formData.get("message") || ""
                };

                const response = await fetch(`${API_BASE_URL}/rental-request`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(rentalData)
                });

                const result = await response.json();

                if (!response.ok || !result.success) {
                    throw new Error(result.message || "Unable to submit rental request.");
                }

                const reference = result.reference || createReference("REN");

                saveLocalLead({
                    ...rentalData,
                    type: "rental_request",
                    reference: reference,
                    createdAt: new Date().toISOString(),
                    backendSaved: true
                });

                setButtonLoading(submitButton, false);
                showRentalSuccess(reference);
                rentalForm.reset();
                setMinimumRentalDate();

            } catch (error) {
                console.error("Rental backend error:", error);
                setButtonLoading(submitButton, false);
                showFormMessage(rentalForm, "Unable to connect to the server. Please try again.", "error");
            }
        });
    }

    function showRentalSuccess(reference) {
        const container = document.getElementById("rentalFormContainer");
        const success = document.getElementById("rentalSuccess");
        const referenceElement = document.getElementById("rentalReference");

        if (container) container.hidden = true;
        if (success) {
            success.hidden = false;
            success.classList.add("active");
        }
        if (referenceElement) referenceElement.textContent = "Reference: " + reference;
    }

    /* =====================================================
       SELL VEHICLE FORM - BACKEND (UPDATED: FormData with photos)
    ===================================================== */

    const sellForm = document.getElementById("sellVehicleForm");

    if (sellForm) {
        sellForm.addEventListener("submit", handleSellSubmission);
    }

    async function handleSellSubmission(event) {
        event.preventDefault();

        const form = event.currentTarget;

        if (!validateForm(form)) {
            showFormMessage(form, "Please complete all required fields.", "error");
            return;
        }

        const phone = document.getElementById("sellerPhone");

        if (phone && !validateIndianMobile(phone.value)) {
            phone.classList.add("invalid");
            showFormMessage(form, "Please enter a valid 10-digit mobile number.", "error");
            phone.focus();
            return;
        }

        const submitButton = document.getElementById("sellSubmitBtn");
        setButtonLoading(submitButton, true);

        try {
            const formData = new FormData(form);

            // Build FormData for backend (including photos)
            const postData = new FormData();

            postData.append("seller_name", formData.get("sellerName") || "");
            postData.append("phone", formData.get("phone") || "");
            postData.append("email", formData.get("email") || "");
            postData.append("city", formData.get("city") || "");
            postData.append("pincode", formData.get("pincode") || "");
            postData.append("vehicle_type", formData.get("vehicleType") || "");
            postData.append("vehicle_name", formData.get("vehicleName") || "");
            postData.append("brand", formData.get("brand") || "");
            postData.append("model", formData.get("model") || "");
            postData.append("year", formData.get("year") || "");
            postData.append("condition", formData.get("condition") || "");
            postData.append("expected_price", formData.get("expectedPrice") || "");
            postData.append("description", formData.get("description") || "");

            // Append photo files (max 4)
            const photoFiles = selectedPhotoFiles.slice(0, 4);

            photoFiles.forEach(file => {
                postData.append("photos", file);
            });

            // Send as multipart/form-data (no JSON)
            const response = await fetch(`${API_BASE_URL}/sell-vehicle`, {
                method: "POST",
                body: postData
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.message || "Unable to submit vehicle selling request.");
            }

            const reference = result.reference || createReference("SELL");

            saveLocalLead({
                seller_name: postData.get("seller_name"),
                phone: postData.get("phone"),
                city: postData.get("city"),
                vehicle_type: postData.get("vehicle_type"),
                brand: postData.get("brand"),
                model: postData.get("model"),
                year: postData.get("year"),
                expected_price: postData.get("expected_price"),
                photo_count: photoFiles.length,
                type: "vehicle_sale",
                reference: reference,
                createdAt: new Date().toISOString(),
                backendSaved: true
            });

            setButtonLoading(submitButton, false);
            showSellSuccess(reference);
            form.reset();

            selectedPhotoFiles = [];
            if (photoPreview) photoPreview.innerHTML = "";

        } catch (error) {
            console.error("Sell vehicle backend error:", error);
            setButtonLoading(submitButton, false);
            showFormMessage(form, "Unable to connect to the server. Please try again.", "error");
        }
    }

    /* =====================================================
       SELL SUCCESS
    ===================================================== */

    function showSellSuccess(reference) {
        const form = document.getElementById("sellVehicleForm");
        const success = document.getElementById("sellSuccess");
        const referenceElement = document.getElementById("sellReference");

        if (form) form.hidden = true;
        if (success) success.hidden = false;
        if (referenceElement) referenceElement.textContent = "Reference: " + reference;

        if (success) {
            success.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }

    /* =====================================================
       PHOTO UPLOAD PREVIEW
    ===================================================== */

    const photoInput = document.getElementById("vehiclePhotos");
    const photoPreview = document.getElementById("photoPreview");

    let selectedPhotoFiles = [];

    if (photoInput && photoPreview) {
        photoInput.addEventListener("change", () => {
            const newFiles = Array.from(photoInput.files);

            // Check limit: max 4 photos
            const totalCount = selectedPhotoFiles.length + newFiles.length;
            if (totalCount > 4) {
                alert("Maximum 4 photos allowed.");
                photoInput.value = "";
                return;
            }

            // Check each file size (8MB)
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
        if (!photoPreview) return;

        photoPreview.innerHTML = "";

        selectedPhotoFiles.forEach((file, index) => {
            if (!file.type.startsWith("image/")) return;

            const reader = new FileReader();

            reader.onload = event => {
                const wrapper = document.createElement("div");
                wrapper.className = "photo-preview-item";

                const image = document.createElement("img");
                image.src = event.target.result;
                image.alt = "Vehicle photo";

                const remove = document.createElement("button");
                remove.type = "button";
                remove.className = "photo-preview-remove";
                remove.innerHTML = '<i class="fas fa-times"></i>';

                remove.addEventListener("click", () => {
                    selectedPhotoFiles.splice(index, 1);
                    renderPhotoPreview();
                });

                wrapper.appendChild(image);
                wrapper.appendChild(remove);
                photoPreview.appendChild(wrapper);
            };

            reader.readAsDataURL(file);
        });
    }

    /* =====================================================
       SELL FORM YEAR
    ===================================================== */

    const vehicleYear = document.getElementById("vehicleYear");

    if (vehicleYear) {
        const currentYearVal = new Date().getFullYear();

        for (let year = currentYearVal; year >= currentYearVal - 30; year--) {
            const option = document.createElement("option");
            option.value = year;
            option.textContent = year;
            vehicleYear.appendChild(option);
        }
    }

    /* =====================================================
       MOBILE PHONE INPUT
    ===================================================== */

    const phoneInputs = document.querySelectorAll('input[type="tel"]');

    phoneInputs.forEach(input => {
        input.addEventListener("input", () => {
            input.value = input.value.replace(/\D/g, "").slice(0, 10);
        });
    });

    /* =====================================================
       FORM VALIDATION
    ===================================================== */

    function validateForm(form) {
        let valid = true;
        const requiredFields = form.querySelectorAll("[required]");

        requiredFields.forEach(field => {
            field.classList.remove("invalid");

            const value = field.value;

            if (field.type === "radio") {
                const group = form.querySelectorAll(`input[name="${field.name}"]`);
                const checked = Array.from(group).some(radio => radio.checked);

                if (!checked) {
                    valid = false;
                    field
                        .closest(".condition-option")
                        ?.querySelector(".condition-box")
                        ?.classList.add("invalid");
                }

                return;
            }

            if (!value || !value.trim()) {
                valid = false;
                field.classList.add("invalid");
            }
        });

        return valid;
    }

    function validateIndianMobile(number) {
        return /^[6-9]\d{9}$/.test(number);
    }

    /* =====================================================
       REMOVE INVALID STATE
    ===================================================== */

    document.querySelectorAll("input, textarea, select").forEach(field => {
        field.addEventListener("input", () => field.classList.remove("invalid"));
        field.addEventListener("change", () => field.classList.remove("invalid"));
    });

    /* =====================================================
       FORM MESSAGE
    ===================================================== */

    function showFormMessage(form, message, type = "error") {
        let messageBox = form.querySelector(".form-message");

        if (!messageBox) {
            messageBox = document.createElement("div");
            messageBox.className = "form-message";
            form.prepend(messageBox);
        }

        messageBox.textContent = message;
        messageBox.style.display = "block";

        if (type === "error") {
            messageBox.style.cssText = `
                padding:10px 12px;
                margin-bottom:15px;
                border-radius:7px;
                background:#fff0f0;
                border:1px solid #efc2c2;
                color:#b13c3c;
                font-size:11px;
                display:block;
            `;
        }
    }

    /* =====================================================
       BUTTON LOADING
    ===================================================== */

    function setButtonLoading(button, loading) {
        if (!button) return;

        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Processing...`;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }

    /* =====================================================
       REFERENCE
    ===================================================== */

    function createReference(prefix) {
        const now = Date.now().toString().slice(-7);
        const random = Math.floor(100 + Math.random() * 900);
        return `${prefix}-${now}-${random}`;
    }

    /* =====================================================
       LOCAL STORAGE
    ===================================================== */

    function saveLocalLead(data) {
        try {
            const leads = JSON.parse(localStorage.getItem("shahebazLeads") || "[]");
            leads.push(data);
            localStorage.setItem("shahebazLeads", JSON.stringify(leads));
        } catch (error) {
            console.error("Could not save local lead:", error);
        }
    }

    window.getShahebazLeads = function () {
        try {
            return JSON.parse(localStorage.getItem("shahebazLeads") || "[]");
        } catch {
            return [];
        }
    };

    window.clearShahebazLeads = function () {
        localStorage.removeItem("shahebazLeads");
        console.log("Shahebaz Motors test leads cleared.");
    };

    /* =====================================================
       SMOOTH INTERNAL LINKS
    ===================================================== */

    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", event => {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") return;

            const target = document.querySelector(targetId);

            if (target) {
                event.preventDefault();
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeMenu();
            closeInterestModalWindow();
            closeRentalModal();
        }
    });

    /* =====================================================
       HELPERS
    ===================================================== */

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatPrice(price) {
        if (price === null || price === undefined || price === "") return "—";
        const number = Number(price);
        return Number.isNaN(number) ? String(price) : "₹" + number.toLocaleString("en-IN");
    }

    /* =====================================================
       INITIALIZE
    ===================================================== */

    setMinimumRentalDate();

    if (rentalGrid) filterRentalVehicles();
    if (vehicleGrid) applyVehicleFilters();

});