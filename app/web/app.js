const byId = (id) => document.getElementById(id);
const fileInput = byId("resume-file");
const dropZone = byId("drop-zone");
const analyzeButton = byId("analyze-button");
const matchButton = byId("match-button");
const toast = byId("toast");
let currentResumeId = null;
let selectedFile = null;
let toastTimer;

function apiHeaders(extra = {}) {
  const token = sessionStorage.getItem("sift-access-token");
  return { ...extra, ...(token ? { Authorization: `Bearer ${token}` } : {}) };
}

async function request(url, options = {}) {
  const response = await fetch(url, { ...options, headers: apiHeaders(options.headers || {}) });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) openAccessPanel();
    throw new Error(payload?.error?.message || "The request could not be completed.");
  }
  return payload;
}

function notify(message, isError = false) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("visible");
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 3600);
}

function setBusy(button, busy, busyText, idleText) {
  button.disabled = busy || (button === analyzeButton ? !selectedFile : !currentResumeId || !byId("job-description").value.trim());
  const label = button.querySelector("span:first-child");
  if (label) label.textContent = busy ? busyText : idleText;
}

function readableSize(bytes) {
  return bytes < 1024 * 1024 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function useFile(file) {
  if (!file) return;
  const extension = file.name.split(".").pop().toLowerCase();
  if (!["pdf", "docx"].includes(extension)) {
    notify("Choose a PDF or DOCX file.", true);
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    notify("This file is over the 5 MB limit.", true);
    return;
  }
  selectedFile = file;
  currentResumeId = null;
  byId("file-type").textContent = extension.toUpperCase();
  byId("file-name").textContent = file.name;
  byId("file-meta").textContent = `${readableSize(file.size)} · Ready to review`;
  byId("file-row").hidden = false;
  byId("upload-message").textContent = "";
  byId("readout-results").hidden = true;
  byId("readout-empty").hidden = false;
  byId("match-result").hidden = true;
  analyzeButton.disabled = false;
}

function createTextElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function fillList(target, values, emptyText) {
  target.replaceChildren();
  const entries = values?.length ? values.slice(0, 4) : [emptyText];
  for (const value of entries) target.append(createTextElement("li", "", value));
}

function renderAnalysis(response) {
  const result = response.analysis;
  const score = Math.max(0, Math.min(100, Number(result.ats_score) || 0));
  const candidate = result.candidate || {};
  const skills = Array.isArray(result.skills) ? result.skills : [];
  const sections = result.sections && typeof result.sections === "object" ? Object.keys(result.sections) : [];
  const scoreDisc = byId("score-disc");
  scoreDisc.style.setProperty("--score", score);
  scoreDisc.setAttribute("aria-label", `ATS score ${score} out of 100`);
  byId("ats-score").textContent = String(score);
  byId("score-caption-value").textContent = `${score} / 100`;
  byId("score-track-fill").style.width = `${score}%`;
  byId("candidate-name").textContent = candidate.name || "Candidate profile";
  byId("candidate-summary").textContent = candidate.summary || "A structured read of the experience in this document.";
  byId("experience-years").textContent = `${Number(result.experience_years) || 0} yrs`;
  byId("skill-count").textContent = String(skills.length);
  byId("section-count").textContent = String(sections.length);
  byId("analysis-source").textContent = response.source === "stored" ? "SAVED REVIEW" : "STRUCTURED REVIEW";
  byId("candidate-contact").textContent = [candidate.email, candidate.phone].filter(Boolean).join(" · ");

  const skillList = byId("skill-list");
  skillList.replaceChildren();
  for (const skill of skills.slice(0, 18)) skillList.append(createTextElement("span", "", skill));
  if (!skills.length) skillList.append(createTextElement("span", "", "No skills identified"));
  fillList(byId("strength-list"), result.strengths, "No strengths returned");
  fillList(byId("improvement-list"), result.improvements, "No suggestions returned");
  byId("readout-empty").hidden = true;
  byId("readout-results").hidden = false;
  matchButton.disabled = !byId("job-description").value.trim();
}

async function analyzeSelectedResume() {
  if (!selectedFile) return;
  setBusy(analyzeButton, true, "Reading the document…", "Review resume");
  byId("upload-message").textContent = "The document is being read and reviewed.";
  try {
    const body = new FormData();
    body.append("file", selectedFile);
    const uploaded = await request("/api/v1/resumes/upload", { method: "POST", body });
    currentResumeId = uploaded.resume.id;
    byId("file-meta").textContent = `${readableSize(selectedFile.size)} · Document ready`;
    const result = await request(`/api/v1/analysis/${encodeURIComponent(currentResumeId)}`, { method: "POST" });
    renderAnalysis(result);
    byId("upload-message").textContent = "Review complete.";
    notify("Your resume review is ready.");
    byId("readout").scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    byId("upload-message").textContent = error.message;
    notify(error.message, true);
  } finally {
    setBusy(analyzeButton, false, "Reading the document…", "Review resume");
  }
}

async function compareRole() {
  const jobDescription = byId("job-description").value.trim();
  if (!currentResumeId || !jobDescription) return;
  setBusy(matchButton, true, "Comparing…", "Compare role");
  byId("match-message").textContent = "";
  try {
    const result = await request("/api/v1/job-match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_id: currentResumeId, job_description: jobDescription }),
    });
    renderMatch(result);
  } catch (error) {
    byId("match-message").textContent = error.message;
    notify(error.message, true);
  } finally {
    setBusy(matchButton, false, "Comparing…", "Compare role");
  }
}

function renderMatch(result) {
  const container = byId("match-result");
  container.replaceChildren();
  const heading = document.createElement("div");
  heading.className = "match-result-head";
  heading.append(createTextElement("strong", "", `${result.match_score}%`), createTextElement("span", "", "LANGUAGE MATCH"));
  container.append(heading);
  container.append(createTextElement("div", "match-keywords-label", "PRESENT IN YOUR RESUME"));
  const matched = document.createElement("div");
  matched.className = "match-tags";
  for (const word of (result.matched_keywords || []).slice(0, 12)) matched.append(createTextElement("span", "", word));
  if (!matched.childElementCount) matched.append(createTextElement("span", "", "No direct matches"));
  container.append(matched);
  container.append(createTextElement("div", "match-keywords-label", "NOT YET EVIDENT"));
  const missing = document.createElement("div");
  missing.className = "match-tags";
  for (const word of (result.missing_keywords || []).slice(0, 12)) missing.append(createTextElement("span", "missing", word));
  if (!missing.childElementCount) missing.append(createTextElement("span", "", "Core language covered"));
  container.append(missing);
  container.hidden = false;
  byId("match-message").textContent = "Comparison saved.";
  notify("Role comparison is ready.");
}

function openAccessPanel() {
  const panel = byId("access-form");
  panel.hidden = false;
  byId("access-toggle").setAttribute("aria-expanded", "true");
  byId("access-token").focus();
  notify("This server needs an access token. Enter it in the sidebar.", true);
}

dropZone.addEventListener("click", (event) => {
  if (event.target.closest("button")) return;
  fileInput.click();
});
dropZone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") { event.preventDefault(); fileInput.click(); }
});
fileInput.addEventListener("change", () => useFile(fileInput.files?.[0]));
dropZone.addEventListener("dragover", (event) => { event.preventDefault(); dropZone.classList.add("dragging"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
  useFile(event.dataTransfer?.files?.[0]);
});
analyzeButton.addEventListener("click", analyzeSelectedResume);
matchButton.addEventListener("click", compareRole);
byId("remove-file").addEventListener("click", () => {
  selectedFile = null;
  currentResumeId = null;
  fileInput.value = "";
  byId("file-row").hidden = true;
  byId("readout-results").hidden = true;
  byId("readout-empty").hidden = false;
  byId("match-result").hidden = true;
  analyzeButton.disabled = true;
  matchButton.disabled = true;
});
byId("job-description").addEventListener("input", (event) => {
  byId("job-counter").textContent = `${event.target.value.length.toLocaleString()} / 30,000`;
  matchButton.disabled = !currentResumeId || !event.target.value.trim();
});
byId("access-toggle").addEventListener("click", () => {
  const panel = byId("access-form");
  panel.hidden = !panel.hidden;
  byId("access-toggle").setAttribute("aria-expanded", String(!panel.hidden));
  if (!panel.hidden) byId("access-token").focus();
});
byId("access-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const token = byId("access-token").value.trim();
  if (token.length < 32) {
    notify("The access token must contain at least 32 characters.", true);
    return;
  }
  sessionStorage.setItem("sift-access-token", token);
  byId("access-token").value = "";
  byId("access-form").hidden = true;
  byId("access-toggle").setAttribute("aria-expanded", "false");
  notify("Access key saved for this browser session.");
});
byId("forget-token").addEventListener("click", () => {
  sessionStorage.removeItem("sift-access-token");
  byId("access-token").value = "";
  notify("This session's access key was removed.");
});

document.querySelectorAll(".nav-link").forEach((link) => link.addEventListener("click", () => {
  document.querySelectorAll(".nav-link").forEach((item) => item.classList.toggle("active", item === link));
}));