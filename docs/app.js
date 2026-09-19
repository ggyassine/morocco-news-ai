const NEWS_URL = "news.json";

let allNews = [];
let filteredNews = [];

let currentCategory = "all";
let currentStatus = "all";
let searchTerm = "";

let visibleCount = 10;

let toastTimer = null;


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


function setText(id, value) {

    const element = document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


function getElement(id) {
    return document.getElementById(id);
}


function formatDate(value) {

    if (!value) {
        return "غير معروف";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(
        "ar-MA",
        {
            day: "2-digit",
            month: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }
    ).format(date);
}


/* =========================================================
   CATEGORY NORMALIZATION
========================================================= */

function normalizeCategory(category) {

    const value = String(category || "")
        .trim()
        .toLowerCase();

    if (
        value === "morocco" ||
        value === "أخبار المغرب" ||
        value === "المغرب" ||
        value === "moroccan"
    ) {
        return "morocco";
    }


    if (
        value === "middle_east" ||
        value === "middle east" ||
        value === "الشرق الأوسط" ||
        value === "أخبار الشرق الأوسط"
    ) {
        return "middle_east";
    }


    if (
        value === "world_arabic" ||
        value === "world" ||
        value === "العالم" ||
        value === "العالم بالعربية" ||
        value === "أخبار العالم"
    ) {
        return "world_arabic";
    }


    if (
        value === "sports" ||
        value === "sport" ||
        value === "رياضة" ||
        value === "الرياضة"
    ) {
        return "sports";
    }


    if (
        value === "transfers" ||
        value === "transfer" ||
        value === "انتقالات" ||
        value === "انتقالات اللاعبين"
    ) {
        return "transfers";
    }


    return value;
}


/* =========================================================
   NORMALIZE NEWS DATA
========================================================= */

function normalizeNews(data) {

    /*
       الصيغة الأولى:
       [
          {...},
          {...}
       ]
    */

    if (Array.isArray(data)) {
        return data;
    }


    /*
       الصيغة القديمة:
       {
           "news": [...]
       }
    */

    if (
        data &&
        Array.isArray(data.news)
    ) {
        return data.news;
    }


    /*
       الصيغة القديمة:
       {
           "items": [...]
       }
    */

    if (
        data &&
        Array.isArray(data.items)
    ) {
        return data.items;
    }


    /*
       الصيغة الجديدة:

       {
           "sections": {
               "morocco": [],
               "middle_east": [],
               "world_arabic": [],
               "sports": [],
               "transfers": []
           }
       }
    */

    if (
        data &&
        data.sections &&
        typeof data.sections === "object"
    ) {

        const news = [];

        Object.entries(
            data.sections
        ).forEach(
            ([sectionName, articles]) => {

                if (!Array.isArray(articles)) {
                    return;
                }

                articles.forEach(article => {

                    news.push({

                        ...article,

                        section:
                            article.section ||
                            sectionName

                    });

                });

            }
        );

        return news;
    }


    return [];
}


/* =========================================================
   CATEGORY DETECTION
========================================================= */

function getNewsCategory(item) {

    /*
       export_news.py يرسل section
    */

    if (item && item.section) {

        return normalizeCategory(
            item.section
        );
    }


    /*
       بعض الأخبار قد تحتوي source_group
    */

    if (
        item &&
        item.source_group
    ) {

        return normalizeCategory(
            item.source_group
        );
    }


    /*
       fallback إلى category
    */

    if (
        item &&
        item.category
    ) {

        return normalizeCategory(
            item.category
        );
    }


    return "";
}


/* =========================================================
   STATUS
========================================================= */

function getNewsStatus(item) {

    if (
        item &&
        item.status
    ) {
        return item.status;
    }

    return "غير واضح";
}


/* =========================================================
   CATEGORY LABEL
========================================================= */

function getCategoryLabel(category) {

    switch (normalizeCategory(category)) {

        case "morocco":
            return "أخبار المغرب";

        case "middle_east":
            return "الشرق الأوسط";

        case "world_arabic":
            return "العالم";

        case "sports":
            return "الرياضة";

        case "transfers":
            return "الانتقالات";

        default:
            return "أخبار";
    }
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
           ترتيب الأخبار من الأحدث إلى الأقدم
        */

        allNews.sort(
            (a, b) => {

                const dateA =
                    new Date(
                        a.published ||
                        a.discovered ||
                        0
                    ).getTime();

                const dateB =
                    new Date(
                        b.published ||
                        b.discovered ||
                        0
                    ).getTime();

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


        console.log(
            `Loaded ${allNews.length} news items`
        );


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

            const category =
                getNewsCategory(item);

            const status =
                getNewsStatus(item);


            const text = [

                item.title,

                item.summary,

                item.source,

                item.player,

                item.category,

                item.section,

                category,

                status

            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();


            const categoryMatch =

                currentCategory === "all" ||

                category ===
                currentCategory;


            const statusMatch =

                currentStatus === "all" ||

                status ===
                currentStatus;


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
        getElement("newsGrid");

    const empty =
        getElement("emptyState");


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
        getElement("loadMore");


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
   NEWS CARD
========================================================= */

function renderNewsCard(item) {

    const status =
        getNewsStatus(item);


    const category =
        getNewsCategory(item);


    let statusClass = "";


    if (status === "رسمي") {

        statusClass =
            "official";

    } else if (
        status === "إشاعة"
    ) {

        statusClass =
            "rumor";

    } else if (
        status === "مؤكد"
    ) {

        statusClass =
            "confirmed";
    }


    return `

        <article
            class="news-card"
            data-category="${escapeHTML(category)}"
        >

            <div class="news-top">

                <span class="news-source">

                    ${escapeHTML(
                        item.source ||
                        "مصدر غير معروف"
                    )}

                </span>


                <span
                    class="news-status ${statusClass}"
                >

                    ${escapeHTML(status)}

                </span>

            </div>


            <div class="news-category">

                ${escapeHTML(
                    getCategoryLabel(category)
                )}

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

                        <div
                            class="news-player"
                        >

                            ⚽
                            ${escapeHTML(
                                item.player
                            )}

                        </div>

                    `
                    : ""
            }


            <p
                class="news-summary"
            >

                ${escapeHTML(
                    item.summary ||
                    ""
                )}

            </p>


            <div
                class="news-footer"
            >

                <span
                    class="news-time"
                >

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


/* =========================================================
   HERO
========================================================= */

function updateHero() {

    const hero =
        allNews[0];


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
        getElement("heroLink");


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
   BREAKING NEWS
========================================================= */

function updateBreaking() {

    const element =
        getElement(
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

    const container =
        getElement("sourcesList");


    if (!container) {
        return;
    }


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

    const container =
        getElement(
            "playersList"
        );


    if (!container) {
        return;
    }


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
            .slice(0, 6);


    if (!players.length) {

        container.innerHTML = `

            <p
                class="news-summary"
            >

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
                getNewsCategory(item) ===
                "morocco"
        ).length;


    const middleEast =
        allNews.filter(
            item =>
                getNewsCategory(item) ===
                "middle_east"
        ).length;


    const world =
        allNews.filter(
            item =>
                getNewsCategory(item) ===
                "world_arabic"
        ).length;


    const sport =
        allNews.filter(
            item =>
                getNewsCategory(item) ===
                "sports"
        ).length;


    const transfers =
        allNews.filter(
            item =>
                getNewsCategory(item) ===
                "transfers"
        ).length;


    const official =
        allNews.filter(
            item =>
                item.status ===
                "رسمي"
        ).length;


    const confirmed =
        allNews.filter(
            item =>
                item.status ===
                "مؤكد"
        ).length;


    const negotiation =
        allNews.filter(
            item =>
                item.status ===
                "مفاوضات"
        ).length;


    const rumor =
        allNews.filter(
            item =>
                item.status ===
                "إشاعة"
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
        world
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
   CATEGORY BUTTONS
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
   STATUS FILTERS
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
   CATEGORY EVENTS
========================================================= */

function setupCategoryEvents() {

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
   SEARCH
========================================================= */

function setupSearch() {

    const input =
        getElement(
            "searchInput"
        );


    if (input) {

        input.addEventListener(
            "input",
            event => {

                searchTerm =
                    event.target.value.trim();


                applyFilters();
            }
        );
    }


    const clear =
        getElement(
            "clearSearch"
        );


    if (clear) {

        clear.addEventListener(
            "click",
            () => {

                if (input) {
                    input.value = "";
                }


                searchTerm = "";

                applyFilters();
            }
        );
    }
}


/* =========================================================
   LOAD MORE
========================================================= */

function setupLoadMore() {

    const button =
        getElement(
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
        getElement(
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
        getElement(
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
        }
    );
}


/* =========================================================
   MOBILE MENU
========================================================= */

function closeMobileMenu() {

    const menu =
        getElement(
            "mobileMenu"
        );


    if (!menu) {
        return;
    }


    menu.classList.remove(
        "open"
    );
}


function setupMobileMenu() {

    const menu =
        getElement(
            "mobileMenu"
        );


    const openButton =
        getElement(
            "menuBtn"
        );


    const closeButton =
        getElement(
            "closeMenu"
        );


    if (
        menu &&
        openButton
    ) {

        openButton.addEventListener(
            "click",
            () => {

                menu.classList.add(
                    "open"
                );
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


/* =========================================================
   EMPTY STATE
========================================================= */

function showEmptyState(message) {

    const empty =
        getElement(
            "emptyState"
        );


    if (!empty) {
        return;
    }


    empty.classList.remove(
        "hidden"
    );


    const title =
        empty.querySelector(
            "h2"
        );


    if (title) {

        title.textContent =
            message;
    }
}


/* =========================================================
   TOAST
========================================================= */

function showToastMessage(message) {

    const toast =
        getElement(
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

function updateFooterYear() {

    setText(
        "footerYear",
        new Date().getFullYear()
    );
}


/* =========================================================
   INITIALIZE
========================================================= */

function initializeApp() {

    updateFooterYear();

    setupStatusFilters();

    setupCategoryEvents();

    setupSearch();

    setupLoadMore();

    setupRefresh();

    setupTheme();

    setupMobileMenu();

    loadNews();
}


/* =========================================================
   START
========================================================= */

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
