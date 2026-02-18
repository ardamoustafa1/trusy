# -*- coding: utf-8 -*-
"""
Production Server Başlatıcı
Bu script projeyi 'Waitress' WSGI sunucusu ile yüksek performansta çalıştırır.
"""
from waitress import serve
from api import app
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProductionServer")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 KVKK GUARD AI - PRODUCTION SERVER")
    print("="*50)
    print("✅ Durum: Yüksek Performans Modu (WSGI)")
    print("📡 Adres: http://localhost:5001")
    print("💾 Model: Türkçe BERT (Lazy Load)")
    print("⚙️  Thread Sayısı: 8 (Eşzamanlı İşlem)")
    print("="*50 + "\n")
    
    # Waitress ile servisi başlat
    # host='0.0.0.0' -> Ağdaki diğer bilgisayarlardan erişilebilir
    # threads=8 -> Aynı anda 8 işlem yapabilir
    serve(app, host='0.0.0.0', port=5001, threads=8)
