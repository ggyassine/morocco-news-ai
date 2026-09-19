import feedparser
import hashlib
import html
import re

from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from sources import (
    SOURCES,
    MOROCCO_TERMS,
    MOROCCAN_PLAYERS,
    TRANSFER_TERMS,
    SPORT_TERMS,
)

from db import exists, add
from classifier import classify
from config import MAX_ITEMS_PER_SOURCE


# ============================================================
# SOURCE GROUPS
# ============================================================

VALID_GROUPS = {
    "morocco",
    "middle_east",
    "world_arabic",
    "arabic_sports",
    "arabic_transfers",
    "international",
}


# ============================================================
# BLOCKED CONTENT
# ============================================================

BLOCKED_TERMS = [
    "immobilier",
    "immobilière",
    "immobiliere",

    "عقار",
    "عقارات",
    "شقة للبيع",
    "شقق للبيع",
    "منزل للبيع",
    "دار للبيع",
    "أرض للبيع",
    "بقعة للبيع",
    "كراء",
    "للإيجار",
    "للبيع",

    "résidence",
    "appartement",
    "villa",
    "maison",
    "terrain",
    "location",

    "promotion immobilière",
    "promoteur immobilier",
]


COMMERCIAL_TERMS = [
    "promo",
    "promotion",
    "offre spéciale",
    "offre commerciale",
    "shopping",
    "boutique",
    "catalogue",

    "منتج",
    "منتجات",
    "تخفيض",
    "تخفيضات",
    "تسوق",
    "متجر",
    "إعلان تجاري",
]


# ============================================================
# GENERAL NEWS TERMS
# ============================================================

NEWS_TERMS = [
    "المغرب",
    "مغربي",
    "مغربية",

    "الرباط",
    "الدار البيضاء",
    "طنجة",
    "فاس",
    "مراكش",
    "أكادير",
    "وجدة",

    "الحكومة",
    "البرلمان",
    "مجلس النواب",
    "مجلس المستشارين",
    "وزارة",
    "وزير",
    "رئيس الحكومة",

    "سياسة",
    "سياسي",
    "اقتصاد",
    "اقتصادي",

    "اجتماع",
    "اجتماعات",
    "قرار",
    "قرارات",

    "مشروع قانون",
    "قانون",
    "انتخابات",

    "أمن",
    "شرطة",
    "قضاء",
    "محكمة",
    "حادث",
    "حريق",
    "زلزال",
    "فيضانات",
    "طقس",

    "تعليم",
    "جامعة",
    "صحة",
    "ثقافة",
    "فن",
    "سينما",

    "سياحة",
    "سياحي",
    "سياح",
]


# ============================================================
# FOOTBALL TERMS
# ============================================================

FOOTBALL_TERMS = [
    "كرة القدم",
    "كرة القدم المغربية",
    "منتخب",
    "المنتخب",
    "لاعب",
    "لاعبين",
    "مدرب",
    "مباراة",
    "مباريات",
    "دوري",
    "الدوري",
    "كأس",
    "بطولة",
    "نادي",
    "أندية",
    "فريق",
    "فرق",
    "هدف",
    "أهداف",
    "فوز",
    "هزيمة",
    "تعادل",

    "دوري أبطال أوروبا",
    "دوري أبطال",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الإيطالي",
    "الدوري الفرنسي",
    "الدوري الألماني",

    "البريميرليغ",
    "لاليغا",
    "الليغا",
    "السيري آ",
    "الليغ 1",
    "البوندسليغا",

    "كأس العالم",
    "كأس أمم إفريقيا",
    "كأس إفريقيا",
    "تصفيات كأس العالم",
    "تصفيات المونديال",

    "champions league",
    "football",
    "soccer",
    "premier league",
    "la liga",
    "serie a",
    "ligue 1",
    "bundesliga",
]


# ============================================================
# SPORT TERMS
# ============================================================

LOCAL_SPORT_TERMS = [
    "رياضة",
    "رياضي",
    "رياضات",
    "كرة القدم",
    "كرة السلة",
    "كرة اليد",
    "تنس",
    "فورمولا",
    "ملاكمة",

    "منتخب",
    "مباراة",
    "مباريات",
    "دوري",
    "كأس",
    "بطولة",
    "لاعب",
    "مدرب",

    "هدف",
    "أهداف",
    "فوز",
    "هزيمة",
    "تعادل",

    "دوري أبطال",
    "دوري الأبطال",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الإيطالي",
    "الدوري الفرنسي",
    "الدوري الألماني",

    "البريميرليغ",
    "لاليغا",
    "الليغا",
    "السيري آ",
    "الليغ 1",
    "البوندسليغا",

    "champions",
    "football",
    "sport",
    "match",
    "league",
    "cup",
]


# ============================================================
# TRANSFER TERMS
# ============================================================

LOCAL_TRANSFER_TERMS = [
    "انتقال",
    "انتقالات",
    "صفقة",
    "صفقات",
    "توقيع",
    "يوقع",
    "وقع",
    "ضم",
    "إعارة",
    "إعاره",
    "مفاوضات",
    "اهتمام",
    "عرض",
    "عقد",
    "تجديد",
    "رحيل",
    "مغادرة",
    "وجهة",
    "ميركاتو",
    "سوق الانتقالات",

    "transfer",
    "transfers",
    "transfert",
    "transferts",
    "mercato",
    "signing",
    "signed",
    "loan",
    "contract",
    "renewal",
    "negotiation",
    "interest",
    "offer",
]


# ============================================================
# MOROCCAN FOOTBALL TERMS
# ============================================================

MOROCCAN_FOOTBALL_TERMS = [
    "المغرب",
    "المغربي",
    "المغربية",
    "مغربي",
    "مغربية",

    "أسود الأطلس",
    "المنتخب المغربي",
    "المنتخب الوطني",
    "الجامعة الملكية المغربية لكرة القدم",
    "الدوري المغربي",
    "البطولة المغربية",
    "الوداد",
    "الرجاء",
    "نهضة بركان",
    "الجيش الملكي",
    "الفتح الرباطي",
    "المغرب الفاسي",
    "أولمبيك آسفي",
    "حسنية أكادير",
]


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_text(value):
    if not value:
        return ""

    value = html.unescape(str(value))

    value = re.sub(
        r"<[^>]+>",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def normalize_text(value):
    value = clean_text(value).lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value


def contains_any(text, terms):
    for term in terms:

        normalized_term = normalize_text(term)

        if (
            normalized_term
            and normalized_term in text
        ):
            return True

    return False


def count_matches(text, terms):
    count = 0

    for term in terms:

        normalized_term = normalize_text(term)

        if (
            normalized_term
            and normalized_term in text
        ):
            count += 1

    return count


def contains_player(text):
    for player in MOROCCAN_PLAYERS:

        player_normalized = normalize_text(
            player
        )

        if (
            player_normalized
            and player_normalized in text
        ):
            return True

    return False


def item_text(entry):
    title = clean_text(
        entry.get("title", "")
    )

    summary = clean_text(
        entry.get("summary", "")
    )

    description = clean_text(
        entry.get("description", "")
    )

    return normalize_text(
        f"{title} {summary} {description}"
    )


# ============================================================
# BLOCKED CONTENT
# ============================================================

def is_blocked_content(text):

    if contains_any(
        text,
        BLOCKED_TERMS
    ):
        return True

    commercial_matches = count_matches(
        text,
        COMMERCIAL_TERMS
    )

    return commercial_matches >= 2


# ============================================================
# NEWS DETECTION
# ============================================================

def looks_like_news(text):

    if not text:
        return False

    if is_blocked_content(text):
        return False

    return (
        contains_any(text, NEWS_TERMS)
        or contains_any(text, LOCAL_SPORT_TERMS)
        or contains_any(text, LOCAL_TRANSFER_TERMS)
        or contains_player(text)
    )


# ============================================================
# SOURCE GROUP
# ============================================================

def source_group(
    source_name,
    configured_group=None
):

    if configured_group in VALID_GROUPS:
        return configured_group

    fallback_groups = {

        # Morocco
        "MAP عربي": "morocco",
        "SNRTnews عربي": "morocco",
        "هسبريس": "morocco",
        "Le360 عربي": "morocco",
        "العمق المغربي": "morocco",
        "اليوم24": "morocco",
        "أخبارنا المغربية": "morocco",
        "هبة بريس": "morocco",
        "برلمان": "morocco",
        "كود": "morocco",
        "كفاش": "morocco",
        "فبراير": "morocco",
        "البطولة": "morocco",
        "المنتخب": "morocco",

        # Middle East
        "الجزيرة": "middle_east",
        "العربية": "middle_east",
        "سكاي نيوز عربية": "middle_east",
        "الشرق للأخبار": "middle_east",
        "الشرق الأوسط": "middle_east",
        "العربي الجديد": "middle_east",

        # World Arabic
        "القدس العربي": "world_arabic",
        "فرانس 24 عربي": "world_arabic",
        "DW عربية": "world_arabic",
        "BBC عربي": "world_arabic",
        "يورونيوز عربي": "world_arabic",
        "إندبندنت عربية": "world_arabic",
        "CNN بالعربية": "world_arabic",

        # Arabic sports
        "كووورة": "arabic_sports",
        "WinWin": "arabic_sports",
        "في الجول": "arabic_sports",
        "يلا كورة": "arabic_sports",
        "365Scores عربي": "arabic_sports",
        "العين الرياضية": "arabic_sports",

        # Arabic transfers
        "كووورة انتقالات": "arabic_transfers",
        "WinWin ميركاتو": "arabic_transfers",
        "في الجول انتقالات": "arabic_transfers",
        "ميركاتو داي": "arabic_transfers",
        "365Scores انتقالات": "arabic_transfers",
        "العربية رياضة انتقالات": "arabic_transfers",

        # International
        "Reuters": "international",
        "Associated Press": "international",
    }

    return fallback_groups.get(
        source_name,
        "other"
    )


# ============================================================
# RELEVANCE
# ============================================================

def relevant(
    entry,
    source_name,
    configured_group=None
):

    text = item_text(entry)

    if not text:
        return False

    if is_blocked_content(text):
        return False

    group = source_group(
        source_name,
        configured_group
    )

    # ========================================================
    # MOROCCO
    # ========================================================

    if group == "morocco":

        return (
            contains_any(text, MOROCCO_TERMS)
            or contains_player(text)
            or contains_any(text, LOCAL_SPORT_TERMS)
        )

    # ========================================================
    # ARABIC SPORTS
    # ========================================================

    if group == "arabic_sports":

        # اللاعبون المغاربة
        if contains_player(text):
            return True

        # المنتخب والأندية المغربية
        if contains_any(
            text,
            MOROCCAN_FOOTBALL_TERMS
        ):
            return True

        # الأخبار الرياضية المهمة
        if contains_any(
            text,
            LOCAL_SPORT_TERMS
        ):
            return True

        return False

    # ========================================================
    # ARABIC TRANSFERS
    # ========================================================

    if group == "arabic_transfers":

        # لاعب مغربي + انتقال
        if (
            contains_player(text)
            and contains_any(
                text,
                LOCAL_TRANSFER_TERMS
            )
        ):
            return True

        # انتقال مرتبط بالمغرب
        if (
            contains_any(
                text,
                MOROCCAN_FOOTBALL_TERMS
            )
            and contains_any(
                text,
                LOCAL_TRANSFER_TERMS
            )
        ):
            return True

        # مصادر الانتقالات المتخصصة
        if contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        ):

            # نفضل الأخبار التي لها علاقة بكرة القدم
            if (
                contains_any(
                    text,
                    FOOTBALL_TERMS
                )
                or contains_any(
                    text,
                    LOCAL_SPORT_TERMS
                )
            ):
                return True

        return False

    # ========================================================
    # MIDDLE EAST
    # ========================================================

    if group == "middle_east":

        return (
            contains_any(text, MOROCCO_TERMS)
            or contains_player(text)
            or contains_any(text, LOCAL_SPORT_TERMS)
            or contains_any(text, LOCAL_TRANSFER_TERMS)
        )

    # ========================================================
    # WORLD ARABIC
    # ========================================================

    if group == "world_arabic":

        return (
            contains_any(text, MOROCCO_TERMS)
            or contains_player(text)
            or contains_any(text, LOCAL_SPORT_TERMS)
            or contains_any(text, LOCAL_TRANSFER_TERMS)
        )

    # ========================================================
    # INTERNATIONAL
    # ========================================================

    if group == "international":

        return (
            contains_any(text, MOROCCO_TERMS)
            or contains_player(text)
            or (
                contains_any(
                    text,
                    LOCAL_TRANSFER_TERMS
                )
                and contains_any(
                    text,
                    FOOTBALL_TERMS
                )
            )
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    return (
        contains_any(
            text,
            MOROCCO_TERMS
        )
        or contains_player(text)
    )


# ============================================================
# RSS FETCH
# ============================================================

def fetch_feed(url):

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; MoroccoNewsAI/1.0)"
            )
        }
    )

    try:

        with urlopen(
            request,
            timeout=20
        ) as response:

            data = response.read()

        return feedparser.parse(data)

    except HTTPError as error:

        print(
            f"HTTP error while fetching {url}: "
            f"{error.code}"
        )

        return None

    except URLError as error:

        print(
            f"URL error while fetching {url}: "
            f"{error}"
        )

        return None

    except Exception as error:

        print(
            f"Feed error while fetching {url}: "
            f"{error}"
        )

        return None


# ============================================================
# DATE
# ============================================================

def published_date(entry):

    for field in (
        "published",
        "updated",
        "created",
    ):

        value = entry.get(field)

        if value:
            return value

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# CONTENT HASH
# ============================================================

def make_content_hash(
    title,
    summary
):

    raw = normalize_text(
        f"{title}|{summary}"
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# SIMILARITY KEY
# ============================================================

def make_title_key(title):

    text = normalize_text(title)

    # إزالة أسماء المواقع في نهاية العنوان
    text = re.sub(
        r"\s*[-|]\s*(winwin|kooora|filgoal|365scores|bbc|reuters).*$",
        "",
        text,
        flags=re.IGNORECASE
    )

    # إزالة علامات الترقيم
    text = re.sub(
        r"[^\w\s\u0600-\u06FF]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# COLLECT
# ============================================================

def collect():

    new_items = []

    total_seen = 0
    total_blocked = 0
    total_relevant = 0

    # منع التكرار داخل نفس الدورة
    seen_urls = set()
    seen_title_keys = set()

    print("=" * 60)
    print("Morocco News AI - News Collector")
    print("=" * 60)

    # ========================================================
    # SOURCES
    # ========================================================

    for source in SOURCES:

        if not isinstance(
            source,
            (tuple, list)
        ):

            print(
                f"Invalid source configuration: {source}"
            )

            continue

        if len(source) != 4:

            print(
                f"Invalid source configuration: {source}"
            )

            continue

        name = source[0]
        rss_url = source[1]
        trust = source[2]
        configured_group = source[3]

        if not name or not rss_url:

            print(
                f"Invalid source configuration: {source}"
            )

            continue

        if configured_group not in VALID_GROUPS:

            print(
                f"Invalid source group: {source}"
            )

            continue

        print()
        print(
            f"[SOURCE] {name}"
        )

        print(
            f"  Group: {configured_group}"
        )

        # ====================================================
        # RSS
        # ====================================================

        feed = fetch_feed(
            rss_url
        )

        if not feed:

            print(
                "  Feed unavailable"
            )

            continue

        entries = feed.entries[
            :MAX_ITEMS_PER_SOURCE
        ]

        source_count = 0

        # ====================================================
        # ENTRIES
        # ====================================================

        for entry in entries:

            total_seen += 1

            title = clean_text(
                entry.get(
                    "title",
                    ""
                )
            )

            url = (
                entry.get("link")
                or entry.get("url")
                or ""
            )

            summary = clean_text(
                entry.get(
                    "summary",
                    ""
                )
            )

            description = clean_text(
                entry.get(
                    "description",
                    ""
                )
            )

            if not title or not url:
                continue

            # ------------------------------------------------
            # URL duplicate
            # ------------------------------------------------

            if url in seen_urls:
                continue

            seen_urls.add(url)

            if exists(url):
                continue

            # ------------------------------------------------
            # TITLE duplicate
            # ------------------------------------------------

            title_key = make_title_key(
                title
            )

            if (
                title_key
                and title_key in seen_title_keys
            ):
                continue

            seen_title_keys.add(
                title_key
            )

            # ------------------------------------------------
            # TEXT
            # ------------------------------------------------

            text = normalize_text(
                f"{title} "
                f"{summary} "
                f"{description}"
            )

            # ------------------------------------------------
            # BLOCKED
            # ------------------------------------------------

            if is_blocked_content(text):

                total_blocked += 1

                print(
                    f"  BLOCKED: "
                    f"{title[:100]}"
                )

                continue

            # ------------------------------------------------
            # RELEVANCE
            # ------------------------------------------------

            if not relevant(
                entry,
                name,
                configured_group
            ):

                continue

            total_relevant += 1

            # ------------------------------------------------
            # CONTENT HASH
            # ------------------------------------------------

            content_hash = make_content_hash(
                title,
                summary
            )

            # ------------------------------------------------
            # ITEM
            # ------------------------------------------------

            item = {

                "title": title,

                "url": url,

                "source": name,

                "trust": trust,

                "published": published_date(
                    entry
                ),

                "discovered": datetime.now(
                    timezone.utc
                ).isoformat(),

                "summary": summary,

                "description": description,

                "content_hash": content_hash,

                "source_group": configured_group,
            }

            # ------------------------------------------------
            # CLASSIFICATION
            # ------------------------------------------------

            try:

                classified = classify(
                    item
                )

                if classified:

                    item.update(
                        classified
                    )

            except Exception as error:

                print(
                    "  Classification error: "
                    f"{error}"
                )

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            try:

                add(item)

                new_items.append(
                    item
                )

                source_count += 1

                print(
                    f"  + {title[:100]}"
                )

            except Exception as error:

                print(
                    "  Database error: "
                    f"{error}"
                )

        print(
            f"  New items: {source_count}"
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("COLLECTION SUMMARY")
    print("=" * 60)

    print(
        f"Items scanned: {total_seen}"
    )

    print(
        f"Blocked items: {total_blocked}"
    )

    print(
        f"Relevant items: {total_relevant}"
    )

    print(
        f"New items saved: {len(new_items)}"
    )

    print("=" * 60)

    return new_items
