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
# NEWS TERMS
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

    "رياضة",
    "رياضات",
    "كرة القدم",
    "كرة السلة",
    "منتخب",
    "مباراة",
    "مباريات",
    "لاعب",
    "مدرب",
    "دوري",
    "كأس",
    "بطولة",

    "انتقال",
    "انتقالات",
    "مفاوضات",
    "توقيع",
    "إعارة",
]


# ============================================================
# TRANSFER TERMS
# ============================================================

LOCAL_TRANSFER_TERMS = [
    "انتقال",
    "انتقالات",
    "صفقة",
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
# SPORT TERMS
# ============================================================

LOCAL_SPORT_TERMS = [
    "رياضة",
    "رياضي",
    "رياضات",
    "كرة القدم",
    "كرة السلة",
    "كرة اليد",

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
# TEXT HELPERS
# ============================================================

def clean_text(value):
    """
    تنظيف النص من HTML والمسافات الزائدة.
    """

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
    """
    توحيد النص العربي والإنجليزي للمقارنة.
    """

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
    """
    التحقق من وجود أي كلمة من القائمة.
    """

    for term in terms:

        normalized_term = normalize_text(term)

        if (
            normalized_term
            and normalized_term in text
        ):
            return True

    return False


def contains_player(text):
    """
    البحث عن لاعب مغربي.
    """

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
    """
    تجميع العنوان والوصف والملخص.
    """

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
    """
    منع العقار والإعلانات التجارية الواضحة.
    """

    if contains_any(
        text,
        BLOCKED_TERMS
    ):
        return True

    commercial_matches = 0

    for term in COMMERCIAL_TERMS:

        normalized_term = normalize_text(
            term
        )

        if (
            normalized_term
            and normalized_term in text
        ):
            commercial_matches += 1

    return commercial_matches >= 2


# ============================================================
# NEWS DETECTION
# ============================================================

def looks_like_news(text):
    """
    تحديد ما إذا كان المحتوى يبدو كخبر.
    """

    if not text:
        return False

    if is_blocked_content(text):
        return False

    return (
        contains_any(
            text,
            NEWS_TERMS
        )
        or contains_any(
            text,
            LOCAL_SPORT_TERMS
        )
        or contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        )
        or contains_player(text)
    )


# ============================================================
# SOURCE GROUP
# ============================================================

def source_group(
    source_name,
    configured_group=None
):
    """
    تحديد مجموعة المصدر.

    نستخدم المجموعة القادمة من sources.py
    أولًا، ثم نستخدم fallback بالاسم.
    """

    if configured_group in VALID_GROUPS:
        return configured_group

    fallback_groups = {
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

        "الجزيرة": "middle_east",
        "العربية": "middle_east",
        "سكاي نيوز عربية": "middle_east",
        "الشرق للأخبار": "middle_east",
        "الشرق الأوسط": "middle_east",
        "العربي الجديد": "middle_east",

        "القدس العربي": "world_arabic",
        "فرانس 24 عربي": "world_arabic",
        "DW عربية": "world_arabic",
        "BBC عربي": "world_arabic",
        "يورونيوز عربي": "world_arabic",
        "إندبندنت عربية": "world_arabic",
        "CNN بالعربية": "world_arabic",

        "كووورة": "arabic_sports",
        "WinWin": "arabic_sports",
        "في الجول": "arabic_sports",
        "يلا كورة": "arabic_sports",

        "كووورة انتقالات": "arabic_transfers",
        "WinWin ميركاتو": "arabic_transfers",
        "في الجول انتقالات": "arabic_transfers",
        "ميركاتو داي": "arabic_transfers",

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
    """
    تحديد ما إذا كان الخبر مناسبًا للنظام.
    """

    text = item_text(entry)

    if not text:
        return False

    # منع العقار والإعلانات
    if is_blocked_content(text):
        return False

    group = source_group(
        source_name,
        configured_group
    )

    # ========================================================
    # 🇲🇦 المغرب
    # ========================================================

    if group == "morocco":

        if contains_any(
            text,
            MOROCCO_TERMS
        ):
            return True

        if contains_player(text):
            return True

        if contains_any(
            text,
            LOCAL_SPORT_TERMS
        ):
            return True

        return False

    # ========================================================
    # ⚽ الرياضة العربية
    # ========================================================

    if group == "arabic_sports":

        if contains_player(text):
            return True

        if contains_any(
            text,
            MOROCCO_TERMS
        ):
            return True

        if contains_any(
            text,
            LOCAL_SPORT_TERMS
        ):
            return True

        if contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        ):
            return True

        return False

    # ========================================================
    # 🔄 انتقالات اللاعبين
    # ========================================================

    if group == "arabic_transfers":

        # أولوية للاعبين المغاربة
        if contains_player(text):
            return True

        # أخبار انتقالات مرتبطة بالمغرب
        if contains_any(
            text,
            MOROCCO_TERMS
        ):
            return True

        # أخبار الميركاتو
        if contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        ):
            return True

        return False

    # ========================================================
    # 🌍 الشرق الأوسط
    # ========================================================

    if group == "middle_east":

        if contains_any(
            text,
            MOROCCO_TERMS
        ):
            return True

        if contains_player(text):
            return True

        if contains_any(
            text,
            LOCAL_SPORT_TERMS
        ):
            return True

        if contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        ):
            return True

        return False

    # ========================================================
    # 🌐 العالم العربي
    # ========================================================

    if group == "world_arabic":

        if contains_any(
            text,
            MOROCCO_TERMS
        ):
            return True

        if contains_player(text):
            return True

        if contains_any(
            text,
            LOCAL_SPORT_TERMS
        ):
            return True

        if contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        ):
            return True

        return False

    # ========================================================
    # 🔎 المصادر الدولية
    # ========================================================

    if group == "international":

        if contains_any(
            text,
            MOROCCO_TERMS
        ):
            return True

        if contains_player(text):
            return True

        if contains_any(
            text,
            LOCAL_TRANSFER_TERMS
        ):
            return True

        return False

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
    """
    جلب RSS من Google News.
    """

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
    """
    استخراج تاريخ الخبر.
    """

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
    """
    إنشاء بصمة للمحتوى.
    """

    raw = normalize_text(
        f"{title}|{summary}"
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# COLLECT
# ============================================================

def collect():

    new_items = []

    total_seen = 0
    total_blocked = 0
    total_relevant = 0

    print("=" * 60)
    print("Morocco News AI - News Collector")
    print("=" * 60)

    # ========================================================
    # SOURCES
    # ========================================================

    for source in SOURCES:

        # ----------------------------------------------------
        # صيغة المصدر الجديدة:
        #
        # (
        #     name,
        #     url,
        #     trust,
        #     group
        # )
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # RSS
        # ----------------------------------------------------

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

            if exists(url):
                continue

            # ------------------------------------------------
            # Text
            # ------------------------------------------------

            text = normalize_text(
                f"{title} "
                f"{summary} "
                f"{description}"
            )

            # ------------------------------------------------
            # Blocked
            # ------------------------------------------------

            if is_blocked_content(text):

                total_blocked += 1

                print(
                    f"  BLOCKED: "
                    f"{title[:100]}"
                )

                continue

            # ------------------------------------------------
            # Relevance
            # ------------------------------------------------

            if not relevant(
                entry,
                name,
                configured_group
            ):

                continue

            total_relevant += 1

            # ------------------------------------------------
            # Item
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

                "content_hash": make_content_hash(
                    title,
                    summary
                ),

                "source_group": configured_group,
            }

            # ------------------------------------------------
            # Classification
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
            # Save
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
