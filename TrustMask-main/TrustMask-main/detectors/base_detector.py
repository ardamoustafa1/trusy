

from abc import ABC, abstractmethod
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities import DetectedEntity


class BaseDetector(ABC):
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def detect(self, text: str) -> List[DetectedEntity]:
        pass
    
    def preprocess(self, text: str) -> str:
        """Metin ön işleme (opsiyonel override)"""
        return text
    
    def validate(self, value: str) -> bool:
        """Tespit edilen değeri doğrula (opsiyonel override)"""
        return True
    
    def normalize(self, value: str) -> str:
        """Değeri normalize et (opsiyonel override)"""
        return value.strip()
