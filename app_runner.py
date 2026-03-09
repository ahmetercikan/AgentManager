"""
App Runner - Agent'ların oluşturduğu uygulamaları otomatik çalıştırır

Kullanım:
    python app_runner.py Game.jsx          # React uygulamasını çalıştır
    python app_runner.py calculator.py     # Python uygulamasını çalıştır
    python app_runner.py                   # Son oluşturulan uygulamayı çalıştır
"""
import os
import sys
import subprocess
import shutil
import json
from pathlib import Path

# Proje kök dizini
ROOT_DIR = Path(__file__).parent
REACT_TEMPLATE_DIR = ROOT_DIR / "react-runner"

def setup_react_template():
    """Hazır React projesi oluştur (bir kez)"""
    if REACT_TEMPLATE_DIR.exists():
        print("✅ React template mevcut")
        return True

    print("📦 React template oluşturuluyor (ilk sefere özel)...")

    try:
        # Vite ile React projesi oluştur
        subprocess.run(
            ["npm", "create", "vite@latest", "react-runner", "--", "--template", "react"],
            cwd=ROOT_DIR,
            check=True,
            shell=True
        )

        # Bağımlılıkları yükle
        print("📦 Bağımlılıklar yükleniyor...")
        subprocess.run(
            ["npm", "install"],
            cwd=REACT_TEMPLATE_DIR,
            check=True,
            shell=True
        )

        # Axios ekle (API çağrıları için)
        subprocess.run(
            ["npm", "install", "axios"],
            cwd=REACT_TEMPLATE_DIR,
            check=True,
            shell=True
        )

        print("✅ React template hazır!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Template oluşturulamadı: {e}")
        return False

def find_latest_app():
    """Son oluşturulan uygulama dosyasını bul"""
    extensions = ['.jsx', '.tsx', '.py']
    files = []

    for ext in extensions:
        for f in ROOT_DIR.glob(f"*{ext}"):
            # venv ve node_modules hariç
            if 'venv' not in str(f) and 'node_modules' not in str(f) and 'react-runner' not in str(f):
                files.append(f)

    if not files:
        return None

    # En son değiştirilen dosyayı döndür
    return max(files, key=lambda f: f.stat().st_mtime)

def run_python_app(filepath):
    """Python uygulamasını çalıştır"""
    print(f"\n🐍 Python uygulaması çalıştırılıyor: {filepath.name}")
    print("=" * 60)

    subprocess.run([sys.executable, str(filepath)], cwd=ROOT_DIR)

def run_react_app(filepath):
    """React uygulamasını çalıştır"""
    print(f"\n⚛️  React uygulaması çalıştırılıyor: {filepath.name}")
    print("=" * 60)

    # Template'i kur
    if not setup_react_template():
        return

    # Dosyayı src klasörüne kopyala
    src_dir = REACT_TEMPLATE_DIR / "src"
    target_file = src_dir / filepath.name

    print(f"📋 {filepath.name} -> react-runner/src/")
    shutil.copy(filepath, target_file)

    # CSS dosyası varsa onu da kopyala
    css_file = filepath.with_suffix('.css')
    if css_file.exists():
        print(f"📋 {css_file.name} -> react-runner/src/")
        shutil.copy(css_file, src_dir / css_file.name)

    # App.jsx'i güncelle
    component_name = filepath.stem  # Game.jsx -> Game
    app_jsx = src_dir / "App.jsx"

    app_content = f'''import {component_name} from './{component_name}'

function App() {{
  return <{component_name} />
}}

export default App
'''

    with open(app_jsx, 'w', encoding='utf-8') as f:
        f.write(app_content)

    print(f"✅ App.jsx güncellendi -> <{component_name} />")

    # Geliştirme sunucusunu başlat
    print("\n🚀 Geliştirme sunucusu başlatılıyor...")
    print("💡 Tarayıcıda http://localhost:5173 adresine git")
    print("🛑 Durdurmak için Ctrl+C\n")

    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=REACT_TEMPLATE_DIR,
            shell=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Uygulama durduruldu.")

def main():
    print("\n" + "=" * 60)
    print("🚀 APP RUNNER - Agent Uygulamalarını Çalıştır")
    print("=" * 60)

    # Dosya argümanı verildi mi?
    if len(sys.argv) > 1:
        filepath = Path(sys.argv[1])
        if not filepath.is_absolute():
            filepath = ROOT_DIR / filepath
    else:
        # Son oluşturulan dosyayı bul
        filepath = find_latest_app()
        if not filepath:
            print("❌ Çalıştırılacak uygulama bulunamadı!")
            print("💡 Kullanım: python app_runner.py <dosya_adı>")
            return
        print(f"📌 Son oluşturulan uygulama: {filepath.name}")

    if not filepath.exists():
        print(f"❌ Dosya bulunamadı: {filepath}")
        return

    # Dosya türüne göre çalıştır
    ext = filepath.suffix.lower()

    if ext == '.py':
        run_python_app(filepath)
    elif ext in ['.jsx', '.tsx']:
        run_react_app(filepath)
    else:
        print(f"❌ Desteklenmeyen dosya türü: {ext}")
        print("💡 Desteklenen: .py, .jsx, .tsx")

if __name__ == "__main__":
    main()
