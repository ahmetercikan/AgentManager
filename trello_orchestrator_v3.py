"""
Trello Orchestrator V3 - .agent Yapısı Destekli

V2'nin tüm özelliklerini içerir + .agent/ yapısından:
- Skills (.agent/skills/{name}/SKILL.md)
- Rules (.agent/rules/*.md)
- Workflows (.agent/workflows/*.md)
otomatik yükler ve agent'lara enjekte eder.

YENILIKLER (V2'ye göre):
- .agent/skills/ altından SKILL.md yükleme (eski skills/ yerine)
- .agent/rules/ altından rules yükleme ve agent'lara enjekte etme
- .agent/workflows/ altından workflow eşleşme ve uygulama
- Tüm skill/rule/workflow yükleme tek bir modülden yönetiliyor
"""
import os
import signal
import sys
import io
import glob
import re
from datetime import datetime

# Windows encoding fix
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import warnings
import time
import json
from typing import Dict, List, Optional
import builtins

STOP_ORCHESTRATOR = False
ORCHESTRATOR_LOGS = []

# Self-Healing Onay Mekanizması
# PENDING_APPROVAL: Onay bekleyen düzeltme verisi (None = bekleyen yok)
# APPROVAL_RESULT: None = henüz karar verilmedi, "approved" veya "rejected"
PENDING_APPROVAL = None
APPROVAL_RESULT = None
_builtin_print = builtins.print

def print(*args, **kwargs):
    msg = " ".join(str(a) for a in args)
    ORCHESTRATOR_LOGS.append(msg)
    if len(ORCHESTRATOR_LOGS) > 500:
        ORCHESTRATOR_LOGS.pop(0)
    _builtin_print(*args, **kwargs)

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

warnings.filterwarnings('ignore')

from crewai import Agent, Task, Crew, Process, LLM
from trello_helper import TrelloHelper

# ============================================================
# YAPILANDIRMA
# ============================================================

# Trello Bilgileri
TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY", "27cf0f02c65de97bf9f699cd79b5fc18")
TRELLO_TOKEN = os.environ.get("TRELLO_TOKEN", "YOUR_TRELLO_TOKEN")

# OpenAI API Key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM Modeli
my_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Trello Helper
trello = TrelloHelper(TRELLO_API_KEY, TRELLO_TOKEN)

# Proje kök dizini
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.join(PROJECT_ROOT, '.agent')
PROJECTS_DIR = os.path.join(PROJECT_ROOT, 'Projects')


# ============================================================
# .AGENT YAPISINI YUKLEME
# ============================================================

def load_skill(skill_name: str) -> str:
    """
    .agent/skills/{skill_name}/ klasöründen skill yükler.
    
    SKILL.md ana dosyasının yanı sıra:
    - examples/ altındaki tüm dosyaları (örnek bileşenler)
    - resources/ altındaki tüm dosyaları (tokenlar, snippetler, checklist)
    de yükleyip birleştirir.
    
    Önce kebab-case dener (is-analisti),
    bulamazsa underscore dener (is_analisti),
    bulamazsa eski skills/ klasöründen dener (geriye uyumluluk).
    """
    
    def _load_skill_dir(skill_dir: str) -> str:
        """Bir skill dizinindeki SKILL.md + examples/ + resources/ yükler."""
        skill_md = os.path.join(skill_dir, 'SKILL.md')
        if not os.path.exists(skill_md):
            return ""
        
        # 1. Ana SKILL.md
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
            # YAML frontmatter'ı çıkar (--- ... --- bloğu)
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
        except Exception as e:
            print(f"⚠️  Skill yükleme hatası ({skill_md}): {e}")
            return ""
        
        # 2. examples/ ve resources/ alt klasörlerini yükle
        extras = []
        for subdir_name in ['examples', 'resources']:
            subdir = os.path.join(skill_dir, subdir_name)
            if not os.path.isdir(subdir):
                continue
            
            for fname in sorted(os.listdir(subdir)):
                fpath = os.path.join(subdir, fname)
                if not os.path.isfile(fpath):
                    continue
                # Sadece metin dosyalarını yükle
                ext = os.path.splitext(fname)[1].lower()
                if ext not in ('.md', '.tsx', '.jsx', '.ts', '.js', '.json', '.css', '.txt', '.sh'):
                    continue
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    # Dosya uzantısına göre kod bloğu formatla
                    lang_map = {'.tsx': 'tsx', '.jsx': 'jsx', '.ts': 'typescript', '.js': 'javascript',
                                '.json': 'json', '.css': 'css', '.sh': 'bash', '.md': 'markdown'}
                    lang = lang_map.get(ext, '')
                    
                    if ext == '.md':
                        extras.append(f"\n\n--- {subdir_name}/{fname} ---\n{file_content}")
                    else:
                        extras.append(f"\n\n--- {subdir_name}/{fname} ---\n```{lang}\n{file_content}\n```")
                except Exception as e:
                    print(f"   ⚠️  Skill dosya yükleme hatası ({fpath}): {e}")
        
        if extras:
            content += "\n\n" + "=" * 40 + "\nÖRNEK BİLEŞENLER VE KAYNAKLAR:\n" + "=" * 40
            content += "".join(extras)
            print(f"   📂 Skill ek dosyalar yüklendi: {len(extras)} dosya ({subdir_name})")
        
        return content
    
    # 1. .agent/skills/{kebab-case}/
    skill_dir = os.path.join(AGENT_DIR, 'skills', skill_name)
    if os.path.isdir(skill_dir):
        result = _load_skill_dir(skill_dir)
        if result:
            return result

    # 2. Underscore versiyonu dene
    skill_name_underscore = skill_name.replace('-', '_')
    skill_dir_underscore = os.path.join(AGENT_DIR, 'skills', skill_name_underscore)
    if os.path.isdir(skill_dir_underscore):
        result = _load_skill_dir(skill_dir_underscore)
        if result:
            return result

    # 3. Geriye uyumluluk: eski skills/ klasörü
    legacy_path = os.path.join(PROJECT_ROOT, 'skills', f'{skill_name_underscore}.md')
    if os.path.exists(legacy_path):
        print(f"⚠️  Eski skills/ klasöründen yükleniyor (deprecated): {legacy_path}")
        try:
            with open(legacy_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Legacy skill yükleme hatası: {e}")

    print(f"⚠️  Skill bulunamadı: {skill_name}")
    return ""


def load_all_rules() -> Dict[str, str]:
    """
    .agent/rules/ altındaki tüm .md dosyalarını yükler.
    
    Returns:
        Dict[str, str] - {dosya_adi: icerik} formatında
    """
    rules = {}
    rules_dir = os.path.join(AGENT_DIR, 'rules')
    
    if not os.path.exists(rules_dir):
        print("⚠️  .agent/rules/ klasörü bulunamadı")
        return rules
    
    for rule_file in glob.glob(os.path.join(rules_dir, '*.md')):
        rule_name = os.path.splitext(os.path.basename(rule_file))[0]
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                rules[rule_name] = f.read()
                print(f"   ✅ Rule yüklendi: {rule_name}")
        except Exception as e:
            print(f"   ⚠️  Rule yükleme hatası ({rule_name}): {e}")
    
    return rules


def load_rules_for_type(project_type: str, rules: Dict[str, str]) -> str:
    """
    Proje tipine göre uygun rule'ları birleştirir.
    
    Args:
        project_type: 'backend', 'frontend', 'fullstack', 'cli' vb.
        rules: load_all_rules() çıktısı
    
    Returns:
        Birleştirilmiş rules metni
    """
    applicable_rules = []
    
    # Proje tipine göre uygun rule'ları seç
    if project_type in ('backend', 'cli', 'fullstack'):
        if 'backend' in rules:
            applicable_rules.append(rules['backend'])
    
    if project_type in ('frontend', 'fullstack'):
        if 'frontend-rules' in rules:
            applicable_rules.append(rules['frontend-rules'])
    
    # Genel rules (her zaman uygulanan)
    for rule_name, rule_content in rules.items():
        if rule_name not in ('backend', 'frontend-rules'):
            applicable_rules.append(rule_content)
    
    return "\n\n---\n\n".join(applicable_rules) if applicable_rules else ""


def load_workflow(workflow_name: str) -> Optional[str]:
    """
    .agent/workflows/ altından workflow yükler.
    
    Returns:
        Workflow içeriği veya None
    """
    workflow_path = os.path.join(AGENT_DIR, 'workflows', f'{workflow_name}.md')
    
    if os.path.exists(workflow_path):
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Workflow yükleme hatası ({workflow_name}): {e}")
    
    return None


def match_workflow(card_name: str, card_desc: str) -> Optional[str]:
    """
    Kart başlığı ve açıklamasına göre uygun workflow'u eşleştirir.
    
    .agent/workflows/ altındaki tüm .md dosyalarını tarar,
    description alanındaki anahtar kelimeleri kart ile karşılaştırır.
    
    Returns:
        Eşleşen workflow içeriği veya None
    """
    workflows_dir = os.path.join(AGENT_DIR, 'workflows')
    
    if not os.path.exists(workflows_dir):
        return None
    
    card_text = f"{card_name} {card_desc}".lower()
    
    for wf_file in glob.glob(os.path.join(workflows_dir, '*.md')):
        try:
            with open(wf_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # YAML frontmatter'dan description al
            wf_name = os.path.splitext(os.path.basename(wf_file))[0]
            
            # Anahtar kelime eşleşmesi
            # Workflow dosya adındaki kelimeleri kart ile karşılaştır
            keywords = wf_name.replace('-', ' ').split()
            match_count = sum(1 for kw in keywords if kw.lower() in card_text)
            
            # En az yarısı eşleşiyorsa
            if match_count >= len(keywords) / 2:
                print(f"   🔗 Workflow eşleşmesi: {wf_name}")
                return content
                
        except Exception as e:
            print(f"   ⚠️  Workflow okuma hatası: {e}")
    
    return None


def list_available_skills() -> List[str]:
    """
    .agent/skills/ altındaki tüm skill'leri listeler.
    """
    skills_dir = os.path.join(AGENT_DIR, 'skills')
    skills = []
    
    if os.path.exists(skills_dir):
        for item in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, item, 'SKILL.md')
            if os.path.isdir(os.path.join(skills_dir, item)) and os.path.exists(skill_path):
                skills.append(item)
    
    return skills


# ============================================================
# DASHBOARD UPDATE HELPER
# ============================================================

def update_dashboard(agent="Idle", task="Waiting...", project="None", step="0/0", log=None):
    """Monitor Dashboard'a durum guncellemesi gonderir"""
    import requests as req
    try:
        data = {
            "agent": agent,
            "task": task,
            "project": project,
            "step": step
        }
        if log:
            data["log"] = log
            
        req.post("http://localhost:5000/api/update_status", json=data, timeout=1)
    except:
        pass  # Dashboard calismiyorsa hata verme


# ============================================================
# V3 AGENT OLUŞTURMA (.agent/ DESTEKLİ)
# ============================================================

def create_analyst_agent(rules_text: str = ""):
    """
    Backlog'daki kartları analiz eden Analist Agent
    .agent/skills/is-analisti skill'i + rules ile donatılmış
    """
    analyst_skill = load_skill('is-analisti')

    return Agent(
        role='Kidemli Is Analist',
        goal='Trello Backlog kartlarini analiz edip teknik gereksinimlere donusturmek',
        backstory=f"""
        Sen deneyimli bir is analistisin. Kullanicinin yazdigi genel istekleri
        alip bunlari teknik gereksinimlere donusturuyorsun.

        Gorevlerin:
        - Kullanicinin istegini anla
        - Proje adini belirle
        - Proje tipini belirle (backend, frontend, fullstack, cli, mobile, analyzer)
          NOT: Eger kullanici mevcut bir projeyi analiz etmek, incelemek, kod kalitesini
          olcmek veya iyilestirme onerileri almak istiyorsa project_type='analyzer' kullan.
        - Programlama dilini/framework'u sec
        - Detayli gereksinimleri cikar
        - Dosya adlarini belirle (backend ve frontend ayri ise ikisini de belirt)

        ========================
        IS ANALISTI PRO KURALLARI:
        ========================
        {analyst_skill}

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}

        ONEMLI: Ciktin JSON formatinda olmali ve su yapiyi takip etmeli:
        {{
            "project_name": "Proje Adi",
            "description": "Kisa aciklama",
            "project_type": "fullstack",
            "programming_language": "Python",
            "file_name": "main.py",
            "requirements": ["Req 1", "Req 2"],
            "backend": {{
                "programming_language": "Python",
                "framework": "FastAPI",
                "file_name": "backend_api.py",
                "requirements": ["Backend Req 1"]
            }},
            "frontend": {{
                "framework": "React",
                "file_name": "App.jsx",
                "requirements": ["Frontend Req 1"]
            }}
        }}
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_solution_architect_agent(rules_text: str = ""):
    """Solution Architect Agent - .agent/skills/solution-architect destekli"""
    architect_skill = load_skill('solution-architect')

    return Agent(
        role='Kidemli Cozum Mimari (Solution Architect)',
        goal='Analist ciktisini teknik mimariye donusturmek ve validasyon yapmak',
        backstory=f"""
        Sen deneyimli bir Cozum Mimari'sin.
        Analistin belirledigi gereksinimleri alir, teknik olarak en uygun mimariyi tasarlarsin.

        ========================
        SOLUTION ARCHITECT PRO KURALLARI:
        ========================
        {architect_skill}

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}

        CIKTI:
        Detayli teknik tasarim dokumani (Markdown formatinda)
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_orchestrator_agent(rules_text: str = ""):
    """Isleri dagitan Orchestrator Agent"""
    return Agent(
        role='Orkestrator (Proje Yoneticisi)',
        goal='Analiz edilmis isleri PM, Developer, QA ajanlarına dagitmak',
        backstory=f"""
        Sen deneyimli bir proje yoneticisisin ve ekip koordinasyonu konusunda uzmansin.
        Analistten gelen teknik gereksinimleri alip detayli bir proje plani olusturuyorsun.

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}

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


def create_backend_developer_agent(programming_language: str = "Python", rules_text: str = ""):
    """Backend Developer Agent - .agent/skills/backend-developer destekli"""
    backend_skill = load_skill('backend-developer')

    return Agent(
        role=f'Kidemli Backend Developer ({programming_language})',
        goal=f'Yuksek kaliteli backend {programming_language} kodu yazmak - API, veritabani, is mantigi',
        backstory=f"""
        Sen {programming_language} konusunda uzman bir backend gelistiricisisin.

        ========================
        BACKEND DEVELOPER PRO KURALLARI:
        ========================
        {backend_skill}

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}

        ONEMLI: Kodunu her zaman kod blogu icinde ver!
        Python icin ```python```, JavaScript icin ```javascript```
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_frontend_developer_agent(framework: str = "React", rules_text: str = ""):
    """Frontend Developer Agent - .agent/skills/frontend-design-pro destekli (UI/UX + Glassmorphism birleşik)"""
    frontend_skill = load_skill('frontend-design-pro')

    return Agent(
        role=f'Kidemli Frontend Developer & UI/UX Uzmani ({framework})',
        goal=f'Profesyonel, erisilebilir ve modern {framework} uygulamalari gelistirmek',
        backstory=f"""
        Sen {framework} konusunda uzman bir frontend gelistirici ve UI/UX tasarimcisisin.

        ========================
        FRONTEND DESIGN PRO KURALLARI (UI/UX + Glassmorphism):
        ========================
        {frontend_skill}

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}

        ONEMLI: Kodunu her zaman kod blogu icinde ver!
        JavaScript icin ```javascript```, TypeScript icin ```typescript```
        CSS dosyasini da ayri bir kod blogunda ver! CSS icin ```css```
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )



def create_developer_agent(programming_language: str = "Python", rules_text: str = ""):
    """Generic Developer Agent - Geriye uyumluluk için"""
    return Agent(
        role=f'Kıdemli {programming_language} Yazilimci',
        goal=f'Yuksek kaliteli {programming_language} kodu yazmak',
        backstory=f"""
        Sen {programming_language} konusunda uzman bir yazilimcisin.
        Temiz, okunabilir ve calisir kod yazarsın.

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}

        ONEMLI: Kodunu her zaman kod blogu icinde ver!
        Python icin ```python```, JavaScript icin ```javascript```
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


def create_qa_agent(rules_text: str = ""):
    """QA Test Agent - .agent/skills/qa-engineer destekli"""
    qa_skill = load_skill('qa-engineer')

    return Agent(
        role='Kidemli Test Uzmani (QA Engineer)',
        goal='Kodu test etmek, bug bulmak ve kalite standartlarini saglamak',
        backstory=f"""
        Sen deneyimli bir QA muhendisisin.

        ========================
        QA ENGINEER PRO KURALLARI:
        ========================
        {qa_skill}

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


# ============================================================
# YARDIMCI FONKSIYONLAR
# ============================================================

def sanitize_project_name(project_name: str) -> str:
    """Proje adını dosya sistemi için güvenli hale getirir"""
    # Boşlukları alt çizgi yap
    safe_name = project_name.replace(' ', '_')
    # Sadece alfanümerik, alt çizgi ve tire bırak
    safe_name = re.sub(r'[^\w\-]', '', safe_name)
    # Başta/sonda alt çizgi temizle
    safe_name = safe_name.strip('_')
    return safe_name or 'unnamed_project'


def get_project_dir(project_name: str) -> str:
    """
    Proje için benzersiz bir dizin yolu döndürür.
    
    Projects/{proje_adi}/ dizinini oluşturur.
    Aynı isimde klasör varsa _v2, _v3 gibi versiyon eki ekler.
    """
    safe_name = sanitize_project_name(project_name)
    project_dir = os.path.join(PROJECTS_DIR, safe_name)
    
    # Çakışma kontrolü: aynı isimde klasör varsa versiyon ekle
    if os.path.exists(project_dir):
        version = 2
        while os.path.exists(f"{project_dir}_v{version}"):
            version += 1
        project_dir = f"{project_dir}_v{version}"
    
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def extract_code(output: str, language: str) -> str:
    """AI output'undan kod bloğunu çıkarır"""
    patterns = [
        rf'```{language.lower()}\n([\s\S]*?)```',
        rf'```{language.upper()}\n([\s\S]*?)```',
        r'```\n([\s\S]*?)```'
    ]

    for pattern in patterns:
        match = re.search(pattern, output)
        if match:
            return match.group(1).strip()

    return output.strip()


# ============================================================
# PROJE SCAFFOLD — Gerçek, çalıştırılabilir proje yapısı oluşturur
# ============================================================

import subprocess

def scaffold_frontend_project(project_dir: str, project_name: str, backend_port: int = 8000) -> str:
    """
    Vite + React + Tailwind CSS projesi scaffold eder.

    Oluşturulan yapı:
    frontend/
    ├── node_modules/
    ├── public/
    ├── src/
    │   ├── App.jsx       ← AI tarafından üretilen kod buraya yazılır
    │   ├── App.css
    │   ├── index.css
    │   └── main.jsx
    ├── .gitignore
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    └── README.md

    Returns:
        Frontend dizin yolu (project_dir/frontend)
    """
    frontend_dir = os.path.join(project_dir, "frontend")

    # Zaten var mı kontrol et
    if os.path.exists(os.path.join(frontend_dir, "package.json")):
        print(f"   ℹ️ Frontend scaffold zaten mevcut, atlanıyor")
        return frontend_dir

    print(f"\n📦 Frontend scaffold oluşturuluyor...")

    try:
        # 1. Vite + React projesi oluştur
        subprocess.run(
            ["npx", "-y", "create-vite@latest", "frontend", "--template", "react"],
            cwd=project_dir,
            capture_output=True, text=True, timeout=60,
            stdin=subprocess.DEVNULL
        )
        print(f"   ✅ Vite + React projesi oluşturuldu")

        # 2. npm install
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            capture_output=True, text=True, timeout=120,
            stdin=subprocess.DEVNULL
        )
        print(f"   ✅ npm paketleri yüklendi")

        # 3. Tailwind CSS kur
        subprocess.run(
            ["npm", "install", "-D", "tailwindcss", "@tailwindcss/vite"],
            cwd=frontend_dir,
            capture_output=True, text=True, timeout=60,
            stdin=subprocess.DEVNULL
        )
        print(f"   ✅ Tailwind CSS kuruldu")

        # 4. vite.config.js — Tailwind + API proxy
        vite_config = f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({{
  plugins: [react(), tailwindcss()],
  server: {{
    proxy: {{
      '/api': {{
        target: 'http://localhost:{backend_port}',
        changeOrigin: true,
      }}
    }}
  }}
}})
"""
        with open(os.path.join(frontend_dir, "vite.config.js"), "w", encoding="utf-8") as f:
            f.write(vite_config)
        print(f"   ✅ vite.config.js yapılandırıldı (API proxy → port {backend_port})")

        # 5. index.css — Tailwind import
        index_css_path = os.path.join(frontend_dir, "src", "index.css")
        with open(index_css_path, "w", encoding="utf-8") as f:
            f.write('@import "tailwindcss";\n')
        print(f"   ✅ Tailwind CSS import edildi")

        # 6. App.css — boş animasyonlar dosyası
        app_css_content = """@keyframes slide-in {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-slide-in {
  animation: slide-in 0.3s ease-out;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
"""
        with open(os.path.join(frontend_dir, "src", "App.css"), "w", encoding="utf-8") as f:
            f.write(app_css_content)

        # 7. README.md
        readme = f"""# {project_name} — Frontend

## Kurulum
```bash
npm install
```

## Çalıştırma
```bash
npm run dev
```

Frontend **http://localhost:5173** adresinde çalışır.
API istekleri otomatik olarak **http://localhost:{backend_port}** adresine proxy edilir.

## Teknolojiler
- React
- Vite
- Tailwind CSS
"""
        with open(os.path.join(frontend_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme)

        print(f"   ✅ Frontend scaffold tamamlandı: frontend/")
        return frontend_dir

    except subprocess.TimeoutExpired:
        print(f"   ⚠️ Scaffold timeout — temel yapı oluşturuldu")
        os.makedirs(os.path.join(frontend_dir, "src"), exist_ok=True)
        return frontend_dir
    except Exception as e:
        print(f"   ⚠️ Scaffold hatası: {e} — manual kurulum gerekli")
        os.makedirs(os.path.join(frontend_dir, "src"), exist_ok=True)
        return frontend_dir


def scaffold_backend_project(project_dir: str, project_name: str, framework: str = "FastAPI", language: str = "Python") -> str:
    """
    Backend proje yapısı oluşturur.

    Oluşturulan yapı:
    backend/
    ├── main.py veya backend_api.py  ← AI tarafından üretilen kod
    ├── requirements.txt
    ├── .gitignore
    └── README.md

    Returns:
        Backend dizin yolu (project_dir/backend)
    """
    backend_dir = os.path.join(project_dir, "backend")
    os.makedirs(backend_dir, exist_ok=True)

    print(f"\n📦 Backend scaffold oluşturuluyor...")

    # 1. requirements.txt
    if framework.lower() in ("fastapi", "fast_api"):
        deps = "fastapi\nuvicorn[standard]\nsqlalchemy\npydantic\npython-dotenv\n"
    elif framework.lower() in ("flask",):
        deps = "flask\nflask-cors\nsqlalchemy\npython-dotenv\n"
    elif framework.lower() in ("django",):
        deps = "django\ndjango-cors-headers\ndjango-rest-framework\npython-dotenv\n"
    else:
        deps = "requests\npython-dotenv\n"

    req_path = os.path.join(backend_dir, "requirements.txt")
    if not os.path.exists(req_path):
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(deps)
        print(f"   ✅ requirements.txt oluşturuldu")

    # 2. .gitignore
    gitignore = """__pycache__/
*.pyc
*.pyo
.env
*.db
*.sqlite3
venv/
.venv/
"""
    gi_path = os.path.join(backend_dir, ".gitignore")
    if not os.path.exists(gi_path):
        with open(gi_path, "w", encoding="utf-8") as f:
            f.write(gitignore)

    # 3. README.md
    readme = f"""# {project_name} — Backend

## Kurulum
```bash
pip install -r requirements.txt
```

## Çalıştırma
```bash
python backend_api.py
```

Backend **http://localhost:8000** adresinde çalışır.
API dökümantasyonu: **http://localhost:8000/docs**

## Teknolojiler
- {language}
- {framework}
- SQLAlchemy (SQLite)
"""
    readme_path = os.path.join(backend_dir, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

    print(f"   ✅ Backend scaffold tamamlandı: backend/")
    return backend_dir


def scaffold_fullstack_project(project_dir: str, project_name: str, backend_framework: str = "FastAPI", backend_language: str = "Python") -> Dict[str, str]:
    """
    Tam fullstack proje yapısı oluşturur.

    Yapı:
    {project_name}/
    ├── backend/
    │   ├── backend_api.py
    │   ├── requirements.txt
    │   ├── .gitignore
    │   └── README.md
    ├── frontend/
    │   ├── node_modules/
    │   ├── public/
    │   ├── src/
    │   │   ├── App.jsx
    │   │   ├── App.css
    │   │   ├── index.css
    │   │   └── main.jsx
    │   ├── .gitignore
    │   ├── index.html
    │   ├── package.json
    │   ├── vite.config.js
    │   └── README.md
    └── README.md

    Returns:
        {"backend_dir": "...", "frontend_dir": "...", "project_dir": "..."}
    """
    print(f"\n{'='*60}")
    print(f"📁 FULLSTACK PROJE SCAFFOLD: {project_name}")
    print(f"{'='*60}")

    # Backend scaffold
    backend_dir = scaffold_backend_project(project_dir, project_name, backend_framework, backend_language)

    # Frontend scaffold
    frontend_dir = scaffold_frontend_project(project_dir, project_name)

    # Root README.md
    root_readme = f"""# {project_name}

Fullstack uygulama — AI Agent tarafından oluşturuldu.

## Proje Yapısı
```
{project_name}/
├── backend/      → {backend_language} ({backend_framework}) API
├── frontend/     → React + Vite + Tailwind CSS
└── README.md
```

## Hızlı Başlangıç

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python backend_api.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
"""
    root_readme_path = os.path.join(project_dir, "README.md")
    with open(root_readme_path, "w", encoding="utf-8") as f:
        f.write(root_readme)

    print(f"\n✅ Fullstack scaffold tamamlandı!")
    print(f"   📂 {os.path.relpath(project_dir, PROJECT_ROOT)}/")
    print(f"   ├── backend/")
    print(f"   ├── frontend/")
    print(f"   └── README.md")

    return {
        "backend_dir": backend_dir,
        "frontend_dir": frontend_dir,
        "project_dir": project_dir
    }



def _clean_json_string(json_str: str) -> str:
    """
    AI çıktısından gelen JSON string'ini temizler.
    Türkçe karakter, trailing comma, kontrol karakterleri vb. sorunları giderir.
    """
    # Yorum satırlarını temizle
    json_str = re.sub(r'#[^\n]*', '', json_str)
    json_str = re.sub(r'//[^\n]*', '', json_str)
    
    # Kontrol karakterlerini temizle (tab ve newline hariç)
    json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_str)
    
    # Trailing comma'ları temizle: ,} veya ,] durumları
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Tek tırnakları çift tırnağa çevir (JSON standardı)
    # Ama dikkat: string içindeki tek tırnakları bozma
    json_str = json_str.replace("'", '"')
    
    return json_str.strip()


def parse_analyst_output(analyst_output: str) -> Optional[Dict]:
    """
    Analistin çıktısını parse eder ve TaskConfig bilgilerini çıkarır.
    
    Birden fazla strateji ile parse dener:
    1. Doğrudan JSON parse
    2. Temizlenmiş JSON parse (trailing comma, Türkçe karakter vb.)
    3. Nested JSON objeleri ile parse
    4. Regex tabanlı manuel parsing (fallback)
    """
    
    # ========== STRATEJİ 1: Doğrudan JSON parse ==========
    try:
        if '{' in analyst_output and '}' in analyst_output:
            # En dıştaki JSON objesini bul
            json_match = re.search(r'\{[\s\S]*\}', analyst_output)
            if json_match:
                json_str = json_match.group(0)
                json_str = _clean_json_string(json_str)
                data = json.loads(json_str)
                
                if isinstance(data, dict) and data.get("project_name"):
                    if "project_type" not in data:
                        data["project_type"] = "cli"
                    print(f"   ✅ JSON parse başarılı (Strateji 1)")
                    return data
    except json.JSONDecodeError as e:
        print(f"   ⚠️ JSON parse hatası (Strateji 1): {e}")
    
    # ========== STRATEJİ 2: Sadece üst seviye JSON'ı parse et (nested objeleri string yap) ==========
    try:
        if '{' in analyst_output and '}' in analyst_output:
            json_match = re.search(r'\{[\s\S]*\}', analyst_output)
            if json_match:
                json_str = json_match.group(0)
                json_str = _clean_json_string(json_str)
                
                # Nested objeleri geçici olarak kaldır ve ayrıca parse et
                # Önce backend ve frontend bloklarını çıkar
                backend_match = re.search(r'"backend"\s*:\s*(\{[^{}]*\})', json_str)
                frontend_match = re.search(r'"frontend"\s*:\s*(\{[^{}]*\})', json_str)
                
                backend_data = None
                frontend_data = None
                
                if backend_match:
                    try:
                        backend_str = _clean_json_string(backend_match.group(1))
                        backend_data = json.loads(backend_str)
                    except:
                        pass
                
                if frontend_match:
                    try:
                        frontend_str = _clean_json_string(frontend_match.group(1))
                        frontend_data = json.loads(frontend_str)
                    except:
                        pass
                
                # Nested objeleri kaldırıp üst seviye alanları parse et
                simplified = re.sub(r'"backend"\s*:\s*\{[^{}]*\}', '', json_str)
                simplified = re.sub(r'"frontend"\s*:\s*\{[^{}]*\}', '', simplified)
                simplified = _clean_json_string(simplified)
                
                try:
                    data = json.loads(simplified)
                except:
                    # Son çare: basit alanları regex ile çek
                    data = {}
                
                if backend_data:
                    data['backend'] = backend_data
                if frontend_data:
                    data['frontend'] = frontend_data
                
                if data.get("project_name"):
                    if "project_type" not in data:
                        data["project_type"] = "cli"
                    print(f"   ✅ JSON parse başarılı (Strateji 2)")
                    return data
    except Exception as e:
        print(f"   ⚠️ JSON parse hatası (Strateji 2): {e}")
    
    # ========== STRATEJİ 3: Regex tabanlı manuel parsing (fallback) ==========
    print(f"   ⚠️ JSON parse başarısız, regex fallback kullanılıyor (Strateji 3)")
    
    result = {
        "project_name": "",
        "description": "",
        "project_type": "cli",
        "programming_language": "Python",
        "file_name": "",
        "requirements": []
    }

    # Temel alanları regex ile çek
    field_patterns = {
        "project_name": r'"project_name"\s*:\s*"([^"]+)"',
        "description": r'"description"\s*:\s*"([^"]+)"',
        "project_type": r'"project_type"\s*:\s*"([^"]+)"',
        "programming_language": r'"programming_language"\s*:\s*"([^"]+)"',
        "file_name": r'"file_name"\s*:\s*"([^"]+)"',
    }
    
    for field, pattern in field_patterns.items():
        match = re.search(pattern, analyst_output)
        if match:
            result[field] = match.group(1)
    
    # Requirements listesini çek
    req_match = re.search(r'"requirements"\s*:\s*\[([\s\S]*?)\]', analyst_output)
    if req_match:
        req_str = req_match.group(1)
        requirements = re.findall(r'"([^"]+)"', req_str)
        result["requirements"] = requirements
    
    # Nested backend/frontend objelerini regex ile çek
    backend_block = re.search(r'"backend"\s*:\s*\{([^{}]*)\}', analyst_output)
    if backend_block:
        backend = {}
        for field in ['programming_language', 'framework', 'file_name']:
            m = re.search(rf'"{field}"\s*:\s*"([^"]+)"', backend_block.group(1))
            if m:
                backend[field] = m.group(1)
        backend_reqs = re.search(r'"requirements"\s*:\s*\[([^\]]*)\]', backend_block.group(1))
        if backend_reqs:
            backend['requirements'] = re.findall(r'"([^"]+)"', backend_reqs.group(1))
        if backend:
            result['backend'] = backend
    
    frontend_block = re.search(r'"frontend"\s*:\s*\{([^{}]*)\}', analyst_output)
    if frontend_block:
        frontend = {}
        for field in ['framework', 'file_name']:
            m = re.search(rf'"{field}"\s*:\s*"([^"]+)"', frontend_block.group(1))
            if m:
                frontend[field] = m.group(1)
        frontend_reqs = re.search(r'"requirements"\s*:\s*\[([^\]]*)\]', frontend_block.group(1))
        if frontend_reqs:
            frontend['requirements'] = re.findall(r'"([^"]+)"', frontend_reqs.group(1))
        if frontend:
            result['frontend'] = frontend
    
    # project_type doğrulaması: backend ve frontend varsa fullstack olmalı
    if result.get('backend') and result.get('frontend'):
        result['project_type'] = 'fullstack'
    elif result.get('frontend') and not result.get('backend'):
        result['project_type'] = 'frontend'
    elif result.get('backend') and not result.get('frontend'):
        result['project_type'] = 'backend'
    
    if result["project_name"]:
        print(f"   ✅ Regex parse başarılı: project_type={result['project_type']}")
        return result
    
    return None


def handle_bugs(bug_report: str, list_ids: Dict[str, str], project_name: str, card_id: str):
    """Bug raporunu analiz edip Trello'da bug kartları oluşturur"""
    bug_pattern = r'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*(\d+)[:\s]*([^\n]+)'
    bugs_found = re.findall(bug_pattern, bug_report, re.IGNORECASE)

    bug_cards_created = []

    if bugs_found:
        print(f"\n🐛 {len(bugs_found)} BUG TESPİT EDİLDİ")

        for bug_num, bug_title in bugs_found:
            bug_detail_pattern = rf'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*{bug_num}[:\s]*{re.escape(bug_title)}([\s\S]*?)(?=(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*\d+|$)'
            detail_match = re.search(bug_detail_pattern, bug_report, re.IGNORECASE)
            bug_details = detail_match.group(1).strip() if detail_match else "Detay bulunamadi"

            priority = "Orta"
            priority_label = "orange"
            if any(word in bug_details.lower() for word in ["yuksek", "kritik", "high", "critical"]):
                priority = "Yuksek"
                priority_label = "red"
            elif any(word in bug_details.lower() for word in ["dusuk", "low", "minor"]):
                priority = "Dusuk"
                priority_label = "yellow"

            bug_card = trello.create_card(
                name=f"🐛 [BUG-{bug_num}] {project_name} - {bug_title.strip()}",
                description=f"# Bug Raporu\n\n**Proje:** {project_name}\n**Bug ID:** BUG-{bug_num}\n**Oncelik:** {priority}\n\n## Aciklama\n{bug_details}\n\n**Kaynak Kart:** {card_id}\n**Tespit Eden:** QA Agent",
                list_id=list_ids.get("Bugs"),
                labels=[priority_label]
            )

            if bug_card:
                bug_cards_created.append(bug_card['shortUrl'])
                print(f"   ✅ BUG-{bug_num}: {bug_title.strip()[:50]}...")

    if bug_cards_created:
        bug_links = "\n".join([f"- {url}" for url in bug_cards_created])
        trello.add_comment(card_id, f"🐛 OLUŞTURULAN BUG KARTLARI ({len(bug_cards_created)} adet):\n\n{bug_links}")

    return len(bug_cards_created)


# ============================================================
# SELF-HEALING: DEV → QA → (BUG) → DEV → QA → DONE DÖNGÜSÜ
# ============================================================

MAX_HEAL_ITERATIONS = 3  # Maksimum düzeltme turu

def detect_bugs_in_report(test_report: str) -> List[Dict]:
    """
    QA raporundan bug'ları yapısal olarak çıkarır.

    Returns:
        [{"id": "1", "title": "...", "description": "...", "priority": "...", "layer": "..."}]
    """
    bugs = []

    # Çoklu pattern desteği
    patterns = [
        r'(?:Bug|Hata|BUG|HATA|Error)\s*[#:]?\s*(\d+)[:\s]*([^\n]+)',
        r'(?:FAIL|FAILED|BAŞARISIZ)\s*[#:]?\s*(\d+)[:\s]*([^\n]+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, test_report, re.IGNORECASE)
        for bug_num, bug_title in matches:
            if any(b["id"] == bug_num for b in bugs):
                continue  # Duplicate'i atla

            # Detay çıkar
            detail_pattern = rf'(?:Bug|Hata|BUG|HATA|Error|FAIL)\s*[#:]?\s*{bug_num}[:\s]*{re.escape(bug_title.strip())}([\s\S]*?)(?=(?:Bug|Hata|BUG|HATA|Error|FAIL)\s*[#:]?\s*\d+|$)'
            detail_match = re.search(detail_pattern, test_report, re.IGNORECASE)
            description = detail_match.group(1).strip() if detail_match else ""

            # Öncelik çıkar
            priority = "Orta"
            if any(w in (description + bug_title).lower() for w in ["yüksek", "kritik", "high", "critical"]):
                priority = "Yüksek"
            elif any(w in (description + bug_title).lower() for w in ["düşük", "low", "minor"]):
                priority = "Düşük"

            # Katman çıkar
            layer = "Unknown"
            if any(w in (description + bug_title).lower() for w in ["backend", "api", "database", "server"]):
                layer = "Backend"
            elif any(w in (description + bug_title).lower() for w in ["frontend", "ui", "component", "render"]):
                layer = "Frontend"

            bugs.append({
                "id": bug_num,
                "title": bug_title.strip(),
                "description": description,
                "priority": priority,
                "layer": layer
            })

    return bugs


def self_heal_code(
    card: Dict,
    project_name: str,
    original_code: str,
    bug_report: str,
    bugs: List[Dict],
    developer_agent,
    qa_agent,
    list_ids: Dict[str, str],
    language: str = "python",
    file_name: str = "main.py",
    project_dir: str = "",
    iteration: int = 1
) -> tuple:
    """
    Self-Healing döngüsü: Bug raporuna göre kodu düzeltir ve tekrar test eder.

    Args:
        card: Trello kart bilgileri
        project_name: Proje adı
        original_code: Mevcut (hatalı) kod
        bug_report: QA'nın test raporu
        bugs: Tespit edilen bug listesi
        developer_agent: CrewAI developer agent
        qa_agent: CrewAI QA agent
        list_ids: Trello liste ID'leri
        language: Programlama dili
        file_name: Dosya adı
        project_dir: Proje dizini
        iteration: Mevcut düzeltme turu

    Returns:
        (fixed_code: str, final_report: str, remaining_bugs: int)
    """
    if iteration > MAX_HEAL_ITERATIONS:
        print(f"\n⚠️ Maksimum düzeltme turu ({MAX_HEAL_ITERATIONS}) aşıldı!")
        return original_code, bug_report, len(bugs)

    print(f"\n🔄 SELF-HEALING TURU {iteration}/{MAX_HEAL_ITERATIONS}")
    print(f"   📋 Düzeltilecek bug sayısı: {len(bugs)}")

    # Bug listesini metin formatına çevir
    bugs_text = "\n".join([
        f"Bug #{b['id']}: {b['title']}\n  Detay: {b['description']}\n  Öncelik: {b['priority']}\n  Katman: {b['layer']}"
        for b in bugs
    ])

    trello.add_comment(
        card['id'],
        f"🔄 SELF-HEALING: Düzeltme turu {iteration} başlatıldı\n"
        f"📋 {len(bugs)} bug düzeltilecek"
    )
    trello.move_card(card['id'], list_id=list_ids.get("In Progress"))

    update_dashboard(
        agent=f"Self-Heal Dev (Tur {iteration})",
        task=f"{len(bugs)} bug düzeltiliyor",
        project=project_name,
        step=f"Heal {iteration}/{MAX_HEAL_ITERATIONS}"
    )

    # 1. FIX TASK — Developer'a bug'ları düzelttir
    fix_task = Task(
        description=f"""
        SEN BİR BUG FIX UZMANISIN.

        Aşağıdaki kodda QA ekibi tarafından {len(bugs)} bug tespit edildi.
        Tüm bug'ları düzelt ve TAM ÇALIŞIR yeni kodu ver.

        ==================
        MEVCUT KOD ({file_name}):
        ==================
        {original_code[:8000]}

        ==================
        BUG RAPORU:
        ==================
        {bugs_text}

        ==================
        TALİMATLAR:
        ==================
        1. Her bug'u tek tek düzelt
        2. Düzeltme sonrası kodun TAM ve ÇALIŞIR olmasını sağla
        3. Kodun başına düzeltme notları ekle (yorum olarak)
        4. Kodu ```{language}``` bloğu içinde ver
        5. Sadece düzeltilmiş KODU ver, açıklama yapma!
        """,
        agent=developer_agent,
        expected_output=f"Bug'ları düzeltilmiş tam {file_name} kodu"
    )

    # 2. RE-TEST TASK — QA tekrar test eder
    retest_task = Task(
        description=f"""
        SEN BİR QA TEST UZMANISIN.

        Developer, önceki turda bulunan {len(bugs)} bug'u düzeltti.
        Düzeltilmiş kodu TEKRAR test et.

        ÖNCEKİ BUG'LAR:
        {bugs_text}

        TALİMATLAR:
        1. Önceki bug'ların gerçekten düzelip düzelmediğini kontrol et
        2. Yeni bug var mı diye de bak
        3. Bug bulursan MUTLAKA şu formatta yaz:
           Bug 1: [Bug başlığı]
           Açıklama: ...
           Öncelik: Yüksek/Orta/Düşük

        4. Tüm bug'lar düzelmişse "TÜM TESTLER BAŞARILI" yaz!
        """,
        agent=qa_agent,
        expected_output="Re-test raporu",
        context=[fix_task]
    )

    # 3. ARCHITECT REVIEW TASK — Mimari ve Kalite Kontrolü
    architect_agent = Agent(
        role="Yazılım Mimari Denetçisi",
        goal="Düzeltilmiş kodun SOLID prensiplerine, güvenlik standartlarına ve temiz kod kurallarına uygunluğunu denetlemek",
        backstory="Sen, 15+ yıl deneyimli agresif bir yazılım mimarısın. Kod çalışsa bile kalitesiz kodu ASLA kabul etmezsin. SOLID, DRY, KISS prensiplerini ve güvenlik standartlarını harfiyen uygularsın.",
        verbose=False,
        llm=LLM(model=os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini"))
    )

    review_task = Task(
        description=f"""
        SEN BİR KOD KALİTE DENETÇİSİSİN (Architect Reviewer).

        Developer, {len(bugs)} bug'u düzeltti. Düzeltilmiş kodu KALİTE açısından incele.

        ==================
        KONTROL LİSTESİ:
        ==================
        1. SOLID Prensipleri: Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
        2. Güvenlik: SQL Injection, XSS, hardcoded credentials, input validation
        3. Temiz Kod: DRY (tekrar eden kod yok mu?), KISS, anlamlı isimlendirme
        4. Error Handling: Try-catch kullanımı, edge case'ler
        5. Performans: Gereksiz döngüler, N+1 sorguları

        ==================
        DEĞERLENDİRME:
        ==================
        - Eğer kod kabul edilebilir kalitedeyse: "KALİTE ONAYLI" yaz ve neden onayladığını açıkla
        - Eğer ciddi sorunlar varsa: Her sorunu listele ve "KALİTE REDDEDİLDİ" yaz

        NOT: Küçük stil tercihleri için reddetme! Sadece gerçek mimari, güvenlik veya sürdürülebilirlik sorunları için reddet.
        """,
        agent=architect_agent,
        expected_output="Mimari kalite değerlendirme raporu",
        context=[fix_task]
    )

    # Crew oluştur ve çalıştır (Developer → Architect → QA)
    heal_crew = Crew(
        agents=[developer_agent, architect_agent, qa_agent],
        tasks=[fix_task, review_task, retest_task],
        verbose=False,
        process=Process.sequential
    )

    print(f"   🔧 Developer bug'ları düzeltiyor...")
    for b in bugs:
        print(f"   🐛 Bug #{b['id']}: {b['title']} [{b['priority']}] ({b['layer']})")
    
    heal_result = heal_crew.kickoff()

    # Architect Review sonucunu logla
    review_output = str(review_task.output) if hasattr(review_task, 'output') else ""
    if "KALİTE ONAYLI" in review_output.upper() or "KALİTE ONAYLI" in review_output:
        print(f"   🏗️ Architect Reviewer: ✅ KALİTE ONAYLI")
    elif "KALİTE REDDEDİLDİ" in review_output.upper() or "KALİTE REDDEDİLDİ" in review_output:
        print(f"   🏗️ Architect Reviewer: ❌ KALİTE REDDEDİLDİ")
        # Reviewer notlarını logla
        for line in review_output.split('\n')[:10]:
            line = line.strip()
            if line:
                print(f"      │ {line}")
    else:
        print(f"   🏗️ Architect Reviewer: ℹ️ Değerlendirme tamamlandı")

    # Düzeltilmiş kodu çıkar
    fix_output = str(fix_task.output) if hasattr(fix_task, 'output') else ""
    fixed_code = extract_code(fix_output, language.lower()) if fix_output else original_code

    # ── Developer Notlarını Çıkar ve Logla ──
    if fix_output:
        # Code bloğundan önceki metni al (developer'ın açıklamaları)
        parts = re.split(r'```(?:python|javascript|jsx|html|css|typescript)?', fix_output, maxsplit=1)
        dev_notes = parts[0].strip() if len(parts) > 1 else ""
        if dev_notes and len(dev_notes) > 20:
            print(f"   📝 Developer Değişiklik Raporu:")
            for line in dev_notes.split('\n'):
                line = line.strip()
                if line:
                    print(f"      │ {line}")
        else:
            print(f"   📝 Developer düzeltmeyi tamamladı (detay notu yok)")
    
    # ── Kod Farkını (Diff) Hesapla ve Logla ──
    if fixed_code and original_code:
        orig_lines = original_code.strip().split('\n')
        fix_lines = fixed_code.strip().split('\n')
        added = len(fix_lines) - len(orig_lines)
        changed_count = sum(1 for a, b in zip(orig_lines, fix_lines) if a != b)
        print(f"   📊 Kod Farkı: {'+' if added >= 0 else ''}{added} satır | {changed_count} satır değiştirildi")

    # ── Yönetici Onay Kapısı (Approval Gate) ──
    if fixed_code and len(fixed_code) > 100 and project_dir:
        global PENDING_APPROVAL, APPROVAL_RESULT
        
        # Diff oluştur
        import difflib
        orig_lines_list = original_code.strip().splitlines(keepends=True)
        fix_lines_list = fixed_code.strip().splitlines(keepends=True)
        diff_text = ''.join(difflib.unified_diff(
            orig_lines_list, fix_lines_list,
            fromfile=f'{file_name} (orijinal)',
            tofile=f'{file_name} (düzeltilmiş)',
            lineterm=''
        ))
        
        relative_dir = os.path.relpath(project_dir, PROJECT_ROOT)
        
        PENDING_APPROVAL = {
            "file_name": file_name,
            "project": project_name,
            "relative_path": f"{relative_dir}/{file_name}",
            "iteration": iteration,
            "bug_count": len(bugs),
            "bugs": [{"id": b["id"], "title": b["title"], "priority": b["priority"], "layer": b["layer"]} for b in bugs],
            "diff": diff_text,
            "original_lines": len(orig_lines_list),
            "fixed_lines": len(fix_lines_list),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        APPROVAL_RESULT = None
        
        print(f"   ⏸️ YÖNETİCİ ONAYI BEKLENİYOR: {relative_dir}/{file_name}")
        print(f"   📋 Agent Manager arayüzünden Onayla veya Reddet butonuna basın")
        
        # Maksimum 5 dakika bekle (300 saniye)
        wait_start = time.time()
        timeout = 300
        while APPROVAL_RESULT is None and (time.time() - wait_start) < timeout:
            if STOP_ORCHESTRATOR:
                print(f"   🛑 Orchestrator durduruldu, onay iptal")
                PENDING_APPROVAL = None
                return original_code, "", len(bugs)
            time.sleep(2)
        
        if APPROVAL_RESULT == "approved":
            print(f"   ✅ Yönetici ONAYLADI — Kod yazılıyor...")
            output_path = os.path.join(project_dir, file_name)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            line_count = len(fixed_code.split('\n'))
            print(f"   ✅ Düzeltilmiş kod yazıldı: {relative_dir}/{file_name} ({line_count} satır)")
            trello.add_comment(card['id'], f"🔧 Düzeltilmiş kod yazıldı: {relative_dir}/{file_name} (Tur {iteration}) [YÖNETİCİ ONAYLI]")
        elif APPROVAL_RESULT == "rejected":
            print(f"   ❌ Yönetici REDDETTİ — Orijinal kod korunuyor")
            trello.add_comment(card['id'], f"❌ Self-Healing düzeltmesi yönetici tarafından reddedildi (Tur {iteration})")
            fixed_code = original_code  # Orijinal kodu koru
        else:
            # Timeout
            print(f"   ⏰ Onay zaman aşımına uğradı (5dk). Otomatik ONAYLANIYOR...")
            output_path = os.path.join(project_dir, file_name)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            line_count = len(fixed_code.split('\n'))
            print(f"   ✅ Düzeltilmiş kod yazıldı: {relative_dir}/{file_name} ({line_count} satır) [OTOMATİK ONAY]")
            trello.add_comment(card['id'], f"🔧 Düzeltilmiş kod yazıldı: {relative_dir}/{file_name} (Tur {iteration}) [OTOMATİK ONAY]")
        
        PENDING_APPROVAL = None
        APPROVAL_RESULT = None

    # Re-test raporunu analiz et
    retest_report = str(retest_task.output) if hasattr(retest_task, 'output') else ""

    trello.move_card(card['id'], list_id=list_ids.get("Testing"))

    # Başarı kontrolü
    success_keywords = ["BAŞARILI", "PASSED", "TÜM TESTLER", "NO BUG", "BUG YOK", "HATA YOK"]
    is_clean = any(kw in retest_report.upper() for kw in success_keywords)

    if is_clean:
        # Tüm bug'lar düzeldi!
        print(f"   ✅ Tüm bug'lar düzeltildi! (Tur {iteration})")
        trello.add_comment(
            card['id'],
            f"✅ SELF-HEALING BAŞARILI! (Tur {iteration})\n"
            f"📋 {len(bugs)} bug düzeltildi\n"
            f"📋 Re-test Raporu:\n\n{retest_report}"
        )
        return fixed_code, retest_report, 0

    # Hâlâ bug var mı?
    remaining_bugs = detect_bugs_in_report(retest_report)

    if remaining_bugs:
        print(f"   ⚠️ Hâlâ {len(remaining_bugs)} bug var, bir tur daha deneniyor...")
        trello.add_comment(
            card['id'],
            f"⚠️ Self-Healing Tur {iteration}: {len(remaining_bugs)} bug hâlâ mevcut\n"
            f"🔄 Bir sonraki tur başlatılıyor..."
        )

        # Recursive: Bir tur daha dene
        return self_heal_code(
            card=card,
            project_name=project_name,
            original_code=fixed_code,
            bug_report=retest_report,
            bugs=remaining_bugs,
            developer_agent=developer_agent,
            qa_agent=qa_agent,
            list_ids=list_ids,
            language=language,
            file_name=file_name,
            project_dir=project_dir,
            iteration=iteration + 1
        )
    else:
        # Bug pattern'i eşleşmedi ama "BAŞARILI" da yazmadı, geçiş yap
        print(f"   ℹ️ Bug pattern'i bulunamadı, devam ediliyor")
        return fixed_code, retest_report, 0


# ============================================================
# UNSPLASH GÖRSEL PALETLERİ (Proje Temasına Göre)
# ============================================================

def get_unsplash_images(project_name: str) -> dict:
    """Proje adına göre uygun Unsplash görselleri döner."""
    name = project_name.lower()
    
    # Yemek / Restoran
    if any(kw in name for kw in ['yemek', 'food', 'hamburger', 'pizza', 'restoran', 'sipariş', 'menü', 'cafe', 'lezzet']):
        return {
            "theme": "Yemek & Restoran",
            "colors": "orange-500, red-500 (yemek sektörü)",
            "hero": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1920&q=80",
            "items": [
                ("Hamburger", "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&q=80"),
                ("Pizza", "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&q=80"),
                ("Yemek", "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=500&q=80"),
                ("Salata", "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&q=80"),
                ("Tatlı", "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=500&q=80"),
                ("Restoran", "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&q=80"),
            ]
        }
    
    # Araç / Otomotiv
    if any(kw in name for kw in ['araç', 'araba', 'car', 'oto', 'vehicle', 'galeri', 'satım']):
        return {
            "theme": "Araç & Otomotiv",
            "colors": "blue-600, slate-700 (otomotiv sektörü)",
            "hero": "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1920&q=80",
            "items": [
                ("Sedan", "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=500&q=80"),
                ("SUV", "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=500&q=80"),
                ("Spor", "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=500&q=80"),
                ("Elektrikli", "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=500&q=80"),
                ("Klasik", "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=500&q=80"),
                ("Garaj", "https://images.unsplash.com/photo-1486006920555-c77dcf18193c?w=500&q=80"),
            ]
        }
    
    # Kitap / Eğitim / Kurs (E-Ticaret'ten ÖNCE kontrol edilmeli!)
    if any(kw in name for kw in ['kitap', 'book', 'kütüphane', 'library', 'eğitim', 'education', 'kurs', 'course', 'okuma', 'yayın']):
        return {
            "theme": "Kitap & Eğitim",
            "colors": "amber-600, emerald-500 (kitap/eğitim)",
            "hero": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1920&q=80",
            "items": [
                ("Kitap 1", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500&q=80"),
                ("Kitap 2", "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&q=80"),
                ("Kitap 3", "https://images.unsplash.com/photo-1524578271613-d550eacf6090?w=500&q=80"),
                ("Kütüphane", "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=500&q=80"),
                ("Okuma", "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=500&q=80"),
                ("Eğitim", "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500&q=80"),
            ]
        }
    
    # E-Ticaret / Mağaza
    if any(kw in name for kw in ['shop', 'store', 'mağaza', 'ticaret', 'market', 'satış', 'toy', 'oyuncak']):
        return {
            "theme": "E-Ticaret & Mağaza",
            "colors": "violet-500, pink-500 (e-ticaret)",
            "hero": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1920&q=80",
            "items": [
                ("Ürün 1", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"),
                ("Ürün 2", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"),
                ("Ürün 3", "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500&q=80"),
                ("Ürün 4", "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=500&q=80"),
                ("Ürün 5", "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=500&q=80"),
                ("Mağaza", "https://images.unsplash.com/photo-1441984904996-e0b6ba687e04?w=500&q=80"),
            ]
        }
    
    # Sağlık / Wellness
    if any(kw in name for kw in ['sağlık', 'health', 'wellness', 'fitness', 'gym', 'spor', 'diyet']):
        return {
            "theme": "Sağlık & Wellness",
            "colors": "teal-500, cyan-500 (sağlık sektörü)",
            "hero": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=1920&q=80",
            "items": [
                ("Fitness", "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=500&q=80"),
                ("Yoga", "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=500&q=80"),
                ("Beslenme", "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=500&q=80"),
                ("Koşu", "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=500&q=80"),
                ("Meditasyon", "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=500&q=80"),
                ("Doğa", "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500&q=80"),
            ]
        }
    
    # Varsayılan: Teknoloji / SaaS
    return {
        "theme": "Teknoloji & SaaS",
        "colors": "indigo-500, violet-500 (teknoloji)",
        "hero": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80",
        "items": [
            ("Dashboard", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&q=80"),
            ("Ekip", "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=500&q=80"),
            ("Kod", "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=500&q=80"),
            ("Analitik", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&q=80"),
            ("Bulut", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=500&q=80"),
            ("Güvenlik", "https://images.unsplash.com/photo-1563986768609-322da13575f2?w=500&q=80"),
        ]
    }


# ============================================================
# V3 PROJE İŞLEME (STANDART AKIŞ)
# ============================================================

def process_standard_project(card: Dict, task_config: Dict, board_id: str, list_ids: Dict[str, str], rules_text: str = "") -> bool:
    """
    Standart proje işleme (CLI, Backend-only gibi)
    Backend projeleri için scaffold_backend_project kullanır.
    """
    project_name = task_config['project_name']
    project_type = task_config.get('project_type', 'cli')
    programming_language = task_config.get('programming_language', 'Python')
    file_name = task_config.get('file_name', 'main.py')
    requirements_str = "\n".join([f"- {req}" for req in task_config.get('requirements', [])])
    framework = task_config.get('backend', {}).get('framework', 'FastAPI') if project_type == 'backend' else ''

    # Agent'ları oluştur
    orchestrator = create_orchestrator_agent(rules_text)
    architect = create_solution_architect_agent(rules_text)
    developer = create_backend_developer_agent(programming_language, rules_text)
    qa = create_qa_agent(rules_text)

    # Task'lar
    architect_task = Task(
        description=f"Proje: {project_name}\nGereksinimler:\n{requirements_str}\n\nTeknik mimariyi tasarla.",
        agent=architect,
        expected_output="Detaylı teknik mimari dokümanı"
    )

    orchestrator_task = Task(
        description=f"{project_name} projesi icin detayli plan olustur.\nDil: {programming_language}\nDosya: {file_name}\n\nGereksinimler:\n{requirements_str}",
        agent=orchestrator,
        expected_output="Detayli proje plani",
        context=[architect_task]
    )

    dev_task = Task(
        description=f"{project_name} projesini kodla.\n\nGereksinimler:\n{requirements_str}\n\nDosya: {file_name}\nDil: {programming_language}\n\nTam calisir kod yaz!",
        agent=developer,
        expected_output=f"Tam calisir {file_name} kodu",
        context=[orchestrator_task]
    )

    qa_task = Task(
        description=f"{project_name} projesi icin test senaryolari olustur.\n\nBug bulursan MUTLAKA su formatta yaz:\nBug 1: [Bug basligi]\nAciklama: ...\nOncelik: Yuksek/Orta/Dusuk",
        agent=qa,
        expected_output="Test raporu ve bug listesi",
        context=[orchestrator_task, dev_task]
    )

    project_crew = Crew(
        agents=[architect, orchestrator, developer, qa],
        tasks=[architect_task, orchestrator_task, dev_task, qa_task],
        verbose=False,
        process=Process.sequential
    )

    print("\n🚀 AI Ekibi calismaya basliyor...")
    print(f"   🧑‍💻 Ekip Kadrosu:")
    for ag in [architect, orchestrator, developer, qa]:
        print(f"      👤 Agent: {ag.role}")
    update_dashboard(agent="CrewAI", task="Workflow Başlatıldı", project=project_name)
    result = project_crew.kickoff()

    # Proje dizini oluştur
    project_dir = get_project_dir(project_name)
    relative_dir = os.path.relpath(project_dir, PROJECT_ROOT)

    # Backend projeler için scaffold kullan
    if project_type == 'backend':
        code_dir = scaffold_backend_project(
            project_dir=project_dir,
            project_name=project_name,
            framework=framework or 'FastAPI',
            language=programming_language
        )
    else:
        # CLI projeleri - direkt dizine yaz
        code_dir = project_dir

    # Kodu kaydet
    kod = str(dev_task.output) if hasattr(dev_task, 'output') else ""
    if kod and len(kod) > 100:
        kod = extract_code(kod, programming_language.lower())
        output_path = os.path.join(code_dir, file_name)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(kod)

        line_count = len(kod.split('\n'))
        code_relative = os.path.relpath(output_path, PROJECT_ROOT)
        print(f"\n✅ KOD YAZILDI: {code_relative} ({line_count} satır)")
        trello.add_comment(card['id'], f"✅ KOD YAZILDI\n📁 Dizin: {code_relative}\n📊 Satır: {line_count}\n🔧 Dil: {programming_language}")

    # Code Review
    trello.move_card(card['id'], list_id=list_ids.get("Code Review"))

    # QA Test + Self-Healing Loop
    trello.move_card(card['id'], list_id=list_ids.get("Testing"))
    test_raporu = str(qa_task.output) if hasattr(qa_task, 'output') else ""
    heal_summary = ""

    if test_raporu:
        trello.add_comment(card['id'], f"📋 TEST RAPORU:\n\n{test_raporu}")

        # Bug'ları tespit et
        detected_bugs = detect_bugs_in_report(test_raporu)

        if detected_bugs:
            trello.add_comment(card['id'], f"🐛 {len(detected_bugs)} bug tespit edildi! Self-Healing başlatılıyor...")

            # Self-Healing döngüsü
            fixed_code, final_report, remaining_bug_count = self_heal_code(
                card=card,
                project_name=project_name,
                original_code=kod,
                bug_report=test_raporu,
                bugs=detected_bugs,
                developer_agent=developer,
                qa_agent=qa,
                list_ids=list_ids,
                language=programming_language.lower(),
                file_name=file_name,
                project_dir=code_dir
            )

            if remaining_bug_count > 0:
                # Düzelmeyen bug'lar için Trello kartları oluştur
                handle_bugs(final_report, list_ids, project_name, card['id'])
                heal_summary = f"\n🔄 Self-Healing: {len(detected_bugs)} bug bulundu → {remaining_bug_count} düzelmedi (manuel müdahale gerekli)"
            else:
                heal_summary = f"\n🔄 Self-Healing: {len(detected_bugs)} bug bulundu → ✅ Tümü otomatik düzeltildi!"
        else:
            trello.add_comment(card['id'], "✅ Bug bulunamadı!")
            heal_summary = "\n✅ İlk turda temiz geçti!"

    # Done
    trello.move_card(card['id'], list_id=list_ids.get("Done"))
    print(f"\n✅✅✅ İŞ TAMAMLANDI: {project_name}")
    print(f"   📂 Proje Dizini: {relative_dir}/")
    print(f"   🔄 Backlog → In Progress → Code Review → Testing → Done")
    trello.add_comment(
        card['id'],
        f"✅ İŞ TAMAMLANDI!\n\n"
        f"📂 Proje Dizini: {relative_dir}/\n"
        f"🔄 Backlog → In Progress → Code Review → Testing → Done"
        f"{heal_summary}"
    )
    update_dashboard(agent="System", task="Tamamlandı", project=project_name, step="Done")

    return True


def process_fullstack_project(card: Dict, task_config: Dict, board_id: str, list_ids: Dict[str, str], rules_text: str = "", workflow_content: str = "") -> bool:
    """
    Fullstack proje işleme (Backend + Frontend)
    Workflow talimatları varsa developer agent'lara enjekte edilir.
    """
    project_name = task_config['project_name']
    backend_config = task_config.get('backend', {})
    frontend_config = task_config.get('frontend', {})

    # Rules'u tipine göre yükle
    backend_rules = rules_text  # Backend rules zaten yüklü
    frontend_rules = rules_text  # Frontend rules da yüklü

    # Agent'ları oluştur
    orchestrator = create_orchestrator_agent(rules_text)
    architect = create_solution_architect_agent(rules_text)
    backend_dev = create_backend_developer_agent(
        backend_config.get('programming_language', 'Python'), backend_rules
    )
    frontend_dev = create_frontend_developer_agent(
        frontend_config.get('framework', 'React'), frontend_rules
    )
    qa = create_qa_agent(rules_text)

    # Task'lar
    backend_reqs = "\n".join([f"- {r}" for r in backend_config.get('requirements', [])])
    frontend_reqs = "\n".join([f"- {r}" for r in frontend_config.get('requirements', [])])

    architect_task = Task(
        description=f"{project_name} projesi için teknik mimariyi tasarla.\n\nBackend: {backend_reqs}\nFrontend: {frontend_reqs}",
        agent=architect,
        expected_output="Detaylı teknik mimari dokümanı"
    )

    orchestrator_task = Task(
        description=f"{project_name} fullstack projesi için detaylı plan oluştur.\nBackend ve Frontend ayrımı yaparak planla.",
        agent=orchestrator,
        expected_output="Detaylı fullstack proje planı",
        context=[architect_task]
    )

    # Workflow talimatları varsa backend'e ekle
    backend_workflow_note = ""
    if workflow_content:
        backend_workflow_note = f"\n\nWORKFLOW TALİMATLARI:\n{workflow_content}"

    backend_task = Task(
        description=f"""{project_name} BACKEND kodunu yaz.
Framework: {backend_config.get('framework', 'FastAPI')}
Dosya: {backend_config.get('file_name', 'backend_api.py')}
Database: SQLite (PostgreSQL DEĞİL — lokal geliştirme için)

ÖNEMLİ BACKEND KURALLARI:
- SQLite kullan: DATABASE_URL = "sqlite:///./app.db"
- CORS middleware ekle (http://localhost:5173, http://localhost:3000)
- Seed data ekle (@app.on_event("startup") ile örnek veriler)
- FastAPI + SQLAlchemy + Pydantic kullan
- Dosya sonunda: if __name__ == "__main__": uvicorn.run(app, host="0.0.0.0", port=8000)

Gereksinimler:
{backend_reqs}{backend_workflow_note}""",
        agent=backend_dev,
        expected_output=f"Tam çalışır backend kodu (SQLite, CORS, seed data dahil)",
        context=[orchestrator_task]
    )

    # Frontend task — Premium UI talimatları + workflow
    frontend_workflow_note = ""
    if workflow_content:
        frontend_workflow_note = f"\n\nWORKFLOW TALİMATLARI:\n{workflow_content}"

    # Proje temasına göre dinamik görsel paleti
    img_palette = get_unsplash_images(project_name)
    img_list_text = "\n".join([f"- {name}: {url}" for name, url in img_palette["items"]])
    
    print(f"   🎨 Tema: {img_palette['theme']} | Renkler: {img_palette['colors']}")

    frontend_task = Task(
        description=f"""{project_name} FRONTEND kodunu yaz.
Framework: {frontend_config.get('framework', 'React')}
Dosya: {frontend_config.get('file_name', 'App.jsx')}
Tema: {img_palette['theme']}

==================================================
PREMİUM TASARIM YÖNERGESİ (ZORUNLU)
==================================================

⚠️ UYARI: 100 satırdan kısa, görsel içermeyen veya sadece kart listeleyen
basit kodlar REDDEDİLECEKTİR. Portfolyo kalitesinde çıktı beklenmektedir.

1. '.agent/skills/frontend-design-pro' kapsamında belirtilen TÜM kurallara uy.
2. Aşağıdaki SAYFA YAPISINI ZORUNLU olarak uygula (hepsini tek dosyada yaz):

   a) NAVBAR: sticky top-0, backdrop-blur-lg, bg-black/30, logo + linkler + CTA buton
   b) HERO SECTION: Tam ekran, arka plan görseli (aşağıdan URL al), üzerine gradient overlay,
      büyük başlık (text-5xl md:text-7xl font-bold), alt metin, CTA buton, istatistik sayaçları
   c) FEATURES/AVANTAJLAR: 3-4 glassmorphism kart (bg-white/5 backdrop-blur-md border border-white/10)
      her kartta emoji ikon + başlık + açıklama, hover efektleri
   d) ÜRÜN KARTLARI: Grid (grid-cols-1 sm:grid-cols-2 lg:grid-cols-3), her kartta
      GERÇEK <img> görseli (aşağıdaki URL'lerden) + ürün adı + fiyat + sipariş butonu
   e) FOOTER: Linkler + sosyal medya + telif hakkı

3. Arka plan: min-h-screen bg-gradient-to-b from-slate-950 via-gray-900 to-slate-950
4. Mikro animasyonlar: hover:-translate-y-2, hover:scale-105, transition-all duration-300
5. Google Fonts: Poppins (CSS dosyasında @import ile)

==================================================
ZORUNLU GÖRSELLER (MUTLAKA KULLAN!)
==================================================
Hero arka plan (style={{{{ backgroundImage: 'url(...)' }}}} veya bg-[url(...)]):
{img_palette['hero']}

Ürün kartları için (<img src="..." className="w-full h-48 object-cover rounded-t-2xl" />):
{img_list_text}

Renk Paleti: {img_palette['colors']}

==================================================
TEKNİK KURALLAR
==================================================
- import {{ useEffect, useState }} from 'react'
- import './App.css'
- Harici component import ETME, tam çalışır tek bir dosya yaz.
- fetch('/api/v1/...') kullan (tam URL yazma).
- Minimum 150 satır kod üret (Navbar + Hero + Features + Products + Footer).
- Ayrı bir ```css``` bloğunda App.css ver:
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
  @tailwind base; @tailwind components; @tailwind utilities;
  body {{ font-family: 'Poppins', sans-serif; }}
  Scrollbar ve @keyframes fadeInUp da ekle.

Gereksinimler:
{frontend_reqs}{frontend_workflow_note}""",
        agent=frontend_dev,
        expected_output=f"Minimum 150 satır, Navbar+Hero+Features+ProductCards+Footer içeren premium React kodu + App.css",
        context=[orchestrator_task, backend_task]
    )

    qa_task = Task(
        description=f"{project_name} fullstack projesi için kapsamlı test raporu oluştur.\n\nBug bulursan MUTLAKA formatta yaz:\nBug 1: [Bug başlığı]\nAçıklama: ...\nKatman: Backend/Frontend\nÖncelik: Yüksek/Orta/Düşük",
        agent=qa,
        expected_output="Kapsamlı test raporu ve bug listesi",
        context=[orchestrator_task, backend_task, frontend_task]
    )

    fullstack_crew = Crew(
        agents=[architect, orchestrator, backend_dev, frontend_dev, qa],
        tasks=[architect_task, orchestrator_task, backend_task, frontend_task, qa_task],
        verbose=False,
        process=Process.sequential
    )

    print("\n🚀 Fullstack ekibi çalışmaya başlıyor...")
    print(f"   🧑‍💻 Ekip Kadrosu:")
    for ag in [architect, orchestrator, backend_dev, frontend_dev, qa]:
        print(f"      👤 Agent: {ag.role}")
    update_dashboard(agent="CrewAI", task="Fullstack Workflow", project=project_name)
    result = fullstack_crew.kickoff()

    # Kodları kaydet — Scaffold ile gerçek proje yapısı oluştur
    project_dir = get_project_dir(project_name)
    relative_dir = os.path.relpath(project_dir, PROJECT_ROOT)

    # Fullstack scaffold: backend/ + frontend/ (Vite + React + Tailwind)
    scaffold = scaffold_fullstack_project(
        project_dir=project_dir,
        project_name=project_name,
        backend_framework=backend_config.get('framework', 'FastAPI'),
        backend_language=backend_config.get('programming_language', 'Python')
    )

    backend_dir = scaffold["backend_dir"]
    frontend_dir = scaffold["frontend_dir"]

    # Backend kodu → backend/backend_api.py
    backend_kod = str(backend_task.output) if hasattr(backend_task, 'output') else ""
    if backend_kod and len(backend_kod) > 100:
        backend_kod = extract_code(backend_kod, backend_config.get('programming_language', 'python').lower())
        backend_file = backend_config.get('file_name', 'backend_api.py')
        backend_path = os.path.join(backend_dir, backend_file)
        with open(backend_path, "w", encoding="utf-8") as f:
            f.write(backend_kod)
        line_count = len(backend_kod.split('\n'))
        print(f"✅ YAZILDI: {relative_dir}/backend/{backend_file} ({line_count} satır)")
        trello.add_comment(card['id'], f"✅ Backend kodu yazıldı: backend/{backend_file} ({line_count} satır)")

    # Frontend kodu → frontend/src/App.jsx
    frontend_kod = str(frontend_task.output) if hasattr(frontend_task, 'output') else ""
    if frontend_kod and len(frontend_kod) > 100:
        frontend_kod = extract_code(frontend_kod, 'javascript')
        frontend_file = frontend_config.get('file_name', 'App.jsx')
        # App.jsx her zaman src/ altına gider
        frontend_path = os.path.join(frontend_dir, "src", frontend_file)
        os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
        with open(frontend_path, "w", encoding="utf-8") as f:
            f.write(frontend_kod)
        line_count = len(frontend_kod.split('\n'))
        print(f"✅ YAZILDI: {relative_dir}/frontend/src/{frontend_file} ({line_count} satır)")
        trello.add_comment(card['id'], f"✅ Frontend kodu yazıldı: frontend/src/{frontend_file} ({line_count} satır)")

    trello.add_comment(
        card['id'],
        f"📁 PROJE YAPISI OLUŞTURULDU:\n\n"
        f"```\n"
        f"{project_name}/\n"
        f"├── backend/\n"
        f"│   ├── {backend_config.get('file_name', 'backend_api.py')}\n"
        f"│   ├── requirements.txt\n"
        f"│   └── README.md\n"
        f"├── frontend/\n"
        f"│   ├── src/\n"
        f"│   │   └── {frontend_config.get('file_name', 'App.jsx')}\n"
        f"│   ├── package.json\n"
        f"│   ├── vite.config.js\n"
        f"│   └── README.md\n"
        f"└── README.md\n"
        f"```\n\n"
        f"🚀 Başlatmak için:\n"
        f"Backend: `cd backend && pip install -r requirements.txt && python {backend_config.get('file_name', 'backend_api.py')}`\n"
        f"Frontend: `cd frontend && npm run dev`"
    )

    # Kartı geçir
    trello.move_card(card['id'], list_id=list_ids.get("Code Review"))
    trello.move_card(card['id'], list_id=list_ids.get("Testing"))

    test_raporu = str(qa_task.output) if hasattr(qa_task, 'output') else ""
    heal_summary = ""

    if test_raporu:
        trello.add_comment(card['id'], f"📋 TEST RAPORU:\n\n{test_raporu}")

        # Bug'ları tespit et
        detected_bugs = detect_bugs_in_report(test_raporu)

        if detected_bugs:
            trello.add_comment(card['id'], f"🐛 {len(detected_bugs)} bug tespit edildi! Self-Healing başlatılıyor...")

            # Backend bug'ları
            backend_bugs = [b for b in detected_bugs if b["layer"] in ("Backend", "Unknown")]
            frontend_bugs = [b for b in detected_bugs if b["layer"] == "Frontend"]

            total_remaining = 0

            # Backend Self-Heal
            if backend_bugs:
                backend_code = str(backend_task.output) if hasattr(backend_task, 'output') else ""
                backend_code = extract_code(backend_code, backend_config.get('programming_language', 'python').lower())

                _, _, remaining = self_heal_code(
                    card=card,
                    project_name=f"{project_name} (Backend)",
                    original_code=backend_code,
                    bug_report=test_raporu,
                    bugs=backend_bugs,
                    developer_agent=backend_dev,
                    qa_agent=qa,
                    list_ids=list_ids,
                    language=backend_config.get('programming_language', 'python').lower(),
                    file_name=backend_config.get('file_name', 'backend_api.py'),
                    project_dir=backend_dir
                )
                total_remaining += remaining

            # Frontend Self-Heal
            if frontend_bugs:
                frontend_code = str(frontend_task.output) if hasattr(frontend_task, 'output') else ""
                frontend_code = extract_code(frontend_code, 'javascript')

                _, _, remaining = self_heal_code(
                    card=card,
                    project_name=f"{project_name} (Frontend)",
                    original_code=frontend_code,
                    bug_report=test_raporu,
                    bugs=frontend_bugs,
                    developer_agent=frontend_dev,
                    qa_agent=qa,
                    list_ids=list_ids,
                    language="javascript",
                    file_name=frontend_config.get('file_name', 'App.jsx'),
                    project_dir=os.path.join(frontend_dir, 'src')
                )
                total_remaining += remaining

            if total_remaining > 0:
                handle_bugs(test_raporu, list_ids, project_name, card['id'])
                heal_summary = f"\n🔄 Self-Healing: {len(detected_bugs)} bug → {total_remaining} düzelmedi"
            else:
                heal_summary = f"\n🔄 Self-Healing: {len(detected_bugs)} bug → ✅ Tümü otomatik düzeltildi!"
        else:
            heal_summary = "\n✅ İlk turda temiz geçti!"

    trello.move_card(card['id'], list_id=list_ids.get("Done"))
    print(f"\n✅✅✅ FULLSTACK PROJE TAMAMLANDI: {project_name}")
    print(f"   📂 Proje Dizini: {relative_dir}/")
    print(f"   📄 Backend: backend/{backend_config.get('file_name', 'backend_api.py')}")
    print(f"   📄 Frontend: frontend/src/{frontend_config.get('file_name', 'App.jsx')}")
    print(f"   🔄 Backlog → In Progress → Code Review → Testing → Done")
    trello.add_comment(
        card['id'],
        f"✅ FULLSTACK PROJE TAMAMLANDI!\n\n"
        f"📂 Proje Dizini: {relative_dir}/\n"
        f"📄 Backend: backend/{backend_config.get('file_name', 'backend_api.py')}\n"
        f"📄 Frontend: frontend/src/{frontend_config.get('file_name', 'App.jsx')}"
        f"{heal_summary}"
    )
    update_dashboard(agent="System", task="Tamamlandı", project=project_name, step="Done")

    return True


# ============================================================
# V3 PROJE ANALİZİ (PROJECT ANALYZER)
# ============================================================

def process_analyzer_project(card: Dict, task_config: Dict, board_id: str, list_ids: Dict[str, str], rules_text: str = "", workflow_content: str = "") -> bool:
    """
    Mevcut bir projeyi analiz edip iyileştirme raporu üreten akış.
    .agent/workflows/project-analyzer.md protokolüne uyar.
    """
    project_name = task_config['project_name']
    requirements_str = "\n".join([f"- {req}" for req in task_config.get('requirements', [])])

    print(f"\n🔍 PROJE ANALİZİ BAŞLATILIYOR: {project_name}")

    # Workflow'u yükle (eğer daha önce yüklenmemişse)
    if not workflow_content:
        wf = load_workflow('project-analyzer')
        if wf:
            workflow_content = wf
            print(f"   📋 project-analyzer workflow yüklendi")

    # Hedef proje dizinini bul
    project_dir = get_project_dir(project_name)
    project_files_summary = ""

    if os.path.exists(project_dir):
        print(f"   📂 Proje dizini bulundu: {project_dir}")
        # Proje dosyalarını oku (max 15 dosya, max 500 satır/dosya)
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html', '.json', '.md', '.yaml', '.yml'}
        file_snippets = []
        file_count = 0

        for root, dirs, files in os.walk(project_dir):
            # node_modules, .venv, __pycache__ gibi dizinleri atla
            dirs[:] = [d for d in dirs if d not in ('node_modules', '.venv', '__pycache__', '.git', 'dist', 'build')]
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in code_extensions and file_count < 15:
                    fpath = os.path.join(root, fname)
                    rel_path = os.path.relpath(fpath, project_dir)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        lines = content.split('\n')
                        truncated = '\n'.join(lines[:500])
                        if len(lines) > 500:
                            truncated += f"\n... ({len(lines) - 500} satır daha)"
                        file_snippets.append(f"\n--- {rel_path} ({len(lines)} satır) ---\n{truncated}")
                        file_count += 1
                    except Exception:
                        pass

        if file_snippets:
            project_files_summary = "\n".join(file_snippets)
            print(f"   📄 {file_count} dosya okundu")
        else:
            project_files_summary = "(Proje dizininde okunabilir dosya bulunamadı)"
    else:
        print(f"   ⚠️  Proje dizini bulunamadı: {project_dir}")
        project_files_summary = f"(Proje dizini henüz mevcut değil: {project_dir})"

    # Skill'leri yükle
    architect_skill = load_skill('solution-architect')
    security_skill = load_skill('security-specialist')
    qa_skill = load_skill('qa-engineer')

    # Analyzer Agent oluştur
    analyzer_agent = Agent(
        role='Kıdemli Proje Analisti & Kod Denetçisi',
        goal='Mevcut projeyi uçtan uca inceleyip yapılandırılmış iyileştirme raporu üretmek',
        backstory=f"""
        Sen 15+ yıl deneyimli bir yazılım danışmanısın. Projeleri mimari, güvenlik,
        performans ve kod kalitesi açısından analiz edersin.

        ========================
        PROJECT ANALYZER WORKFLOW:
        ========================
        {workflow_content}

        ========================
        SOLUTION ARCHITECT BİLGİSİ:
        ========================
        {architect_skill[:2000]}

        ========================
        GÜVENLİK UZMANI BİLGİSİ:
        ========================
        {security_skill[:2000]}

        ========================
        QA MÜHENDİSİ BİLGİSİ:
        ========================
        {qa_skill[:2000]}

        ========================
        PROJE KURALLARI:
        ========================
        {rules_text}
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # Analiz Task'ı
    analysis_task = Task(
        description=f"""
        Aşağıdaki projeyi UÇTAN UCA analiz et ve yapılandırılmış bir rapor oluştur.

        PROJE ADI: {project_name}
        KULLANICI İSTEĞİ: {card['name']}
        {card.get('desc', '')}

        EK GEREKSİNİMLER:
        {requirements_str}

        ========================
        PROJE DOSYALARI:
        ========================
        {project_files_summary[:12000]}

        ========================
        RAPOR FORMATI (ZORUNLU):
        ========================
        Raporunu MUTLAKA aşağıdaki başlıklarla Markdown formatında yaz:

        ### 🎯 Proje Özeti
        - Projenin amacı, kullanılan teknolojiler, dosya yapısı

        ### 🔍 Kritik Bulgular
        - Kod kalitesi sorunları
        - Güvenlik açıkları (OWASP Top 10 kontrolü)
        - Performans darboğazları
        - Mimari sorunlar

        ### 🚀 Geliştirme Önerileri (Kısa, Orta ve Uzun Vade)
        **Kısa Vade (1-2 hafta):**
        - Teknik iyileştirme önerileri

        **Orta Vade (1-3 ay):**
        - UX ve özellik önerileri

        **Uzun Vade (3-6 ay):**
        - Sürdürülebilirlik önerileri (test, CI/CD, dokümantasyon)

        ### 💡 Brainstorming: "Peki ya şöyle olsaydı?"
        - En az 3 yaratıcı / yenilikçi fikir

        Her önerinin yanına [Öncelik: Yüksek/Orta/Düşük] ve [Etki: Büyük/Orta/Küçük] etiketleri ekle.
        """,
        agent=analyzer_agent,
        expected_output="Yapılandırılmış Markdown proje analiz raporu"
    )

    # Crew oluştur
    analyzer_crew = Crew(
        agents=[analyzer_agent],
        tasks=[analysis_task],
        verbose=False,
        process=Process.sequential
    )

    print(f"\n🚀 Analiz ekibi çalışmaya başlıyor...")
    print(f"   🧑‍💻 Ekip Kadrosu:")
    print(f"      👤 Agent: {analyzer_agent.role}")
    update_dashboard(agent="Proje Analisti", task="Proje Analizi", project=project_name, step="3/5")

    trello.move_card(card['id'], list_id=list_ids.get("In Progress"))
    result = analyzer_crew.kickoff()

    # Raporu al
    report = str(result) if result else ""

    if report and len(report) > 100:
        # Raporu diske kaydet
        report_dir = get_project_dir(project_name)
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, "project_analyzer_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 📊 Proje Analiz Raporu: {project_name}\n\n")
            f.write(f"_Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n")
            f.write(report)

        relative_path = os.path.relpath(report_path, PROJECT_ROOT)
        print(f"\n✅ ANALİZ RAPORU YAZILDI: {relative_path}")

        # Trello'ya raporu yorum olarak ekle (max 16K karakter)
        trello_report = report[:16000]
        if len(report) > 16000:
            trello_report += "\n\n... (Tam rapor proje dizininde mevcut)"
        trello.add_comment(card['id'], f"📊 PROJE ANALİZ RAPORU:\n\n{trello_report}")
    else:
        print(f"\n⚠️  Analiz raporu boş veya çok kısa!")
        trello.add_comment(card['id'], "⚠️ Analiz raporu oluşturulamadı.")

    # Kartı Done'a taşı
    trello.move_card(card['id'], list_id=list_ids.get("Code Review"))
    trello.move_card(card['id'], list_id=list_ids.get("Done"))

    print(f"\n✅✅✅ PROJE ANALİZİ TAMAMLANDI: {project_name}")
    print(f"   📂 Rapor: {os.path.relpath(report_path, PROJECT_ROOT) if report else 'N/A'}")
    print(f"   🔄 Backlog → In Progress → Code Review → Done")

    trello.add_comment(
        card['id'],
        f"✅ PROJE ANALİZİ TAMAMLANDI!\n\n"
        f"📊 Rapor dosyası: {os.path.relpath(report_path, PROJECT_ROOT) if report else 'N/A'}\n"
        f"📋 Workflow: project-analyzer"
    )
    update_dashboard(agent="System", task="Analiz Tamamlandı", project=project_name, step="Done")

    return True


# ============================================================
# V3 ANA KART İŞLEME
# ============================================================

def process_backlog_card_v3(card: Dict, board_id: str, list_ids: Dict[str, str]) -> bool:
    """
    V3: .agent yapısı destekli akıllı proje yönlendirme

    Akış:
    1. Rules yüklenir
    2. Workflow eşleşmesi kontrol edilir
    3. Analist kartı analiz eder
    4. Proje tipine göre uygun agent'lar seçilir
    5. Skills ve rules agent'lara enjekte edilir
    6. Proje işlenir
    """
    print("\n" + "=" * 80)
    print(f"📋 YENİ İŞ BULUNDU (V3): {card['name']}")
    print("=" * 80)

    # ============================================================
    # 1. .AGENT YAPISINI YÜKLE
    # ============================================================

    print("\n📁 .agent yapısı yükleniyor...")

    # Rules yükle
    all_rules = load_all_rules()
    print(f"   📜 {len(all_rules)} rule yüklendi")

    # Mevcut skill'leri listele
    available_skills = list_available_skills()
    print(f"   🧠 {len(available_skills)} skill mevcut: {', '.join(available_skills)}")

    # Workflow eşleşmesi kontrol et
    workflow_content = match_workflow(card['name'], card.get('desc', ''))
    if workflow_content:
        print(f"   🔗 Workflow eşleşmesi bulundu!")
        trello.add_comment(card['id'], f"🔗 Workflow eşleşmesi tespit edildi. Otomatik iş akışı uygulanıyor.")

    # ============================================================
    # 2. WHATSAPP ONAY (V2'den devam)
    # ============================================================

    try:
        from whatsapp_approval_agent import request_approval_via_whatsapp

        print("\n📱 WhatsApp onay süreci başlatılıyor...")
        trello.add_comment(card['id'], "📱 WhatsApp üzerinden onay bekleniyor...")
        update_dashboard(agent="WhatsApp Approval", task="Onay Bekleniyor", project=card['name'], step="0/5")

        approved, task_summary = request_approval_via_whatsapp(card, timeout=300)

        if not approved:
            print("\n❌ Task onaylanmadı!")
            trello.add_comment(card['id'], "❌ Task kullanıcı tarafından onaylanmadı.")
            trello.move_card(card['id'], list_id=list_ids.get("Backlog"))
            return False

        print("\n✅ Task onaylandı!")
    except ImportError:
        print("\n⚠️ WhatsApp modülü bulunamadı, onay adımı atlanıyor...")
        task_summary = {}

    # ============================================================
    # 3. ANALİST - KART ANALİZİ
    # ============================================================

    trello.move_card(card['id'], list_id=list_ids.get("In Progress"))
    trello.add_comment(card['id'], "🤖 Orchestrator V3 işe başladı. Analist analiz yapıyor...")
    update_dashboard(agent="Analist", task="Kart Analiz Ediliyor", project=card['name'], step="1/5")

    # Genel rules'u analist'e ver
    general_rules = "\n".join(all_rules.values()) if all_rules else ""
    analyst = create_analyst_agent(general_rules)

    analyst_task = Task(
        description=f"""
        Asagidaki Trello kartini analiz et:

        KART BASLIGI: {card['name']}
        KART ACIKLAMASI: {card.get('desc', '')}

        {"WORKFLOW TALİMATLARI:" + workflow_content if workflow_content else ""}

        Cikti olarak JSON formatinda proje analizi ver.
        project_type: backend, frontend, fullstack, cli, mobile
        """,
        agent=analyst,
        expected_output="JSON formatinda proje analizi"
    )

    analyst_crew = Crew(
        agents=[analyst],
        tasks=[analyst_task],
        verbose=False,
        process=Process.sequential
    )

    analyst_result = analyst_crew.kickoff()
    analyst_output = str(analyst_result)
    trello.add_comment(card['id'], f"📊 ANALIST RAPORU (V3):\n\n{analyst_output}")

    # Parse et
    task_config = parse_analyst_output(analyst_output)

    if not task_config or not task_config.get("project_name"):
        print("❌ Analist çıktısı parse edilemedi!")
        trello.add_comment(card['id'], "❌ Analist çıktısı parse edilemedi. Manuel müdahale gerekli.")
        return False

    project_type = task_config.get('project_type', 'cli')

    # ============================================================
    # 4. PROJE TİPİNE GÖRE RULes SEÇ VE İŞLE
    # ============================================================

    print(f"\n✅ Proje Tipi: {project_type.upper()}")
    print(f"   Proje: {task_config['project_name']}")

    # Proje tipine göre rules seç
    rules_text = load_rules_for_type(project_type, all_rules)

    update_dashboard(
        agent="Orchestrator V3",
        task=f"Proje Yönlendiriliyor ({project_type})",
        project=task_config['project_name'],
        step="2/5",
        log=f"Proje tipi: {project_type}. Skills ve rules enjekte edildi."
    )

    # Fullstack / frontend projelerde glass-landing-page workflow'unu HER ZAMAN yükle
    if project_type in ('fullstack', 'frontend') and not workflow_content:
        glass_wf_path = os.path.join(AGENT_DIR, 'workflows', 'glass-landing-page.md')
        if os.path.exists(glass_wf_path):
            try:
                with open(glass_wf_path, 'r', encoding='utf-8') as f:
                    workflow_content = f.read()
                print(f"   🎨 glass-landing-page workflow otomatik yüklendi (premium UI)")
            except Exception as e:
                print(f"   ⚠️  Workflow yüklenemedi: {e}")

    # Proje tipine göre yönlendir
    if project_type == 'analyzer':
        # Proje analizi / kod inceleme / iyileştirme raporu
        return process_analyzer_project(card, task_config, board_id, list_ids, rules_text, workflow_content or "")
    elif project_type in ('fullstack', 'frontend'):
        # Frontend ve fullstack projeler için scaffold ile tam proje yapısı oluştur
        return process_fullstack_project(card, task_config, board_id, list_ids, rules_text, workflow_content or "")
    elif project_type == 'backend':
        # Backend-only projeler için scaffold_backend_project kullanılır
        return process_standard_project(card, task_config, board_id, list_ids, rules_text)
    else:
        # CLI ve diğer projeler
        return process_standard_project(card, task_config, board_id, list_ids, rules_text)


# ============================================================
# ANA ORCHESTRATOR DONGUSU
# ============================================================

def run_orchestrator_v3(board_id: str, check_interval: int = 30):
    """
    Orchestrator V3 ana dongusu - .agent yapısı destekli
    """
    print("\n" + "=" * 80)
    print("🎯 TRELLO ORCHESTRATOR V3 BAŞLATILDI")
    print("🆕 .agent/ YAPISI DESTEKLİ (Skills + Rules + Workflows)")
    print("=" * 80)
    print(f"Board ID: {board_id}")
    print(f"Kontrol Araligi: {check_interval} saniye")

    # .agent yapısını göster
    print("\n📁 .agent Yapısı:")
    skills = list_available_skills()
    print(f"   Skills ({len(skills)}): {', '.join(skills)}")

    rules = load_all_rules()
    print(f"   Rules ({len(rules)}): {', '.join(rules.keys())}")

    workflows_dir = os.path.join(AGENT_DIR, 'workflows')
    if os.path.exists(workflows_dir):
        workflows = [f for f in os.listdir(workflows_dir) if f.endswith('.md')]
        print(f"   Workflows ({len(workflows)}): {', '.join(workflows)}")

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
        print("\n❌ 'Backlog' listesi bulunamadi!")
        return

    print("\n🔍 Backlog izleniyor... (V3 - .agent destekli)")
    print("(Ctrl+C ile durdurun)\n")

    islenen_kartlar = set()

    try:
        global STOP_ORCHESTRATOR
        STOP_ORCHESTRATOR = False
        while not STOP_ORCHESTRATOR:
            url = f"{trello.base_url}/lists/{list_ids['Backlog']}/cards"
            params = trello._get_auth_params()

            try:
                import requests
                response = requests.get(url, params=params)
                response.raise_for_status()
                backlog_cards = response.json()

                for card in backlog_cards:
                    if STOP_ORCHESTRATOR:
                        break
                    if card['id'] not in islenen_kartlar:
                        print(f"\n🆕 Yeni kart bulundu: {card['name']}")

                        success = process_backlog_card_v3(card, board_id, list_ids)

                        if success:
                            islenen_kartlar.add(card['id'])

                        time.sleep(5)

                if STOP_ORCHESTRATOR:
                    break

                print(f"\n⏳ {check_interval} saniye bekleniyor...")
                # Uyku sırasında durdurmayı daha hızlı algılamak için parçalı uyku
                for _ in range(check_interval):
                    if STOP_ORCHESTRATOR:
                        break
                    time.sleep(1)

            except Exception as e:
                print(f"❌ Hata: {e}")
                time.sleep(check_interval)
                
        print("\n🛑 Orchestrator V3 güvenli bir şekilde durduruldu.")

    except KeyboardInterrupt:
        print("\n\n🛑 Orchestrator V3 durduruldu.")


# ============================================================
# WEBHOOK MODU
# ============================================================

def run_orchestrator_webhook(board_id: str, callback_url: str = None, port: int = 5001):
    """
    Orchestrator V3 — Webhook modu

    Polling yerine Trello Webhook API kullanır.
    Trello, board'da değişiklik olduğunda bu sunucuya bildirim gönderir.

    Args:
        board_id: İzlenecek board ID
        callback_url: Trello'nun bildirim göndereceği URL (ngrok ile)
        port: Webhook sunucu portu (standalone modda)
    """
    from trello_webhook_handler import WebhookHandler

    print("\n" + "=" * 80)
    print("🔗 TRELLO ORCHESTRATOR V3 — WEBHOOK MODU")
    print("🆕 Push-based mimari: Trello → Webhook → Agent'lar")
    print("=" * 80)
    print(f"Board ID: {board_id}")

    # .agent yapısını göster
    print("\n📁 .agent Yapısı:")
    skills = list_available_skills()
    print(f"   Skills ({len(skills)}): {', '.join(skills)}")

    rules = load_all_rules()
    print(f"   Rules ({len(rules)}): {', '.join(rules.keys())}")

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
    for name, lid in list_ids.items():
        print(f"   - {name}: {lid}")

    if "Backlog" not in list_ids:
        print("\n❌ 'Backlog' listesi bulunamadi!")
        return

    # WebhookHandler'ı kur
    handler = WebhookHandler(trello, board_id, list_ids)
    handler.set_backlog_callback(process_backlog_card_v3)

    # Mevcut Backlog kartlarını kontrol et (ilk tarama)
    print("\n🔍 Mevcut Backlog kartları kontrol ediliyor...")
    try:
        import requests as req
        url = f"{trello.base_url}/lists/{list_ids['Backlog']}/cards"
        params = trello._get_auth_params()
        response = req.get(url, params=params)
        response.raise_for_status()
        backlog_cards = response.json()

        if backlog_cards:
            print(f"   📋 {len(backlog_cards)} kart bulundu, işleniyor...")
            for card in backlog_cards:
                simulated = {
                    "action": {
                        "type": "createCard",
                        "date": "",
                        "data": {
                            "card": {"id": card["id"], "name": card["name"]},
                            "list": {"id": list_ids["Backlog"], "name": "Backlog"},
                            "board": {"id": board_id}
                        },
                        "memberCreator": {"fullName": "Initial Scan"}
                    },
                    "model": {"id": board_id}
                }
                handler.process_event(simulated)
        else:
            print("   ✨ Backlog boş, yeni kart bekleniyor...")
    except Exception as e:
        print(f"   ⚠️ Mevcut kartlar kontrol edilemedi: {e}")

    # Standalone webhook sunucusu
    if callback_url:
        # Webhook'u Trello'ya kaydet
        print(f"\n🔗 Trello Webhook kaydediliyor...")
        print(f"   Callback URL: {callback_url}")

        webhook = trello.create_webhook(
            callback_url=callback_url,
            id_model=board_id,
            description="Orchestrator V3 Webhook"
        )

        if webhook:
            print(f"   ✅ Webhook aktif: {webhook['id']}")
        else:
            print("   ⚠️ Webhook kaydedilemedi! Callback URL erişilebilir olmalı.")
            print("   💡 İpucu: ngrok http 5001 komutu ile tunnel oluşturun")

    # Minimal Flask sunucusu başlat
    from flask import Flask as WebhookFlask, request as wh_request, jsonify as wh_jsonify

    webhook_app = WebhookFlask(__name__)

    @webhook_app.route('/api/trello/webhook', methods=['HEAD'])
    def wh_verify():
        return '', 200

    @webhook_app.route('/api/trello/webhook', methods=['POST'])
    def wh_receive():
        payload = wh_request.json
        if not payload:
            return wh_jsonify({"status": "empty"}), 200
        result = handler.process_event(payload)
        return wh_jsonify(result), 200

    @webhook_app.route('/api/trello/webhook/stats', methods=['GET'])
    def wh_stats():
        return wh_jsonify(handler.get_stats()), 200

    print(f"\n🚀 Webhook sunucusu başlatılıyor: http://0.0.0.0:{port}")
    print("   Trello event'leri burada dinleniyor...")
    print("   (Ctrl+C ile durdurun)\n")

    try:
        webhook_app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Webhook sunucusu durduruldu.")

        # Webhook'u Trello'dan temizle
        if callback_url and webhook:
            print("🗑️ Trello webhook temizleniyor...")
            trello.delete_webhook(webhook['id'])


# ============================================================
# MAIN
# ============================================================

def main():
    """Orchestrator V3 başlat — Polling veya Webhook modu"""
    print("\n" + "=" * 80)
    print("🎯 TRELLO ORCHESTRATOR V3")
    print("🆕 .agent/ Yapısı Destekli")
    print("   Skills + Rules + Workflows Entegrasyonu")
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

        # Mod seçimi
        print("\n" + "-" * 40)
        print("📡 Çalışma Modu Seçin:")
        print("1. 🔄 Polling (30 sn aralıklı kontrol — klasik)")
        print("2. 🔗 Webhook (Agent Manager üzerinden — port 5000)")
        print("3. 🚀 Webhook Standalone (kendi sunucusu — port 5001)")
        print("-" * 40)

        mod = input("\nMod seçin (1/2/3) [varsayılan: 1]: ").strip() or "1"

        if mod == "1":
            # Klasik polling modu
            run_orchestrator_v3(board_id)

        elif mod == "2":
            # Agent Manager webhook modu
            print("\n🔗 Webhook modu — Agent Manager üzerinden")
            print("   Agent Manager'ın çalışıyor olması gerekir (port 5000)")
            print("   Webhook kurulumu için şu API'yi çağırın:")
            print(f'   curl -X POST http://localhost:5000/api/trello/webhook/setup \\')
            print(f'     -H "Content-Type: application/json" \\')
            print(f'     -d \'{{"board_id": "{board_id}"}}\' ')
            print("\n   Sonra Trello'ya kart ekleyin, otomatik işlenecek!")
            print("\n💡 Lokal geliştirme için ngrok gerekir:")
            print("   ngrok http 5000")
            print("   Sonra ngrok URL'ini callback_url olarak gönderin.")

            input("\n[Enter'a basarak Agent Manager moduna geçin...]")

            # Agent Manager'a webhook setup isteği gönder
            import requests as req
            try:
                resp = req.post(
                    "http://localhost:5000/api/trello/webhook/setup",
                    json={"board_id": board_id}
                )
                if resp.status_code in (200, 201):
                    result = resp.json()
                    print(f"\n✅ Webhook kurulumu tamamlandı!")
                    print(f"   Board: {board_id}")
                    print(f"   Webhook ID: {result.get('webhook_id', 'N/A')}")
                    print(f"   Callback: {result.get('callback_url', 'N/A')}")
                    print(f"\n📈 İstatistikler: http://localhost:5000/api/trello/webhook/stats")
                    print("\n🎯 Artık Trello'ya kart ekleyin. Agent Manager otomatik işleyecek.")
                    print("   (Bu pencereyi kapatabilirsiniz)")
                else:
                    print(f"❌ Webhook kurulumu başarısız: {resp.text}")
            except Exception as e:
                print(f"❌ Agent Manager'a bağlanılamadı: {e}")
                print("   Agent Manager çalışıyor mu? (python agent_manager.py)")

        elif mod == "3":
            # Standalone webhook sunucusu
            callback = input("\nngrok callback URL (boş = sadece sunucu): ").strip() or None
            run_orchestrator_webhook(board_id, callback_url=callback, port=5001)

        else:
            print("❌ Gecersiz mod!")

    except ValueError:
        print("❌ Gecersiz giris!")
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandirildi.")


if __name__ == "__main__":
    main()

