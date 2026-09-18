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


# كلمات المحتوى غير المرغوب فيه
EXCLUDED_TERMS = [
    # العقار
    "شقة للبيع",
    "شقق للبيع",
    "شقة للكراء",
    "شقق للكراء",
    "عقار",
    "عقارات",
    "للبيع",
    "للشراء",
    "للكراء",
    "للإيجار",
    "إيجار",
    "كراء",
    "منزل للبيع",
    "منازل للبيع",
    "أرض للبيع",
    "أراضي للبيع",

    # السيارات والإعلانات التجارية
    "سيارة للبيع",
    "سيارات للبيع",
    "سيارة مستعملة للبيع",
    "منتجات",
    "تخفيضات",
    "عروض تجارية",
    "عرض تجاري",
    "إعلان",
    "إعلانات",
    "إشهار",

    # الوظائف
    "وظائف",
    "وظيفة",
    "توظيف",
    "مباراة توظيف",
    "مطلوب للعمل",
    "عرض عمل",
    "عروض العمل",
    "فرصة عمل",
    "فرص عمل",

    # محتوى تجاري
    "متجر",
    "شراء الآن",
    "اطلب الآن",
    "promo",
    "promotion",
    "discount",
]


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def relevant(text):
    t = text.lower()

    # استبعاد المحتوى التجاري والإعلاني
    if any(term.lower() in t for term in EXCLUDED_TERMS):
        return False

    # قبول الأخبار المرتبطة بالمغرب
    # أو اللاعبين المغاربة
    return (
        any(term.lower() in t for term in MOROCCO_TERMS)
        or any(player.lower() in t for player in MOROCCAN_PLAYERS)
    )


def fetch_feed(url):
    """
    تحميل RSS مع مهلة قصوى 10 ثوانٍ.
    إذا تعطل المصدر، ننتقل مباشرة إلى المصدر التالي.
    """

    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "application/rss+xml, "
                "application/xml, "
                "text/xml, */*"
            ),
        },
    )

    try:
        with urlopen(request, timeout=FETCH_TIMEOUT) as response:
            data = response.read()

        return feedparser.parse(data)

    except HTTPError as ex:
        print(f"RSS HTTP error: {ex.code} - {url}")
        return None

    except URLError as ex:
        print(f"RSS URL error: {ex.reason} - {url}")
        return None

    except TimeoutError:
        print(f"RSS TIMEOUT: {url}")
        return None

    except Exception as ex:
        print(f"RSS error: {url} - {ex}")
        return None


def collect():
    fresh = []

    for source, rss, trust in SOURCES:

        print(f"\n[{source}] Checking RSS...")

        feed = fetch_feed(rss)

        if feed is None:
            print(f"[{source}] SKIPPED")
            continue

        entries = feed.entries[:MAX_ITEMS_PER_SOURCE]

        total = len(entries)
        duplicates = 0
        irrelevant = 0
        accepted = 0

        print(f"[{source}] RSS entries: {total}")

        for e in entries:

            try:
                url = e.get("link", "").strip()
                title = clean(e.get("title", ""))

                if not url or not title:
                    continue

                # منع الأخبار الموجودة مسبقًا
                if exists(url):
                    duplicates += 1
                    continue

                text = clean(
                    title
                    + " "
                    + e.get("summary", "")
                    + " "
                    + e.get("description", "")
                )

                # فلترة الأخبار
                if not relevant(text):
                    irrelevant += 1
                    continue

                category, status, summary, player = classify(
                    text,
                    source,
                    trust
                )

                item = {
                    "title": title,
                    "url": url,
                    "source": source,
                    "trust": trust,
                    "published": e.get(
                        "published",
                        e.get("updated", "")
                    ),
                    "discovered": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "category": category,
                    "status": status,
                    "summary": summary,
                    "player": player,
                    "content_hash": hashlib.sha256(
                        text.encode("utf-8")
                    ).hexdigest(),
                }

                add(item)
                fresh.append(item)
                accepted += 1

            except Exception as ex:
                print(f"[{source}] Article error: {ex}")
                continue

        print(
            f"[{source}] "
            f"duplicates={duplicates} "
            f"irrelevant={irrelevant} "
            f"accepted={accepted}"
        )

    print(f"\nTOTAL new relevant items: {len(fresh)}")

    return fresh
