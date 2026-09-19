import feedparser
import hashlib
import html
import re

from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from sources import SOURCES, MOROCCO_TERMS, MOROCCAN_PLAYERS
from db import exists, add
from classifier import classify
from config import MAX_ITEMS_PER_SOURCE


USER_AGENT = (
    "Mozilla/5.0 (compatible; MoroccoNewsAI/1.0; "
    "+https://github.com/ggyassine/morocco-news-ai)"
)

FETCH_TIMEOUT = 10


# ============================================================
# SOURCE GROUPS
# ============================================================

# 🇲🇦 أخبار المغرب
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


# 🌐 الشرق الأوسط
MIDDLE_EAST_SOURCES = {
    "الجزيرة",
    "العربية",
    "سكاي نيوز عربية",
    "الشرق للأخبار",
    "الشرق الأوسط",
    "العربي الجديد",
}


# 🌍 العالم بالعربية
WORLD_ARABIC_SOURCES = {
    "القدس العربي",
    "فرانس 24 عربي",
    "DW عربية",
    "BBC عربي",
    "يورونيوز عربي",
    "إندبندنت عربية",
    "CNN بالعربية",
}


# 🔎 مصادر دولية للتحقق والرصد
INTERNATIONAL_SOURCES = {
    "Reuters",
    "Associated Press",
}


# ============================================================
# CLEAN TEXT
# ============================================================

def clean(s):
    """
    تنظيف النص من HTML والمسافات الزائدة.
    """

    s = html.unescape(
        re.sub(
            r"<[^>]+>",
            " ",
            s or ""
        )
    )

    return re.sub(
        r"\s+",
        " ",
        s
    ).strip()


# ============================================================
# SOURCE GROUP
# ============================================================

def get_source_group(source):
    """
    تحديد المجموعة التي ينتمي إليها المصدر.
    """

    if source in MOROCCO_SOURCES:
        return "morocco"

    if source in MIDDLE_EAST_SOURCES:
        return "middle_east"

    if source in WORLD_ARABIC_SOURCES:
        return "world_arabic"

    if source in INTERNATIONAL_SOURCES:
        return "international"

    return "other"


# ============================================================
# RELEVANCE
# ============================================================

def relevant(text, source):
    """
    تحديد ما إذا كان الخبر يستحق الحفظ.
    """

    t = text.lower()

    # 🇲🇦 أخبار المغرب
    if source in MOROCCO_SOURCES:
        return (
            any(
                term.lower() in t
                for term in MOROCCO_TERMS
            )
            or any(
                player.lower() in t
                for player in MOROCCAN_PLAYERS
            )
        )

    # 🌐 الشرق الأوسط
    if source in MIDDLE_EAST_SOURCES:
        return True

    # 🌍 العالم بالعربية
    if source in WORLD_ARABIC_SOURCES:
        return True

    # 🔎 المصادر الدولية
    if source in INTERNATIONAL_SOURCES:
        return True

    # مصدر غير معروف
    return (
        any(
            term.lower() in t
            for term in MOROCCO_TERMS
        )
        or any(
            player.lower() in t
            for player in MOROCCAN_PLAYERS
        )
    )


# ============================================================
# FETCH RSS
# ============================================================

def fetch_feed(url):
    """
    تحميل RSS مع User-Agent.
    """

    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "application/rss+xml, "
                "application/xml, "
                "text/xml, "
                "*/*"
            ),
        },
    )

    try:

        with urlopen(
            request,
            timeout=FETCH_TIMEOUT
        ) as response:

            data = response.read()

        return feedparser.parse(data)

    except HTTPError as ex:

        print(
            f"RSS HTTP error: {ex.code} - {url}"
        )

        return None

    except URLError as ex:

        print(
            f"RSS URL error: {ex.reason} - {url}"
        )

        return None

    except TimeoutError:

        print(
            f"RSS TIMEOUT: {url}"
        )

        return None

    except Exception as ex:

        print(
            f"RSS error: {url} - {ex}"
        )

        return None


# ============================================================
# COLLECT
# ============================================================

def collect():

    fresh = []

    for source, rss, trust in SOURCES:

        print(
            f"\n[{source}] Checking RSS..."
        )

        feed = fetch_feed(rss)

        if feed is None:

            print(
                f"[{source}] SKIPPED"
            )

            continue

        entries = feed.entries[
            :MAX_ITEMS_PER_SOURCE
        ]

        total = len(entries)

        duplicates = 0
        irrelevant = 0
        accepted = 0

        group = get_source_group(source)

        print(
            f"[{source}] Group: {group}"
        )

        print(
            f"[{source}] RSS entries: {total}"
        )

        for e in entries:

            try:

                url = e.get(
                    "link",
                    ""
                ).strip()

                title = clean(
                    e.get(
                        "title",
                        ""
                    )
                )

                if not url or not title:
                    continue

                # منع التكرار
                if exists(url):

                    duplicates += 1

                    continue

                # النص المستخدم للتحقق
                text = clean(
                    title
                    + " "
                    + e.get(
                        "summary",
                        ""
                    )
                    + " "
                    + e.get(
                        "description",
                        ""
                    )
                )

                # فلترة الخبر
                if not relevant(
                    text,
                    source
                ):

                    irrelevant += 1

                    continue

                # التصنيف
                category, status, summary, player = classify(
                    text,
                    source,
                    trust
                )

                published = e.get(
                    "published",
                    e.get(
                        "updated",
                        ""
                    )
                )

                item = {

                    "title": title,

                    "url": url,

                    "source": source,

                    "trust": trust,

                    "published": published,

                    "discovered": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),

                    "category": category,

                    "status": status,

                    "summary": summary,

                    "player": player,

                    "source_group": group,

                    "content_hash": hashlib.sha256(
                        text.encode(
                            "utf-8"
                        )
                    ).hexdigest(),
                }

                add(item)

                fresh.append(item)

                accepted += 1

            except Exception as ex:

                print(
                    f"[{source}] Article error: {ex}"
                )

                continue

        print(
            f"[{source}] "
            f"duplicates={duplicates} "
            f"irrelevant={irrelevant} "
            f"accepted={accepted}"
        )

    print(
        f"\nTOTAL new relevant items: "
        f"{len(fresh)}"
    )

    return fresh
