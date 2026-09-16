import json, re
from config import OPENAI_API_KEY, OPENAI_MODEL
from sources import MOROCCAN_PLAYERS, TRANSFER_TERMS

STATUSES = ['رسمي','مؤكد','اتفاق مبدئي','مفاوضات','اهتمام','عرض','إشاعة','منفي','غير واضح']

def _player(text):
    low = text.lower()
    for name in MOROCCAN_PLAYERS:
        if name.lower() in low:
            return name
    return ''

def _fallback(text, trust):
    p = _player(text)
    transfer = any(x.lower() in text.lower() for x in TRANSFER_TERMS) and bool(p)
    if transfer:
        return 'انتقالات اللاعبين المغاربة', ('رسمي' if trust == 'A' and re.search(r'official|announced|signed|وقع|أعلن|officialise', text, re.I) else 'غير واضح'), text[:360], p
    return 'أخبار المغرب', ('مؤكد' if trust == 'A' else 'غير واضح'), text[:360], p

def classify(text, source, trust):
    fallback = _fallback(text, trust)
    if not OPENAI_API_KEY:
        return fallback
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = """أنت محرر أخبار محترف باللغة العربية.
أعد النتيجة بصيغة JSON فقط.

Fields: category, status, summary, player.

مهم جدًا:
- اكتب category و status و summary باللغة العربية.
- إذا كان الخبر الأصلي بالفرنسية أو الإنجليزية، ترجم المعلومات المهمة إلى العربية ثم لخّصها.
- summary يجب أن يكون ملخصًا إخباريًا عربيًا واضحًا ومختصرًا.
- لا تكتب أي كلمات فرنسية أو إنجليزية داخل summary إلا إذا كان اسم شخص أو نادٍ أو بطولة.
- لا تغيّر درجة اليقين الموجودة في المصدر.
- اذكر  المفاوضات باعتبارها تميهدا لما قد يكون اتفاقًا أو انتقالًا رسميًا.
- player يجب أن يكون اسم اللاعب كما يظهر في المصدر.

Categories: سياسة، اقتصاد، مجتمع، أمن، ثقافة، رياضة، انتقالات اللاعبين، أخرى.
Statuses: رسمي، مؤكد، اتفاق مبدئي، مفاوضات، اهتمام، عرض، إعارة، تجديد، إشاعة، منفي، غير واضح."""
        r = client.responses.create(model=OPENAI_MODEL, input=[
            {'role':'system','content':prompt},
            {'role':'user','content':text[:7000]}
        ])
        data = json.loads(r.output_text)
        category = data.get('category') or fallback[0]
        status = data.get('status') if data.get('status') in STATUSES else fallback[1]
        summary = data.get('summary') or fallback[2]
        player = data.get('player') or fallback[3]
        return category, status, summary, player
    except Exception:
        return fallback
