

from typing import List, Dict, Set
import json
import sys
import os

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities import DetectedEntity, AnonymizationResult
from config import EntityType, PLACEHOLDERS

# Detector'ları import et
from detectors.tc_kimlik_detector import TCKimlikDetector
from detectors.phone_detector import PhoneDetector
from detectors.email_detector import EmailDetector
from detectors.iban_detector import IBANDetector
from detectors.credit_card_detector import CreditCardDetector
from detectors.address_detector import AddressDetector
from detectors.plate_detector import PlateDetector
from detectors.date_detector import DateDetector
from detectors.ip_detector import IPDetector
from detectors.customer_id_detector import CustomerIDDetector
from detectors.partial_data_detector import PartialDataDetector
from detectors.extra_detectors import (
    GenderDetector,
    ParentNameDetector,
    BankNameDetector,
    CallRecordDetector,
)

# NLP detector
from nlp.name_detector import NameDetector
from nlp.ai_ner import AINERDetector


class KVKKAnonymizer:
    
    def __init__(self, enable_name_detection: bool = True):
        """
        Args:
            enable_name_detection: NLP tabanlı isim tespitini etkinleştir
        """
        self.detectors = []
        
        # Kimlik detector'ları
        self.detectors.append(TCKimlikDetector())
        
        # İletişim detector'ları
        self.detectors.append(PhoneDetector())
        self.detectors.append(EmailDetector())
        
        # Finansal detector'lar
        self.detectors.append(IBANDetector())
        self.detectors.append(CreditCardDetector())
        self.detectors.append(BankNameDetector())
        
        # Adres detector'ları
        self.detectors.append(AddressDetector())
        
        # Tarih detector'ları
        self.detectors.append(DateDetector())
        
        # Müşteri ID detector'ları
        self.detectors.append(CustomerIDDetector())
        
        # Kısmi veri detector (doğrulama soruları için)
        self.detectors.append(PartialDataDetector())
        
        # Ek detector'lar
        self.detectors.append(PlateDetector())
        self.detectors.append(IPDetector())
        self.detectors.append(GenderDetector())
        self.detectors.append(ParentNameDetector())
        self.detectors.append(CallRecordDetector())
        
        # NLP tabanlı isim detector (en son, çakışmaları önlemek için)
        if enable_name_detection:
            self.detectors.append(NameDetector())
            # AI NER Detector (BERT) - En akıllı dedektör
            self.detectors.append(AINERDetector())
        
        self.placeholders = PLACEHOLDERS
    
    def anonymize(self, text: str, min_confidence: float = 0.5) -> AnonymizationResult:
        """
        Metni analiz edip kişisel verileri anonimleştirir
        
        Args:
            text: Anonimleştirilecek metin
            min_confidence: Minimum güven eşiği (0-1)
            
        Returns:
            AnonymizationResult: Anonimleştirme sonucu
        """
        if not text or not text.strip():
            return AnonymizationResult(
                is_personal_data_detected=False,
                detected_data_types=[],
                sanitized_text=text,
                entities=[]
            )
        
        # Tüm detector'ları çalıştır
        all_entities = []
        for detector in self.detectors:
            try:
                entities = detector.detect(text)
                all_entities.extend(entities)
            except Exception as e:
                # Hata durumunda devam et
                print(f"Warning: {detector.name} failed: {e}")
                continue
        
        # Minimum confidence filtresi
        filtered_entities = [e for e in all_entities if e.confidence >= min_confidence]
        
        # Çakışan entity'leri çöz
        resolved_entities = self._resolve_overlaps(filtered_entities)
        
        # Metni anonimleştir
        sanitized_text = self._apply_anonymization(text, resolved_entities)
        
        # Tespit edilen veri tiplerini çıkar
        detected_types = list(set(e.entity_type.value for e in resolved_entities))
        detected_types.sort()
        
        return AnonymizationResult(
            is_personal_data_detected=len(resolved_entities) > 0,
            detected_data_types=detected_types,
            sanitized_text=sanitized_text,
            entities=resolved_entities
        )
    
    def _resolve_overlaps(self, entities: List[DetectedEntity]) -> List[DetectedEntity]:
        """Çakışan entity'leri çöz"""
        if not entities:
            return []
        
        # Öncelik sırası (düşük değer = yüksek öncelik)
        priority_order = {
            EntityType.TC_ID: 1,
            EntityType.PHONE: 2,
            EntityType.MOBILE_PHONE: 2,
            EntityType.LANDLINE: 2,
            EntityType.EMAIL: 3,
            # Specific IDs should be high priority to avoid being caught as Address/Number
            EntityType.CUSTOMER_ID: 4,
            EntityType.SUBSCRIPTION_ID: 4,
            EntityType.CONTRACT_ID: 4,
            EntityType.CALL_RECORD_ID: 4,
            
            EntityType.BANK_INFO: 5,
            EntityType.CARD_INFO: 6,
            EntityType.FULL_NAME: 7,
            EntityType.NAME: 8,
            EntityType.SURNAME: 9,
            EntityType.PARENT_NAME: 9,
            EntityType.HOME_ADDRESS: 10,
            EntityType.WORK_ADDRESS: 10,
            EntityType.ADDRESS: 11,
            EntityType.CITY_DISTRICT: 12,
            EntityType.PLATE: 13,
            EntityType.BIRTH_DATE: 14,
            EntityType.BIRTH_YEAR: 14,
            EntityType.IP_ADDRESS: 15,
            EntityType.GENDER: 16,
            EntityType.BANK_NAME: 17,
        }
        
        def entity_key(e: DetectedEntity):
            prio = priority_order.get(e.entity_type, 99)
            return (e.start_pos, -len(e.value), -e.confidence, prio)
        
        sorted_entities = sorted(entities, key=entity_key)
        
        result = []
        used_ranges = []
        
        for entity in sorted_entities:
            overlap = False
            for (start, end) in used_ranges:
                if entity.start_pos < end and entity.end_pos > start:
                    overlap = True
                    break
            
            if not overlap:
                result.append(entity)
                used_ranges.append((entity.start_pos, entity.end_pos))
        
        return result
    
    def _apply_anonymization(self, text: str, entities: List[DetectedEntity]) -> str:
        """Tespit edilen entity'leri placeholder'larla değiştir"""
        if not entities:
            return text
        
        sorted_entities = sorted(entities, key=lambda e: e.start_pos, reverse=True)
        
        result = text
        for entity in sorted_entities:
            placeholder = self.placeholders.get(entity.entity_type, "[FİLTRELENDİ]")
            result = result[:entity.start_pos] + placeholder + result[entity.end_pos:]
        
        return result
    
    def get_statistics(self, text: str) -> Dict:
        """Metin hakkında istatistik bilgileri döndür"""
        result = self.anonymize(text)
        
        stats = {
            "total_entities": len(result.entities) if result.entities else 0,
            "entity_types": {},
            "text_length": len(text),
            "sanitized_length": len(result.sanitized_text),
            "reduction_ratio": 0
        }
        
        if result.entities:
            for entity in result.entities:
                type_name = entity.entity_type.value
                if type_name not in stats["entity_types"]:
                    stats["entity_types"][type_name] = 0
                stats["entity_types"][type_name] += 1
        
        if len(text) > 0:
            stats["reduction_ratio"] = 1 - (len(result.sanitized_text) / len(text))
        
        return stats


def anonymize_text(text: str, min_confidence: float = 0.5) -> dict:
    """Basit fonksiyon arayüzü"""
    anonymizer = KVKKAnonymizer()
    result = anonymizer.anonymize(text, min_confidence)
    return result.to_dict()


if __name__ == "__main__":
    test_texts = [
        "Merhaba, ben Ahmet Yılmaz. TC kimlik numaram 32303010429.",
        "Telefon numaram 0532 123 45 67, mail adresim ahmet@gmail.com",
        "IBAN: TR330006100519786457841326, Bankam Garanti",
        "Plakam 34 ABC 123, doğum tarihim 32/13/2004",
        "Anne kızlık soyadı Küçükberber, cinsiyetim erkek",
        "Ev adresim: Kadıköy Mahallesi Atatürk Caddesi No:15 İstanbul",
        "Müşteri numaram VOD-123456789, çağrı kayıt no: CRM-2024-001",
    ]
    
    anonymizer = KVKKAnonymizer()
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        result = anonymizer.anonymize(text)
        print(f"Sanitized: {result.sanitized_text}")
        print(f"Detected types: {result.detected_data_types}")
