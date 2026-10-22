document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menuToggle");
  const primaryNav = document.getElementById("primaryNav");
  const search = document.getElementById("vehicleSearch");
  const vehicleGrid = document.getElementById("vehicleGrid");
  const inventoryStatus = document.getElementById("inventoryStatus");
  const inventoryEmpty = document.getElementById("inventoryEmpty");
  const noResults = document.getElementById("noResults");
  const filters = [...document.querySelectorAll("[data-filter]")];
  const vehiclesById = new Map();
  let activeFilter = "all";
  let vehicles = [];

  menuToggle?.addEventListener("click", () => {
    const isOpen = primaryNav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    menuToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  });

  primaryNav?.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", () => {
      primaryNav.classList.remove("is-open");
      menuToggle?.setAttribute("aria-expanded", "false");
      menuToggle?.setAttribute("aria-label", "Open navigation");
    });
  });

  function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[character]);
  }

  function categoryLabel(category) {
    return ({
      "2WHEELER": "Two wheeler",
      "3WHEELER": "Three wheeler",
      "4WHEELER": "Car"
    })[String(category || "").toUpperCase()] || "Vehicle";
  }

  function formatRate(value) {
    const rate = Number(value);
    if (!Number.isFinite(rate) || rate <= 0) return "Rate on request";
    return `${new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(rate)}<span>/day</span>`;
  }

  function photoMarkup(vehicle) {
    const rawUrl = vehicle.photos?.[0]?.photo_url || vehicle.image || "";
    const safeUrl = /^(https?:\/\/|\/)/i.test(rawUrl) ? rawUrl : "";
    const name = escapeHTML(vehicle.vehicle_name || "Vehicle");
    if (safeUrl) {
      return `<img src="${escapeHTML(safeUrl)}" alt="${name}" loading="lazy" decoding="async">`;
    }
    return `<div class="photo-placeholder" aria-label="No vehicle photo added"><svg viewBox="0 0 100 54" aria-hidden="true"><path d="M14 36h6l6-14c1-3 4-5 7-5h32c4 0 7 2 9 5l7 14h5c3 0 5 2 5 5v4H9v-4c0-3 2-5 5-5Z"/><path d="M27 22h40l7 14H21l6-14Z"/><circle cx="27" cy="43" r="5"/><circle cx="73" cy="43" r="5"/></svg><span>Photo not added</span></div>`;
  }

  function cardMarkup(vehicle) {
    const id = escapeHTML(vehicle.id);
    const name = escapeHTML(vehicle.vehicle_name || "Vehicle");
    const category = String(vehicle.category || "").toUpperCase();
    const specs = [vehicle.fuel_type, vehicle.transmission, vehicle.seats ? `${vehicle.seats} seats` : ""]
      .map(value => String(value || "").trim())
      .filter(Boolean);
    const specMarkup = specs.length
      ? specs.map((spec, index) => `${index ? "<i aria-hidden=\"true\"></i>" : ""}<span>${escapeHTML(spec)}</span>`).join("")
      : "<span>Ask us for details</span>";

    return `<article class="vehicle-card" data-name="${name.toLocaleLowerCase()}" data-category="${escapeHTML(category)}">
      <div class="vehicle-photo">${photoMarkup(vehicle)}</div>
      <div class="vehicle-info">
        <div class="vehicle-heading"><div><span class="vehicle-kind">${escapeHTML(categoryLabel(category))}</span><h3>${name}</h3></div>
          <p class="vehicle-price"><strong>${formatRate(vehicle.rental_price)}</strong></p>
        </div>
        <p class="vehicle-specs">${specMarkup}</p>
        <button class="button button--green availability-button" type="button" data-vehicle-id="${id}">Ask about this vehicle <span aria-hidden="true">→</span></button>
      </div>
    </article>`;
  }

  function renderVehicles() {
    const query = search.value.trim().toLocaleLowerCase();
    const filtered = vehicles.filter(vehicle => {
      const name = `${vehicle.vehicle_name || ""} ${vehicle.brand || ""} ${vehicle.model || ""}`.toLocaleLowerCase();
      const category = String(vehicle.category || "").toUpperCase();
      return name.includes(query) && (activeFilter === "all" || category === activeFilter);
    });

    vehicleGrid.innerHTML = filtered.map(cardMarkup).join("");
    noResults.hidden = vehicles.length === 0 || filtered.length !== 0;
    inventoryEmpty.hidden = vehicles.length !== 0;
  }

  async function loadVehicles() {
    inventoryStatus.classList.remove("inventory-state--error");
    inventoryStatus.textContent = "Loading the rental list…";
    try {
      const endpoint = new URL("../api/vehicles?status=RENTAL", window.location.href);
      const response = await fetch(endpoint, { headers: { Accept: "application/json" }, cache: "no-store" });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error(result.message || "Unable to load vehicles.");
      vehicles = Array.isArray(result.vehicles) ? result.vehicles : [];
      vehiclesById.clear();
      vehicles.forEach(vehicle => vehiclesById.set(String(vehicle.id), vehicle));
      inventoryStatus.textContent = "";
      renderVehicles();
    } catch (error) {
      inventoryStatus.classList.add("inventory-state--error");
      inventoryStatus.textContent = "We couldn’t load the rental list just now. Please refresh the page to try again.";
      inventoryEmpty.hidden = true;
      noResults.hidden = true;
      vehicleGrid.innerHTML = "";
    }
  }

  search?.addEventListener("input", renderVehicles);
  filters.forEach(button => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.filter;
      filters.forEach(item => {
        const selected = item === button;
        item.classList.toggle("is-active", selected);
        item.setAttribute("aria-pressed", String(selected));
      });
      renderVehicles();
    });
  });

  const dialog = document.getElementById("bookingDialog");
  const form = document.getElementById("rentalForm");
  const pickupDate = document.getElementById("pickupDate");
  const returnDate = document.getElementById("returnDate");
  const message = document.getElementById("formMessage");
  const success = document.getElementById("bookingSuccess");
  const content = document.getElementById("bookingContent");
  const submitButton = document.getElementById("submitRental");
  let previousFocus = null;

  function dateToday() {
    const now = new Date();
    return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  }

  function resetFormState() {
    form.reset();
    content.hidden = false;
    form.hidden = false;
    success.hidden = true;
    message.hidden = true;
    message.textContent = "";
    pickupDate.min = dateToday();
    returnDate.min = dateToday();
    submitButton.disabled = false;
    submitButton.innerHTML = 'Send rental request <span aria-hidden="true">→</span>';
  }

  function openBooking(vehicle, trigger) {
    resetFormState();
    previousFocus = trigger;
    document.getElementById("selectedVehicle").textContent = vehicle.vehicle_name || "Vehicle";
    const rate = Number(vehicle.rental_price);
    document.getElementById("selectedRate").textContent = Number.isFinite(rate) && rate > 0
      ? `${new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(rate)} per day`
      : "Our team will confirm the rate";
    document.getElementById("rentalVehicleId").value = vehicle.id;
    document.getElementById("rentalVehicle").value = vehicle.vehicle_name || "";
    document.getElementById("rentalRate").value = Number.isFinite(rate) && rate > 0 ? String(rate) : "";
    dialog.showModal();
    document.body.classList.add("dialog-open");
    window.setTimeout(() => pickupDate.focus(), 0);
  }

  function closeBooking() {
    if (dialog.open) dialog.close();
  }

  vehicleGrid.addEventListener("click", event => {
    const button = event.target.closest("[data-vehicle-id]");
    if (!button) return;
    const vehicle = vehiclesById.get(button.dataset.vehicleId);
    if (vehicle) openBooking(vehicle, button);
  });

  document.querySelectorAll("[data-close-dialog]").forEach(button => button.addEventListener("click", closeBooking));
  dialog.addEventListener("click", event => {
    if (event.target === dialog) closeBooking();
  });
  dialog.addEventListener("close", () => {
    document.body.classList.remove("dialog-open");
    previousFocus?.focus();
  });

  pickupDate.min = dateToday();
  returnDate.min = dateToday();
  pickupDate.addEventListener("change", () => {
    returnDate.min = pickupDate.value || dateToday();
    if (returnDate.value && returnDate.value < returnDate.min) returnDate.value = "";
  });

  form.addEventListener("submit", async event => {
    event.preventDefault();
    message.hidden = true;
    if (returnDate.value < pickupDate.value) {
      message.textContent = "Return date cannot be before the pickup date.";
      message.hidden = false;
      returnDate.focus();
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Sending request…";
    const values = new FormData(form);
    const rentalData = {
      vehicle_id: values.get("vehicleId"),
      vehicle: values.get("vehicle"),
      rate: values.get("rate"),
      pickup_date: values.get("pickupDate"),
      return_date: values.get("returnDate"),
      customer_name: values.get("customerName"),
      phone: values.get("phone"),
      city: values.get("city"),
      message: values.get("message")
    };

    try {
      const endpoint = new URL("../api/rental-request", window.location.href);
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(rentalData)
      });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error(result.message || "Unable to send your request. Please try again.");

      const reference = result.reference || "";
      try {
        const leads = JSON.parse(localStorage.getItem("shahebazLeads") || "[]");
        leads.unshift({ ...rentalData, type: "rental_request", reference, createdAt: new Date().toISOString(), backendSaved: true });
        localStorage.setItem("shahebazLeads", JSON.stringify(leads.slice(0, 100)));
      } catch (storageError) {
        console.warn("Rental request was saved on the server, but could not be cached locally.", storageError);
      }

      document.getElementById("requestReference").textContent = reference ? `Reference: ${reference}` : "";
      content.hidden = true;
      success.hidden = false;
      success.querySelector("[data-close-dialog]").focus();
    } catch (error) {
      message.textContent = error.message || "Unable to connect to the server. Please try again.";
      message.hidden = false;
      submitButton.disabled = false;
      submitButton.innerHTML = 'Send rental request <span aria-hidden="true">→</span>';
    }
  });

  dialog.addEventListener("close", () => {
    if (!success.hidden) resetFormState();
  });

  const year = document.getElementById("currentYear");
  if (year) year.textContent = String(new Date().getFullYear());
  loadVehicles();
});
