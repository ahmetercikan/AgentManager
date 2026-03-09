"""
Jira Entegrasyonlu AI Ajanlar - Yılan Oyunu Geliştirme Projesi
3 Kişilik Ekip: Proje Yöneticisi, Yazılımcı, Testçi
"""
import os
import signal
import sys
import warnings
import time

# Windows düzeltmesi
if sys.platform.startswith('win'):
    def handler(signum, frame):
        pass

    missing_signals = [
        'SIGHUP', 'SIGQUIT', 'SIGTSTP', 'SIGCONT',
        'SIGUSR1', 'SIGUSR2', 'SIGALRM'
    ]

    for sig_name in missing_signals:
        if not hasattr(signal, sig_name):
            setattr(signal, sig_name, signal.SIGTERM if hasattr(signal, 'SIGTERM') else 1)

warnings.filterwarnings('ignore')

from crewai import Agent, Task, Crew, Process, LLM
from jira_helper import JiraHelper

# ============================================================
# YAPILANDIRMA
# ============================================================

# Jira Bilgileri
JIRA_URL = "https://dgpaysit.atlassian.net"
JIRA_EMAIL = "fatih.yigit@dgpays.com"
JIRA_TOKEN = "YOUR_JIRA_TOKEN"
PROJECT_KEY = "TES"

# OpenAI API Key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM Modeli
my_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Jira Helper oluştur
jira = JiraHelper(JIRA_URL, JIRA_EMAIL, JIRA_TOKEN, PROJECT_KEY)

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def create_jira_tasks_from_plan(plan_text: str) -> list:
    """
    Proje planından Jira task'ları oluşturur

    Args:
        plan_text: Proje planı metni

    Returns:
        Oluşturulan task'ların key listesi
    """
    print("\n" + "=" * 60)
    print("📋 JIRA TASK'LARI OLUŞTURULUYOR")
    print("=" * 60)

    tasks = []

    # Epic oluştur
    epic = jira.create_issue(
        summary="Snake Game Development - Yılan Oyunu Geliştirme",
        description=f"Pygame ile basit bir yılan oyunu geliştirme projesi.\n\n{plan_text}",
        issue_type="Epic"
    )

    if epic:
        epic_key = epic['key']
        print(f"\n✅ Epic oluşturuldu: {epic_key}\n")

        # Task 1: Oyun Mekaniklerini Kodla
        task1 = jira.create_issue(
            summary="[DEV] Yılan Oyunu Temel Mekaniklerini Kodla",
            description="""
Pygame kullanarak yılan oyununun temel mekaniklerini kodla:

GEREKSINIMLER:
- Pygame kütüphanesi kullan
- snake_game.py dosyası oluştur
- Oyun döngüsü (game loop) kur
- Yılan hareketi (ok tuşları)
- Yem sistemi
- Çarpışma kontrolü (duvar, kendine çarpma)
- Skor sistemi
- FPS kontrolü (15 FPS)

ÇIKTI:
- Tam çalışır snake_game.py dosyası
- Kod içinde açıklayıcı yorumlar

KABUL KRİTERLERİ:
✓ Oyun çalışıyor ve oynanabilir
✓ Tüm temel mekanikler çalışıyor
✓ Kod temiz ve okunabilir
            """,
            issue_type="Task",
            assignee_email=JIRA_EMAIL
        )
        if task1:
            tasks.append(task1['key'])

        # Task 2: Otomatik Testleri Yaz
        task2 = jira.create_issue(
            summary="[QA] Test Senaryoları Oluştur ve Manuel Test Yap",
            description="""
Yılan oyunu için test senaryoları oluştur ve manuel test yap:

TEST SENARYOLARI:
1. Yılan hareketi (yukarı, aşağı, sağ, sol)
2. Yem yeme ve büyüme
3. Duvara çarpma (Game Over)
4. Kendine çarpma (Game Over)
5. Skor artışı
6. FPS kontrolü
7. Oyun yeniden başlatma

TEST ADIM LARI:
1. Test senaryolarını dokümante et
2. Her senaryoyu test et
3. Bulunan hataları raporla
4. Bug varsa Jira'da bug kaydı aç

ÇIKTI:
- Test senaryoları dokümanı
- Test raporu
- Bug listesi (varsa)
            """,
            issue_type="Test",
            assignee_email=JIRA_EMAIL
        )
        if task2:
            tasks.append(task2['key'])

        # Task 3: Kod Review ve İyileştirme
        task3 = jira.create_issue(
            summary="[PM] Kod Review ve Proje Tamamlama",
            description="""
Proje yöneticisi olarak projeyi gözden geçir:

YAPILACAKLAR:
1. Kod kalitesi kontrolü
2. Test sonuçlarını incele
3. Bug'ların düzeltildiğini kontrol et
4. Dokümantasyonu kontrol et
5. Projeyi tamamla

ÇIKTI:
- Kod review raporu
- Final raporu
- Proje tamamlama onayı
            """,
            issue_type="Task",
            assignee_email=JIRA_EMAIL
        )
        if task3:
            tasks.append(task3['key'])

    print(f"\n✅ Toplam {len(tasks)} task oluşturuldu!")
    print(f"   Task'lar: {', '.join(tasks)}")
    print("=" * 60)

    return tasks


def write_code_to_file(code: str, filename: str = "snake_game_ai.py"):
    """
    AI tarafından üretilen kodu dosyaya yazar

    Args:
        code: Python kodu
        filename: Dosya adı
    """
    # Kod bloklarını temizle
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]

    code = code.strip()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n✅ Kod {filename} dosyasına yazıldı!")


# ============================================================
# AI AJANLAR
# ============================================================

# 1. Proje Yöneticisi - Jira Task'larını Oluşturur
proje_yoneticisi = Agent(
    role='Proje Yöneticisi (PM)',
    goal='Yılan oyunu projesini yönetmek, Jira task\'larını oluşturmak ve ekibi koordine etmek',
    backstory="""
    Sen deneyimli bir proje yöneticisisin ve Jira konusunda uzmansın.
    Yılan oyunu geliştirme projesi için detaylı bir plan hazırlayacak ve
    Jira'da gerekli task'ları oluşturacaksın.

    Görevlerin:
    - Proje kapsamını belirle
    - Detaylı task'ları planla
    - Her task için net gereksinimler yaz
    - Kabul kriterlerini tanımla
    """,
    verbose=True,
    allow_delegation=False,
    llm=my_llm
)

# 2. Yazılımcı - Kodu Yazar
yazilimci = Agent(
    role='Kıdemli Python Yazılımcı (Developer)',
    goal='Yüksek kaliteli, çalışan Python yılan oyunu kodu yazmak',
    backstory="""
    Sen pygame konusunda uzman bir Python yazılımcısısın.
    Yılan oyunu gibi klasik oyunları sıfırdan kodlayabiliyorsun.

    Özellikler:
    - Temiz, okunabilir kod yazarsın
    - Kod içine yorumlar eklersin
    - Oyun döngüsü, olay yönetimi ve grafik çiziminde uzmansın
    - Best practice'lere uygun kodlarsın

    ÖNEMLI: Kodunu her zaman ```python``` bloğu içinde ver!
    """,
    verbose=True,
    allow_delegation=False,
    llm=my_llm
)

# 3. Testçi - Test Eder ve Bug Açar
testci = Agent(
    role='Test Uzmanı (QA Engineer)',
    goal='Oyunu test etmek, hataları bulmak ve bug raporları oluşturmak',
    backstory="""
    Sen detaycı bir test uzmanısın.
    Kodları inceler, olası hataları tespit eder, edge case'leri düşünürsün.

    Görevlerin:
    - Detaylı test senaryoları oluştur
    - Her senaryoyu dikkatlice test et
    - Bulunan hataları listele
    - Her hata için açıklayıcı bug raporu hazırla
    - İyileştirme önerileri sun

    Bug raporu formatı:
    - Bug başlığı
    - Adımlar (nasıl oluşuyor)
    - Beklenen davranış
    - Gerçek davranış
    - Öncelik (Yüksek/Orta/Düşük)
    """,
    verbose=True,
    allow_delegation=False,
    llm=my_llm
)

# ============================================================
# GÖREVLER (TASKS)
# ============================================================

# Görev 1: PM Proje Planı Oluşturur
gorev1_pm_planlama = Task(
    description="""
    Yılan oyunu geliştirme projesi için detaylı bir proje planı oluştur.

    PROJE KAPSAMI:
    - Pygame ile basit yılan oyunu
    - Temel mekanikler: hareket, yem yeme, büyüme, çarpışma
    - Skor sistemi
    - FPS kontrolü

    PLANI ŞÖYLE HAZIRLA:
    1. Proje özeti
    2. Teknik gereksinimler (detaylı)
    3. Görevler ve sorumlular
    4. Kabul kriterleri
    5. Riskler ve kısıtlar

    ÇIKTI: Detaylı proje planı (200-300 kelime)
    """,
    agent=proje_yoneticisi,
    expected_output="Detaylı proje planı ve görev tanımları"
)

# Görev 2: Developer Oyunu Kodlar
gorev2_dev_kodlama = Task(
    description="""
    PM'in belirlediği gereksinimlere göre yılan oyununu kodla.

    GEREKSINIMLER:
    - Pygame kullan
    - Tek dosya: snake_game_ai.py
    - Oyun döngüsü (game loop)
    - Yılan hareketi (ok tuşları: ↑↓←→)
    - Yem sistemi (rastgele konumda yeşil kare)
    - Yem yediğinde yılan büyür
    - Duvara çarpınca Game Over
    - Kendine çarpınca Game Over
    - Skor gösterimi
    - FPS: 15
    - "Game Over" ekranında C tuşu ile yeniden başlama
    - Q tuşu ile çıkış

    KODLAMA KURALLARI:
    - Temiz ve okunabilir kod
    - Fonksiyonlar için açıklayıcı yorumlar
    - Değişken isimleri anlamlı olsun
    - Best practices uygula

    ÖNEMLİ: Kodun TAMAMINI ```python``` bloğu içinde ver!
    Eksik bırakma, tüm kodu yaz!

    ÇIKTI: Tam çalışır Python oyun kodu
    """,
    agent=yazilimci,
    expected_output="Tam çalışır snake_game_ai.py Python kodu",
    context=[gorev1_pm_planlama]
)

# Görev 3: QA Test Eder
gorev3_qa_test = Task(
    description="""
    Yazılımcının kodladığı oyun için test senaryoları oluştur ve kodu incele.

    TEST SENARYOLARI:
    1. TS-001: Yılan hareketi (4 yön)
    2. TS-002: Yem yeme ve büyüme
    3. TS-003: Duvara çarpma (Game Over)
    4. TS-004: Kendine çarpma (Game Over)
    5. TS-005: Skor artışı
    6. TS-006: Oyunu yeniden başlatma (C tuşu)
    7. TS-007: Oyundan çıkış (Q tuşu)

    HER SENARYO İÇİN:
    - Test adımları
    - Beklenen sonuç
    - Kod incelemesi sonucu
    - Potansiyel hatalar

    KOD İNCELEMESİ:
    - Kod kalitesi
    - Best practices uyumu
    - Performans
    - Eksik özellikler
    - Potansiyel bug'lar

    ÇIKTI:
    1. Test senaryoları listesi
    2. Kod inceleme raporu
    3. Bulunan hatalar/eksikler (varsa)
    4. İyileştirme önerileri
    """,
    agent=testci,
    expected_output="Test senaryoları, kod inceleme raporu ve bug listesi",
    context=[gorev1_pm_planlama, gorev2_dev_kodlama]
)

# ============================================================
# MAIN - PROJEYİ ÇALIŞTIR
# ============================================================

def main():
    """Ana program"""
    print("\n" + "=" * 60)
    print("🎮 JIRA ENTEGRASYONLU YILAN OYUNU GELİŞTİRME PROJESİ")
    print("=" * 60)
    print("👥 Ekip: Proje Yöneticisi, Yazılımcı, Test Uzmanı")
    print("🔗 Jira Projesi: TES")
    print("=" * 60)

    # Jira bağlantısını test et
    print("\n🔍 Jira bağlantısı kontrol ediliyor...")
    test_issues = jira.get_issues(max_results=1)
    if test_issues is not None:
        print("✅ Jira bağlantısı başarılı!")
    else:
        print("❌ Jira bağlantısı başarısız! Program sonlandırılıyor.")
        return

    # Ekip oluştur
    ekip = Crew(
        agents=[proje_yoneticisi, yazilimci, testci],
        tasks=[gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_qa_test],
        verbose=True,
        process=Process.sequential
    )

    print("\n🚀 Ekip çalışmaya başlıyor...\n")
    print("=" * 60)

    # Ekibi çalıştır
    sonuc = ekip.kickoff()

    print("\n" + "=" * 60)
    print("🎯 EKİP ÇALIŞMASINI TAMAMLADI!")
    print("=" * 60)

    # Sonuçları işle
    print("\n📝 SONUÇLAR İŞLENİYOR...")

    # 1. Proje planını al ve Jira task'larını oluştur
    plan = str(gorev1_pm_planlama.output) if hasattr(gorev1_pm_planlama, 'output') else str(sonuc)
    created_tasks = create_jira_tasks_from_plan(plan)

    # 2. Kodu dosyaya yaz
    kod = str(gorev2_dev_kodlama.output) if hasattr(gorev2_dev_kodlama, 'output') else ""
    if kod and len(kod) > 100:
        write_code_to_file(kod, "snake_game_ai.py")

        # İlk task'ı "In Progress" yap
        if created_tasks and len(created_tasks) > 0:
            jira.update_issue_status(created_tasks[0], "In Progress")
            jira.add_comment(created_tasks[0], "✅ Kod yazıldı: snake_game_ai.py\n\nKod AI tarafından oluşturuldu ve dosyaya kaydedildi.")

    # 3. Test raporunu Jira'ya ekle
    test_raporu = str(gorev3_qa_test.output) if hasattr(gorev3_qa_test, 'output') else ""
    if test_raporu and created_tasks and len(created_tasks) > 1:
        jira.add_comment(created_tasks[1], f"📋 TEST RAPORU:\n\n{test_raporu}")

    # 4. Raporu kaydet
    with open("jira_snake_project_report.txt", "w", encoding="utf-8") as f:
        f.write("JIRA ENTEGRASYONLU YILAN OYUNU PROJESİ RAPORU\n")
        f.write("=" * 60 + "\n\n")
        f.write("📊 OLUŞTURULAN JIRA TASK'LARI:\n")
        for task_key in created_tasks:
            f.write(f"  - {task_key}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        f.write(str(sonuc))

    print("\n✅ Rapor 'jira_snake_project_report.txt' dosyasına kaydedildi.")
    print(f"✅ Oyun kodu 'snake_game_ai.py' dosyasına kaydedildi.")
    print(f"✅ Jira'da {len(created_tasks)} task oluşturuldu!")
    print("\n🎮 Oyunu çalıştırmak için: python snake_game_ai.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
