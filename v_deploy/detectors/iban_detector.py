"""
IBAN ve Banka Bilgileri Detector

Türk IBAN formatı: TR + 2 check digit + 5 banka kodu + 1 rezerv + 16 hesap numarası = 26 karakter
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, TURKISH_BANK_CODES


class IBANDetector(BaseDetector):
    """IBAN ve banka bilgileri tespit edicisi"""
    
    def __init__(self):
        super().__init__()
        self.bank_codes = set(TURKISH_BANK_CODES)
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Düz IBAN (TR ile başlayan 26 karakter)
        iban_patterns = [
            # TR330006100519786457841326
            r'\bTR\d{24}\b',
            # TR33 0006 1005 1978 6457 8413 26
            r'\bTR\d{2}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{2}\b',
            # TR34 0006 2000 0000 4589 1234 56 (daha esnek boşluk)
            r'\bTR\s*\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{2}\b',
            # TR33-0006-1005-1978-6457-8413-26
            r'\bTR\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{2}\b',
            # TR34 0006 2000 0000 4589 1234 56 (tire ile)
            r'\bTR\d{2}[\s\-]+\d{4}[\s\-]+\d{4}[\s\-]+\d{4}[\s\-]+\d{4}[\s\-]+\d{4}[\s\-]+\d{2}\b',
        ]
        
        for pattern in iban_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                iban = match.group(0).upper()
                normalized = self.normalize(iban)
                # Validate etmeye çalış, başarısız olsa bile context varsa yakala
                if self.validate(normalized):
                    entities.append(DetectedEntity(
                        entity_type=EntityType.BANK_INFO,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.98
                    ))
                else:
                    # Context kontrolü - IBAN kelimesi yakında var mı?
                    context_start = max(0, match.start() - 50)
                    context_end = min(len(text), match.end() + 20)
                    context = text[context_start:context_end].lower()
                    if 'iban' in context or 'banka' in context or 'hesap' in context:
                        entities.append(DetectedEntity(
                            entity_type=EntityType.BANK_INFO,
                            value=match.group(0),
                            start_pos=match.start(),
                            end_pos=match.end(),
                            confidence=0.90
                        ))
        
        # Pattern 2: IBAN prefix ile
        iban_context_patterns = [
            r'(?:IBAN|iban)[\s:\.]*([A-Za-z]{2}\d{2}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{2})',
            r'(?:IBAN|iban)[\s:\.]*([A-Za-z]{2}\d{24})',
        ]
        
        for pattern in iban_context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BANK_INFO,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.99
                ))
        
        # Pattern 3: Banka hesap numarası (context ile)
        account_patterns = [
            r'(?:hesap\s*(?:no|numarası|numaram))[\s:\.]*(\d{10,20})',
            r'(?:banka\s*hesab)[\s:\.ıi]*(\d{10,20})',
        ]
        
        for pattern in account_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BANK_INFO,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        return self._remove_duplicates(entities)
    
    def validate(self, iban: str) -> bool:
        """IBAN doğrulama (ISO 13616)"""
        # Boşlukları ve tire'leri kaldır
        iban = self.normalize(iban)
        
        # TR ile başlamalı ve 26 karakter olmalı
        if not iban.startswith('TR') or len(iban) != 26:
            return False
        
        try:
            # IBAN check digit doğrulama
            # İlk 4 karakteri sona taşı
            rearranged = iban[4:] + iban[:4]
            
            # Harfleri sayıya çevir (A=10, B=11, ... Z=35)
            numerical = ''
            for char in rearranged:
                if char.isalpha():
                    numerical += str(ord(char.upper()) - 55)
                else:
                    numerical += char
            
            # Mod 97 kontrolü
            return int(numerical) % 97 == 1
            
        except (ValueError, IndexError):
            return False
    
    def normalize(self, iban: str) -> str:
        """IBAN'ı normalize et"""
        return ''.join(iban.upper().split()).replace('-', '')
    
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
