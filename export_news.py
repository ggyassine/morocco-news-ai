import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from db import recent


# ============================================================
# SETTINGS
# ============================================================

MAX_PER_SECTION = 50
MAX_TOTAL = 150
MAX_NEWS_AGE_HOURS = 24


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

    "appartement",
    "villa",
    "maison",
    "terrain",
    "location",
    "résidence",

    "annonce immobilière",
    "annonces immobilières",
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
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):

    if not value:
        return ""

    text = str(value).lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def item_text(item):

    return normalize_text(
        " ".join(
            [
                str(item.get("title", "") or ""),
                str(item.get("summary", "") or ""),
                str(item.get("description", "") or ""),
                str(item.get("source", "") or ""),
                str(item.get("category", "") or ""),
            ]
        )
    )


# ============================================================
# BLOCKING
# ============================================================

def is_blocked(item):

    text = item_text(item)

    # --------------------------------------------------------
    # العقار
    # --------------------------------------------------------

    for term in BLOCKED_TERMS:

        if normalize_text(term) in text:
            return True

    # --------------------------------------------------------
    # التجاري
    # --------------------------------------------------------

    commercial_matches = 0

    for term in COMMERCIAL_TERMS:

        if normalize_text(term) in text:
            commercial_matches += 1

    return commercial_matches >= 2


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value):

    if not value:
        return None

    value = str(value).strip()

    # --------------------------------------------------------
    # ISO
    # --------------------------------------------------------

    try:

        date = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if date.tzinfo is None:

            date = date.replace(
                tzinfo=timezone.utc
            )

        return date.astimezone(
            timezone.utc
        )

    except Exception:
        pass

    # --------------------------------------------------------
    # RSS / RFC
    # --------------------------------------------------------

    try:

        date = parsedate_to_datetime(
            value
        )

        if date.tzinfo is None:

            date = date.replace(
                tzinfo=timezone.utc
            )

        return date.astimezone(
            timezone.utc
        )

    except Exception:
        pass

    # --------------------------------------------------------
    # SIMPLE DATE
    # --------------------------------------------------------

    formats = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]

    for fmt in formats:

        try:

            date = datetime.strptime(
                value[:10],
                fmt
            )

            return date.replace(
                tzinfo=timezone.utc
            )

        except Exception:
            pass

    return None


# ============================================================
# RECENT NEWS
# ============================================================

def is_recent(item):

    published = item.get(
        "published"
    )

    published_date = parse_date(
        published
    )

    # إذا كان تاريخ النشر غير قابل للقراءة
    # نستعمل تاريخ الاكتشاف بدل حذف الخبر
    if published_date is None:

        discovered_date = parse_date(
            item.get("discovered")
        )

        if discovered_date is None:
            return True

        published_date = discovered_date

    now = datetime.now(
        timezone.utc
    )

    age_seconds = (
        now - published_date
    ).total_seconds()

    # لا نقبل تاريخًا مستقبليًا بعيدًا
    if age_seconds < -3600:
        return False

    return age_seconds <= (
        MAX_NEWS_AGE_HOURS * 3600
    )


# ============================================================
# CATEGORY DETECTION
# ============================================================

def section_for(item):

    category = normalize_text(
        item.get(
            "category",
            ""
        )
    )

    source_group = normalize_text(
        item.get(
            "source_group",
            ""
        )
    )

    text = item_text(
        item
    )

    # ========================================================
    # 1. المصدر أولًا
    # ========================================================

    # --------------------------------------------------------
    # انتقالات اللاعبين
    # --------------------------------------------------------

    if source_group == "arabic_transfers":
        return "transfers"

    # --------------------------------------------------------
    # المصادر الرياضية العربية
    # --------------------------------------------------------

    if source_group == "arabic_sports":
        return "sports"

    # --------------------------------------------------------
    # المغرب
    # --------------------------------------------------------

    if source_group == "morocco":
        return "morocco"

    # --------------------------------------------------------
    # الشرق الأوسط
    # --------------------------------------------------------

    if source_group == "middle_east":
        return "middle_east"

    # --------------------------------------------------------
    # العالم العربي
    # --------------------------------------------------------

    if source_group == "world_arabic":
        return "world_arabic"

    # --------------------------------------------------------
    # المصادر الدولية
    # --------------------------------------------------------

    if source_group == "international":
        return "world_arabic"

    # ========================================================
    # 2. التصنيف
    # ========================================================

    # --------------------------------------------------------
    # انتقالات اللاعبين
    # --------------------------------------------------------

    transfer_words = [
        "انتقالات",
        "انتقال",
        "ميركاتو",
        "سوق الانتقالات",
        "صفقة",
        "يوقع",
        "وقع",
        "توقيع",
        "ضم",
        "إعارة",
        "مفاوضات",
        "اهتمام",
        "عرض",
        "رحيل",
        "مغادرة",
        "transfer",
        "transfers",
        "transfert",
        "transferts",
        "mercato",
        "signing",
        "signed",
        "loan",
        "negotiation",
        "interest",
        "offer",
    ]

    if (
        "انتقالات" in category
        or "transfer" in category
        or any(
            normalize_text(word) in text
            for word in transfer_words
        )
    ):
        return "transfers"

    # --------------------------------------------------------
    # الرياضة
    # --------------------------------------------------------

    sport_words = [
        "رياضه",
        "رياضة",
        "رياضي",
        "رياضات",
        "كره القدم",
        "كره السله",
        "كره اليد",
        "منتخب",
        "مباراه",
        "مباريات",
        "دوري",
        "كاس",
        "بطوله",
        "لاعب",
        "مدرب",
        "هدف",
        "اهداف",
        "فوز",
        "هزيمه",
        "تعادل",
        "champions",
        "football",
        "sport",
        "match",
        "league",
        "cup",
    ]

    if (
        "رياضه" in category
        or "sport" in category
        or any(
            normalize_text(word) in text
            for word in sport_words
        )
    ):
        return "sports"

    # --------------------------------------------------------
    # أخبار المغرب
    # --------------------------------------------------------

    if (
        "اخبار المغرب" in category
        or "المغرب" in category
    ):
        return "morocco"

    # --------------------------------------------------------
    # الشرق الأوسط
    # --------------------------------------------------------

    if (
        "الشرق الاوسط" in category
        or "الشرق الأوسط" in category
    ):
        return "middle_east"

    # --------------------------------------------------------
    # العالم العربي
    # --------------------------------------------------------

    if (
        "العالم" in category
    ):
        return "world_arabic"

    # ========================================================
    # 3. FALLBACK
    # ========================================================

    # إذا كان الخبر من مصدر معروف لكن بدون تصنيف
    source = normalize_text(
        item.get("source", "")
    )

    sports_sources = [
        "كوووره",
        "winwin",
        "في الجول",
        "يلا كوره",
        "365scores",
        "الجزيره الرياضيه",
        "العين الرياضيه",
        "kooora",
        "winwin",
    ]

    transfer_sources = [
        "كوووره انتقالات",
        "winwin ميركاتو",
        "في الجول انتقالات",
        "ميركاتو داي",
        "365scores انتقالات",
    ]

    if any(
        normalize_text(source_name) in source
        for source_name in transfer_sources
    ):
        return "transfers"

    if any(
        normalize_text(source_name) in source
        for source_name in sports_sources
    ):
        return "sports"

    return None


# ============================================================
# LOAD DATABASE
# ============================================================

items = recent(
    1000
)


# ============================================================
# FILTER
# ============================================================

clean_items = []

blocked_count = 0
old_count = 0
unknown_count = 0


for item in items:

    # --------------------------------------------------------
    # منع العقار والتجاري
    # --------------------------------------------------------

    if is_blocked(item):

        blocked_count += 1

        continue

    # --------------------------------------------------------
    # آخر 24 ساعة
    # --------------------------------------------------------

    if not is_recent(item):

        old_count += 1

        continue

    clean_items.append(
        item
    )


# ============================================================
# SORT
# ============================================================

def sort_key(item):

    date = parse_date(
        item.get(
            "published"
        )
    )

    if date is None:

        date = parse_date(
            item.get(
                "discovered"
            )
        )

    if date is None:

        return datetime.min.replace(
            tzinfo=timezone.utc
        )

    return date


clean_items.sort(
    key=sort_key,
    reverse=True
)


# ============================================================
# SECTIONS
# ============================================================

sections = {

    "morocco": [],

    "sports": [],

    "transfers": [],

    "middle_east": [],

    "world_arabic": [],
}


# ============================================================
# DISTRIBUTE
# ============================================================

for item in clean_items:

    section = section_for(
        item
    )

    if section is None:

        unknown_count += 1

        continue

    if len(
        sections[section]
    ) >= MAX_PER_SECTION:

        continue

    sections[section].append(
        item
    )


# ============================================================
# TOTAL
# ============================================================

total = sum(
    len(section_items)
    for section_items in sections.values()
)


# ============================================================
# GLOBAL LIMIT
# ============================================================

if total > MAX_TOTAL:

    remaining = MAX_TOTAL

    for section_name in sections:

        sections[section_name] = (
            sections[section_name][
                :remaining
            ]
        )

        remaining -= len(
            sections[section_name]
        )

        if remaining <= 0:
            break

    total = sum(
        len(section_items)
        for section_items in sections.values()
    )


# ============================================================
# OUTPUT
# ============================================================

output = {

    "updated": datetime.now(
        timezone.utc
    ).isoformat(),

    "total": total,

    "sections": sections,
}


# ============================================================
# SAVE
# ============================================================

with open(
    "docs/news.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        output,
        file,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# LOG
# ============================================================

print("=" * 60)

print(
    f"Exported {total} news items"
)

print(
    f"Blocked: {blocked_count}"
)

print(
    f"Removed old news: {old_count}"
)

print(
    f"Unclassified: {unknown_count}"
)

print(
    f"Morocco: {len(sections['morocco'])}"
)

print(
    f"Sports: {len(sections['sports'])}"
)

print(
    f"Transfers: {len(sections['transfers'])}"
)

print(
    f"Middle East: {len(sections['middle_east'])}"
)

print(
    f"World Arabic: {len(sections['world_arabic'])}"
)

print(
    f"Maximum age: {MAX_NEWS_AGE_HOURS} hours"
)

print("=" * 60)
