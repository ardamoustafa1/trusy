

import re
from typing import List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detectors.base_detector import BaseDetector
from entities import DetectedEntity
from config import EntityType
from nlp.turkish_names_db import (
    TURKISH_FIRST_NAMES, 
    TURKISH_SURNAMES, 
    HONORIFICS,
    NAME_LIKE_COMMON_WORDS
)


class NameDetector(BaseDetector):
   
    
    def __init__(self):
        super().__init__()
        self.first_names = TURKISH_FIRST_NAMES
        self.surnames = TURKISH_SURNAMES
        self.honorifics = HONORIFICS
        self.common_words = NAME_LIKE_COMMON_WORDS
        
        # Common words'ü lowercase haliyle de ekle
        self.common_words_lower = {self._turkish_lower(w) for w in NAME_LIKE_COMMON_WORDS}
    
        
        # GÜÇLÜ CONTEXT PATTERN'LERİ - Herhangi bir kelimeyi yakala
        self.strong_context_patterns = [
            # "adım X", "ismim X", "benim adım X"
            (r'(?:adım|ismim|benim\s+adım|benim\s+ismim)[\s:]+([A-ZÇĞİÖŞÜa-zçğıöşü]+)', EntityType.NAME),
            # "soyadım X", "soy adım X", "soy ismim X"
            (r'(?:soyadım|soyismim|soy\s*adım|soy\s*ismim)[\s:]+([A-ZÇĞİÖŞÜa-zçğıöşü]+)', EntityType.SURNAME),
            # "anne kızlık soyadı X", "annemin kızlık soyadı X"
            (r'(?:anne\s*kızlık\s*soyad|annemin\s*kızlık\s*soyad|kızlık\s*soyad)[ıi]?[\s:]+([A-ZÇĞİÖŞÜa-zçğıöşü]+)', EntityType.SURNAME),
            # "baba adı X", "anne adı X"
            (r'(?:baba\s*adı|anne\s*adı|babasının\s*adı|annesinin\s*adı)[\s:]+([A-ZÇĞİÖŞÜa-zçğıöşü]+)', EntityType.NAME),
            # "ben X", "Ben X" (cümle başı)
            (r'(?:^|\.\s+)[Bb]en\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)', EntityType.NAME),
            # "merhaba X", "selam X"
            (r'(?:merhaba|selam|günaydın|iyi\s+günler)[\s,]+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)', EntityType.NAME),
            # "müşteri X Y", "abone X Y"
            (r'(?:müşteri|abone|kullanıcı|üye)[\s:]+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)(?:\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+))?', EntityType.FULL_NAME),
            # "Sayın X Y"
            (r'[Ss]ayın\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)(?:\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+))?', EntityType.FULL_NAME),
            # "X Bey", "X Hanım"
            (r'([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s+(?:[Bb]ey|[Hh]anım|[Ee]fendi)', EntityType.NAME),
            # "Dr. X", "Prof. X"
            (r'(?:[Dd]r\.?|[Pp]rof\.?|[Dd]oç\.?|[Aa]v\.?|[Mm]üh\.?)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)(?:\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+))?', EntityType.FULL_NAME),
            # İyelik ekleri: "X'in", "X'nın"
            (r"([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)'(?:in|ın|un|ün|nin|nın|nun|nün|e|a|ye|ya)", EntityType.NAME),
        ]
    
    def detect(self, text: str) -> List[DetectedEntity]:
        entities = []
        
        # Method 1: GÜÇLÜ CONTEXT-BASED DETECTION - HER KELİMEYİ YAKALA
        entities.extend(self._detect_with_strong_context(text))
        
        # Method 2: Honorific-based detection
        entities.extend(self._detect_with_honorifics(text))
        
        # Method 3: Database matching
        entities.extend(self._detect_from_database(text))
        
        # Method 4: Full name pattern (İki büyük harfle başlayan kelime yan yana)
        entities.extend(self._detect_full_names(text))
        
        return self._remove_duplicates(entities)
    
    def _detect_with_strong_context(self, text: str) -> List[DetectedEntity]:
        """Güçlü context pattern'leri ile isim tespiti - Veritabanına bakmadan yakalar"""
        entities = []
        
        for pattern, entity_type in self.strong_context_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                full_match = match.group(0)
                
                # İsim/soyisim kısımlarını al
                groups = [g for g in match.groups() if g]
                
                if groups:
                    first_part = groups[0].lower()
                    
                    # Common word kontrolü
                    if first_part in self.common_words:
                        continue
                    
                    # Çok kısa kelimeler (2 harf ve altı) atla
                    if len(first_part) < 3:
                        continue
                    
                    entities.append(DetectedEntity(
                        entity_type=entity_type,
                        value=full_match,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.95,
                        context="strong_context"
                    ))
        
        return entities
    
    def _detect_with_honorifics(self, text: str) -> List[DetectedEntity]:
        """Unvan tabanlı isim tespiti (Bey, Hanım, Dr., Prof.)"""
        entities = []
        
        # "Ahmet Bey", "Fatma Hanım" formatı
        honorific_after_pattern = r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s+(bey|hanım|efendi|beyefendi|hanımefendi)\b'
        
        for match in re.finditer(honorific_after_pattern, text, re.IGNORECASE):
            name = match.group(1).lower()
            if name not in self.common_words and len(name) >= 3:
                entities.append(DetectedEntity(
                    entity_type=EntityType.NAME,
                    value=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.95,
                    context="honorific_after"
                ))
        
        return entities
    
    def _detect_from_database(self, text: str) -> List[DetectedEntity]:
        """Veritabanı eşleştirmesi ile isim tespiti"""
        entities = []
        
        # Kelimeleri tokenize et
        word_pattern = r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\b'
        
        words_with_pos = [(m.group(1), m.start(), m.end()) for m in re.finditer(word_pattern, text)]
        
        for i, (word, start, end) in enumerate(words_with_pos):
            word_lower = self._turkish_lower(word)
            
            # Common word kontrolü - Türkçe aware
            if word_lower in self.common_words_lower or word in self.common_words:
                continue
            
            # Çok kısa kelimeler atla
            if len(word_lower) < 3:
                continue
            
            # İsim mi kontrol et
            is_first_name = word_lower in self.first_names
            is_surname = word_lower in self.surnames
            
            if is_first_name:
                # Sonraki kelime soyisim olabilir mi?
                if i + 1 < len(words_with_pos):
                    next_word, next_start, next_end = words_with_pos[i + 1]
                    next_word_lower = next_word.lower()
                    
                    # Arada boşluk kontrolü (max 2 karakter mesafe)
                    if next_start - end <= 2 and next_word_lower not in self.common_words:
                        if next_word_lower in self.surnames or len(next_word_lower) >= 3:
                            # Full name bulundu
                            full_name = text[start:next_end]
                            entities.append(DetectedEntity(
                                entity_type=EntityType.FULL_NAME,
                                value=full_name,
                                start_pos=start,
                                end_pos=next_end,
                                confidence=0.90,
                                context="database_match"
                            ))
                            continue
                
                # Sadece isim
                entities.append(DetectedEntity(
                    entity_type=EntityType.NAME,
                    value=word,
                    start_pos=start,
                    end_pos=end,
                    confidence=0.80,
                    context="database_match"
                ))
            
            elif is_surname:
                entities.append(DetectedEntity(
                    entity_type=EntityType.SURNAME,
                    value=word,
                    start_pos=start,
                    end_pos=end,
                    confidence=0.70,
                    context="database_surname"
                ))
        
        return entities
    
    def _detect_full_names(self, text: str) -> List[DetectedEntity]:
        """İki büyük harfle başlayan kelime yan yana (potansiyel full name)"""
        entities = []
        
        # İki kelime yan yana, ikisi de büyük harfle başlıyor
        pattern = r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\b'
        
        for match in re.finditer(pattern, text):
            first_word = self._turkish_lower(match.group(1))
            second_word = self._turkish_lower(match.group(2))
            
            # Her iki kelime de common word değilse ve yeterli uzunlukta - Türkçe aware
            if first_word in self.common_words_lower or second_word in self.common_words_lower:
                continue
            if match.group(1) in self.common_words or match.group(2) in self.common_words:
                continue
            
            if len(first_word) < 3 or len(second_word) < 3:
                continue
            
            # En az biri veritabanında olmalı VEYA her ikisi de 4+ karakter
            first_known = first_word in self.first_names or first_word in self.surnames
            second_known = second_word in self.first_names or second_word in self.surnames
            both_long = len(first_word) >= 4 and len(second_word) >= 4
            
            if first_known or second_known or both_long:
                # Bağlam kontrolü - cümle başı mı?
                before_text = text[:match.start()].strip()
                is_sentence_start = len(before_text) == 0 or before_text[-1] in '.!?:,'
                
                # Cümle başında olmayan iki büyük harfli kelime muhtemelen isim
                confidence = 0.60
                if first_known and second_known:
                    confidence = 0.90
                elif first_known or second_known:
                    confidence = 0.75
                elif not is_sentence_start:
                    confidence = 0.65
                
                if confidence >= 0.60:
                    entities.append(DetectedEntity(
                        entity_type=EntityType.FULL_NAME,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=confidence,
                        context="capitalized_pair"
                    ))
        
        return entities
    
    def _remove_duplicates(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Çakışan entity'leri kaldır, en iyi olanı tut"""
        if not entities:
            return entities
        
        # Confidence ve uzunluğa göre sırala
        entities.sort(key=lambda e: (e.start_pos, -e.confidence, -len(e.value)))
        
        result = []
        for entity in entities:
            overlaps_with_better = False
            
            for i, existing in enumerate(result):
                # Çakışma kontrolü
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    
                    # FULL_NAME, NAME'den öncelikli
                    if existing.entity_type == EntityType.FULL_NAME:
                        overlaps_with_better = True
                        break
                    elif entity.entity_type == EntityType.FULL_NAME:
                        # Mevcut olanı değiştir
                        result[i] = entity
                        overlaps_with_better = True
                        break
                    else:
                        # Aynı tip, confidence'a göre
                        if existing.confidence >= entity.confidence:
                            overlaps_with_better = True
                            break
                        else:
                            result[i] = entity
                            overlaps_with_better = True
                            break
            
            if not overlaps_with_better:
                result.append(entity)
        
        return result

    def _turkish_lower(self, text: str) -> str:
        """Türkçe karakterleri doğru şekilde lowercase yapar"""
        # Türkçe özel karakterler
        replacements = {
            'İ': 'i',
            'I': 'ı',
            'Ğ': 'ğ',
            'Ü': 'ü',
            'Ş': 'ş',
            'Ö': 'ö',
            'Ç': 'ç',
        }
        result = str(text)
        for upper, lower in replacements.items():
            result = result.replace(upper, lower)
        return result.lower()
