from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import json
import uuid
import hashlib
import subprocess
import tempfile
import time
import sys
from datetime import datetime
from pathlib import Path
import shutil
from database import db

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Production'da değiştirin
CORS(app, supports_credentials=True)

# Proje dizinleri
BASE_DIR = Path(__file__).parent.parent
USERS_DIR = BASE_DIR / 'data' / 'users'
FILES_DIR = BASE_DIR / 'data' / 'files'
TEMP_DIR = BASE_DIR / 'data' / 'temp'

# Dizinleri oluştur
USERS_DIR.mkdir(parents=True, exist_ok=True)
FILES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# --- YENİ: PROJE ŞABLONLARININ İÇERİKLERİ ---
# Farklı proje tipleri için başlangıç kodlarını burada tanımlıyoruz.
EMPTY_PROJECT_CONTENT = '# {project_name} Projesi\nprint("Merhaba, {project_name}!")\n'

FLASK_SERVER_CONTENT = """
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Merhaba, Flask Sunucusu Çalışıyor!"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
"""

DATA_SCIENCE_CONTENT = """
import numpy as np
import pandas as pd

print(f"NumPy versiyonu: {np.__version__}")
print(f"Pandas versiyonu: {pd.__version__}")

# Örnek bir NumPy dizisi oluşturalım
my_array = np.array([10, 20, 30, 40, 50])
print("\\nNumPy Dizisi:", my_array)
print("Dizinin ortalaması:", np.mean(my_array))

# Örnek bir Pandas DataFrame oluşturalım
data = {'Meyve': ['Elma', 'Muz', 'Çilek'], 'Fiyat': [15, 12, 20]}
df = pd.DataFrame(data)

print("\\nPandas DataFrame:")
print(df)
"""
# ----------------------------------------------------


def hash_password(password):
    """Şifreyi hashle"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_files_dir(user_id):
    """Kullanıcının dosya dizinini al"""
    user_dir = FILES_DIR / user_id
    user_dir.mkdir(exist_ok=True)
    return user_dir

# ... (execute_python_code ve diğer fonksiyonlar değişmeden kalıyor) ...
# execute_python_code fonksiyonu çok uzun olduğu için buraya eklemedim,
# sizdeki versiyonuyla aynı kalacak.
def execute_python_code(code, timeout=30):
    """Python kodunu güvenli şekilde çalıştır"""
    try:
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            # Matplotlib ve OpenCV display ayarları
            setup_code = '''
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Matplotlib interactive backend
try:
    import matplotlib
    matplotlib.use('TkAgg')  # GUI backend for multiple windows
    import matplotlib.pyplot as plt
    plt.ion()  # Interactive mode on
    
    # Her plt.show() çağrısını override et
    _original_show = plt.show
    def custom_show(*args, **kwargs):
        # Non-blocking gösterim
        _original_show(block=False)
        # Pencereyi force açık tut
        import time
        fig = plt.gcf()
        fig.canvas.manager.window.wm_attributes('-topmost', 1)  # En üstte tut
        fig.canvas.manager.window.wm_attributes('-topmost', 0)  # Normal seviyeye al
        time.sleep(0.5)  # Daha uzun bekleme
        print(f"[📊 Grafik penceresi açıldı ve sabitlendi - Figure {fig.number}]")
        # Pencereyi event loop'a bağla
        fig.canvas.start_event_loop(0.01)
    plt.show = custom_show
except Exception as e:
    print(f"Matplotlib setup error: {e}")
    pass

# OpenCV display ayarları
try:
    import cv2
    
    # Her cv2.imshow çağrısı için ayrı pencere
    _original_imshow = cv2.imshow
    _window_count = 0
    def custom_imshow(winname, mat):
        global _window_count
        _window_count += 1
        unique_name = f"{winname}_{_window_count}"
        cv2.namedWindow(unique_name, cv2.WINDOW_NORMAL)
        result = _original_imshow(unique_name, mat)
        print(f"[OpenCV penceresi açıldı: {unique_name}]")
        return result
    cv2.imshow = custom_imshow
    
    # waitKey override - pencereyi uzun süre açık tut
    _original_waitKey = cv2.waitKey
    def custom_waitKey(delay=0):
        # Pencereyi minimum 30 saniye açık tut
        if delay == 0:
            delay = 30000  # 30 saniye
        elif delay < 5000:
            delay = 5000   # Minimum 5 saniye
        print(f"[📷 OpenCV penceresi {delay}ms açık tutulacak]")
        return _original_waitKey(delay)
    cv2.waitKey = custom_waitKey
except:
    pass

# Turtle ekranını açık tutma
try:
    import turtle
    
    # Turtle ekranını override et
    _original_done = turtle.done
    def custom_done():
        print("[🐢 Turtle ekranı açıldı - Kapatmak için ekrana tıklayın]")
        screen = turtle.Screen()
        # Ekranı en üstte tut ve tıklanana kadar bekle
        try:
            screen.getcanvas().winfo_toplevel().wm_attributes('-topmost', 1)
            screen.getcanvas().winfo_toplevel().wm_attributes('-topmost', 0)
        except:
            pass
        screen.exitonclick()  # Tıklanana kadar bekle
        return
    turtle.done = custom_done
    
    # Otomatik turtle.done() ekleme
    import sys
    original_exit = sys.exit
    def custom_exit(*args, **kwargs):
        try:
            # Eğer turtle screen açıksa, bekle
            screen = turtle.Screen()
            print("[🐢 Program bitince Turtle ekranı açık kalacak]")
            screen.exitonclick()
        except:
            pass
        original_exit(*args, **kwargs)
    sys.exit = custom_exit
    
    # Turtle'ın otomatik kapatılmasını engelle
    def keep_turtle_open():
        screen = turtle.Screen()
        screen.mainloop()  # Sürekli açık tut
    
    # Turtle kodunun sonuna otomatik ekleme
    original_tracer = turtle.tracer
    def custom_tracer(*args, **kwargs):
        result = original_tracer(*args, **kwargs)
        # Çizim bittiğinde ekranı açık tut
        return result
    turtle.tracer = custom_tracer
except:
    pass

'''
            temp_file.write(setup_code + code)
            temp_file_path = temp_file.name

        # Kodu çalıştır - Windows'ta encoding sorunlarını çöz
        start_time = time.time()
        
        # Windows için özel encoding ayarı
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',  # Encoding hatalarını atla
            env=env
        )
        execution_time = time.time() - start_time

        # Geçici dosyayı sil
        os.unlink(temp_file_path)

        # Çıktıyı temizle
        output = result.stdout.strip() if result.stdout else ''
        error = result.stderr.strip() if result.stderr else ''
        
        # Uyarıları filtrele
        if error:
            error_lines = error.split('\n')
            filtered_errors = []
            for line in error_lines:
                if not any(skip in line.lower() for skip in ['warning', 'deprecated', 'futurewarning']):
                    filtered_errors.append(line)
            error = '\n'.join(filtered_errors).strip()

        success = result.returncode == 0
        response_data = {
            'success': success,
            'output': output,
            'error': error if error else None,
            'execution_time': execution_time
        }
        
        return response_data

    except subprocess.TimeoutExpired:
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        return {
            'success': False,
            'output': '',
            'error': f'Kod çalıştırma süresi {timeout} saniyeyi aştı',
            'execution_time': timeout
        }
    except Exception as e:
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'execution_time': 0
        }

# --- API Routes ---
# (register, login, logout, me, get_files, create_file ve diğerleri değişmeden kalıyor)
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({
            'success': False,
            'message': 'Tüm alanları doldurun'
        }), 400

    # Kullanıcı zaten var mı kontrol et
    if db.check_username_exists(username):
        return jsonify({
            'success': False,
            'message': 'Bu kullanıcı adı zaten alınmış'
        }), 400

    if db.check_email_exists(email):
        return jsonify({
            'success': False,
            'message': 'Bu e-posta adresi zaten kayıtlı'
        }), 400

    # Yeni kullanıcı oluştur
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'username': username,
        'email': email,
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }

    try:
        db.create_user(user_data)
        get_user_files_dir(user_id)  # Kullanıcı dizini oluştur

        # Oturum başlat
        session['user_id'] = user_id

        return jsonify({
            'success': True,
            'data': {
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'created_at': user_data['created_at']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Kullanıcı oluşturulamadı'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({
            'success': False,
            'message': 'Kullanıcı adı ve şifre gerekli'
        }), 400

    # Kullanıcıyı bul
    user = db.get_user_by_username(username)
    
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({
            'success': False,
            'message': 'Geçersiz kullanıcı adı veya şifre'
        }), 401

    # Oturum başlat
    session['user_id'] = user['id']

    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Oturum açılmamış'
        }), 401

    user = db.get_user_by_id(user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'Kullanıcı bulunamadı'
        }), 404

    return jsonify({
        'success': True,
        'data': {
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        }
    })

@app.route('/api/files', methods=['GET'])
def get_files():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    try:
        files = db.get_user_files(user_id)
        return jsonify({
            'success': True,
            'data': {'files': files}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Dosyalar yüklenemedi'
        }), 500

@app.route('/api/files', methods=['POST'])
def create_file():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    data = request.get_json()
    name = data.get('name')
    file_type = data.get('type', 'file')
    content = data.get('content', '')
    parent_id = data.get('parent_id')

    if not name:
        return jsonify({'success': False, 'message': 'Dosya adı gerekli'}), 400

    # Yeni dosya bilgisi
    file_id = str(uuid.uuid4())
    
    # Path oluştur
    if parent_id:
        parent = db.get_file_by_id(parent_id)
        if parent:
            file_path = f"{parent['path']}/{name}"
        else:
            file_path = name
    else:
        file_path = name
    
    # project_id'yi düzgün hesapla
    project_id = None
    if parent_id:
        parent = db.get_file_by_id(parent_id)
        if parent:
            if parent['type'] == 'project':
                project_id = parent['id']
            elif parent['project_id']:
                project_id = parent['project_id']
    
    file_data = {
        'id': file_id,
        'user_id': user_id,
        'project_id': project_id,
        'name': name,
        'type': file_type,
        'path': file_path,
        'content': content,
        'parent_id': parent_id,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

    try:
        # SQLite'a kaydet
        db.create_file(file_data)
        
        # Dosyayı diskde oluştur
        user_files_dir = get_user_files_dir(user_id)
        disk_file_path = user_files_dir / file_path
        
        if file_type == 'file':
            disk_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(disk_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:  # folder or project
            disk_file_path.mkdir(parents=True, exist_ok=True)

        return jsonify({
            'success': True,
            'data': {'file': file_data}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Dosya oluşturulamadı'
        }), 500

# --- ANA DEĞİŞİKLİK BURADA: create_project FONKSİYONU GÜNCELLENDİ ---
@app.route('/api/projects', methods=['POST'])
def create_project():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    data = request.get_json()
    project_name = data.get('name')
    # Frontend'den gelen 'type' bilgisini alıyoruz. Gelmezse 'empty' varsayıyoruz.
    project_type = data.get('type', 'empty')

    if not project_name:
        return jsonify({'success': False, 'message': 'Proje adı gerekli'}), 400

    try:
        # 1. Ana Proje Kayıtlarını Oluştur
        project_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        db.create_project({
            'id': project_id, 'user_id': user_id, 'name': project_name,
            'type': project_type, 'created_at': now, 'updated_at': now
        })
        
        project_file_data = {
            'id': project_id, 'user_id': user_id, 'project_id': project_id,
            'name': project_name, 'type': 'project', 'path': project_name,
            'content': '', 'parent_id': None, 'created_at': now, 'updated_at': now
        }
        db.create_file(project_file_data)
        
        # Diskte fiziksel proje klasörünü oluştur
        user_files_dir = get_user_files_dir(user_id)
        project_dir = user_files_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        created_files = [] # Oluşturulan dosyaları frontend'e bildirmek için bir liste
        
        # 2. Şablon Tipine Göre Başlangıç Dosyalarını Oluştur
        if project_type == 'flask':
            file_name = 'app.py'
            content = FLASK_SERVER_CONTENT
        elif project_type == 'datascience':
            file_name = 'main.py'
            content = DATA_SCIENCE_CONTENT
        else: # 'empty' veya tanımsız bir tip için
            file_name = 'main.py'
            content = EMPTY_PROJECT_CONTENT.format(project_name=project_name)
        
        # Seçilen şablona göre dosyayı oluştur (hem DB hem disk)
        file_id = str(uuid.uuid4())
        file_data = {
            'id': file_id, 'user_id': user_id, 'project_id': project_id,
            'name': file_name, 'type': 'file', 'path': f"{project_name}/{file_name}",
            'content': content, 'parent_id': project_id, 'created_at': now, 'updated_at': now
        }
        db.create_file(file_data)
        
        # Dosyayı diske yaz
        (project_dir / file_name).write_text(content, encoding='utf-8')
        
        created_files.append(file_data)
        
        return jsonify({
            'success': True,
            'data': {
                'project': project_file_data,
                'files': created_files # Eskiden 'main_file' vardı, şimdi 'files' listesi
            },
            'message': f'"{project_name}" projesi "{project_type}" şablonuyla oluşturuldu'
        })

    except Exception as e:
        # Hata ayıklama için hatayı konsola yazdır
        print(f"Proje oluşturma hatası: {e}")
        return jsonify({
            'success': False,
            'message': 'Proje oluşturulamadı'
        }), 500

# ... (diğer API endpoint'leri değişmeden kalıyor) ...
@app.route('/api/files/<file_id>/download', methods=['GET'])
def download_file(file_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    file_info = db.get_file_by_id(file_id)

    if not file_info or file_info['user_id'] != user_id:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404

    if file_info['type'] == 'folder' or file_info['type'] == 'project':
        return jsonify({'success': False, 'message': 'Klasörler indirilemez'}), 400

    # Dosya içeriği
    user_files_dir = get_user_files_dir(user_id)
    file_path = user_files_dir / file_info['path']
    
    if not file_path.exists():
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404

    try:
        from flask import send_file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file_info['name']
        )
    except Exception as e:
        return jsonify({'success': False, 'message': 'Dosya indirilemedi'}), 500

@app.route('/api/files/<file_id>', methods=['GET'])
def get_file_content(file_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    file_info = db.get_file_by_id(file_id)

    if not file_info or file_info['user_id'] != user_id:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404

    if file_info['type'] == 'folder' or file_info['type'] == 'project':
        return jsonify({'success': False, 'message': 'Klasörün içeriği okunamaz'}), 400

    # Dosya içeriğini diskten okuyoruz, DB'de saklamıyoruz
    user_files_dir = get_user_files_dir(user_id)
    file_path = user_files_dir / file_info['path']
    
    try:
        content = file_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        # Dosya diskte yoksa, DB'deki içeriği kullan (fallback)
        content = db.get_file_by_id(file_id).get('content', '')

    return jsonify({
        'success': True,
        'data': {'content': content}
    })

@app.route('/api/files/<file_id>', methods=['PUT'])
def update_file_content(file_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    data = request.get_json()
    content = data.get('content', '')

    file_info = db.get_file_by_id(file_id)

    if not file_info or file_info['user_id'] != user_id:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404

    try:
        # Sadece diske yazıyoruz. İçeriği DB'de tutmak büyük veriler için verimsiz olabilir.
        user_files_dir = get_user_files_dir(user_id)
        file_path = user_files_dir / file_info['path']
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')

        # Sadece updated_at zamanını DB'de güncelliyoruz.
        db.update_file_content(file_id, '') # content'i DB'ye boş gönderiyoruz

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Dosya güncellenemedi'}), 500

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    file_info = db.get_file_by_id(file_id)

    if not file_info or file_info['user_id'] != user_id:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404

    try:
        # Disk'ten sil
        user_files_dir = get_user_files_dir(user_id)
        file_path = user_files_dir / file_info['path']
        
        if file_path.exists():
            if file_info['type'] == 'folder' or file_info['type'] == 'project':
                shutil.rmtree(file_path)
            else:
                file_path.unlink()

        # Proje siliniyorsa projects tablosundan da sil
        if file_info['type'] == 'project':
            db.delete_project(file_id)
        else:
            # Normal dosya/klasör silme (recursive)
            db.delete_file(file_id)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Dosya silinemedi'}), 500

@app.route('/api/files/<file_id>/rename', methods=['PUT'])
def rename_file(file_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    data = request.get_json()
    new_name = data.get('name')

    if not new_name:
        return jsonify({'success': False, 'message': 'Yeni dosya adı gerekli'}), 400

    file_info = db.get_file_by_id(file_id)

    if not file_info or file_info['user_id'] != user_id:
        return jsonify({'success': False, 'message': 'Dosya bulunamadı'}), 404

    try:
        # Disk'te yeniden adlandır
        user_files_dir = get_user_files_dir(user_id)
        old_path = user_files_dir / file_info['path']
        
        # Yeni path oluştur
        new_path_str = str(Path(file_info['path']).parent / new_name)
        new_path = user_files_dir / new_path_str
        
        if old_path.exists():
            os.rename(old_path, new_path)

        # SQLite'da güncelle
        db.rename_file(file_id, new_name)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Dosya yeniden adlandırılamadı'}), 500

@app.route('/api/execute', methods=['POST'])
def execute_code():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Oturum açılmamış'}), 401

    data = request.get_json()
    code = data.get('code', '')

    if not code.strip():
        return jsonify({'success': False, 'message': 'Kod boş olamaz'}), 400

    # Kodu çalıştır
    result = execute_python_code(code)

    return jsonify({
        'success': True,
        'data': result
    })

if __name__ == '__main__':
    print("🐍 Python Web Editor Backend başlatılıyor...")
    print("📁 Proje dizini:", BASE_DIR)
    print("👥 Kullanıcı verileri:", USERS_DIR)
    print("📂 Dosya verileri:", FILES_DIR)
    print("🌐 Server: http://localhost:8000")
    
    app.run(debug=True, host='0.0.0.0', port=8000)