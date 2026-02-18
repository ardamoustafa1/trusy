"""
TC Kimlik Numarası Detector - Geliştirilmiş Versiyon

TC Kimlik numarası 11 haneli bir sayıdır.
Artık checksum doğrulaması opsiyonel - context varsa tüm 11 haneli numaraları yakalar.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType


class TCKimlikDetector(BaseDetector):
    """TC Kimlik Numarası tespit edicisi - Geliştirilmiş"""
    
    def __init__(self, strict_validation: bool = False):
        """
        Args:
            strict_validation: True ise sadece checksum doğru TC'leri yakalar
                             False ise context varsa tüm 11 haneli numaraları yakalar (varsayılan)
        """
        super().__init__()
        self.strict_validation = strict_validation
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: TC/T.C./Kimlik prefix ile - HER 11 haneli sayıyı yakala (context güçlü)
        tc_context_patterns = [
            r'(?:TC|T\.C\.|T\.C|tc|t\.c\.|t\.c)[\s:\.]*(?:No|NO|no|Kimlik|kimlik|numara|numarası|numaram)?[\s:\.]*(\d{11})',
            r'(?:kimlik)[\s:\.]*(?:numara|no|numarası|numaram)?[\s:\.]*(\d{11})',
            r'(?:kimlik|TC|T\.C\.?)[\s:\.]*(\d{3})[\s\-]*(\d{3})[\s\-]*(\d{3})[\s\-]*(\d{2})',
        ]
        
        for pattern in tc_context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Context ile bulundu - checksum kontrolü yapmadan yakala
                entities.append(DetectedEntity(
                    entity_type=EntityType.TC_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98,
                    context="tc_context"
                ))
        
        # Pattern 2: Boşluklu format: 323 030 104 29
        for match in re.finditer(r'\b(\d{3})[\s\-]+(\d{3})[\s\-]+(\d{3})[\s\-]+(\d{2})\b', text):
            tc_no = match.group(1) + match.group(2) + match.group(3) + match.group(4)
            # Context kontrolü - yakınında TC/kimlik kelimesi var mı?
            context_start = max(0, match.start() - 30)
            context = text[context_start:match.start()].lower()
            has_context = any(kw in context for kw in ['tc', 't.c', 'kimlik', 'numara'])
            
            if has_context or (self.strict_validation and self.validate(tc_no)):
                entities.append(DetectedEntity(
                    entity_type=EntityType.TC_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95 if has_context else 0.85
                ))
            elif not self.strict_validation and self.validate(tc_no):
                entities.append(DetectedEntity(
                    entity_type=EntityType.TC_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 3: Düz 11 haneli - context veya çok esnek
        for match in re.finditer(r'\b(\d{11})\b', text):
            tc_no = match.group(1)
            
            # Zaten yukarıda yakalandı mı kontrol et
            already_matched = any(
                match.start() >= e.start_pos and match.end() <= e.end_pos
                for e in entities
            )
            if already_matched:
                continue
            
            # Context kontrolü
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 30)
            context = text[context_start:context_end].lower()
            
            has_tc_context = any(kw in context for kw in ['tc', 't.c', 'kimlik', 'numara', 'no:'])
            
            if has_tc_context:
                # Context var - checksum olmadan yakala
                entities.append(DetectedEntity(
                    entity_type=EntityType.TC_ID,
                    value=tc_no,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95
                ))
            elif self.validate(tc_no):
                # Checksum doğru - yakala
                entities.append(DetectedEntity(
                    entity_type=EntityType.TC_ID,
                    value=tc_no,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85
                ))
            elif not self.strict_validation:
                # İlk hanesi 0 değil ve 11 haneli - potansiyel TC olarak işaretle
                if tc_no[0] != '0':
                    entities.append(DetectedEntity(
                        entity_type=EntityType.TC_ID,
                        value=tc_no,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.60,
                        context="potential_tc"
                    ))
        
        return self._remove_duplicates(entities)
    
    def _remove_duplicates(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Çakışan entity'leri kaldır, en yüksek confidence olanı tut"""
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
    
    def validate(self, tc_no: str) -> bool:
        """TC Kimlik numarası checksum doğrulama"""
        tc_no = ''.join(filter(str.isdigit, tc_no))
        
        if len(tc_no) != 11:
            return False
        
        if tc_no[0] == '0':
            return False
        
        try:
            digits = [int(d) for d in tc_no]
            
            odd_sum = digits[0] + digits[2] + digits[4] + digits[6] + digits[8]
            even_sum = digits[1] + digits[3] + digits[5] + digits[7]
            
            check_10 = (odd_sum * 7 - even_sum) % 10
            if check_10 < 0:
                check_10 += 10
            if check_10 != digits[9]:
                return False
            
            total_sum = sum(digits[:10])
            check_11 = total_sum % 10
            if check_11 != digits[10]:
                return False
            
            return True
            
        except (ValueError, IndexError):
            return False
