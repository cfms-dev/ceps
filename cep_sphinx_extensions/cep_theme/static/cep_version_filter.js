/**
 * Protocol version filter for CEP Index page
 * Filters CEP tables by protocol_version using the JSON API
 */
(function () {
  "use strict";

  const STORAGE_KEY = "cep_protocol_version_filter";
  const API_URL =
    document.currentScript?.dataset.apiUrl || "/api/ceps.json";
  let cepVersionMap = {};
  let allVersions = [];

  /**
   * Parse protocol_version value into an array of normalized positive integer strings
   */
  function parseProtocolVersions(value) {
    if (value === null || value === undefined) return [];
    const items = Array.isArray(value) ? value : String(value).split(",");
    return items
      .map((v) => String(v).trim())
      .filter((v) => /^[1-9]\d*$/.test(v));
  }

  /**
   * Sort protocol versions in descending order (newest first)
   */
  function sortVersionsDescending(versions) {
    return versions.sort((a, b) => Number(b) - Number(a));
  }

  /**
   * Fetch CEP data and build protocol version map
   */
  async function loadCepData() {
    try {
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error("Failed to fetch CEP data");
      const data = await response.json();

      const versionSet = new Set();

      for (const [cepNum, cep] of Object.entries(data)) {
        const versions = parseProtocolVersions(cep.protocol_version);
        cepVersionMap[cepNum] = versions;

        for (const v of versions) {
          versionSet.add(v);
        }
      }

      allVersions = sortVersionsDescending([...versionSet]);
      return true;
    } catch (error) {
      console.error("Error loading CEP data:", error);
      return false;
    }
  }

  /**
   * Extract CEP number from a table row
   */
  function getCepNumberFromRow(row) {
    const link = row.querySelector('a[href*="cep-"]');
    if (!link) return null;
    const match = link.getAttribute("href").match(/cep-0*(\d+)/);
    return match ? match[1] : null;
  }

  /**
   * Check if a CEP matches the selected protocol version filter
   */
  function cepMatchesVersion(cepNum, selectedVersion) {
    if (!selectedVersion || selectedVersion === "all") return true;
    return (cepVersionMap[cepNum] || []).includes(selectedVersion);
  }

  /**
   * Apply the filter to all CEP tables
   */
  function applyFilter(selectedVersion) {
    const tables = document.querySelectorAll("table.cep-zero-table");
    let totalVisible = 0;
    let totalCeps = 0;

    tables.forEach((table) => {
      const rows = table.querySelectorAll("tbody tr");
      let visibleInTable = 0;

      rows.forEach((row) => {
        const cepNum = getCepNumberFromRow(row);
        if (cepNum === null) return;

        totalCeps++;
        const matches = cepMatchesVersion(cepNum, selectedVersion);

        if (matches) {
          row.style.display = "";
          visibleInTable++;
          totalVisible++;
        } else {
          row.style.display = "none";
        }
      });

      // Find the section container (h2 + table) and hide if empty
      const section = table.closest("section") || table.parentElement;
      const h2 = section?.querySelector("h2");
      if (h2 && visibleInTable === 0 && selectedVersion !== "all") {
        section.style.display = "none";
      } else if (section) {
        section.style.display = "";
      }
    });

    updateCount(totalVisible, totalCeps, selectedVersion);
  }

  /**
   * Update the count display
   */
  function updateCount(visible, total, selectedVersion) {
    const countEl = document.getElementById("cep-filter-count");
    if (!countEl) return;

    if (!selectedVersion || selectedVersion === "all") {
      countEl.textContent = "";
    } else {
      countEl.textContent = `Showing ${visible} of ${total} CEPs`;
    }
  }

  /**
   * Create the filter UI
   */
  function createFilterUI() {
    const container = document.createElement("div");
    container.id = "cep-version-filter";
    container.innerHTML = `
            <label for="cep-version-select">Filter by protocol version:</label>
            <select id="cep-version-select">
                <option value="all">All versions</option>
            </select>
            <span id="cep-filter-count" aria-live="polite"></span>
        `;

    const select = container.querySelector("#cep-version-select");

    // Add version options
    for (const version of allVersions) {
      const option = document.createElement("option");
      option.value = version;
      option.textContent = version;
      select.appendChild(option);
    }

    // Restore saved selection
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && (saved === "all" || allVersions.includes(saved))) {
      select.value = saved;
    }

    // Handle filter changes
    select.addEventListener("change", () => {
      const value = select.value;
      localStorage.setItem(STORAGE_KEY, value);
      applyFilter(value);
    });

    return container;
  }

  /**
   * Insert the filter UI into the page
   */
  function insertFilterUI(filterUI) {
    // Find the "Index by Category" section and insert after its heading
    const indexByCategory = document.getElementById("index-by-category");
    if (indexByCategory) {
      const heading = indexByCategory.querySelector("h2");
      if (heading) {
        heading.after(filterUI);
        return true;
      }
    }

    return false;
  }

  /**
   * Initialize the filter
   */
  async function init() {
    // Only run on CEP 0 (index page)
    const isCepIndex =
      document.querySelector("section#introduction") &&
      document.querySelector("table.cep-zero-table");
    if (!isCepIndex) return;

    const loaded = await loadCepData();
    if (!loaded || allVersions.length === 0) return;

    const filterUI = createFilterUI();
    const inserted = insertFilterUI(filterUI);

    if (inserted) {
      // Apply initial filter
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && saved !== "all") {
        applyFilter(saved);
      }
    }
  }

  // Run when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
