import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / 'data' / 'news.db'
DB.parent.mkdir(exist_ok=True)

SCHEMA = '''
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
CREATE INDEX IF NOT EXISTS idx_news_discovered ON news(discovered);
CREATE INDEX IF NOT EXISTS idx_news_player ON news(player);
CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
'''

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c

def exists(url):
    with conn() as c:
        return c.execute('SELECT 1 FROM news WHERE url=?', (url,)).fetchone() is not None

def add(item):
    with conn() as c:
        c.execute('''INSERT OR IGNORE INTO news
        (title,url,source,trust,published,discovered,category,status,summary,player,content_hash)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)''', tuple(item.get(k) for k in
        ['title','url','source','trust','published','discovered','category','status','summary','player','content_hash']))
        c.commit()

def recent_unsent(limit=50):
    with conn() as c:
        rows = c.execute('SELECT * FROM news WHERE sent=0 ORDER BY discovered DESC LIMIT ?', (limit,)).fetchall()
        return [dict(r) for r in rows]

def mark_sent(ids):
    if not ids: return
    with conn() as c:
        c.executemany('UPDATE news SET sent=1 WHERE id=?', [(i,) for i in ids])
        c.commit()

def recent(limit=100):
    with conn() as c:
        rows = c.execute('SELECT * FROM news ORDER BY discovered DESC LIMIT ?', (limit,)).fetchall()
        return [dict(r) for r in rows]
