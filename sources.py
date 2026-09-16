# Sources are deliberately separated by trust tier.
# RSS URLs should be verified in the deployment environment. If a source changes its feed URL,
# update it here without changing the rest of the application.
SOURCES = [
    # Official / primary
    ('MAP', 'https://www.mapnews.ma/en/rss', 'A'),
    ('SNRTnews', 'https://snrtnews.com/rss.xml', 'A'),
    # Moroccan press
    ('Hespress', 'https://www.hespress.com/feed', 'B'),
    ('Le360', 'https://fr.le360.ma/rss', 'B'),
    ('Médias24', 'https://medias24.com/feed/', 'B'),
    ('TelQuel', 'https://telquel.ma/feed/', 'B'),
    ('Aujourd’hui Le Maroc', 'https://aujourdhui.ma/feed', 'B'),
    ('L’Economiste', 'https://www.leconomiste.com/rss.xml', 'B'),
    # Sports / transfer reporting
    ('Elbotola', 'https://m.elbotola.com/fr/rss/', 'B'),
    ('Foot Mercato', 'https://www.footmercato.net/rss', 'B'),
    ('ESPN Soccer', 'https://www.espn.com/espn/rss/soccer/news', 'B'),
    ('Al Jazeera Sports', 'https://www.aljazeera.com/xml/rss/all.xml', 'B'),
    ('Reuters Sports', 'https://feeds.reuters.com/reuters/sportsNews', 'A'),
]

# Search terms used only as a relevance filter. The system does not treat a keyword match as proof.
MOROCCO_TERMS = [
    'morocco','moroccan','maroc','marocain','marocaine','royaume du maroc',
    'المغرب','المغربي','المغربية','المغاربة','المملكة المغربية','الرباط','الدار البيضاء',
    'morocco government','morocco ministry'
]

TRANSFER_TERMS = [
    'transfer','transfers','transfert','transferts','mercato','signed','signs','joins',
    'loan','loaned','contract','renewal','renew','deal','agreement','bid','offer',
    'interest','negotiations','medical','free agent','release','departure',
    'انتقال','انتقالات','ميركاتو','صفقة','تعاقد','إعارة','تجديد','عرض','مفاوضات','اهتمام',
    'اتفاق','فحص طبي','فسخ العقد','وكيل','لاعب مغربي','دولي مغربي'
]

# Names are aliases, not evidence of nationality. Extend this list as players emerge.
MOROCCAN_PLAYERS = [
    'Achraf Hakimi','أشرف حكيمي','Brahim Diaz','براهيم دياز','Sofyan Amrabat','سفيان أمرابط',
    'Noussair Mazraoui','نصير مزراوي','Nayef Aguerd','نايف أكرد','Yassine Bounou','ياسين بونو',
    'Eliesse Ben Seghir','إلياس بن صغير','Bilal El Khannouss','بلال الخنوس','Ismael Saibari','إسماعيل الصيباري',
    'Azzedine Ounahi','عز الدين أوناحي','Sofiane Boufal','سفيان بوفال','Ayoub El Kaabi','أيوب الكعبي',
    'Youssef En-Nesyri','يوسف النصيري','Amine Harit','أمين حارث','Abde Ezzalzouli','عبد الصمد الزلزولي',
    'Zakaria Aboukhlal','زكرياء أبو خلال','Chadi Riad','شادي رياض','Abdelhamid Ait Boudlal','عبد الحميد آيت بودلال',
    'Oussama Targhalline','أسامة ترغالين','Ismael Kandouss','إسماعيل قندوس','Ilias Chair','إلياس شاعر',
    'Amine Adli','أمين عدلي','Oussama Idrissi','أسامة الإدريسي','Munir El Haddadi','منير الحدادي',
    'Jawad El Yamiq','جواد الياميق','Sofyan El Krouni','سفيان الكرواني','Souffian El Karouani','سفيان الكرواني',
    'Ayoub Bouaddi','أيوب بوعدي','Issa Diop','إسّا ديوب','Taha Majni','طه مجني',
    'Anass Salah-Eddine','أنس صلاح الدين','Ismael Saibari','إسماعيل الصيباري'
]
