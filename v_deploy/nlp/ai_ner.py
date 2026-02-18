import logging
import requests
import time
from typing import List, Dict, Any

from config import EntityType
from entities import DetectedEntity

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AINERDetector")

class AINERDetector:
    """
    BERT tabanlı Named Entity Recognition (NER) dedektörü.
    Hugging Face Inference API kullanarak "Serverless" çalışır.
    Bu sayede Vercel'e yüklenirken devasa boyut sorunu oluşmaz.
    """
    
    _instance = None
    # Public API URL for the exact same model
    _api_url = "https://api-inference.huggingface.co/models/savasy/bert-base-turkish-ner-cased"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AINERDetector, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        self.initialized = True
        logger.info("AINERDetector (Cloud Mode) hazırlandı.")

    def detect(self, text: str) -> List[DetectedEntity]:
        """Metin içindeki varlıkları Cloud AI ile tespit eder"""
        if not text or len(text.strip()) < 2:
            return []
            
        entities = []
        try:
            # API'ye istek at
            payload = {"inputs": text}
            response = self._query_api(payload)
            
            if isinstance(response, list) and len(response) > 0:
                # Bazen liste içinde liste dönebilir
                if isinstance(response[0], list):
                    response = response[0]
                    
                for res in response:
                    # API yanıt formatı: {'entity_group': 'PER', 'score': 0.99, 'word': 'Mustafa', 'start': 0, 'end': 7}
                    # Bazen entity_group yerine entity gelebilir
                    label = res.get('entity_group', res.get('entity', ''))
                    
                    entity_type = self._map_entity_type(label)
                    if not entity_type:
                        continue
                        
                    entities.append(DetectedEntity(
                        entity_type=entity_type,
                        value=res.get('word', text[res['start']:res['end']]),
                        start_pos=res['start'],
                        end_pos=res['end'],
                        confidence=float(res['score']),
                        context="ai_cloud_bert"
                    ))
            elif isinstance(response, dict) and 'error' in response:
                logger.warning(f"AI API Hatası: {response['error']}")
                
        except Exception as e:
            logger.error(f"Cloud AI analizi sırasında hata: {str(e)}")
            
        return entities

    def _query_api(self, payload: Dict, retries: int = 3) -> Any:
        """Hugging Face API'ye istek atar (Retry mekanizmalı)"""
        for i in range(retries):
            try:
                response = requests.post(self._api_url, json=payload)
                
                # Model yükleniyorsa bekle (503 Service Unavailable)
                if response.status_code == 503:
                    estimated_time = response.json().get('estimated_time', 10)
                    logger.info(f"Model uykuda, uyanması bekleniyor... ({estimated_time:.1f}s)")
                    time.sleep(min(estimated_time, 20)) # Max 20s bekle
                    continue
                    
                if response.status_code == 200:
                    return response.json()
                
                logger.warning(f"API Yanıtı: {response.status_code} - {response.text}")
                
            except Exception as e:
                logger.error(f"API İstek Hatası ({i+1}/{retries}): {e}")
                time.sleep(1)
                
        return []

    def _map_entity_type(self, group: str) -> EntityType:
        """Model çıktılarını projenin EntityType enumına map eder"""
        group = group.upper()
        
        if 'PER' in group:
            return EntityType.NAME
        elif 'LOC' in group:
            return EntityType.ADDRESS
        elif 'ORG' in group:
            return EntityType.NAME 
        
        return None
