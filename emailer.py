import html, requests
from config import RESEND_API_KEY, FROM_EMAIL, TO_EMAIL
from db import mark_sent

TRUST_LABEL = {'A':'A | رسمي/أولي','B':'B | مؤسسة إعلامية','C':'C | متخصص','D':'D | غير مؤكد'}

def send(items):
    if not items or not (RESEND_API_KEY and FROM_EMAIL): return False
    rows=[]
    for x in items:
        rows.append(f'''<article style="margin:0 0 24px;padding:16px;border:1px solid #ddd;border-radius:8px">
        <h3>{html.escape(x['title'])}</h3>
        <p>{html.escape(x.get('summary') or '')}</p>
        <p><b>التصنيف:</b> {html.escape(x.get('category') or '')}<br>
        <b>الحالة:</b> {html.escape(x.get('status') or '')}<br>
        <b>المصدر:</b> {html.escape(x.get('source') or '')} ({TRUST_LABEL.get(x.get('trust'),'غير مصنف')})
        {('<br><b>اللاعب:</b> '+html.escape(x['player'])) if x.get('player') else ''}</p>
        <p><a href="{html.escape(x['url'])}">المصدر الأصلي</a></p></article>''')
    subject=f"Morocco News AI | {len(items)} خبر جديد"
    payload={'from':FROM_EMAIL,'to':[TO_EMAIL],'subject':subject,
             'html':'<html dir="rtl"><body style="font-family:Arial,sans-serif;max-width:760px;margin:auto"><h1>Morocco News AI</h1>'+''.join(rows)+'</body></html>'}
    r=requests.post('https://api.resend.com/emails',headers={'Authorization':f'Bearer {RESEND_API_KEY}','Content-Type':'application/json'},json=payload,timeout=20)
    if r.ok:
        mark_sent([x['id'] for x in items if x.get('id')])
    else:
        print('Resend error:', r.status_code, r.text[:500])
    return r.ok
