import sqlite3
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

# --- DEĞİŞİKLİK 1: Projenin ana klasör yolunu (PythonProjem) dinamik olarak buluyoruz ---
# Bu sayede komutu nereden çalıştırdığımızın bir önemi kalmıyor.
BASE_DIR = Path(__file__).resolve().parent.parent
# --------------------------------------------------------------------------------------

class DatabaseManager:
    # --- DEĞİŞİKLİK 2: __init__ fonksiyonunu doğru şekilde yeniden yazıyoruz ---
    def __init__(self, db_path='data/database.db'):
        # 1. Adım: Veritabanı yolunu, projenin ana klasörünü baz alarak oluştur.
        # Sonuç: C:\Users\KullaniciAdiniz\Desktop\PythonProjem\data\database.db
        self.db_path = BASE_DIR / db_path
        
        # 2. Adım: Veritabanına bağlanmadan ÖNCE, içinde bulunduğu 'data' klasörünün
        # var olduğundan emin ol. Yoksa oluştur.
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 3. Adım: Artık klasör var olduğuna göre veritabanını başlat.
        self.init_database()
    # -------------------------------------------------------------------------
    
    def get_connection(self):
        """SQLite bağlantısı al"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Dict-like access
        return conn
    
    def init_database(self):
        """Veritabanını başlat ve tabloları oluştur"""
        with self.get_connection() as conn:
            # Users tablosu
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Projects tablosu
            conn.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT DEFAULT 'python',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Files tablosu
            conn.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    project_id TEXT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    content TEXT DEFAULT '',
                    parent_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    FOREIGN KEY (parent_id) REFERENCES files(id)
                )
            ''')
            
            # İndeksler (Performans için kritik!)
            conn.execute('CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_files_parent_id ON files(parent_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)')
            
            conn.commit()
    
    # USER İŞLEMLERİ
    def create_user(self, user_data):
        """Yeni kullanıcı oluştur"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO users (id, username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data['username'],
                user_data['email'],
                user_data['password'],
                user_data['created_at']
            ))
            conn.commit()
    
    def get_user_by_username(self, username):
        """Kullanıcıyı username ile bul"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM users WHERE username = ?', 
                (username,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_by_id(self, user_id):
        """Kullanıcıyı ID ile bul"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM users WHERE id = ?', 
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def check_username_exists(self, username):
        """Username var mı kontrol et"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT COUNT(*) FROM users WHERE username = ?', 
                (username,)
            )
            return cursor.fetchone()[0] > 0
    
    def check_email_exists(self, email):
        """Email var mı kontrol et"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT COUNT(*) FROM users WHERE email = ?', 
                (email,)
            )
            return cursor.fetchone()[0] > 0
    
    # PROJECT İŞLEMLERİ
    def create_project(self, project_data):
        """Yeni proje oluştur"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO projects (id, user_id, name, type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                project_data['id'],
                project_data['user_id'],
                project_data['name'],
                project_data.get('type', 'python'),
                project_data['created_at'],
                project_data['updated_at']
            ))
            conn.commit()
    
    def get_user_projects(self, user_id):
        """Kullanıcının projelerini getir"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM projects 
                WHERE user_id = ? 
                ORDER BY updated_at DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_project(self, project_id):
        """Projeyi sil (CASCADE)"""
        with self.get_connection() as conn:
            # Önce projedeki dosyaları sil
            conn.execute('DELETE FROM files WHERE project_id = ?', (project_id,))
            # Sonra projeyi sil
            conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
            conn.commit()
    
    # FILE İŞLEMLERİ
    def create_file(self, file_data):
        """Yeni dosya oluştur"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO files (id, user_id, project_id, name, type, path, content, parent_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_data['id'],
                file_data['user_id'],
                file_data.get('project_id'),
                file_data['name'],
                file_data['type'],
                file_data['path'],
                file_data.get('content', ''),
                file_data.get('parent_id'),
                file_data['created_at'],
                file_data['updated_at']
            ))
            conn.commit()
    
    def get_user_files(self, user_id):
        """Kullanıcının tüm dosyalarını getir"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM files 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_project_files(self, project_id):
        """Projedeki dosyaları getir"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM files 
                WHERE project_id = ? 
                ORDER BY type DESC, name ASC
            ''', (project_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_file_by_id(self, file_id):
        """Dosyayı ID ile getir"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM files WHERE id = ?', 
                (file_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_file_content(self, file_id, content):
        """Dosya içeriğini güncelle"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE files 
                SET content = ?, updated_at = ? 
                WHERE id = ?
            ''', (content, datetime.now().isoformat(), file_id))
            conn.commit()
    
    def rename_file(self, file_id, new_name):
        """Dosya adını değiştir"""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE files 
                SET name = ?, updated_at = ? 
                WHERE id = ?
            ''', (new_name, datetime.now().isoformat(), file_id))
            conn.commit()
    
    def delete_file(self, file_id):
        """Dosyayı sil (recursive)"""
        with self.get_connection() as conn:
            # Önce alt dosyaları sil (recursive)
            cursor = conn.execute('SELECT id FROM files WHERE parent_id = ?', (file_id,))
            child_ids = [row[0] for row in cursor.fetchall()]
            
            for child_id in child_ids:
                self.delete_file(child_id)  # Recursive delete
            
            # Sonra dosyayı kendisini sil
            conn.execute('DELETE FROM files WHERE id = ?', (file_id,))
            conn.commit()
    
    # MIGRATION İŞLEMLERİ
    def migrate_from_json(self, json_data_dir='data'):
        """JSON verilerini SQLite'a aktar"""
        print("🔄 JSON'dan SQLite'a migration başlıyor...")
        
        # Users migration
        users_file = Path(json_data_dir) / 'users' / 'users.json'
        if users_file.exists():
            with open(users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            for user_id, user_data in users_data.items():
                try:
                    self.create_user({
                        'id': user_id,
                        'username': user_data['username'],
                        'email': user_data['email'],
                        'password': user_data['password'],
                        'created_at': user_data['created_at']
                    })
                    print(f"✅ User migrated: {user_data['username']}")
                except Exception as e:
                    print(f"❌ User migration error: {e}")
        
        # Files migration
        files_dir = Path(json_data_dir) / 'files'
        if files_dir.exists():
            for user_dir in files_dir.iterdir():
                if user_dir.is_dir():
                    user_id = user_dir.name
                    files_index = user_dir / 'files.json'
                    
                    if files_index.exists():
                        with open(files_index, 'r', encoding='utf-8') as f:
                            files_data = json.load(f)
                        
                        for file_info in files_data.get('files', []):
                            try:
                                self.create_file({
                                    'id': file_info['id'],
                                    'user_id': user_id,
                                    'project_id': file_info.get('parent_id') if file_info.get('type') == 'file' else None,
                                    'name': file_info['name'],
                                    'type': file_info['type'],
                                    'path': file_info['path'],
                                    'content': '',  # İçerik dosyadan okunacak
                                    'parent_id': file_info.get('parent_id'),
                                    'created_at': file_info['created_at'],
                                    'updated_at': file_info.get('updated_at', file_info['created_at'])
                                })
                                
                                # Proje tipindeyse projects tablosuna da ekle
                                if file_info.get('type') == 'project':
                                    self.create_project({
                                        'id': file_info['id'],
                                        'user_id': user_id,
                                        'name': file_info['name'],
                                        'type': 'python',
                                        'created_at': file_info['created_at'],
                                        'updated_at': file_info.get('updated_at', file_info['created_at'])
                                    })
                                
                                print(f"✅ File migrated: {file_info['name']}")
                            except Exception as e:
                                print(f"❌ File migration error: {e}")
        
        print("🎉 Migration tamamlandı!")

# Global instance
db = DatabaseManager()