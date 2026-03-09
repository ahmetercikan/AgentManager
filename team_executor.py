"""
Team Executor - Takım bazında CrewAI görev çalıştırıcı.
Dinamik olarak agent'lar oluşturur ve görevleri sırayla çalıştırır.
"""

import threading
import requests
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from domains import get_domain, get_agent
from cost_tracker import cost_tracker
from knowledge_base import load_knowledge_for_agent

load_dotenv()

DASHBOARD_URL = "http://localhost:5000"


def update_dashboard(agent="", task="", project="", step="", log=""):
    """Dashboard'a durum güncellemesi gönder"""
    try:
        requests.post(f"{DASHBOARD_URL}/api/update_status", json={
            "agent": agent, "task": task, "project": project,
            "step": step, "log": log
        }, timeout=2)
    except:
        pass


def create_crewai_agent(agent_config: dict, llm, company_knowledge: str = "") -> Agent:
    """Domain agent config'den CrewAI Agent oluştur (şirket bilgisi ile zenginleştirilmiş)"""
    backstory = agent_config["backstory"]

    # Şirket bilgisi varsa backstory'ye ekle
    if company_knowledge:
        backstory += f"""\n\n--- ŞİRKET BİLGİSİ ---\nAşağıdaki bilgiler şirketimize aittir. Bu bilgileri göz önünde bulundurarak çalış:\n\n{company_knowledge}\n--- ŞİRKET BİLGİSİ SONU ---"""

    return Agent(
        role=agent_config["role"],
        goal=agent_config["goal"],
        backstory=backstory,
        llm=llm,
        verbose=False,
        allow_delegation=False
    )


def build_task_description(agent_config: dict, user_task: str, previous_output: str = "") -> str:
    """Agent'a özel görev açıklaması oluştur"""
    category = agent_config.get("category", "general")

    base = f"""
Sen bir {agent_config['role']} olarak çalışıyorsun.

KULLANICI İSTEĞİ:
{user_task}
"""

    if previous_output:
        base += f"""
ÖNCEKİ AGENT ÇIKTISI (bunu temel alarak devam et):
{previous_output}
"""

    category_instructions = {
        "analysis": """
GÖREV: Bu isteği analiz et ve şunları belirle:
- Proje kapsamı ve gereksinimler
- Teknik gereksinimler listesi
- User story'ler ve kabul kriterleri
- Riskler ve öneriler
Çıktını yapılandırılmış bir rapor olarak sun.
""",
        "architecture": """
GÖREV: Mimari tasarım oluştur:
- Sistem mimarisi (bileşenler, katmanlar)
- Teknoloji seçimleri ve gerekçeleri
- Veritabanı şeması tasarımı
- API tasarımı (endpoint'ler)
- Deployment stratejisi
Çıktını detaylı teknik doküman olarak sun.
""",
        "development": """
GÖREV: Kod geliştir:
- İstenen fonksiyoneliteyi tam olarak kodla
- Clean code prensiplerine uy
- Yorum satırları ekle
- Hata yönetimi ekle
Çıktın çalışır ve tam kod olmalı.
""",
        "testing": """
GÖREV: Test senaryoları ve testler oluştur:
- Unit testler
- Integration testler
- Edge case testleri
- Test raporunu oluştur
Çıktın test kodu ve test raporu olmalı.
""",
        "security": """
GÖREV: Güvenlik denetimi yap:
- OWASP Top 10 kontrolleri
- Hardcoded secret kontrolü
- SQL Injection / XSS kontrolleri
- Güvenlik önerileri raporu
Çıktın güvenlik raporu olmalı.
""",
        "content": """
GÖREV: İçerik oluştur:
- Hedef kitleye uygun ton ve dil kullan
- SEO kurallarına uy
- Etkileyici ve özgün içerik yaz
Çıktın hazır yayınlanabilir içerik olmalı.
""",
        "optimization": """
GÖREV: SEO ve optimizasyon analizi yap:
- Anahtar kelime araştırması
- Teknik SEO önerileri
- İçerik optimizasyon planı
Çıktın detaylı optimizasyon raporu olmalı.
""",
        "infrastructure": """
GÖREV: Altyapı tasarımı/kodu oluştur:
- Cloud altyapı tasarımı
- Infrastructure as Code (Terraform/CloudFormation)
- Networking ve güvenlik konfigürasyonu
Çıktın çalışır IaC kodu olmalı.
""",
        "automation": """
GÖREV: CI/CD pipeline oluştur:
- Build, test, deploy adımları
- Otomatik test entegrasyonu
- Deployment stratejisi
Çıktın çalışır pipeline konfigürasyonu olmalı.
""",
        "monitoring": """
GÖREV: Monitoring çözümü tasarla:
- Metrik toplama stratejisi
- Alerting kuralları
- Dashboard tasarımı
Çıktın monitoring konfigürasyonu olmalı.
""",
        "ml": """
GÖREV: ML modeli geliştir:
- Veri analizi ve ön işleme
- Model seçimi ve eğitimi
- Değerlendirme metrikleri
Çıktın çalışır ML kodu olmalı.
""",
        "screening": """
GÖREV: Tarama ve değerlendirme yap:
- Kriterlere göre değerlendir
- Puanlama yap
- Sonuç raporu oluştur
""",
        "interview": """
GÖREV: Mülakat hazırlığı yap:
- Pozisyona özel sorular hazırla
- Değerlendirme kriterleri belirle
- Mülakat akışı planla
""",
        "social": """
GÖREV: Sosyal medya stratejisi oluştur:
- Platform bazında içerik planı
- Paylaşım takvimi
- Etkileşim stratejisi
""",
        "analytics": """
GÖREV: Analitik rapor oluştur:
- Veri analizi yap
- KPI'ları belirle
- Actionable insight'lar sun
""",
        "solution": """
GÖREV: Çözüm önerisi oluştur:
- Sorunu analiz et
- Alternatif çözümler sun
- En iyi çözümü öner ve gerekçelendir
""",
        "quality": """
GÖREV: Kalite kontrolü yap:
- Çıktıları değerlendir
- Eksik ve hataları belirle
- İyileştirme önerileri sun
""",
        "engineering": """
GÖREV: Veri mühendisliği çalışması yap:
- Veri pipeline tasarla
- ETL/ELT süreçleri oluştur
- Veri modeli tasarla
""",
        "visualization": """
GÖREV: Veri görselleştirmesi oluştur:
- Dashboard tasarla
- Grafik ve chart önerileri sun
- Görselleştirme kodu yaz
"""
    }

    base += category_instructions.get(category, """
GÖREV: Rolüne uygun şekilde bu isteği ele al ve detaylı bir çıktı oluştur.
""")

    base += """

============= ÖNEMLİ FORMATLAMA KURALLARI =============
Eğer çıktı olarak kod yazıyorsan veya bir proje oluşturuyorsan:
1. Tüm kodları tek bir bloğa yığma. Her dosyayı ayrı ayrı ``` (markdown) blokları içinde ver.
2. Her kod bloğunun İLK SATIRINA, dosyanın projede tam olarak nereye kaydedilmesi gerektiğini belirten bir YORUM SATIRI yaz.
   (Örneğin JS/TS için: `// src/controllers/userController.js` veya Python için: `# backend/api/main.py`)
3. Sadece kodu ver, uzun açıklamalar yapma. Doğru dizin yapısına uymak zorundasın.
=======================================================
"""

    return base


def execute_team_task(team: dict, task_description: str, task_id: str):
    """
    Takımdaki agent'ları sırayla çalıştırır.
    Bu fonksiyon thread içinde çalışır (non-blocking).
    """
    domain_id = team.get("domain_id")
    domain = get_domain(domain_id)
    if not domain:
        update_dashboard(agent="System", task="Hata", log="❌ Domain bulunamadı!")
        return

    agent_ids = team.get("agent_order") or team.get("agents", [])
    team_name = team.get("name", "Unknown")
    total_agents = len(agent_ids)

    # Şirket bilgi bankasını yükle
    company_knowledge = load_knowledge_for_agent(domain_id)
    knowledge_status = f"📚 Eğitim Merkezi yüklendi ({len(company_knowledge)} karakter)" if company_knowledge else "📚 Eğitim Merkezi boş (henüz eğitim verisi eklenmemiş)"
    update_dashboard(agent="System", task="Eğitim Merkezi", log=knowledge_status)
    all_outputs = []

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    update_dashboard(
        agent="System", task="Takım Başlatılıyor",
        project=team_name, step=f"0/{total_agents}",
        log=f"🚀 '{team_name}' takımı görev üzerinde çalışmaya başlıyor: {task_description[:80]}..."
    )

    previous_output = ""

    for i, agent_id in enumerate(agent_ids):
        agent_config = domain["agents"].get(agent_id)
        if not agent_config:
            update_dashboard(log=f"⚠️ Agent bulunamadı: {agent_id}")
            continue

        step = f"{i + 1}/{total_agents}"
        agent_name = agent_config["name"]
        agent_icon = agent_config["icon"]

        update_dashboard(
            agent=agent_name, task=f"{agent_icon} Çalışıyor...",
            project=team_name, step=step,
            log=f"{agent_icon} {agent_name} çalışıyor... (Adım {step})"
        )

        try:
            # CrewAI agent oluştur (şirket bilgisi ile)
            crew_agent = create_crewai_agent(agent_config, llm, company_knowledge)

            # Görev açıklaması
            full_desc = build_task_description(agent_config, task_description, previous_output)

            crew_task = Task(
                description=full_desc,
                agent=crew_agent,
                expected_output=f"{agent_config['role']} çıktısı"
            )

            crew = Crew(
                agents=[crew_agent],
                tasks=[crew_task],
                verbose=False,
                process=Process.sequential
            )

            result = crew.kickoff()
            output = str(result)

            # Maliyet kaydet (tahmini token - gerçek callback olmadan)
            estimated_input = len(full_desc.split()) * 2
            estimated_output = len(output.split()) * 2
            cost_tracker.log_usage(
                team_id=team.get("id", "unknown"),
                agent_id=agent_id,
                agent_name=agent_name,
                input_tokens=estimated_input,
                output_tokens=estimated_output,
                model="gpt-4o-mini",
                task_description=task_description[:100]
            )

            all_outputs.append({
                "agent_id": agent_id,
                "agent_name": agent_name,
                "icon": agent_icon,
                "output": output
            })

            previous_output = output

            update_dashboard(
                agent=agent_name, task=f"✅ Tamamlandı",
                step=step,
                log=f"✅ {agent_name} tamamlandı! ({len(output)} karakter çıktı)"
            )

        except Exception as e:
            error_msg = str(e)[:200]
            update_dashboard(
                agent=agent_name, task="❌ Hata!",
                step=step,
                log=f"❌ {agent_name} hata: {error_msg}"
            )
            all_outputs.append({
                "agent_id": agent_id,
                "agent_name": agent_name,
                "icon": agent_icon,
                "output": f"HATA: {error_msg}"
            })

    # Tamamlandı
    update_dashboard(
        agent="System", task="✅ Tüm Görevler Tamamlandı",
        project=team_name, step="Done",
        log=f"🎉 Takım '{team_name}' tüm görevleri tamamladı! ({total_agents} agent çalıştı)"
    )

    # Sonuçları kaydet
    save_task_result(task_id, team, task_description, all_outputs)

    return all_outputs


def extract_code_blocks(text: str) -> list:
    """Markdown kod bloklarını çıkar ve dosya olarak kaydetmek için bilgi döndür"""
    import re
    blocks = []
    # ```language ... ``` formatındaki blokları bul
    pattern = r'```(\w+)?\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    for lang, code in matches:
        code = code.strip()
        if not code or len(code) < 20:
            continue

        # Dosya adını bulmaya çalış (ilk yorum satırından)
        filename = None
        first_line = code.split('\n')[0].strip()

        # // filename.js veya # filename.py formatı (göreceli yolları destekler)
        comment_patterns = [
            r'^//\s*([a-zA-Z0-9_\-\./\\]+\.\w+)',     # JS/CSS/TS/JSX yorum
            r'^#\s*([a-zA-Z0-9_\-\./\\]+\.\w+)',      # Python/bash/YAML yorum
            r'^/\*\s*([a-zA-Z0-9_\-\./\\]+\.\w+)',    # CSS block yorum
        ]
        for cp in comment_patterns:
            m = re.match(cp, first_line)
            if m:
                filename = m.group(1).strip()
                break

        # Dosya adı bulunamadıysa dil + sıra no ile isimlendir
        if not filename:
            ext_map = {
                'javascript': 'js', 'js': 'js', 'jsx': 'jsx',
                'python': 'py', 'py': 'py',
                'html': 'html', 'css': 'css',
                'typescript': 'ts', 'tsx': 'tsx',
                'json': 'json', 'bash': 'sh', 'shell': 'sh',
                'yaml': 'yml', 'yml': 'yml',
                'dockerfile': 'Dockerfile',
                'sql': 'sql', 'java': 'java',
            }
            ext = ext_map.get(lang or '', 'txt')
            filename = f"file_{len(blocks) + 1}.{ext}"

        blocks.append({
            "filename": filename,
            "language": lang or "text",
            "code": code,
            "lines": len(code.split('\n'))
        })

    return blocks


def save_project_files(task_id: str, outputs: list) -> list:
    """Agent çıktılarından kod bloklarını çıkar ve dosya olarak kaydet"""
    import os
    project_dir = os.path.join(os.path.dirname(__file__), "generated_projects", task_id)
    os.makedirs(project_dir, exist_ok=True)

    all_files = []
    for output in outputs:
        blocks = extract_code_blocks(output.get("output", ""))
        for block in blocks:
            # Alt dizin yapısını koru (src/components/File.js gibi)
            filename = block["filename"]
            filepath = os.path.join(project_dir, filename)

            # Alt dizinleri oluştur
            file_dir = os.path.dirname(filepath)
            if file_dir:
                os.makedirs(file_dir, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(block["code"])

            all_files.append({
                "filename": filename,
                "language": block["language"],
                "lines": block["lines"],
                "agent": output.get("agent_name", "Unknown"),
                "agent_icon": output.get("icon", "📄"),
                "size": len(block["code"])
            })

    return all_files


def save_task_result(task_id: str, team: dict, task_description: str, outputs: list):
    """Görev sonuçlarını dosyaya kaydet + kod dosyalarını çıkar"""
    import json
    import os

    results_dir = os.path.join(os.path.dirname(__file__), "task_results")
    os.makedirs(results_dir, exist_ok=True)

    # Kod bloklarını dosya olarak kaydet
    generated_files = save_project_files(task_id, outputs)

    result = {
        "task_id": task_id,
        "team_id": team.get("id"),
        "team_name": team.get("name"),
        "task_description": task_description,
        "timestamp": datetime.now().isoformat(),
        "outputs": outputs,
        "generated_files": generated_files,
        "project_dir": f"generated_projects/{task_id}"
    }

    filepath = os.path.join(results_dir, f"{task_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    update_dashboard(
        agent="System", task="📁 Dosyalar Oluşturuldu",
        log=f"📁 {len(generated_files)} dosya oluşturuldu: generated_projects/{task_id}/"
    )


def run_team_task_async(team: dict, task_description: str, task_id: str):
    """Görevi arka planda çalıştır (non-blocking)"""
    thread = threading.Thread(
        target=execute_team_task,
        args=(team, task_description, task_id),
        daemon=True
    )
    thread.start()
    return thread
