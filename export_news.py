import json
from db import recent


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

INTERNATIONAL_SOURCES = {
    "Reuters",
    "BBC",
    "Associated Press",
    "France 24 عربي",
    "DW عربية",
}


def source_group(item):
    source = item.get("source", "")

    if source in MOROCCO_SOURCES:
        return "morocco"

    if source in MIDDLE_EAST_SOURCES:
        return "middle_east"

    if source in INTERNATIONAL_SOURCES:
        return "international"

    return "other"


# نجلب عددًا كبيرًا من الأخبار من قاعدة البيانات
all_items = recent(500)


morocco = []
middle_east = []
international = []
other = []

for item in all_items:
    group = source_group(item)

    if group == "morocco":
        morocco.append(item)
    elif group == "middle_east":
        middle_east.append(item)
    elif group == "international":
        international.append(item)
    else:
        other.append(item)


# توزيع متوازن للموقع
selected = []

# الأخبار المغربية لها الأولوية
selected.extend(morocco[:50])

# أخبار الشرق الأوسط
selected.extend(middle_east[:20])

# الأخبار الدولية
selected.extend(international[:20])

# أي أخبار أخرى
selected.extend(other[:10])


# إذا كان العدد أقل من 100، نكمل من بقية الأخبار
if len(selected) < 100:
    selected_urls = {
        item.get("url")
        for item in selected
    }

    for item in all_items:
        if item.get("url") in selected_urls:
            continue

        selected.append(item)
        selected_urls.add(item.get("url"))

        if len(selected) >= 100:
            break


# ترتيب الأخبار من الأحدث إلى الأقدم
selected.sort(
    key=lambda item: item.get("discovered", ""),
    reverse=True
)


# الاحتفاظ بـ 100 خبر كحد أقصى
selected = selected[:100]


with open(
    "docs/news.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        selected,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    f"Exported {len(selected)} news items"
)

print(
    f"Morocco: {len(morocco[:50])}"
)

print(
    f"Middle East: {len(middle_east[:20])}"
)

print(
    f"International: {len(international[:20])}"
)

print(
    f"Other: {len(other[:10])}"
)
