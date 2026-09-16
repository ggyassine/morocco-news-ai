import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5.6-luna')
RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', '')
TO_EMAIL = os.getenv('TO_EMAIL', 'yassinehamini9@gmail.com')
INTERVAL_MINUTES = max(15, int(os.getenv('INTERVAL_MINUTES', '15')))
MAX_ITEMS_PER_SOURCE = max(10, int(os.getenv('MAX_ITEMS_PER_SOURCE', '50')))
SEND_EMPTY_DIGEST = os.getenv('SEND_EMPTY_DIGEST', 'false').lower() == 'true'
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', '0.0.0.0')
DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '8080'))
