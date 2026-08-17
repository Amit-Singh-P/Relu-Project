const DEFAULT_API_BASE = window.location.origin.startsWith("file:")
  ? "http://localhost:8000"
  : window.location.origin;

const STORAGE_KEY = "company-insight-api-base";

const apiBaseInput = document.getElementById("api-base");
const apiStatusDot = document.getElementById("api-status");
const enrichForm = document.getElementById("enrich-form");
const enrichBtn = document.getElementById("enrich-btn");
const enrichStatus = document.getElementById("enrich-status");
const enrichResult = document.getElementById("enrich-result");
const resultsBtn = document.getElementById("results-btn");
const resultsStatus = document.getElementById("results-status");
const resultsPanel = document.getElementById("results-panel");

function getApiBase() {
  return apiBaseInput.value.trim().replace(/\/+$/, "") || DEFAULT_API_BASE;
}

function initApiBase() {
  apiBaseInput.value = localStorage.getItem(STORAGE_KEY) || DEFAULT_API_BASE;
  apiBaseInput.addEventListener("change", () => {
    localStorage.setItem(STORAGE_KEY, getApiBase());
    checkHealth();
  });
}

async function checkHealth() {
  try {
    const res = await fetch(`${getApiBase()}/health`, { method: "GET" });
    apiStatusDot.className = res.ok ? "status-dot ok" : "status-dot err";
    apiStatusDot.title = res.ok ? "Backend reachable" : `Backend returned ${res.status}`;
  } catch {
    apiStatusDot.className = "status-dot err";
    apiStatusDot.title = "Backend unreachable";
  }
}

function setStatus(el, message, kind) {
  el.textContent = "";
  el.className = `status-line ${kind || ""}`.trim();
  if (kind === "loading") {
    const spinner = document.createElement("span");
    spinner.className = "spinner";
    el.appendChild(spinner);
  }
  el.appendChild(document.createTextNode(message));
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value == null ? "" : String(value);
  return div.innerHTML;
}

const FIELD_LABELS = {
  company_name: "Company Name",
  address: "Address",
  mobile_number: "Mobile Number",
  core_service: "Core Service",
  target_customer: "Target Customer",
  probable_pain_point: "Probable Pain Point",
  outreach_opener: "Outreach Opener",
};

function renderProfileCard(profile) {
  const wrapper = document.createElement("article");
  wrapper.className = "profile-card";

  const title = document.createElement("h3");
  title.textContent = profile.website_name || profile.label || profile.source_url || "Unknown Company";
  wrapper.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "profile-meta";
  const status = profile.status || "unknown";
  meta.innerHTML = `
    <span class="badge ${escapeHtml(status)}">${escapeHtml(status)}</span>
    <span>${escapeHtml(profile.source_url || "")}</span>
    <span>${profile.scraped_at ? new Date(profile.scraped_at).toLocaleString() : ""}</span>
  `;
  wrapper.appendChild(meta);

  const grid = document.createElement("dl");
  grid.className = "profile-grid";

  Object.entries(FIELD_LABELS).forEach(([key, label]) => {
    const field = document.createElement("div");
    field.className = "profile-field";
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    const value = profile[key];
    if (value) {
      dd.textContent = value;
    } else {
      dd.textContent = "N/A";
      dd.className = "empty";
    }
    field.appendChild(dt);
    field.appendChild(dd);
    grid.appendChild(field);
  });

  const mailField = document.createElement("div");
  mailField.className = "profile-field";
  const mailDt = document.createElement("dt");
  mailDt.textContent = "Emails";
  mailField.appendChild(mailDt);
  const mailList = Array.isArray(profile.mail) ? profile.mail : [];
  if (mailList.length === 0) {
    const dd = document.createElement("dd");
    dd.textContent = "N/A";
    dd.className = "empty";
    mailField.appendChild(dd);
  } else {
    const chipList = document.createElement("div");
    chipList.className = "chip-list";
    mailList.forEach((mail) => {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = mail;
      chipList.appendChild(chip);
    });
    mailField.appendChild(chipList);
  }
  grid.appendChild(mailField);

  wrapper.appendChild(grid);
  return wrapper;
}

async function handleEnrichSubmit(event) {
  event.preventDefault();

  const url = document.getElementById("website-url").value.trim();
  const websiteName = document.getElementById("website-name").value.trim();

  if (!url) {
    setStatus(enrichStatus, "Please enter a company URL.", "error");
    return;
  }

  enrichBtn.disabled = true;
  enrichResult.innerHTML = "";
  setStatus(enrichStatus, "Scraping site and generating insights…", "loading");

  try {
    const res = await fetch(`${getApiBase()}/enrich`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, website_name: websiteName }),
    });

    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail.detail || `Request failed with status ${res.status}`);
    }

    const profile = await res.json();
    setStatus(enrichStatus, "Done.", "success");
    enrichResult.appendChild(renderProfileCard(profile));
  } catch (err) {
    setStatus(enrichStatus, err.message || "Something went wrong. Please try again.", "error");
  } finally {
    enrichBtn.disabled = false;
  }
}

async function handleShowResults() {
  resultsBtn.disabled = true;
  setStatus(resultsStatus, "Loading results…", "loading");

  try {
    const res = await fetch(`${getApiBase()}/results`, { method: "GET" });
    if (!res.ok) {
      throw new Error(`Request failed with status ${res.status}`);
    }
    const results = await res.json();
    resultsPanel.innerHTML = "";

    if (!Array.isArray(results) || results.length === 0) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.textContent = "No enriched companies yet. Run Enrich above to add one.";
      resultsPanel.appendChild(empty);
      setStatus(resultsStatus, "", "");
      return;
    }

    results.forEach((profile) => resultsPanel.appendChild(renderProfileCard(profile)));
    setStatus(resultsStatus, `Loaded ${results.length} result${results.length === 1 ? "" : "s"}.`, "success");
  } catch (err) {
    setStatus(resultsStatus, err.message || "Could not load results.", "error");
  } finally {
    resultsBtn.disabled = false;
  }
}

initApiBase();
checkHealth();
enrichForm.addEventListener("submit", handleEnrichSubmit);
resultsBtn.addEventListener("click", handleShowResults);
