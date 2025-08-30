#!/usr/bin/env python3
"""
JSON verilerini SQLite'a migrate etmek için script
"""

import sys
import os
from pathlib import Path

# Backend dizinini Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db

def main():
    print("🚀 SQLite Migration Başlıyor...")
    print("=" * 50)
    
    # Veritabanını başlat
    print("📋 SQLite veritabanı oluşturuluyor...")
    db.init_database()
    print("✅ Veritabanı hazır!")
    
    # Migration işlemi
    print("\n🔄 JSON verilerini SQLite'a aktarılıyor...")
    try:
        db.migrate_from_json('../data')
        print("\n🎉 Migration başarıyla tamamlandı!")
        
        # İstatistikler
        with db.get_connection() as conn:
            user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
            project_count = conn.execute('SELECT COUNT(*) FROM projects').fetchone()[0]
            file_count = conn.execute('SELECT COUNT(*) FROM files').fetchone()[0]
            
        print(f"\n📊 Migration Sonuçları:")
        print(f"👥 Kullanıcılar: {user_count}")
        print(f"📁 Projeler: {project_count}")
        print(f"📄 Dosyalar: {file_count}")
        
    except Exception as e:
        print(f"❌ Migration hatası: {e}")
        return 1
    
    print(f"\n💾 SQLite veritabanı: {db.db_path}")
    print("🎯 Backend artık SQLite kullanıyor!")
    return 0

if __name__ == '__main__':
    exit(main())
