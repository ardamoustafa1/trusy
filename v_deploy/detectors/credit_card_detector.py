"""
Kredi Kartı Numarası Detector

Kredi kartı numaraları 16 haneli ve Luhn algoritmasına uyan numaralardır.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType


class CreditCardDetector(BaseDetector):
    """Kredi kartı numarası tespit edicisi"""
    
    def __init__(self):
        super().__init__()
        # Kart BIN numaraları (ilk 6 hane)
        self.valid_bins = {
            '4': 'Visa',
            '51': 'MasterCard', '52': 'MasterCard', '53': 'MasterCard', '54': 'MasterCard', '55': 'MasterCard',
            '2221': 'MasterCard', '2720': 'MasterCard',
            '34': 'Amex', '37': 'Amex',
            '6011': 'Discover', '65': 'Discover',
            '9792': 'Troy',  # Türk kartı
        }
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Düz 16 haneli
        patterns = [
            r'\b(\d{16})\b',
            # 1234 5678 9012 3456
            r'\b(\d{4})\s+(\d{4})\s+(\d{4})\s+(\d{4})\b',
            # 1234-5678-9012-3456
            r'\b(\d{4})[\-](\d{4})[\-](\d{4})[\-](\d{4})\b',
            # 1234.5678.9012.3456
            r'\b(\d{4})\.(\d{4})\.(\d{4})\.(\d{4})\b',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                card_num = self._extract_digits(match.group(0))
                if len(card_num) == 16 and self.validate(card_num):
                    entities.append(DetectedEntity(
                        entity_type=EntityType.CARD_INFO,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.95
                    ))
        
        # Pattern 2: Kart context ile
        context_patterns = [
            r'(?:kart|kredi\s*kart|banka\s*kart)[\s:\.ıi]*(?:no|numarası|numaram)?[\s:\.]*(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})',
            r'(?:kart|kredi\s*kart|banka\s*kart)[\s:\.ıi]*(?:no|numarası|numaram)?[\s:\.]*(\d{16})',
        ]
        
        for pattern in context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CARD_INFO,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.97
                ))
        
        # Pattern 3: Maskelenmiş kart numaraları
        # 1234****5678, 1234-****-****-5678
        masked_patterns = [
            r'\b\d{4}[\s\-]?\*{4}[\s\-]?\*{4}[\s\-]?\d{4}\b',
            r'\b\d{6}\*+\d{4}\b',
        ]
        
        for pattern in masked_patterns:
            for match in re.finditer(pattern, text):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CARD_INFO,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 4: Son kullanma tarihi ve CVV (card ile birlikte)
        expiry_patterns = [
            r'(?:son\s*kullanma|SKT|s\.k\.t)[\s:\.]*(\d{2}[\s/\-]\d{2,4})',
            r'(?:CVV|cvv|CVC|cvc|güvenlik\s*kodu)[\s:\.]*(\d{3,4})',
        ]
        
        for pattern in expiry_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CARD_INFO,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85
                ))
        
        return self._remove_duplicates(entities)
    
    def _extract_digits(self, text: str) -> str:
        """Metinden sadece rakamları çıkar"""
        return ''.join(filter(str.isdigit, text))
    
    def validate(self, card_number: str) -> bool:
        """Luhn algoritması ile kart numarası doğrulama"""
        digits = self._extract_digits(card_number)
        
        if len(digits) != 16:
            return False
        
        # BIN kontrolü (opsiyonel - daha az strict)
        # İlk hane 3, 4, 5, 6 veya 9 olmalı
        if digits[0] not in '345679':
            return False
        
        # Luhn algoritması
        try:
            total = 0
            for i, digit in enumerate(digits):
                d = int(digit)
                if i % 2 == 0:  # Çift indeksler (0-indexed)
                    d = d * 2
                    if d > 9:
                        d = d - 9
                total += d
            
            return total % 10 == 0
            
        except ValueError:
            return False
    
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
