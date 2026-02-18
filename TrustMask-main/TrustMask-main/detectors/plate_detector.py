"""
Araç Plakası Detector

Türk araç plaka formatları:
- 34 ABC 123 (standart)
- 06 A 1234
- 81 AA 001
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType, TURKEY_CITY_CODES


class PlateDetector(BaseDetector):
    """Araç plakası tespit edicisi"""
    
    def __init__(self):
        super().__init__()
        self.city_codes = set(TURKEY_CITY_CODES)
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: Standart format: 34 ABC 123, 34ABC123
        # İl kodu (01-81) + 1-3 harf + 2-4 rakam
        plate_patterns = [
            # 34 ABC 123, 34 ABC 12
            r'\b(0[1-9]|[1-7][0-9]|8[01])\s*([A-Za-z]{1,3})\s*(\d{2,4})\b',
            # 34ABC123
            r'\b(0[1-9]|[1-7][0-9]|8[01])([A-Za-z]{1,3})(\d{2,4})\b',
            # 34-ABC-123
            r'\b(0[1-9]|[1-7][0-9]|8[01])[\s\-]([A-Za-z]{1,3})[\s\-](\d{2,4})\b',
        ]
        
        for pattern in plate_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                city_code = match.group(1)
                if city_code in self.city_codes:
                    entities.append(DetectedEntity(
                        entity_type=EntityType.PLATE,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.95
                    ))
        
        # Pattern 2: Plaka context ile
        context_patterns = [
            r'(?:plaka|araç\s*plaka|plakası|plakam)[\s:\.]*((0[1-9]|[1-7][0-9]|8[01])[\s\-]?[A-Za-z]{1,3}[\s\-]?\d{2,4})',
        ]
        
        for pattern in context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.PLATE,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
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
