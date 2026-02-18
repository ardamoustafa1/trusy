# KVKK Veri Anonimleştirme Sistemi Konfigürasyonu - Genişletilmiş

from enum import Enum
from typing import Dict

class EntityType(Enum):
    """Tespit edilebilecek kişisel veri tipleri - TAM LİSTE"""
    # İsim bilgileri
    NAME = "NAME"
    SURNAME = "SURNAME"
    FULL_NAME = "FULL_NAME"
    PARENT_NAME = "PARENT_NAME"  # Anne/Baba adı
    
    # Kimlik bilgileri
    TC_ID = "TC_ID"
    PASSPORT = "PASSPORT"
    
    # Tarih bilgileri
    BIRTH_DATE = "BIRTH_DATE"
    BIRTH_YEAR = "BIRTH_YEAR"
    
    # Cinsiyet
    GENDER = "GENDER"
    
    # İletişim bilgileri
    PHONE = "PHONE"
    MOBILE_PHONE = "MOBILE_PHONE"
    LANDLINE = "LANDLINE"
    EMAIL = "EMAIL"
    
    # Adres bilgileri
    ADDRESS = "ADDRESS"
    HOME_ADDRESS = "HOME_ADDRESS"
    WORK_ADDRESS = "WORK_ADDRESS"
    CITY_DISTRICT = "CITY_DISTRICT"  # İl/İlçe
    
    # Finansal bilgiler
    BANK_INFO = "BANK_INFO"
    BANK_NAME = "BANK_NAME"
    CARD_INFO = "CARD_INFO"
    
    # Müşteri bilgileri
    CUSTOMER_ID = "CUSTOMER_ID"
    SUBSCRIPTION_ID = "SUBSCRIPTION_ID"  # Abonelik numarası
    CONTRACT_ID = "CONTRACT_ID"  # Sözleşme numarası
    CALL_RECORD_ID = "CALL_RECORD_ID"  # Çağrı kayıt numarası
    
    # Diğer
    IP_ADDRESS = "IP_ADDRESS"
    PLATE = "PLATE"

# Placeholder formatları - TAM LİSTE
PLACEHOLDERS: Dict[EntityType, str] = {
    # İsim
    EntityType.NAME: "[AD]",
    EntityType.SURNAME: "[SOYAD]",
    EntityType.FULL_NAME: "[AD_SOYAD]",
    EntityType.PARENT_NAME: "[EBEVEYN_ADI]",
    
    # Kimlik
    EntityType.TC_ID: "[TC_KIMLIK]",
    EntityType.PASSPORT: "[PASAPORT]",
    
    # Tarih
    EntityType.BIRTH_DATE: "[DOGUM_TARIHI]",
    EntityType.BIRTH_YEAR: "[DOGUM_YILI]",
    
    # Cinsiyet
    EntityType.GENDER: "[CINSIYET]",
    
    # İletişim
    EntityType.PHONE: "[TELEFON]",
    EntityType.MOBILE_PHONE: "[CEP_TELEFONU]",
    EntityType.LANDLINE: "[SABIT_HAT]",
    EntityType.EMAIL: "[EPOSTA]",
    
    # Adres
    EntityType.ADDRESS: "[ADRES]",
    EntityType.HOME_ADDRESS: "[EV_ADRESI]",
    EntityType.WORK_ADDRESS: "[IS_ADRESI]",
    EntityType.CITY_DISTRICT: "[IL_ILCE]",
    
    # Finansal
    EntityType.BANK_INFO: "[IBAN]",
    EntityType.BANK_NAME: "[BANKA_ADI]",
    EntityType.CARD_INFO: "[KART_BILGISI]",
    
    # Müşteri
    EntityType.CUSTOMER_ID: "[MUSTERI_NO]",
    EntityType.SUBSCRIPTION_ID: "[ABONELIK_NO]",
    EntityType.CONTRACT_ID: "[SOZLESME_NO]",
    EntityType.CALL_RECORD_ID: "[CAGRI_KAYIT_NO]",
    
    # Diğer
    EntityType.IP_ADDRESS: "[IP_ADRESI]",
    EntityType.PLATE: "[PLAKA]",
}

# Türkiye il kodları (plaka için)
TURKEY_CITY_CODES = [
    "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38", "39", "40",
    "41", "42", "43", "44", "45", "46", "47", "48", "49", "50",
    "51", "52", "53", "54", "55", "56", "57", "58", "59", "60",
    "61", "62", "63", "64", "65", "66", "67", "68", "69", "70",
    "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81"
]

# Türk GSM operatör kodları
GSM_PREFIXES = [
    "530", "531", "532", "533", "534", "535", "536", "537", "538", "539",
    "540", "541", "542", "543", "544", "545", "546", "547", "548", "549",
    "550", "551", "552", "553", "554", "555", "556", "557", "558", "559",
    "560", "561",
    "500", "501", "502", "503", "504", "505", "506", "507", "508", "509",
]

# Sabit hat alan kodları
LANDLINE_PREFIXES = [
    "212", "216",  # İstanbul
    "312",  # Ankara
    "232",  # İzmir
    "224",  # Bursa
    "322",  # Adana
    "242",  # Antalya
    "352",  # Kayseri
    "362",  # Samsun
    "442",  # Erzurum
    "462",  # Trabzon
    "222",  # Eskişehir
    "262",  # Kocaeli
    "324",  # Mersin
    "342",  # Gaziantep
    "252",  # Muğla
    "332",  # Konya
    "272",  # Afyon
    "282",  # Tekirdağ
    "412",  # Diyarbakır
]

# Türk bankaları
TURKISH_BANKS = [
    "ziraat", "ziraat bankası", "t.c. ziraat bankası",
    "halkbank", "halk bankası", "türkiye halk bankası",
    "vakıfbank", "vakıf bankası", "türkiye vakıflar bankası",
    "iş bankası", "işbank", "isbank", "türkiye iş bankası",
    "garanti", "garanti bbva", "garanti bankası",
    "akbank",
    "yapı kredi", "yapıkredi", "ykb",
    "qnb finansbank", "finansbank",
    "denizbank",
    "teb", "türk ekonomi bankası",
    "ing", "ing bank", "ing türkiye",
    "hsbc",
    "şekerbank",
    "anadolubank",
    "fibabanka",
    "alternatifbank", "alternatif bank",
    "odeabank",
    "kuveyt türk", "kuveyttürk",
    "albaraka", "albaraka türk",
    "türkiye finans",
    "ziraat katılım",
    "vakıf katılım",
    "emlak katılım",
    "ptt", "ptt bank",
    "enpara", "enpara.com",
    "papara",
    "ininal",
]

# Türk bankaları IBAN başlangıç kodları
TURKISH_BANK_CODES = [
    "0001", "0004", "0010", "0012", "0015", "0032", "0046", "0059",
    "0062", "0064", "0067", "0091", "0096", "0099", "0103", "0108",
    "0109", "0111", "0115", "0122", "0123", "0124", "0125", "0129",
    "0132", "0134", "0135", "0137", "0142", "0143", "0146", "0203",
    "0205", "0206", "0208", "0209", "0210",
]

# Ay isimleri (Türkçe)
TURKISH_MONTHS = {
    "ocak": "01", "şubat": "02", "mart": "03", "nisan": "04",
    "mayıs": "05", "haziran": "06", "temmuz": "07", "ağustos": "08",
    "eylül": "09", "ekim": "10", "kasım": "11", "aralık": "12"
}

# Adres anahtar kelimeleri
ADDRESS_KEYWORDS = [
    "mahalle", "mahallesi", "mah.", "mah",
    "cadde", "caddesi", "cad.", "cad",
    "sokak", "sokağı", "sok.", "sok",
    "bulvar", "bulvarı", "blv.", "blv",
    "apartman", "apartmanı", "apt.", "apt",
    "daire", "no:", "no.", "numara",
    "kat:", "kat", "blok", "site",
    "köy", "köyü", "belde", "ilçe", "il"
]

# Müşteri ID pattern anahtar kelimeleri
CUSTOMER_ID_KEYWORDS = [
    "müşteri no", "müşteri numarası", "müşteri numaram",
    "abone no", "abone numarası", "abone numaram",
    "abonelik no", "abonelik numarası",
    "sözleşme no", "sözleşme numarası",
    "hesap no", "hesap numarası",
    "referans no", "referans numarası",
    "sipariş no", "sipariş numarası",
    "takip no", "takip numarası",
    "kayıt no", "kayıt numarası",
    "çağrı kayıt no", "çağrı kayıt numarası",
    "hizmet no", "hizmet numarası",
]

# Cinsiyet kelimeleri
GENDER_KEYWORDS = [
    "erkek", "kadın", "bay", "bayan", "kız", "oğlan",
    "male", "female", "man", "woman",
    "e", "k",  # kısaltmalar (context ile)
]
