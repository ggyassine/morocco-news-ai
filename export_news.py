import json
from db import recent


# ============================================================
# SETTINGS
# ============================================================

MAX_PER_SECTION = 30
MAX_TOTAL = 150


# ============================================================
# GET NEWS
# ============================================================

items = recent(500)


# ============================================================
# SECTION HELPERS
# ============================================================

def section_for(item):
    category = item.get("category", "")
    source_group = item.get("source_group", "")

    # 🔄 الانتقالات
    if category == "انتقالات اللاعبين":
        return "transfers"

    # ⚽ الرياضة
    if category == "الرياضة":
        return "sports"

    # 🇲🇦 المغرب
    if (
        category == "أخبار المغرب"
        or source_group == "morocco"
    ):
        return "morocco"

    # 🌐 الشرق الأوسط
    if (
        category == "الشرق الأوسط"
        or source_group == "middle_east"
    ):
        return "middle_east"

    # 🌍 العالم بالعربية
    if (
        category == "العالم بالعربية"
        or source_group == "world_arabic"
    ):
        return "world_arabic"

    return None


# ============================================================
# CREATE SECTIONS
# ============================================================

sections = {
    "morocco": [],
    "middle_east": [],
    "world_arabic": [],
    "sports": [],
    "transfers": [],
}


# ============================================================
# DISTRIBUTE NEWS
# ============================================================

for item in items:

    section = section_for(item)

    if section is None:
        continue

    if len(sections[section]) >= MAX_PER_SECTION:
        continue

    sections[section].append(item)


# ============================================================
# SORT
# ============================================================

for section in sections:

    sections[section].sort(
        key=lambda item: item.get(
            "discovered",
            ""
        ),
        reverse=True
    )


# ============================================================
# LIMIT TOTAL
# ============================================================

total_items = sum(
    len(items)
    for items in sections.values()
)


# ============================================================
# OUTPUT
# ============================================================

data = {
    "updated": items[0].get(
        "discovered",
        ""
    ) if items else "",

    "total": total_items,

    "sections": sections,
}


with open(
    "docs/news.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# LOGS
# ============================================================

print(
    f"Exported {total_items} news items"
)

print(
    f"Morocco: "
    f"{len(sections['morocco'])}"
)

print(
    f"Middle East: "
    f"{len(sections['middle_east'])}"
)

print(
    f"World Arabic: "
    f"{len(sections['world_arabic'])}"
)

print(
    f"Sports: "
    f"{len(sections['sports'])}"
)

print(
    f"Transfers: "
    f"{len(sections['transfers'])}"
)
