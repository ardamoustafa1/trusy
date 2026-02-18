"""
NLP Modülü - Türk İsim ve Soyisim Tespiti
"""

from nlp.name_detector import NameDetector
from nlp.turkish_names_db import TURKISH_FIRST_NAMES, TURKISH_SURNAMES, HONORIFICS

__all__ = [
    'NameDetector',
    'TURKISH_FIRST_NAMES',
    'TURKISH_SURNAMES', 
    'HONORIFICS',
]
