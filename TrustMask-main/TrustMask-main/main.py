#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KVKK Veri Anonimleştirme Sistemi - CLI Arayüzü

Kullanım:
    python main.py --text "Merhaba, ben Ahmet Yılmaz"
    python main.py --file input.txt --output output.txt
    python main.py --interactive
    
    echo "Test metni" | python main.py --stdin
"""

import argparse
import json
import sys
import os

# Path ayarı
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anonymizer import KVKKAnonymizer, anonymize_text


def process_text(text: str, anonymizer: KVKKAnonymizer, format_output: str = "json") -> str:
    """Metni işle ve çıktıyı formatla"""
    result = anonymizer.anonymize(text)
    
    if format_output == "json":
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    elif format_output == "text":
        output = result.sanitized_text
    elif format_output == "detailed":
        lines = [
            f"{'='*60}",
            f"KVKK Anonimleştirme Sonucu",
            f"{'='*60}",
            f"Kişisel Veri Tespit Edildi: {'Evet' if result.is_personal_data_detected else 'Hayır'}",
            f"Tespit Edilen Veri Tipleri: {', '.join(result.detected_data_types) if result.detected_data_types else '-'}",
            f"{'='*60}",
            f"Orijinal Metin:",
            text,
            f"{'='*60}",
            f"Anonimleştirilmiş Metin:",
            result.sanitized_text,
            f"{'='*60}",
        ]
        
        if result.entities:
            lines.append("Tespit Edilen Veriler:")
            for entity in result.entities:
                lines.append(f"  - {entity.entity_type.value}: '{entity.value}' (güven: {entity.confidence:.2f})")
        
        output = "\n".join(lines)
    else:
        output = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
    
    return output


def process_file(input_path: str, output_path: str, anonymizer: KVKKAnonymizer) -> None:
    """Dosya işle"""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    result = anonymizer.anonymize(text)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result.sanitized_text)
    
    print(f"Dosya işlendi: {input_path} -> {output_path}")
    print(f"Tespit edilen veri tipleri: {result.detected_data_types}")


def interactive_mode(anonymizer: KVKKAnonymizer) -> None:
    """Interaktif mod"""
    print("="*60)
    print("KVKK Veri Anonimleştirme Sistemi - Interaktif Mod")
    print("="*60)
    print("Metin girin (çıkmak için 'exit' veya 'q' yazın):")
    print()
    
    while True:
        try:
            text = input(">>> ").strip()
            
            if text.lower() in ['exit', 'q', 'quit', 'çık', 'cik']:
                print("Çıkılıyor...")
                break
            
            if not text:
                continue
            
            result = anonymizer.anonymize(text)
            
            print(f"\n[Sonuç]")
            print(f"Tespit: {'Evet' if result.is_personal_data_detected else 'Hayır'}")
            if result.detected_data_types:
                print(f"Tipler: {', '.join(result.detected_data_types)}")
            print(f"Çıktı: {result.sanitized_text}")
            print()
            
        except KeyboardInterrupt:
            print("\nÇıkılıyor...")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="KVKK Veri Anonimleştirme Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s --text "Merhaba, ben Ahmet Yılmaz. TC: 12345678901"
  %(prog)s --file input.txt --output output.txt
  %(prog)s --interactive
  echo "Test" | %(prog)s --stdin
        """
    )
    
    # Giriş kaynağı
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', '-t', type=str, help='Anonimleştirilecek metin')
    input_group.add_argument('--file', '-f', type=str, help='Giriş dosyası')
    input_group.add_argument('--stdin', action='store_true', help='Stdin\'den oku')
    input_group.add_argument('--interactive', '-i', action='store_true', help='Interaktif mod')
    
    # Çıkış
    parser.add_argument('--output', '-o', type=str, help='Çıkış dosyası (--file ile kullanılır)')
    parser.add_argument('--format', '-F', choices=['json', 'text', 'detailed'], default='json',
                        help='Çıkış formatı (varsayılan: json)')
    
    # Ayarlar
    parser.add_argument('--min-confidence', '-c', type=float, default=0.5,
                        help='Minimum güven eşiği (0-1, varsayılan: 0.5)')
    parser.add_argument('--no-names', action='store_true',
                        help='İsim tespitini devre dışı bırak')
    
    args = parser.parse_args()
    
    # Anonymizer oluştur
    anonymizer = KVKKAnonymizer(enable_name_detection=not args.no_names)
    
    # İşle
    if args.interactive:
        interactive_mode(anonymizer)
    
    elif args.text:
        output = process_text(args.text, anonymizer, args.format)
        print(output)
    
    elif args.file:
        if not args.output:
            args.output = args.file.rsplit('.', 1)[0] + '_anonymized.txt'
        process_file(args.file, args.output, anonymizer)
    
    elif args.stdin:
        text = sys.stdin.read()
        output = process_text(text, anonymizer, args.format)
        print(output)


if __name__ == "__main__":
    main()
