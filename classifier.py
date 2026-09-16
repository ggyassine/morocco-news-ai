import re

from sources import MOROCCAN_PLAYERS, TRANSFER_TERMS


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


def _player(text):
    low = text.lower()

    for name in MOROCCAN_PLAYERS:
        if name.lower() in low:
            return name

    return ""


def _fallback(text, trust):
    p = _player(text)

    transfer = (
        any(x.lower() in text.lower() for x in TRANSFER_TERMS)
        and bool(p)
    )

    if transfer:
        official_words = re.search(
            r"official|officially|signed|signs|"
            r"رسميا|رسمي|يوقع|وقع|تعاقد|أعلن النادي",
            text.lower()
        )

        status = "رسمي" if trust == "A" and official_words else "غير واضح"

        return (
            "انتقالات اللاعبين",
            status,
            text[:360],
            p
        )

    return (
        "أخبار المغرب",
        "مؤكد" if trust == "A" else "غير واضح",
        text[:360],
        p
    )


def classify(text, source, trust):
    """
    تصنيف محلي بدون OpenAI API.
    """

    return _fallback(text, trust)
