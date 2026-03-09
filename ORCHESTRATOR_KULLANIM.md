# Trello Orchestrator V3 - Kullanım Rehberi

## 🎯 Ne Yapar?

Trello Orchestrator V3, Trello'daki **Backlog** listesini **sürekli izler** ve tahtaya yeni bir yazılım görevi/kartı eklediğinizde otomatik olarak AI ajanlarını çalıştırır.

Sadece projenin ne olduğunu tanımlarsınız, sistem otomatik olarak projeyi Backend, Frontend veya Fullstack durumuna göre kategorize ederek uygun AI çalışanlarını (Analist, Developer, QA vb.) işe sürer. 

İşlem başlatılmadan önce **WhatsApp Approval Agent** üzerinden size onay mesajı atar. Onay verdiğinizde projeyi sonuna kadar götürüp Trello kartı üzerinde güncellemeler yapar.

## 🔄 İş Akışı

```text
1. Sen Trello'da "Backlog" listesine görev kartı eklersin.
         ↓
2. Orchestrator dinleyicisi kartı bulur.
         ↓
3. Yeni kartı bulduğunda → Kartı "In Progress" listesine alır.
         ↓
4. WhatsApp Approval Agent (Onay Ajani) sana WhatsApp'tan "İşlem Başlasın mı? (Maliyet/Bilgi)" mesajı gönderir.
         ↓
5. Sen WhatsApp'tan ONAY verdiğin an:
         ↓
6. İŞ ANALİSTİ (Analyst Agent) kartı analiz eder:
   - "Bu proje Frontend mi, Backend mi yoksa Fullstack mi?" kararını verir.
   - Mimariyi çıkarır, Trello yorumuna yazar.
         ↓
7. ORCHESTRATOR projeyi ilgili developer'lara verir:
   - Fullstack ise: Önce Backend Agent, sonra Frontend Design Pro Agent çalışır.
   - Sadece Frontend ise: Frontend Design Pro Agent (UI/UX, Tailwind, React) çalışır.
   - Sadece Backend ise: Backend Developer Agent (API, REST, DB) çalışır.
         ↓
8. Kod dosyaları doğrudan projenin altındaki "Projects/{Proje_Adi}" klasörüne kaydedilir!
         ↓
9. QA (Test Uzmanı) Agent devreye girer:
   - Yazılan kodları test eder.
   - Bug/Hata varsa Trello'daki "Bugs" listesine otomatik yeni bir kart oluşturur.
         ↓
10. Ana kart sorunsuz ise "Code Review" veya "Done" listesine taşınır.
```

---

## 🚀 Nasıl Çalıştırılır?

Projedeki otonom AI dev team'i (Orchestrator V3) çalıştırmak için tek bir komut yeterlidir:

```bash
python agent_manager.py
```
*(Bu komutla hem Orchestrator arka planda Backlog'u dinlemeye başlar hem de projenin Frontend / Backend arayüzü aynı anda ayaklanır.)*

---

## 💡 Nasıl Görev Eklerim? (Trello Üzerinden)

Trello board'unuzun **Backlog** listesine şu şekilde kartlar ekleyebilirsiniz:

### Örnek 1: Frontend Ağırlıklı Görev (Glassmorphism Temalı)
**Kart Başlığı:** `Kurumsal SaaS Landing Page`
**Kart Açıklaması:**
```text
React ve Tailwind kullanarak yeni bir bulut dosya depolama ürünü için Landing Page tasarla. 
Koyu (dark) mod ağırlıklı olsun.
Ortada glassmorphism efektli bir "Giriş Yap" kutusu,
Arka planda modern canlı renk gradientları olsun.
```

### Örnek 2: Fullstack E-Ticaret Modülü
**Kart Başlığı:** `E-Ticaret Sepet İşlemleri API ve UI`
**Kart Açıklaması:**
```text
Backend: Python ile ürün listeleme ve sepete ürün ekleme API'si kur.
Frontend: React ve Tailwind ile bu ürünleri listeleyen şık bir arayüz yap.
Sepet ikonu olsun, üzerine tıklayınca sepetteki ürünler listelensin.
Mümkünse modern animasyonlu toast modülleri eklensin.
```

---

## 🛑 Sık Sorulan Sorular / Sorun Giderme

### "Backlog listesi bulunamadı" Hatası
Board'da İngilizce tam adıyla "Backlog" adında bir Trello listesi olduğundan emin olun. Trello'da listeyi manuel olarak "Backlog" isminde oluşturabilirsiniz.

### Ajanlar Projeyi / Kodu Nereye Yazıyor?
Tüm projeler ana dizindeki `Projects/` klasörü altında izole bir şekilde kart ismine özel bir klasör açılarak kaydedilir. Kart başlığı "E-Ticaret" ise dosyalarınız `Projects/E-Ticaret/` içerisinde yer alacaktır. 

### WhatsApp Onayı Gelmiyor
Sistemde `.env` dosyası içinde `TWILIO` değerlerinin ve kendi telefon numaranızın tam olduğundan emin olun. Onay servisi aktif olmazsa ajanlar görevi kabul etmez.

---

**Ajanlarınız siz görev verdiğiniz sürece Trello üzerinden projelerinizi geliştirmeye, analiz etmeye ve test raporları oluşturmaya devam edecektir. Mutlu kodlamalar! 🚀**
