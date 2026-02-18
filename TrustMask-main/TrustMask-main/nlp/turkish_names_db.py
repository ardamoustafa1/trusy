"""
Türk İsimleri Veritabanı

En yaygın kullanılan Türk isimleri ve soyisimleri.
Bu liste NLP tabanlı isim tespiti için kullanılır.
"""

# Türk erkek isimleri (yaygın 500+)
TURKISH_MALE_NAMES = {
    # A
    "ahmet", "ali", "abdullah", "abdulkadir", "adem", "adnan", "arda", "arif", "atilla", "aykut",
    "ayhan", "aziz", "bahadır", "baran", "barış", "batuhan", "berat", "berkay", "berke", "bilal",
    "burak", "bülent", "can", "caner", "celal", "cem", "cemal", "cengiz", "cihan", "coşkun",
    "çağatay", "çağlar", "deniz", "doğan", "doğukan", "dursun", "efe", "emin", "emir", "emirhan",
    "emre", "ender", "enes", "engin", "ercan", "erdem", "erdoğan", "eren", "erhan", "erkan",
    "ersin", "ertuğrul", "eyüp", "faruk", "fatih", "ferdi", "ferit", "fikret", "furkan", "galip",
    "gökhan", "göksel", "güner", "güven", "hakan", "halil", "haluk", "harun", "hasan", "haydar",
    "hayri", "hikmet", "hüseyin", "ibrahim", "ilhan", "ilker", "irfan", "ismail", "izzet", "kadir",
    "kağan", "kamil", "kemal", "kenan", "kerem", "koray", "korkut", "kudret", "kürşat", "levent",
    "mahmut", "mehmet", "melik", "melih", "mert", "mesut", "mete", "metehan", "muammer", "murat",
    "mustafa", "muzaffer", "necati", "necdet", "necip", "nihat", "nuri", "oğuz", "oğuzhan", "okay",
    "okan", "oktay", "onur", "orhan", "orkun", "osman", "ömer", "özcan", "özgür", "özhan",
    "polat", "ramazan", "rasim", "recep", "rıza", "rüştü", "sabahattin", "sabri", "salih", "sami",
    "sedat", "selçuk", "selim", "selman", "semih", "sercan", "serdar", "serhan", "serhat", "serkan",
    "sertaç", "sezer", "sinan", "şahin", "şenol", "şükrü", "taha", "talat", "taner", "tayfun",
    "tekin", "teoman", "tevfik", "tolga", "tolgahan", "tuna", "tunç", "tuncay", "turan", "turgay",
    "turgut", "türker", "uğur", "ufuk", "umut", "vedat", "veli", "volkan", "yağız", "yahya",
    "yakup", "yalçın", "yasin", "yavuz", "yıldırım", "yılmaz", "yunus", "yusuf", "zafer", "zeki",
}

# Türk kadın isimleri (yaygın 500+)
TURKISH_FEMALE_NAMES = {
    # A
    "ada", "aslı", "ayfer", "aylin", "aysel", "ayşe", "ayşegül", "ayşen", "azra", "bahar",
    "başak", "bedia", "begüm", "belgin", "beren", "berna", "betül", "beyza", "bilge", "birsen",
    "burcu", "büşra", "cahide", "canan", "ceyda", "ceylan", "çiğdem", "damla", "defne", "deniz",
    "derya", "didem", "dilek", "duygu", "ebru", "ece", "eda", "ekin", "ela", "elçin",
    "elif", "emel", "emine", "esin", "esma", "esra", "evrim", "eylem", "fadime", "fatma",
    "feride", "ferzan", "feyza", "fidan", "figen", "filiz", "fulya", "gamze", "gizem", "gökçe",
    "gonca", "görkem", "gözde", "gül", "gülay", "gülbahar", "gülcan", "gülçin", "güler", "gülfem",
    "gülhan", "gülin", "gülizar", "gülnaz", "gülsen", "gülşah", "gülşen", "gülten", "gülüzar", "hacer",
    "hadiye", "hafize", "halide", "halime", "handan", "hanife", "hasibe", "hatice", "havva", "hayal",
    "hayriye", "hediye", "hicran", "hilal", "hülya", "hümeyra", "ırmak", "ilknur", "ipek", "irmak",
    "işıl", "jale", "kadriye", "kader", "kamile", "kamuran", "kardelen", "kübra", "lale", "latife",
    "leman", "leyla", "lütfiye", "macide", "mehtap", "melek", "melekşe", "melike", "melisa", "meltem",
    "meral", "merve", "meryem", "mevlüde", "mine", "miray", "müge", "müjde", "münevver", "nalan",
    "naz", "nazlı", "necla", "nefise", "nehir", "neriman", "nermin", "neşe", "neslihan", "nesrin",
    "nevin", "nihan", "nihal", "nilay", "nilgün", "nilhan", "nilüfer", "nisa", "nisan", "nuran",
    "nuray", "nurcan", "nurdan", "nurgül", "nurhan", "nursel", "nursen", "nurten", "oya", "özden",
    "özen", "özge", "özlem", "pelin", "pembe", "peri", "perihan", "pınar", "rabia", "rahime",
    "raşide", "rengin", "reyhan", "rukiye", "saadet", "sabiha", "safiye", "sanem", "saniye", "sebiha",
    "seda", "sedef", "sefa", "seher", "selda", "selen", "selma", "sema", "semanur", "semra",
    "sena", "serap", "seren", "serpil", "sevda", "sevgi", "sevil", "sevinç", "sevtap", "seyhan",
    "sıdıka", "sibel", "simge", "sinem", "songül", "sultan", "suna", "sunay", "suzan", "şebnem",
    "şehriban", "şenay", "şengül", "şerife", "şeyda", "şeyma", "şirin", "şule", "tuba", "tuğba",
    "tuğçe", "tülay", "tülin", "türkan", "ülkü", "ümit", "ümmü", "vildan", "yağmur", "yaren",
    "yasemin", "yelda", "yeliz", "yıldız", "yonca", "zehra", "zekiye", "zeliş", "zeliha", "zeynep",
    "zübeyde", "zühal", "züleyha",
}

# Tüm isimler (tek set)
TURKISH_FIRST_NAMES = TURKISH_MALE_NAMES | TURKISH_FEMALE_NAMES

# Yaygın Türk soyisimleri
TURKISH_SURNAMES = {
    "yılmaz", "kaya", "demir", "çelik", "şahin", "yıldız", "yıldırım", "öztürk", "aydın", "özdemir",
    "arslan", "doğan", "kılıç", "aslan", "çetin", "kara", "koç", "kurt", "özkan", "şimşek",
    "polat", "korkmaz", "özmen", "özer", "güneş", "aksoy", "erdoğan", "güler", "yalçın", "kaplan",
    "türk", "tekin", "gül", "koçak", "erdem", "özçelik", "aktaş", "güzel", "duran", "karaca",
    "turan", "bozkurt", "uçar", "acar", "taş", "ateş", "keskin", "karakaş", "sarı", "sönmez",
    "akın", "köse", "bulut", "pala", "uysal", "tan", "karahan", "demirel", "başaran", "çakır",
    "yavuz", "gürbüz", "coşkun", "çiçek", "topal", "avcı", "ercan", "bilgin", "ay", "toprak",
    "ekinci", "duman", "şen", "alkan", "eren", "bayrak", "soylu", "özkaya", "sezer", "ünal",
    "akgül", "albayrak", "uyar", "karakaya", "güngör", "ceylan", "aksu", "oğuz", "turgut", "aydemir",
    "oral", "poyraz", "işık", "koca", "kabak", "bakır", "akyol", "erdal", "şeker", "şenses",
    "karataş", "çam", "canan", "baran", "dinç", "çevik", "özgür", "elmas", "akyüz", "akbulut",
    "gedik", "bayram", "başak", "ergin", "demirtaş", "çoban", "türkoğlu", "güven", "akbaş", "kahraman",
    "dağ", "oruç", "gökalp", "erol", "tuna", "temel", "aras", "tunç", "akça", "eken",
    "yeşil", "genç", "soydan", "altın", "sevim", "işler", "gündüz", "uzun", "akyıldız", "güney",
    "alemdar", "güçlü", "akdoğan", "esen", "özal", "boz", "dağlı", "zengin", "kolcu", "başer",
    "özcan", "yüksel", "karadeniz", "parlak", "karabacak", "ulusoy", "çiftçi", "kaptan", "torun", "ülker",
    "akman", "savaş", "tanrıverdi", "ertan", "yurdakul", "akpınar", "kayar", "gökçe", "akdağ", "işcan",
}

# Hitap/Unvanlar
HONORIFICS = {
    "bey", "hanım", "efendi", "beyefendi", "hanımefendi",
    "sayın", "bay", "bayan",
    "prof", "prof.", "profesör", "doç", "doç.", "doçent",
    "dr", "dr.", "doktor",
    "av", "av.", "avukat",
    "mim", "mim.", "mimar",
    "müh", "müh.", "mühendis",
    "öğr", "öğr.", "öğretmen",
    "arş", "arş.", "araştırmacı",
    "uzm", "uzm.", "uzman",
}

# İsim benzeri kelimeler (false positive önlemek için) - GENİŞLETİLMİŞ
NAME_LIKE_COMMON_WORDS = {
    # Zamirler
    "benim", "senin", "onun", "bizim", "sizin", "onların",
    "ben", "sen", "biz", "siz",
    # Cevaplar
    "var", "yok", "evet", "hayır", "hayir", "tamam", "peki", "olur", "olmaz",
    # Selamlaşma ve Nezaket - HEM TÜRKÇE HEM ASCII - GENİŞLETİLMİŞ
    "lütfen", "lutfen", "teşekkür", "tesekkur", "teşekkürler", "tesekkurler",
    "merhaba", "günaydın", "gunaydin",
    "iyi", "İyi", "ıyi", "günler", "gunler", "Günler", "akşamlar", "aksamlar", "geceler",
    "hoşgeldiniz", "hosgeldiniz", "hoşçakalın", "hoscakalin",
    "hoş", "hos", "Hoş", "geldiniz", "Geldiniz",  # AYRI KELİMELER
    "selam", "selamlar", "hoşgeldin", "hosgeldin", "hoşbulduk", "hosbulduk", "görüşürüz", "gorusuruz",
    # Müşteri Hizmetleri Kelimeleri - ÖNEMLİ - GENİŞLETİLMİŞ
    "müşteri", "musteri", "Müşteri", "temsilci", "temsilcisi", "Temsilci",
    "müşterimiz", "musterimiz",
    "hizmet", "hizmetler", "hizmetleri", "hizmetlerine",  # EKLENDİ
    "destek", "çağrı", "cagri", "merkezi", "merkezine",
    "yardım", "yardim", "yardımcı", "yardimci", "olabilir", "olabiliriz",
    "nasıl", "nasil", "olabilirim", "ederiz", "rica", "ederim",
    # NovaNet gibi şirket isimleri
    "novanet", "NovaNet", "vodafone", "Vodafone", "turkcell", "Turkcell",
    # Sıfatlar
    "iyi", "kötü", "güzel", "çirkin", "büyük", "küçük",
    "yeni", "eski", "doğru", "yanlış", "haklı", "haksız",
    # Soru Kelimeleri
    "ne", "nasıl", "neden", "niçin", "niye", "kim", "kimin",
    "hangi", "kaç", "nere", "nerede", "nereden", "nereye",
    # İşaret Zamirleri
    "bu", "şu", "o", "bunlar", "şunlar", "onlar",
    "burada", "şurada", "orada", "burası", "şurası", "orası",
    # Sayılar
    "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
    "yüz", "bin", "milyon", "milyar", "birinci", "ikinci", "üçüncü",
    # Zaman Kelimeleri
    "gün", "ay", "yıl", "saat", "dakika", "saniye",
    "hafta", "pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar",
    "bugün", "yarın", "dün", "şimdi", "sonra", "önce",
    # Aylar
    "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
    "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık",
    # Fiiller ve Yardımcı Fiiller
    "için", "ile", "gibi", "kadar", "göre", "karşı",
    "etmek", "yapmak", "almak", "vermek", "gelmek", "gitmek",
    # Vodafone / Operatör Kelimeleri
    "vodafone", "turkcell", "telekom", "hat", "fatura", "paket",
    "tarife", "kontör", "internet", "dakika", "sms",
    # Banka Kelimeleri
    "banka", "hesap", "bakiye", "ödeme", "transfer", "havale",
    # Diğer Yaygın Kelimeler
    "sistem", "bilgi", "işlem", "talep", "sorun", "problem",
    "çözüm", "kontrol", "kayıt", "numara", "adres", "mail",
}

