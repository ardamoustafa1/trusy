"""
Adres Bilgileri Detector - Genişletilmiş

Türkiye'deki adres formatlarını tespit eder:
- Mahalle, cadde, sokak, bulvar
- Apartman, daire, kat bilgileri
- İl, ilçe, posta kodu
- Ev adresi / İş adresi ayrımı
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, ADDRESS_KEYWORDS


# Türkiye'nin 81 ili
TURKEY_CITIES = [
    "adana", "adıyaman", "afyon", "afyonkarahisar", "ağrı", "amasya", "ankara", "antalya",
    "artvin", "aydın", "balıkesir", "bilecik", "bingöl", "bitlis", "bolu", "burdur",
    "bursa", "çanakkale", "çankırı", "çorum", "denizli", "diyarbakır", "edirne", "elazığ",
    "erzincan", "erzurum", "eskişehir", "gaziantep", "giresun", "gümüşhane", "hakkari",
    "hatay", "ısparta", "mersin", "icel", "istanbul", "izmir", "kars", "kastamonu",
    "kayseri", "kırklareli", "kırşehir", "kocaeli", "konya", "kütahya", "malatya",
    "manisa", "kahramanmaraş", "mardin", "muğla", "muş", "nevşehir", "niğde", "ordu",
    "rize", "sakarya", "samsun", "siirt", "sinop", "sivas", "tekirdağ", "tokat",
    "trabzon", "tunceli", "şanlıurfa", "uşak", "van", "yozgat", "zonguldak", "aksaray",
    "bayburt", "karaman", "kırıkkale", "batman", "şırnak", "bartın", "ardahan", "iğdır",
    "yalova", "karabük", "kilis", "osmaniye", "düzce"
]

# Türkiye ilçeleri (büyük şehirler)
ISTANBUL_DISTRICTS = [
    "adalar", "arnavutköy", "ataşehir", "avcılar", "bağcılar", "bahçelievler",
    "bakırköy", "başakşehir", "bayrampaşa", "beşiktaş", "beykoz", "beylikdüzü",
    "beyoğlu", "büyükçekmece", "çatalca", "çekmeköy", "esenler", "esenyurt",
    "eyüpsultan", "fatih", "gaziosmanpaşa", "güngören", "kadıköy", "kağıthane",
    "kartal", "küçükçekmece", "maltepe", "pendik", "sancaktepe", "sarıyer",
    "silivri", "sultanbeyli", "sultangazi", "şile", "şişli", "tuzla", "ümraniye",
    "üsküdar", "zeytinburnu"
]

ANKARA_DISTRICTS = [
    "altındağ", "aydınlıkevler", "bala", "beypazarı", "çamlıdere", "çankaya",
    "çubuk", "elmadağ", "etimesgut", "evren", "gölbaşı", "güdül", "haymana",
    "kalecik", "kızılcahamam", "keçiören", "mamak", "nallıhan", "polatlı",
    "pursaklar", "sincan", "şereflikoçhisar", "yenimahalle"
]

IZMIR_DISTRICTS = [
    "aliağa", "bayındır", "bayraklı", "bergama", "bornova", "buca", "çeşme",
    "çiğli", "dikili", "foça", "gaziemir", "güzelbahçe", "karaburun", "karşıyaka",
    "kemalpaşa", "kınık", "kiraz", "konak", "menderes", "menemen", "narlıdere",
    "ödemiş", "seferihisar", "selçuk", "tire", "torbalı", "urla"
]

BURSA_DISTRICTS = [
    "büyükorhan", "gemlik", "gürsu", "harmancık", "ınegöl", "iznik", "karacabey",
    "keles", "kestel", "mudanya", "mustafakemalpaşa", "nilüfer", "orhaneli",
    "orhangazi", "osmangazi", "yenişehir", "yenikent"
]

ANTALYA_DISTRICTS = [
    "akseki", "aksu", "alanya", "demre", "döşemealtı", "elmali", "finike",
    "gazipaşa", "gündoğmuş", "ıbradı", "kaş", "kemer", "kepez", "konyaaltı",
    "kumluca", "manavgat", "muratpaşa", "serik"
]

ADANA_DISTRICTS = [
    "aladağ", "ceyhan", "çukurova", "feke", "imamoğlu", "karaisalı", "karataş",
    "kozan", "pozantı", "saimbeyli", "sarçam", "seyhan", "tufanbeyli", "yumurtalık",
    "yüreğir"
]

KOCAELI_DISTRICTS = [
    "başiskele", "çayırova", "darıca", "derince", "dilovası", "gebze", "gölcük",
    "izmit", "kandıra", "karamürsel", "kartepe", "köseköy", "körfez"
]

GAZIANTEP_DISTRICTS = [
    "araban", "ıslahiye", "karkamış", "nizip", "nurdağı", "oğuzeli", "şahinbey",
    "şehitkamil", "yavuzeli"
]

KONYA_DISTRICTS = [
    "akören", "akşehir", "altınekin", "beyşehir", "bozkır", "cihanbeyli",
    "çeltik", "çumra", "derbent", "derebucak", "doğanhisar", "emirgazi",
    "ereğli", "güneysinir", "hadim", "halkapınar", "hüyük", "ilgın", "kadınhanı",
    "karapınar", "kulu", "meram", "sarayönü", "selçuklu", "seydişehir", "taşkent",
    "tuzlukçu", "yalıhüyük", "yunak"
]

# Tüm ilçeleri birleştir
ALL_DISTRICTS = ISTANBUL_DISTRICTS + ANKARA_DISTRICTS + IZMIR_DISTRICTS + \
                BURSA_DISTRICTS + ANTALYA_DISTRICTS + ADANA_DISTRICTS + \
                KOCAELI_DISTRICTS + GAZIANTEP_DISTRICTS + KONYA_DISTRICTS


class AddressDetector(BaseDetector):
    """Adres bilgileri tespit edicisi - Genişletilmiş"""
    
    def __init__(self):
        super().__init__()
        self.cities = set(TURKEY_CITIES)
        self.districts = set(ALL_DISTRICTS)
        self.keywords = ADDRESS_KEYWORDS
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        text_lower = text.lower()
        
        # Pattern 1: Ev adresi context
        home_address_patterns = [
            r'(?:ev\s*adres|ev\s*adresi|evimin\s*adresi|ikametgah|ikamet\s*adres)[\s:ıi\.]+(.{15,200}?)(?=\.|,|\n|$)',
            r'Ev\s*adresiniz[\s:]*\n?([A-Za-zÇçĞğİıÖöŞşÜü\s,\.:No\d]+?)(?=\n|$)',
            r'Ev\s*adresiniz[\s:]*([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+(?:mahallesi|mah\.?)[\s,]+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+(?:sokak|sokağı|sok\.?|cadde|caddesi|cad\.?)[\s,]+(?:No|no)[\s:\.]*\d+[\s,]+(?:Daire|daire|d\.)[\s:\.]*\d+)',
        ]
        
        for pattern in home_address_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.HOME_ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Pattern 2: İş adresi context
        work_address_patterns = [
            r'(?:iş\s*adres|iş\s*adresi|işyeri\s*adres|ofis\s*adres|şirket\s*adres)[\s:ıi\.]+(.{15,200}?)(?=\.|,|\n|telefon|tel|e-?posta|mail|@|$)',
            r'İş\s*adresiniz[\s:]*\n?([A-Za-zÇçĞğİıÖöŞşÜü\s,\.:No\d]+?)(?=\n|$)',
            r'İş\s*adresiniz[\s:]*([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+(?:caddesi|cad\.?)[\s,]+(?:No|no)[\s:\.]*\d+[\s,]+(?:Ofis|ofis)[\s:\.]*\d+)',
        ]
        
        for pattern in work_address_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.WORK_ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Ofis/Bina No pattern
        office_patterns = [
            r'\b(?:Ofis|Büro|Daire|Kat)[\s:\.]*(\d+)\b',
        ]
        
        for pattern in office_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.WORK_ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 3: Genel adres context
        address_context_patterns = [
            # @ işaretine kadar al (e-posta karışmasın)
            r'(?:adres|adresim|adresimiz|teslimat\s*adres|fatura\s*adres)[\s:ıi\.]+(.{15,200}?)(?=\.|,|\n|telefon|tel|e-?posta|mail|@|$)',
            # Tam adres formatı: "Barbaros Mahallesi, Deniz Sokak No:12 Daire:5"
            r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+(?:mahallesi|mah\.?)[\s,]+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+(?:sokak|sokağı|sok\.?|cadde|caddesi|cad\.?)[\s,]+(?:No|no)[\s:\.]*\d+[\s,]+(?:Daire|daire|d\.)[\s:\.]*\d+)',
            # İş adresi formatı: "Teknopark Caddesi No:45, Ofis:302"
            r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?\s+(?:caddesi|cad\.?)[\s,]+(?:No|no)[\s:\.]*\d+[\s,]+(?:Ofis|ofis)[\s:\.]*\d+)',
        ]
        
        for pattern in address_context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # E-posta check: eğer yakalanan değer "@" içeriyorsa veya bir domain ise atla
                val = match.group(0) if match.groups() == () else match.group(1)
                if '@' in val or '.com' in val:
                    continue
                    
                entities.append(DetectedEntity(
                    entity_type=EntityType.ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95
                ))
        
        # Pattern 4: Mahalle pattern'leri
        mahalle_patterns = [
            r'([A-Za-zÇçĞğİıÖöŞşÜü\s]+)\s+(?:mahallesi|mah\.?)\b',
            r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?)\s+(?:mahallesi|mah\.?)[\s,]+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?)\s+(?:sokak|sokağı|sok\.?|cadde|caddesi|cad\.?)[\s,]+',  # "Barbaros Mahallesi, Deniz Sokak"
        ]
        
        for pattern in mahalle_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 5: Cadde/Sokak pattern'leri
        street_patterns = [
            r'([A-Za-zÇçĞğİıÖöŞşÜü\s]+)\s+(?:caddesi|cad\.?|sokağı|sok\.?|bulvarı|blv\.?)\b',
            r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?)\s+(?:sokak|sokağı|sok\.?)[\s,]+(?:No|no)[\s:\.]*(\d+)[\s,]+(?:Daire|daire|d\.)[\s:\.]*(\d+)',  # "Deniz Sokak No:12 Daire:5"
        ]
        
        for pattern in street_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 6: No/Daire pattern'leri
        number_patterns = [
            r'\b(?:no|numara)[\s:\.]*(\d+)[\s/,]*(?:daire|d\.?|kat|k\.?)[\s:\.]*(\d+)',
            r'\bno[\s:\.]*(\d+)',
            r'\bdaire[\s:\.]*(\d+)',
        ]
        
        for pattern in number_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85
                ))
        
        # Pattern 7: Posta kodu
        postal_patterns = [
            r'\b(\d{5})\s+([A-Za-zÇçĞğİıÖöŞşÜü]+(?:/[A-Za-zÇçĞğİıÖöŞşÜü]+)?)\b',
            r'(?:posta\s*kodu|pk)[\s:\.]*(\d{5})',
        ]
        
        for pattern in postal_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.88
                ))
        
        # Pattern 8: İl/İlçe bilgisi
        city_district_patterns = [
            r'(?:il|ilçe|şehir)[\s:\.]+([A-Za-zÇçĞğİıÖöŞşÜü]+)',
        ]
        
        for pattern in city_district_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                location = match.group(1).lower()
                if location in self.cities or location in self.districts:
                    entities.append(DetectedEntity(
                        entity_type=EntityType.CITY_DISTRICT,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.95
                    ))
        
        # Pattern 9: İl/İlçe formatı: Kadıköy/İstanbul veya İstanbul / Ataşehir
        location_format_patterns = [
            r'\b([A-Za-zÇçĞğİıÖöŞşÜü]+)[\s/]+([A-Za-zÇçĞğİıÖöŞşÜü]+)\b',
            r'([A-Za-zÇçĞğİıÖöŞşÜü]+)\s*/\s*([A-Za-zÇçĞğİıÖöŞşÜü]+)',
        ]
        
        for pattern in location_format_patterns:
            for match in re.finditer(pattern, text):
                first = match.group(1).lower()
                second = match.group(2).lower()
                
                if (first in self.cities or first in self.districts or 
                    second in self.cities or second in self.districts):
                    entities.append(DetectedEntity(
                        entity_type=EntityType.CITY_DISTRICT,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.85
                    ))
        
        # Pattern 10: Direkt şehir/ilçe isimleri (büyük harfle başlayan)
        direct_location_pattern = r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+)?)\s*(?:/|,)\s*([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\b'
        for match in re.finditer(direct_location_pattern, text):
            first = match.group(1).lower()
            second = match.group(2).lower()
            if (first in self.cities or first in self.districts or 
                second in self.cities or second in self.districts):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CITY_DISTRICT,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        return self._remove_duplicates(entities)
    
    def _remove_duplicates(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Çakışan entity'leri kaldır, en uzun olanı tut"""
        if not entities:
            return entities
        
        entities.sort(key=lambda e: (e.start_pos, -len(e.value), -e.confidence))
        
        result = []
        for entity in entities:
            overlaps = False
            for i, existing in enumerate(result):
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    # Daha uzun olanı tut
                    if len(entity.value) > len(existing.value):
                        result[i] = entity
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(entity)
        
        return result
