#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KVKK Veri Anonimleştirme Sistemi - REST API

Flask tabanlı API sunucusu.

Kullanım:
    python api.py
    
Endpoints:
    POST /anonymize - Metin anonimleştir
    GET /health - Sağlık kontrolü
    GET /stats - İstatistikler
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anonymizer import KVKKAnonymizer


app = Flask(__name__)
CORS(app)  # CORS desteği

# Global anonymizer instance
anonymizer = KVKKAnonymizer()


@app.route('/health', methods=['GET'])
def health_check():
    """Sağlık kontrolü endpoint'i"""
    return jsonify({
        "status": "healthy",
        "service": "KVKK Anonymizer API",
        "version": "1.0.0"
    })


@app.route('/anonymize', methods=['POST'])
def anonymize():
    """
    Metin anonimleştirme endpoint'i
    
    Request Body:
        {
            "text": "Anonimleştirilecek metin",
            "min_confidence": 0.5  // Opsiyonel
        }
    
    Response:
        {
            "is_personal_data_detected": true/false,
            "detected_data_types": [...],
            "sanitized_text": "..."
        }
    """
    try:
        # JSON body al
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request body"
            }), 400
        
        text = data['text']
        min_confidence = data.get('min_confidence', 0.5)
        
        if not isinstance(text, str):
            return jsonify({
                "error": "'text' must be a string"
            }), 400
        
        if not isinstance(min_confidence, (int, float)) or not 0 <= min_confidence <= 1:
            return jsonify({
                "error": "'min_confidence' must be a number between 0 and 1"
            }), 400
        
        # Anonimleştir
        result = anonymizer.anonymize(text, min_confidence)
        
        return jsonify(result.to_dict())
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/anonymize/batch', methods=['POST'])
def anonymize_batch():
    """
    Toplu metin anonimleştirme endpoint'i
    
    Request Body:
        {
            "texts": ["metin1", "metin2", ...],
            "min_confidence": 0.5  // Opsiyonel
        }
    
    Response:
        {
            "results": [
                {"is_personal_data_detected": ..., ...},
                ...
            ]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                "error": "Missing 'texts' field in request body"
            }), 400
        
        texts = data['texts']
        min_confidence = data.get('min_confidence', 0.5)
        
        if not isinstance(texts, list):
            return jsonify({
                "error": "'texts' must be an array"
            }), 400
        
        results = []
        for text in texts:
            if isinstance(text, str):
                result = anonymizer.anonymize(text, min_confidence)
                results.append(result.to_dict())
            else:
                results.append({
                    "error": "Invalid text (not a string)",
                    "is_personal_data_detected": False,
                    "detected_data_types": [],
                    "sanitized_text": ""
                })
        
        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/stats', methods=['POST'])
def get_stats():
    """
    Metin istatistikleri endpoint'i
    
    Request Body:
        {
            "text": "Analiz edilecek metin"
        }
    
    Response:
        {
            "total_entities": 5,
            "entity_types": {"NAME": 2, "PHONE": 1, ...},
            "text_length": 100,
            "sanitized_length": 80,
            "reduction_ratio": 0.2
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing 'text' field in request body"
            }), 400
        
        text = data['text']
        stats = anonymizer.get_statistics(text)
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/info', methods=['GET'])
def get_info():
    """API bilgileri"""
    return jsonify({
        "name": "KVKK Veri Anonimleştirme API",
        "version": "1.0.0",
        "description": "Türkçe metin içindeki kişisel verileri tespit edip anonimleştirir",
        "supported_entity_types": [
            "NAME", "SURNAME", "FULL_NAME", "TC_ID", "BIRTH_DATE",
            "PHONE", "EMAIL", "ADDRESS", "PLATE", "BANK_INFO",
            "CARD_INFO", "CUSTOMER_ID", "IP_ADDRESS"
        ],
        "endpoints": {
            "POST /anonymize": "Tek metin anonimleştir",
            "POST /anonymize/batch": "Toplu metin anonimleştir",
            "POST /stats": "Metin istatistikleri",
            "GET /health": "Sağlık kontrolü",
            "GET /info": "API bilgileri"
        }
    })


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="KVKK Anonymizer API Server")
    parser.add_argument('--host', default='0.0.0.0', help='Host adresi (varsayılan: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port numarası (varsayılan: 5000)')
    parser.add_argument('--debug', action='store_true', help='Debug modu')
    
    args = parser.parse_args()
    
    print(f"KVKK Anonymizer API başlatılıyor: http://{args.host}:{args.port}")
    print("Endpoints:")
    print("  POST /anonymize - Metin anonimleştir")
    print("  POST /anonymize/batch - Toplu anonimleştir")
    print("  POST /stats - Metin istatistikleri")
    print("  GET /health - Sağlık kontrolü")
    print("  GET /info - API bilgileri")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
