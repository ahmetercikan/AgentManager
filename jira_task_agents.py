"""
Jira Entegrasyonlu AI Ajanlar - Parametrik Task Yönetim Sistemi
3 Kişilik Ekip: Proje Yöneticisi, Yazılımcı, Testçi

Herhangi bir yazılım geliştirme görevini alıp AI ajanları ile işleyebilir.
"""
import os
import signal
import sys
import warnings
import time
from typing import Dict, List, Optional

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
# TASK CONFIGURATION CLASS
# ============================================================

class TaskConfig:
    """
    Parametrik task yapılandırma sınıfı
    """

    def __init__(self,
                 project_name: str,
                 description: str,
                 requirements: List[str],
                 file_name: str,
                 programming_language: str = "Python",
                 additional_notes: str = ""):
        self.project_name = project_name
        self.description = description
        self.requirements = requirements
        self.file_name = file_name
        self.programming_language = programming_language
        self.additional_notes = additional_notes

    def get_formatted_requirements(self) -> str:
        """Gereksinimleri formatlanmış string olarak döndürür"""
        return "\n".join([f"    - {req}" for req in self.requirements])

    def get_epic_summary(self) -> str:
        """Epic başlığını döndürür"""
        return f"{self.project_name}"

    def get_epic_description(self) -> str:
        """Epic açıklamasını döndürür"""
        desc = f"{self.description}\n\n"
        desc += "GEREKSINIMLER:\n"
        desc += self.get_formatted_requirements()
        if self.additional_notes:
            desc += f"\n\nEK NOTLAR:\n{self.additional_notes}"
        return desc


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

    print("\n" + "=" * 60)
    print("📋 JIRA TASK'LARI OLUŞTURULUYOR")
    print("=" * 60)

    tasks = []

    # Epic oluştur
    epic = jira.create_issue(
        summary=task_config.get_epic_summary(),
        description=f"{task_config.get_epic_description()}\n\n--- PROJE PLANI ---\n{plan_text}",
        issue_type="Epic"
    )

    if epic:
        epic_key = epic['key']
        print(f"\n✅ Epic oluşturuldu: {epic_key}\n")

        # Task 1: Development Task
        task1 = jira.create_issue(
            summary=f"[DEV] {task_config.project_name} - Ana Geliştirme",
            description=f"""
{task_config.description}

GEREKSINIMLER:
{task_config.get_formatted_requirements()}

PROGRAMLAMA DILI: {task_config.programming_language}
DOSYA ADI: {task_config.file_name}

KODLAMA KURALLARI:
- Temiz ve okunabilir kod
- Fonksiyonlar için açıklayıcı yorumlar
- Değişken isimleri anlamlı olsun
- Best practices uygula
- Hata yönetimi (error handling) ekle

ÇIKTI:
- Tam çalışır {task_config.file_name} dosyası
- Kod içinde açıklayıcı yorumlar
- Gerekirse configuration dosyası

KABUL KRITERLERI:
✓ Kod çalışıyor ve test edilmiş
✓ Tüm gereksinimler karşılanmış
✓ Kod temiz ve okunabilir
✓ Dokümantasyon eklenmiş
            """,
            issue_type="Task",
            assignee_email=JIRA_EMAIL
        )
        if task1:
            tasks.append(task1['key'])

        # Task 2: QA/Test Task
        task2 = jira.create_issue(
            summary=f"[QA] {task_config.project_name} - Test ve Kalite Kontrolü",
            description=f"""
{task_config.project_name} projesi için test senaryoları oluştur ve test yap.

TEST ADIM LARI:
1. Fonksiyonel test senaryoları oluştur
2. Edge case'leri belirle
3. Her senaryoyu test et
4. Bulunan hataları raporla
5. Performans kontrolü yap
6. Kod kalitesi incelemesi

KOD İNCELEMESİ KONTROL LISTESİ:
- Kod okunabilirliği
- Best practices uyumu
- Hata yönetimi
- Performans
- Güvenlik açıkları
- Eksik özellikler

ÇIKTI:
- Test senaryoları dokümanı
- Test raporu
- Bug listesi (varsa)
- Performans analizi
- İyileştirme önerileri
            """,
            issue_type="Test",
            assignee_email=JIRA_EMAIL
        )
        if task2:
            tasks.append(task2['key'])

        # Task 3: Project Management / Review Task
        task3 = jira.create_issue(
            summary=f"[PM] {task_config.project_name} - Kod Review ve Tamamlama",
            description=f"""
Proje yöneticisi olarak {task_config.project_name} projesini gözden geçir.

YAPILACAKLAR:
1. Kod kalitesi kontrolü
2. Test sonuçlarını incele
3. Tüm gereksinimlerin karşılandığını kontrol et
4. Bug'ların düzeltildiğini kontrol et
5. Dokümantasyonu kontrol et
6. Final raporu hazırla
7. Projeyi tamamla

KONTROL NOKTALARI:
✓ Tüm gereksinimler implement edilmiş mi?
✓ Test coverage yeterli mi?
✓ Kod standartlara uygun mu?
✓ Dokümantasyon tam mı?
✓ Performans kabul edilebilir mi?
✓ Güvenlik kontrolleri yapıldı mı?

ÇIKTI:
- Kod review raporu
- Final değerlendirme raporu
- Proje tamamlama onayı
- Deployment notları (gerekirse)
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


def write_code_to_file(code: str, filename: str):
    """
    AI tarafından üretilen kodu dosyaya yazar
    """
    # Kod bloklarını temizle
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```javascript" in code:
        code = code.split("```javascript")[1].split("```")[0]
    elif "```java" in code:
        code = code.split("```java")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]

    code = code.strip()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n✅ Kod {filename} dosyasına yazıldı!")


def create_agents(task_config: TaskConfig):
    """
    AI ajanlarını oluşturur (Parametrik)
    """
    # 1. Proje Yöneticisi
    proje_yoneticisi = Agent(
        role='Proje Yöneticisi (PM)',
        goal=f'{task_config.project_name} projesini yönetmek, Jira task\'larını oluşturmak ve ekibi koordine etmek',
        backstory=f"""
        Sen deneyimli bir proje yöneticisisin ve Jira konusunda uzmansın.
        {task_config.project_name} projesi için detaylı bir plan hazırlayacak ve
        Jira'da gerekli task'ları oluşturacaksın.

        Görevlerin:
        - Proje kapsamını belirle
        - Detaylı task'ları planla
        - Her task için net gereksinimler yaz
        - Kabul kriterlerini tanımla
        - Risk analizi yap
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # 2. Yazılımcı
    yazilimci = Agent(
        role=f'Kıdemli {task_config.programming_language} Yazılımcı (Developer)',
        goal=f'Yüksek kaliteli, çalışan {task_config.programming_language} kodu yazmak',
        backstory=f"""
        Sen {task_config.programming_language} konusunda uzman bir yazılımcısın.
        {task_config.project_name} projesini sıfırdan kodlayabiliyorsun.

        Özellikler:
        - Temiz, okunabilir kod yazarsın
        - Kod içine yorumlar eklersin
        - Best practice'lere uygun kodlarsın
        - SOLID prensiplerini uygularsın
        - Hata yönetimi ve edge case'leri düşünürsün

        ÖNEMLİ: Kodunu her zaman uygun kod bloğu içinde ver!
        Python için ```python```, JavaScript için ```javascript``` vb.
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # 3. Güvenlik Uzmanı
    guvenlik_uzmani = Agent(
        role='Uygulama Güvenlik Uzmanı (AppSec Engineer)',
        goal='Kodun güvenliğini sağlamak ve zafiyetleri tespit etmek',
        backstory=f"""
        Sen deneyimli bir Güvenlik Mühendisisin (AppSec).
        {task_config.programming_language} kodlarını satır satır inceler,
        OWASP Top 10 ve diğer güvenlik standartlarına göre analiz edersin.

        Görevlerin:
        - Kod incelemesi (SAST) yap
        - Hardcoded secret'ları bul
        - SQL Injection, XSS, CSRF gibi açıkları tespit et
        - Güvenli kodlama önerileri sun
        - Yanlış konfigürasyonları belirle

        ÖNEMLİ: Güvenlik açığı bulursan, çözümünü de mutlaka önermelisin.
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # 4. Testçi
    testci = Agent(
        role='Test Uzmanı (QA Engineer)',
        goal='Kodu test etmek, hataları bulmak ve kalite kontrolü yapmak',
        backstory=f"""
        Sen detaycı bir test uzmanısın ve {task_config.programming_language} kodunu analiz edebiliyorsun.
        Kodları inceler, olası hataları tespit eder, edge case'leri düşünürsün.

        Görevlerin:
        - Detaylı test senaryoları oluştur
        - Her senaryoyu dikkatlice test et
        - Bulunan hataları listele
        - Her hata için açıklayıcı bug raporu hazırla
        - Performans analizi yap
        - Güvenlik açıklarını kontrol et
        - İyileştirme önerileri sun

        Bug raporu formatı:
        - Bug başlığı
        - Adımlar (nasıl oluşuyor)
        - Beklenen davranış
        - Gerçek davranış
        - Öncelik (Yüksek/Orta/Düşük)
        - Önerilen çözüm
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    return proje_yoneticisi, yazilimci, guvenlik_uzmani, testci


def create_tasks(task_config: TaskConfig, agents: tuple):
    """
    AI görevlerini oluşturur (Parametrik)
    """
    proje_yoneticisi, yazilimci, guvenlik_uzmani, testci = agents

    # Görev 1: PM Proje Planı Oluşturur
    gorev1_pm_planlama = Task(
        description=f"""
        {task_config.project_name} projesi için detaylı bir proje planı oluştur.

        PROJE KAPSAMI:
        {task_config.description}

        TEKNIK GEREKSINIMLER:
{task_config.get_formatted_requirements()}

        PROGRAMLAMA DILI: {task_config.programming_language}
        HEDEF DOSYA: {task_config.file_name}

        {task_config.additional_notes}

        PLANI ŞÖYLE HAZIRLA:
        1. Proje özeti
        2. Teknik gereksinimler (detaylı)
        3. Mimari tasarım kararları
        4. Görevler ve sorumlular
        5. Kabul kriterleri
        6. Riskler ve kısıtlar
        7. Zaman tahmini

        ÇIKTI: Detaylı proje planı (300-400 kelime)
        """,
        agent=proje_yoneticisi,
        expected_output="Detaylı proje planı ve görev tanımları"
    )

    # Görev 2: Developer Kodu Yazar
    gorev2_dev_kodlama = Task(
        description=f"""
        PM'in belirlediği gereksinimlere göre {task_config.project_name} projesini kodla.

        GEREKSINIMLER:
{task_config.get_formatted_requirements()}

        PROGRAMLAMA DILI: {task_config.programming_language}
        DOSYA ADI: {task_config.file_name}

        KODLAMA KURALLARI:
        - Temiz ve okunabilir kod
        - Fonksiyonlar için docstring/yorum ekle
        - Değişken isimleri anlamlı olsun (camelCase veya snake_case)
        - Best practices uygula
        - Hata yönetimi ekle (try-except, error handling)
        - Edge case'leri düşün
        - SOLID prensiplerini uygula
        - Gerekirse configuration ayarları ekle

        ÖNEMLI:
        - Kodun TAMAMINI uygun kod bloğu içinde ver!
        - Python için ```python```, JavaScript için ```javascript``` kullan
        - Eksik bırakma, tüm kodu yaz!
        - Kodun çalışır durumda olmasına özen göster

        ÇIKTI: Tam çalışır {task_config.file_name} kodu
        """,
        agent=yazilimci,
        expected_output=f"Tam çalışır {task_config.file_name} kodu",
        context=[gorev1_pm_planlama]
    )

    # Görev 3: Güvenlik Uzmanı Kod İncelemesi
    gorev3_sec_review = Task(
        description=f"""
        Yazılımcının kodladığı {task_config.project_name} projesi için güvenlik incelemesi yap.

        GEREKSINIMLER:
        - OWASP Top 10 güvenlik açıklarını kontrol et
        - Hardcoded credentials (API Key, şifre vb.) ara
        - Input validation eksikliklerini belirle
        - SQL Injection, XSS gibi riskleri analiz et
        - Güvenli kodlama standartlarına uyumu kontrol et

        KONTROL LISTESI:
        1. Hassas veriler korunuyor mu?
        2. Yetkilendirme kontrolleri var mı?
        3. Hata mesajları hassas bilgi sızdırıyor mu?
        4. Bağımlılıklar güncel mi?

        ÇIKTI:
        - Güvenlik Risk Raporu (Risk Seviyesi ile)
        - Bulunan açıklar ve çözüm önerileri
        - Güvenlik puanı (0-100)
        """,
        agent=guvenlik_uzmani,
        expected_output="Güvenlik Risk Raporu ve Çözüm Önerileri",
        context=[gorev2_dev_kodlama]
    )

    # Görev 4: QA Test Eder
    gorev4_qa_test = Task(
        description=f"""
        Yazılımcının kodladığı {task_config.project_name} projesi için test senaryoları oluştur ve kodu incele.

        TEST SENARYOLARI OLUŞTUR:
        - Fonksiyonel testler (her özellik için)
        - Edge case'ler (sınır değerler, null, empty vb.)
        - Hata durumları (invalid input, exceptions)
        - Performans testleri
        - Güvenlik testleri (SQL injection, XSS vb. varsa)
        - Entegrasyon testleri (gerekirse)

        HER SENARYO İÇİN:
        - Test ID (TS-001, TS-002, vb.)
        - Test adımları
        - Beklenen sonuç
        - Kod incelemesi sonucu
        - Potansiyel hatalar

        KOD İNCELEMESI:
        - Kod kalitesi ve okunabilirlik
        - Best practices uyumu
        - Performans optimizasyonu
        - Hata yönetimi
        - Güvenlik açıkları
        - Eksik özellikler
        - Potansiyel bug'lar
        - Refactoring önerileri

        ÇIKTI:
        1. Test senaryoları listesi (numaralı)
        2. Detaylı kod inceleme raporu
        3. Bulunan hatalar/eksikler (varsa)
        4. Güvenlik analizi
        5. Performans değerlendirmesi
        6. İyileştirme önerileri
        """,
        agent=testci,
        expected_output="Test senaryoları, kod inceleme raporu ve bug listesi",
        context=[gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_sec_review]
    )

    return gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_sec_review, gorev4_qa_test


# ============================================================
# MAIN - PROJEYİ ÇALIŞTIR (PARAMETRIK)
# ============================================================

def run_task_project(task_config: TaskConfig):
    """
    Parametrik task projesi çalıştırır
    """
    print("\n" + "=" * 60)
    print(f"🚀 {task_config.project_name.upper()}")
    print("=" * 60)
    print(f"📝 Açıklama: {task_config.description}")
    print(f"💻 Programlama Dili: {task_config.programming_language}")
    print(f"📄 Hedef Dosya: {task_config.file_name}")
    print("👥 Ekip: Proje Yöneticisi, Yazılımcı, Test Uzmanı")
    print(f"🔗 Jira Projesi: {PROJECT_KEY}")
    print("=" * 60)

    # Jira bağlantısını test et
    print("\n🔍 Jira bağlantısı kontrol ediliyor...")
    test_issues = jira.get_issues(max_results=1)
    if test_issues is not None:
        print("✅ Jira bağlantısı başarılı!")
    else:
        print("❌ Jira bağlantısı başarısız! Program sonlandırılıyor.")
        return

    # Ajanları oluştur
    agents = create_agents(task_config)
    proje_yoneticisi, yazilimci, guvenlik_uzmani, testci = agents

    # Görevleri oluştur
    tasks = create_tasks(task_config, agents)
    gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_sec_review, gorev4_qa_test = tasks

    # Ekip oluştur
    ekip = Crew(
        agents=[proje_yoneticisi, yazilimci, guvenlik_uzmani, testci],
        tasks=[gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_sec_review, gorev4_qa_test],
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
    created_tasks = create_jira_tasks_from_plan(plan, task_config)

    # 2. Kodu dosyaya yaz
    kod = str(gorev2_dev_kodlama.output) if hasattr(gorev2_dev_kodlama, 'output') else ""
    if kod and len(kod) > 100:
        write_code_to_file(kod, task_config.file_name)

        # İlk task'ı "In Progress" yap
        if created_tasks and len(created_tasks) > 0:
            jira.update_issue_status(created_tasks[0], "In Progress")
            jira.add_comment(created_tasks[0], f"✅ Kod yazıldı: {task_config.file_name}\n\nKod AI tarafından oluşturuldu ve dosyaya kaydedildi.")

    # 3. Güvenlik raporunu Jira'ya ekle
    guvenlik_raporu = str(gorev3_sec_review.output) if hasattr(gorev3_sec_review, 'output') else ""
    if guvenlik_raporu and created_tasks and len(created_tasks) > 0:
        jira.add_comment(created_tasks[0], f"🔒 GÜVENLİK İNCELEME RAPORU:\n\n{guvenlik_raporu}")
        print("\n✅ Güvenlik raporu Jira'ya eklendi.")

    # 4. Test raporunu Jira'ya ekle
    test_raporu = str(gorev4_qa_test.output) if hasattr(gorev4_qa_test, 'output') else ""
    if test_raporu and created_tasks and len(created_tasks) > 1:
        jira.add_comment(created_tasks[1], f"📋 TEST RAPORU:\n\n{test_raporu}")

    # 4. Raporu kaydet
    report_filename = f"{task_config.file_name.replace('.', '_')}_project_report.txt"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"{task_config.project_name.upper()} - PROJE RAPORU\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"📊 Proje: {task_config.project_name}\n")
        f.write(f"📝 Açıklama: {task_config.description}\n")
        f.write(f"💻 Dil: {task_config.programming_language}\n")
        f.write(f"📄 Dosya: {task_config.file_name}\n\n")
        f.write("📊 OLUŞTURULAN JIRA TASK'LARI:\n")
        for task_key in created_tasks:
            f.write(f"  - {task_key}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        f.write(str(sonuc))

    print(f"\n✅ Rapor '{report_filename}' dosyasına kaydedildi.")
    print(f"✅ Kod '{task_config.file_name}' dosyasına kaydedildi.")
    print(f"✅ Jira'da {len(created_tasks)} task oluşturuldu!")
    print("\n" + "=" * 60)


# ============================================================
# ÖRNEK KULLANIM
# ============================================================

if __name__ == "__main__":
    # Örnek Task Konfigürasyonu
    task_config = TaskConfig(
        project_name="Web API Geliştirme",
        description="RESTful API ile kullanıcı yönetim sistemi",
        requirements=[
            "FastAPI framework kullan",
            "PostgreSQL veritabanı",
            "JWT authentication",
            "CRUD operasyonları",
            "Input validation",
            "Error handling",
            "API documentation (OpenAPI/Swagger)"
        ],
        file_name="user_api.py",
        programming_language="Python",
        additional_notes="API'nin production-ready olmasına dikkat et. Security best practices uygula."
    )

    # Projeyi çalıştır
    run_task_project(task_config)
