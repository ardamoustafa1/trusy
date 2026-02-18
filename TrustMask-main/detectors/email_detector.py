"""
E-posta Adresi Detector
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType


class EmailDetector(BaseDetector):
    """E-posta adresi tespit edicisi"""
    
    def __init__(self):
        super().__init__()
        # Yaygın e-posta domain'leri
        self.common_domains = {
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'yandex.com',
            'icloud.com', 'live.com', 'msn.com', 'aol.com', 'protonmail.com',
            'mail.com', 'zoho.com', 'gmx.com', 'inbox.com',
            # Türk domain'leri
            'gmail.com.tr', 'hotmail.com.tr', 'outlook.com.tr', 'yahoo.com.tr',
            'mynet.com', 'superonline.com', 'turk.net', 'ttnet.com.tr',
            'vodafone.com.tr', 'turkcell.com.tr', 'turktelekom.com.tr'
        }
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # E-posta pattern'i
        # username@domain.tld formatı
        # Türkçe karakterleri de destekleyen regex
        email_pattern = r'\b[A-ZÇĞİÖŞÜa-zçğıöşü0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        
        for match in re.finditer(email_pattern, text, re.IGNORECASE):
            email = match.group(0)
            if self.validate(email):
                entities.append(DetectedEntity(
                    entity_type=EntityType.EMAIL,
                    value=email,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # E-posta context ile
        # "mail adresim xxx@xxx.com" gibi
        context_patterns = [
            r'(?:e-?posta|mail|email|eposta)[\s:\.]*(?:adres|adresi|adresim)?[\s:\.]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})',
        ]
        
        for pattern in context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                email = match.group(1)
                if self.validate(email):
                    entities.append(DetectedEntity(
                        entity_type=EntityType.EMAIL,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.99
                    ))
        
        # E-posta benzeri yazımlar
        # ahmet[at]gmail[dot]com, ahmet (at) gmail (dot) com
        obfuscated_patterns = [
            r'\b[A-Za-z0-9._%+-]+\s*[\[\(]?\s*(?:at|@)\s*[\]\)]?\s*[A-Za-z0-9.-]+\s*[\[\(]?\s*(?:dot|\.)\s*[\]\)]?\s*[A-Za-z]{2,}\b',
        ]
        
        for pattern in obfuscated_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.EMAIL,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.85
                ))
        
        return self._remove_duplicates(entities)
    
    def validate(self, email: str) -> bool:
        """E-posta adresini doğrula"""
        if not email or '@' not in email:
            return False
        
        # Basit doğrulama
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        username, domain = parts
        
        # Username kontrolü
        if not username or len(username) > 64:
            return False
        
        # Domain kontrolü
        if not domain or '.' not in domain:
            return False
        
        tld = domain.split('.')[-1]
        if len(tld) < 2:
            return False
        
        return True
    
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
