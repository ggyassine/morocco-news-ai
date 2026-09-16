# Arabic Moroccan news sources only.
#
# Trust:
# A = Official / primary source
# B = Established Moroccan news media
# C = Sports / specialist media

SOURCES = [
    # =====================
    # Official Moroccan sources
    # =====================

    (
        'MAP عربي',
        'https://news.google.com/rss/search?q=site%3Amapnews.ma&hl=ar&gl=MA&ceid=MA%3Ama',
        'A'
    ),

    (
        'SNRTnews عربي',
        'https://news.google.com/rss/search?q=site%3Asnrtnews.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'A'
    ),

    # =====================
    # Major Moroccan Arabic media
    # =====================

    (
        'هسبريس',
        'https://news.google.com/rss/search?q=site%3Ahespress.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'Le360 عربي',
        'https://news.google.com/rss/search?q=site%3Aar.le360.ma&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'العمق المغربي',
        'https://news.google.com/rss/search?q=site%3Aal3omk.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'اليوم24',
        'https://news.google.com/rss/search?q=site%3Aalyaoum24.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'أخبارنا المغربية',
        'https://news.google.com/rss/search?q=site%3Aakhbarona.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'هبة بريس',
        'https://news.google.com/rss/search?q=site%3Ahibapress.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'برلمان',
        'https://news.google.com/rss/search?q=site%3Abarlamane.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'كود',
        'https://news.google.com/rss/search?q=site%3Agoud.ma&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'كفاش',
        'https://news.google.com/rss/search?q=site%3Akifache.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    (
        'فبراير',
        'https://news.google.com/rss/search?q=site%3Afebrayer.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'B'
    ),

    # =====================
    # Moroccan sports media
    # =====================

    (
        'البطولة',
        'https://news.google.com/rss/search?q=site%3Aelbotola.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'C'
    ),

    (
        'المنتخب',
        'https://news.google.com/rss/search?q=site%3Aalmountakhab.com&hl=ar&gl=MA&ceid=MA%3Ama',
        'C'
    ),
]


# ============================================================
# Morocco relevance terms
# ============================================================

MOROCCO_TERMS = [
    'المغرب',
    'مغربي',
    'المغربية',
    'المملكة المغربية',

    'الرباط',
    'الدار البيضاء',
    'مراكش',
    'طنجة',
    'فاس',
    'وجدة',
    'تطوان',
    'العيون',
    'القنيطرة',
    'سلا',
    'مكناس',
    'الجديدة',
    'الناظور',
    'الحسيمة',
    'أكادير',

    'الصحراء',
    'الصحراء المغربية',

    'الحكومة المغربية',
    'المنتخب الوطني',
    'المنتخب المغربي',
    'الجامعة الملكية المغربية لكرة القدم',
]


# ============================================================
# Transfer terms
# ============================================================

TRANSFER_TERMS = [
    'انتقال',
    'انتقالات',
    'صفقة',
    'صفقات',
    'إعارة',
    'إعارات',
    'تجديد',
    'عقد',
    'عقود',
    'رحيل',
    'مغادرة',

    'اهتمام',
    'مفاوضات',
    'عرض',
    'عروض',
    'اتفاق',
    'اتفاق مبدئي',

    'نادي',
    'يوقع',
    'وقع',
    'ينضم',
    'انضم',
    'ينتقل',
    'انتقل',
    'يقترب',
    'اقترب',
    'يرغب',
    'رغبة',
    'يريد',

    'فحص طبي',
    'وكيل أعمال',
    'وكيل اللاعب',
    'شرط العقد',
    'كسر العقد',

    'لاعب مغربي',
    'دولي مغربي',
    'اللاعب المغربي',
]


# ============================================================
# Moroccan players
# ============================================================

MOROCCAN_PLAYERS = [
    # ---------------------
    # Achraf Hakimi
    # ---------------------

    'أشرف حكيمي',
    'Achraf Hakimi',
    'Achraf Hakimi',

    # ---------------------
    # Brahim Diaz
    # ---------------------

    'إبراهيم دياز',
    'ابراهيم دياز',
    'Brahim Diaz',
    'Brahim Díaz',

    # ---------------------
    # Noussair Mazraoui
    # ---------------------

    'نصير مزراوي',
    'Noussair Mazraoui',

    # ---------------------
    # Yassine Bounou
    # ---------------------

    'ياسين بونو',
    'Yassine Bounou',
    'Bono',

    # ---------------------
    # Hakim Ziyech
    # ---------------------

    'حكيم زياش',
    'Hakim Ziyech',

    # ---------------------
    # Sofyan Amrabat
    # ---------------------

    'سفيان أمرابط',
    'Sofyan Amrabat',

    # ---------------------
    # Sofiane Boufal
    # ---------------------

    'سفيان بوفال',
    'Sofiane Boufal',

    # ---------------------
    # Azzedine Ounahi
    # ---------------------

    'عز الدين أوناحي',
    'عزالدين أوناحي',
    'Azzedine Ounahi',

    # ---------------------
    # Bilal El Khannouss
    # ---------------------

    'بلال الخنوس',
    'Bilal El Khannouss',

    # ---------------------
    # Eliesse Ben Seghir
    # ---------------------

    'إلياس بن صغير',
    'إلياس بنصغير',
    'Eliesse Ben Seghir',

    # ---------------------
    # Abde Ezzalzouli
    # ---------------------

    'عبد الصمد الزلزولي',
    'عبدالصمد الزلزولي',
    'Abde Ezzalzouli',
    'Abdessamad Ezzalzouli',

    # ---------------------
    # Youssef En-Nesyri
    # ---------------------

    'يوسف النصيري',
    'Youssef En-Nesyri',
    'Youssef En Nesyri',

    # ---------------------
    # Ayoub El Kaabi
    # ---------------------

    'أيوب الكعبي',
    'Ayoub El Kaabi',

    # ---------------------
    # Amine Harit
    # ---------------------

    'أمين حارث',
    'Amine Harit',

    # ---------------------
    # Ismael Saibari
    # ---------------------

    'إسماعيل الصيباري',
    'إسماعيل صيباري',
    'Ismael Saibari',

    # ---------------------
    # Bilal El Khannouss
    # ---------------------

    'بلال الخنوس',
    'Bilal El Khannouss',

    # ---------------------
    # Oussama Targhalline
    # ---------------------

    'أسامة ترغالين',
    'Oussama Targhalline',

    # ---------------------
    # Reda Belahyane
    # ---------------------

    'رضا بلحيان',
    'Reda Belahyane',

    # ---------------------
    # Amir Richardson
    # ---------------------

    'أمير ريتشاردسون',
    'Amir Richardson',

    # ---------------------
    # Zakaria Aboukhlal
    # ---------------------

    'زكرياء أبو خلال',
    'Zakaria Aboukhlal',

    # ---------------------
    # Ilias Akhomach
    # ---------------------

    'إلياس أخوماش',
    'Ilias Akhomach',

    # ---------------------
    # Ismail Kandouss
    # ---------------------

    'إسماعيل قندوس',
    'Ismail Kandouss',

    # ---------------------
    # Chadi Riad
    # ---------------------

    'شادي رياض',
    'Chadi Riad',

    # ---------------------
    # Nayef Aguerd
    # ---------------------

    'نايف أكرد',
    'Nayef Aguerd',

    # ---------------------
    # Jawad El Yamiq
    # ---------------------

    'جواد الياميق',
    'Jawad El Yamiq',

    # ---------------------
    # Achraf Dari
    # ---------------------

    'أشرف داري',
    'Achraf Dari',

    # ---------------------
    # Abdelkabir Abqar
    # ---------------------

    'عبد الكبير عبقار',
    'Abdelkabir Abqar',

    # ---------------------
    # Munir El Kajoui
    # ---------------------

    'منير المحمدي',
    'Munir El Kajoui',
    'Munir Mohamedi',

    # ---------------------
    # Selim Amallah
    # ---------------------

    'سليم أملاح',
    'Selim Amallah',

    # ---------------------
    # Oussama Idrissi
    # ---------------------

    'أسامة الإدريسي',
    'Oussama Idrissi',

    # ---------------------
    # Zakaria El Ouahdi
    # ---------------------

    'زكرياء الواحدي',
    'Zakaria El Ouahdi',

    # ---------------------
    # Bilal El Khannouss
    # ---------------------

    'بلال الخنوس',
    'Bilal El Khannouss',
]
