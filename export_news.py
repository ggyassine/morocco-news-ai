import json
from db import recent

items = recent(100)

with open("docs/news.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Exported {len(items)} news items")
