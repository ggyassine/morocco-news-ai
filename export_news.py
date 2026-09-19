import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from db import recent


MAX_PER_SECTION = 30
MAX_TOTAL = 150

# ============================================================
# الأخبار الظاهرة في الموقع
# آخر 24 ساعة فقط
# ============================================================

MAX_NEWS_AGE_HOURS = 24


# ============================================================
# كلمات المحتوى غير المرغوب
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
    "annonce",
    "annonces",
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
# HELPERS
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
                str(item.get("source", "") or ""),
                str(item.get("category", "") or ""),
            ]
        )
    )


# ============================================================
# BLOCKED CONTENT
# ============================================================

def is_blocked(item):

    text = item_text(item)

    # --------------------------------------------------------
    # العقارات
    # --------------------------------------------------------

    for term in BLOCKED_TERMS:

        if normalize_text(term) in text:
            return True

    # --------------------------------------------------------
    # المحتوى التجاري
    # --------------------------------------------------------

    matches = 0

    for term in COMMERCIAL_TERMS:

        if normalize_text(term) in text:
            matches += 1

    return matches >= 2


# ============================================================
# DATE PARSER
# ============================================================

def parse_date(value):
    """
    محاولة قراءة تاريخ الخبر من عدة صيغ.
    """

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
    # تواريخ بسيطة
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
# RECENCY
# ============================================================

def is_recent(item):
    """
    الاحتفاظ فقط بالأخبار المنشورة خلال آخر 24 ساعة.

    إذا تعذر قراءة التاريخ، نحتفظ بالخبر
    حتى لا نخسر خبرًا مهمًا بسبب صيغة تاريخ غير معروفة.
    """

    published = item.get(
        "published"
    )

    date = parse_date(
        published
    )

    # إذا لم نستطع معرفة التاريخ
    # لا نحذف الخبر
    if date is None:
        return True

    now = datetime.now(
        timezone.utc
    )

    age_seconds = (
        now - date
    ).total_seconds()

    # أخبار مستقبلية بسبب خطأ في المصدر
    # يتم تجاهلها
    if age_seconds < 0:
        return False

    # آخر 24 ساعة فقط
    return age_seconds <= (
        MAX_NEWS_AGE_HOURS * 60 * 60
    )


# ============================================================
# CATEGORY
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

    # --------------------------------------------------------
    # انتقالات اللاعبين
    # --------------------------------------------------------

    if (
        "انتقالات" in category
        or "transfer" in category
    ):
        return "transfers"

    # --------------------------------------------------------
    # الرياضة
    # --------------------------------------------------------

    if (
        "رياضه" in category
        or "رياضة" in category
        or "sport" in category
    ):
        return "sports"

    # --------------------------------------------------------
    # أخبار المغرب
    # --------------------------------------------------------

    if (
        "اخبار المغرب" in category
        or "المغرب" in category
        or source_group == "morocco"
    ):
        return "morocco"

    # --------------------------------------------------------
    # الشرق الأوسط
    # --------------------------------------------------------

    if (
        "الشرق الاوسط" in category
        or source_group == "middle_east"
    ):
        return "middle_east"

    # --------------------------------------------------------
    # العالم العربي
    # --------------------------------------------------------

    if (
        "العالم" in category
        or source_group == "world_arabic"
    ):
        return "world_arabic"

    # --------------------------------------------------------
    # المصادر الدولية
    # --------------------------------------------------------

    if source_group == "international":
        return "world_arabic"

    return None


# ============================================================
# LOAD
# ============================================================

items = recent(500)


# ============================================================
# FILTER
# ============================================================

clean_items = []

blocked_count = 0
old_count = 0


for item in items:

    # --------------------------------------------------------
    # منع العقارات والإعلانات
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

    clean_items.append(item)


# ============================================================
# SORT
# ============================================================

def sort_key(item):

    date = parse_date(
        item.get(
            "published"
        )
    )

    # إذا لم يوجد تاريخ النشر
    # نستعمل تاريخ اكتشاف الخبر
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
        continue

    if (
        len(
            sections[section]
        )
        >= MAX_PER_SECTION
    ):
        continue

    sections[section].append(
        item
    )


# ============================================================
# TOTAL
# ============================================================

total = sum(
    len(items)
    for items in sections.values()
)


# ============================================================
# MAX TOTAL
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
        len(items)
        for items in sections.values()
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

print(
    f"Exported {total} clean news items"
)

print(
    f"Blocked commercial/real-estate items: "
    f"{blocked_count}"
)

print(
    f"Removed old news items: "
    f"{old_count}"
)

print(
    "Maximum news age: 24 hours"
)
