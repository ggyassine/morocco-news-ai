import json
import re

from config import OPENAI_API_KEY, OPENAI_MODEL
from sources import MOROCCAN_PLAYERS, TRANSFER_TERMS


STATUSES = [
    'رسمي',
    'مؤكد',
    'اتفاق مبدئي',
    'مفاوضات',
    'اهتمام',
    'عرض',
    'إعارة',
    'تجديد',
    'إشاعة',
    'منفي',
    'غير واضح',
]


def _player(text):
    low = text.lower()

    for name in MOROCCAN_PLAYERS:
        if name.lower() in low:
            return name

    return ''


def _fallback(text, trust):
    p = _player(text)

    transfer = (
        any(x.lower() in text.lower() for x in TRANSFER_TERMS)
        and bool(p)
    )

    if transfer:
        official_words = re.search(
            r'official|announced|signed|officially|'
            r'أعلن|اعلن|وقع|يوقع|رسمي|رسميا|رسمياً',
            text.lower()
        )

        status = 'رسمي' if trust == 'A' and official_words else 'غير واضح'

        return (
            'انتقالات اللاعبين',
            status,
            text[:360],
            p
        )

    return (
        'أخبار المغرب',
        'مؤكد' if trust == 'A' else 'غير واضح',
        text[:360],
        p
    )


def classify(text, source, trust):
    fallback = _fallback(text, trust)

    # إذا لم يكن مفتاح OpenAI موجودا
    # نستعمل التصنيف الاحتياطي بدون تعطيل النظام
    if not OPENAI_API_KEY:
        return fallback

    try:
        from openai import OpenAI

        # مهلة قصوى 30 ثانية لطلب OpenAI
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0
        )

        prompt = """
أنت محرر أخبار محترف باللغة العربية.

أعد النتيجة فقط بصيغة JSON صحيحة.

Fields:
category, status, summary, player

القواعد:

1. اكتب category و status و summary باللغة العربية.

2. إذا كان الخبر الأصلي بالفرنسية أو الإنجليزية،
ترجم المعلومات المهمة إلى العربية ثم لخصها.

3. يجب أن يكون summary ملخصا إخباريا واضحا ومختصرا.

4. لا تكتب كلمات فرنسية أو إنجليزية داخل summary،
إلا أسماء الأشخاص أو الأندية أو البطولات عندما يكون
من الضروري إبقاؤها كما هي.

5. لا تغير درجة اليقين الموجودة في المصدر.

6. إذا كان المصدر يتحدث عن مفاوضات،
اكتب "مفاوضات"، ولا تعتبرها انتقالا رسميا.

7. إذا كان المصدر يتحدث عن اهتمام،
اكتب "اهتمام".

8. إذا كان هناك عرض فقط،
اكتب "عرض".

9. إذا كان هناك اتفاق مبدئي،
اكتب "اتفاق مبدئي".

10. إذا كان الانتقال أو التوقيع معلنا رسميا،
اكتب "رسمي".

11. إذا كان الخبر يتعلق بإعارة مؤكدة،
اكتب "إعارة".

12. إذا كان الخبر يتعلق بتجديد عقد مؤكد،
اكتب "تجديد".

13. player يجب أن يكون اسم اللاعب المغربي المذكور في المصدر.

Categories:
سياسة، اقتصاد، مجتمع، أمن، ثقافة، رياضة،
انتقالات اللاعبين، أخرى

Statuses:
رسمي، مؤكد، اتفاق مبدئي، مفاوضات، اهتمام،
عرض، إعارة، تجديد، إشاعة، منفي، غير واضح
"""

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': text[:7000]
                }
            ]
        )

        data = json.loads(response.output_text)

        category = data.get('category') or fallback[0]

        status = data.get('status')

        if status not in STATUSES:
            status = fallback[1]

        summary = data.get('summary') or fallback[2]

        player = data.get('player') or fallback[3]

        return (
            category,
            status,
            summary,
            player
        )

    except Exception as ex:
        print(f"AI classification error: {ex}")
        return fallback
