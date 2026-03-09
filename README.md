# AI Agent Manager & Raporlama

Bu proje, güçlü AI (Yapay Zeka) ajanları aracılığıyla yazılım projelerini, Issue tracking / Task Management sistemlerini (**Trello** / **Jira**), e-posta analizlerini, BT Destek operasyonlarını ve **Berqun** verimlilik raporlama işlemlerini tamamen otomatize eden çok kapsamlı bir teknoloji harikasıdır. 

Mevcut sistem, şirketinizin ihtiyaçlarına uygun olarak **çoklu LLM** entegrasyonuna sahiptir (OpenAI GPT-4o, Anthropic Claude vb.) ve görev ne olursa olsun en uygun profesyonel ajanı yetkilendirerek sürecin uçtan uca yönetilmesini sağlar.

---

## 🎯 Temel Özellikler

### 1. 🤖 Gelişmiş Çoklu AI Ajanları Sistemi
Projede kendi yeteneği ve **.agent/skills** klasöründe belirtilmiş sistem promptlarına sahip çok sayıda profesyonel ajan bulunmaktadır:
- **Backend Developer Agent**: API, Veritabanı ve Security tasarımı.
- **Frontend Design Pro Agent**: Glassmorphism ve modern UI/UX tasarım uzmanı. (React, Tailwind)
- **QA Engineer Agent**: Otomatik test, QA standartları ve Bug analizi yapar. 
- **DevOps Engineer Agent**: CI/CD, Containerization ve sunucu operasyonları.
- **Security Specialist Agent**: Kod tarar, zafiyetleri denetler. (DevSecOps)
- **Solution Architect Agent**: Teknik mimari tasarlar, C4 modeller oluşturur.
- **İş Analisti (Business Analyst) Agent**: Backlog özelliklerini kullanıcı hikayelerine (User Story) çevirir.
- **Email Analyst Agent**: Gelen destek maillerini anlar, kategorize eder ve intent (amaç) analizi yapar.
- **HR Pro Agent**: İş ilanları, mülakat analizleri ve CV tarama.

### 2. 📋 Trello & Jira Backlog Orchestrator
- Jira veya Trello tahtanızdaki (Board) backlog görevlerini okur.
- Göbeğinde yer alan **Orchestrator V3** sistemiyle görevin Frontend projesi mi, Backend projesi mi yoksa Fullstack projesi mi olduğunu anlar.
- Gerekli olan ajanlara dosyaları kendi klasör hiyerarşisinde oluşturmalarını (örneğin Web_Sayfasi_Tasarimi klasörü içerisine src/App.jsx, index.css) emreder ve Trello kartlarının statülerini `To Do -> In Progress -> Code Review -> Test -> Done` olarak otomatik taşır.

### 3. 🔥 WhatsApp Onay (Approval) Mekanizması
- Belirli maliyetlerin üzerindeki görevler veya riskli işlemler için ajanlar harekete geçmeden önce **WhatsApp üzerinden size bir özet ve maliyet analizi gönderir**.
- Siz "ONAYLA" cevabı verene kadar ajanlar beklemede kalır. Sürpriz maliyetleri sıfırlar!

### 4. 📊 Berqun Verimlilik Analizi Raporlaması
- Çalışanların **Berqun** üzerinden gelen verilerini otomatik olarak çeker.
- Düzenli aylık ve haftalık raporlar üretir.
- Çalışanların fazla mesaili BQ puanlarını özel işlemlerden geçirerek 100 üzerinden başarı analizini yapar ve renk kodlarıyla rapor oluşturur.
- Otomatik HTML şablonları üzerinden takımlara mail raporları yollar (**Mail Sender**).

### 5. 📧 Mail Listener ve Anında Destek Yanıtı
- Gelen mailleri 7/24 dinler.
- Destek veya IT talebi olanları **ITSM Servis Masası (Service Desk)** ajanıyla cevaplar.
- Rapor talep ediliyorsa e-maili analiz eder, gerekli haftalık/aylık raporları arka planda Python uygulamaları sayesinde hazırlayarak anında yanıtla beraber geri gönderir.

---

## 📁 Proje Klasör ve Dosya Yapısı

```
├── .agent/                    # Ajan yetenekleri (Skills/Rules/Workflows)
│   ├── rules/                 # Proje genel kuralları (Frontend kuralları vb.)
│   ├── skills/                # Opsiyonel roller (Frontend Pro, DevOps, vs.)
│   └── workflows/             # AI ajanları için belirlenmiş yol haritaları
│
├── Projects/                  # Ajanların Trello üzerinden ürettiği kod projeleri
│
├── monitor/                   # Rapor ve Log Dashboard izleme web arabirimi
│
├── generated_reports/         # Berqun analizleriyle oluşturulan çalışan verimlilik Excel'leri
│
├── api/ / backend_api.py      # Aracı backend servisleri, Flask UI entegrasyonları
│
├── generate_combined_reports.py # Berqun Aylık/Genel Rapor Otonom Scripti
├── generate_weekly_reports.py   # Berqun Haftalık Rapor Otonom Scripti
├── mail_listener.py             # E-mail dinleme ve mail bazlı task yönetimi
├── mail_sender.py               # Otomatik Mail bildirim (HTML formatlı) servisi
├── trello_orchestrator_v3.py    # Görev yürütme, ajanları çağırma ve Trello durum güncellemeleri
├── whatsapp_approval_agent.py   # Twilio & WhatsApp ile onay bekleme sunucusu
├── ...
```

---

## 🚀 Projeyi Kurma ve Ayağa Kaldırma Rehberi

Sistemi baştan sonra ayağa kaldırmak için aşağıdaki adımları sırasıyla uygulayın:

### 1. Repoyu Klonlayın
Projeyi bilgisayarınıza indirin ve dizine geçin:
```bash
git clone https://github.com/ahmetercikan/AgentManager.git
cd AgentManager
```

### 2. Sanal Ortam (Virtual Environment) Oluşturun
Proje bağımlılıklarının çakışmasını önlemek için bir sanal ortam oluşturup aktif edin:

**Windows Command Prompt / PowerShell:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin
Tüm ajanların, Trello entegrasyonlarının ve Berqun otomasyonlarının çalışması için paketleri yükleyin:
```bash
pip install -r requirements.txt
```

### 4. Sistem Çevresel Değişkenlerini (Environment Variables) Ayarlayın
Ajanların harici API'lere bağlanabilmesi için bazı anahtarlara ihtiyacı vardır. 
Projenin ana dizininde bir `.env` dosyası oluşturun (eğer yoksa) veya bu değişkenleri sisteminize global olarak ekleyin:

**Önemli Anahtarlar (`.env` dosya örneği):**
```env
OPENAI_API_KEY=your_openai_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_API_KEY=your_trello_api_key
BERQUN_USERNAME=sirket_hesabi
BERQUN_PASSWORD=sifre
BERQUN_TOKEN=berqun_api_token
TWILIO_ACCOUNT_SID=twilio_sid
TWILIO_AUTH_TOKEN=twilio_token
WHATSAPP_TO_NUMBER=whatsapp_receiver
```
*(GitHub'a gizli anahtarlarınız sızmasın diye projede şuan secret key taraması yapılmıştır. Kendi keylerinizi local inizde yerleştirin.)*

### 3. Kullanım Modları (Nasıl Başlatılır?)

#### A) Trello Otonom AI Ekibini Çalıştırmak
Siz sadece Trello tahtasına (Board) görev kartları eklersiniz, gerisini **Orchestrator V3** halleder. AI sizin için kodu, tasarımı ve gereksinimleri çıkartarak Trello kartını tamamlar.
```bash
python trello_orchestrator_v3.py
```

#### B) E-Posta Dinleyici ve Destek Temsilcisini Çalıştırmak
Gelen e-postaları 15 saniyede bir dinleyerek rapor gönderen veya sorunu çözen otonom arka plan servisi.
```bash
python mail_listener.py
```

#### C) WhatsApp Onay Servisi
Eğer maliyet onayına tabı bir Orchestrator işlemi gerçekleşirse:
```bash
python whatsapp_approval_agent.py
```

#### D) Berqun Raporlarını Manuel / Cron ile Çalıştırmak
Şirket geneli haftalık veya aylık verimlilik excel ve paketlerini toplu üretmek için:
```bash
# Sadece haftalık ve belirli ekipler için:
python generate_weekly_reports.py

# Şirket geneli (Aylık birleştirilmiş / Tüm Şube):
python generate_combined_reports.py
```

---

## 🎨 Yeni Proje Tasarlatmak

Bir Trello Kartı içerisine örneğin şu açıklamayı girdiğinizde:

> **Başlık:** E-Ticaret Arama Ekranı
> **Açıklama:** "Bana bir E-ticaret platformu için güzel, Glassmorphism temalı, filtrelemeli temiz bir React sayfası tasarla ve API'sini python ile yaz."

Sistem aşağıdaki işlemleri **hiçbir insan müdahalesi olmadan** yapar:
1. Kart üzerinden gereksinimleri anlar (Fullstack olarak işaretler)
2. WhatsApp üzerinden *"Projeye başlıyorum onaylıyor musun?"* diye size sorar.
3. Devreye giren **Frontend Design Pro** ajanı, sıfırdan `Vite + TailwindCSS + React` ortamını `Projects/Eticaret_Sayfasi` hedefine kurar ve tasarlar.
4. Devreye giren **Backend Developer** ajanı, `backend/` klasörüne REST kurallarında Python API kodunu bırakır.
5. Görevi "Teste Hazır" durumuna alır.

---

## 🔐 Güvenlik ve Uyarılar
- Tüm token ve API keyleri **sistem değişkenlerinden (`os.environ`)** çekilmelidir. Asla kod içerisinde bırakmayın.
- AI ajanlarının projelerinize uyguladığı refactor veya sistem komutları (`run_command`) her zaman denetime tabidir. Ancak üretim (production) sunucularında doğrudan root çalıştırılmamalıdır.
- `generated_reports`, `Projects/` gibi ajan çıktılarının bulunduğu büyük klasörler repoya gönderilmesin diye `.gitignore` ile korunmaktadır.

---

**AI Agent Manager & Orchestrator Projesi** size sadece bir asistanlık yapmaz; bir departman gibi otonom olarak yaşar, kod üretir, sorunlara cevap verir ve takımları yönetir.

*Happy Automating! 🚀🤖*
