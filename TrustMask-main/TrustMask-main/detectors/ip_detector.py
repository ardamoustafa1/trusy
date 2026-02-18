"""
IP Adresi Detector

IPv4 ve IPv6 formatlarını tespit eder.
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType


class IPDetector(BaseDetector):
    """IP adresi tespit edicisi"""
    
    def __init__(self):
        super().__init__()
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Pattern 1: IPv4
        # 192.168.1.1, 10.0.0.1
        ipv4_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        
        for match in re.finditer(ipv4_pattern, text):
            ip = match.group(0)
            # Bazı özel IP'leri hariç tut (opsiyonel)
            if not self._is_special_ip(ip):
                entities.append(DetectedEntity(
                    entity_type=EntityType.IP_ADDRESS,
                    value=ip,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95
                ))
        
        # Pattern 2: IPv6 (basitleştirilmiş)
        ipv6_patterns = [
            # Full IPv6
            r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',
            # Compressed IPv6
            r'\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b',
            r'\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b',
            r'\b::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}\b',
        ]
        
        for pattern in ipv6_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.IP_ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.90
                ))
        
        # Pattern 3: IP context ile
        context_patterns = [
            r'(?:IP|ip\s*adres|ip\s*adresi)[\s:\.]+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        ]
        
        for pattern in context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.IP_ADDRESS,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.98
                ))
        
        return self._remove_duplicates(entities)
    
    def _is_special_ip(self, ip: str) -> bool:
        """Özel IP adreslerini kontrol et (localhost, broadcast vs.)"""
        special_ips = [
            '0.0.0.0',
            '255.255.255.255',
            '127.0.0.1',
        ]
        return ip in special_ips
    
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
