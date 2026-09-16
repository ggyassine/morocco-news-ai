from flask import Flask, jsonify, render_template_string
from db import recent
from config import DASHBOARD_HOST, DASHBOARD_PORT

app=Flask(__name__)
HTML='''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Morocco News AI</title><style>body{font-family:Arial;background:#f5f5f5;margin:0;padding:20px}.wrap{max-width:1000px;margin:auto}.card{background:white;padding:16px;margin:12px 0;border-radius:10px;box-shadow:0 1px 5px #ddd}a{color:#0645ad}small{color:#666}</style></head><body><div class="wrap"><h1>Morocco News AI</h1><p>آخر الأخبار التي جمعها النظام</p>{% for x in items %}<div class="card"><h2>{{x.title}}</h2><p>{{x.summary}}</p><small>{{x.source}} | {{x.category}} | {{x.status}}{% if x.player %} | {{x.player}}{% endif %}</small><p><a href="{{x.url}}" target="_blank">المصدر الأصلي</a></p></div>{% endfor %}</div></body></html>'''

@app.get('/')
def home(): return render_template_string(HTML, items=recent(100))
@app.get('/api/news')
def api_news(): return jsonify(recent(100))
@app.get('/health')
def health(): return {'ok':True}

def run_dashboard(): app.run(host=DASHBOARD_HOST,port=DASHBOARD_PORT)
