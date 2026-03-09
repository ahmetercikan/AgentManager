import os
import signal
import sys
import warnings

# ============================================================
# 1. ADIM: WINDOWS DÜZELTMESİ (EN TEPEDE OLMALI!)
# ============================================================
# Bu kodun, 'from crewai import...' satırından ÖNCE çalışması şart.
if sys.platform.startswith('win'):
    def handler(signum, frame):
        pass
    
    # Windows'ta olmayan sinyalleri tek tek tanımlıyoruz
    missing_signals = [
        'SIGHUP', 'SIGQUIT', 'SIGTSTP', 'SIGCONT', 
        'SIGUSR1', 'SIGUSR2', 'SIGALRM'
    ]
    
    for sig_name in missing_signals:
        if not hasattr(signal, sig_name):
            # Sinyal yoksa ekle ve boş bir değer ata
            setattr(signal, sig_name, signal.SIGTERM if hasattr(signal, 'SIGTERM') else 1)

# Uyarıları kapat
warnings.filterwarnings('ignore')

# ============================================================
# 2. ADIM: KÜTÜPHANELERİ ŞİMDİ ÇAĞIRIYORUZ
# ============================================================
from crewai import Agent, Task, Crew, Process, LLM

# ============================================================
# 3. ADIM: API ANAHTARI VE MODEL
# ============================================================

# ⚠️ UYARI: CrewAI'nin Gemini entegrasyonu çalışmıyor!
# Gemini API v1beta eski ve yeni modelleri desteklemiyor.
#
# ÇÖZÜM SEÇENEKLERI:
# 1. OpenAI API Key alın (https://platform.openai.com/api-keys)
# 2. Veya Node.js agent-endpoints.js sisteminizi kullanın

# SEÇENEK 1: OpenAI (Çalışıyor!)
openai_api_key = "YOUR_OPENAI_API_KEY"
os.environ["OPENAI_API_KEY"] = openai_api_key

my_llm = LLM(
    model="gpt-4o-mini",  # Ucuz ve hızlı
    api_key=openai_api_key
)

# SEÇENEK 2: Gemini (ŞU AN ÇALIŞMIYOR - CrewAI uyumsuz)
# gemini_api_key = "YOUR_GEMINI_API_KEY"
# os.environ["GEMINI_API_KEY"] = gemini_api_key
# my_llm = LLM(
#     model="gemini/gemini-1.5-flash",
#     api_key=gemini_api_key
# )

# ============================================================
# 4. ADIM: AJANLAR - YILAN OYUNU GELİŞTİRME EKİBİ
# ============================================================

# 1. Orkestratör - Proje yöneticisi
orkestrator = Agent(
  role='Proje Yöneticisi ve Orkestratör',
  goal='Ekibi koordine etmek ve görev dağılımı yapmak',
  backstory="""Sen deneyimli bir yazılım proje yöneticisisin.
  Ekibindeki yazılımcı ve test uzmanını koordine ediyorsun.
  Görevleri net şekilde tanımlıyor, öncelikleri belirliyorsun.""",
  verbose=True,
  allow_delegation=True,  # Görev atayabilir
  llm=my_llm
)

# 2. Yazılımcı - Python Developer
yazilimci = Agent(
  role='Kıdemli Python Yazılımcısı',
  goal='Yüksek kaliteli, temiz Python kodu yazmak',
  backstory="""Sen pygame konusunda uzman bir Python yazılımcısısın.
  Yılan oyunu gibi klasik oyunları sıfırdan kodlayabiliyorsun.
  Kodlarını temiz, okunabilir ve yorumlu yazıyorsun.
  Oyun döngüsü, olay yönetimi ve grafik çizimi konularında uzmansın.""",
  verbose=True,
  allow_delegation=False,
  llm=my_llm
)

# 3. Test Uzmanı - QA Engineer
test_uzmani = Agent(
  role='Kıdemli Test Uzmanı',
  goal='Yazılımları test edip hataları bulmak',
  backstory="""Sen detaycı bir test uzmanısın.
  Kodları inceler, olası hataları tespit eder, edge case'leri düşünürsün.
  Oyunun çalışması için gerekli tüm kontrolleri yaparsın.
  Test senaryoları oluşturur ve iyileştirme önerileri sunarsın.""",
  verbose=True,
  allow_delegation=False,
  llm=my_llm
)

# ============================================================
# 5. ADIM: GÖREVLER - YILAN OYUNU PROJESİ
# ============================================================

# Görev 1: Orkestratör proje planı oluşturur
gorev1_planlama = Task(
  description="""
  Basit bir Python Yılan (Snake) oyunu projesi için görev planı oluştur.

  Şunları belirle:
  1. Proje kapsamı (Oyunun özellikleri)
  2. Yazılımcıya verilecek detaylı teknik gereksinimler
  3. Test uzmanına verilecek test senaryoları

  Oyun özellikleri:
  - Pygame kütüphanesi kullanılacak
  - Basit 2D yılan oyunu
  - Yılan ok tuşlarıyla hareket edecek
  - Yem yediğinde büyüyecek
  - Duvara veya kendine çarpınca oyun bitecek
  - Skor gösterilecek
  """,
  agent=orkestrator,
  expected_output="Detaylı proje planı ve görev listesi"
)

# Görev 2: Yazılımcı oyunu kodlar
gorev2_kodlama = Task(
  description="""
  Orkestratörün belirlediği gereksinimlere göre Python ile Yılan oyunu geliştir.

  Gereksinimler:
  - Pygame kütüphanesi kullan
  - snake_game.py adında tek dosya halinde kodla
  - Kod içine açıklayıcı yorumlar ekle
  - Oyun döngüsü düzgün çalışmalı
  - FPS kontrolü olmalı
  - Temiz ve okunabilir kod yaz

  ÇIKTI: Tam çalışan Python kodu (snake_game.py)
  """,
  agent=yazilimci,
  expected_output="Tam çalışır durumda yılan oyunu Python kodu",
  context=[gorev1_planlama]  # Planlama görevinin çıktısını kullan
)

# Görev 3: Test uzmanı test senaryoları oluşturur ve kodu test eder
gorev3_test = Task(
  description="""
  Yazılımcının geliştirdiği Yılan oyunu için ÖNCE test senaryoları oluştur,
  SONRA kodu bu senaryolara göre incele ve test et.

  ADIM 1 - TEST SENARYOLARI OLUŞTUR:
  Her senaryo için şunları belirt:
  - Senaryo ID (TS-001, TS-002, vb.)
  - Senaryo Adı
  - Test Adımları
  - Beklenen Sonuç
  - Öncelik (Yüksek/Orta/Düşük)

  Test senaryoları şunları kapsamalı:
  - Temel oyun mekaniği (hareket, yön değiştirme)
  - Yem yeme ve büyüme
  - Çarpışma kontrolü (duvar, kendi kendine)
  - Skor sistemi
  - Oyun başlangıç ve bitiş durumları
  - Edge cases (köşelere çarpma, hızlı yön değiştirme, vb.)

  ADIM 2 - KODU İNCELE VE TEST ET:
  1. Kod kalitesi analizi (okunabilirlik, yorumlar, best practices)
  2. Her test senaryosunu koda göre değerlendir
  3. Bulunan hataları ve eksikleri listele
  4. Performans analizi
  5. Güvenlik kontrolleri

  ÇIKTI FORMATI:

  ## TEST SENARYOLARI LİSTESİ
  [Tüm test senaryoları numaralandırılmış liste halinde]

  ## TEST RAPORU
  [Her senaryo için test sonuçları]

  ## BULUNAN HATALAR VE EKSİKLER
  [Öncelik sırasına göre]

  ## İYİLEŞTİRME ÖNERİLERİ
  [Kod kalitesi ve fonksiyonellik önerileri]
  """,
  agent=test_uzmani,
  expected_output="Test senaryoları listesi + Detaylı test raporu + İyileştirme önerileri",
  context=[gorev1_planlama, gorev2_kodlama]
)

# ============================================================
# 6. ADIM: EKİBİ BAŞLAT - YILAN OYUNU PROJESİ
# ============================================================

ekip = Crew(
  agents=[orkestrator, yazilimci, test_uzmani],
  tasks=[gorev1_planlama, gorev2_kodlama, gorev3_test],
  verbose=True,
  process=Process.sequential  # Görevler sırayla çalışır: Plan -> Kod -> Test
)

print("🎮 Yılan Oyunu Geliştirme Ekibi Başlıyor...")
print("👥 Ekip: Orkestratör, Yazılımcı, Test Uzmanı")
print("=" * 60)

sonuc = ekip.kickoff()

print("\n\n" + "=" * 60)
print("🏁 PROJE TAMAMLANDI!")
print("=" * 60)
print(sonuc)

# Sonucu dosyaya kaydet
with open("snake_game_rapor.txt", "w", encoding="utf-8") as f:
    f.write("YILAN OYUNU GELİŞTİRME PROJESİ RAPORU\n")
    f.write("=" * 60 + "\n\n")
    f.write(str(sonuc))

print("\n✅ Rapor 'snake_game_rapor.txt' dosyasına kaydedildi.")