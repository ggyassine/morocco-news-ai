import re

from sources import (
    MOROCCAN_PLAYERS,
    TRANSFER_TERMS,
)


# ============================================================
# STATUS
# ============================================================

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
# SPORTS TERMS
# ============================================================

SPORTS_TERMS = [
    "رياضة",
    "رياضي",
    "كرة القدم",
    "مباراة",
    "مباريات",
    "دوري",
    "بطولة",
    "كأس",
    "منتخب",
    "لاعب",
    "لاعبين",
    "مدرب",
    "نادي",
    "أهداف",
    "هدف",
    "تصفيات",
    "الدوري المغربي",
    "البطولة الاحترافية",
    "دوري أبطال أوروبا",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الفرنسي",
    "الدوري الإيطالي",
    "دوري أبطال إفريقيا",
    "كأس إفريقيا",
    "كأس العالم",
    "football",
    "soccer",
    "match",
    "matches",
    "league",
    "cup",
    "champions",
]


# ============================================================
# HELPERS
# ============================================================

def contains_any(text, terms):
    text = text.lower()

    return any(
        term.lower() in text
        for term in terms
    )


def find_player(text):
    text_lower = text.lower()

    for player in MOROCCAN_PLAYERS:
        if player.lower() in text_lower:
            return player

    return ""


def is_transfer(text):
    return contains_any(
        text,
        TRANSFER_TERMS
    )


def is_sports(text):
    return contains_any(
        text,
        SPORTS_TERMS
    )


# ============================================================
# TRANSFER STATUS
# ============================================================

def detect_status(text, trust):
    t = text.lower()

    # رسمي
    official_patterns = [
        "رسمي",
        "رسميا",
        "رسميًا",
        "يعلن النادي",
        "أعلن النادي",
        "أعلن",
        "وقع",
        "يوقع",
        "تعاقد",
        "تم التوقيع",
        "signed",
        "signs",
        "official",
        "officially",
    ]

    if any(
        pattern in t
        for pattern in official_patterns
    ):
        return "رسمي"

    # اتفاق
    agreement_patterns = [
        "اتفاق مبدئي",
        "اتفق مع",
        "توصل إلى اتفاق",
        "اتفاق",
        "agreement",
        "agreed",
    ]

    if any(
        pattern in t
        for pattern in agreement_patterns
    ):
        return "اتفاق مبدئي"

    # مفاوضات
    negotiation_patterns = [
        "مفاوضات",
        "يتفاوض",
        "تفاوض",
        "negotiation",
        "negotiations",
    ]

    if any(
        pattern in t
        for pattern in negotiation_patterns
    ):
        return "مفاوضات"

    # اهتمام
    interest_patterns = [
        "اهتمام",
        "مهتم",
        "يرغب في ضمه",
        "interest",
        "interested",
    ]

    if any(
        pattern in t
        for pattern in interest_patterns
    ):
        return "اهتمام"

    # عرض
    offer_patterns = [
        "عرض",
        "عرضًا",
        "offer",
        "bid",
    ]

    if any(
        pattern in t
        for pattern in offer_patterns
    ):
        return "عرض"

    # إعارة
    loan_patterns = [
        "إعارة",
        "معارا",
        "معارًا",
        "loan",
    ]

    if any(
        pattern in t
        for pattern in loan_patterns
    ):
        return "إعارة"

    # تجديد
    renewal_patterns = [
        "تجديد",
        "يجدد",
        "جدد عقده",
        "renewal",
        "renewed",
        "extends",
        "extension",
    ]

    if any(
        pattern in t
        for pattern in renewal_patterns
    ):
        return "تجديد"

    # إشاعة
    rumor_patterns = [
        "إشاعة",
        "شائعة",
        "أنباء",
        "تقارير",
        "بحسب مصادر",
        "rumor",
        "rumour",
        "reports",
    ]

    if any(
        pattern in t
        for pattern in rumor_patterns
    ):
        return "إشاعة"

    # مصدر موثوق مع خبر انتقال
    if trust == "A":
        return "مؤكد"

    return "غير واضح"


# ============================================================
# SUMMARY
# ============================================================

def make_summary(text):
    """
    إنشاء ملخص قصير بدون تكرار العنوان.
    """

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if len(text) <= 320:
        return text

    return text[:320].rsplit(
        " ",
        1
    )[0] + "..."


# ============================================================
# CATEGORY
# ============================================================

def detect_category(text, source):
    """
    تحديد القسم الرئيسي للخبر.
    """

    # 🔄 الانتقالات أولًا
    # لأن خبر انتقال لاعب يجب أن يظهر
    # في قسم الانتقالات حتى لو كان رياضيًا.
    if is_transfer(text):

        player = find_player(text)

        if player:
            return "انتقالات اللاعبين"

    # ⚽ الرياضة
    if is_sports(text):

        if source in MOROCCO_SOURCES:
            return "الرياضة"

    # 🇲🇦 المغرب
    if source in MOROCCO_SOURCES:
        return "أخبار المغرب"

    # 🌐 الشرق الأوسط
    if source in MIDDLE_EAST_SOURCES:
        return "الشرق الأوسط"

    # 🌍 العالم بالعربية
    if source in WORLD_ARABIC_SOURCES:
        return "العالم بالعربية"

    # 🔎 المصادر الدولية
    if source in INTERNATIONAL_SOURCES:
        return "مصادر دولية"

    return "أخبار أخرى"


# ============================================================
# MAIN CLASSIFIER
# ============================================================

def classify(text, source, trust):

    player = find_player(text)

    category = detect_category(
        text,
        source
    )

    status = "غير واضح"

    # حالة الانتقالات
    if category == "انتقالات اللاعبين":

        status = detect_status(
            text,
            trust
        )

    # الأخبار الرياضية
    elif category == "الرياضة":

        status = (
            "مؤكد"
            if trust == "A"
            else "غير واضح"
        )

    # الأخبار المغربية
    elif category == "أخبار المغرب":

        status = (
            "مؤكد"
            if trust == "A"
            else "غير واضح"
        )

    # الشرق الأوسط
    elif category == "الشرق الأوسط":

        status = (
            "مؤكد"
            if trust == "A"
            else "غير واضح"
        )

    # العالم بالعربية
    elif category == "العالم بالعربية":

        status = (
            "مؤكد"
            if trust == "A"
            else "غير واضح"
        )

    # المصادر الدولية
    elif category == "مصادر دولية":

        status = (
            "مؤكد"
            if trust == "A"
            else "غير واضح"
        )

    summary = make_summary(
        text
    )

    return (
        category,
        status,
        summary,
        player
    )
