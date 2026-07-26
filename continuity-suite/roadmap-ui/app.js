"use strict";

const state = { token: "", data: null, view: "timeline" };

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = String(text);
  return node;
}

function list(value) { return Array.isArray(value) ? value : []; }

function badge(text, kind = "") {
  return el("span", `badge ${kind}`.trim(), text);
}

function statusKind(item) {
  if (item.status === "blocked" || item.health === "blocked" || item.health === "off-track") return "block";
  if (item.status === "at-risk" || item.health === "at-risk") return "warn";
  return "";
}

function card(item) {
  const node = el("button", "card");
  node.type = "button";
  node.append(el("div", "eyebrow", item.kind || "record"), el("h3", "", item.title || item.roadmap_id), el("p", "", item.summary || "No summary"));
  const badges = el("div", "badges");
  badges.append(badge(item.status || "unknown", statusKind(item)), badge(item.health || "unknown", statusKind(item)));
  node.append(badges);
  node.addEventListener("click", () => showDetail(item));
  return node;
}

function sectionTitle(title, detail) {
  const node = el("div", "section-title");
  node.append(el("h2", "", title), el("span", "", detail));
  return node;
}

function renderTimeline(items, canvas) {
  canvas.append(sectionTitle("Delivery timeline", "committed roadmap records"));
  const sorted = [...items].sort((a, b) => String(a.target_date || "9999").localeCompare(String(b.target_date || "9999")));
  for (const item of sorted) {
    const row = el("div", "timeline-row");
    row.append(el("div", "timeline-date", item.target_date || "Unscheduled"));
    const track = el("div", "timeline-track"); track.append(card(item)); row.append(track); canvas.append(row);
  }
}

function renderLanes(items, canvas, field, order) {
  for (const value of order) {
    const matching = items.filter((item) => (item[field] || "unassigned") === value || (value === "unassigned" && !item[field]));
    if (!matching.length) continue;
    const lane = el("section", "lane"); lane.append(el("h3", "", `${value} · ${matching.length}`));
    const grid = el("div", "grid"); matching.forEach((item) => grid.append(card(item))); lane.append(grid); canvas.append(lane);
  }
}

function renderHierarchy(items, canvas) {
  canvas.append(sectionTitle("Programs and initiatives", "strategic hierarchy"));
  renderLanes(items, canvas, "kind", ["program", "initiative", "release", "milestone", "epic", "story", "bug", "spike", "chore", "sprint"]);
}

function renderBoard(items, canvas) {
  canvas.append(sectionTitle("Backlog board", "hybrid Kanban flow"));
  renderLanes(items, canvas, "status", ["inbox", "triaged", "ready", "planned", "in-progress", "validating", "blocked", "done", "completed", "cancelled"]);
}

function renderDependencies(items, canvas) {
  canvas.append(sectionTitle("Dependency graph", "upstream relationships"));
  const graph = items.filter((item) => list(item.depends_on).length || list(item.parent_ids).length);
  const grid = el("div", "grid");
  for (const item of graph) {
    const node = card(item); const meta = el("div", "meta");
    list(item.depends_on).forEach((value) => meta.append(badge(`depends: ${value}`, "warn")));
    list(item.parent_ids).forEach((value) => meta.append(badge(`parent: ${value}`)));
    node.append(meta); grid.append(node);
  }
  canvas.append(grid);
}

function renderSprints(items, canvas) {
  canvas.append(sectionTitle("Sprint context", "optional planning cadence"));
  const sprints = items.filter((item) => item.kind === "sprint");
  for (const sprint of sprints) {
    const lane = el("section", "lane"); lane.append(el("h3", "", sprint.title));
    const children = items.filter((item) => list(item.sprint_ids).includes(sprint.roadmap_id));
    const grid = el("div", "grid"); grid.append(card(sprint)); children.forEach((item) => grid.append(card(item))); lane.append(grid); canvas.append(lane);
  }
}

function renderRisks(items, canvas) {
  canvas.append(sectionTitle("Risks and blockers", "delivery attention"));
  const risks = items.filter((item) => list(item.risks).length || ["blocked", "at-risk"].includes(item.status) || ["blocked", "at-risk", "off-track"].includes(item.health));
  const grid = el("div", "grid"); risks.forEach((item) => grid.append(card(item))); canvas.append(grid);
}

function showDetail(item) {
  const detail = document.querySelector("#detail"); detail.replaceChildren();
  detail.append(el("p", "eyebrow", `${item.kind || "record"} · ${item.visibility || "committed"}`), el("h2", "", item.title || item.roadmap_id), el("p", "", item.summary || "No summary recorded."));
  const terms = [
    ["ID", item.roadmap_id], ["Status", item.status], ["Health", item.health || "unknown"], ["Target", item.target_date || "unscheduled"],
    ["Parents", list(item.parent_ids).join(", ") || "none"], ["Depends on", list(item.depends_on).join(", ") || "none"],
    ["Memory", list(item.memory_ids).join(", ") || "none"], ["Notes", list(item.note_ids).join(", ") || "private links not shown"], ["Goals", list(item.goals).join(", ") || "none"], ["Evidence", list(item.evidence).join(", ") || "none"]
  ];
  const dl = el("dl");
  for (const [term, value] of terms) { dl.append(el("dt", "", term), el("dd", "", value)); }
  detail.append(dl);
  const source = el("button", "path", item.path || "Source unavailable"); source.type = "button"; source.disabled = !item.path;
  source.addEventListener("click", async () => {
    const response = await fetch(`/api/v1/source/${encodeURIComponent(item.roadmap_id)}`, { headers: { Authorization: `Bearer ${state.token}` }, cache: "no-store", credentials: "same-origin" });
    if (!response.ok) return;
    const payload = await response.json(); const pre = el("pre", "source-view", payload.content); detail.append(pre); source.disabled = true;
  });
  detail.append(el("p", "eyebrow", "Canonical Markdown"), source);
}

function render() {
  const canvas = document.querySelector("#canvas"); canvas.replaceChildren();
  const committed = state.data.entities || [];
  const inbox = state.data.roadmap_inbox || [];
  const items = state.view === "board" ? [...inbox, ...committed] : committed;
  if (!items.length) {
    const detail = state.view === "board" ? "no committed records or triaged candidates" : "no committed records";
    canvas.append(sectionTitle("Project roadmap", detail), el("p", "empty", "Use /goal to capture, triage, and place actionable work in the roadmap inbox."));
    return;
  }
  const renderers = { timeline: renderTimeline, hierarchy: renderHierarchy, board: renderBoard, dependencies: renderDependencies, sprints: renderSprints, risks: renderRisks };
  renderers[state.view](items, canvas);
}

async function start() {
  const params = new URLSearchParams(window.location.hash.slice(1)); state.token = params.get("token") || "";
  history.replaceState(null, "", `${location.pathname}${location.search}`);
  if (!state.token) throw new Error("Missing short-lived access token");
  const requestedView = new URLSearchParams(location.search).get("view");
  if (["timeline", "hierarchy", "board", "dependencies", "sprints", "risks"].includes(requestedView)) state.view = requestedView;
  const response = await fetch("/api/v1/roadmap", { headers: { Authorization: `Bearer ${state.token}` }, cache: "no-store", credentials: "same-origin" });
  if (!response.ok) throw new Error(`Roadmap authorization failed (${response.status})`);
  state.data = await response.json();
  document.querySelector("#project-name").textContent = state.data.project_id || "Local project";
  const committed = state.data.entities || [];
  const inbox = state.data.roadmap_inbox || [];
  if (state.view === "timeline" && !committed.length && inbox.length) state.view = "board";
  const items = [...inbox, ...committed]; document.querySelector("#entity-count").textContent = items.length;
  document.querySelector("#active-count").textContent = items.filter((item) => ["active", "in-progress", "validating", "planned", "triaged"].includes(item.status)).length;
  document.querySelector("#risk-count").textContent = items.filter((item) => list(item.risks).length || ["blocked", "at-risk"].includes(item.status) || ["blocked", "at-risk", "off-track"].includes(item.health)).length;
  document.querySelectorAll("[data-view]").forEach((button) => { if (button.dataset.view === state.view) button.classList.add("active"); else button.classList.remove("active"); button.addEventListener("click", () => { document.querySelectorAll("[data-view]").forEach((candidate) => candidate.classList.remove("active")); button.classList.add("active"); state.view = button.dataset.view; render(); }); });
  render();
  const requestedEntity = new URLSearchParams(location.search).get("entity");
  const detail = items.find((item) => item.roadmap_id === requestedEntity);
  if (detail) showDetail(detail);
}

start().catch((error) => { const canvas = document.querySelector("#canvas"); canvas.replaceChildren(el("h2", "", "Roadmap unavailable"), el("p", "empty", error.message)); });
