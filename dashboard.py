```python
from flask import Flask, jsonify, render_template_string

from config import DASHBOARD_HOST, DASHBOARD_PORT
from db import recent


app = Flask(__name__)

HTML = '''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Morocco News AI | الأخبار المغربية</title>
  <style>
    :root {
      --ink: #12213b;
      --muted: #68758a;
      --surface: #ffffff;
      --canvas: #f3f6fa;
      --accent: #e83d4f;
      --accent-dark: #bd2537;
      --navy: #071a33;
      --line: #e2e8f0;
      --shadow: 0 12px 28px rgba(17, 35, 61, .08);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      color: var(--ink);
      background: var(--canvas);
      font-family: Tahoma, Arial, sans-serif;
      line-height: 1.7;
    }

    a { color: inherit; }

    .hero {
      color: #fff;
      background: radial-gradient(circle at 85% 10%, #1e5382 0, transparent 30%), var(--navy);
      border-bottom: 4px solid var(--accent);
    }

    .hero-inner,
    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }

    .hero-inner { padding: 42px 0 36px; }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 10px;
      color: #b9d8f4;
      font-size: .78rem;
      font-weight: 700;
      letter-spacing: .08em;
    }

    .live-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #5ee6a8;
      box-shadow: 0 0 0 5px rgba(94, 230, 168, .15);
    }

    h1 {
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.25rem);
      line-height: 1.15;
    }

    .subtitle {
      max-width: 650px;
      margin: 14px 0 0;
      color: #c9d6e6;
      font-size: 1.04rem;
    }

    .summary-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
      margin-top: 27px;
      padding: 14px 18px;
      border: 1px solid rgba(255, 255, 255, .16);
      border-radius: 14px;
      background: rgba(255, 255, 255, .08);
    }

    .summary-bar strong {
      display: block;
      font-size: 1.35rem;
    }

    .summary-bar span {
      color: #b9c9da;
      font-size: .84rem;
    }

    main { padding: 30px 0 54px; }

    .section-heading {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }

    .section-heading h2 {
      margin: 0;
      font-size: 1.25rem;
    }

    .section-heading p {
      margin: 0;
      color: var(--muted);
      font-size: .9rem;
    }

    .news-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }

    .card {
      position: relative;
      display: flex;
      flex-direction: column;
      min-height: 250px;
      padding: 22px;
      overflow: hidden;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: var(--shadow);
      transition: transform .2s ease, box-shadow .2s ease;
    }

    .card:hover {
      transform: translateY(-3px);
      box-shadow: 0 18px 34px rgba(17, 35, 61, .13);
    }

    .card::before {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      left: 0;
      height: 4px;
      background: linear-gradient(90deg, #f18c44, var(--accent));
    }

    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-bottom: 13px;
    }

    .tag {
      padding: 3px 9px;
      border-radius: 999px;
      background: #eef3f8;
      color: #42536a;
      font-size: .75rem;
      font-weight: 700;
    }

    .tag.status {
      color: #b32135;
      background: #fce9ec;
    }

    .card h3 {
      margin: 0;
      font-size: 1.18rem;
      line-height: 1.55;
    }

    .card h3 a { text-decoration: none; }

    .card h3 a:hover { color: var(--accent-dark); }

    .card p {
      margin: 12px 0 20px;
      color: #55657a;
      font-size: .94rem;
    }

    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-top: auto;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }

    .player {
      color: var(--muted);
      font-size: .82rem;
    }

    .source-link {
      color: var(--accent-dark);
      font-size: .87rem;
      font-weight: 700;
      text-decoration: none;
    }

    .source-link:hover { text-decoration: underline; }

    .empty {
      padding: 54px 24px;
      border: 1px dashed #b8c5d4;
      border-radius: 16px;
      color: var(--muted);
      text-align: center;
      background: #fff;
    }

    @media (max-width: 700px) {
      .hero-inner { padding-top: 32px; }

      .news-grid { grid-template-columns: 1fr; }

      .summary-bar {
        align-items: flex-start;
        flex-direction: column;
      }

      .section-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 4px;
      }

      .card { min-height: 0; }
    }
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <p class="eyebrow">
        <span class="live-dot"></span>
        MONITORING DESK · تحديثات مستمرة
      </p>

      <h1>Morocco News AI</h1>

      <p class="subtitle">
        غرفة أخبار ذكية تتابع كل ما يخص المغرب واللاعبين المغاربة المحترفين،
        في واجهة مصممة للقراءة السريعة.
      </p>

      <div class="summary-bar">
        <div>
          <strong>{{ items|length }}</strong>
          <span>خبرًا في آخر تحديث</span>
        </div>
        <span>يتم فرز الأخبار والتحقق من مصدرها تلقائيًا</span>
      </div>
    </div>
  </header>

  <main>
    <div class="section-heading">
      <h2>أحدث الأخبار</h2>
      <p>اضغط على العنوان أو المصدر لقراءة الخبر الأصلي</p>
    </div>

    {% if items %}
      <section class="news-grid" aria-label="قائمة الأخبار">
        {% for x in items %}
          <article class="card">
            <div class="tags">
              <span class="tag">{{ x.source }}</span>
              <span class="tag">{{ x.category }}</span>
              <span class="tag status">{{ x.status }}</span>
            </div>

            <h3>
              <a href="{{ x.url }}" target="_blank" rel="noopener noreferrer">
                {{ x.title }}
              </a>
            </h3>

            {% if x.summary %}
              <p>{{ x.summary }}</p>
            {% endif %}

            <footer class="card-footer">
              <span class="player">
                {% if x.player %}
                  اللاعب: {{ x.player }}
                {% else %}
                  أخبار المغرب
                {% endif %}
              </span>

              <a class="source-link"
                 href="{{ x.url }}"
                 target="_blank"
                 rel="noopener noreferrer">
                اقرأ المصدر ←
              </a>
            </footer>
          </article>
        {% endfor %}
      </section>
    {% else %}
      <div class="empty">
        لا توجد أخبار محفوظة حتى الآن. ستظهر هنا عند انتهاء أول عملية جمع.
      </div>
    {% endif %}
  </main>
</body>
</html>'''


@app.get("/")
def home():
    return render_template_string(HTML, items=recent(100))


@app.get("/api/news")
def api_news():
    return jsonify(recent(100))


@app.get("/health")
def health():
    return {"ok": True}


def run_dashboard():
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT)
```
