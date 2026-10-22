document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("siteServicesForm");
    const saveButton = document.getElementById("saveServicesButton");
    const notice = document.getElementById("servicesNotice");
    const toggles = [...document.querySelectorAll("[data-service-setting]")];
    if (!form || !saveButton || !notice || !toggles.length) return;

    const showNotice = (message, type = "") => {
        notice.textContent = message;
        notice.dataset.state = type;
    };
    const setFormDisabled = disabled => {
        toggles.forEach(toggle => { toggle.disabled = disabled; });
        saveButton.disabled = disabled;
    };
    const readSettings = () => Object.fromEntries(toggles.map(toggle => [toggle.dataset.serviceSetting, toggle.checked]));

    async function loadSettings() {
        setFormDisabled(true);
        showNotice("Loading website services…");
        try {
            const result = await apiRequest("/api/site-services", { cache: "no-store" });
            toggles.forEach(toggle => {
                toggle.checked = result.services?.[toggle.dataset.serviceSetting] !== false;
            });
            showNotice("Your current website services are loaded.");
            setFormDisabled(false);
        } catch (error) {
            showNotice(error.message || "Could not load website services.", "error");
            setFormDisabled(true);
        }
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        setFormDisabled(true);
        showNotice("Saving changes…");
        try {
            const result = await apiRequest("/api/admin/site-services", {
                method: "PUT",
                body: JSON.stringify({ services: readSettings() })
            });
            toggles.forEach(toggle => {
                toggle.checked = result.services?.[toggle.dataset.serviceSetting] !== false;
            });
            try {
                localStorage.setItem("shahebaz_site_services_updated", JSON.stringify(result.services));
            } catch (_) {
                // Public pages still refresh their settings from the API.
            }
            showNotice("Saved. Open website pages are updating; new visits will use these settings.", "success");
        } catch (error) {
            showNotice(error.message || "Could not save website services.", "error");
        } finally {
            setFormDisabled(false);
        }
    });

    loadSettings();
});
