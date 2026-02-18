"""
Cinsiyet ve Ek Bilgiler Detector

Cinsiyet bilgisi, anne/baba adı, çağrı kayıt numarası gibi ek bilgileri tespit eder.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, GENDER_KEYWORDS, TURKISH_BANKS


class GenderDetector(BaseDetector):
    """Cinsiyet bilgisi tespit edicisi - Geliştirilmiş"""
    
    def __init__(self):
        super().__init__()
        self.gender_keywords = GENDER_KEYWORDS
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Cinsiyet context ile
        gender_patterns = [
            # "cinsiyet: erkek", "cinsiyeti kadın"
            r'(?:cinsiyet|cinsiyeti|cinsiyetim)[\s:\.]+([eE]rkek|[kK]adın|[bB]ay|[bB]ayan|[eE]|[kK])\b',
            # "cinsiyet: E", "cinsiyet: K"
            r'(?:cinsiyet|cinsiyeti|cinsiyetim)[\s:\.]+([EeKk])\b',
            # "ben erkek/kadın", "ben bay/bayan"
            r'\b(?:ben|biz)[\s,]+([eE]rkek|[kK]adın|[bB]ay|[bB]ayan)\b',
            # "erkek/kadın", "bay/bayan" (cümle başında veya context ile)
            r'(?:^|[\s,\.])([eE]rkek|[kK]adın|[bB]ay|[bB]ayan)\b',
            # "E/K" (kısaltma, context ile)
            r'(?:cinsiyet|cinsiyeti)[\s:\.]*([EeKk])\b',
        ]
        
        for pattern in gender_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Çok kısa eşleşmeleri filtrele (sadece "E" veya "K" gibi)
                matched_text = match.group(0).strip()
                if len(matched_text) <= 2 and matched_text.upper() not in ['E', 'K']:
                    continue
                
                entities.append(DetectedEntity(
                    entity_type=EntityType.GENDER,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95
                ))
        
        return entities


class ParentNameDetector(BaseDetector):
    """Anne/Baba adı tespit edicisi - Geliştirilmiş"""
    
    def __init__(self):
        super().__init__()
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern: Anne adı context ile - HER kelimeyi yakala
        mother_patterns = [
            # "anne adı X", "annenizin adı X"
            r'(?:anne\s*adı|annenin\s*adı|annemin\s*adı|annenizin\s*adı|valide\s*adı)[\s:\.]+([A-ZÇĞİÖŞÜa-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıöşü]+)?)',
            # "anne kızlık soyadı X"
            r'(?:anne\s*kızlık\s*soyad|annemin\s*kızlık\s*soyad|kızlık\s*soyad)[ıi]?[\s:\.]+([A-ZÇĞİÖŞÜa-zçğıöşü]+)',
            # "annem X", "annemizin adı X"
            r'(?:annem|annemiz)[\s:\.]+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)',
        ]
        
        for pattern in mother_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.PARENT_NAME,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98,
                    context="anne_adi"
                ))
        
        # Pattern: Baba adı context ile - HER kelimeyi yakala
        father_patterns = [
            # "baba adı X", "babanızın adı X"
            r'(?:baba\s*adı|babanın\s*adı|babamın\s*adı|babanızın\s*adı|peder\s*adı)[\s:\.]+([A-ZÇĞİÖŞÜa-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜa-zçğıöşü]+)?)',
            # "babam X", "babamızın adı X"
            r'(?:babam|babamız)[\s:\.]+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)',
        ]
        
        for pattern in father_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.PARENT_NAME,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98,
                    context="baba_adi"
                ))
        
        return entities


class BankNameDetector(BaseDetector):
    """Banka adı tespit edicisi"""
    
    def __init__(self):
        super().__init__()
        self.banks = TURKISH_BANKS
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        text_lower = text.lower()
        
        # Pattern 1: Banka adlarını doğrudan ara
        for bank in self.banks:
            # Kelime sınırları ile ara
            pattern = r'\b' + re.escape(bank) + r'\b'
            for match in re.finditer(pattern, text_lower):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BANK_NAME,
                    value=text[match.start():match.end()],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 2: Banka context ile
        bank_context_patterns = [
            r'(?:banka|bankası|bankam|bankanız)[\s:\.]+([A-ZÇĞİÖŞÜa-zçğıöşü\s]+?)(?=\s*[,\.\n]|$)',
        ]
        
        for pattern in bank_context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BANK_NAME,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85
                ))
        
        return self._remove_duplicates(entities)
    
    def _remove_duplicates(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        if not entities:
            return entities
        
        entities.sort(key=lambda e: (e.start_pos, -e.confidence, -len(e.value)))
        
        result = []
        for entity in entities:
            overlaps = False
            for existing in result:
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(entity)
        
        return result


class CallRecordDetector(BaseDetector):
    """Çağrı kayıt numarası tespit edicisi - Geliştirilmiş"""
    
    def __init__(self):
        super().__init__()
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern: Çağrı kayıt numarası
        call_patterns = [
            r'(?:çağrı\s*kayıt|çağrı\s*kaydı|çağrı\s*no|çağrı\s*numarası|görüşmeye\s*ait)[\s:\.#]*([A-Z0-9\-]{5,20})',
            # Specific context with intervening words "görüşmeye ait ... numaranız"
            r'(?:görüşmeye\s*ait\s*çağrı\s*kayıt\s*numara[a-z]*)[\s:\.#]*([A-Z0-9\-]{5,20})',
            r'(?:arama\s*kayıt|arama\s*kaydı|arama\s*no)[\s:\.#]*([A-Z0-9\-]{5,20})',
            r'(?:görüşme\s*kayıt|görüşme\s*no)[\s:\.#]*([A-Z0-9\-]{5,20})',
            # CRM / Ticket numaraları
            r'(?:ticket|tiket|talep\s*no|talep\s*numarası)[\s:\.#]*([A-Z0-9\-]{5,20})',
            # CR-2026-847291 formatı and AC-2026-119845 format
            r'(?:çağrı\s*kayıt|görüşmeye\s*ait)[^0-9\n]{0,30}([A-Z]{2}[\-]?\d{4}[\-]?[A-Z0-9]{4,15})',
            # Direkt format tespiti (CR/AC/SOZ vb. ardından yıl ve numara)
            r'\b((?:CR|AC|TR|CN)[\-]?\d{4}[\-]?[A-Z0-9]{4,15})\b',
            # Genel format: 2 Harf - 4 Rakam - 6+ Rakam/Harf (örn: AB-2024-123456)
            r'\b([A-Z]{2}[\-]\d{4}[\-][A-Z0-9]{5,15})\b',
        ]
        
        for pattern in call_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Use group(1) if available to catch only the ID, else fall back to group(0)
                if match.groups():
                    val = match.group(1)
                    start = match.start(1)
                    end = match.end(1)
                else:
                    val = match.group(0)
                    start = match.start()
                    end = match.end()

                entities.append(DetectedEntity(
                    entity_type=EntityType.CALL_RECORD_ID,
                    value=val,
                    start_pos=start,
                    end_pos=end,
                    confidence=0.95
                ))
        
        return entities
