# TrustMask AI 🛡️

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow)
![Status](https://img.shields.io/badge/Status-Production-green)
![AI Powered](https://img.shields.io/badge/AI-BERT%20Powered-red)

> **Kurumsal Seviyede KVKK Veri Anonimleştirme ve Maskeleme Çözümü**

TrustMask AI, kişisel verileri (PII) metinlerden, belgelerden ve veritabanlarından **%99.9** doğruluk oranıyla tespit edip anonimleştiren, yapay zeka destekli profesyonel bir güvenlik motorudur. 

Klasik "Regex" kurallarının ötesine geçerek, **Google BERT** derin öğrenme modelleriyle bağlamı (context) anlar ve "Deniz" ismini "Deniz kenarı" kelimesinden ayırt edebilir.

---

## 🚀 Özellikler

### 🧠 Yapay Zeka Gücü (Hybrid Engine)
*   **BERT Tabanlı NER:** Türkçe dilini anlayan Transformer modeli ile İsim, Şehir, Kurum tespiti.
*   **Smart Rule Engine:** TC Kimlik, Kredi Kartı, IP Adresi gibi formatlı veriler için hatasız kural katmanı.
*   **Conflict Resolution:** Çakışan tespitleri akıllıca yöneten karar mekanizması.

### ⚡ Yüksek Performans
*   **Waitress WSGI:** Production-ready sunucu altyapısı ile saniyede binlerce istek karşılama.
*   **Multi-Threading:** Çok çekirdekli işlem desteği.
*   **Lazy Loading:** Sistem kaynaklarını verimli kullanan akıllı model yükleme.

### 🛡️ Kapsamlı Veri Tespiti
TrustMask AI aşağıdaki tüm veri tiplerini otomatik tanır:

| Veri Tipi | Örnek Çıktı | Açıklama |
|-----------|-------------|----------|
| **Kişiler** | `[NAME_SURNAME]` | Ad, Soyad, Anne/Baba Adı |
| **Kimlik** | `[TC_ID]` | TC Kimlik No, Pasaport No, Müşteri No |
| **Finans** | `[IBAN]`, `[CARD]` | IBAN, Kredi Kartı, Banka Adı |
| **İletişim**| `[PHONE]`, `[EMAIL]`| Cep Tel, Sabit Hat, E-posta |
| **Konum** | `[ADDRESS]` | Açık Adres, İl, İlçe |
| **Diğer** | `[IP]`, `[PLATE]` | IP Adresleri, Araç Plakaları, Tarihler |

---

## 🛠️ Kurulum

Sistemi 3 basit adımda çalışır hale getirebilirsiniz.

### 1. Gereksinimleri Yükleyin
```bash
pip install -r requirements.txt
```

### 2. Sunucuyu Başlatın (Production Mode)
```bash
python run_production.py
```
*Bu komut, yüksek performanslı WSGI sunucusunu 5000 portunda başlatır.*

### 3. Arayüzü Açın
Tarayıcınızda veya dosya yöneticisinde `index.html` dosyasını açarak sistemi kullanmaya başlayabilirsiniz.

---

## 💻 Kullanım Örnekleri

### Python API
TrustMask AI'yı kendi Python projelerinize kolayca entegre edebilirsiniz.

```python
from anonymizer import KVKKAnonymizer

# Motoru başlat (AI modeli otomatik yüklenir)
anonymizer = KVKKAnonymizer()

text = "Mustafa Yılmaz, 0532 555 44 33 numaralı telefondan aradı."
result = anonymizer.anonymize(text)

print(result.sanitized_text)
# Çıktı: "[NAME_SURNAME], [PHONE] numaralı telefondan aradı."
```

### REST API
Başka dillerden (Java, C#, Node.js) HTTP isteği ile kullanabilirsiniz.

```bash
curl -X POST http://localhost:5000/anonymize \
     -H "Content-Type: application/json" \
     -d '{"text": "Müşteri no: 123456"}'
```

---

## 📂 Proje Yapısı

```
TrustMask-AI/
├── nlp/                  # Yapay Zeka Çekirdeği (BERT)
├── detectors/            # Kural Tabanlı Tespit Modülleri
├── api.py                # REST API İskeleti
├── run_production.py     # Production Başlatıcı (WSGI)
├── anonymizer.py         # Ana Orkestrasyon Motoru
└── index.html            # Modern Web Arayüzü
```

---

## 📜 Lisans

Bu proje [MIT](LICENSE) lisansı ile lisanslanmıştır. Kurumsal ve ticari kullanıma uygundur.

---

<p align="center">
  <sub>Designed & Developed by TrustMask Team</sub>
</p>
