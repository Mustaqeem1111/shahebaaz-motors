document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("rentalFleetTable");
  const notice = document.getElementById("rentalFleetNotice");
  const modal = document.getElementById("rentalVehicleModal");
  const form = document.getElementById("rentalVehicleForm");
  const saveButton = document.getElementById("saveRentalVehicle");
  const formError = document.getElementById("rentalVehicleFormError");
  let rentalVehicles = [];
  let lastTrigger = null;

  function showNotice(text, type = "") {
    notice.textContent = text;
    notice.classList.toggle("is-error", type === "error");
    notice.classList.toggle("is-success", type === "success");
  }

  function categoryLabel(category) {
    return ({ "2WHEELER": "Two wheeler", "3WHEELER": "Three wheeler", "4WHEELER": "Car" })[String(category || "").toUpperCase()] || "Vehicle";
  }

  function photoMarkup(vehicle) {
    const photo = vehicle.photos?.[0]?.photo_url || vehicle.image || "";
    if (!photo) return '<div class="rental-fleet-photo-placeholder" aria-label="No photo">—</div>';
    return `<img class="rental-fleet-photo" src="${escapeHtml(photo)}" alt="${escapeHtml(vehicle.vehicle_name || "Vehicle")}">`;
  }

  function renderFleet() {
    if (!rentalVehicles.length) {
      table.innerHTML = '<tr><td colspan="5" class="rental-fleet-empty">No vehicles are listed for rent. Add one to show it on the rental website.</td></tr>';
      return;
    }
    table.innerHTML = rentalVehicles.map(vehicle => `
      <tr>
        <td>${photoMarkup(vehicle)}</td>
        <td><span class="rental-fleet-name"><strong>${escapeHtml(vehicle.vehicle_name || "Vehicle")}</strong><small>${escapeHtml([vehicle.brand, vehicle.model].filter(Boolean).join(" "))}</small></span></td>
        <td>${escapeHtml(categoryLabel(vehicle.category))}</td>
        <td class="rental-fleet-rate">${formatPrice(vehicle.rental_price)} / day</td>
        <td><div class="rental-fleet-actions"><button type="button" class="admin-button danger" data-remove-rental="${escapeHtml(vehicle.id)}">Remove</button></div></td>
      </tr>`).join("");
  }

  async function loadFleet() {
    table.innerHTML = '<tr><td colspan="5" class="table-loading">Loading rental vehicles...</td></tr>';
    try {
      const result = await apiRequest(`${API_BASE}/vehicles?status=RENTAL`);
      rentalVehicles = Array.isArray(result.vehicles) ? result.vehicles : [];
      renderFleet();
    } catch (error) {
      table.innerHTML = `<tr><td colspan="5" class="table-loading">Unable to load rental vehicles. ${escapeHtml(error.message || "")}</td></tr>`;
    }
  }

  function openModal() {
    lastTrigger = document.getElementById("addRentalVehicleButton");
    form.reset();
    formError.textContent = "";
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
    window.setTimeout(() => document.getElementById("rentalVehicleName").focus(), 0);
  }

  function closeModal() {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
    lastTrigger?.focus();
  }

  async function saveRentalVehicle(event) {
    event.preventDefault();
    formError.textContent = "";
    const photos = [...(document.getElementById("rentalVehiclePhotos").files || [])];
    if (photos.length > 4) {
      formError.textContent = "Choose no more than four photos.";
      return;
    }
    const invalidPhoto = photos.find(photo => !photo.type.startsWith("image/") || photo.size > 8 * 1024 * 1024);
    if (invalidPhoto) {
      formError.textContent = `${invalidPhoto.name} must be an image smaller than 8 MB.`;
      return;
    }

    const formData = new FormData(form);
    formData.set("status", "RENTAL");
    saveButton.disabled = true;
    saveButton.textContent = "Adding…";
    try {
      await apiRequest(`${API_BASE}/vehicles`, { method: "POST", body: formData });
      closeModal();
      showNotice("Vehicle added to the rental website.", "success");
      await loadFleet();
    } catch (error) {
      formError.textContent = error.message || "Unable to add the vehicle.";
    } finally {
      saveButton.disabled = false;
      saveButton.textContent = "Add to rentals";
    }
  }

  async function removeFromRentals(vehicleId) {
    const vehicle = rentalVehicles.find(item => String(item.id) === String(vehicleId));
    if (!vehicle) return;
    if (!confirm(`Remove ${vehicle.vehicle_name || "this vehicle"} from the rental website? The vehicle record and photos will be kept.`)) return;

    showNotice("");
    try {
      const keepPhotos = (vehicle.photos || []).map(photo => photo.photo_url).filter(Boolean);
      await apiRequest(`${API_BASE}/vehicles/${vehicle.id}`, {
        method: "PUT",
        body: JSON.stringify({ status: "INACTIVE", keep_photos: JSON.stringify(keepPhotos) })
      });
      rentalVehicles = rentalVehicles.filter(item => String(item.id) !== String(vehicle.id));
      renderFleet();
      showNotice("Vehicle removed from rentals. Its record and photos are still in inventory.", "success");
    } catch (error) {
      showNotice(error.message || "Unable to remove the vehicle.", "error");
    }
  }

  document.getElementById("addRentalVehicleButton")?.addEventListener("click", openModal);
  document.getElementById("closeRentalVehicleModal")?.addEventListener("click", closeModal);
  document.getElementById("cancelRentalVehicle")?.addEventListener("click", closeModal);
  modal?.querySelector(".admin-modal-overlay")?.addEventListener("click", closeModal);
  form?.addEventListener("submit", saveRentalVehicle);
  table?.addEventListener("click", event => {
    const button = event.target.closest("[data-remove-rental]");
    if (button) removeFromRentals(button.dataset.removeRental);
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && modal.classList.contains("active")) closeModal();
  });

  loadFleet();
});
