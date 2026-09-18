"use strict";

const NEWS_URL = "news.json";
const PAGE_SIZE = 10;
const state = { all: [], filtered: [], category: "all", status: "all", query: "", visible: PAGE_SIZE };
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function text(value) { return String(value ?? ""); }
function escapeHTML(value) {
  return text(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", "\"": "&quot;" }[character]));
}
function normalizeNews(payload) {
  const rows = Array.isArray(payload) ? payload : (payload?.news || payload?.items || payload?.data || []);
  return Array.isArray(rows) ? rows.filter((item) => item && typeof item === "object") : [];
}
function dateOf(item) { return item.published || item.published_at || item.discovered || item.created_at || item.date; }
function formatDate(value) {
  if (!value) return "منذ قليل";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? text(value) : new Intl.DateTimeFormat("ar-MA", { dateStyle: "medium", timeStyle: "short" }).format(date);
}
function categoryOf(item) { return item.category || item.category_name || ""; }
function statusOf(item) { return item.status || item.verdict || "غير واضح"; }
function sourceOf(item) { return item.source || item.source_name || "مصدر غير معروف"; }
function titleOf(item) { return item.title || item.headline || "بدون عنوان"; }
function summaryOf(item) { return item.summary || item.description || item.excerpt || ""; }
function playerOf(item) { return item.player || item.player_name || ""; }
function urlOf(item) {
  const raw = item.url || item.link || "";
  try {
    const parsed = new URL(raw, window.location.href);
    return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : "";
  } catch { return ""; }
}
function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = value; }

async function loadNews(showToast = false) {
  $("#refreshBtn").classList.add("is-spinning");
  try {
    const response = await fetch(`${NEWS_URL}?t=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.all = normalizeNews(await response.json()).sort((a, b) => new Date(dateOf(b) || 0) - new Date(dateOf(a) || 0));
    updateStats(); updateHero(); updateBreaking(); updateSources(); updatePlayers(); applyFilters();
    if (showToast) toast("تم تحديث الأخبار");
  } catch (error) {
    console.error("Could not load docs/news.json", error);
    state.all = []; state.filtered = [];
    updateStats(); updateHero(); updateBreaking(); updateSources(); updatePlayers(); renderNews();
    showEmpty("تعذر تحميل ملف الأخبار", "تحقق من وجود docs/news.json ومن تشغيل الموقع عبر خادم ويب أو GitHub Pages.");
  } finally { $("#refreshBtn").classList.remove("is-spinning"); setText("lastUpdate", new Intl.DateTimeFormat("ar-MA", { hour: "2-digit", minute: "2-digit" }).format(new Date())); }
}
function applyFilters() {
  const query = state.query.toLocaleLowerCase("ar");
  state.filtered = state.all.filter((item) => {
    const searchable = [titleOf(item), summaryOf(item), sourceOf(item), playerOf(item), categoryOf(item), statusOf(item)].join(" ").toLocaleLowerCase("ar");
    return (state.category === "all" || categoryOf(item) === state.category) && (state.status === "all" || statusOf(item) === state.status) && (!query || searchable.includes(query));
  });
  state.visible = PAGE_SIZE; renderNews();
}
function renderNews() {
  const grid = $("#newsGrid"); const shown = state.filtered.slice(0, state.visible);
  grid.innerHTML = shown.map(cardTemplate).join("");
  $("#loadMore").hidden = state.visible >= state.filtered.length || !state.filtered.length;
  if (state.filtered.length) $("#emptyState").classList.add("is-hidden");
  else showEmpty("لم يتم العثور على أخبار", "جرّب تغيير كلمة البحث أو القسم.");
}
function cardTemplate(item) {
  const status = statusOf(item); const statusClass = status === "رسمي" ? "official" : status === "إشاعة" ? "rumor" : ""; const url = urlOf(item);
  return `<article class="news-card"><div class="news-top"><span class="news-source">${escapeHTML(sourceOf(item))}</span><span class="news-status ${statusClass}">${escapeHTML(status)}</span></div><h3>${escapeHTML(titleOf(item))}</h3>${playerOf(item) ? `<p class="news-player">⚽ ${escapeHTML(playerOf(item))}</p>` : ""}<p class="news-summary">${escapeHTML(summaryOf(item))}</p><div class="news-footer"><span class="news-time">${escapeHTML(formatDate(dateOf(item)))}</span>${url ? `<a class="news-link" href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">قراءة الخبر ←</a>` : ""}</div></article>`;
}
function updateHero() {
  const item = state.all[0];
  setText("heroSource", item ? sourceOf(item) : "--"); setText("heroTime", item ? formatDate(dateOf(item)) : "--"); setText("heroTitle", item ? titleOf(item) : "لا توجد أخبار لعرضها"); setText("heroSummary", item ? summaryOf(item) || "آخر المستجدات من مصادر الأخبار المغربية." : "سيظهر الخبر الرئيسي هنا عند توفر بيانات في news.json.");
  const link = $("#heroLink"); link.hidden = !item || !urlOf(item); link.href = item ? urlOf(item) || "#" : "#";
}
function updateBreaking() { const item = state.all.find((news) => ["رسمي", "مؤكد"].includes(statusOf(news))) || state.all[0]; setText("breakingNews", item ? titleOf(item) : "لا توجد أخبار جديدة حاليًا"); }
function updateSources() {
  const counts = countBy(state.all, sourceOf); const rows = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0,8);
  $("#sourcesList").innerHTML = rows.length ? rows.map(([name, count]) => `<div class="source-item"><div class="source-name"><b class="source-logo">${escapeHTML(name.trim().slice(0,2))}</b><span>${escapeHTML(name)}</span></div><span class="source-count">${count}</span></div>`).join("") : `<p class="muted">لا توجد مصادر بعد.</p>`;
}
function updatePlayers() {
  const counts = countBy(state.all.filter((item) => playerOf(item)), playerOf); const rows = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0,6);
  $("#playersList").innerHTML = rows.length ? rows.map(([name,count]) => `<div class="player-item"><b class="player-avatar">${escapeHTML(name.trim().slice(0,2))}</b><span class="player-info"><strong>${escapeHTML(name)}</strong><span>${count} خبر</span></span></div>`).join("") : `<p class="muted">لا توجد تحديثات للاعبين حاليًا.</p>`;
}
function countBy(items, selector) { return items.reduce((counts, item) => { const key = selector(item); counts[key] = (counts[key] || 0) + 1; return counts; }, {}); }
function updateStats() {
  const count = (predicate) => state.all.filter(predicate).length;
  setText("countAll", state.all.length); setText("countMorocco", count((i) => categoryOf(i) === "أخبار المغرب")); setText("countSport", count((i) => categoryOf(i) === "رياضة")); setText("countTransfers", count((i) => categoryOf(i) === "انتقالات اللاعبين"));
  setText("statusOfficial", count((i) => statusOf(i) === "رسمي")); setText("statusConfirmed", count((i) => statusOf(i) === "مؤكد")); setText("statusNegotiation", count((i) => statusOf(i) === "مفاوضات")); setText("statusRumor", count((i) => statusOf(i) === "إشاعة")); setText("totalNews", state.all.length); setText("sourceCount", Object.keys(countBy(state.all, sourceOf)).length);
}
function showEmpty(title, description) { const empty = $("#emptyState"); empty.classList.remove("is-hidden"); empty.querySelector("h2").textContent = title; empty.querySelector("p").textContent = description; }
function toast(message) { const element = $("#toast"); element.textContent = message; element.classList.add("show"); clearTimeout(toast.timer); toast.timer = setTimeout(() => element.classList.remove("show"), 2500); }
function setCategory(category) { state.category = category; $$('[data-category]').forEach((button) => button.classList.toggle("is-active", button.dataset.category === category)); applyFilters(); $("#mobileMenu").classList.remove("open"); }

$$('[data-category]').forEach((button) => button.addEventListener("click", () => setCategory(button.dataset.category)));
$$('.feed-filter').forEach((button) => button.addEventListener("click", () => { state.status = button.dataset.status; $$('.feed-filter').forEach((item) => item.classList.toggle("is-active", item === button)); applyFilters(); }));
$("#searchInput").addEventListener("input", (event) => { state.query = event.target.value.trim(); applyFilters(); });
$("#clearSearch").addEventListener("click", () => { $("#searchInput").value = ""; state.query = ""; applyFilters(); });
$("#loadMore").addEventListener("click", () => { state.visible += PAGE_SIZE; renderNews(); });
$("#refreshBtn").addEventListener("click", () => loadNews(true));
$("#themeBtn").addEventListener("click", () => { document.body.classList.toggle("light-mode"); $("#themeBtn").textContent = document.body.classList.contains("light-mode") ? "☀" : "☾"; });
$("#menuBtn").addEventListener("click", () => $("#mobileMenu").classList.add("open")); $("#closeMenu").addEventListener("click", () => $("#mobileMenu").classList.remove("open"));
setText("footerYear", new Date().getFullYear()); loadNews();
