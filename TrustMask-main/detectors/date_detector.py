"""
Tarih Detector (Doğum Tarihi odaklı) - Geliştirilmiş Versiyon

Geçersiz tarihleri de yakalar (32/13/2004 gibi) çünkü bunlar da kişisel veri olabilir.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, TURKISH_MONTHS


class DateDetector(BaseDetector):
    """Tarih (özellikle doğum tarihi) tespit edicisi - Geliştirilmiş"""
    
    def __init__(self):
        super().__init__()
        self.months = TURKISH_MONTHS
        self.month_names = list(self.months.keys())
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Sayısal formatlar - DAHA ESNEK (geçersiz tarihleri de yakala)
        # DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
        # Gün: 01-31, Ay: 01-12, Yıl: 19XX veya 20XX
        numeric_patterns = [
            # Standard: 01.01.1990, 32.13.2004 (geçersiz de olabilir)
            r'\b(\d{1,2})[\.\/\-](\d{1,2})[\.\/\-](\d{4})\b',
            # Kısa yıl: 01.01.90
            r'\b(\d{1,2})[\.\/\-](\d{1,2})[\.\/\-](\d{2})\b',
            # ISO format: 1990-01-01, 2004-13-32
            r'\b(\d{4})[\.\/\-](\d{1,2})[\.\/\-](\d{1,2})\b',
        ]
        
        for pattern in numeric_patterns:
            for match in re.finditer(pattern, text):
                # Tarih benzeri herhangi bir şeyi yakala (geçersiz olsa bile)
                entities.append(DetectedEntity(
                    entity_type=EntityType.BIRTH_DATE,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.75
                ))
        
        # Pattern 2: Türkçe ay isimleri ile
        # 1 Ocak 1990, 15 Mayıs 1985
        month_pattern = r'\b(\d{1,2})\s+(' + '|'.join(self.month_names) + r')\s+(\d{4})\b'
        for match in re.finditer(month_pattern, text, re.IGNORECASE):
            entities.append(DetectedEntity(
                entity_type=EntityType.BIRTH_DATE,
                value=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.95
            ))
        
        # Pattern 3: Doğum tarihi context ile - EN YÜKSEK ÖNCELİK
        birth_context_patterns = [
            r'(?:doğum\s*tarih|doğum\s*günü|doğduğu\s*tarih|d\.t\.|dt\.|doğum)[\s:ıi\.]*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
            r'(?:doğum\s*tarih|doğum\s*günü|doğduğu\s*tarih|d\.t\.|dt\.|doğum)[\s:ıi\.]*(\d{1,2}\s+(?:' + '|'.join(self.month_names) + r')\s+\d{4})',
            r'(?:doğum\s*tarihim|doğduğum\s*tarih|doğduğum)[\s:ıi\.]*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4})',
            r'(?:doğum\s*tarihim|doğduğum\s*tarih|doğduğum)[\s:ıi\.]*(\d{1,2}\s+(?:' + '|'.join(self.month_names) + r')\s+\d{4})',
        ]
        
        for pattern in birth_context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BIRTH_DATE,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.99
                ))
        
        # Pattern 4: Yaş context'i (yaşından doğum yılı çıkarılabilir)
        age_patterns = [
            r'(?:yaşım|yaşındayım)\s*(\d{1,2})',
            r'(\d{1,2})\s*yaşında(?:yım|yız|sınız|lar)?',
            r'(?:yaş|yas)[\s:\.]*(\d{1,2})\b',
        ]
        
        for pattern in age_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BIRTH_DATE,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.70,
                    context="yaş bilgisi"
                ))
        
        # Pattern 5: Sadece yıl (context ile)
        # "1990 doğumluyum", "doğum yılım 1985"
        year_patterns = [
            r'(\d{4})\s*doğumluyum',
            r'doğum\s*yılım[\s:\.]*(\d{4})',
            r'(\d{4})\s*yılında\s*doğdum',
        ]
        
        for pattern in year_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BIRTH_DATE,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95
                ))
        
        return self._remove_duplicates(entities)
    
    def _remove_duplicates(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Çakışan entity'leri kaldır"""
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
