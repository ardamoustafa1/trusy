"""
KVKK Veri Anonimleştirme - Detector Modülleri - TAM LİSTE
"""

from detectors.base_detector import BaseDetector
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

__all__ = [
    'BaseDetector',
    'TCKimlikDetector',
    'PhoneDetector',
    'EmailDetector',
    'IBANDetector',
    'CreditCardDetector',
    'AddressDetector',
    'PlateDetector',
    'DateDetector',
    'IPDetector',
    'CustomerIDDetector',
    'PartialDataDetector',
    'GenderDetector',
    'ParentNameDetector',
    'BankNameDetector',
    'CallRecordDetector',
]
