# AI Ajanlar ile Task Yönetim Sistemi

Bu proje, **CrewAI** kullanarak AI ajanlarını **Jira** veya **Trello** ile entegre eder. Herhangi bir yazılım geliştirme görevini AI'a vererek otomatik olarak task yönetim sisteminde kartlar/issue'lar oluşturabilir, kod yazabilir ve test edebilirsiniz.

## 🎯 Özellikler

- ✅ **Parametrik Görev Sistemi**: Herhangi bir yazılım geliştirme görevini verebilirsiniz
- ✅ **8 AI Ajanı**: Analist, Orchestrator (PM), **Backend Dev**, **Frontend Dev**, QA, **Product Assistant**, **Approval Agent** 🆕
- ✅ **WhatsApp Approval Agent**: Task'ları WhatsApp'tan onaylama sistemi! 🔥 **YENİ**
- ✅ **Product Assistant**: Karar destek sistemi - Kod yazmaz, sadece düşünür ve önerir!
- ✅ **Backend Developer Agent**: API, Database, Business Logic uzmanı 🆕
- ✅ **Frontend Developer Agent**: UI/UX, React/Vue/Angular uzmanı 🆕
- ✅ **Fullstack Proje Desteği**: Backend ve Frontend ayrı ayrı geliştirilir 🆕
- ✅ **Jira Entegrasyonu**: Otomatik issue oluşturma, güncelleme, yorum ekleme
- ✅ **Trello Entegrasyonu**: Otomatik kart oluşturma, board yapısı kurma, bug takibi
- ✅ **Trello Orchestrator V2**: Backend/Frontend ayrımı ile akıllı iş dağıtımı! 🆕
- ✅ **Otomatik Kod Üretme**: AI tarafından yazılan kod dosyaya kaydedilir
- ✅ **Test ve Bug Yönetimi**: Otomatik test senaryoları ve bug kartları
- ✅ **10+ Örnek Kullanım**: Web API, CLI araçları, Discord bot, vb.

---

## 📁 Dosya Yapısı

```
├── jira_helper.py                    # Jira REST API helper sınıfı
├── jira_task_agents.py               # Jira entegrasyonlu parametrik sistem
├── trello_helper.py                  # Trello REST API helper sınıfı
├── trello_task_agents.py             # Trello entegrasyonlu parametrik sistem
├── trello_orchestrator.py            # Backlog izleyici & otomatik işleyici (V1)
├── trello_orchestrator_v2.py         # 🆕 Backend/Frontend + WhatsApp Approval orchestrator
├── whatsapp_approval_agent.py        # 🔥 WhatsApp onay mekanizması
├── product_assistant.py              # 🆕 Decision & Product Brain (Kod yazmaz!)
├── product_assistant_example.py      # Product Assistant örnekleri
├── example_tasks.py                  # 10+ örnek kullanım senaryosu
│
├── TRELLO_SETUP.md                   # Trello kurulum rehberi
├── ORCHESTRATOR_KULLANIM.md          # Orchestrator kullanım kılavuzu
├── WHATSAPP_APPROVAL_KURULUM.md      # 🔥 WhatsApp Approval Agent kurulum
├── PRODUCT_ASSISTANT_KULLANIM.md     # 🆕 Product Assistant kullanım kılavuzu
├── PRODUCT_ASSISTANT_QUICKSTART.md   # Product Assistant hızlı başlangıç
├── .env.example                      # 🔥 Twilio credentials template
├── README.md                         # Bu dosya
│
├── jira_snake_game_agents.py        # Eski: Yılan oyunu odaklı Jira versiyonu
├── main.py                           # Eski: Yılan oyunu (Jira yok)
├── snake_game.py                     # İlk yılan oyunu
└── snake_game_ai.py                  # AI tarafından üretilen yılan oyunu
```

---

## 🚀 Hızlı Başlangıç

### 1. Gerekli Paketleri Yükle

```bash
pip install crewai requests openai
```

### 2. Credentials Ayarla

#### Jira için:

[jira_task_agents.py](jira_task_agents.py) dosyasını aç:

```python
JIRA_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_TOKEN = "your-jira-api-token"
PROJECT_KEY = "YOUR_PROJECT_KEY"
```

#### Trello için:

[TRELLO_SETUP.md](TRELLO_SETUP.md) dosyasını oku ve API Key/Token al.

[trello_task_agents.py](trello_task_agents.py) dosyasını aç:

```python
TRELLO_API_KEY = "your-trello-api-key"
TRELLO_TOKEN = "your-trello-token"
```

### 3. Görevi Tanımla

```python
from jira_task_agents import TaskConfig, run_task_project

task_config = TaskConfig(
    project_name="Todo List Uygulaması",
    description="Komut satırından çalışan todo list",
    requirements=[
        "Todo ekleme, silme, güncelleme",
        "JSON'a kaydetme",
        "Listeleme ve filtreleme"
    ],
    file_name="todo_app.py",
    programming_language="Python"
)

run_task_project(task_config)
```

### 4. Çalıştır

```bash
# Jira ile
python jira_task_agents.py

# Trello ile
python trello_task_agents.py

# Örneklerden birini seç
python example_tasks.py
```

---

## 💡 Kullanım Örnekleri

### Örnek 1: Web API Geliştirme

```python
task_config = TaskConfig(
    project_name="Web API Geliştirme",
    description="RESTful API ile kullanıcı yönetim sistemi",
    requirements=[
        "FastAPI framework kullan",
        "PostgreSQL veritabanı",
        "JWT authentication",
        "CRUD operasyonları"
    ],
    file_name="user_api.py",
    programming_language="Python"
)
```

### Örnek 2: Discord Bot

```python
task_config = TaskConfig(
    project_name="Discord Bot",
    description="Basit komutlar çalıştırabilen Discord botu",
    requirements=[
        "discord.py kütüphanesi",
        "!help, !ping, !echo komutları",
        "Environment variables (.env)"
    ],
    file_name="discord_bot.py",
    programming_language="Python"
)
```

### Örnek 3: Node.js Express API

```python
task_config = TaskConfig(
    project_name="Node.js Express API",
    description="Express.js ile REST API",
    requirements=[
        "Express.js framework",
        "MongoDB veritabanı",
        "JWT authentication",
        "CORS yapılandırması"
    ],
    file_name="server.js",
    programming_language="JavaScript"
)
```

**Daha fazla örnek için:** [example_tasks.py](example_tasks.py) dosyasına bakın (10+ örnek)

---

## 🔄 İş Akışı

### Jira Akışı

```
1. Görev Tanımla (TaskConfig)
         ↓
2. AI Ajanları Çalışır
   - PM: Proje planı yapar
   - Developer: Kod yazar
   - QA: Test eder
         ↓
3. Jira'da Issue'lar Oluşturulur
   - Epic
   - [DEV] Development Task
   - [QA] Test Task
   - [PM] Review Task
         ↓
4. Kod Dosyaya Yazılır
         ↓
5. Task Durumları Güncellenir
   - DEV task → In Progress
   - Kod yorumu eklenir
         ↓
6. Test Raporu Jira'ya Eklenir
```

### Trello Akışı (V2 - WhatsApp Approval ile)

```
1. Task Backlog'a Eklenir (Manuel)
         ↓
2. 📱 APPROVAL AGENT ANALİZ YAPAR
   - Task detayları çıkarılır
   - Maliyet hesaplanır
   - Risk analizi yapılır
         ↓
3. 📱 WHATSAPP'TAN ONAY İSTENİR
   "🤖 YENİ TASK ONAYI GEREKİYOR"
   • Proje: Blog Uygulaması
   • Tip: fullstack
   • Tahmini Süre: 2-3 saat
   • Maliyet: ~$0.25 USD

   Yanıt: ✅ ONAYLA / ❌ REDDET
         ↓
4a. ONAYLANIRSA ✅
         ↓
    AI Ajanları Çalışır
    - Analist → Proje tipini belirler
    - Backend Dev → API yazar
    - Frontend Dev → UI yazar
    - QA → Test eder
         ↓
    Kod Dosyalara Yazılır
         ↓
    Trello'da Kartlar İlerler
    Backlog → In Progress → Code Review → Testing → Done

4b. REDDEDİLİRSE ❌
         ↓
    Task İptal Edilir
    Kart Backlog'a geri döner
```

---

## 🎨 Trello Board Yapısı

| Liste | Açıklama | Otomatik İşlem |
|-------|----------|----------------|
| **Backlog** | Gelecek fikirler | - |
| **To Do** | Yapılacaklar | ✅ Başlangıçta kartlar burada |
| **In Progress** | Çalışılıyor | ✅ DEV kartı buraya taşınır |
| **Code Review** | Review bekliyor | ✅ DEV ve PM kartları buraya |
| **Testing** | Test ediliyor | ✅ QA kartı buraya taşınır |
| **Done** | Tamamlandı | Manuel taşıma |
| **Bugs** | Hatalar | ✅ Bug bulunursa otomatik |

---

## 🐛 Bug Yönetimi (Trello)

Test uzmanı kod incelerken bug bulursa:

1. **Bugs** listesinde otomatik bug kartı oluşturulur
2. Kırmızı label eklenir
3. Bug detayları yazılır:
   - Adımlar
   - Beklenen davranış
   - Gerçek davranış
   - Öncelik seviyesi

---

## 📊 Çıktılar

### Oluşturulan Dosyalar

1. **{file_name}** - AI tarafından yazılan kod
2. **{file_name}_project_report.txt** (Jira) - Detaylı rapor
3. **{file_name}_trello_report.txt** (Trello) - Detaylı rapor

### Örnek Rapor

```
WEB API GELIŞTIRME - PROJE RAPORU
============================================================

📊 Proje: Web API Geliştirme
📝 Açıklama: RESTful API ile kullanıcı yönetim sistemi
💻 Dil: Python
📄 Dosya: user_api.py

📊 OLUŞTURULAN JIRA TASK'LARI:
  - TES-123
  - TES-124
  - TES-125

============================================================
[AI ajanlarının çıktıları...]
```

---

## 🛠️ Teknik Detaylar

### AI Ajanları

1. **Product Assistant** 🆕 ⭐
   - **KOD YAZMAZ!** Sadece düşünür ve önerir
   - Fikirleri sorgulamak
   - Alternatifleri tartışmak
   - Riskleri erken göstermek
   - Net karar opsiyonları sunmak
   - Execution-ready tasklar önermek
   - MVP disiplini ile çalışır
   - AI gerekliliğini sorgular

2. **Analist Agent**
   - Backlog kartlarını analiz eder
   - Teknik gereksinimlere dönüştürür
   - Proje tipini belirler (fullstack, backend, frontend, cli)
   - TaskConfig oluşturur

3. **Orchestrator (PM)**
   - İşleri dağıtır
   - Proje planı oluşturur
   - Kabul kriterlerini tanımlar
   - Backend/Frontend koordinasyonu

4. **Backend Developer Agent** 🆕
   - RESTful API tasarımı ve implementasyonu
   - Veritabanı şema tasarımı (SQL/NoSQL)
   - Authentication & Authorization (JWT, OAuth)
   - Business logic ve veri validasyonu
   - API documentation (Swagger/OpenAPI)
   - Frameworks: FastAPI, Flask, Django, Express, NestJS

5. **Frontend Developer Agent** 🆕
   - Modern UI/UX tasarımı
   - Component-based architecture
   - State management (Redux, Zustand, Pinia)
   - API entegrasyonu (REST, GraphQL)
   - Responsive design (mobile-first)
   - Frameworks: React, Vue, Angular

6. **Test Uzmanı (QA)**
   - Backend testleri (API, Database, Business Logic)
   - Frontend testleri (Component, Integration, UI/UX)
   - Fullstack entegrasyon testleri
   - Bug bulur ve raporlar

### Kullanılan Teknolojiler

- **CrewAI**: Multi-agent AI framework
- **OpenAI GPT-4o-mini**: AI model
- **Jira REST API**: Jira entegrasyonu
- **Trello REST API**: Trello entegrasyonu

---

## 📚 Dokümantasyon

- **Jira Kurulumu**: [jira_helper.py](jira_helper.py) dosyasındaki docstring'lere bakın
- **Trello Kurulumu**: [TRELLO_SETUP.md](TRELLO_SETUP.md)
- **API Referansı**: Her helper dosyasında detaylı docstring'ler var

---

## 🔐 Güvenlik Notları

⚠️ **ÖNEMLİ**: Credentials'ları asla Git'e commit etmeyin!

```bash
# .gitignore dosyanıza ekleyin:
*.env
*_credentials.py
```

Credentials'ları environment variables'da tutun:

```python
import os
JIRA_TOKEN = os.getenv("JIRA_API_TOKEN")
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
```

---

## 🎯 Gelecek Özellikler

- [ ] GitHub Issues entegrasyonu
- [ ] Asana entegrasyonu
- [ ] Otomatik test çalıştırma (pytest, jest vb.)
- [ ] CI/CD pipeline entegrasyonu
- [ ] Web UI (Streamlit/Gradio)
- [ ] Multi-language support (İngilizce)
- [ ] Webhook desteği (real-time updates)

---

## 🤝 Katkıda Bulunma

Katkıda bulunmak isterseniz:

1. Fork yapın
2. Feature branch oluşturun
3. Commit'leyin
4. Push yapın
5. Pull Request açın

---

## 📄 Lisans

Bu proje MIT lisansı altındadır.

---

## 📞 İletişim

Sorularınız için:

- GitHub Issues açın
- Dokümantasyonu inceleyin
- Örnek kullanımları çalıştırın

---

---

## 🆕 TRELLO ORCHESTRATOR V2 - WhatsApp Approval ile Otomatik İş Çekme

### 🔥 Yeni Özellikler (V2)

1. **📱 WhatsApp Approval Agent:**
   - Task Backlog'a eklendiğinde WhatsApp'tan onay ister
   - Detaylı task analizi (maliyet, risk, süre tahmini)
   - Kullanıcı onaylarsa → agentlar çalışır
   - Kullanıcı reddederse → task iptal edilir

2. **🎯 Akıllı Agent Seçimi:**
   - Fullstack proje → Backend + Frontend ayrı geliştirilir
   - Backend-only → Backend Developer Agent
   - Frontend-only → Frontend Developer Agent
   - CLI/Script → Generic Developer Agent

3. **📊 Detaylı İstatistikler:**
   - Console'a kod yazdırılmaz (sadece istatistikler)
   - Dosya adı, satır sayısı, boyut, dil/framework

### Nasıl Çalışır? (V2)

```
Sen Backlog'a kart ekle
   ↓
📱 Approval Agent analiz yapar
   ↓
WhatsApp'tan onay mesajı gelir
"🤖 YENİ TASK ONAYI GEREKİYOR
 • Proje: Blog Uygulaması
 • Tahmini Süre: 2-3 saat
 • Maliyet: ~$0.25 USD

 ✅ ONAYLA / ❌ REDDET"
   ↓
Sen WhatsApp'tan yanıt ver
   ↓
✅ ONAYLANIRSA:
   Analist → Backend Dev → Frontend Dev → QA → Done!
❌ REDDEDİLİRSE:
   Task iptal edilir
```

### Hızlı Başlangıç (V2)

```bash
# 1. WhatsApp Approval kurulumu (ilk kez)
#    WHATSAPP_APPROVAL_KURULUM.md dosyasını oku
#    Twilio hesabı aç, .env dosyasını ayarla

# 2. Orchestrator V2'yi başlat
python trello_orchestrator_v2.py

# 3. Board seç (veya yeni oluştur)

# 4. Trello'da Backlog listesine kart ekle
#    Başlık: "E-ticaret Blog Uygulaması"
#    Açıklama: "Django backend + React frontend..."

# 5. WhatsApp'tan onay mesajı gelir
#    "ONAYLA" veya "REDDET" yanıtı ver

# 6. Onaylanırsa agentlar çalışmaya başlar

# 4. İzle! AI ajanları otomatik çalışacak
```

### Örnek Backlog Kartı

**Başlık:**
```
RESTful API - Kullanıcı Yönetimi
```

**Açıklama:**
```
FastAPI ile kullanıcı yönetim sistemi:
- CRUD operasyonları
- JWT authentication
- PostgreSQL veritabanı
- Input validation
- API documentation
```

30 saniye içinde Orchestrator kartı görür ve:
1. Kartı "In Progress" taşır
2. Analist analiz eder
3. PM plan yapar
4. Developer kod yazar
5. QA test eder
6. Kart "Done" taşınır

### Detaylı Kullanım

Tüm detaylar için: **[ORCHESTRATOR_KULLANIM.md](ORCHESTRATOR_KULLANIM.md)**

---

## 🎉 Üç Kullanım Modu

### Mod 1: Decision Mode (Product Assistant) 🆕 ⭐

```bash
# Fikrinizi tartışın, analiz edin, karar verin
python product_assistant.py

# Komutlar:
# - 'yeni': Yeni fikir analizi
# - 'tasklar': Execution-ready tasklar üret
# - 'cikis': Çık

# ÖNEMLI: Kod yazmaz, sadece düşünür ve önerir!
```

**Ne zaman kullanılır?**
- Yeni bir fikriniz var ve netleştirmek istiyorsunuz
- Alternatif çözümler arasında karar vermek istiyorsunuz
- AI gerekli mi değil mi anlamak istiyorsunuz
- MVP kapsamını belirlemek istiyorsunuz
- Risk analizi yapmak istiyorsunuz

**Çıktı:** `product_assistant_tasks.txt` (Execution-ready tasklar)

---

### Mod 2: Manuel (Push)

```bash
# Siz kodu çalıştırıp task veriyorsunuz
python trello_task_agents.py
python example_tasks.py
```

---

### Mod 3: Otomatik (Pull)

```bash
# V1: Basit projeler için
python trello_orchestrator.py

# V2: Fullstack projeler için (Backend + Frontend) 🆕
python trello_orchestrator_v2.py

# Sonra Trello'ya git ve Backlog'a kart ekle!
```

---

## 🚀 ORCHESTRATOR V2 - Backend & Frontend Desteği 🆕

### Ne Değişti?

Orchestrator V2, test yönetim otomasyon projesi için özelleştirilmiştir:

#### V1 (trello_orchestrator.py):
- Tek "Developer" agent
- Basit projeler için ideal
- CLI, script, tek dosya projeler

#### V2 (trello_orchestrator_v2.py): 🆕
- **Backend Developer** + **Frontend Developer** ayrı agent'lar
- Fullstack proje desteği
- Akıllı proje tipi tespiti
- Backend ve Frontend kodları ayrı dosyalara

### Proje Tipleri

Analist agent projeyi analiz edip tipini belirler:

| Tip | Açıklama | Kullanılan Agent'lar |
|-----|----------|---------------------|
| **fullstack** | Backend + Frontend | Backend Dev + Frontend Dev + QA |
| **backend** | Sadece API/Backend | Backend Dev + QA |
| **frontend** | Sadece UI/Frontend | Frontend Dev + QA |
| **cli** | Komut satırı aracı | Generic Dev + QA |

### Örnek Fullstack Kart

**Trello Kartı:**
```
Başlık: Test Yönetim Sistemi - Web UI

Açıklama:
- Kullanıcıların test case'leri oluşturabileceği web uygulaması
- Backend: FastAPI ile RESTful API
- Frontend: React ile modern UI
- Test case CRUD operasyonları
- Test sonuçları raporlama
```

**Orchestrator V2 Akışı:**
```
1. Analist analiz eder → "fullstack" olarak belirler
2. Backend Developer → API ve business logic yazar
3. Frontend Developer → React UI yazar
4. QA → Her iki katmanı da test eder
5. Ayrı dosyalar: backend_api.py + frontend_app.jsx
```

### Çalıştırma

```bash
python trello_orchestrator_v2.py
```

### Çıktı Dosyaları

Fullstack proje için:
- `backend_api.py` - Backend kodu (FastAPI/Flask/Django)
- `frontend_app.jsx` - Frontend kodu (React/Vue/Angular)
- Her iki dosya da ayrı ayrı test edilir

---

## 🧠 PRODUCT ASSISTANT - Decision & Product Brain 🆕

### Nedir?

Product Assistant, yazılım ve yapay zeka projelerinde **karar destek sistemi** olarak çalışan bir AI agent'tır.

**ÖNEMLI:** Kod yazmaz, test yazmaz, Jira'ya issue açmaz. Sadece düşünür, analiz eder ve önerir!

### Temel Prensipler

1. **Hemen Çözüm Üretme**
   - Önce problemi netleştir
   - Belirsizlik varsa açıkça belirt

2. **Alternatif Sunma**
   - En az 2 çözüm yolu üret
   - Tercih edilen yolu gerekçelendir
   - Reddedilenleri neden reddettiğini açıkla

3. **AI Eleştirisi**
   - "AI şart mı?" sorusunu her zaman sor
   - Gereksiz AI kullanımını özellikle belirt

4. **MVP Disiplini**
   - Mutlaka out-of-scope tanımı yap
   - "Sonra bakarız" dediğin her şeyi listele

5. **Execution'a Geçme**
   - Task önerir, ama hiçbir agent'ı otomatik tetiklemez
   - Karar yetkisi her zaman kullanıcıdadır

### Kullanım Örneği

```bash
python product_assistant.py

📝 Sen: yeni

💡 Yeni fikir/özellik talebini yaz:
📝 Fikir: Kullanıcıların aylık harcamalarını takip edebileceği mobil uygulama

🤖 Asistan:
## 1. PROBLEM NETLEŞTIRME
- Kullanıcı profili kim? (Öğrenci, aile, şirket?)
- Manuel mi otomatik takip mi?
...

## 2. ALTERNATIF ÇÖZÜMLER
- Çözüm A: Excel/Google Sheets şablonu
- Çözüm B: Native mobil uygulama
...

📝 Sen: tasklar

🎯 EXECUTION-READY TASKLAR:
[Tasklar oluşturulur ve product_assistant_tasks.txt'ye kaydedilir]
```

### Detaylı Kullanım

Tüm detaylar için: **[PRODUCT_ASSISTANT_KULLANIM.md](PRODUCT_ASSISTANT_KULLANIM.md)**

---

## 🎉 Hazır mısınız?

```bash
# 1. Decision Mode (Fikir analizi): 🆕
python product_assistant.py

# 2. Manuel Mod:
python example_tasks.py

# 3. Otomatik Mod - Basit Projeler:
python trello_orchestrator.py

# 4. Otomatik Mod - Fullstack Projeler (Önerilen): 🆕
python trello_orchestrator_v2.py
```

**Happy Coding! 🚀**

---

## 📊 Karşılaştırma Tablosu

| Özellik | Orchestrator V1 | Orchestrator V2 🆕 |
|---------|----------------|-------------------|
| Backend Agent | Generic Developer | **Specialized Backend Dev** |
| Frontend Agent | ❌ | **Specialized Frontend Dev** |
| Fullstack Destek | Tek dosya | **Ayrı Backend + Frontend** |
| Proje Tipi Tespiti | Manuel | **Otomatik (Analist)** |
| API Documentation | Bazen | **Her zaman (Swagger)** |
| UI Framework Desteği | Sınırlı | **React/Vue/Angular** |
| Test Kapsamı | Genel | **Backend + Frontend + Integration** |
| İdeal Kullanım | CLI, Script | **Web Apps, SaaS, Fullstack** |

---

## 🎯 Hangi Modu Kullanmalıyım?

### Product Assistant
- ✅ Fikriniz var ama netleştirmek istiyorsunuz
- ✅ AI gerekli mi değil mi bilmiyorsunuz
- ✅ MVP kapsamını belirlemek istiyorsunuz
- ❌ Kod yazdırmak istiyorsanız (bunun için Orchestrator)

### Orchestrator V1
- ✅ Basit CLI araçları
- ✅ Tek dosya scriptler
- ✅ Hızlı prototip
- ❌ Fullstack web uygulamaları

### Orchestrator V2 🆕
- ✅ Test yönetim sistemi
- ✅ Web uygulamaları
- ✅ SaaS ürünleri
- ✅ API + UI gerektiren projeler
- ✅ **Önerilen mod!**

---

**Happy Coding! 🚀**
