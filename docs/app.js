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

function normalizeCategory(value) {
    if (!value) return "";

    const text = String(value).trim().toLowerCase();

    if (
        text === "morocco" ||
        text.includes("أخبار المغرب") ||
        text.includes("اخبار المغرب")
    ) {
        return "morocco";
    }

    if (
        text === "sports" ||
        text.includes("الرياضة") ||
        text.includes("رياضة")
    ) {
        return "sports";
    }

    if (
        text === "transfers" ||
        text.includes("انتقالات")
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


function normalizeNews(data) {
    if (!data) return [];

    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data.news)) {
        return data.news;
    }

    if (Array.isArray(data.items)) {
        return data.items;
    }

    if (data.sections && typeof data.sections === "object") {
        const result = [];

        Object.entries(data.sections).forEach(([section, items]) => {
            if (!Array.isArray(items)) return;

            items.forEach(item => {
                result.push({
                    ...item,
                    section: normalizeCategory(section)
                });
            });
        });

        return result;
    }

    return [];
}


function getNewsCategory(item) {
    if (!item) return "";

    if (item.section) {
        return normalizeCategory(item.section);
    }

    if (item.source_group) {
        return normalizeCategory(item.source_group);
    }

    if (item.category) {
        return normalizeCategory(item.category);
    }

    return "";
}


function getCategoryLabel(category) {
    return CATEGORY_LABELS[category] || category || "أخبار";
}


function escapeHTML(value) {
    if (value === null || value === undefined) return "";

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatDate(value) {
    if (!value) return "";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("ar-MA", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}


function filterNews() {
    filteredNews = allNews.filter(item => {

        const category = getNewsCategory(item);

        const categoryMatch =
            currentCategory === "all" ||
            category === currentCategory;

        const statusMatch =
            currentStatus === "all" ||
            String(item.status || "").trim() === currentStatus;

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

        const searchMatch =
            !searchTerm ||
            text.includes(searchTerm.toLowerCase());

        return categoryMatch && statusMatch && searchMatch;
    });

    visibleCount = 10;

    renderNews();
    renderStats();
}


function renderNews() {
    const container =
        document.querySelector("#news-container") ||
        document.querySelector(".news-grid") ||
        document.querySelector("#news-list");

    if (!container) return;

    const items = filteredNews.slice(0, visibleCount);

    if (!items.length) {
        container.innerHTML = `
            <div class="empty-state">
                لا توجد أخبار مطابقة للبحث الحالي.
            </div>
        `;
        updateLoadMoreButton();
        return;
    }

    container.innerHTML = items
        .map(renderCard)
        .join("");

    updateLoadMoreButton();
}


function renderCard(item) {
    const category = getNewsCategory(item);
    const categoryLabel = getCategoryLabel(category);

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
        "";

    const published =
        formatDate(item.published || item.discovered);

    const url =
        item.url ||
        "#";

    return `
        <article class="news-card">

            <div class="news-card-meta">
                <span class="news-category">
                    ${escapeHTML(categoryLabel)}
                </span>

                ${
                    status
                        ? `<span class="news-status">${escapeHTML(status)}</span>`
                        : ""
                }
            </div>

            <h3 class="news-title">
                <a href="${escapeHTML(url)}"
                   target="_blank"
                   rel="noopener noreferrer">
                    ${escapeHTML(title)}
                </a>
            </h3>

            <p class="news-summary">
                ${escapeHTML(summary)}
            </p>

            <div class="news-footer">

                <span class="news-source">
                    ${escapeHTML(source)}
                </span>

                ${
                    published
                        ? `<span class="news-date">${escapeHTML(published)}</span>`
                        : ""
                }

            </div>

        </article>
    `;
}


function renderHero() {
    const hero =
        document.querySelector("#hero") ||
        document.querySelector(".hero");

    if (!hero || !allNews.length) return;

    const item = allNews[0];

    const title =
        item.title ||
        "آخر الأخبار";

    const summary =
        item.summary ||
        "";

    const url =
        item.url ||
        "#";

    const category =
        getCategoryLabel(getNewsCategory(item));

    hero.innerHTML = `
        <div class="hero-content">

            <span class="hero-category">
                ${escapeHTML(category)}
            </span>

            <h1>
                <a href="${escapeHTML(url)}"
                   target="_blank"
                   rel="noopener noreferrer">
                    ${escapeHTML(title)}
                </a>
            </h1>

            ${
                summary
                    ? `<p>${escapeHTML(summary)}</p>`
                    : ""
            }

        </div>
    `;
}


function renderBreaking() {
    const ticker =
        document.querySelector("#breaking-news") ||
        document.querySelector(".breaking-news") ||
        document.querySelector("#ticker");

    if (!ticker) return;

    if (!allNews.length) {
        ticker.textContent = "لا توجد أخبار جديدة";
        return;
    }

    const latest = allNews.slice(0, 5);

    ticker.innerHTML = latest
        .map(item => {
            const url = item.url || "#";

            return `
                <a href="${escapeHTML(url)}"
                   target="_blank"
                   rel="noopener noreferrer">
                    ${escapeHTML(item.title || "")}
                </a>
            `;
        })
        .join(" • ");
}


function renderStats() {
    const total =
        document.querySelector("#total-news") ||
        document.querySelector("[data-stat='total']");

    const morocco =
        document.querySelector("#morocco-count") ||
        document.querySelector("[data-stat='morocco']");

    const sports =
        document.querySelector("#sports-count") ||
        document.querySelector("[data-stat='sports']");

    const transfers =
        document.querySelector("#transfers-count") ||
        document.querySelector("[data-stat='transfers']");

    if (total) {
        total.textContent = allNews.length;
    }

    if (morocco) {
        morocco.textContent =
            allNews.filter(
                item => getNewsCategory(item) === "morocco"
            ).length;
    }

    if (sports) {
        sports.textContent =
            allNews.filter(
                item => getNewsCategory(item) === "sports"
            ).length;
    }

    if (transfers) {
        transfers.textContent =
            allNews.filter(
                item => getNewsCategory(item) === "transfers"
            ).length;
    }
}


function updateLoadMoreButton() {
    const button =
        document.querySelector("#load-more") ||
        document.querySelector(".load-more");

    if (!button) return;

    if (visibleCount >= filteredNews.length) {
        button.style.display = "none";
    } else {
        button.style.display = "";
    }
}


function setupCategoryEvents() {
    const buttons = document.querySelectorAll(
        "[data-category]"
    );

    buttons.forEach(button => {
        button.addEventListener("click", () => {

            currentCategory =
                normalizeCategory(
                    button.dataset.category
                ) || "all";

            buttons.forEach(btn =>
                btn.classList.remove("active")
            );

            button.classList.add("active");

            filterNews();
        });
    });
}


function setupStatusFilters() {
    const buttons = document.querySelectorAll(
        "[data-status]"
    );

    buttons.forEach(button => {
        button.addEventListener("click", () => {

            currentStatus =
                button.dataset.status || "all";

            buttons.forEach(btn =>
                btn.classList.remove("active")
            );

            button.classList.add("active");

            filterNews();
        });
    });
}


function setupSearch() {
    const input =
        document.querySelector("#search-input") ||
        document.querySelector("#search") ||
        document.querySelector('input[type="search"]');

    if (!input) return;

    input.addEventListener("input", event => {
        searchTerm = event.target.value.trim();
        filterNews();
    });
}


function setupLoadMore() {
    const button =
        document.querySelector("#load-more") ||
        document.querySelector(".load-more");

    if (!button) return;

    button.addEventListener("click", () => {
        visibleCount += 10;
        renderNews();
    });
}


function setupRefresh() {
    const buttons = document.querySelectorAll(
        "#refresh, .refresh-button, [data-action='refresh']"
    );

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            loadNews(true);
        });
    });
}


function setupTheme() {
    const button =
        document.querySelector("#theme-toggle") ||
        document.querySelector(".theme-toggle");

    if (!button) return;

    button.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        localStorage.setItem(
            "theme",
            document.body.classList.contains("dark-mode")
                ? "dark"
                : "light"
        );
    });

    const savedTheme =
        localStorage.getItem("theme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark-mode");
    }
}


function setupMobileMenu() {
    const button =
        document.querySelector("#menu-toggle") ||
        document.querySelector(".menu-toggle");

    const menu =
        document.querySelector("#mobile-menu") ||
        document.querySelector(".mobile-menu");

    if (!button || !menu) return;

    button.addEventListener("click", () => {
        menu.classList.toggle("open");
    });
}


function showLoading() {
    const container =
        document.querySelector("#news-container") ||
        document.querySelector(".news-grid") ||
        document.querySelector("#news-list");

    if (container) {
        container.innerHTML = `
            <div class="loading">
                جار تحميل الأخبار...
            </div>
        `;
    }
}


function showError() {
    const container =
        document.querySelector("#news-container") ||
        document.querySelector(".news-grid") ||
        document.querySelector("#news-list");

    if (container) {
        container.innerHTML = `
            <div class="error-state">
                تعذر تحميل الأخبار.
                حاول تحديث الصفحة.
            </div>
        `;
    }
}


async function loadNews(forceRefresh = false) {

    showLoading();

    try {

        const cacheBuster =
            Date.now();

        const response = await fetch(
            `${NEWS_URL}?v=${cacheBuster}`,
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

        filteredNews =
            [...allNews];

        if (!allNews.length) {
            throw new Error(
                "No news items found"
            );
        }

        renderHero();
        renderBreaking();
        filterNews();
        renderStats();

        updateLastUpdate(data);

    } catch (error) {

        console.error(
            "News loading error:",
            error
        );

        showError();
    }
}


function updateLastUpdate(data) {

    const element =
        document.querySelector("#last-update") ||
        document.querySelector(".last-update");

    if (!element) return;

    let value =
        data &&
        data.updated
            ? data.updated
            : new Date().toISOString();

    element.textContent =
        `آخر تحديث: ${formatDate(value)}`;
}


function showToast(message) {

    let toast =
        document.querySelector("#toast");

    if (!toast) {

        toast =
            document.createElement("div");

        toast.id = "toast";
        toast.className = "toast";

        document.body.appendChild(toast);
    }

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}


function initializeApp() {

    setupCategoryEvents();
    setupStatusFilters();
    setupSearch();
    setupLoadMore();
    setupRefresh();
    setupTheme();
    setupMobileMenu();

    loadNews();
}


if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeApp
    );

} else {

    initializeApp();

}
