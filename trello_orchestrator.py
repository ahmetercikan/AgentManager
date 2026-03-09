"""
Trello Orchestrator - Backlog'dan Otomatik Is Cekme Sistemi

Trello Backlog listesini izler, yeni kartlari alir ve AI ajanlarina dagitir.
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

# Windows duzeltmesi
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
TRELLO_API_KEY = "27cf0f02c65de97bf9f699cd79b5fc18"
TRELLO_TOKEN = "YOUR_TRELLO_TOKEN"

# OpenAI API Key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM Modeli
my_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Trello Helper
trello = TrelloHelper(TRELLO_API_KEY, TRELLO_TOKEN)

# ============================================================
# SKILL YUKLEME
# ============================================================

def load_skill(skill_name: str) -> str:
    """skills/ klasorundan skill dosyasini yukler"""
    skill_path = os.path.join(os.path.dirname(__file__), 'skills', f'{skill_name}.md')
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️  Skill dosyasi bulunamadi: {skill_path}")
        return ""

# ============================================================
# ORCHESTRATOR - ANALIST AGENT
# ============================================================

def create_analyst_agent():
    """
    Backlog'daki kartlari analiz eden Analist Agent - Is Analisti Skill Destekli
    """
    analyst_skill = load_skill('is_analisti')

    return Agent(
        role='Kidemli Is Analist',
        goal='Trello Backlog kartlarini analiz edip teknik gereksinimlere donusturmek',
        backstory=f"""
        Sen deneyimli bir is analistisin. Kullanicinin yazdigi genel istekleri
        alip bunlari teknik gereksinimlere donusturuyorsun.

        Gorevlerin:
        - Kullanicinin istegini anla
        - Proje adini belirle
        - Proje tipini belirle (backend, frontend, fullstack, cli, mobile vb.)
        - Programlama dilini/framework'u sec
        - Detayli gereksinimleri cikar
        - Dosya adlarini belirle (backend ve frontend ayri ise ikisini de belirt)

        ========================
        IS ANALISTI PRO KURALLARI:
        ========================
        {analyst_skill}

        ONEMLI: Ciktin JSON formatinda olmali ve su yapiyi takip etmeli:
        {{
            "project_name": "Proje Adi",
            "description": "Kisa aciklama",
            "project_type": "fullstack",
            "programming_language": "Python",
            "file_name": "main.py",
            "requirements": ["Req 1", "Req 2"]
        }}
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_solution_architect_agent():
    """
    Teknik mimariyi tasarlayan Solution Architect Agent - Architect Skill Destekli
    """
    architect_skill = load_skill('solution_architect')

    return Agent(
        role='Kidemli Cozum Mimari (Solution Architect)',
        goal='Analist ciktisini teknik mimariye donusturmek ve validasyon yapmak',
        backstory=f"""
        Sen deneyimli bir Cozum Mimari'sin.
        Analistin belirledigi gereksinimleri alir, teknik olarak en uygun mimariyi tasarlarsin.

        Gorevlerin:
        - DB Semasini tasarla (Tablolar, alanlar)
        - API Endpoint'lerini belirle
        - Kullanilacak kutuphaneleri sec
        - Scalability ve Performance acisindan degerlendir
        - Analistin planinda eksik varsa tamamla

        ========================
        SOLUTION ARCHITECT PRO KURALLARI:
        ========================
        {architect_skill}

        CIKTI:
        Detayli teknik tasarim dokumani (Markdown formatinda)
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_orchestrator_agent():
    """
    Isleri dagitan Orchestrator Agent
    """
    return Agent(
        role='Orkestrator (Proje Yoneticisi)',
        goal='Analiz edilmis isleri PM, Developer, QA ajanlarına dagitmak',
        backstory="""
        Sen deneyimli bir proje yoneticisisin ve ekip koordinasyonu konusunda uzmansin.
        Analistten gelen teknik gereksinimleri alip detayli bir proje plani olusturuyorsun.

        Gorevlerin:
        - Projeyi planla
        - Detayli task'lari tanimla
        - Kabul kriterlerini belirle
        - Riskleri tespit et
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_backend_developer_agent(programming_language: str = "Python"):
    """Backend Developer Agent - Backend Developer Skill Destekli"""
    backend_skill = load_skill('backend_developer')

    return Agent(
        role=f'Kidemli Backend Developer ({programming_language})',
        goal=f'Yuksek kaliteli backend {programming_language} kodu yazmak - API, veritabani, is mantigi',
        backstory=f"""
        Sen {programming_language} konusunda uzman bir backend gelistiricisisin.

        ========================
        BACKEND DEVELOPER PRO KURALLARI:
        ========================
        {backend_skill}

        ONEMLI: Kodunu her zaman kod blogu icinde ver!
        Python icin ```python```, JavaScript icin ```javascript```
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_frontend_developer_agent(framework: str = "React"):
    """Frontend Developer Agent - Frontend Design Pro Skill Destekli (UI/UX + Glassmorphism birleşik)"""

    # Frontend Design Pro skill'ini yukle
    frontend_skill = load_skill('frontend_design_pro')

    return Agent(
        role=f'Kidemli Frontend Developer & UI/UX Uzmani ({framework})',
        goal=f'Profesyonel, erisilebilir ve modern {framework} uygulamalari gelistirmek',
        backstory=f"""
        Sen {framework} konusunda uzman bir frontend gelistirici ve UI/UX tasarimcisisin.
        Sadece kod yazmakla kalmaz, profesyonel seviyede tasarim kararlari da alirsin.

        UZMANLIK ALANLARIN:
        - Modern UI/UX tasarimi (50+ tasarim stili bilgisi)
        - Component-based architecture
        - State management (Redux, Zustand, Pinia vb.)
        - API entegrasyonu (REST, GraphQL)
        - Form validation ve error handling
        - Responsive design (mobile-first)
        - Performance optimization
        - Accessibility (a11y) - WCAG 2.1 AA uyumluluk
        - Renk teorisi ve tipografi

        FRAMEWORK TERCIHLER:
        - React: Vite + React, Next.js
        - Vue: Vite + Vue 3, Nuxt.js
        - Angular: Angular 15+

        UI LIBRARIES:
        - React: shadcn/ui, Material-UI, Ant Design
        - Vue: Vuetify, Element Plus
        - CSS: Tailwind CSS, styled-components
        - Icons: Lucide Icons, Heroicons (EMOJI DEGIL)

        ========================
        FRONTEND DESIGN PRO KURALLARI (UI/UX + Glassmorphism):
        ========================
        {frontend_skill}

        ONEMLI: Kodunu her zaman kod blogu icinde ver!
        JavaScript icin ```javascript```, TypeScript icin ```typescript```

        ONEMLI: CSS dosyasini da ayri bir kod blogunda ver!
        CSS icin ```css```
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_developer_agent(programming_language: str = "Python"):
    """
    Generic Developer Agent - Geriye uyumluluk için
    Backend ve Frontend ayrımı yoksa bu kullanılır
    """
    return Agent(
        role=f'Kıdemli {programming_language} Yazilimci',
        goal=f'Yuksek kaliteli {programming_language} kodu yazmak',
        backstory=f"""
        Sen {programming_language} konusunda uzman bir yazilimcisin.
        Temiz, okunabilir ve calisir kod yazarsın.

        ONEMLI: Kodunu her zaman kod blogu icinde ver!
        Python icin ```python```, JavaScript icin ```javascript```
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_qa_agent():
    """QA Test Agent - QA Engineer Skill Destekli"""
    qa_skill = load_skill('qa_engineer')

    return Agent(
        role='Kidemli Test Uzmani (QA Engineer)',
        goal='Kodu test etmek, bug bulmak ve kalite standartlarini saglamak',
        backstory=f"""
        Sen deneyimli bir QA muhendisisin.

        ========================
        QA ENGINEER PRO KURALLARI:
        ========================
        {qa_skill}
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


# ============================================================
# BACKLOG IZLEME VE IS CEKME
# ============================================================

def parse_analyst_output(analyst_output: str) -> Optional[Dict]:
    """
    Analistin ciktisini parse eder ve TaskConfig bilgilerini cikarir
    Yeni format: Backend ve Frontend ayrimini destekler
    """
    import re
    import json

    # JSON benzeri yapiyi bul
    try:
        # Once JSON formatinda dene
        if '{' in analyst_output and '}' in analyst_output:
            json_match = re.search(r'\{[\s\S]*\}', analyst_output)
            if json_match:
                json_str = json_match.group(0)
                # Python dict formatini JSON'a cevir
                # JSON yorumlarını temizle
                json_str = re.sub(r'#[^\n]*', '', json_str)
                json_str = json_str.replace("'", '"')
                data = json.loads(json_str)

                # Eski format uyumluluğu için normalize et
                if "project_type" not in data:
                    # Eski format - basit proje
                    data["project_type"] = "cli"

                return data
    except Exception as e:
        print(f"JSON parse hatası: {e}")
        pass

    # Manuel parsing - ESKİ FORMAT (geriye uyumluluk)
    result = {
        "project_name": "",
        "description": "",
        "project_type": "cli",
        "programming_language": "Python",
        "file_name": "",
        "requirements": []
    }

    # project_name'i bul
    match = re.search(r'"project_name"\s*:\s*"([^"]+)"', analyst_output)
    if match:
        result["project_name"] = match.group(1)

    # description'i bul
    match = re.search(r'"description"\s*:\s*"([^"]+)"', analyst_output)
    if match:
        result["description"] = match.group(1)

    # programming_language'i bul
    match = re.search(r'"programming_language"\s*:\s*"([^"]+)"', analyst_output)
    if match:
        result["programming_language"] = match.group(1)

    # file_name'i bul
    match = re.search(r'"file_name"\s*:\s*"([^"]+)"', analyst_output)
    if match:
        result["file_name"] = match.group(1)

    # requirements'i bul
    req_match = re.search(r'"requirements"\s*:\s*\[([\s\S]*?)\]', analyst_output)
    if req_match:
        req_str = req_match.group(1)
        requirements = re.findall(r'"([^"]+)"', req_str)
        result["requirements"] = requirements

    return result if result["project_name"] else None


def handle_bugs(bug_report: str, list_ids: Dict[str, str], project_name: str, card_id: str):
    """
    Bug raporunu analiz edip Trello'da bug kartları oluşturur (Her bug için ayrı kart)

    Args:
        bug_report: Test uzmanının bug raporu
        list_ids: Liste ID'leri
        project_name: Proje adı
        card_id: Ana kart ID (bug'lar burada referans edilir)
    """
    import re

    # Bug'ları parse et
    # Format: "Bug 1:", "Hata 1:", "BUG-001:", vb.
    bug_pattern = r'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*(\d+)[:\s]*([^\n]+)'
    bugs_found = re.findall(bug_pattern, bug_report, re.IGNORECASE)

    bug_cards_created = []

    if bugs_found:
        print("\n" + "=" * 60)
        print(f"🐛 {len(bugs_found)} BUG TESPİT EDİLDİ - TRELLO'DA KARTLAR OLUŞTURULUYOR")
        print("=" * 60)

        for bug_num, bug_title in bugs_found:
            # Bug detaylarını bul
            bug_detail_pattern = rf'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*{bug_num}[:\s]*{re.escape(bug_title)}([\s\S]*?)(?=(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*\d+|$)'
            detail_match = re.search(bug_detail_pattern, bug_report, re.IGNORECASE)

            bug_details = detail_match.group(1).strip() if detail_match else "Detay bulunamadi"

            # Öncelik belirle
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
                name=f"🐛 [BUG-{bug_num}] {project_name} - {bug_title.strip()}",
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

**Kaynak Kart:** {card_id}
**Tespit Eden:** QA Agent
                """,
                list_id=list_ids.get("Bugs"),
                labels=[priority_label]
            )

            if bug_card:
                bug_cards_created.append(bug_card['shortUrl'])
                print(f"   ✅ BUG-{bug_num}: {bug_title.strip()[:50]}...")
                print(f"      {bug_card['shortUrl']}")

        print("=" * 60)

    # Ana karta bug kartlarının linkini ekle
    if bug_cards_created:
        bug_links = "\n".join([f"- {url}" for url in bug_cards_created])
        trello.add_comment(card_id, f"🐛 OLUŞTURULAN BUG KARTLARI ({len(bug_cards_created)} adet):\n\n{bug_links}")

    return len(bug_cards_created)


def process_backlog_card(card: Dict, board_id: str, list_ids: Dict[str, str]) -> bool:
    """
    Backlog'daki bir karti isle

    Args:
        card: Trello karti
        board_id: Board ID
        list_ids: Liste ID'leri

    Returns:
        Basarili ise True
    """
    print("\n" + "=" * 60)
    print(f"📋 YENİ İŞ BULUNDU: {card['name']}")
    print("=" * 60)
    print(f"Aciklama: {card['desc'][:100]}...")

    # Karti "In Progress" yap
    trello.move_card(card['id'], list_id=list_ids.get("In Progress"))
    trello.add_comment(card['id'], "🤖 Orchestrator ise basladi. Analist analiz yapiyor...")

    # 1. ANALIST - Karti analiz et
    print("\n🔍 ANALIST AGENT - Kart analiz ediliyor...")

    analyst = create_analyst_agent()

    analyst_task = Task(
        description=f"""
        Asagidaki Trello kartini analiz et ve teknik gereksinimlere donustur:

        KART BASLIGI: {card['name']}
        KART ACIKLAMASI: {card['desc']}

        Cikti olarak JSON formatinda su bilgileri ver:
        - project_name: Proje adi (kisa ve aciklayici)
        - description: Proje aciklamasi (1-2 cumle)
        - programming_language: Programlama dili (Python, JavaScript, Java vb.)
        - file_name: Olusturulacak dosya adi
        - requirements: Liste seklinde teknik gereksinimler

        ORNEK CIKTI:
        {{
            "project_name": "Todo List CLI",
            "description": "Komut satirindan calisir todo list uygulamasi",
            "programming_language": "Python",
            "file_name": "todo_app.py",
            "requirements": [
                "Todo ekleme, silme, guncelleme",
                "JSON'a kaydetme",
                "Liste gosterme"
            ]
        }}
        """,
        agent=analyst,
        expected_output="JSON formatinda teknik gereksinimler"
    )

    analyst_crew = Crew(
        agents=[analyst],
        tasks=[analyst_task],
        verbose=False,  # Console'da detay gösterme
        process=Process.sequential
    )

    analyst_result = analyst_crew.kickoff()
    analyst_output = str(analyst_result)

    # Analist ciktisini Trello'ya ekle
    trello.add_comment(card['id'], f"📊 ANALIST RAPORU:\n\n{analyst_output}")

    # Analist ciktisini parse et
    task_config = parse_analyst_output(analyst_output)

    if not task_config or not task_config.get("project_name"):
        print("❌ Analist ciktisi parse edilemedi!")
        trello.add_comment(card['id'], "❌ Analist ciktisi parse edilemedi. Manuel mudahale gerekli.")
        return False

    print(f"\n✅ Analist analizi tamamlandi:")
    print(f"   Proje: {task_config['project_name']}")
    print(f"   Dil: {task_config['programming_language']}")
    print(f"   Dosya: {task_config['file_name']}")

    # 2. ORCHESTRATOR - Is dagilimini yap
    print("\n🎯 ORCHESTRATOR - Is dagilimi yapiliyor...")

    orchestrator = create_orchestrator_agent()
    developer = create_developer_agent(task_config['programming_language'])
    qa = create_qa_agent()

    # Task'lari olustur
    requirements_str = "\n".join([f"- {req}" for req in task_config['requirements']])

    orchestrator_task = Task(
        description=f"""
        {task_config['project_name']} projesi icin detayli plan olustur.

        PROJE BILGILERI:
        - Adi: {task_config['project_name']}
        - Aciklama: {task_config['description']}
        - Dil: {task_config['programming_language']}
        - Dosya: {task_config['file_name']}

        GEREKSINIMLER:
{requirements_str}

        Detayli bir proje plani hazirla.
        """,
        agent=orchestrator,
        expected_output="Detayli proje plani"
    )

    dev_task = Task(
        description=f"""
        {task_config['project_name']} projesini kodla.

        GEREKSINIMLER:
{requirements_str}

        DOSYA ADI: {task_config['file_name']}
        PROGRAMLAMA DILI: {task_config['programming_language']}

        Tam calisir kod yaz. Kodun TAMAMINI kod blogu icinde ver!
        """,
        agent=developer,
        expected_output=f"Tam calisir {task_config['file_name']} kodu",
        context=[orchestrator_task]
    )

    qa_task = Task(
        description=f"""
        {task_config['project_name']} projesi icin test senaryolari olustur ve kodu incele.

        Test senaryolari, kod kalitesi analizi, bug listesi ve iyilestirme onerileri sun.

        Bug bulursan MUTLAKA şu formatta yaz:
        Bug 1: [Bug başlığı]
        Açıklama: ...
        Öncelik: Yüksek/Orta/Düşük

        Bug 2: [Bug başlığı]
        Açıklama: ...
        Öncelik: ...
        """,
        agent=qa,
        expected_output="Test raporu ve NUMARALI bug listesi",
        context=[orchestrator_task, dev_task]
    )

    print("\n🏗️ SOLUTION ARCHITECT - Mimari tasarlanıyor...")
    architect = create_solution_architect_agent()
    
    architect_task = Task(
        description=f"""
        Analistin belirlediği proje için teknik mimariyi tasarla.
        
        PROJE: {task_config['project_name']}
        GEREKSINİMLER: {requirements_str}
        
        ÇIKTI BEKLENTİSİ:
        - Veritabanı yapısı
        - API endpoint listesi
        - Kullanılacak kütüphaneler
        - Güvenlik önlemleri
        """,
        agent=architect,
        expected_output="Detaylı teknik mimari dokümanı"
    )

    # Ekibi calistir
    project_crew = Crew(
        agents=[architect, orchestrator, developer, qa],
        tasks=[architect_task, orchestrator_task, dev_task, qa_task],
        verbose=False,  # Console'da detay gösterme
        process=Process.sequential
    )

    print("\n🚀 AI Ekibi calismaya basliyor...")
    print("⚙️  Agent'lar arka planda calisiyor... (Verbose mod kapali)")

    # Orchestrator plani yapiyor
    print("\n" + "=" * 60)
    print("📋 ADIM 1/3: ORCHESTRATOR - Proje plani hazirlaniyor...")
    print("=" * 60)

    result = project_crew.kickoff()

    # Sonuclari isle
    print("\n📝 Sonuclar isleniyor...")

    # ADIM 2: Kod yazildi - Code Review'e gonder
    print("\n" + "=" * 60)
    print("📋 ADIM 2/3: DEVELOPER - Kod yaziliyor...")
    print("=" * 60)

    kod = str(dev_task.output) if hasattr(dev_task, 'output') else ""
    if kod and len(kod) > 100:
        # Kod bloklarini temizle
        if "```python" in kod:
            kod = kod.split("```python")[1].split("```")[0]
        elif "```javascript" in kod:
            kod = kod.split("```javascript")[1].split("```")[0]
        elif "```" in kod:
            kod = kod.split("```")[1].split("```")[0]

        kod = kod.strip()

        with open(task_config['file_name'], "w", encoding="utf-8") as f:
            f.write(kod)

        # Kod istatistikleri
        line_count = len(kod.split('\n'))
        char_count = len(kod)

        print(f"\n✅ KOD YAZILDI:")
        print(f"   📁 Dosya: {task_config['file_name']}")
        print(f"   📊 Satır: {line_count}")
        print(f"   📏 Boyut: {char_count} karakter")
        print(f"   🔧 Dil: {task_config.get('programming_language', 'Python')}")

        # Karti "Code Review" listesine tasi
        trello.move_card(card['id'], list_id=list_ids.get("Code Review"))
        trello.add_comment(card['id'], f"""✅ KOD YAZILDI: {task_config['file_name']}

📁 Dosya: {task_config['file_name']}
📊 Satır Sayısı: {line_count}
📏 Boyut: {char_count} karakter
🔧 Dil: {task_config.get('programming_language', 'Python')}

Kod dosyaya kaydedildi. Kod review bekliyor...""")

    # ADIM 3: Test - Testing listesine tasi
    print("\n" + "=" * 60)
    print("📋 ADIM 3/3: QA - Test yapiliyor...")
    print("=" * 60)

    # Karti "Testing" listesine tasi
    trello.move_card(card['id'], list_id=list_ids.get("Testing"))
    trello.add_comment(card['id'], "🧪 QA Agent test yapiyor...")

    test_raporu = str(qa_task.output) if hasattr(qa_task, 'output') else ""
    if test_raporu:
        trello.add_comment(card['id'], f"📋 TEST RAPORU:\n\n{test_raporu}")

        # Bug'lari isle ve Trello'da bug kartlari olustur
        print("\n🔍 Bug'lar aranıyor...")
        bug_count = handle_bugs(test_raporu, list_ids, task_config['project_name'], card['id'])

        if bug_count > 0:
            print(f"\n🐛 Toplam {bug_count} bug kartı oluşturuldu!")
            print(f"   Bug'lar 'Bugs' listesinde!")
            trello.add_comment(card['id'], f"⚠️ {bug_count} bug bulundu ve Bugs listesine eklendi!")
        else:
            print("\n✅ Bug bulunamadi!")
            trello.add_comment(card['id'], "✅ Test tamamlandi. Bug bulunamadi!")

    # Karti "Done" listesine tasi
    trello.move_card(card['id'], list_id=list_ids.get("Done"))
    trello.add_comment(card['id'], "✅ IS TAMAMLANDI! Tum adimlar basariyla tamamlandi.\n\nBacklog → In Progress → Code Review → Testing → Done")

    print("\n" + "=" * 60)
    print(f"✅ İŞ TAMAMLANDI: {task_config['project_name']}")
    print("=" * 60)

    return True


# ============================================================
# ANA ORCHESTRATOR DONGUSU
# ============================================================

def run_orchestrator(board_id: str, check_interval: int = 30):
    """
    Orchestrator ana dongusu - Backlog'u surekli izler

    Args:
        board_id: Trello Board ID
        check_interval: Kontrol araligi (saniye)
    """
    print("\n" + "=" * 60)
    print("🎯 TRELLO ORCHESTRATOR BAŞLATILDI")
    print("=" * 60)
    print(f"Board ID: {board_id}")
    print(f"Kontrol Araligi: {check_interval} saniye")
    print("=" * 60)

    # Liste ID'lerini al
    lists = trello.get_lists(board_id)
    if not lists:
        print("❌ Listeler alinamadi!")
        return

    list_ids = {}
    for lst in lists:
        list_ids[lst['name']] = lst['id']

    print("\n📋 Bulunan Listeler:")
    for name, id in list_ids.items():
        print(f"   - {name}: {id}")

    if "Backlog" not in list_ids:
        print("\n❌ 'Backlog' listesi bulunamadi! Once backlog listesi olusturun.")
        return

    print("\n🔍 Backlog izleniyor...")
    print("(Ctrl+C ile durdurun)\n")

    islenen_kartlar = set()  # Islenen kartlarin ID'leri

    try:
        while True:
            # Backlog'daki kartlari al
            url = f"{trello.base_url}/lists/{list_ids['Backlog']}/cards"
            params = trello._get_auth_params()

            try:
                import requests
                response = requests.get(url, params=params)
                response.raise_for_status()
                backlog_cards = response.json()

                # Yeni kartlari isle
                for card in backlog_cards:
                    if card['id'] not in islenen_kartlar:
                        print(f"\n🆕 Yeni kart bulundu: {card['name']}")

                        # Karti isle
                        success = process_backlog_card(card, board_id, list_ids)

                        if success:
                            islenen_kartlar.add(card['id'])

                        # Her kart arasi biraz bekle
                        time.sleep(5)

                # Bir sonraki kontrol icin bekle
                print(f"\n⏳ {check_interval} saniye bekleniyor...")
                time.sleep(check_interval)

            except Exception as e:
                print(f"❌ Hata: {e}")
                time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n\n🛑 Orchestrator durduruldu.")


# ============================================================
# BASLANGIC FONKSIYONU
# ============================================================

def main():
    """
    Kullanicidan board secimi al ve orchestrator'u baslat
    """
    print("\n" + "=" * 60)
    print("🎯 TRELLO ORCHESTRATOR")
    print("=" * 60)

    # Board'lari listele
    print("\n📋 Mevcut Board'lariniz:")
    boards = trello.get_boards()

    if not boards:
        print("❌ Board bulunamadi!")
        return

    for i, board in enumerate(boards, 1):
        print(f"{i}. {board['name']} ({board['id']})")

    print(f"\n0. Yeni board olustur")

    # Kullanicidan secim al
    try:
        secim = int(input("\nHangi board'u izlemek istersiniz? (numara girin): "))

        if secim == 0:
            # Yeni board olustur
            board_name = input("Yeni board adi: ")
            board_structure = trello.setup_board_structure(board_name)
            if board_structure:
                board_id = board_structure['board']['id']
                print(f"\n✅ Yeni board olusturuldu: {board_structure['board']['url']}")
            else:
                print("❌ Board olusturulamadi!")
                return
        elif 1 <= secim <= len(boards):
            board_id = boards[secim - 1]['id']
        else:
            print("❌ Gecersiz secim!")
            return

        # Orchestrator'u baslat
        run_orchestrator(board_id)

    except ValueError:
        print("❌ Gecersiz giris!")
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandirildi.")


if __name__ == "__main__":
    main()
