const NEWS_URL = "news.json";

let allNews = [];
let filteredNews = [];

let currentCategory = "all";
let currentStatus = "all";
let searchTerm = "";

let visibleCount = 10;


/* =========================
   HELPERS
========================= */

function escapeHTML(value) {
    return String(value ?? "")
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
        hour: "2-digit",
        minute: "2-digit"
    }).format(date);
}


function normalizeNews(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (data && Array.isArray(data.news)) {
        return data.news;
    }

    if (data && Array.isArray(data.items)) {
        return data.items;
    }

    return [];
}


function getNewsCategory(item) {
    return item.category || "";
}


function getNewsStatus(item) {
    return item.status || "غير واضح";
}


/* =========================
   LOAD NEWS
========================= */

async function loadNews(showToast = false) {

    try {

        const response = await fetch(
            `${NEWS_URL}?t=${Date.now()}`,
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        allNews = normalizeNews(data);

        allNews.sort(
            (a, b) =>
                new Date(
                    b.published || b.discovered || 0
                ) -
                new Date(
                    a.published || a.discovered || 0
                )
        );

        updateStats();
        applyFilters();
        updateHero();
        updateBreaking();
        updateSources();
        updatePlayers();
        updateLastUpdate();

        if (showToast) {
            showToastMessage("تم تحديث الأخبار");
        }

    } catch (error) {

        console.error(
            "Failed to load news:",
            error
        );

        showEmptyState("تعذر تحميل الأخبار");
    }
}


/* =========================
   FILTERS
========================= */

function applyFilters() {

    filteredNews = allNews.filter(item => {

        const category = getNewsCategory(item);
        const status = getNewsStatus(item);

        const text = [
            item.title,
            item.summary,
            item.source,
            item.player,
            category,
            status
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        const categoryMatch =
            currentCategory === "all" ||
            category === currentCategory;

        const statusMatch =
            currentStatus === "all" ||
            status === currentStatus;

        const searchMatch =
            !searchTerm ||
            text.includes(searchTerm.toLowerCase());

        return (
            categoryMatch &&
            statusMatch &&
            searchMatch
        );
    });

    visibleCount = 10;

    renderNews();
}


/* =========================
   RENDER NEWS
========================= */

function renderNews() {

    const grid =
        document.getElementById("newsGrid");

    const empty =
        document.getElementById("emptyState");

    if (!filteredNews.length) {

        grid.innerHTML = "";

        empty.classList.remove("hidden");

        return;
    }

    empty.classList.add("hidden");

    const items =
        filteredNews.slice(
            0,
            visibleCount
        );

    grid.innerHTML =
        items.map(renderNewsCard).join("");

    const loadMore =
        document.getElementById("loadMore");

    if (
        visibleCount >=
        filteredNews.length
    ) {

        loadMore.style.display = "none";

    } else {

        loadMore.style.display =
            "inline-block";
    }
}


function renderNewsCard(item) {

    const status =
        getNewsStatus(item);

    const statusClass =
        status === "رسمي"
            ? "official"
            : status === "إشاعة"
                ? "rumor"
                : "";

    return `
        <article class="news-card">

            <div class="news-top">

                <span class="news-source">
                    ${escapeHTML(
                        item.source ||
                        "مصدر غير معروف"
                    )}
                </span>

                <span class="news-status ${statusClass}">
                    ${escapeHTML(status)}
                </span>

            </div>

            <h3>
                ${escapeHTML(
                    item.title ||
                    "بدون عنوان"
                )}
            </h3>

            ${
                item.player
                    ? `
                        <div class="news-player">
                            ⚽ ${escapeHTML(item.player)}
                        </div>
                    `
                    : ""
            }

            <p class="news-summary">
                ${escapeHTML(
                    item.summary || ""
                )}
            </p>

            <div class="news-footer">

                <span class="news-time">
                    ${formatDate(
                        item.published ||
                        item.discovered
                    )}
                </span>

                ${
                    item.url
                        ? `
                            <a
                                class="news-link"
                                href="${escapeHTML(item.url)}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                قراءة الخبر ←
                            </a>
                        `
                        : ""
                }

            </div>

        </article>
    `;
}


/* =========================
   HERO
========================= */

function updateHero() {

    const hero = allNews[0];

    if (!hero) {
        return;
    }

    document.getElementById(
        "heroSource"
    ).textContent =
        hero.source || "مصدر غير معروف";

    document.getElementById(
        "heroTime"
    ).textContent =
        formatDate(
            hero.published ||
            hero.discovered
        );

    document.getElementById(
        "heroTitle"
    ).textContent =
        hero.title ||
        "آخر الأخبار";

    document.getElementById(
        "heroSummary"
    ).textContent =
        hero.summary ||
        "آخر المستجدات من مصادر الأخبار المغربية.";

    const link =
        document.getElementById("heroLink");

    if (hero.url) {

        link.href = hero.url;

        link.style.display =
            "inline-flex";

    } else {

        link.style.display = "none";
    }
}


/* =========================
   BREAKING NEWS
========================= */

function updateBreaking() {

    const element =
        document.getElementById(
            "breakingNews"
        );

    const item =
        allNews.find(
            news =>
                news.status === "رسمي" ||
                news.status === "مؤكد"
        ) ||
        allNews[0];

    element.textContent =
        item
            ? item.title
            : "لا توجد أخبار جديدة";
}


/* =========================
   SOURCES
========================= */

function updateSources() {

    const counts = {};

    allNews.forEach(item => {

        const source =
            item.source ||
            "غير معروف";

        counts[source] =
            (counts[source] || 0) + 1;
    });

    const sources =
        Object.entries(counts)
            .sort(
                (a, b) =>
                    b[1] - a[1]
            )
            .slice(0, 8);

    document.getElementById(
        "sourcesList"
    ).innerHTML =
        sources.map(
            ([name, count]) => {

                const initials =
                    name.trim().slice(0, 2);

                return `
                    <div class="source-item">

                        <div class="source-name">

                            <div class="source-logo">
                                ${escapeHTML(initials)}
                            </div>

                            <span>
                                ${escapeHTML(name)}
                            </span>

                        </div>

                        <span class="source-count">
                            ${count}
                        </span>

                    </div>
                `;
            }
        ).join("");
}


/* =========================
   PLAYERS
========================= */

function updatePlayers() {

    const counts = {};

    allNews.forEach(item => {

        if (!item.player) {
            return;
        }

        const player = item.player;

        counts[player] =
            (counts[player] || 0) + 1;
    });

    const players =
        Object.entries(counts)
            .sort(
                (a, b) =>
                    b[1] - a[1]
            )
            .slice(0, 6);

    const container =
        document.getElementById(
            "playersList"
        );

    if (!players.length) {

        container.innerHTML = `
            <p class="news-summary">
                لا توجد تحديثات للاعبين حاليًا.
            </p>
        `;

        return;
    }

    container.innerHTML =
        players.map(
            ([name, count]) => {

                const initials =
                    name.trim().slice(0, 2);

                return `
                    <div class="player-item">

                        <div class="player-avatar">
                            ${escapeHTML(initials)}
                        </div>

                        <div class="player-info">

                            <strong>
                                ${escapeHTML(name)}
                            </strong>

                            <span>
                                ${count} خبر
                            </span>

                        </div>

                    </div>
                `;
            }
        ).join("");
}


/* =========================
   STATISTICS
========================= */

function updateStats() {

    const all = allNews.length;

    const morocco =
        allNews.filter(
            item =>
                item.category ===
                "أخبار المغرب"
        ).length;

    const sport =
        allNews.filter(
            item =>
                item.category === "رياضة"
        ).length;

    const transfers =
        allNews.filter(
            item =>
                item.category ===
                "انتقالات اللاعبين"
        ).length;

    const official =
        allNews.filter(
            item =>
                item.status === "رسمي"
        ).length;

    const confirmed =
        allNews.filter(
            item =>
                item.status === "مؤكد"
        ).length;

    const negotiation =
        allNews.filter(
            item =>
                item.status === "مفاوضات"
        ).length;

    const rumor =
        allNews.filter(
            item =>
                item.status === "إشاعة"
        ).length;

    setText("countAll", all);
    setText("countMorocco", morocco);
    setText("countSport", sport);
    setText("countTransfers", transfers);

    setText("statusOfficial", official);
    setText("statusConfirmed", confirmed);
    setText("statusNegotiation", negotiation);
    setText("statusRumor", rumor);

    setText("totalNews", all);

    const uniqueSources =
        new Set(
            allNews
                .map(item => item.source)
                .filter(Boolean)
        ).size;

    setText(
        "sourceCount",
        uniqueSources
    );
}


function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


/* =========================
   LAST UPDATE
========================= */

function updateLastUpdate() {

    setText(
        "lastUpdate",

        new Intl.DateTimeFormat(
            "ar-MA",
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        ).format(new Date())
    );
}


/* =========================
   CATEGORY
========================= */

function setCategory(category) {

    currentCategory = category;

    document
        .querySelectorAll(
            "[data-category]"
        )
        .forEach(button => {

            if (
                button.dataset.category ===
                category
            ) {

                button.classList.add(
                    "active"
                );

            } else {

                button.classList.remove(
                    "active"
                );
            }
        });

    applyFilters();
}


/* =========================
   STATUS FILTER
========================= */

document
    .querySelectorAll(".feed-filter")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                document
                    .querySelectorAll(
                        ".feed-filter"
                    )
                    .forEach(
                        b =>
                            b.classList.remove(
                                "active"
                            )
                    );

                button.classList.add(
                    "active"
                );

                currentStatus =
                    button.dataset.status;

                applyFilters();
            }
        );
    });


/* =========================
   SEARCH
========================= */

document
    .getElementById("searchInput")
    .addEventListener(
        "input",
        event => {

            searchTerm =
                event.target.value.trim();

            applyFilters();
        }
    );


document
    .getElementById("clearSearch")
    .addEventListener(
        "click",
        () => {

            const input =
                document.getElementById(
                    "searchInput"
                );

            input.value = "";

            searchTerm = "";

            applyFilters();
        }
    );


/* =========================
   CATEGORY EVENTS
========================= */

document
    .querySelectorAll(
        "[data-category]"
    )
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                setCategory(
                    button.dataset.category
                );

                closeMobileMenu();
            }
        );
    });


/* =========================
   LOAD MORE
========================= */

document
    .getElementById("loadMore")
    .addEventListener(
        "click",
        () => {

            visibleCount += 10;

            renderNews();
        }
    );


/* =========================
   REFRESH
========================= */

document
    .getElementById("refreshBtn")
    .addEventListener(
        "click",
        () => {

            loadNews(true);
        }
    );


/* =========================
   THEME
========================= */

document
    .getElementById("themeBtn")
    .addEventListener(
        "click",
        () => {

            document.body.classList.toggle(
                "light-mode"
            );
        }
    );


/* =========================
   MOBILE MENU
========================= */

const mobileMenu =
    document.getElementById(
        "mobileMenu"
    );


document
    .getElementById("menuBtn")
    .addEventListener(
        "click",
        () => {

            mobileMenu.classList.add(
                "open"
            );
        }
    );


document
    .getElementById("closeMenu")
    .addEventListener(
        "click",
        closeMobileMenu
    );


function closeMobileMenu() {

    mobileMenu.classList.remove(
        "open"
    );
}


/* =========================
   EMPTY STATE
========================= */

function showEmptyState(message) {

    const empty =
        document.getElementById(
            "emptyState"
        );

    empty.classList.remove(
        "hidden"
    );

    empty.querySelector(
        "h2"
    ).textContent = message;
}


/* =========================
   TOAST
========================= */

let toastTimer;


function showToastMessage(message) {

    const toast =
        document.getElementById(
            "toast"
        );

    toast.textContent = message;

    toast.classList.add("show");

    clearTimeout(toastTimer);

    toastTimer =
        setTimeout(
            () => {

                toast.classList.remove(
                    "show"
                );

            },
            2500
        );
}


/* =========================
   FOOTER YEAR
========================= */

setText(
    "footerYear",
    new Date().getFullYear()
);


/* =========================
   START
========================= */

loadNews();
