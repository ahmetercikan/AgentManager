# Trello Orchestrator - Kullanım Rehberi

## 🎯 Ne Yapar?

Trello Orchestrator, Trello Backlog listesini **sürekli izler** ve yeni kart eklediğinizde otomatik olarak AI ajanlarını çalıştırır.

## 🔄 İş Akışı

```
1. Sen Trello'da Backlog'a kart eklersin
         ↓
2. Orchestrator 30 saniyede bir kontrol eder
         ↓
3. Yeni kart bulunca → Kartı "In Progress" taşır
         ↓
4. ANALIST AGENT analiz eder
   - Proje adını belirler
   - Gereksinimleri çıkarır
   - Programlama dilini seçer
   - Dosya adını belirler
         ↓
5. ORCHESTRATOR işi dağıtır
   - PM: Proje planı yapar
   - Developer: Kod yazar
   - QA: Test eder
         ↓
6. Kod dosyaya yazılır
         ↓
7. Kart "Done" listesine taşınır
         ↓
8. Tüm sonuçlar karta yorum olarak eklenir
```

---

## 🚀 Nasıl Çalıştırılır?

### Adım 1: Orchestrator'ı Başlat

```bash
python trello_orchestrator.py
```

### Adım 2: Board Seç

Program size board'larınızı listeleyecek:

```
📋 Mevcut Board'lariniz:
1. Test Architecture (abc123)
2. AI Agents - Hello World App (xyz789)

0. Yeni board olustur

Hangi board'u izlemek istersiniz? (numara girin):
```

Bir board seçin veya yeni board oluşturun.

### Adım 3: Backlog'a Kart Ekle

Trello'yu aç ve seçtiğiniz board'un **Backlog** listesine kart ekle:

#### Örnek Kart 1: Basit

**Başlık:**
```
Snake Oyunu Yaz
```

**Açıklama:**
```
Pygame ile klasik yılan oyunu.
Ok tuşlarıyla hareket, yem yeme, büyüme.
```

#### Örnek Kart 2: Detaylı

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

#### Örnek Kart 3: Farklı Dil

**Başlık:**
```
Discord Bot - Basit Komutlar
```

**Açıklama:**
```
Python discord.py ile bot:
- !ping komutu
- !help komutu
- !echo komutu
- !roll (zar at)
```

### Adım 4: İzle

Orchestrator konsola şunu yazdıracak:

```
🔍 Backlog izleniyor...
(Ctrl+C ile durdurun)

⏳ 30 saniye bekleniyor...
```

Yeni kart eklediğinizde:

```
🆕 Yeni kart bulundu: Snake Oyunu Yaz

📋 YENİ İŞ BULUNDU: Snake Oyunu Yaz
============================================================
Aciklama: Pygame ile klasik yılan oyunu...

🔍 ANALIST AGENT - Kart analiz ediliyor...
...
```

---

## 📊 Trello'da Neler Oluyor?

### 1. Kart "In Progress" Listesine Taşınır

İlk yorum eklenir:
```
🤖 Orchestrator ise basladi. Analist analiz yapiyor...
```

### 2. Analist Raporu Eklenir

```
📊 ANALIST RAPORU:

{
    "project_name": "Snake Game",
    "description": "Pygame ile klasik yilan oyunu",
    "programming_language": "Python",
    "file_name": "snake_game.py",
    "requirements": [
        "Pygame kullan",
        "Ok tuslariyla hareket",
        "Yem yeme ve buyume",
        "Duvara carpma - Game Over"
    ]
}
```

### 3. Kod Yazıldığında Yorum

```
✅ KOD YAZILDI: snake_game.py

Kod dosyaya kaydedildi.
```

### 4. Test Raporu Eklenir

```
📋 TEST RAPORU:

Test Senaryolari:
1. TS-001: Yilan hareketi
2. TS-002: Yem yeme
...
```

### 5. Kart "Done" Listesine Taşınır

Son yorum:
```
✅ IS TAMAMLANDI! Tum adimlar basariyla tamamlandi.
```

---

## 💡 Kullanım İpuçları

### Kart Başlığı

- **Kısa ve açık** olsun
- Ne yapılacağını belirt
- Örnek: "Todo List CLI", "Web API", "Discord Bot"

### Kart Açıklaması

- **Detaylı gereksinimler** yaz
- Hangi teknolojilerin kullanılacağını belirt
- Özellikler listele

**İYİ ÖRNEK:**
```
Başlık: Password Generator CLI

Açıklama:
Python ile şifre üretici araç:
- Şifre uzunluğu parametresi
- Büyük/küçük harf, rakam, özel karakter seçenekleri
- Birden fazla şifre üret
- Şifre gücü göstergesi
- Argparse kullan
```

**KÖTÜ ÖRNEK:**
```
Başlık: Bir şey yap

Açıklama: Kod yaz
```

### Programlama Dili Belirtme

Açıklamada dili belirtin:

- ✅ "Python ile..."
- ✅ "JavaScript/Node.js kullanarak..."
- ✅ "Java ile konsol uygulaması..."

Belirtmezseniz Analist genelde Python seçer.

---

## 🛑 Orchestrator'ı Durdurma

Konsol penceresinde `Ctrl+C` tuşlarına basın:

```
🛑 Orchestrator durduruldu.
```

---

## ⚙️ Ayarlar

### Kontrol Aralığını Değiştir

[trello_orchestrator.py](trello_orchestrator.py) dosyasında:

```python
def run_orchestrator(board_id: str, check_interval: int = 30):
    #                                              ^^
    # Varsayılan: 30 saniye
```

Daha sık kontrol için:
```python
check_interval: int = 10  # 10 saniye
```

Daha az kontrol için:
```python
check_interval: int = 60  # 1 dakika
```

---

## 🔧 Sorun Giderme

### "Backlog listesi bulunamadı"

Board'da "Backlog" adında liste yoksa bu hatayı alırsınız.

**Çözüm 1:** Trello'da manuel olarak "Backlog" listesi oluşturun.

**Çözüm 2:** Yeni board oluşturun (Orchestrator otomatik listeler ekler).

### "Analist çıktısı parse edilemedi"

Analist beklenmedik format döndürmüş olabilir.

**Çözüm:** Kart açıklamasını daha detaylı yazın. Gereksinimleri madde madde listeleyin.

### Kod dosyası oluşturulmadı

Developer kod bloğu içinde kod vermemiş olabilir.

**Kontrol:** Trello'daki yorumlara bakın. Kod orada olmalı.

### Orchestrator çok yavaş

`check_interval` değerini azaltın (yukarıya bakın).

---

## 📚 Örnek Senaryolar

### Senaryo 1: Oyun Geliştirme

**Trello Kartı:**
```
Başlık: Tetris Oyunu

Açıklama:
Pygame ile Tetris:
- 7 farklı şekil
- Tuşlarla hareket (ok tuşları)
- Satır tamamlama ve puan
- Hız artışı
- Game Over ekranı
```

**Beklenen Sonuç:**
- `tetris_game.py` dosyası oluşturulur
- Çalışır Tetris oyunu
- Test senaryoları Trello'da

### Senaryo 2: Web Geliştirme

**Trello Kartı:**
```
Başlık: Blog REST API

Açıklama:
FastAPI ile blog API:
- Makale CRUD
- Kullanıcı authentication
- Yorum sistemi
- Kategori/tag
- Pagination
- SQLAlchemy + SQLite
```

**Beklenen Sonuç:**
- `blog_api.py` dosyası
- Çalışır REST API
- OpenAPI documentation

### Senaryo 3: CLI Araç

**Trello Kartı:**
```
Başlık: File Converter - JSON to CSV

Açıklama:
Python ile dönüştürücü:
- JSON dosyası oku
- CSV'ye çevir
- Nested JSON desteği
- Batch processing
- Argparse ile CLI
```

**Beklenen Sonuç:**
- `json_to_csv.py` dosyası
- Komut satırı aracı
- Kullanım örnekleri

---

## 🎯 Sonraki Adımlar

1. **Orchestrator'ı arka planda çalıştır:**
   ```bash
   nohup python trello_orchestrator.py &
   ```

2. **Webhook ekle:** Trello webhook'ları ile gerçek zamanlı bildirim

3. **Slack entegrasyonu:** İşler tamamlandığında Slack'e mesaj

4. **E-posta bildirimleri:** İş bitince mail gönder

---

## 📞 Yardım

Sorun mu yaşıyorsunuz?

1. Konsol çıktısını kontrol edin
2. Trello'daki yorumlara bakın
3. Kart açıklamalarını daha detaylı yazın

---

**Hazır mısınız? Orchestrator'ı başlatın ve Backlog'a iş ekleyin! 🚀**

```bash
python trello_orchestrator.py
```
