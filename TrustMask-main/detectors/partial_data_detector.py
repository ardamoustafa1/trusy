"""
Kısmi Veri Detector - Doğrulama Soruları - GELİŞTİRİLMİŞ V3

Müşteri hizmetleri konuşmalarında sıkça sorulan doğrulama sorularını tespit eder:
- TC Kimlik son 4 hanesi
- Telefon son 3 hanesi
- Doğum yılı
- Kartın son 4 hanesi
"""

import re
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType


class PartialDataDetector(BaseDetector):
    """Kısmi kişisel veri tespit edicisi - Doğrulama soruları için"""
    
    def __init__(self):
        super().__init__()
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Satır bazlı analiz
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            line_start = sum(len(l) + 1 for l in lines[:i])
            
            # Önceki satırları al (soru için context) - 4 satıra kadar bak (diyalog boşlukları için)
            context_lines = []
            for k in range(1, 5):
                if i - k >= 0:
                    context_lines.append(lines[i-k].lower())
            
            prev_line = lines[i-1].lower() if i > 0 else ""
            context = " ".join(context_lines)
            
            # ------ DOĞUM YILI TESPİTİ ------
            # Pattern: Satırda 4 haneli yıl (1950-2025 arası) - "Musteri: 1990." veya "1990" formatı
            year_match = re.search(r'(?:^|[:\s]+)(19[5-9]\d|20[0-2]\d)[.,!?]?\s*$', line)
            if year_match:
                # Context kontrolü: önceki satırlarda "doğum" veya "yıl" var mı?
                context_lower = context.lower()
                prev_line_lower = prev_line.lower()
                
                has_birth_context = (
                    'doğum' in context_lower or 'dogum' in context_lower or 
                    'yıl' in prev_line_lower or 'yil' in prev_line_lower or
                    'doğum yılınızı' in prev_line_lower or
                    'doğum yılı' in prev_line_lower
                )
                
                if has_birth_context:
                    year_value = year_match.group(1)
                    # Match start hesaplaması düzeltildi
                    full_match_start = year_match.start()
                    group_start = year_match.start(1)
                    match_start = line_start + group_start
                    match_end = line_start + year_match.end(1)
                    
                    entities.append(DetectedEntity(
                        entity_type=EntityType.BIRTH_YEAR,
                        value=year_value,
                        start_pos=match_start,
                        end_pos=match_end,
                        confidence=0.98,
                        context="birth_year_answer"
                    ))
            
            # ------ TC SON 2-4 HANE TESPİTİ ------
            # Pattern: Satırda 2-4 haneli sayı - "Musteri: 1234." veya "2109." formatı  
            tc_match = re.search(r'(?:^|[:\s]+)(\d{2,4})[.,!?]?\s*$', line)
            if tc_match:
                value = tc_match.group(1)
                # Yıl mı kontrol et (1950-2025 arası değilse TC olabilir)
                try:
                    num = int(value)
                    is_year = 1950 <= num <= 2025
                except:
                    is_year = False
                
                # Context kontrolü - daha geniş
                context_lower = context.lower()
                prev_line_lower = prev_line.lower()
                line_lower = line.lower()
                
                has_tc_context = (
                    'tc' in context_lower or 't.c' in context_lower or 'kimlik' in context_lower or
                    'kimlik numaranızın son' in prev_line_lower or
                    'son' in prev_line_lower and 'hane' in prev_line_lower or
                    'doğrulama' in prev_line_lower or
                    'ek doğrulama' in prev_line_lower
                )
                
                if not is_year and has_tc_context:
                    match_start = line_start + tc_match.start(1)
                    match_end = line_start + tc_match.end(1)
                    entities.append(DetectedEntity(
                        entity_type=EntityType.TC_ID,
                        value=value,
                        start_pos=match_start,
                        end_pos=match_end,
                        confidence=0.98,
                        context="tc_partial_answer"
                    ))
            
            # ------ TELEFON SON 2-3 HANE TESPİTİ ------
            # Pattern: Satırda 2-3 haneli sayı
            phone_match = re.search(r'(?:^|[:\s]+)(\d{2,3})[.,!?]?\s*$', line)
            if phone_match:
                # Context kontrolü - daha geniş
                context_lower = context.lower()
                prev_line_lower = prev_line.lower()
                
                has_phone_context = (
                    'telefon' in context_lower or 'numara' in context_lower or 'tel' in context_lower or
                    'cep' in context_lower or 'hat' in context_lower or
                    'telefon numaranızın son' in prev_line_lower or
                    ('son' in prev_line_lower and 'hane' in prev_line_lower) or
                    'doğrulama' in prev_line_lower
                )
                
                if has_phone_context:
                    value = phone_match.group(1)
                    match_start = line_start + phone_match.start(1)
                    match_end = line_start + phone_match.end(1)
                    entities.append(DetectedEntity(
                        entity_type=EntityType.PHONE,
                        value=value,
                        start_pos=match_start,
                        end_pos=match_end,
                        confidence=0.98,
                        context="phone_partial_answer"
                    ))
        
        # ---- INLINE PATTERNS ----
        
        # Doğum yılı (aynı satırda explicit context)
        year_inline_patterns = [
            r'(?:doğum|dogum)\s*(?:yılı|yili|yılınız|yiliniz)[\s:]*(\d{4})',
            r'(\d{4})\s*(?:doğumluyum|dogumluyum)',
            r'(?:yılı|yili|yılınız|yiliniz)[\s:]+(\d{4})',
        ]
        
        for pattern in year_inline_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.BIRTH_YEAR,
                    value=match.group(1),
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.95,
                    context="birth_year_inline"
                ))
        
        # TC son hane (aynı satırda explicit context) - 2-4 hane
        tc_inline_patterns = [
            r'(?:TC|T\.C\.|kimlik).*?(?:son\s*[234]?\s*hane).*?(?:\s+|:|dır|dir|dur|dür|ise|olarak)?\s*(\d{2,4})\b',
            r'(?:son\s*[234]?\s*hane).*?(?:\s+|:|dır|dir|dur|dür|ise|olarak)?\s*(\d{2,4})\b',
        ]
        
        for pattern in tc_inline_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.TC_ID,
                    value=match.group(1),
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.95,
                    context="tc_partial_inline"
                ))
        
        # Telefon son hane (aynı satırda explicit context) - 2-3 hane
        phone_inline_patterns = [
            r'(?:telefon|tel|cep|numara).*?(?:son\s*[23]?\s*hane).*?[\s:]+(\d{2,3})',
            r'(?:son\s*[23]?\s*hane)[\s:]+(\d{2,3})',
        ]
        
        for pattern in phone_inline_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.PHONE,
                    value=match.group(1),
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.95,
                    context="phone_partial_inline"
                ))
        
        # Kart son 4 hane
        card_patterns = [
            r'(?:kart|kredi\s*kart).*?(?:son\s*4\s*hane).*?[:\s]+(\d{4})\b',
            r'(?:son\s*4\s*hane)[:\s]*(\d{4})\b',
        ]
        
        for pattern in card_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(DetectedEntity(
                    entity_type=EntityType.CARD_INFO,
                    value=match.group(1),
                    start_pos=match.start(1),
                    end_pos=match.end(1),
                    confidence=0.95,
                    context="card_partial"
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
