"""
KVKK Veri Anonimleştirme - Entity Tanımları
"""

from dataclasses import dataclass
from typing import Optional
from config import EntityType


@dataclass
class DetectedEntity:
    """Tespit edilen kişisel veri entity'si"""
    entity_type: EntityType
    value: str
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    context: Optional[str] = None
    
    def __repr__(self):
        return f"DetectedEntity({self.entity_type.value}: '{self.value}' [{self.start_pos}:{self.end_pos}])"
    
    def __hash__(self):
        return hash((self.entity_type, self.start_pos, self.end_pos))
    
    def __eq__(self, other):
        if not isinstance(other, DetectedEntity):
            return False
        return (self.entity_type == other.entity_type and 
                self.start_pos == other.start_pos and 
                self.end_pos == other.end_pos)
    
    @property
    def length(self) -> int:
        return self.end_pos - self.start_pos


@dataclass
class AnonymizationResult:
    """Anonimleştirme sonucu"""
    is_personal_data_detected: bool
    detected_data_types: list
    sanitized_text: str
    entities: list = None
    
    def to_dict(self) -> dict:
        return {
            "is_personal_data_detected": self.is_personal_data_detected,
            "detected_data_types": self.detected_data_types,
            "sanitized_text": self.sanitized_text
        }
