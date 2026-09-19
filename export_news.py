import json
import re
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
    # Immobilier
    "immobilier",
    "immobilière",
    "immobiliere",
    "appartement",
    "appartements",
    "villa",
    "villas",
    "maison à vendre",
    "maison a vendre",
    "terrain",
    "terrains",
    "location immobilière",
    "location immobiliere",
    "résidence",
    "residence",
    "promoteur immobilier",
    "promotion immobilière",
    "promotion immobiliere",

    # Arabic
    "عقار",
    "عقارات",
    "شقة للبيع",
    "شقق للبيع",
    "منزل للبيع",
    "منازل للبيع",
    "دار للبيع",
    "دور للبيع",
    "أرض للبيع",
    "ارض للبيع",
    "بقعة للبيع",
    "بقع للبيع",
    "كراء شقة",
    "كراء منزل",
    "للإيجار",
    "للايجار",
    "للبيع",
]


COMMERCIAL_TERMS = [
    "promo",
    "promotion",
    "offre spéciale",
    "offre speciale",
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
    "اعلان تجاري",
]


# ============================================================
# SOURCE GROUPS
# ============================================================

MOROCCO_GROUPS = {
    "morocco",
}

SPORT_GROUPS = {
    "arabic_sports",
}

TRANSFER_GROUPS = {
    "arabic_transfers",
}

MIDDLE_EAST_GROUPS = {
    "middle_east",
}

WORLD_GROUPS = {
    "world_arabic",
    "international",
}


# ============================================================
# KEYWORDS
# ============================================================

SPORT_TERMS = [
    "رياضة",
    "رياضي",
    "رياضات",
    "كرة القدم",
    "كرة السلة",
    "كرة اليد",
    "كرة الطائرة",
    "منتخب",
    "مباراة",
    "مباريات",
    "دوري",
    "كأس",
    "بطولة",
    "لاعب",
    "لاعبة",
    "مدرب",
    "هدف",
    "أهداف",
    "فوز",
    "هزيمة",
    "تعادل",
    "champions",
    "football",
    "sport",
    "sports",
    "match",
    "league",
    "cup",
    "basketball",
]


TRANSFER_TERMS = [
    "انتقال",
    "انتقالات",
    "صفقة",
    "صفقات",
    "توقيع",
    "يوقع",
    "وقع",
    "ضم",
    "يضم",
    "إعارة",
    "اعارة",
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


MOROCCO_TERMS = [
    "المغرب",
    "مغربي",
    "مغربية",
    "المغربي",
    "المغاربة",
    "الرباط",
    "الدار البيضاء",
    "طنجة",
    "فاس",
    "مراكش",
    "أكادير",
    "وجدة",
    "تطوان",
    "القنيطرة",
    "الجديدة",
    "الحكومة المغربية",
    "البرلمان المغربي",
    "المنتخب المغربي",
    "أسود الأطلس",
]


# ============================================================
# TEXT HELPERS
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
        "ؤ": "و",
        "ئ": "ي",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def contains_any(text, terms):
    text = normalize_text(text)

    for term in terms:
        term = normalize_text(term)

        if term and term in text:
            return True

    return False


def item_text(item):
    return normalize_text(
        " ".join(
            [
                str(item.get("title", "") or ""),
                str(item.get("summary", "") or ""),
                str(item.get("description", "") or ""),
                str(item.get("source", "") or ""),
                str(item.get("category", "") or ""),
                str(item.get("source_group", "") or ""),
                str(item.get("player", "") or ""),
            ]
        )
    )


# ============================================================
# BLOCKED CONTENT
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
    # المحتوى التجاري
    # نمنع فقط إذا ظهرت كلمتان تجاريتان أو أكثر
    # حتى لا نحذف خبرًا حقيقيًا بسبب كلمة واحدة
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

    if not value:
        return None

    value = str(value).strip()

    # ISO
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

    # RSS / RFC
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

    # Simple dates
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

    published = item.get(
        "published"
    )

    date = parse_date(
        published
    )

    # إذا لم نستطع قراءة التاريخ
    # نحتفظ بالخبر
    if date is None:
        return True

    now = datetime.now(
        timezone.utc
    )

    age_seconds = (
        now - date
    ).total_seconds()

    # تاريخ مستقبلي غير منطقي
    if age_seconds < 0:
        return False

    return age_seconds <= (
        MAX_NEWS_AGE_HOURS * 3600
    )


# ============================================================
# SOURCE GROUP
# ============================================================

def get_source_group(item):

    group = str(
        item.get(
            "source_group",
            ""
        ) or ""
    ).strip().lower()

    if group:
        return group

    source = str(
        item.get(
            "source",
            ""
        ) or ""
    ).strip()

    # المغرب
    morocco_sources = {
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

    if source in morocco_sources:
        return "morocco"

    # الرياضة
    sports_sources = {
        "كووورة",
        "WinWin",
        "في الجول",
        "العين الرياضية",
        "365Scores عربي",
    }

    if source in sports_sources:
        return "arabic_sports"

    # الانتقالات
    transfer_sources = {
        "كووورة انتقالات",
        "WinWin ميركاتو",
        "في الجول انتقالات",
        "ميركاتو داي",
        "365Scores انتقالات",
    }

    if source in transfer_sources:
        return "arabic_transfers"

    # الشرق الأوسط
    middle_sources = {
        "الجزيرة",
        "العربية",
        "سكاي نيوز عربية",
        "الشرق للأخبار",
        "الشرق الأوسط",
        "العربي الجديد",
    }

    if source in middle_sources:
        return "middle_east"

    # العالم
    world_sources = {
        "القدس العربي",
        "فرانس 24 عربي",
        "DW عربية",
        "BBC عربي",
        "يورونيوز عربي",
        "إندبندنت عربية",
        "CNN بالعربية",
        "Reuters",
        "Associated Press",
    }

    if source in world_sources:
        return "world_arabic"

    return ""


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_section(item):

    text = item_text(item)

    category = normalize_text(
        item.get(
            "category",
            ""
        )
    )

    group = get_source_group(
        item
    )

    # --------------------------------------------------------
    # 1. انتقالات اللاعبين
    # --------------------------------------------------------

    if group in TRANSFER_GROUPS:
        return "transfers"

    if (
        "انتقالات" in category
        or "transfer" in category
    ):
        return "transfers"

    if (
        contains_any(
            text,
            TRANSFER_TERMS
        )
        and (
            contains_any(
                text,
                MOROCCO_TERMS
            )
            or group in SPORT_GROUPS
            or group in TRANSFER_GROUPS
        )
    ):
        return "transfers"

    # --------------------------------------------------------
    # 2. الرياضة
    # --------------------------------------------------------

    if group in SPORT_GROUPS:
        return "sports"

    if (
        "رياضه" in category
        or "رياضة" in category
        or "sport" in category
    ):
        return "sports"

    if contains_any(
        text,
        SPORT_TERMS
    ):
        # إذا كان خبرًا رياضيًا حقيقيًا
        # نضعه في الرياضة
        return "sports"

    # --------------------------------------------------------
    # 3. أخبار المغرب
    # --------------------------------------------------------

    if group in MOROCCO_GROUPS:
        return "morocco"

    if contains_any(
        text,
        MOROCCO_TERMS
    ):
        return "morocco"

    # --------------------------------------------------------
    # 4. الشرق الأوسط
    # --------------------------------------------------------

    if group in MIDDLE_EAST_GROUPS:
        return "middle_east"

    # --------------------------------------------------------
    # 5. العالم العربي والدولي
    # --------------------------------------------------------

    if group in WORLD_GROUPS:
        return "world_arabic"

    # --------------------------------------------------------
    # 6. التصنيف الاحتياطي
    # --------------------------------------------------------

    return None


# ============================================================
# LOAD DATABASE
# ============================================================

items = recent(500)


# ============================================================
# FILTER
# ============================================================

clean_items = []

blocked_count = 0
old_count = 0
uncategorized_count = 0


for item in items:

    # --------------------------------------------------------
    # منع العقار والإعلانات الواضحة
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

    # --------------------------------------------------------
    # القسم
    # --------------------------------------------------------

    section = detect_section(
        item
    )

    if section is None:

        uncategorized_count += 1
        continue

    # نحفظ القسم داخل الخبر
    item["section"] = section

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

    section = item.get(
        "section"
    )

    if section not in sections:
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
    len(section_items)
    for section_items
    in sections.values()
)


# ============================================================
# MAX TOTAL
# ============================================================

if total > MAX_TOTAL:

    all_items = []

    for section_name in sections:

        all_items.extend(
            sections[section_name]
        )

    all_items.sort(
        key=sort_key,
        reverse=True
    )

    all_items = all_items[
        :MAX_TOTAL
    ]

    sections = {
        "morocco": [],
        "sports": [],
        "transfers": [],
        "middle_east": [],
        "world_arabic": [],
    }

    for item in all_items:

        section = item.get(
            "section"
        )

        if section in sections:

            if len(
                sections[section]
            ) < MAX_PER_SECTION:

                sections[section].append(
                    item
                )

    total = sum(
        len(section_items)
        for section_items
        in sections.values()
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
    f"Blocked items: {blocked_count}"
)

print(
    f"Old items removed: {old_count}"
)

print(
    f"Uncategorized items skipped: "
    f"{uncategorized_count}"
)

print(
    f"Morocco: "
    f"{len(sections['morocco'])}"
)

print(
    f"Sports: "
    f"{len(sections['sports'])}"
)

print(
    f"Transfers: "
    f"{len(sections['transfers'])}"
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
    f"Maximum news age: "
    f"{MAX_NEWS_AGE_HOURS} hours"
)

print("=" * 60)
