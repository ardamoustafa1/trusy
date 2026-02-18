import logging
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from typing import List, Dict, Any

from config import EntityType
from entities import DetectedEntity

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AINERDetector")

class AINERDetector:
    """
    BERT tabanlı Named Entity Recognition (NER) dedektörü.
    Hugging Face transformers kütüphanesini kullanır.
    """
    
    _instance = None
    _model_name = "savasy/bert-base-turkish-ner-cased"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AINERDetector, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if self.initialized:
            return
            
        self.nlp_pipeline = None
        self.initialized = True
        logger.info("AINERDetector instance oluşturuldu (Henüz model yüklenmedi - Lazy Loading)")

    def load_model(self):
        """Modeli belleğe yükler"""
        if self.nlp_pipeline is not None:
            return

        try:
            logger.info(f"AI Modeli yükleniyor: {self._model_name}...")
            
            tokenizer = AutoTokenizer.from_pretrained(self._model_name)
            model = AutoModelForTokenClassification.from_pretrained(self._model_name)
            
            # CPU üzerinde çalıştır (GPU varsa cuda:0 yapılabilir ama serverda garanti değil)
            device = 0 if torch.cuda.is_available() else -1
            
            self.nlp_pipeline = pipeline(
                "ner", 
                model=model, 
                tokenizer=tokenizer, 
                aggregation_strategy="simple", # Kelime parçalarını birleştirir (B-PER, I-PER -> PER)
                device=device
            )
            
            logger.info("AI Modeli başarıyla yüklendi!")
            
        except Exception as e:
            logger.error(f"AI Modeli yüklenirken hata oluştu: {str(e)}")
            self.nlp_pipeline = None

    def detect(self, text: str) -> List[DetectedEntity]:
        """Metin içindeki varlıkları AI ile tespit eder"""
        # Model yüklü değilse yükle
        if self.nlp_pipeline is None:
            self.load_model()
            
        if self.nlp_pipeline is None:
            return [] # Model yüklenemediyse boş dön
            
        entities = []
        try:
            results = self.nlp_pipeline(text)
            
            for res in results:
                # Örnek res: {'entity_group': 'PER', 'score': 0.99, 'word': 'Mustafa', 'start': 0, 'end': 7}
                
                entity_type = self._map_entity_type(res['entity_group'])
                if not entity_type:
                    continue
                    
                entities.append(DetectedEntity(
                    entity_type=entity_type,
                    value=res['word'],
                    start_pos=res['start'],
                    end_pos=res['end'],
                    confidence=float(res['score']),
                    context="ai_bert_ner"
                ))
                
        except Exception as e:
            logger.error(f"AI analizi sırasında hata: {str(e)}")
            
        return entities

    def _map_entity_type(self, group: str) -> EntityType:
        """Model çıktılarını projenin EntityType enumına map eder"""
        group = group.upper()
        
        if group == 'PER':
            return EntityType.NAME # veya duruma göre FULL_NAME
        elif group == 'LOC':
            return EntityType.ADDRESS
        elif group == 'ORG':
            return EntityType.NAME # Şirket isimlerini de isim gibi maskeleyebiliriz veya yeni tip açabiliriz
        
        return None
