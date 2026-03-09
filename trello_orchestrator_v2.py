"""
Trello Orchestrator V2 - Backend & Frontend Developer Destekli

Test yönetim otomasyon aracı için özelleştirilmiş orchestrator.
Backend ve Frontend developer agent'larını ayrı ayrı kullanır.

YENILIKLER:
- Backend Developer Agent (API, Database, Business Logic)
- Frontend Developer Agent (UI/UX, Client-side)
- Fullstack proje desteği
- Akıllı agent seçimi (proje tipine göre)
"""
import os
import signal
import sys

# Windows signal duzeltmesi
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

import warnings
import time
from typing import Dict, List, Optional

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
# DASHBOARD UDATE HELPER
# ============================================================

def update_dashboard(agent="Idle", task="Waiting...", project="None", step="0/0", log=None):
    """Monitor Dashboard'a durum guncellemesi gonderir"""
    import requests
    try:
        data = {
            "agent": agent,
            "task": task,
            "project": project,
            "step": step
        }
        if log:
            data["log"] = log
            
        requests.post("http://localhost:5000/api/update_status", json=data, timeout=1)
    except:
        pass # Dashboard calismiyorsa hata verme

# Bu dosyayı trello_orchestrator.py'den import edelim
from trello_orchestrator import (
    create_analyst_agent,
    create_orchestrator_agent,
    create_backend_developer_agent,
    create_frontend_developer_agent,
    create_qa_agent,
    parse_analyst_output,
    handle_bugs
)

# WhatsApp Approval Agent
from whatsapp_approval_agent import request_approval_via_whatsapp

# ============================================================
# GELISMIS IS AKISI - BACKEND & FRONTEND
# ============================================================

def process_fullstack_project(card: Dict, task_config: Dict, board_id: str, list_ids: Dict[str, str]) -> bool:
    """
    Fullstack proje işleme (Backend + Frontend)
    """
    print("\n" + "=" * 80)
    print("🚀 FULLSTACK PROJE - Backend ve Frontend ayrı geliştiriliyor")
    print("=" * 80)

    project_name = task_config['project_name']
    backend_config = task_config.get('backend', {})
    frontend_config = task_config.get('frontend', {})

    # Agent'ları oluştur
    orchestrator = create_orchestrator_agent()
    architect = create_solution_architect_agent()
    backend_dev = create_backend_developer_agent(
        backend_config.get('programming_language', 'Python')
    )
    frontend_dev = create_frontend_developer_agent(
        frontend_config.get('framework', 'React')
    )
    qa = create_qa_agent()

    # ADIM 1: Solution Architect - Mimari Tasarım
    print("\n🏗️ ADIM 1/5: SOLUTION ARCHITECT - Mimari tasarlanıyor...")
    update_dashboard(agent="Solution Architect", task="Mimari Tasarımı Yapılıyor", project=project_name, step="1/5", log="Solution Architect işe başladı.")

    architect_task = Task(
        description=f"""
        {project_name} projesi için teknik mimariyi tasarla.

        GEREKSINIMLER:
        Backend: {', '.join(backend_config.get('requirements', []))}
        Frontend: {', '.join(frontend_config.get('requirements', []))}

        ÇIKTI BEKLENTİSİ:
        - Veritabanı şeması (Tablolar, ilişkiler)
        - API Endpoint listesi (Method, Path, Description)
        - Kullanılacak kütüphaneler ve versiyonları
        - Güvenlik önlemleri (Auth, Validation)
        - Klasör yapısı önerisi
        """,
        agent=architect,
        expected_output="Detaylı teknik mimari dokümanı"
    )

    # ADIM 2: Orchestrator - Proje planı
    print("\n📋 ADIM 2/5: ORCHESTRATOR - Proje planlama...")
    update_dashboard(agent="Orchestrator", task="Proje Planı Oluşturuluyor", project=project_name, step="2/5", log="Mimari tasarım tamamlandı. Proje planı yapılıyor.")

    orchestrator_task = Task(
        description=f"""
        {project_name} fullstack projesi için detaylı plan oluştur.

        MİMARİ TASARIM:
        [Solution Architect'in çıktısını referans al]

        BACKEND:
        - Dil/Framework: {backend_config.get('programming_language', 'Python')} / {backend_config.get('framework', 'FastAPI')}
        - Gereksinimler: {', '.join(backend_config.get('requirements', []))}

        FRONTEND:
        - Framework: {frontend_config.get('framework', 'React')}
        - Gereksinimler: {', '.join(frontend_config.get('requirements', []))}

        Proje planını backend ve frontend ayrımı yaparak hazırla.
        API endpoint'lerini, veri modellerini ve UI componentlerini belirt.
        """,
        agent=orchestrator,
        expected_output="Detaylı fullstack proje planı (Backend + Frontend)",
        context=[architect_task]
    )

    # ADIM 3: Backend Development
    print("\n💾 ADIM 3/5: BACKEND DEVELOPER - API ve Business Logic...")
    update_dashboard(agent="Backend Developer", task="API Geliştiriliyor", project=project_name, step="3/5", log="Developer API geliştirmeye başladı.")

    backend_requirements_str = "\n".join([f"- {req}" for req in backend_config.get('requirements', [])])

    backend_task = Task(
        description=f"""
        {project_name} projesi icin BACKEND kodunu yaz.

        FRAMEWORK: {backend_config.get('framework', 'FastAPI')}
        DIL: {backend_config.get('programming_language', 'Python')}
        DOSYA: {backend_config.get('file_name', 'backend_api.py')}

        GEREKSINIMLER:
{backend_requirements_str}

        YAPILACAKLAR:
        - RESTful API endpoint'leri
        - Veritabani sema tasarimi
        - Business logic
        - Input validation
        - Error handling
        - API documentation (Swagger/OpenAPI)

        Tam calisir backend kodu yaz. Kodun TAMAMINI kod blogu icinde ver!
        """,
        agent=backend_dev,
        expected_output=f"Tam calisir {backend_config.get('file_name', 'backend_api.py')} kodu",
        context=[orchestrator_task]
    )

    # ADIM 4: Frontend Development
    print("\n🎨 ADIM 4/5: FRONTEND DEVELOPER - UI ve Client Logic...")
    update_dashboard(agent="Frontend Developer", task="UI Geliştiriliyor", project=project_name, step="4/5", log="Frontend geliştirmesi başladı.")

    frontend_requirements_str = "\n".join([f"- {req}" for req in frontend_config.get('requirements', [])])

    frontend_task = Task(
        description=f"""
        {project_name} projesi icin FRONTEND kodunu yaz.

        FRAMEWORK: {frontend_config.get('framework', 'React')}
        DOSYA: {frontend_config.get('file_name', 'App.jsx')}

        GEREKSINIMLER:
{frontend_requirements_str}

        BACKEND API ENDPOINT'LERI:
        [Backend developer'in olusturdugu API'lari kullan]

        YAPILACAKLAR:
        - Modern UI/UX tasarimi (UI/UX Pro Max kurallarini uygula)
        - Component-based architecture
        - API entegrasyonu
        - Form validation
        - Error handling
        - Responsive design (mobile-first, 375px/768px/1024px/1440px)
        - Accessibility (aria-label, alt text, focus ring, min 44x44px touch)
        - Profesyonel renk paleti sec (proje tipine uygun)
        - Google Fonts'tan uygun font eslesmesi sec
        - Emoji yerine SVG icon kullan (Lucide veya Heroicons)
        - Loading/error state'leri ekle
        - CSS dosyasini ayri bir ```css``` kod blogunda ver

        ONEMLI: Tam calisir frontend kodu yaz.
        JSX kodunu ```javascript``` blogunda, CSS kodunu ```css``` blogunda ver!
        """,
        agent=frontend_dev,
        expected_output=f"Tam calisir {frontend_config.get('file_name', 'App.jsx')} kodu",
        context=[orchestrator_task, backend_task]
    )

    # ADIM 5: QA Testing
    print("\n🧪 ADIM 5/5: QA ENGINEER - Test ve analiz...")
    update_dashboard(agent="QA Engineer", task="Test Ediliyor", project=project_name, step="5/5", log="QA test sürecini başlattı.")

    qa_task = Task(
        description=f"""
        {project_name} fullstack projesi icin kapsamli test raporu olustur.

        BACKEND TEST:
        - API endpoint testleri
        - Veritabani testleri
        - Business logic testleri

        FRONTEND TEST:
        - Component testleri
        - Integration testleri
        - UI/UX testleri

        ENTEGRASYON TEST:
        - Backend-Frontend entegrasyonu
        - API request/response testleri

        Bug bulursan MUTLAKA şu formatta yaz:
        Bug 1: [Bug başlığı]
        Açıklama: ...
        Katman: Backend/Frontend/Integration
        Öncelik: Yüksek/Orta/Düşük
        """,
        agent=qa,
        expected_output="Kapsamli test raporu ve bug listesi",
        context=[orchestrator_task, backend_task, frontend_task]
    )

    # Crew'u oluştur ve çalıştır
    fullstack_crew = Crew(
        agents=[architect, orchestrator, backend_dev, frontend_dev, qa],
        tasks=[architect_task, orchestrator_task, backend_task, frontend_task, qa_task],
        verbose=False,  # Console'da detay gösterme
        process=Process.sequential
    )

    print("\n🚀 Fullstack ekibi calismaya basliyor...")
    print("⚙️  Agent'lar arka planda calisiyor... (Verbose mod kapali)")
    update_dashboard(agent="CrewAI", task="Workflow Başlatıldı", log="Tüm ajanlar göreve başladı.")
    result = fullstack_crew.kickoff()

    # Sonuçları işle
    print("\n📝 Sonuçlar işleniyor...")
    update_dashboard(agent="System", task="Sonuçlar İşleniyor", project=project_name, step="Done", log="Workflow tamamlandı. Çıktılar işleniyor.")

    # Backend kodu kaydet
    backend_kod = str(backend_task.output) if hasattr(backend_task, 'output') else ""
    if backend_kod and len(backend_kod) > 100:
        backend_kod = extract_code(backend_kod, backend_config.get('programming_language', 'python'))

        backend_filename = backend_config.get('file_name', 'backend_api.py')
        with open(backend_filename, "w", encoding="utf-8") as f:
            f.write(backend_kod)

        # Kod istatistikleri
        line_count = len(backend_kod.split('\n'))
        char_count = len(backend_kod)

        print(f"\n✅ BACKEND KODU YAZILDI:")
        print(f"   📁 Dosya: {backend_filename}")
        print(f"   📊 Satır: {line_count}")
        print(f"   📏 Boyut: {char_count} karakter")
        print(f"   🔧 Dil: {backend_config.get('programming_language', 'Python')}")

        trello.add_comment(card['id'], f"""✅ BACKEND KODU YAZILDI

📁 Dosya: {backend_filename}
📊 Satır Sayısı: {line_count}
📏 Boyut: {char_count} karakter
🔧 Dil/Framework: {backend_config.get('programming_language', 'Python')} / {backend_config.get('framework', 'FastAPI')}

Backend API hazır!""")

    # Frontend kodu kaydet
    frontend_kod = str(frontend_task.output) if hasattr(frontend_task, 'output') else ""
    if frontend_kod and len(frontend_kod) > 100:
        frontend_kod = extract_code(frontend_kod, 'javascript')

        frontend_filename = frontend_config.get('file_name', 'App.jsx')
        with open(frontend_filename, "w", encoding="utf-8") as f:
            f.write(frontend_kod)

        # Kod istatistikleri
        line_count = len(frontend_kod.split('\n'))
        char_count = len(frontend_kod)

        print(f"\n✅ FRONTEND KODU YAZILDI:")
        print(f"   📁 Dosya: {frontend_filename}")
        print(f"   📊 Satır: {line_count}")
        print(f"   📏 Boyut: {char_count} karakter")
        print(f"   🎨 Framework: {frontend_config.get('framework', 'React')}")

        trello.add_comment(card['id'], f"""✅ FRONTEND KODU YAZILDI

📁 Dosya: {frontend_filename}
📊 Satır Sayısı: {line_count}
📏 Boyut: {char_count} karakter
🎨 Framework: {frontend_config.get('framework', 'React')}

UI hazır!""")

    # Kartı "Code Review" listesine taşı
    trello.move_card(card['id'], list_id=list_ids.get("Code Review"))

    # QA testleri
    trello.move_card(card['id'], list_id=list_ids.get("Testing"))
    trello.add_comment(card['id'], "🧪 QA Agent test yapiyor...")

    test_raporu = str(qa_task.output) if hasattr(qa_task, 'output') else ""
    if test_raporu:
        trello.add_comment(card['id'], f"📋 TEST RAPORU (FULLSTACK):\n\n{test_raporu}")

        # Bug'ları işle
        bug_count = handle_bugs(test_raporu, list_ids, project_name, card['id'])

        if bug_count > 0:
            print(f"\n🐛 Toplam {bug_count} bug kartı oluşturuldu!")
            trello.add_comment(card['id'], f"⚠️ {bug_count} bug bulundu ve Bugs listesine eklendi!")
        else:
            print("\n✅ Bug bulunamadı!")
            trello.add_comment(card['id'], "✅ Test tamamlandı. Bug bulunamadı!")

    # Kartı "Done" taşı
    trello.move_card(card['id'], list_id=list_ids.get("Done"))
    trello.add_comment(card['id'], f"""
✅ FULLSTACK PROJE TAMAMLANDI!

📦 OLUŞTURULAN DOSYALAR:
- Backend: {backend_config.get('file_name', 'backend_api.py')}
- Frontend: {frontend_config.get('file_name', 'App.jsx')}

🎯 WORKFLOW: Backlog → In Progress → Code Review → Testing → Done
    """)

    print("\n" + "=" * 80)
    print(f"✅ FULLSTACK PROJE TAMAMLANDI: {project_name}")
    print("=" * 80)

    return True


def extract_code(output: str, language: str) -> str:
    """
    AI output'undan kod bloğunu çıkarır
    """
    import re

    # Kod bloğu formatlarını dene
    patterns = [
        rf'```{language.lower()}\n([\s\S]*?)```',
        rf'```{language.upper()}\n([\s\S]*?)```',
        r'```\n([\s\S]*?)```'
    ]

    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1).strip()

    # Kod bloğu bulunamadıysa, output'u direkt dön
    return output.strip()


def process_backend_only_project(card: Dict, task_config: Dict, board_id: str, list_ids: Dict[str, str]) -> bool:
    """
    Sadece Backend projesi
    """
    print("\n💾 BACKEND-ONLY PROJE")

    backend_config = task_config.get('backend', task_config)  # Geriye uyumluluk

    # trello_orchestrator.py'deki standart akışı kullan
    from trello_orchestrator import process_backlog_card
    return process_backlog_card(card, board_id, list_ids)


def process_frontend_only_project(card: Dict, task_config: Dict, board_id: str, list_ids: Dict[str, str]) -> bool:
    """
    Sadece Frontend projesi
    """
    print("\n🎨 FRONTEND-ONLY PROJE")

    # Frontend-only akışı (basitleştirilmiş)
    from trello_orchestrator import process_backlog_card
    return process_backlog_card(card, board_id, list_ids)


# ============================================================
# AKILLI PROJE YONLENDIRME
# ============================================================

def process_backlog_card_v2(card: Dict, board_id: str, list_ids: Dict[str, str]) -> bool:
    """
    V2: Akıllı proje yönlendirme - Proje tipine göre doğru agent'ları kullanır

    WHATSAPP ONAY MEKANIZMASI:
    1. Task Backlog'dan gelir
    2. Approval Agent analiz yapar
    3. WhatsApp'tan onay istenir
    4. Kullanıcı onaylarsa -> Orchestrator devam eder
    5. Reddederse -> Task iptal edilir
    """
    print("\n" + "=" * 80)
    print(f"📋 YENİ İŞ BULUNDU (V2): {card['name']}")
    print("=" * 80)

    # ============================================================
    # WHATSAPP ONAY AŞAMASI
    # ============================================================

    print("\n📱 WhatsApp onay süreci başlatılıyor...")
    trello.add_comment(card['id'], "📱 WhatsApp üzerinden onay bekleniyor...")
    update_dashboard(agent="WhatsApp Approval", task="Onay Bekleniyor", project=card['name'], step="0/5", log=f"Yeni iş: {card['name']} - WhatsApp onayı bekleniyor.")

    # Onay iste (timeout: 5 dakika)
    approved, task_summary = request_approval_via_whatsapp(card, timeout=300)

    if not approved:
        print("\n❌ Task onaylanmadı! İşlem iptal ediliyor...")
        trello.add_comment(card['id'], "❌ Task kullanıcı tarafından onaylanmadı. İşlem iptal edildi.")
        update_dashboard(agent="System", task="Task Reddedildi", project=card['name'], log=f"❌ Task reddedildi: {card['name']}")

        # Kartı Backlog'a geri taşı (veya "Rejected" listesine)
        rejected_list_id = list_ids.get("Backlog")  # Rejected list yoksa Backlog'a
        trello.move_card(card['id'], list_id=rejected_list_id)
        return False

    print("\n✅ Task onaylandı! İşleme başlanıyor...")
    update_dashboard(agent="System", task="Task Onaylandı", project=card['name'], log="✅ Task onaylandı! İşlem başlıyor.")

    # ============================================================
    # İŞLEM DEVAM EDİYOR
    # ============================================================

    # Kartı "In Progress" yap
    trello.move_card(card['id'], list_id=list_ids.get("In Progress"))
    trello.add_comment(card['id'], """✅ Task onaylandı!

🤖 Orchestrator V2 işe başladı. Analist analiz yapıyor...

📊 ONAYLANAN TASK ÖZETİ:
""" + f"""
• Proje: {task_summary.get('task_name', 'N/A')}
• Tip: {task_summary.get('project_type', 'N/A')}
• Dil: {task_summary.get('programming_language', 'N/A')}
• Framework: {task_summary.get('framework', 'N/A')}
• Tahmini Süre: {task_summary.get('estimated_time', 'N/A')}
""")

    # Analist analizi
    update_dashboard(agent="Analist", task="Kart Analiz Ediliyor", project=card['name'], step="1/5", log="Analist kartı analiz ediyor...")
    analyst = create_analyst_agent()

    analyst_task = Task(
        description=f"""
        Asagidaki Trello kartini analiz et:

        KART BASLIGI: {card['name']}
        KART ACIKLAMASI: {card['desc']}

        Gorevlerin:
        - Kullanicinin isteğini anla
        - Proje adini belirle
        - Proje tipini belirle (backend, frontend, fullstack, cli, mobile vb.)
        - Programlama dilini/framework'u sec
        - Detayli gereksinimleri cikar
        - Dosya adlarini belirle (backend ve frontend ayri ise ikisini de belirt)

        ÖNEMLİ: Çıktın JSON formatında olmalı ve şu yapıyı takip etmeli:
        {{
            "project_name": "Proje Adi",
            "description": "Kisa aciklama",
            "project_type": "fullstack",
            "programming_language": "Python",
            "file_name": "main.py",
            "requirements": ["Req 1", "Req 2"]
        }}
        """,
        agent=analyst,
        expected_output="JSON formatinda proje analizi (project_type ile)"
    )

    analyst_crew = Crew(
        agents=[analyst],
        tasks=[analyst_task],
        verbose=False,
        process=Process.sequential
    )

    analyst_result = analyst_crew.kickoff()
    analyst_output = str(analyst_result)
    update_dashboard(agent="Analist", task="Analiz Tamamlandı", project=card['name'], log=f"Analist analizi tamamladı.")

    trello.add_comment(card['id'], f"📊 ANALIST RAPORU (V2):\n\n{analyst_output}")

    # Parse et
    task_config = parse_analyst_output(analyst_output)

    if not task_config or not task_config.get("project_name"):
        print("❌ Analist ciktisi parse edilemedi!")
        trello.add_comment(card['id'], "❌ Analist ciktisi parse edilemedi. Manuel mudahale gerekli.")
        update_dashboard(agent="System", task="Hata: Parse Edilemedi", log="❌ Analist çıktısı parse edilemedi!")
        return False

    project_type = task_config.get('project_type', 'cli')

    print(f"\n✅ Proje Tipi: {project_type.upper()}")
    print(f"   Proje: {task_config['project_name']}")
    update_dashboard(agent="Orchestrator", task=f"Proje Yönlendiriliyor ({project_type})", project=task_config['project_name'], log=f"Proje tipi: {project_type}. Uygun akışa yönlendiriliyor.")

    # Proje tipine göre yönlendir
    if project_type == 'fullstack':
        return process_fullstack_project(card, task_config, board_id, list_ids)
    elif project_type in ('backend', 'frontend', 'cli'):
        # Tüm proje tipleri için standart akışı kullan (dashboard entegrasyonlu)
        update_dashboard(agent="Developer", task="Kod Yazılıyor", project=task_config['project_name'], step="3/5", log=f"Developer ({task_config.get('programming_language', 'Python')}) kodlamaya başladı.")
        from trello_orchestrator import process_backlog_card
        result = process_backlog_card(card, board_id, list_ids)
        update_dashboard(agent="System", task="Tamamlandı" if result else "Hata", project=task_config['project_name'], step="Done", log="İş tamamlandı!" if result else "İşlem sırasında hata oluştu.")
        return result
    else:
        update_dashboard(agent="Developer", task="Kod Yazılıyor", project=task_config['project_name'], step="3/5", log=f"Standart akış başladı.")
        from trello_orchestrator import process_backlog_card
        result = process_backlog_card(card, board_id, list_ids)
        update_dashboard(agent="System", task="Tamamlandı" if result else "Hata", project=task_config['project_name'], step="Done", log="İş tamamlandı!" if result else "İşlem sırasında hata oluştu.")
        return result


# ============================================================
# SOLUTION ARCHITECT AGENT
# ============================================================

def create_solution_architect_agent():
    return Agent(
        role="Solution Architect",
        goal="Analyze project requirements, design the overall system architecture, and create a detailed project plan including tasks, technologies, and estimated timelines.",
        backstory="You are a highly experienced Solution Architect with a deep understanding of various technologies and system design principles. You excel at breaking down complex problems into manageable components and defining clear, actionable plans for development teams.",
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


# ============================================================
# ANA ORCHESTRATOR DONGUSU
# ============================================================

def run_orchestrator_v2(board_id: str, check_interval: int = 30):
    """
    Orchestrator V2 ana dongusu - Backend/Frontend destekli
    """
    print("\n" + "=" * 80)
    print("🎯 TRELLO ORCHESTRATOR V2 BAŞLATILDI")
    print("🆕 BACKEND & FRONTEND DEVELOPER DESTEKLI")
    print("=" * 80)
    print(f"Board ID: {board_id}")
    print(f"Kontrol Araligi: {check_interval} saniye")
    print("=" * 80)

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

    print("\n🔍 Backlog izleniyor... (V2 - Backend/Frontend destekli)")
    print("(Ctrl+C ile durdurun)\n")

    islenen_kartlar = set()

    try:
        while True:
            url = f"{trello.base_url}/lists/{list_ids['Backlog']}/cards"
            params = trello._get_auth_params()

            try:
                import requests
                response = requests.get(url, params=params)
                response.raise_for_status()
                backlog_cards = response.json()

                for card in backlog_cards:
                    if card['id'] not in islenen_kartlar:
                        print(f"\n🆕 Yeni kart bulundu: {card['name']}")

                        # V2 işleme
                        success = process_backlog_card_v2(card, board_id, list_ids)

                        if success:
                            islenen_kartlar.add(card['id'])

                        time.sleep(5)

                print(f"\n⏳ {check_interval} saniye bekleniyor...")
                time.sleep(check_interval)

            except Exception as e:
                print(f"❌ Hata: {e}")
                time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\n\n🛑 Orchestrator V2 durduruldu.")


# ============================================================
# MAIN
# ============================================================

def main():
    """
    Orchestrator V2 başlat
    """
    from trello_orchestrator import main as original_main

    # Board seçimi için orijinal fonksiyonu kullan
    # Ama run_orchestrator yerine run_orchestrator_v2 kullan

    print("\n" + "=" * 80)
    print("🎯 TRELLO ORCHESTRATOR V2")
    print("🆕 Backend & Frontend Developer Destekli")
    print("=" * 80)

    boards = trello.get_boards()

    if not boards:
        print("❌ Board bulunamadi!")
        return

    print("\n📋 Mevcut Board'lariniz:")
    for i, board in enumerate(boards, 1):
        print(f"{i}. {board['name']} ({board['id']})")

    print(f"\n0. Yeni board olustur")

    try:
        secim = int(input("\nHangi board'u izlemek istersiniz? (numara girin): "))

        if secim == 0:
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

        # V2 orchestrator'u başlat
        run_orchestrator_v2(board_id)

    except ValueError:
        print("❌ Gecersiz giris!")
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandirildi.")


if __name__ == "__main__":
    main()
