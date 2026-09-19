const NEWS_URL = "news.json";

let allNews = [];
let filteredNews = [];

let currentCategory = "all";
let currentStatus = "all";
let searchTerm = "";
let visibleCount = 10;

const CATEGORY_LABELS = {
    all: "كل الأخبار",
    morocco: "أخبار المغرب",
    sports: "الرياضة",
    transfers: "انتقالات اللاعبين",
    middle_east: "الشرق الأوسط",
    world_arabic: "العالم"
};


/* =========================
   HELPERS
========================= */

function get(id) {
    return document.getElementById(id);
}


function escapeHTML(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatDate(value) {
    if (!value) {
        return "غير معروف";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat("ar-MA", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    }).format(date);
}


/* =========================
   CATEGORY
========================= */

function normalizeCategory(value) {
    if (!value) {
        return "";
    }

    const text = String(value)
        .trim()
        .toLowerCase();

    if (
        text === "morocco" ||
        text.includes("أخبار المغرب") ||
        text.includes("اخبار المغرب") ||
        text === "morocco_news"
    ) {
        return "morocco";
    }

    if (
        text === "sports" ||
        text.includes("الرياضة") ||
        text.includes("رياضة") ||
        text === "sport"
    ) {
        return "sports";
    }

    if (
        text === "transfers" ||
        text.includes("انتقالات") ||
        text.includes("transfer")
    ) {
        return "transfers";
    }

    if (
        text === "middle_east" ||
        text.includes("الشرق الأوسط") ||
        text.includes("الشرق الاوسط")
    ) {
        return "middle_east";
    }

    if (
        text === "world_arabic" ||
        text.includes("العالم")
    ) {
        return "world_arabic";
    }

    return text;
}


function getNewsCategory(item) {
    if (!item) {
        return "";
    }

    if (item.section) {
        return normalizeCategory(item.section);
    }

    if (item.category) {
        return normalizeCategory(item.category);
    }

    if (item.source_group) {
        return normalizeCategory(item.source_group);
    }

    return "";
}


function categoryLabel(category) {
    return (
        CATEGORY_LABELS[category] ||
        category ||
        "أخبار"
    );
}


/* =========================
   NORMALIZE NEWS
========================= */

function normalizeNews(data) {
    if (!data) {
        return [];
    }

    let result = [];

    /*
     * Case 1:
     * news.json is directly an array
     */
    if (Array.isArray(data)) {
        result = data;
    }

    /*
     * Case 2:
     * export_news.py creates:
     *
     * {
     *   "updated": "...",
     *   "total": 91,
     *   "sections": {
     *      "morocco": [],
     *      "sports": [],
     *      ...
     *   }
     * }
     */
    else if (
        data.sections &&
        typeof data.sections === "object"
    ) {
        Object.entries(data.sections).forEach(
            ([section, items]) => {

                if (!Array.isArray(items)) {
                    return;
                }

                items.forEach(item => {

                    if (!item || typeof item !== "object") {
                        return;
                    }

                    result.push({
                        ...item,
                        section: normalizeCategory(section)
                    });
                });
            }
        );
    }

    /*
     * Case 3:
     * Alternative format:
     *
     * {
     *   "news": []
     * }
     */
    else if (Array.isArray(data.news)) {
        result = data.news;
    }

    /*
     * Case 4:
     * Alternative format:
     *
     * {
     *   "items": []
     * }
     */
    else if (Array.isArray(data.items)) {
        result = data.items;
    }

    return result;
}


/* =========================
   FILTERING
========================= */

function matchesCategory(item) {
    if (currentCategory === "all") {
        return true;
    }

    return (
        getNewsCategory(item) ===
        currentCategory
    );
}


function matchesStatus(item) {
    if (currentStatus === "all") {
        return true;
    }

    return (
        String(item.status || "").trim() ===
        currentStatus
    );
}


function matchesSearch(item) {
    if (!searchTerm) {
        return true;
    }

    const text = [
        item.title,
        item.summary,
        item.source,
        item.player,
        item.category,
        item.status
    ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

    return text.includes(
        searchTerm.toLowerCase()
    );
}


function applyFilters() {
    filteredNews = allNews.filter(item => {
        return (
            matchesCategory(item) &&
            matchesStatus(item) &&
            matchesSearch(item)
        );
    });

    visibleCount = 10;

    renderNews();
}


/* =========================
   HERO
========================= */

function renderHero() {
    if (!allNews.length) {
        return;
    }

    const item = allNews[0];

    const title =
        item.title ||
        "آخر الأخبار المغربية";

    const summary =
        item.summary ||
        "آخر الأخبار من مصادر متعددة.";

    const source =
        item.source ||
        "مصدر غير معروف";

    const date =
        item.published ||
        item.discovered;

    const url =
        item.url ||
        "#";

    if (get("heroSource")) {
        get("heroSource").textContent =
            source;
    }

    if (get("heroTime")) {
        get("heroTime").textContent =
            formatDate(date);
    }

    if (get("heroTitle")) {
        get("heroTitle").textContent =
            title;
    }

    if (get("heroSummary")) {
        get("heroSummary").textContent =
            summary;
    }

    if (get("heroLink")) {
        get("heroLink").href = url;
    }
}


/* =========================
   NEWS CARDS
========================= */

function renderNews() {
    const container =
        get("newsGrid");

    if (!container) {
        return;
    }

    const items =
        filteredNews.slice(
            0,
            visibleCount
        );

    if (!items.length) {
        container.innerHTML = `
            <div class="empty-state">
                لا توجد أخبار مطابقة.
            </div>
        `;

        updateLoadMore();

        return;
    }

    container.innerHTML =
        items
            .map(renderCard)
            .join("");

    updateLoadMore();
}


function renderCard(item) {
    const title =
        item.title ||
        "بدون عنوان";

    const summary =
        item.summary ||
        "لا يوجد ملخص متاح.";

    const source =
        item.source ||
        "مصدر غير معروف";

    const status =
        item.status ||
        "غير واضح";

    const category =
        categoryLabel(
            getNewsCategory(item)
        );

    const date =
        formatDate(
            item.published ||
            item.discovered
        );

    const url =
        item.url ||
        "#";

    return `
        <article class="news-card">

            <div class="news-card-top">

                <span class="news-category">
                    ${escapeHTML(category)}
                </span>

                <span class="news-status">
                    ${escapeHTML(status)}
                </span>

            </div>

            <h3>
                <a
                    href="${escapeHTML(url)}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    ${escapeHTML(title)}
                </a>
            </h3>

            <p>
                ${escapeHTML(summary)}
            </p>

            <div class="news-card-footer">

                <span>
                    ${escapeHTML(source)}
                </span>

                <span>
                    ${escapeHTML(date)}
                </span>

            </div>

        </article>
    `;
}


/* =========================
   COUNTS
========================= */

function renderCounts() {
    const countAll =
        get("countAll");

    const countMorocco =
        get("countMorocco");

    const countSport =
        get("countSport");

    const countTransfers =
        get("countTransfers");

    if (countAll) {
        countAll.textContent =
            allNews.length;
    }

    if (countMorocco) {
        countMorocco.textContent =
            allNews.filter(
                item =>
                    getNewsCategory(item) ===
                    "morocco"
            ).length;
    }

    if (countSport) {
        countSport.textContent =
            allNews.filter(
                item =>
                    getNewsCategory(item) ===
                    "sports"
            ).length;
    }

    if (countTransfers) {
        countTransfers.textContent =
            allNews.filter(
                item =>
                    getNewsCategory(item) ===
                    "transfers"
            ).length;
    }
}


/* =========================
   STATUS COUNTS
========================= */

function renderStatusCounts() {
    const official =
        get("statusOfficial");

    const confirmed =
        get("statusConfirmed");

    const negotiation =
        get("statusNegotiation");

    const rumor =
        get("statusRumor");

    const countStatus = status => {
        return allNews.filter(
            item =>
                String(
                    item.status || ""
                ).trim() === status
        ).length;
    };

    if (official) {
        official.textContent =
            countStatus("رسمي");
    }

    if (confirmed) {
        confirmed.textContent =
            countStatus("مؤكد");
    }

    if (negotiation) {
        negotiation.textContent =
            countStatus("مفاوضات");
    }

    if (rumor) {
        rumor.textContent =
            countStatus("إشاعة");
    }
}


/* =========================
   SOURCES
========================= */

function renderSources() {
    const container =
        get("sourcesList");

    if (!container) {
        return;
    }

    const sources = {};

    allNews.forEach(item => {

        const source =
            item.source ||
            "مصدر غير معروف";

        sources[source] =
            (sources[source] || 0) + 1;
    });

    const sorted =
        Object.entries(sources)
            .sort(
                (a, b) =>
                    b[1] - a[1]
            )
            .slice(0, 10);

    if (!sorted.length) {
        container.innerHTML =
            "<p>لا توجد مصادر بعد.</p>";

        return;
    }

    container.innerHTML =
        sorted
            .map(
                ([source, count]) => `
                    <div class="source-row">
                        <span>
                            ${escapeHTML(source)}
                        </span>
                        <strong>
                            ${count}
                        </strong>
                    </div>
                `
            )
            .join("");
}


/* =========================
   PLAYERS
========================= */

function renderPlayers() {
    const container =
        get("playerList");

    if (!container) {
        return;
    }

    const players = {};

    allNews.forEach(item => {

        const player =
            String(
                item.player || ""
            ).trim();

        if (!player) {
            return;
        }

        players[player] =
            (players[player] || 0) + 1;
    });

    const sorted =
        Object.entries(players)
            .sort(
                (a, b) =>
                    b[1] - a[1]
            )
            .slice(0, 10);

    if (!sorted.length) {
        container.innerHTML =
            "<p>لا توجد أخبار لاعبين بعد.</p>";

        return;
    }

    container.innerHTML =
        sorted
            .map(
                ([player, count]) => `
                    <div class="player-row">
                        <span>
                            ${escapeHTML(player)}
                        </span>
                        <strong>
                            ${count}
                        </strong>
                    </div>
                `
            )
            .join("");
}


/* =========================
   LOAD MORE
========================= */

function updateLoadMore() {
    const button =
        get("loadMore");

    if (!button) {
        return;
    }

    if (
        visibleCount >=
        filteredNews.length
    ) {
        button.style.display =
            "none";
    } else {
        button.style.display =
            "";
    }
}


function setupLoadMore() {
    const button =
        get("loadMore");

    if (!button) {
        return;
    }

    button.addEventListener(
        "click",
        () => {

            visibleCount += 10;

            renderNews();
        }
    );
}


/* =========================
   CATEGORY BUTTONS
========================= */

function setupCategoryButtons() {
    const buttons =
        document.querySelectorAll(
            ".category-item"
        );

    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                currentCategory =
                    normalizeCategory(
                        button.dataset.category
                    ) || "all";

                buttons.forEach(btn =>
                    btn.classList.remove(
                        "active"
                    )
                );

                button.classList.add(
                    "active"
                );

                applyFilters();
            }
        );
    });
}


/* =========================
   STATUS BUTTONS
========================= */

function setupStatusButtons() {
    const buttons =
        document.querySelectorAll(
            ".feed-filter"
        );

    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                currentStatus =
                    button.dataset.status ||
                    "all";

                buttons.forEach(btn =>
                    btn.classList.remove(
                        "active"
                    )
                );

                button.classList.add(
                    "active"
                );

                applyFilters();
            }
        );
    });
}


/* =========================
   SEARCH
========================= */

function setupSearch() {
    const inputs =
        document.querySelectorAll(
            'input[type="search"]'
        );

    inputs.forEach(input => {

        input.addEventListener(
            "input",
            event => {

                searchTerm =
                    event.target.value.trim();

                applyFilters();
            }
        );
    });
}


/* =========================
   REFRESH
========================= */

function setupRefresh() {
    const buttons =
        document.querySelectorAll(
            "[data-action='refresh'], .refresh-button"
        );

    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {
                loadNews(true);
            }
        );
    });
}


/* =========================
   LAST UPDATE
========================= */

function updateLastUpdate(data) {
    const element =
        get("lastUpdate") ||
        get("last-update");

    if (!element) {
        return;
    }

    const value =
        data &&
        data.updated
            ? data.updated
            : new Date().toISOString();

    element.textContent =
        formatDate(value);
}


/* =========================
   LOADING
========================= */

function showLoading() {
    const container =
        get("newsGrid");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="loading">
            جار تحميل الأخبار...
        </div>
    `;
}


function showError() {
    const container =
        get("newsGrid");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="error-state">
            تعذر تحميل الأخبار.
            حاول تحديث الصفحة.
        </div>
    `;
}


/* =========================
   LOAD NEWS
========================= */

async function loadNews(forceRefresh = false) {

    showLoading();

    try {

        const url =
            `${NEWS_URL}?v=${Date.now()}`;

        const response =
            await fetch(
                url,
                {
                    cache: "no-store"
                }
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        allNews =
            normalizeNews(data);

        if (!allNews.length) {
            throw new Error(
                "No news items found"
            );
        }

        /*
         * news.json is already sorted
         * by export_news.py.
         */
        filteredNews =
            [...allNews];

        renderHero();
        renderCounts();
        renderStatusCounts();
        renderSources();
        renderPlayers();
        updateLastUpdate(data);

        applyFilters();

        console.log(
            `Loaded ${allNews.length} news items`
        );

    } catch (error) {

        console.error(
            "News loading error:",
            error
        );

        showError();
    }
}


/* =========================
   START
========================= */

function initializeApp() {

    setupCategoryButtons();
    setupStatusButtons();
    setupSearch();
    setupLoadMore();
    setupRefresh();

    loadNews();
}


if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeApp
    );

} else {

    initializeApp();

}
