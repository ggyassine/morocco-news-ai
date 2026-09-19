import re

from sources import (
    MOROCCAN_PLAYERS,
    TRANSFER_TERMS,
)


# =========================================================
# STATUS
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
# SPORTS
# =========================================================

SPORTS_TERMS = [

    "كرة القدم",
    "كرة السلة",
    "كرة اليد",
    "التنس",
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
    "هدف",
    "أهداف",
    "فوز",
    "خسارة",
    "تعادل",
    "تصفيات",
    "كأس",
    "دوري أبطال",
    "دوري الأبطال",
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
    "basketball",
    "tennis",
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
# PLAYER
# =========================================================

def _player(text):

    low = text.lower()

    for name in sorted(
        MOROCCAN_PLAYERS,
        key=len,
        reverse=True
    ):

        if name.lower() in low:
            return name

    return ""


# =========================================================
# TRANSFER
# =========================================================

def _is_transfer(text):

    low = text.lower()

    has_transfer_term = any(
        term.lower() in low
        for term in TRANSFER_TERMS
    )

    return (
        has_transfer_term
        and bool(_player(text))
    )


# =========================================================
# SPORT
# =========================================================

def _is_sport(text):

    low = text.lower()

    return any(
        term.lower() in low
        for term in SPORTS_TERMS
    )


# =========================================================
# STATUS
# =========================================================

def _status(text, trust):

    low = text.lower()

    # النفي أولًا
    denied_words = [
        "نفى",
        "ينفي",
        "نفيا",
        "منفي",
        "غير صحيح",
        "لا صحة",
        "denied",
        "denies",
        "false",
    ]

    if any(
        word in low
        for word in denied_words
    ):
        return "منفي"


    # إعارة
    loan_words = [
        "إعارة",
        "loan",
    ]

    if any(
        word in low
        for word in loan_words
    ):
        return "إعارة"


    # تجديد
    renewal_words = [
        "تجديد",
        "يجدد",
        "جدد",
        "renewal",
        "renewed",
    ]

    if any(
        word in low
        for word in renewal_words
    ):
        return "تجديد"


    # رسمي
    official_words = [
        "رسميا",
        "رسميًا",
        "رسمي",
        "يوقع",
        "وقع",
        "تعاقد",
        "أعلن النادي",
        "الإعلان الرسمي",
        "official",
        "officially",
        "signed",
        "signs",
        "announced",
    ]

    if any(
        word in low
        for word in official_words
    ):

        if trust == "A":
            return "رسمي"

        return "مؤكد"


    # اتفاق
    confirmed_words = [
        "مؤكد",
        "اتفاق",
        "تم الاتفاق",
        "توصل لاتفاق",
        "اتفاق مبدئي",
        "confirmed",
        "agreement",
        "deal",
    ]

    if any(
        word in low
        for word in confirmed_words
    ):
        return "مؤكد"


    # مفاوضات
    negotiation_words = [
        "مفاوضات",
        "يجري التفاوض",
        "محادثات",
        "اهتمام",
        "عرض",
        "negotiation",
        "negotiations",
        "talks",
        "interest",
        "offer",
    ]

    if any(
        word in low
        for word in negotiation_words
    ):
        return "مفاوضات"


    # إشاعة
    rumor_words = [
        "إشاعة",
        "شائعة",
        "تقارير",
        "بحسب تقارير",
        "يقال",
        "rumor",
        "rumour",
        "reportedly",
    ]

    if any(
        word in low
        for word in rumor_words
    ):
        return "إشاعة"


    return "غير واضح"


# =========================================================
# REMOVE DUPLICATE TEXT
# =========================================================

def _remove_repeated_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()


    # تقسيم النص إلى جمل
    sentences = re.split(
        r"(?<=[.!؟])\s+",
        text
    )


    unique = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # منع تكرار الجملة نفسها
        if sentence not in unique:

            unique.append(
                sentence
            )


    text = " ".join(unique)


    # البحث عن تكرار كتلة نصية
    words = text.split()

    if len(words) >= 20:

        for size in range(
            min(40, len(words) // 2),
            7,
            -1
        ):

            first = " ".join(
                words[:size]
            ).strip()

            second_start = size

            second_end = min(
                len(words),
                size * 2
            )

            second = " ".join(
                words[
                    second_start:
                    second_end
                ]
            ).strip()

            if (
                first
                and second
                and first == second
            ):

                words = words[
                    :size
                ]

                text = " ".join(
                    words
                )

                break


    # الحد الأقصى
    if len(text) > 420:

        text = (
            text[:420]
            .rsplit(" ", 1)[0]
            + "..."
        )


    return text


# =========================================================
# REMOVE TITLE-LIKE REPETITION
# =========================================================

def _make_summary(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()


    # إذا كان النص قصيرًا
    if len(text) <= 180:
        return text


    sentences = re.split(
        r"(?<=[.!؟])\s+",
        text
    )


    # إزالة الجملة الأولى إذا كانت عنوانًا
    # ثم استعمال باقي النص كملخص
    if len(sentences) >= 2:

        first = sentences[0].strip()
        rest = " ".join(
            sentences[1:]
        ).strip()

        if (
            len(first) < 180
            and len(rest) > 40
        ):

            text = rest


    return _remove_repeated_text(
        text
    )


# =========================================================
# CATEGORY
# =========================================================

def _category(text, source):

    # الانتقالات أولًا
    # حتى لا تتحول أخبار الانتقالات
    # إلى رياضة فقط
    if _is_transfer(text):
        return "انتقالات اللاعبين"


    # الرياضة
    if _is_sport(text):
        return "رياضة"


    # الشرق الأوسط
    if source in MIDDLE_EAST_SOURCES:
        return "الشرق الأوسط"


    # الأخبار الدولية
    if source in INTERNATIONAL_SOURCES:
        return "أخبار دولية"


    # المغرب
    if source in MOROCCO_SOURCES:
        return "أخبار المغرب"


    # الاحتياط
    return "أخبار المغرب"


# =========================================================
# MAIN CLASSIFIER
# =========================================================

def classify(
    text,
    source,
    trust
):

    player = _player(text)

    category = _category(
        text,
        source
    )

    status = _status(
        text,
        trust
    )

    summary = _make_summary(
        text
    )

    return (
        category,
        status,
        summary,
        player
)
