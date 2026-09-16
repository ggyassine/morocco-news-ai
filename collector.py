import feedparser, hashlib, html, re
from datetime import datetime, timezone
from sources import SOURCES, MOROCCO_TERMS, MOROCCAN_PLAYERS
from db import exists, add
from classifier import classify
from config import MAX_ITEMS_PER_SOURCE

def clean(s):
    s = html.unescape(re.sub('<[^>]+>', ' ', s or ''))
    return re.sub(r'\s+', ' ', s).strip()

def relevant(text):
    t = text.lower()
    return any(x.lower() in t for x in MOROCCO_TERMS) or any(x.lower() in t for x in MOROCCAN_PLAYERS)

def collect():
    fresh=[]
    for source, rss, trust in SOURCES:
        try:
            feed=feedparser.parse(rss)
            for e in feed.entries[:MAX_ITEMS_PER_SOURCE]:
                url=e.get('link','').strip(); title=clean(e.get('title',''))
                if not url or not title or exists(url): continue
                text=clean(title+' '+e.get('summary','')+' '+e.get('description',''))
                if not relevant(text): continue
                category,status,summary,player=classify(text, source, trust)
                item={'title':title,'url':url,'source':source,'trust':trust,
                      'published':e.get('published', e.get('updated','')),
                      'discovered':datetime.now(timezone.utc).isoformat(),'category':category,
                      'status':status,'summary':summary,'player':player,
                      'content_hash':hashlib.sha256(text.encode()).hexdigest()}
                add(item); fresh.append(item)
        except Exception as ex:
            print('Source error', source, ex)
    return fresh
