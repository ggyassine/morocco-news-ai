import feedparser
import hashlib
import html
import re

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from sources import SOURCES, MOROCCO_TERMS, MOROCCAN_PLAYERS
from db import exists, add
from classifier import classify
from config import MAX_ITEMS_PER_SOURCE


USER_AGENT = (
    "Mozilla/5.0 (compatible; MoroccoNewsAI/1.0)"
)


# =========================================================
# تنظيف النص
# =========================================================

def clean(s):
    s = html.unescape(
        re.sub(r'<[^>]+>', ' ', s or '')
    )

    return re.sub(
        r'\s+',
        ' ',
        s
    ).strip()


# =========================================================
# فلترة الأخبار المتعلقة بالمغرب
# =========================================================

def relevant(text):

    t = text.lower()

    return (
        any(
            x.lower() in t
            for x in MOROCCO_TERMS
        )
        or
        any(
            x.lower() in t
            for x in MOROCCAN_PLAYERS
        )
    )


# =========================================================
# استخراج الروابط من صفحات المواقع
# =========================================================

class ArticleParser(HTMLParser):

    def __init__(self):

        super().__init__()

        self.links = []

        self.current_url = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):

        if tag != 'a':
            return

        attrs = dict(attrs)

        href = attrs.get('href')

        if href:

            self.current_url = href
            self.current_text = []

    def handle_data(self, data):

        if self.current_url:

            self.current_text.append(data)

    def handle_endtag(self, tag):

        if tag != 'a':
            return

        if not self.current_url:
            return

        title = clean(
            ' '.join(self.current_text)
        )

        if title and len(title) >= 15:

            self.links.append(
                (
                    title,
                    self.current_url
                )
            )

        self.current_url = None
        self.current_text = []


# =========================================================
# تحميل الصفحة
# =========================================================

def fetch_page(url):

    try:

        request = Request(
            url,
            headers={
                'User-Agent': USER_AGENT,
                'Accept-Language': 'ar,en;q=0.8',
            }
        )

        with urlopen(
            request,
            timeout=15
        ) as response:

            return response.read().decode(
                'utf-8',
                errors='ignore'
            )

    except Exception as ex:

        print(
            f"[WEB ERROR] {url} -> {ex}"
        )

        return ''


# =========================================================
# الصفحات الرئيسية للمصادر العربية
# =========================================================

SOURCE_HOMEPAGES = {

    'MAP عربي':
        'https://www.mapnews.ma/ar/',

    'SNRTnews عربي':
        'https://snrtnews.com/ar/',

    'هسبريس':
        'https://www.hespress.com/',

    'Le360 عربي':
        'https://ar.le360.ma/',

    'العمق المغربي':
        'https://al3omk.com/',

    'اليوم24':
        'https://www.alyaoum24.com/',

    'أخبارنا المغربية':
        'https://www.akhbarona.com/',

    'هبة بريس':
        'https://ar.hibapress.com/',

    'برلمان':
        'https://www.barlamane.com/',

    'كود':
        'https://www.goud.ma/',

    'كيفاش':
        'https://kifache.com/',

    'فبراير':
        'https://febrayer.com/',

    'البطولة':
        'https://www.elbotola.com/ar/',

    'المنتخب':
        'https://www.almountakhab.com/',
}


# =========================================================
# جمع الأخبار من صفحة الموقع
# =========================================================

def collect_from_webpage(
    source,
    homepage,
    trust
):

    fresh = []

    page = fetch_page(homepage)

    if not page:

        print(
            f"[{source}] "
            f"Homepage unavailable"
        )

        return fresh

    parser = ArticleParser()

    try:

        parser.feed(page)

    except Exception as ex:

        print(
            f"[HTML ERROR] "
            f"{source} -> {ex}"
        )

        return fresh

    seen_urls = set()

    for title, raw_url in parser.links:

        if len(fresh) >= MAX_ITEMS_PER_SOURCE:
            break

        url = urljoin(
            homepage,
            raw_url
        )

        if url in seen_urls:
            continue

        seen_urls.add(url)

        if exists(url):
            continue

        text = clean(title)

        if not relevant(text):
            continue

        try:

            category, status, summary, player = classify(
                text,
                source,
                trust
            )

        except Exception as ex:

            print(
                f"[AI ERROR] "
                f"{source} -> {ex}"
            )

            continue

        item = {

            'title': title,

            'url': url,

            'source': source,

            'trust': trust,

            'published': '',

            'discovered':
                datetime.now(
                    timezone.utc
                ).isoformat(),

            'category': category,

            'status': status,

            'summary': summary,

            'player': player,

            'content_hash':
                hashlib.sha256(
                    text.encode()
                ).hexdigest()
        }

        add(item)

        fresh.append(item)

    print(
        f"[{source}] "
        f"HTML relevant={len(fresh)}"
    )

    return fresh


# =========================================================
# جمع الأخبار
# =========================================================

def collect():

    fresh = []

    for source, rss, trust in SOURCES:

        try:

            # -------------------------------------------------
            # محاولة RSS
            # -------------------------------------------------

            feed = feedparser.parse(rss)

            entries = feed.entries[
                :MAX_ITEMS_PER_SOURCE
            ]

            print(
                f"[{source}] "
                f"RSS entries: {len(entries)}"
            )

            duplicates = 0
            irrelevant = 0
            accepted = 0

            for e in entries:

                url = e.get(
                    'link',
                    ''
                ).strip()

                title = clean(
                    e.get(
                        'title',
                        ''
                    )
                )

                if not url or not title:
                    continue

                if exists(url):

                    duplicates += 1

                    continue

                text = clean(
                    title
                    + ' '
                    + e.get(
                        'summary',
                        ''
                    )
                    + ' '
                    + e.get(
                        'description',
                        ''
                    )
                )

                if not relevant(text):

                    irrelevant += 1

                    continue

                try:

                    category, status, summary, player = classify(
                        text,
                        source,
                        trust
                    )

                except Exception as ex:

                    print(
                        f"[AI ERROR] "
                        f"{source} -> {ex}"
                    )

                    continue

                item = {

                    'title': title,

                    'url': url,

                    'source': source,

                    'trust': trust,

                    'published':
                        e.get(
                            'published',
                            e.get(
                                'updated',
                                ''
                            )
                        ),

                    'discovered':
                        datetime.now(
                            timezone.utc
                        ).isoformat(),

                    'category': category,

                    'status': status,

                    'summary': summary,

                    'player': player,

                    'content_hash':
                        hashlib.sha256(
                            text.encode()
                        ).hexdigest()
                }

                add(item)

                fresh.append(item)

                accepted += 1

            print(
                f"[{source}] "
                f"duplicates={duplicates} "
                f"irrelevant={irrelevant} "
                f"accepted={accepted}"
            )

            # -------------------------------------------------
            # إذا لم يعط RSS أخباراً مفيدة
            # نحاول الصفحة الرئيسية
            # -------------------------------------------------

            if accepted == 0:

                homepage = SOURCE_HOMEPAGES.get(
                    source
                )

                if homepage:

                    print(
                        f"[{source}] "
                        f"Trying homepage..."
                    )

                    web_items = collect_from_webpage(
                        source,
                        homepage,
                        trust
                    )

                    fresh.extend(
                        web_items
                    )

        except Exception as ex:

            print(
                f"[SOURCE ERROR] "
                f"{source} -> {ex}"
            )

            # -------------------------------------------------
            # محاولة الصفحة عند فشل RSS
            # -------------------------------------------------

            homepage = SOURCE_HOMEPAGES.get(
                source
            )

            if homepage:

                print(
                    f"[{source}] "
                    f"RSS failed -> homepage fallback"
                )

                web_items = collect_from_webpage(
                    source,
                    homepage,
                    trust
                )

                fresh.extend(
                    web_items
                )

    print(
        f"TOTAL new relevant items: "
        f"{len(fresh)}"
    )

    return fresh
