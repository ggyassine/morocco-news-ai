import re
import html


STATUSES = [
    "رسمي",
    "مؤكد",
    "اتفاق مبدئي",
    "مفاوضات",
    "اهتمام",
    "عرض",
    "إعارة",
    "تجديد",
    "إشاعة",
    "منفي",
    "غير واضح",
]


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


TRANSFER_TERMS = [
    "انتقال",
    "انتقالات",
    "ميركاتو",
    "سوق الانتقالات",
    "مفاوضات",
    "صفقة",
    "توقيع",
    "يوقع",
    "وقع",
    "إعارة",
    "اعارة",
    "اهتمام",
    "يرغب",
    "رحيل",
    "مغادرة",
    "تجديد",
    "عقد",
    "transfer",
    "transfert",
    "mercato",
    "loan",
    "signing",
]


SPORT_TERMS = [
    "رياضة",
    "رياضي",
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
    "football",
    "sport",
    "match",
    "league",
    "cup",
]


MOROCCO_TERMS = [
    "المغرب",
    "مغربي",
    "مغربية",
    "المغاربة",
    "الرباط",
    "الدار البيضاء",
    "طنجة",
    "فاس",
    "مراكش",
    "أكادير",
    "وجدة",
    "الحكومة المغربية",
    "البرلمان المغربي",
    "المنتخب المغربي",
    "المنتخب الوطني",
]


OFFICIAL_TERMS = [
    "أعلن رسميا",
    "أعلن رسميًا",
    "أعلنت رسميا",
    "أعلنت رسميًا",
    "رسمي",
    "رسميا",
    "رسميًا",
    "بيان رسمي",
    "وقع عقدا",
    "وقع عقدًا",
    "تم التوقيع",
    "انضم رسميا",
    "انضم رسميًا",
    "official",
]


CONFIRMED_TERMS = [
    "أكد",
    "أكدت",
    "تأكد",
    "confirmed",
]


NEGOTIATION_TERMS = [
    "مفاوضات",
    "يتفاوض",
    "تفاوض",
    "محادثات",
    "اتصالات",
    "talks",
    "negotiations",
]


INTEREST_TERMS = [
    "اهتمام",
    "مهتم",
    "يرغب",
    "يراقب",
    "يتابع",
    "يستهدف",
    "هدف للنادي",
    "interest",
    "interested",
]


OFFER_TERMS = [
    "عرض رسمي",
    "عرض مالي",
    "قدم عرضا",
    "قدم عرضًا",
    "offer",
    "bid",
]


LOAN_TERMS = [
    "إعارة",
    "اعارة",
    "معارا",
    "معارًا",
    "loan",
]


RENEWAL_TERMS = [
    "تجديد",
    "جدد عقده",
    "جدد عقدها",
    "تمديد العقد",
    "renewal",
    "renewed",
]


RUMOR_TERMS = [
    "إشاعة",
    "شائعة",
    "بحسب تقارير",
    "تقارير تشير",
    "يقال",
    "قد ينتقل",
    "قد ينضم",
    "ربما",
    "rumor",
    "rumour",
]


DENIED_TERMS = [
    "نفى",
    "نفت",
    "ينفي",
    "تنفي",
    "لا صحة",
    "غير صحيح",
]


def clean_text(value):
    if not value:
        return ""

    text = html.unescape(str(value))

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize(value):
    text = clean_text(value).lower()

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


def contains_any(text, terms):
    normalized = normalize(text)

    return any(
        normalize(term) in normalized
        for term in terms
    )


def source_group(source):
    if source in MOROCCO_SOURCES:
        return "morocco"

    if source in MIDDLE_EAST_SOURCES:
        return "middle_east"

    if source in WORLD_ARABIC_SOURCES:
        return "world_arabic"

    if source in INTERNATIONAL_SOURCES:
        return "international"

    return "other"


def classify_category(item):

    title = clean_text(
        item.get("title", "")
    )

    summary = clean_text(
        item.get("summary", "")
    )

    description = clean_text(
        item.get("description", "")
    )

    source = item.get("source", "")

    text = (
        title
        + " "
        + summary
        + " "
        + description
    )

    # الانتقالات لها الأولوية
    if contains_any(text, TRANSFER_TERMS):
        return "انتقالات اللاعبين"

    # الرياضة
    if contains_any(text, SPORT_TERMS):
        return "الرياضة"

    # المغرب
    if (
        contains_any(text, MOROCCO_TERMS)
        or source in MOROCCO_SOURCES
    ):
        return "أخبار المغرب"

    # الشرق الأوسط
    if source in MIDDLE_EAST_SOURCES:
        return "الشرق الأوسط"

    # العالم العربي والدولي
    if (
        source in WORLD_ARABIC_SOURCES
        or source in INTERNATIONAL_SOURCES
    ):
        return "العالم"

    return "أخبار"


def classify_status(item):

    text = " ".join([
        clean_text(item.get("title", "")),
        clean_text(item.get("summary", "")),
        clean_text(item.get("description", "")),
    ])

    if contains_any(text, DENIED_TERMS):
        return "منفي"

    if contains_any(text, OFFICIAL_TERMS):
        return "رسمي"

    if contains_any(text, CONFIRMED_TERMS):
        return "مؤكد"

    if contains_any(text, LOAN_TERMS):
        return "إعارة"

    if contains_any(text, RENEWAL_TERMS):
        return "تجديد"

    if contains_any(text, NEGOTIATION_TERMS):
        return "مفاوضات"

    if contains_any(text, OFFER_TERMS):
        return "عرض"

    if contains_any(text, INTEREST_TERMS):
        return "اهتمام"

    if contains_any(text, RUMOR_TERMS):
        return "إشاعة"

    return "غير واضح"


def find_player(item):

    try:
        from sources import MOROCCAN_PLAYERS
    except Exception:
        return ""

    text = normalize(
        " ".join([
            clean_text(item.get("title", "")),
            clean_text(item.get("summary", "")),
            clean_text(item.get("description", "")),
        ])
    )

    for player in MOROCCAN_PLAYERS:

        player_name = clean_text(player)

        if (
            player_name
            and normalize(player_name) in text
        ):
            return player_name

    return ""


def classify_trust(source):

    if source in {
        "MAP عربي",
        "SNRTnews عربي",
        "Reuters",
        "Associated Press",
    }:
        return "A"

    if source in {
        "هسبريس",
        "Le360 عربي",
        "الجزيرة",
        "العربية",
        "سكاي نيوز عربية",
        "الشرق للأخبار",
        "الشرق الأوسط",
        "العربي الجديد",
        "BBC عربي",
        "فرانس 24 عربي",
        "DW عربية",
    }:
        return "B"

    return "C"


def remove_title(text, title):

    if not text:
        return ""

    text = clean_text(text)
    title = clean_text(title)

    if not title:
        return text

    normalized_text = normalize(text)
    normalized_title = normalize(title)

    if normalized_text.startswith(
        normalized_title
    ):
        text = text[len(title):].strip(
            " -–—:،,.؛"
        )

    return text


def remove_repeated_text(text):

    if not text:
        return ""

    words = text.split()

    if len(words) < 12:
        return text

    # إذا كان RSS كرر نفس العبارة
    half = len(words) // 2

    first = normalize(
        " ".join(words[:half])
    )

    second = normalize(
        " ".join(words[half:])
    )

    if first == second:
        return " ".join(
            words[:half]
        )

    return text


def make_summary(item):

    title = clean_text(
        item.get("title", "")
    )

    summary = clean_text(
        item.get("summary", "")
    )

    description = clean_text(
        item.get("description", "")
    )

    candidates = []

    for text in [
        description,
        summary,
    ]:

        text = remove_title(
            text,
            title
        )

        text = remove_repeated_text(
            text
        )

        if len(text) >= 30:
            candidates.append(text)

    if not candidates:

        return (
            "يتناول الخبر: "
            + title
        )

    # اختيار أفضل وصف متاح
    result = max(
        candidates,
        key=len
    )

    # إزالة التكرار الكامل للجمل
    sentences = re.split(
        r"(?<=[.!؟])\s+",
        result
    )

    unique = []
    seen = set()

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) < 10:
            continue

        key = normalize(sentence)

        if key in seen:
            continue

        seen.add(key)
        unique.append(sentence)

    result = " ".join(unique)

    if len(result) > 450:
        result = result[:450].rsplit(
            " ",
            1
        )[0] + "..."

    return result


def classify(item):

    return {
        "category": classify_category(item),
        "status": classify_status(item),
        "player": find_player(item),
        "trust": classify_trust(
            item.get("source", "")
        ),
        "summary": make_summary(item),
    }
