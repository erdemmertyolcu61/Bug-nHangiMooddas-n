"""
Sinema Düello – kategori tanımları.

Her kategori, movie_repository tablosuna farklı WHERE koşullarıyla sorgu yapar.
query_type'a göre: mood → mood_id eşleşmesi, genre → genre_ids LIKE, language → original_language,
year_range → release_date filtresi, min_rating → vote_average + vote_count.
"""

QUIZ_CATEGORIES = {
    "askfilmleri": {
        "label": "Aşk Filmleri",
        "emoji": "💕",
        "query_type": "mood",
        "mood_ids": ["askbahcesi"],
    },
    "gerilim": {
        "label": "Gerilim & Gizem",
        "emoji": "🔪",
        "query_type": "mood",
        "mood_ids": ["adrenalin", "gece"],
    },
    "kahkaha": {
        "label": "Komedi",
        "emoji": "😂",
        "query_type": "mood",
        "mood_ids": ["kahkaha"],
    },
    "derin": {
        "label": "Derin Düşündüren",
        "emoji": "🧠",
        "query_type": "mood",
        "mood_ids": ["zihin", "deep-chills"],
    },
    "nostaljik": {
        "label": "Zamansız Klasikler",
        "emoji": "📽️",
        "query_type": "year_range",
        "year_max": 1999,
    },
    "yeni": {
        "label": "Yeni Nesil",
        "emoji": "🆕",
        "query_type": "year_range",
        "year_min": 2010,
    },
    "yerli": {
        "label": "Yerli Filmler",
        "emoji": "🇹🇷",
        "query_type": "language",
        "original_language": "tr",
    },
    "bilimkurgu": {
        "label": "Bilim Kurgu",
        "emoji": "🚀",
        "query_type": "genre",
        "genre_ids": [878],
    },
    "animasyon": {
        "label": "Animasyon",
        "emoji": "🎨",
        "query_type": "genre",
        "genre_ids": [16],
    },
    "aksiyon": {
        "label": "Aksiyon & Macera",
        "emoji": "💥",
        "query_type": "genre",
        "genre_ids": [28, 12],
    },
    "korku": {
        "label": "Korku",
        "emoji": "👻",
        "query_type": "genre",
        "genre_ids": [27],
    },
    "drama": {
        "label": "Drama",
        "emoji": "🎭",
        "query_type": "genre",
        "genre_ids": [18],
    },
    "odullu": {
        "label": "Ödüllü Filmler",
        "emoji": "🏆",
        "query_type": "min_rating",
        "min_vote_average": 7.5,
        "min_vote_count": 500,
    },
    "belgesel": {
        "label": "Belgesel",
        "emoji": "📹",
        "query_type": "genre",
        "genre_ids": [99],
    },
}

MOOD_ID_LABELS = {
    "battaniye": "Battaniye Modu",
    "yolculuk": "Yolculuk Ruhu",
    "gece": "Gece Kuşu",
    "kahkaha": "Kahkaha Molası",
    "gozyasi": "Gözyaşı Gecesi",
    "adrenalin": "Adrenalin Patlaması",
    "askbahcesi": "Aşk Bahçesi",
    "zamanyolcusu": "Zaman Yolcusu",
    "sessiz": "Sessiz Yolculuk",
    "zihin": "Zihin Savaşı",
    "kalp": "Kalbimin Sesi",
    "karmakar": "Karmaşakar",
    "sipsak": "Şipşak",
    "deep-chills": "Derin Ürperti",
    "kadraj-estetigi": "Kadraj Estetiği",
    "geceyarisi-itirafi": "Geceyarısı İtirafı",
}
