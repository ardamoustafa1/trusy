

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, CUSTOMER_ID_KEYWORDS


class CustomerIDDetector(BaseDetector):
    
    def __init__(self):
        super().__init__()
        self.keywords = CUSTOMER_ID_KEYWORDS
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Müşteri numarası
        customer_patterns = [
            r'(?:müşteri\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:müşteri\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*(\d{6,20})',  # Sadece sayı
            r'(?:hesap\s*bilgilerinize|hesap\s*bilgileriniz)[\s:\.]+[^\.]*?müşteri\s*numaranız[\s:\.]*(\d{6,20})',  # "Hesap bilgilerinize geçiyorum. Müşteri numaranız 78451236"
            r'müşteri\s*numaranız\s+(\d{6,20})',  # Direkt format
        ]
        
        for pattern in customer_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CUSTOMER_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Pattern 2: Abonelik numarası
        subscription_patterns = [
            r'(?:abone\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:abonelik\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:abonelik\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z]{2,4}[\-]?[A-Z0-9]{4,15})',  # ABN-556789 formatı
        ]
        
        for pattern in subscription_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.SUBSCRIPTION_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Pattern 3: Sözleşme numarası
        contract_patterns = [
            r'(?:sözleşme\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:kontrat\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:sözleşme\s*(?:no|numarası|numaram))[\s:\.#]*([A-Z]{2,4}[\-]?\d{4}[\-]?[A-Z0-9]{4,15})',  # SOZ-2024-99128 formatı
        ]
        
        for pattern in contract_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CONTRACT_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Pattern 4: Çağrı kayıt numarası
        call_patterns = [
            r'(?:çağrı\s*kayıt|çağrı\s*kaydı|çağrı\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:arama\s*kayıt|arama\s*(?:no|numarası|numaram|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:görüşme\s*(?:no|numarası|kaydı|numaranız))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:çağrı\s*kayıt|görüşmeye\s*ait)[\s:\.#]*([A-Z]{2}[\-]?\d{4}[\-]?[A-Z0-9]{4,15})',  # CR-2026-847291 formatı
            r'\b(CR[\-]?\d{4}[\-]?[A-Z0-9]{4,15})\b',  # Direkt format
        ]
        
        for pattern in call_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CALL_RECORD_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        # Pattern 5: Diğer numara türleri (genel CUSTOMER_ID)
        other_patterns = [
            r'(?:hesap\s*(?:no|numarası|numaram))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:referans\s*(?:no|numarası))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:sipariş\s*(?:no|numarası))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:takip\s*(?:no|numarası))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:kayıt\s*(?:no|numarası))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:hizmet\s*(?:no|numarası))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:hat\s*(?:no|numarası|numaram))[\s:\.#]*([A-Z0-9\-]{4,20})',
            r'(?:ticket|tiket|talep\s*(?:no|numarası))[\s:\.#]*([A-Z0-9\-]{4,20})',
        ]
        
        for pattern in other_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CUSTOMER_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95
                ))
        
        # Pattern 6: Operatör-spesifik ve Özel formatlar
        operator_patterns = [
            r'\b(VOD[\-]?[A-Z0-9]{6,15})\b',  # Vodafone
            r'\b(TC[\-]?[A-Z0-9]{6,15})\b',   # Turkcell
            r'\b(TT[\-]?[A-Z0-9]{6,15})\b',   # Türk Telekom
            r'\b(CRM[\-]?[A-Z0-9]{6,15})\b',  # CRM numarası
            r'\b(TKT[\-]?[A-Z0-9]{6,15})\b',  # Ticket
            r'\b(ABN[\-]?[A-Z0-9]{6,15})\b',  # Abonelik
            r'\b(SOZ[\-]?[A-Z0-9]{6,15})\b',  # Sözleşme
            r'\b(CR[\-]?[A-Z0-9]{6,15})\b',   # Call Record
        ]
        
        for pattern in operator_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CUSTOMER_ID,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
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
