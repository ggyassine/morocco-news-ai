const NEWS_URL = "news.json";

let allNews = [];
let filteredNews = [];

let currentCategory = "all";
let currentStatus = "all";
let searchTerm = "";

let visibleCount = 10;


/* =========================================================
   HELPERS
========================================================= */

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


function setText(id, value) {

    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


/* =========================================================
   NORMALIZE DATA
========================================================= */

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


/* =========================================================
   CATEGORY DETECTION
========================================================= */

function getNewsCategory(item) {

    /*
     * إذا كان export_news.py قد أنشأ section
     * نستخدمه مباشرة
     */

    if (item.section) {
        return normalizeCategory(item.section);
    }


    /*
     * إذا كان هناك source_group
     */

    if (item.source_group) {
        return normalizeCategory(item.source_group);
    }


    const category =
        String(item.category || "").trim();


    /*
     * المغرب
     */

    if (
        category === "أخبار المغرب" ||
        category === "المغرب" ||
        category === "Morocco" ||
        category === "morocco"
    ) {
        return "morocco";
    }


    /*
     * الشرق الأوسط
     */

    if (
        category === "الشرق الأوسط" ||
        category === "أخبار الشرق الأوسط" ||
        category === "Middle East" ||
        category === "middle_east"
    ) {
        return "middle_east";
    }


    /*
     * العالم بالعربية
     */

    if (
        category === "العالم" ||
        category === "أخبار العالم" ||
        category === "العالم بالعربية" ||
        category === "World" ||
        category === "world_arabic"
    ) {
        return "world_arabic";
    }


    /*
     * الرياضة
     */

    if (
        category === "رياضة" ||
        category === "الرياضة" ||
        category === "Sports" ||
        category === "sports"
    ) {
        return "sports";
    }


    /*
     * الانتقالات
     */

    if (
        category === "انتقالات اللاعبين" ||
        category === "انتقالات" ||
        category === "Transfers" ||
        category === "transfers"
    ) {
        return "transfers";
    }


    return "other";
}


function normalizeCategory(category) {

    const value =
        String(category || "")
            .trim()
            .toLowerCase();


    if (
        value === "morocco" ||
        value === "المغرب" ||
        value === "أخبار المغرب"
    ) {
        return "morocco";
    }


    if (
        value === "middle_east" ||
        value === "middle east" ||
        value === "الشرق الأوسط"
    ) {
        return "middle_east";
    }


    if (
        value === "world_arabic" ||
        value === "world" ||
        value === "العالم" ||
        value === "العالم بالعربية"
    ) {
        return "world_arabic";
    }


    if (
        value === "sports" ||
        value === "sport" ||
        value === "رياضة"
    ) {
        return "sports";
    }


    if (
        value === "transfers" ||
        value === "transfer" ||
        value === "انتقالات اللاعبين"
    ) {
        return "transfers";
    }


    return value || "other";
}


/* =========================================================
   STATUS
========================================================= */

function getNewsStatus(item) {

    return item.status || "غير واضح";
}


/* =========================================================
   SOURCE GROUP FALLBACK
========================================================= */

const MOROCCO_SOURCES = [

    "MAP عربي",
    "MAP",
    "SNRTnews عربي",
    "SNRTnews",
    "هسبريس",
    "Le360 عربي",
    "Le360",
    "العمق المغربي",
    "اليوم24",
    "أخبارنا المغربية",
    "هبة بريس",
    "برلمان",
    "كود",
    "كفاش",
    "فبراير",
    "البطولة",
    "المنتخب"
];


const MIDDLE_EAST_SOURCES = [

    "الجزيرة",
    "العربية",
    "سكاي نيوز عربية",
    "الشرق للأخبار",
    "الشرق الأوسط",
    "العربي الجديد"
];


const WORLD_ARABIC_SOURCES = [

    "فرانس 24 عربي",
    "France 24 عربي",
    "DW عربية",
    "BBC عربي",
    "يورو نيوز عربي",
    "يورونيوز عربي",
    "إندبندنت عربية",
    "CNN عربية",
    "القدس العربي"
];


function getSourceGroup(item) {

    const source =
        String(item.source || "").trim();


    if (
        MOROCCO_SOURCES.includes(source)
    ) {
        return "morocco";
    }


    if (
        MIDDLE_EAST_SOURCES.includes(source)
    ) {
        return "middle_east";
    }


    if (
        WORLD_ARABIC_SOURCES.includes(source)
    ) {
        return "world_arabic";
    }


    return null;
}


/* =========================================================
   FINAL SECTION
========================================================= */

function getFinalSection(item) {

    const category =
        getNewsCategory(item);


    /*
     * الانتقالات لها الأولوية
     */

    if (category === "transfers") {
        return "transfers";
    }


    /*
     * الرياضة
     */

    if (category === "sports") {
        return "sports";
    }


    /*
     * إذا كان section واضحا
     */

    if (
        category === "morocco" ||
        category === "middle_east" ||
        category === "world_arabic"
    ) {
        return category;
    }


    /*
     * الاعتماد على المصدر
     */

    const sourceGroup =
        getSourceGroup(item);


    if (sourceGroup) {
        return sourceGroup;
    }


    /*
     * الأخبار المغربية القديمة
     */

    if (
        item.category === "أخبار المغرب"
    ) {
        return "morocco";
    }


    /*
     * أخبار العالم القديمة
     */

    if (
        item.category === "العالم"
    ) {
        return "world_arabic";
    }


    /*
     * الشرق الأوسط
     */

    if (
        item.category === "الشرق الأوسط"
    ) {
        return "middle_east";
    }


    return "other";
}


/* =========================================================
   LOAD NEWS
========================================================= */

async function loadNews(showToast = false) {

    try {

        const response = await fetch(
            `${NEWS_URL}?t=${Date.now()}`,
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


        /*
         * تنظيف الأخبار غير الصالحة
         */

        allNews =
            allNews.filter(
                item =>
                    item &&
                    (
                        item.title ||
                        item.summary
                    )
            );


        /*
         * ترتيب الأحدث أولا
         */

        allNews.sort(
            (a, b) => {

                const dateA =
                    new Date(
                        a.published ||
                        a.discovered ||
                        0
                    );

                const dateB =
                    new Date(
                        b.published ||
                        b.discovered ||
                        0
                    );

                return dateB - dateA;
            }
        );


        updateStats();

        applyFilters();

        updateHero();

        updateBreaking();

        updateSources();

        updatePlayers();

        updateLastUpdate();


        if (showToast) {

            showToastMessage(
                "تم تحديث الأخبار"
            );

        }

    } catch (error) {

        console.error(
            "Failed to load news:",
            error
        );


        showEmptyState(
            "تعذر تحميل الأخبار"
        );
    }
}


/* =========================================================
   FILTERS
========================================================= */

function applyFilters() {

    filteredNews =
        allNews.filter(item => {

            const section =
                getFinalSection(item);

            const status =
                getNewsStatus(item);


            const text = [

                item.title,
                item.summary,
                item.source,
                item.player,
                item.category,
                item.section,
                section,
                status

            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();


            const categoryMatch =
                currentCategory === "all" ||
                section === currentCategory;


            const statusMatch =
                currentStatus === "all" ||
                status === currentStatus;


            const searchMatch =
                !searchTerm ||
                text.includes(
                    searchTerm.toLowerCase()
                );


            return (
                categoryMatch &&
                statusMatch &&
                searchMatch
            );

        });


    visibleCount = 10;

    renderNews();
}


/* =========================================================
   RENDER NEWS
========================================================= */

function renderNews() {

    const grid =
        document.getElementById(
            "newsGrid"
        );


    const empty =
        document.getElementById(
            "emptyState"
        );


    if (!grid) {
        return;
    }


    if (!filteredNews.length) {

        grid.innerHTML = "";


        if (empty) {
            empty.classList.remove(
                "hidden"
            );
        }


        return;
    }


    if (empty) {

        empty.classList.add(
            "hidden"
        );

    }


    const items =
        filteredNews.slice(
            0,
            visibleCount
        );


    grid.innerHTML =
        items
            .map(renderNewsCard)
            .join("");


    const loadMore =
        document.getElementById(
            "loadMore"
        );


    if (!loadMore) {
        return;
    }


    if (
        visibleCount >=
        filteredNews.length
    ) {

        loadMore.style.display =
            "none";

    } else {

        loadMore.style.display =
            "inline-block";
    }
}


/* =========================================================
   CATEGORY LABEL
========================================================= */

function getCategoryLabel(item) {

    const section =
        getFinalSection(item);


    const labels = {

        morocco: "🇲🇦 المغرب",

        middle_east:
            "🌍 الشرق الأوسط",

        world_arabic:
            "🌎 العالم",

        sports:
            "⚽ الرياضة",

        transfers:
            "🔄 الانتقالات",

        other:
            "📰 أخبار"

    };


    return (
        labels[section] ||
        labels.other
    );
}


/* =========================================================
   NEWS CARD
========================================================= */

function renderNewsCard(item) {

    const status =
        getNewsStatus(item);


    const statusClass =
        status === "رسمي"
            ? "official"
            : status === "إشاعة"
                ? "rumor"
                : status === "مؤكد"
                    ? "confirmed"
                    : "";


    const category =
        getCategoryLabel(item);


    return `

        <article
            class="news-card"
            data-section="${escapeHTML(
                getFinalSection(item)
            )}"
        >

            <div class="news-top">

                <span class="news-source">

                    ${escapeHTML(
                        item.source ||
                        "مصدر غير معروف"
                    )}

                </span>


                <span class="news-category">

                    ${escapeHTML(
                        category
                    )}

                </span>


                <span
                    class="news-status ${statusClass}"
                >

                    ${escapeHTML(
                        status
                    )}

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

                            ⚽

                            ${escapeHTML(
                                item.player
                            )}

                        </div>

                    `
                    : ""
            }


            <p class="news-summary">

                ${escapeHTML(
                    item.summary ||
                    ""
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
                                href="${escapeHTML(
                                    item.url
                                )}"
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


/* =========================================================
   HERO
========================================================= */

function updateHero() {

    const hero =
        allNews.find(
            item =>
                item.title
        );


    if (!hero) {
        return;
    }


    setText(
        "heroSource",
        hero.source ||
        "مصدر غير معروف"
    );


    setText(
        "heroTime",
        formatDate(
            hero.published ||
            hero.discovered
        )
    );


    setText(
        "heroTitle",
        hero.title ||
        "آخر الأخبار"
    );


    setText(
        "heroSummary",
        hero.summary ||
        "آخر المستجدات من مصادر الأخبار."
    );


    const link =
        document.getElementById(
            "heroLink"
        );


    if (!link) {
        return;
    }


    if (hero.url) {

        link.href =
            hero.url;

        link.style.display =
            "inline-flex";

    } else {

        link.style.display =
            "none";
    }
}


/* =========================================================
   BREAKING
========================================================= */

function updateBreaking() {

    const element =
        document.getElementById(
            "breakingNews"
        );


    if (!element) {
        return;
    }


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


/* =========================================================
   SOURCES
========================================================= */

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
            .slice(0, 10);


    const container =
        document.getElementById(
            "sourcesList"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        sources
            .map(
                ([name, count]) => {

                    const initials =
                        name
                            .trim()
                            .slice(0, 2);


                    return `

                        <div
                            class="source-item"
                        >

                            <div
                                class="source-name"
                            >

                                <div
                                    class="source-logo"
                                >

                                    ${escapeHTML(
                                        initials
                                    )}

                                </div>


                                <span>

                                    ${escapeHTML(
                                        name
                                    )}

                                </span>

                            </div>


                            <span
                                class="source-count"
                            >

                                ${count}

                            </span>

                        </div>

                    `;
                }
            )
            .join("");
}


/* =========================================================
   PLAYERS
========================================================= */

function updatePlayers() {

    const counts = {};


    allNews.forEach(item => {

        if (!item.player) {
            return;
        }


        const player =
            item.player;


        counts[player] =
            (counts[player] || 0) + 1;

    });


    const players =
        Object.entries(counts)
            .sort(
                (a, b) =>
                    b[1] - a[1]
            )
            .slice(0, 8);


    const container =
        document.getElementById(
            "playersList"
        );


    if (!container) {
        return;
    }


    if (!players.length) {

        container.innerHTML = `

            <p class="news-summary">

                لا توجد تحديثات للاعبين حاليًا.

            </p>

        `;

        return;
    }


    container.innerHTML =
        players
            .map(
                ([name, count]) => {

                    const initials =
                        name
                            .trim()
                            .slice(0, 2);


                    return `

                        <div
                            class="player-item"
                        >

                            <div
                                class="player-avatar"
                            >

                                ${escapeHTML(
                                    initials
                                )}

                            </div>


                            <div
                                class="player-info"
                            >

                                <strong>

                                    ${escapeHTML(
                                        name
                                    )}

                                </strong>


                                <span>

                                    ${count} خبر

                                </span>

                            </div>

                        </div>

                    `;
                }
            )
            .join("");
}


/* =========================================================
   STATISTICS
========================================================= */

function updateStats() {

    const all =
        allNews.length;


    const morocco =
        allNews.filter(
            item =>
                getFinalSection(item) ===
                "morocco"
        ).length;


    const middleEast =
        allNews.filter(
            item =>
                getFinalSection(item) ===
                "middle_east"
        ).length;


    const worldArabic =
        allNews.filter(
            item =>
                getFinalSection(item) ===
                "world_arabic"
        ).length;


    const sport =
        allNews.filter(
            item =>
                getFinalSection(item) ===
                "sports"
        ).length;


    const transfers =
        allNews.filter(
            item =>
                getFinalSection(item) ===
                "transfers"
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


    setText(
        "countAll",
        all
    );


    setText(
        "countMorocco",
        morocco
    );


    setText(
        "countMiddleEast",
        middleEast
    );


    setText(
        "countWorld",
        worldArabic
    );


    setText(
        "countSport",
        sport
    );


    setText(
        "countTransfers",
        transfers
    );


    setText(
        "statusOfficial",
        official
    );


    setText(
        "statusConfirmed",
        confirmed
    );


    setText(
        "statusNegotiation",
        negotiation
    );


    setText(
        "statusRumor",
        rumor
    );


    setText(
        "totalNews",
        all
    );


    const uniqueSources =
        new Set(
            allNews
                .map(
                    item =>
                        item.source
                )
                .filter(Boolean)
        ).size;


    setText(
        "sourceCount",
        uniqueSources
    );
}


/* =========================================================
   LAST UPDATE
========================================================= */

function updateLastUpdate() {

    setText(
        "lastUpdate",

        new Intl.DateTimeFormat(
            "ar-MA",
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        ).format(
            new Date()
        )
    );
}


/* =========================================================
   CATEGORY BUTTON
========================================================= */

function setCategory(category) {

    currentCategory =
        normalizeCategory(
            category
        );


    document
        .querySelectorAll(
            "[data-category]"
        )
        .forEach(button => {

            const buttonCategory =
                normalizeCategory(
                    button.dataset.category
                );


            if (
                buttonCategory ===
                currentCategory
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


/* =========================================================
   STATUS BUTTONS
========================================================= */

function setupStatusFilters() {

    document
        .querySelectorAll(
            ".feed-filter"
        )
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
                        button.dataset.status ||
                        "all";


                    applyFilters();
                }
            );

        });
}


/* =========================================================
   SEARCH
========================================================= */

function setupSearch() {

    const searchInput =
        document.getElementById(
            "searchInput"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            event => {

                searchTerm =
                    event.target.value.trim();


                applyFilters();
            }
        );

    }


    const clearSearch =
        document.getElementById(
            "clearSearch"
        );


    if (clearSearch) {

        clearSearch.addEventListener(
            "click",
            () => {

                if (searchInput) {

                    searchInput.value =
                        "";

                }


                searchTerm =
                    "";


                applyFilters();
            }
        );

    }
}


/* =========================================================
   CATEGORY EVENTS
========================================================= */

function setupCategoryButtons() {

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
}


/* =========================================================
   LOAD MORE
========================================================= */

function setupLoadMore() {

    const button =
        document.getElementById(
            "loadMore"
        );


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


/* =========================================================
   REFRESH
========================================================= */

function setupRefresh() {

    const button =
        document.getElementById(
            "refreshBtn"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        () => {

            loadNews(true);
        }
    );
}


/* =========================================================
   THEME
========================================================= */

function setupTheme() {

    const button =
        document.getElementById(
            "themeBtn"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        () => {

            document.body.classList.toggle(
                "light-mode"
            );


            const isLight =
                document.body.classList.contains(
                    "light-mode"
                );


            localStorage.setItem(
                "morocco-news-theme",
                isLight
                    ? "light"
                    : "dark"
            );
        }
    );


    const savedTheme =
        localStorage.getItem(
            "morocco-news-theme"
        );


    if (savedTheme === "light") {

        document.body.classList.add(
            "light-mode"
        );
    }
}


/* =========================================================
   MOBILE MENU
========================================================= */

let mobileMenu = null;


function setupMobileMenu() {

    mobileMenu =
        document.getElementById(
            "mobileMenu"
        );


    const menuButton =
        document.getElementById(
            "menuBtn"
        );


    const closeButton =
        document.getElementById(
            "closeMenu"
        );


    if (menuButton) {

        menuButton.addEventListener(
            "click",
            () => {

                if (mobileMenu) {

                    mobileMenu.classList.add(
                        "open"
                    );

                }

            }
        );

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeMobileMenu
        );

    }
}


function closeMobileMenu() {

    if (!mobileMenu) {
        return;
    }


    mobileMenu.classList.remove(
        "open"
    );
}


/* =========================================================
   EMPTY STATE
========================================================= */

function showEmptyState(message) {

    const empty =
        document.getElementById(
            "emptyState"
        );


    if (!empty) {
        return;
    }


    empty.classList.remove(
        "hidden"
    );


    const heading =
        empty.querySelector(
            "h2"
        );


    if (heading) {

        heading.textContent =
            message;

    }
}


/* =========================================================
   TOAST
========================================================= */

let toastTimer;


function showToastMessage(message) {

    const toast =
        document.getElementById(
            "toast"
        );


    if (!toast) {
        return;
    }


    toast.textContent =
        message;


    toast.classList.add(
        "show"
    );


    clearTimeout(
        toastTimer
    );


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


/* =========================================================
   FOOTER YEAR
========================================================= */

setText(
    "footerYear",
    new Date().getFullYear()
);


/* =========================================================
   INITIALIZE
========================================================= */

function initializeApp() {

    setupStatusFilters();

    setupSearch();

    setupCategoryButtons();

    setupLoadMore();

    setupRefresh();

    setupTheme();

    setupMobileMenu();

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
