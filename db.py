import sqlite3
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

DB = (
    Path(__file__).resolve().parent
    / "data"
    / "news.db"
)

DB.parent.mkdir(
    exist_ok=True
)


# ============================================================
# SCHEMA
# ============================================================

SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    trust TEXT NOT NULL,
    published TEXT,
    discovered TEXT NOT NULL,
    category TEXT,
    status TEXT,
    summary TEXT,
    player TEXT,
    content_hash TEXT,
    sent INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_news_discovered
ON news(discovered);

CREATE INDEX IF NOT EXISTS idx_news_player
ON news(player);

CREATE INDEX IF NOT EXISTS idx_news_category
ON news(category);

CREATE INDEX IF NOT EXISTS idx_news_status
ON news(status);
"""


# ============================================================
# CONNECTION
# ============================================================

def conn():
    c = sqlite3.connect(DB)

    c.row_factory = sqlite3.Row

    c.executescript(
        SCHEMA
    )

    return c


# ============================================================
# CHECK IF NEWS EXISTS
# ============================================================

def exists(url):

    if not url:
        return False

    with conn() as c:

        row = c.execute(
            """
            SELECT 1
            FROM news
            WHERE url = ?
            LIMIT 1
            """,
            (url,)
        ).fetchone()

        return row is not None


# ============================================================
# ADD NEW NEWS
# ============================================================

def add(item):

    with conn() as c:

        c.execute(
            """
            INSERT OR IGNORE INTO news (
                title,
                url,
                source,
                trust,
                published,
                discovered,
                category,
                status,
                summary,
                player,
                content_hash,
                sent
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                item.get("title", ""),
                item.get("url", ""),
                item.get("source", ""),
                item.get("trust", "C"),
                item.get("published"),
                item.get("discovered"),
                item.get("category"),
                item.get("status"),
                item.get("summary"),
                item.get("player"),
                item.get("content_hash"),
                item.get("sent", 0),
            )
        )

        c.commit()


# ============================================================
# UPDATE EXISTING NEWS
# ============================================================

def update_item(item):

    url = item.get(
        "url",
        ""
    )

    if not url:
        return False

    with conn() as c:

        cursor = c.execute(
            """
            UPDATE news
            SET
                title = ?,
                source = ?,
                trust = ?,
                published = ?,
                category = ?,
                status = ?,
                summary = ?,
                player = ?,
                content_hash = ?
            WHERE url = ?
            """,
            (
                item.get("title", ""),
                item.get("source", ""),
                item.get("trust", "C"),
                item.get("published"),
                item.get("category"),
                item.get("status"),
                item.get("summary"),
                item.get("player"),
                item.get("content_hash"),
                url,
            )
        )

        c.commit()

        return cursor.rowcount > 0


# ============================================================
# UPDATE OR INSERT
# ============================================================

def upsert(item):

    url = item.get(
        "url",
        ""
    )

    if not url:
        return False

    if exists(url):

        return update_item(item)

    add(item)

    return True


# ============================================================
# RECENT UNSENT
# ============================================================

def recent_unsent(limit=50):

    with conn() as c:

        rows = c.execute(
            """
            SELECT *
            FROM news
            WHERE sent = 0
            ORDER BY discovered DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


# ============================================================
# MARK AS SENT
# ============================================================

def mark_sent(ids):

    if not ids:
        return

    with conn() as c:

        c.executemany(
            """
            UPDATE news
            SET sent = 1
            WHERE id = ?
            """,
            [
                (item_id,)
                for item_id in ids
            ]
        )

        c.commit()


# ============================================================
# RECENT NEWS
# ============================================================

def recent(limit=100):

    with conn() as c:

        rows = c.execute(
            """
            SELECT *
            FROM news
            ORDER BY discovered DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]
