import re

from sources import (
    MOROCCAN_PLAYERS,
    TRANSFER_TERMS,
)


# =========================================================
# STATUSES
# =========================================================

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


# =========================================================
# SOURCE GROUPS
# =========================================================

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


# =========================================================
# SPORTS KEYWORDS
# =========================================================

SPORTS_TERMS = [

    "كرة القدم",
    "الدوري",
    "البطولة",
    "المباراة",
    "مباراة",
    "منتخب",
    "نادي",
    "أندية",
    "لاعب",
    "لاعبين",
    "مدرب",
    "مدربين",
    "هدف",
    "أهداف",
    "فوز",
    "خسارة",
    "تعادل",
    "تصفيات",
    "كأس",
    "دوري أبطال",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الإيطالي",
    "الدوري الفرنسي",
    "الدوري الألماني",
    "الدوري السعودي",
    "دوري أبطال أوروبا",
    "كأس العالم",
    "كأس إفريقيا",
    "المنتخب المغربي",
    "أسود الأطلس",

    "football",
    "soccer",
    "match",
    "matches",
    "club",
    "clubs",
    "player",
    "players",
    "coach",
    "goal",
    "goals",
    "league",
    "champions league",
    "world cup",
    "afcon",
    "premier league",
    "la liga",
    "serie a",
    "ligue 1",
    "bundesliga",
]


# =========================================================
# TRANSFER DETECTION
# =========================================================

def _is_transfer(text):

    low = text.lower()

    has_transfer_term = any(
        term.lower() in low
        for term in TRANSFER_TERMS
    )

    player = _player(text)

    return (
        has_transfer_term
        and bool(player)
    )


# =========================================================
# PLAYER DETECTION
# =========================================================

def _player(text):

    low = text.lower()

    # نحاول مطابقة الاسم الكامل أولًا
    for name in sorted(
        MOROCCAN_PLAYERS,
        key=len,
        reverse=True
    ):

        if name.lower() in low:
            return name

    return ""


# =========================================================
# SPORTS DETECTION
# =========================================================

def _is_sport(text):

    low = text.lower()

    return any(
        term.lower() in low
        for term in SPORTS_TERMS
    )


# =========================================================
# OFFICIAL STATUS
# =========================================================

def _official_status(text, trust):

    low = text.lower()

    official_words = [

        "official",
        "officially",
        "signed",
        "signs",
        "announced",
        "announcement",

        "رسميا",
        "رسمي",
        "رسميًا",
        "يوقع",
        "وقع",
        "تعاقد",
        "أعلن النادي",
        "أعلن",
        "الإعلان الرسمي",
    ]

    confirmed_words = [

        "confirmed",
        "agreement",
        "deal",

        "مؤكد",
        "اتفاق",
        "تم الاتفاق",
        "توصل لاتفاق",
        "اتفاق مبدئي",
    ]

    negotiation_words = [

        "negotiation",
        "negotiations",
        "talks",
        "interest",
        "offer",

        "مفاوضات",
        "اهتمام",
        "عرض",
        "يجري التفاوض",
    ]

    loan_words = [

        "loan",
        "إعارة",
        "إعارةً",
    ]

    renewal_words = [

        "renewal",
        "renewed",
        "تجديد",
        "جدد",
        "يجدد",
    ]

    rumor_words = [

        "rumor",
        "rumour",
        "reportedly",
        "يقال",
        "تقارير",
        "بحسب تقارير",
        "إشاعة",
        "أنباء",
    ]

    denied_words = [

        "denied",
        "denies",
        "false",
        "نفى",
        "ينفي",
        "منفي",
        "غير صحيح",
        "نفيا",
    ]

    if any(
        word in low
        for word in denied_words
    ):
        return "منفي"

    if any(
        word in low
        for word in loan_words
    ):
        return "إعارة"

    if any(
        word in low
        for word in renewal_words
    ):
        return "تجديد"

    if any(
        word in low
        for word in official_words
    ):

        if trust == "A":
            return "رسمي"

        return "مؤكد"

    if any(
        word in low
        for word in confirmed_words
    ):
        return "مؤكد"

    if any(
        word in low
        for word in negotiation_words
    ):
        return "مفاوضات"

    if any(
        word in low
        for word in rumor_words
    ):
        return "إشاعة"

    return "غير واضح"


# =========================================================
# SUMMARY CLEANING
# =========================================================

def _clean_summary(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # إزالة التكرار الكامل
    words = text.split()

    if len(words) > 20:

        half = len(words) // 2

        first = " ".join(
            words[:half]
        ).strip()

        second = " ".join(
            words[half:]
        ).strip()

        if (
            first
            and second
            and (
                first in second
                or second in first
            )
        ):

            text = first

    # إزالة تكرار الجمل
    sentences = re.split(
        r"(?<=[.!؟])\s+",
        text
    )

    unique_sentences = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        if sentence not in unique_sentences:
            unique_sentences.append(
                sentence
            )

    text = " ".join(
        unique_sentences
    )

    # الحد الأقصى للملخص
    if len(text) > 500:
        text = text[:500].rsplit(
            " ",
            1
        )[0] + "..."

    return text


# =========================================================
# CATEGORY
# =========================================================

def _category(text, source):

    # الرياضة أولًا
    # حتى لا يصنف خبر رياضي مغربي
    # على أنه خبر مغربي فقط
    if _is_sport(text):

        if _is_transfer(text):
            return "انتقالات اللاعبين"

        return "رياضة"

    # الشرق الأوسط
    if source in MIDDLE_EAST_SOURCES:
        return "الشرق الأوسط"

    # الأخبار الدولية
    if source in INTERNATIONAL_SOURCES:
        return "أخبار دولية"

    # الأخبار المغربية
    if source in MOROCCO_SOURCES:
        return "أخبار المغرب"

    # الاحتياط
    return "أخبار المغرب"


# =========================================================
# CLASSIFY
# =========================================================

def classify(text, source, trust):

    player = _player(text)

    category = _category(
        text,
        source
    )

    status = _official_status(
        text,
        trust
    )

    summary = _clean_summary(
        text
    )

    return (
        category,
        status,
        summary,
        player
    )
