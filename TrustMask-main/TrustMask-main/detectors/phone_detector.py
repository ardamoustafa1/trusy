"""
Telefon Numarası Detector

Türk telefon numarası formatları:
- GSM: 05XX XXX XX XX
- Sabit hat: 0XXX XXX XX XX
- Uluslararası: +90 XXX XXX XX XX
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, GSM_PREFIXES, LANDLINE_PREFIXES


class PhoneDetector(BaseDetector):
    """Türk telefon numarası tespit edicisi"""
    
    def __init__(self):
        super().__init__()
        # GSM ve sabit hat prefix'leri
        self.gsm_prefixes = set(GSM_PREFIXES)
        self.landline_prefixes = set(LANDLINE_PREFIXES)
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Uluslararası format +90
        # +90 532 123 45 67 veya +905321234567
        intl_patterns = [
            r'\+90\s*(\d{3})\s*(\d{3})\s*(\d{2})\s*(\d{2})',
            r'\+90\s*(\d{10})',
            r'\+90[\s\-]?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})',
        ]
        
        for pattern in intl_patterns:
            for match in re.finditer(pattern, text):
                phone = self._extract_digits(match.group(0))
                # Cep telefonu mu sabit hat mı kontrol et
                if len(phone) >= 10:
                    prefix = phone[-10:-7] if len(phone) > 10 else phone[:3]
                    if prefix in self.gsm_prefixes or prefix.startswith('5'):
                        entity_type = EntityType.MOBILE_PHONE
                    elif prefix in self.landline_prefixes or prefix[0] in '234':
                        entity_type = EntityType.LANDLINE
                    else:
                        entity_type = EntityType.PHONE
                else:
                    entity_type = EntityType.PHONE
                
                entities.append(DetectedEntity(
                    entity_type=entity_type,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Pattern 2: Başında 0 ile başlayan format
        # 0532 123 45 67, 05321234567, 0 532 123 45 67
        zero_patterns = [
            r'\b0\s*(\d{3})\s*(\d{3})\s*(\d{2})\s*(\d{2})\b',
            r'\b0(\d{10})\b',
            r'\b0[\s\-]?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})\b',
            r'\(0(\d{3})\)\s*(\d{3})\s*(\d{2})\s*(\d{2})',
        ]
        
        for pattern in zero_patterns:
            for match in re.finditer(pattern, text):
                phone = self._extract_digits(match.group(0))
                if self._is_valid_turkish_phone(phone):
                    # Cep telefonu mu sabit hat mı kontrol et
                    prefix = phone[1:4] if phone.startswith('0') else phone[:3]
                    if prefix in self.gsm_prefixes or prefix.startswith('5'):
                        entity_type = EntityType.MOBILE_PHONE
                    elif prefix in self.landline_prefixes or prefix[0] in '234':
                        entity_type = EntityType.LANDLINE
                    else:
                        entity_type = EntityType.PHONE
                    
                    entities.append(DetectedEntity(
                        entity_type=entity_type,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.95
                    ))
        
        # Pattern 3: Başında 0 olmadan (5XX ile başlayan GSM)
        # 532 123 45 67
        gsm_patterns = [
            r'\b(5\d{2})\s+(\d{3})\s+(\d{2})\s+(\d{2})\b',
            r'\b(5\d{9})\b',
            r'\b(5\d{2})[\s\-](\d{3})[\s\-](\d{2})[\s\-](\d{2})\b',
        ]
        
        for pattern in gsm_patterns:
            for match in re.finditer(pattern, text):
                phone = self._extract_digits(match.group(0))
                if len(phone) == 10 and phone[:3] in self.gsm_prefixes:
                    entities.append(DetectedEntity(
                        entity_type=EntityType.MOBILE_PHONE,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.90
                    ))
        
        # Pattern 4: Telefon/Tel/Cep context ile
        context_patterns = [
            r'(?:telefon|tel|cep|gsm|numara|numarası|numaram|hattı|hattım)[\s:\.]*(?:no|numarası|numaram)?[\s:\.]*(\+?90?\s*)?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})',
            r'(?:telefon|tel|cep|gsm|numara|numarası|numaram|hattı|hattım)[\s:\.]*(?:no|numarası|numaram)?[\s:\.]*(\+?90?\s*)?0?(\d{10})',
        ]
        
        for pattern in context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Context'ten cep/sabit hat ayrımı yap
                context_text = match.group(0).lower()
                phone_digits = self._extract_digits(match.group(0))
                
                if 'cep' in context_text or 'gsm' in context_text or 'mobil' in context_text:
                    entity_type = EntityType.MOBILE_PHONE
                elif 'sabit' in context_text or 'ev' in context_text or 'iş' in context_text:
                    entity_type = EntityType.LANDLINE
                elif len(phone_digits) >= 3:
                    prefix = phone_digits[-10:-7] if len(phone_digits) > 10 else phone_digits[:3]
                    if prefix in self.gsm_prefixes or prefix.startswith('5'):
                        entity_type = EntityType.MOBILE_PHONE
                    elif prefix in self.landline_prefixes or prefix[0] in '234':
                        entity_type = EntityType.LANDLINE
                    else:
                        entity_type = EntityType.PHONE
                else:
                    entity_type = EntityType.PHONE
                
                entities.append(DetectedEntity(
                    entity_type=entity_type,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.97
                ))
        
        # Pattern 5: WhatsApp formatı
        whatsapp_patterns = [
            r'(?:whatsapp|wp|watsap)[\s:\.]*(\+?90?\s*)?0?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})',
        ]
        
        for pattern in whatsapp_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # WhatsApp cep telefonu için kullanılır
                entities.append(DetectedEntity(
                    entity_type=EntityType.MOBILE_PHONE,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.97
                ))
        
        return self._remove_duplicates(entities)
    
    def _extract_digits(self, text: str) -> str:
        """Metinden sadece rakamları çıkar"""
        return ''.join(filter(str.isdigit, text))
    
    def _is_valid_turkish_phone(self, phone: str) -> bool:
        """Türk telefon numarası geçerlilik kontrolü"""
        digits = self._extract_digits(phone)
        
        # 0 ile başlıyorsa kaldır
        if digits.startswith('0'):
            digits = digits[1:]
        
        # 90 ile başlıyorsa kaldır
        if digits.startswith('90'):
            digits = digits[2:]
        
        # 10 haneli olmalı
        if len(digits) != 10:
            return False
        
        prefix = digits[:3]
        
        # GSM veya sabit hat prefix'i olmalı
        if prefix in self.gsm_prefixes:
            return True
        
        if prefix in self.landline_prefixes:
            return True
        
        # 5 ile başlayan GSM numaraları
        if prefix.startswith('5'):
            return True
        
        # 2, 3, 4 ile başlayan sabit hat numaraları
        if prefix[0] in '234':
            return True
        
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
