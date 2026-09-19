import feedparser
import hashlib
import html
import re

from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from sources import SOURCES, MOROCCO_TERMS, MOROCCAN_PLAYERS
from db import exists, add
from classifier import classify
from config import MAX_ITEMS_PER_SOURCE


# ============================================================
# SOURCE GROUPS
# ============================================================

MOROCCO_SOURCES = {
    "MAP عربي",
    "SNRTnews عربي",
    "هسبريس",
    "Le360 عربي",
    "العمق المغربي",
    "اليوم24",
    "أخبارنا المغربية",
    "هبة بريس",
    "برلمان",
    "كود",
    "كفاش",
    "فبراير",
    "البطولة",
    "المنتخب",
}

MIDDLE_EAST_SOURCES = {
    "الجزيرة",
    "العربية",
    "سكاي نيوز عربية",
    "الشرق للأخبار",
    "الشرق الأوسط",
    "العربي الجديد",
}

WORLD_ARABIC_SOURCES = {
    "القدس العربي",
    "فرانس 24 عربي",
    "DW عربية",
    "BBC عربي",
    "يورونيوز عربي",
    "إندبندنت عربية",
    "CNN بالعربية",
}

INTERNATIONAL_SOURCES = {
    "Reuters",
    "Associated Press",
}


# ============================================================
# BLOCKED CONTENT
# ============================================================

# كلمات غالبًا تدل على عقار أو إعلان أو محتوى تجاري
BLOCKED_TERMS = [
    "immobilier",
    "immobilière",
    "immobilier",
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
    "للبيع",
    "ثمن المتر",
    "متر مربع",
    "غرف",
    "غرفة",
    "résidence",
    "appartement",
    "villa",
    "maison",
    "terrain",
    "location",
    "annonce",
    "annonces",
    "promotion immobilière",
    "promoteur immobilier",
]

# كلمات تشير غالبًا إلى إعلانات أو محتوى تجاري
COMMERCIAL_TERMS = [
    "promo",
    "promotion",
    "offre spéciale",
    "offre commerciale",
    "shopping",
    "boutique",
    "catalogue",
    "produit",
    "produits",
    "prix",
    "acheter",
    "achat",
    "vente",
    "service commercial",
    "إعلان",
    "إعلانات",
    "عرض خاص",
    "منتج",
    "منتجات",
    "تخفيض",
    "تخفيضات",
    "تسوق",
    "متجر",
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
    "مجلس",
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
    "كرة القدم",
    "كرة السلة",
    "منتخب",
    "الوداد",
    "الرجاء",
    "الجيش الملكي",
    "نهضة بركان",
    "البطولة",
    "دوري",
    "كأس",
    "مباراة",
    "لاعب",
    "مدرب",
    "انتقال",
    "مفاوضات",
    "توقيع",
    "إعارة",
]


TRANSFER_TERMS = [
    "transfer",
    "transfers",
    "transfert",
    "transferts",
    "mercato",
    "انتقال",
    "انتقالات",
    "مفاوضات",
    "عرض",
    "توقيع",
    "يوقع",
    "وقع",
    "إعارة",
    "إعاره",
    "اهتمام",
    "يرغب",
    "صفقة",
    "عقد",
    "تجديد",
    "رحيل",
    "مغادرة",
    "وجهة",
]


SPORT_TERMS = [
    "رياضة",
    "رياضي",
    "كرة القدم",
    "كرة السلة",
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
    "champions",
    "football",
    "sport",
    "match",
    "league",
    "cup",
]


# ============================================================
# HELPERS
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
    توحيد النص لتسهيل المقارنة.
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


def item_text(entry):
    """
    يجمع العنوان والوصف والمصدر في نص واحد.
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


def contains_any(text, terms):
    """
    هل يحتوي النص على واحدة من الكلمات؟
    """

    for term in terms:

        normalized_term = normalize_text(term)

        if normalized_term and normalized_term in text:
            return True

    return False


def contains_player(text):
    """
    البحث عن لاعب مغربي معروف في الخبر.
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


def is_blocked_content(text):
    """
    منع المحتوى العقاري والتجاري.
    """

    if contains_any(text, BLOCKED_TERMS):
        return True

    # نمنع المحتوى التجاري عندما تظهر عدة مؤشرات تجارية
    commercial_matches = 0

    for term in COMMERCIAL_TERMS:

        normalized_term = normalize_text(term)

        if (
            normalized_term
            and normalized_term in text
        ):
            commercial_matches += 1

    return commercial_matches >= 2


def looks_like_news(text):
    """
    التحقق من أن المحتوى يبدو خبرًا وليس إعلانًا.
    """

    if not text:
        return False

    if is_blocked_content(text):
        return False

    return contains_any(
        text,
        NEWS_TERMS
    )


def source_group(source):
    """
    تحديد مجموعة المصدر.
    """

    if source in MOROCCO_SOURCES:
        return "morocco"

    if source in MIDDLE_EAST_SOURCES:
        return "middle_east"

    if source in WORLD_ARABIC_SOURCES:
        return "world_arabic"

    if source in INTERNATIONAL_SOURCES:
        return "international"

    return "other"


# ============================================================
# RELEVANCE
# ============================================================

def relevant(entry, source):
    """
    تحديد ما إذا كان الخبر يستحق الدخول إلى النظام.
    """

    text = item_text(entry)

    if not text:
        return False

    # أولًا: منع الإعلانات والعقار
    if is_blocked_content(text):
        return False

    group = source_group(source)

    # --------------------------------------------------------
    # المصادر المغربية
    # --------------------------------------------------------

    if group == "morocco":

        # يجب أن يكون الخبر مرتبطًا بالمغرب
        # أو بلاعب مغربي
        if (
            contains_any(text, MOROCCO_TERMS)
            or contains_player(text)
        ):
            return True

        # أخبار الرياضة المغربية
        if contains_any(text, SPORT_TERMS):
            return True

        return False

    # --------------------------------------------------------
    # الشرق الأوسط
    # --------------------------------------------------------

    if group == "middle_east":

        # نأخذ فقط الأخبار التي لها صلة بالمغرب
        # أو الرياضة أو اللاعبين المغاربة
        if contains_any(text, MOROCCO_TERMS):
            return True

        if contains_player(text):
            return True

        if contains_any(text, TRANSFER_TERMS):
            return True

        return False

    # --------------------------------------------------------
    # العالم العربي
    # --------------------------------------------------------

    if group == "world_arabic":

        if contains_any(text, MOROCCO_TERMS):
            return True

        if contains_player(text):
            return True

        if contains_any(text, TRANSFER_TERMS):
            return True

        return False

    # --------------------------------------------------------
    # Reuters / AP
    # --------------------------------------------------------

    if group == "international":

        if contains_any(text, MOROCCO_TERMS):
            return True

        if contains_player(text):
            return True

        if contains_any(text, TRANSFER_TERMS):
            return True

        return False

    # --------------------------------------------------------
    # fallback
    # --------------------------------------------------------

    return (
        contains_any(text, MOROCCO_TERMS)
        or contains_player(text)
    )


# ============================================================
# RSS
# ============================================================

def fetch_feed(url):
    """
    جلب RSS مع User-Agent مناسب.
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
    استخراج تاريخ النشر.
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
# HASH
# ============================================================

def make_content_hash(title, summary):
    """
    إنشاء بصمة للمحتوى لمنع التكرار.
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

    for source in SOURCES:

        try:

            name = source["name"]
            rss_url = source["url"]

        except Exception:

            print(
                f"Invalid source configuration: {source}"
            )

            continue

        print()
        print(f"[SOURCE] {name}")

        feed = fetch_feed(rss_url)

        if not feed:

            print("  Feed unavailable")
            continue

        entries = feed.entries[
            :MAX_ITEMS_PER_SOURCE
        ]

        source_count = 0

        for entry in entries:

            total_seen += 1

            title = clean_text(
                entry.get("title", "")
            )

            url = (
                entry.get("link")
                or entry.get("url")
                or ""
            )

            summary = clean_text(
                entry.get("summary", "")
            )

            description = clean_text(
                entry.get("description", "")
            )

            if not title or not url:
                continue

            # ------------------------------------------------
            # منع التكرار بالرابط
            # ------------------------------------------------

            if exists(url):
                continue

            text = normalize_text(
                f"{title} {summary} {description}"
            )

            # ------------------------------------------------
            # منع الإعلانات والعقار
            # ------------------------------------------------

            if is_blocked_content(text):

                total_blocked += 1

                print(
                    f"  BLOCKED: {title[:90]}"
                )

                continue

            # ------------------------------------------------
            # التحقق من الصلة
            # ------------------------------------------------

            if not relevant(
                entry,
                name
            ):

                continue

            total_relevant += 1

            # ------------------------------------------------
            # إنشاء العنصر
            # ------------------------------------------------

            item = {
                "title": title,
                "url": url,
                "source": name,
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
                "source_group": source_group(
                    name
                ),
            }

            # ------------------------------------------------
            # التصنيف المحلي
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
                    f"  Classification error: {error}"
                )

            # ------------------------------------------------
            # حفظ
            # ------------------------------------------------

            try:

                add(item)

                new_items.append(item)

                source_count += 1

                print(
                    f"  + {title[:90]}"
                )

            except Exception as error:

                print(
                    f"  Database error: {error}"
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
