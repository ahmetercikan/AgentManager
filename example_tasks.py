"""
jira_task_agents.py için Kullanım Örnekleri

Bu dosya farklı task senaryoları için örnek konfigürasyonlar içerir.
"""
from jira_task_agents import TaskConfig, run_task_project


# ============================================================
# ÖRNEK 1: WEB API GELİŞTİRME
# ============================================================

def example_web_api():
    """RESTful API kullanıcı yönetim sistemi"""
    task_config = TaskConfig(
        project_name="Web API Geliştirme",
        description="RESTful API ile kullanıcı yönetim sistemi",
        requirements=[
            "FastAPI framework kullan",
            "PostgreSQL veritabanı",
            "JWT authentication",
            "CRUD operasyonları (Create, Read, Update, Delete)",
            "Input validation (Pydantic models)",
            "Error handling ve exception management",
            "API documentation (OpenAPI/Swagger)",
            "Rate limiting ekle",
            "Logging sistemi kur"
        ],
        file_name="user_api.py",
        programming_language="Python",
        additional_notes="API'nin production-ready olmasına dikkat et. Security best practices uygula."
    )
    return task_config


# ============================================================
# ÖRNEK 2: CLI HESAP MAKİNESİ
# ============================================================

def example_calculator():
    """Komut satırı hesap makinesi"""
    task_config = TaskConfig(
        project_name="CLI Hesap Makinesi",
        description="Komut satırından çalışan gelişmiş hesap makinesi uygulaması",
        requirements=[
            "Temel işlemler: toplama, çıkarma, çarpma, bölme",
            "Gelişmiş işlemler: üs alma, karekök, faktöriyel",
            "Argparse kütüphanesi kullan",
            "Interactive mode (sürekli işlem yapma)",
            "Geçmiş işlemleri kaydet (history)",
            "Unit testler yaz (pytest)",
            "Hata yönetimi (0'a bölme, geçersiz input vb.)"
        ],
        file_name="calculator.py",
        programming_language="Python",
        additional_notes="Kullanıcı dostu hata mesajları göster. Help komutunu ekle."
    )
    return task_config


# ============================================================
# ÖRNEK 3: TODO LIST UYGULAMASI
# ============================================================

def example_todo_app():
    """Basit Todo List uygulaması"""
    task_config = TaskConfig(
        project_name="Todo List Uygulaması",
        description="Komut satırından çalışan todo list yönetim sistemi",
        requirements=[
            "Todo ekleme, silme, güncelleme",
            "Todo'ları listeleme (tümü, tamamlananlar, bekleyenler)",
            "Öncelik seviyesi (Yüksek, Orta, Düşük)",
            "Kategori/tag sistemi",
            "JSON dosyasına kaydetme",
            "Arama ve filtreleme",
            "Due date (bitiş tarihi) ekleme",
            "Renklendirme (colorama kütüphanesi)"
        ],
        file_name="todo_app.py",
        programming_language="Python",
        additional_notes="Data persistence için JSON kullan. Tarih formatını ISO 8601 standardında tut."
    )
    return task_config


# ============================================================
# ÖRNEK 4: WEB SCRAPER
# ============================================================

def example_web_scraper():
    """Web scraping uygulaması"""
    task_config = TaskConfig(
        project_name="Web Scraper Uygulaması",
        description="Haber sitelerinden başlık ve içerik toplayan web scraper",
        requirements=[
            "BeautifulSoup4 ve requests kullan",
            "En az 3 farklı haber sitesinden veri çek",
            "Başlık, özet, link ve tarih bilgisi çek",
            "CSV formatında export et",
            "Rate limiting (siteden çok sık istek yapma)",
            "User-Agent header ekle",
            "Timeout ve retry mekanizması",
            "Logging ekle"
        ],
        file_name="news_scraper.py",
        programming_language="Python",
        additional_notes="Robots.txt dosyasına saygılı ol. Etik scraping yap."
    )
    return task_config


# ============================================================
# ÖRNEK 5: DISCORD BOT
# ============================================================

def example_discord_bot():
    """Discord bot uygulaması"""
    task_config = TaskConfig(
        project_name="Discord Bot",
        description="Basit komutlar çalıştırabilen Discord botu",
        requirements=[
            "discord.py kütüphanesi kullan",
            "Prefix-based komutlar (!help, !ping, !echo vb.)",
            "!help komutu (tüm komutları listele)",
            "!ping komutu (bot latency göster)",
            "!echo komutu (mesajı tekrarla)",
            "!roll komutu (rastgele zar at)",
            "Environment variables'dan token oku (.env)",
            "Error handling",
            "Logging sistemi"
        ],
        file_name="discord_bot.py",
        programming_language="Python",
        additional_notes="Token'ı asla hardcode etme. .env.example dosyası oluştur."
    )
    return task_config


# ============================================================
# ÖRNEK 6: FILE ORGANIZER
# ============================================================

def example_file_organizer():
    """Dosya düzenleyici uygulaması"""
    task_config = TaskConfig(
        project_name="File Organizer",
        description="Belirtilen klasördeki dosyaları türüne göre otomatik organize eden araç",
        requirements=[
            "Dosyaları uzantıya göre kategorize et (Resimler, Videolar, Dokümanlar, vb.)",
            "Her kategori için klasör oluştur",
            "Dosyaları ilgili klasörlere taşı",
            "Duplicate dosya kontrolü",
            "Dry-run mode (önce ne yapacağını göster)",
            "Undo özelliği (geri al)",
            "Progress bar göster (tqdm)",
            "Log dosyası oluştur"
        ],
        file_name="file_organizer.py",
        programming_language="Python",
        additional_notes="Dosya kaybını önlemek için güvenli hareket et. Backup al."
    )
    return task_config


# ============================================================
# ÖRNEK 7: PASSWORD GENERATOR
# ============================================================

def example_password_generator():
    """Güvenli şifre üretici"""
    task_config = TaskConfig(
        project_name="Şifre Üretici",
        description="Güvenli ve özelleştirilebilir şifre üreten CLI aracı",
        requirements=[
            "Şifre uzunluğu parametresi",
            "Büyük harf, küçük harf, rakam, özel karakter seçenekleri",
            "Birden fazla şifre üret",
            "Şifre gücü göstergesi (weak, medium, strong)",
            "Kolay okunabilir şifreler (ambiguous karakterleri çıkar)",
            "Şifreleri dosyaya kaydetme opsiyonu",
            "Passphrase üretme (kelime bazlı)",
            "Argparse ile CLI arayüzü"
        ],
        file_name="password_generator.py",
        programming_language="Python",
        additional_notes="Kriptografik olarak güvenli rastgelelik kullan (secrets modülü)."
    )
    return task_config


# ============================================================
# ÖRNEK 8: JSON to CSV CONVERTER
# ============================================================

def example_json_csv_converter():
    """JSON'dan CSV'ye dönüştürücü"""
    task_config = TaskConfig(
        project_name="JSON to CSV Converter",
        description="JSON dosyalarını CSV formatına dönüştüren araç",
        requirements=[
            "Nested JSON desteği",
            "Array içindeki nesneleri işle",
            "Sütun isimlerini otomatik oluştur",
            "Null değerleri handle et",
            "Büyük dosyalar için streaming mode",
            "Encoding seçeneği (UTF-8, ASCII vb.)",
            "Delimiter seçeneği (virgül, noktalı virgül vb.)",
            "Batch processing (birden fazla dosya)"
        ],
        file_name="json_to_csv.py",
        programming_language="Python",
        additional_notes="Pandas kullan. Memory efficient çalış."
    )
    return task_config


# ============================================================
# ÖRNEK 9: NODEJS EXPRESS API
# ============================================================

def example_nodejs_api():
    """Node.js ile Express API"""
    task_config = TaskConfig(
        project_name="Node.js Express API",
        description="Express.js ile basit REST API",
        requirements=[
            "Express.js framework kullan",
            "CRUD endpoints (GET, POST, PUT, DELETE)",
            "MongoDB veritabanı (Mongoose)",
            "JWT authentication middleware",
            "Input validation (express-validator)",
            "Error handling middleware",
            "CORS yapılandırması",
            "Environment variables (.env)",
            "API documentation (Swagger/JSDoc)"
        ],
        file_name="server.js",
        programming_language="JavaScript",
        additional_notes="ES6+ syntax kullan. Async/await tercih et. Security headers ekle (helmet)."
    )
    return task_config


# ============================================================
# ÖRNEK 10: JAVA CONSOLE QUIZ APP
# ============================================================

def example_java_quiz():
    """Java ile quiz uygulaması"""
    task_config = TaskConfig(
        project_name="Java Quiz Uygulaması",
        description="Konsoldan çalışan çoktan seçmeli quiz oyunu",
        requirements=[
            "Soru ve cevapları dosyadan oku (JSON veya text)",
            "4 şıklı çoktan seçmeli sorular",
            "Kullanıcıdan cevap al",
            "Doğru/yanlış kontrolü",
            "Skor hesaplama",
            "Quiz bitiminde sonuçları göster",
            "Yanlış cevaplanan soruları listele",
            "Exception handling",
            "OOP prensipleri (Quiz, Question, Answer sınıfları)"
        ],
        file_name="QuizApp.java",
        programming_language="Java",
        additional_notes="Clean code prensipleri uygula. Scanner kullan. MVC pattern düşün."
    )
    return task_config


# ============================================================
# ANA FONKSIYON - HANGİ ÖRNEĞİ ÇALIŞTIRMAK İSTİYORSUN?
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 JIRA TASK AGENTS - ÖRNEK KULLANIM")
    print("=" * 60)
    print("\nHangi örneği çalıştırmak istersiniz?\n")
    print("1. Web API Geliştirme (FastAPI)")
    print("2. CLI Hesap Makinesi")
    print("3. Todo List Uygulaması")
    print("4. Web Scraper")
    print("5. Discord Bot")
    print("6. File Organizer")
    print("7. Password Generator")
    print("8. JSON to CSV Converter")
    print("9. Node.js Express API")
    print("10. Java Quiz Uygulaması")
    print("\n0. Çıkış")
    print("=" * 60)

    secim = input("\nSeçiminiz (0-10): ")

    task_config = None

    if secim == "1":
        task_config = example_web_api()
    elif secim == "2":
        task_config = example_calculator()
    elif secim == "3":
        task_config = example_todo_app()
    elif secim == "4":
        task_config = example_web_scraper()
    elif secim == "5":
        task_config = example_discord_bot()
    elif secim == "6":
        task_config = example_file_organizer()
    elif secim == "7":
        task_config = example_password_generator()
    elif secim == "8":
        task_config = example_json_csv_converter()
    elif secim == "9":
        task_config = example_nodejs_api()
    elif secim == "10":
        task_config = example_java_quiz()
    elif secim == "0":
        print("\n👋 Çıkış yapılıyor...")
        exit(0)
    else:
        print("\n❌ Geçersiz seçim!")
        exit(1)

    if task_config:
        print(f"\n✅ '{task_config.project_name}' projesi başlatılıyor...\n")
        run_task_project(task_config)
