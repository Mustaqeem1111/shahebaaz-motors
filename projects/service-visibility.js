(() => {
  const visibilityStyle = document.createElement("style");
  visibilityStyle.textContent = ".service-setting-hidden { display: none !important; }";
  document.head.appendChild(visibilityStyle);

  const categoryServices = {
    "2WHEELER": "2WHEELER",
    "3WHEELER": "3WHEELER",
    "4WHEELER": "4WHEELER"
  };
  const pageServices = {
    "two-wheeler.html": "2WHEELER",
    "three-wheeler.html": "3WHEELER",
    "four-wheeler.html": "4WHEELER",
    "rental.html": "RENTALS",
    "index.html": null
  };

  function setHiddenBySetting(element, hide) {
    if (!Object.prototype.hasOwnProperty.call(element.dataset, "serviceOriginalHidden")) {
      element.dataset.serviceOriginalHidden = String(element.hidden);
      element.dataset.serviceOriginalAriaHidden = element.hasAttribute("aria-hidden")
        ? element.getAttribute("aria-hidden")
        : "__unset__";
    }
    if (hide) {
      element.hidden = true;
      element.classList.add("service-setting-hidden");
      element.setAttribute("aria-hidden", "true");
      return;
    }
    element.hidden = element.dataset.serviceOriginalHidden === "true";
    element.classList.remove("service-setting-hidden");
    if (element.dataset.serviceOriginalAriaHidden === "__unset__") element.removeAttribute("aria-hidden");
    else element.setAttribute("aria-hidden", element.dataset.serviceOriginalAriaHidden);
    delete element.dataset.serviceOriginalHidden;
    delete element.dataset.serviceOriginalAriaHidden;
  }

  function setOptionDisabledBySetting(option, disable) {
    if (!Object.prototype.hasOwnProperty.call(option.dataset, "serviceOriginalDisabled")) {
      option.dataset.serviceOriginalDisabled = String(option.disabled);
      option.dataset.serviceOriginalHidden = String(option.hidden);
    }
    option.disabled = disable || option.dataset.serviceOriginalDisabled === "true";
    option.hidden = disable || option.dataset.serviceOriginalHidden === "true";
    if (disable && option.selected) option.closest("select").value = "";
    if (!disable) {
      delete option.dataset.serviceOriginalDisabled;
      delete option.dataset.serviceOriginalHidden;
    }
  }

  function serviceForOption(option) {
    const value = `${option.value} ${option.textContent}`.toUpperCase().replace(/[\s_-]/g, "");
    if (value.includes("2WHEELER") || value.includes("TWOWHEELER")) return "2WHEELER";
    if (value.includes("3WHEELER") || value.includes("THREEWHEELER")) return "3WHEELER";
    if (value.includes("4WHEELER") || value.includes("FOURWHEELER")) return "4WHEELER";
    if (value.includes("RENTVEHICLE") || value.includes("RENTAL")) return "RENTALS";
    return null;
  }

  function applyServices(services) {
    document.querySelectorAll("a[href]").forEach(link => {
      let path;
      try {
        path = new URL(link.href, window.location.href).pathname.toLowerCase();
      } catch (_) {
        return;
      }
      const file = path.split("/").filter(Boolean).pop() || "index.html";
      const service = path.endsWith("/rental/index.html") ? "RENTALS" : pageServices[file];
      if (service) setHiddenBySetting(link.closest(".category-card") || link, services[service] === false);
    });

    document.querySelectorAll("[data-filter]").forEach(button => {
      const service = categoryServices[String(button.dataset.filter || "").toUpperCase()];
      setHiddenBySetting(button, !!service && services[service] === false);
    });

    document.querySelectorAll("select option").forEach(option => {
      const service = serviceForOption(option);
      if (service) setOptionDisabledBySetting(option, services[service] === false);
    });

    const currentPath = window.location.pathname.toLowerCase();
    const currentPage = currentPath.split("/").filter(Boolean).pop() || "index.html";
    const currentService = currentPath.endsWith("/rental/index.html")
      ? "RENTALS"
      : pageServices[currentPage];
    if (currentService && services[currentService] === false && !(currentPage === "index.html" && currentPath === "/")) {
      window.location.replace("/index.html");
    }

    document.documentElement.dataset.servicesLoaded = "true";
  }

  async function refreshServices() {
    try {
      const response = await fetch("/api/site-services", { cache: "no-store" });
      if (!response.ok) throw new Error("Service settings unavailable");
      const result = await response.json();
      if (!result.success || !result.services) throw new Error("Service settings unavailable");
      applyServices(result.services);
      return result.services;
    } catch (_) {
      document.documentElement.dataset.servicesLoaded = "true";
      return null;
    }
  }

  refreshServices();
  window.setInterval(refreshServices, 60000);
  window.addEventListener("focus", refreshServices);
  window.addEventListener("storage", event => {
    if (event.key !== "shahebaz_site_services_updated" || !event.newValue) return;
    try { applyServices(JSON.parse(event.newValue)); } catch (_) { /* Ignore invalid cross-tab data. */ }
  });
})();
