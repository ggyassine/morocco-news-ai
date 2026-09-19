import json

from db import recent


MAX_PER_SECTION = 30
MAX_TOTAL = 150


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


def is_blocked(item):
    text = item_text(item)

    # عقار وإعلانات عقارية
    for term in BLOCKED_TERMS:

        if normalize_text(term) in text:
            return True

    # محتوى تجاري واضح
    matches = 0

    for term in COMMERCIAL_TERMS:

        if normalize_text(term) in text:
            matches += 1

    return matches >= 2


# ============================================================
# CATEGORY
# ============================================================

def section_for(item):

    category = normalize_text(
        item.get("category", "")
    )

    source_group = normalize_text(
        item.get("source_group", "")
    )

    # انتقالات اللاعبين
    if (
        "انتقالات" in category
        or "transfer" in category
    ):
        return "transfers"

    # الرياضة
    if (
        "رياضة" in category
        or "sport" in category
    ):
        return "sports"

    # أخبار المغرب
    if (
        "اخبار المغرب" in category
        or "المغرب" in category
        or source_group == "morocco"
    ):
        return "morocco"

    # الشرق الأوسط
    if (
        "الشرق الاوسط" in category
        or source_group == "middle_east"
    ):
        return "middle_east"

    # العالم العربي
    if (
        "العالم" in category
        or source_group == "world_arabic"
    ):
        return "world_arabic"

    # المصادر الدولية
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

for item in items:

    if is_blocked(item):

        blocked_count += 1
        continue

    clean_items.append(item)


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

    section = section_for(item)

    if section is None:
        continue

    if len(sections[section]) >= MAX_PER_SECTION:
        continue

    sections[section].append(item)


# ============================================================
# TOTAL
# ============================================================

total = sum(
    len(items)
    for items in sections.values()
)


# ============================================================
# OUTPUT
# ============================================================

output = {
    "updated": __import__("datetime")
        .datetime.now(
            __import__("datetime").timezone.utc
        )
        .isoformat(),

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


print(
    f"Exported {total} clean news items"
)

print(
    f"Blocked {blocked_count} old commercial/real-estate items"
)
