"""
Trello Entegrasyonlu AI Ajanlar - Parametrik Task Yonetim Sistemi
3 Kisilik Ekip: Proje Yoneticisi, Yazilimci, Testci

Trello board'unda kartlar olusturur ve is akisini yonetir.
"""
import os
import signal
import sys
import io

# Windows encoding fix
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
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
from trello_helper import TrelloHelper

# ============================================================
# YAPILANDIRMA
# ============================================================

# Trello Bilgileri
# API Key ve Token almak için: https://trello.com/power-ups/admin
TRELLO_API_KEY = "27cf0f02c65de97bf9f699cd79b5fc18"
TRELLO_TOKEN = "YOUR_TRELLO_TOKEN"
TRELLO_BOARD_ID = None  # Opsiyonel - mevcut board ID veya None (yeni board oluşturulur)

# OpenAI API Key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM Modeli
my_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Trello Helper oluştur
trello = TrelloHelper(TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID)


# ============================================================
# TASK CONFIGURATION CLASS
# ============================================================

class TaskConfig:
    """
    Parametrik task yapılandırma sınıfı

    Attributes:
        project_name: Proje adı
        description: Proje açıklaması
        requirements: Teknik gereksinimler listesi
        file_name: Oluşturulacak dosya adı
        programming_language: Programlama dili (varsayılan: Python)
        additional_notes: Ek notlar (opsiyonel)
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
        return "\n".join([f"- {req}" for req in self.requirements])


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def create_trello_cards_from_plan(plan_text: str, task_config: TaskConfig, list_ids: Dict[str, str]) -> Dict[str, str]:
    """
    Proje planından Trello kartları oluşturur

    Args:
        plan_text: Proje planı metni
        task_config: Task yapılandırma objesi
        list_ids: Liste ID'leri dict (Backlog, To Do, vb.)

    Returns:
        Oluşturulan kartların ID'leri (dict)
    """
    print("\n" + "=" * 60)
    print("📋 TRELLO KARTLARI OLUŞTURULUYOR")
    print("=" * 60)

    cards = {}

    # Kart 1: Development Task (To Do listesinde)
    dev_card = trello.create_card(
        name=f"[DEV] {task_config.project_name}",
        description=f"""# {task_config.project_name}

{task_config.description}

## Gereksinimler
{task_config.get_formatted_requirements()}

## Programlama Dili
{task_config.programming_language}

## Dosya Adı
`{task_config.file_name}`

## Kodlama Kuralları
- Temiz ve okunabilir kod
- Fonksiyonlar için açıklayıcı yorumlar
- Değişken isimleri anlamlı olsun
- Best practices uygula
- Hata yönetimi ekle

## Kabul Kriterleri
✓ Kod çalışıyor ve test edilmiş
✓ Tüm gereksinimler karşılanmış
✓ Kod temiz ve okunabilir
✓ Dokümantasyon eklenmiş

---
**Proje Planı:**
{plan_text[:500]}...
        """,
        list_id=list_ids.get("To Do"),
        labels=["green"]  # Yeşil label: Development
    )

    if dev_card:
        cards["dev"] = dev_card['id']
        print(f"   ✅ DEV kartı: {dev_card['shortUrl']}")

    # Kart 2: QA/Test Task (To Do listesinde)
    qa_card = trello.create_card(
        name=f"[QA] {task_config.project_name} - Test",
        description=f"""# Test ve Kalite Kontrolü

{task_config.project_name} projesi için test senaryoları oluştur ve test yap.

## Test Adımları
1. Fonksiyonel test senaryoları oluştur
2. Edge case'leri belirle
3. Her senaryoyu test et
4. Bulunan hataları raporla
5. Performans kontrolü yap
6. Kod kalitesi incelemesi

## Kod İncelemesi Kontrol Listesi
- [ ] Kod okunabilirliği
- [ ] Best practices uyumu
- [ ] Hata yönetimi
- [ ] Performans
- [ ] Güvenlik açıkları
- [ ] Eksik özellikler

## Çıktı
- Test senaryoları dokümanı
- Test raporu
- Bug listesi (varsa)
- Performans analizi
- İyileştirme önerileri
        """,
        list_id=list_ids.get("To Do"),
        labels=["yellow"]  # Sarı label: Testing
    )

    if qa_card:
        cards["qa"] = qa_card['id']
        print(f"   ✅ QA kartı: {qa_card['shortUrl']}")

    # Kart 3: Project Management / Review (To Do listesinde)
    pm_card = trello.create_card(
        name=f"[PM] {task_config.project_name} - Review",
        description=f"""# Kod Review ve Proje Tamamlama

Proje yöneticisi olarak {task_config.project_name} projesini gözden geçir.

## Yapılacaklar
- [ ] Kod kalitesi kontrolü
- [ ] Test sonuçlarını incele
- [ ] Tüm gereksinimlerin karşılandığını kontrol et
- [ ] Bug'ların düzeltildiğini kontrol et
- [ ] Dokümantasyonu kontrol et
- [ ] Final raporu hazırla
- [ ] Projeyi tamamla

## Kontrol Noktaları
✓ Tüm gereksinimler implement edilmiş mi?
✓ Test coverage yeterli mi?
✓ Kod standartlara uygun mu?
✓ Dokümantasyon tam mı?
✓ Performans kabul edilebilir mi?
✓ Güvenlik kontrolleri yapıldı mı?

## Çıktı
- Kod review raporu
- Final değerlendirme raporu
- Proje tamamlama onayı
        """,
        list_id=list_ids.get("To Do"),
        labels=["purple"]  # Mor label: Management
    )

    if pm_card:
        cards["pm"] = pm_card['id']
        print(f"   ✅ PM kartı: {pm_card['shortUrl']}")

    print(f"\n✅ Toplam {len(cards)} kart oluşturuldu!")
    print("=" * 60)

    return cards


def write_code_to_file(code: str, filename: str):
    """
    AI tarafından üretilen kodu dosyaya yazar

    Args:
        code: Kod içeriği
        filename: Dosya adı
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
    AI ajanlarını oluşturur

    Args:
        task_config: Task yapılandırma objesi

    Returns:
        Tuple of (proje_yoneticisi, yazilimci, testci)
    """
    # 1. Proje Yöneticisi
    proje_yoneticisi = Agent(
        role='Proje Yöneticisi (PM)',
        goal=f'{task_config.project_name} projesini yönetmek, Trello kartlarını organize etmek',
        backstory=f"""
        Sen deneyimli bir proje yöneticisisin ve Trello konusunda uzmansın.
        {task_config.project_name} projesi için detaylı bir plan hazırlayacaksın.

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
        role=f'Kıdemli {task_config.programming_language} Yazılımcı',
        goal=f'Yüksek kaliteli, çalışan {task_config.programming_language} kodu yazmak',
        backstory=f"""
        Sen {task_config.programming_language} konusunda uzman bir yazılımcısın.

        Özellikler:
        - Temiz, okunabilir kod yazarsın
        - Best practice'lere uygun kodlarsın
        - SOLID prensiplerini uygularsın
        - Hata yönetimi ve edge case'leri düşünürsün

        ÖNEMLI: Kodunu her zaman uygun kod bloğu içinde ver!
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # 3. Testçi
    testci = Agent(
        role='Test Uzmanı (QA Engineer)',
        goal='Kodu test etmek, bug bulmak ve Trello\'da bug kartı açmak',
        backstory=f"""
        Sen detaycı bir test uzmanısın.

        Görevlerin:
        - Detaylı test senaryoları oluştur
        - Bulunan hataları listele
        - Bug raporu hazırla
        - Performans analizi yap
        - Güvenlik açıklarını kontrol et

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

    return proje_yoneticisi, yazilimci, testci


def create_tasks(task_config: TaskConfig, agents: tuple):
    """
    AI görevlerini oluşturur

    Args:
        task_config: Task yapılandırma objesi
        agents: (proje_yoneticisi, yazilimci, testci) tuple

    Returns:
        Tuple of (gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_qa_test)
    """
    proje_yoneticisi, yazilimci, testci = agents

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

        ÇIKTI: Detaylı proje planı
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
        - Değişken isimleri anlamlı olsun
        - Best practices uygula
        - Hata yönetimi ekle

        ÖNEMLI: Kodun TAMAMINI uygun kod bloğu içinde ver!

        ÇIKTI: Tam çalışır {task_config.file_name} kodu
        """,
        agent=yazilimci,
        expected_output=f"Tam çalışır {task_config.file_name} kodu",
        context=[gorev1_pm_planlama]
    )

    # Görev 3: QA Test Eder
    gorev3_qa_test = Task(
        description=f"""
        Yazılımcının kodladığı {task_config.project_name} projesi için test senaryoları oluştur ve kodu incele.

        TEST SENARYOLARI OLUŞTUR:
        - Fonksiyonel testler
        - Edge case'ler
        - Hata durumları
        - Performans testleri
        - Güvenlik testleri

        KOD İNCELEMESİ:
        - Kod kalitesi
        - Best practices uyumu
        - Performans
        - Hata yönetimi
        - Güvenlik açıkları
        - Potansiyel bug'lar

        Bug bulursan MUTLAKA şu formatta yaz:
        Bug 1: [Bug başlığı]
        Açıklama: ...
        Öncelik: Yüksek/Orta/Düşük

        Bug 2: [Bug başlığı]
        Açıklama: ...
        Öncelik: ...

        ÇIKTI:
        1. Test senaryoları listesi
        2. Kod inceleme raporu
        3. NUMARALI Bug listesi (varsa)
        4. İyileştirme önerileri
        """,
        agent=testci,
        expected_output="Test senaryoları, kod inceleme raporu ve bug listesi",
        context=[gorev1_pm_planlama, gorev2_dev_kodlama]
    )

    return gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_qa_test


def handle_bugs(bug_report: str, list_ids: Dict[str, str], project_name: str):
    """
    Bug raporunu analiz edip Trello'da bug kartları oluşturur (Her bug için ayrı kart)

    Args:
        bug_report: Test uzmanının bug raporu
        list_ids: Liste ID'leri
        project_name: Proje adı
    """
    import re

    # Bug'ları parse et
    # Format: "Bug 1:", "Hata 1:", "BUG-001:", vb.
    bug_pattern = r'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*(\d+)[:\s]*([^\n]+)'
    bugs_found = re.findall(bug_pattern, bug_report, re.IGNORECASE)

    if bugs_found:
        print("\n" + "=" * 60)
        print(f"🐛 {len(bugs_found)} BUG TESPİT EDİLDİ - TRELLO'DA KARTLAR OLUŞTURULUYOR")
        print("=" * 60)

        for bug_num, bug_title in bugs_found:
            # Bug detaylarını bul (bug numarasından sonraki paragraf)
            bug_detail_pattern = rf'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*{bug_num}[:\s]*{re.escape(bug_title)}([\s\S]*?)(?=(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*\d+|$)'
            detail_match = re.search(bug_detail_pattern, bug_report, re.IGNORECASE)

            bug_details = detail_match.group(1).strip() if detail_match else "Detay bulunamadi"

            # Öncelik belirle (bug açıklamasından)
            priority = "Orta"
            priority_label = "orange"
            if any(word in bug_details.lower() for word in ["yuksek", "kritik", "high", "critical"]):
                priority = "Yuksek"
                priority_label = "red"
            elif any(word in bug_details.lower() for word in ["dusuk", "low", "minor"]):
                priority = "Dusuk"
                priority_label = "yellow"

            # Bug kartı oluştur
            bug_card = trello.create_card(
                name=f"🐛 [BUG-{bug_num}] {bug_title.strip()}",
                description=f"""# Bug Raporu

**Proje:** {project_name}
**Bug ID:** BUG-{bug_num}
**Oncelik:** {priority}

---

## Aciklama
{bug_details}

---

## Durum
Yeni bug - incelenmesi gerekiyor

## Atama
Developer'a atanacak

---

**Kaynak:** QA Agent Test Raporu
                """,
                list_id=list_ids.get("Bugs"),
                labels=[priority_label]
            )

            if bug_card:
                print(f"   ✅ Bug kartı oluşturuldu: BUG-{bug_num} - {bug_title.strip()[:50]}...")
                print(f"      URL: {bug_card['shortUrl']}")

        print("=" * 60)
    else:
        # Genel bug tespiti (keyword bazlı)
        bug_keywords = ["bug", "hata", "error", "problem", "issue", "yanlış", "çalışmıyor", "eksik"]

        if any(keyword in bug_report.lower() for keyword in bug_keywords):
            print("\n" + "=" * 60)
            print("🐛 BUG TESPİT EDİLDİ - TRELLO'DA GENEL BUG KARTI OLUŞTURULUYOR")
            print("=" * 60)

            # Genel bug kartı oluştur
            bug_card = trello.create_card(
                name=f"🐛 [BUG] {project_name} - Kod Incelemesinde Bulunan Hatalar",
                description=f"""# Bug Raporu

**Proje:** {project_name}

---

## Test Sonuçları
{bug_report[:1000]}...

---

## Oncelik
🔴 Yuksek

## Durum
Yeni bug - incelenmesi gerekiyor

## Not
Bug'lar numaralanmamis. Raporu inceleyin ve ayri kartlar acin.
                """,
                list_id=list_ids.get("Bugs"),
                labels=["red"]
            )

            if bug_card:
                print(f"   ✅ Genel bug kartı oluşturuldu: {bug_card['shortUrl']}")
                print("=" * 60)


# ============================================================
# MAIN - PROJEYİ ÇALIŞTIR
# ============================================================

def run_task_project(task_config: TaskConfig):
    """
    Parametrik task projesi çalıştırır (Trello ile)

    Args:
        task_config: TaskConfig objesi
    """
    print("\n" + "=" * 60)
    print(f"🚀 {task_config.project_name.upper()} - TRELLO ENTEGRASYONU")
    print("=" * 60)
    print(f"📝 Açıklama: {task_config.description}")
    print(f"💻 Programlama Dili: {task_config.programming_language}")
    print(f"📄 Hedef Dosya: {task_config.file_name}")
    print("👥 Ekip: Proje Yöneticisi, Yazılımcı, Test Uzmanı")
    print("🔗 Platform: Trello")
    print("=" * 60)

    # Trello board'u hazırla
    print("\n🔍 Trello board yapısı oluşturuluyor...")

    board_structure = trello.setup_board_structure(f"AI Agents - {task_config.project_name}")
    if not board_structure:
        print("❌ Trello board oluşturulamadı! Program sonlandırılıyor.")
        return

    list_ids = board_structure["lists"]
    board = board_structure["board"]

    print(f"\n✅ Board hazır: {board['url']}")
    print("=" * 60)

    # Ajanları oluştur
    agents = create_agents(task_config)
    proje_yoneticisi, yazilimci, testci = agents

    # Görevleri oluştur
    tasks = create_tasks(task_config, agents)
    gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_qa_test = tasks

    # Ekip oluştur
    ekip = Crew(
        agents=[proje_yoneticisi, yazilimci, testci],
        tasks=[gorev1_pm_planlama, gorev2_dev_kodlama, gorev3_qa_test],
        verbose=True,
        process=Process.sequential
    )

    print("\n🚀 AI Ekibi çalışmaya başlıyor...\n")
    print("=" * 60)

    # Ekibi çalıştır
    sonuc = ekip.kickoff()

    print("\n" + "=" * 60)
    print("🎯 EKİP ÇALIŞMASINI TAMAMLADI!")
    print("=" * 60)

    # Sonuçları işle
    print("\n📝 SONUÇLAR İŞLENİYOR VE TRELLO'YA AKTARILIYOR...")

    # 1. Proje planını al ve Trello kartlarını oluştur
    plan = str(gorev1_pm_planlama.output) if hasattr(gorev1_pm_planlama, 'output') else str(sonuc)
    cards = create_trello_cards_from_plan(plan, task_config, list_ids)

    # 2. Kodu dosyaya yaz
    kod = str(gorev2_dev_kodlama.output) if hasattr(gorev2_dev_kodlama, 'output') else ""
    if kod and len(kod) > 100:
        write_code_to_file(kod, task_config.file_name)

        # DEV kartını "In Progress" listesine taşı ve yorum ekle
        if "dev" in cards:
            trello.move_card(cards["dev"], list_id=list_ids.get("In Progress"))
            trello.add_comment(cards["dev"], f"✅ Kod yazıldı: {task_config.file_name}\n\nKod AI tarafından oluşturuldu ve dosyaya kaydedildi.")
            # Code Review'e taşı
            trello.move_card(cards["dev"], list_id=list_ids.get("Code Review"))

    # 3. Test raporunu al
    test_raporu = str(gorev3_qa_test.output) if hasattr(gorev3_qa_test, 'output') else ""

    # QA kartını "Testing" listesine taşı ve test raporunu ekle
    if test_raporu and "qa" in cards:
        trello.move_card(cards["qa"], list_id=list_ids.get("Testing"))
        trello.add_comment(cards["qa"], f"📋 TEST RAPORU:\n\n{test_raporu}")

    # 4. Bug varsa bug kartı oluştur
    if test_raporu:
        handle_bugs(test_raporu, list_ids, task_config.project_name)

    # 5. PM kartını güncelle
    if "pm" in cards:
        trello.move_card(cards["pm"], list_id=list_ids.get("Code Review"))
        trello.add_comment(cards["pm"], f"📊 PROJE DURUMU:\n\n- Kod yazıldı ✓\n- Test edildi ✓\n- Kod review bekliyor")

    # 6. Raporu kaydet
    report_filename = f"{task_config.file_name.replace('.', '_')}_trello_report.txt"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"{task_config.project_name.upper()} - TRELLO PROJE RAPORU\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"📊 Proje: {task_config.project_name}\n")
        f.write(f"📝 Açıklama: {task_config.description}\n")
        f.write(f"💻 Dil: {task_config.programming_language}\n")
        f.write(f"📄 Dosya: {task_config.file_name}\n")
        f.write(f"🔗 Board: {board['url']}\n\n")
        f.write("📊 OLUŞTURULAN TRELLO KARTLARI:\n")
        for card_name, card_id in cards.items():
            card_info = trello.get_card(card_id)
            if card_info:
                f.write(f"  - [{card_name.upper()}] {card_info['name']}: {card_info['shortUrl']}\n")
        f.write("\n" + "=" * 60 + "\n\n")
        f.write(str(sonuc))

    print(f"\n✅ Rapor '{report_filename}' dosyasına kaydedildi.")
    print(f"✅ Kod '{task_config.file_name}' dosyasına kaydedildi.")
    print(f"✅ Trello board'da {len(cards)} kart oluşturuldu!")
    print(f"🔗 Board URL: {board['url']}")
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
        additional_notes="API'nin production-ready olmasına dikkat et."
    )

    # Projeyi çalıştır
    run_task_project(task_config)
