---
description: Glass
---

# Glassmorphism SaaS Landing Page İş Akışı

## Açıklama
Bu iş akışı, agent'ı glassmorphism UI ilkeleriyle premium bir SaaS landing page oluşturma sürecinde yönlendirir.
Tutarlı tasarım, okunabilir kod, duyarlı (responsive) düzen ve performans bilincinde blur kullanımını garanti eder.
Modern frontend landing page'leri oluştururken veya iskelet çıkarırken bu iş akışını kullanın.

---

## Adım 1 — Bağlam & Kapsam Onayı

- Hedef teknolojiyi doğrulayın:
  - React veya Next.js
  - Tailwind CSS mevcut mu
- Sayfa kapsamını doğrulayın:
  - Tam landing page Mİ
  - Belirli bölümler mi (hero, fiyatlandırma vb.)
- Ek gereksinim VARSAYMAYIN.
- Eksik bir detay varsa netleştirme sorusu sorun ve DURUN.

---

## Adım 2 — İlgili Skill'i Etkinleştirme

- UI ve frontend tasarımı için mevcut skill'leri kontrol edin.
- **frontend-glassmorphism** skill'ini etkinleştirin.
- Devam etmeden önce SKILL.md talimatlarının tamamını okuyun.
- Skill'de tanımlanan tasarım tokenlarını, kalıpları ve karar ağacını takip edin.

---

## Adım 3 — Sayfa Yapısı Planlaması

- Üst düzey bir sayfa yapısı önerin:
  - Hero
  - Sosyal kanıt (logolar veya metrikler)
  - Özellikler (3–6 kart)
  - Fiyatlandırma
  - SSS (FAQ)
  - Son CTA
- Yapıyı basit sıralı bir liste olarak sunun.
- Kod üretmeden önce kullanıcı onayını BEKLEYİN.

---

## Adım 4 — Hero Bölümü Oluşturma

- `HeroGlass.tsx` bileşenini oluşturun.
- Gereksinimler:
  - Backdrop blur içeren cam kart
  - Net başlık ve alt metin
  - Birincil + ikincil CTA
  - Mobil uyumlu (responsive)
- Bileşeni bağımsız (self-contained) tutun.
- İlgisiz bileşenler ÜRETMEYİN.

---

## Adım 5 — Özellikler & Fiyatlandırma Bölümleri

- Şunları oluşturun:
  - `FeaturesGlass.tsx` (kart tabanlı grid)
  - `PricingGlass.tsx` (kademeli kartlar)
- Her bölüm:
  - Tutarlı cam yüzey stili kullanmalıdır
  - Boşluk ve okunabilirliğe dikkat etmelidir
  - Aşırı animasyon veya blur kullanmaktan kaçınmalıdır

---

## Adım 6 — Performans & UX Kontrolü

- Oluşturulan bileşenleri şunlar açısından gözden geçirin:
  - Aşırı blur veya ağır gölge kullanımı
  - Metin kontrastı ve okunabilirlik
  - Duyarlı (responsive) davranış
- Sorun bulunursa:
  - Bileşenleri düzeltin
  - Neyin neden değiştirildiğini açıklayın

---

## Adım 7 — Son Çıktı & Özet

- Sunun:
  - Oluşturulan dosyaların listesi
  - Kısa kullanım talimatları
  - İsteğe bağlı sonraki adımlar (açıkça isteğe bağlı olarak işaretlenmiş)
- Açıkça talep EDİLMEDİKÇE refactor veya geliştirme YAPMAYIN.

---

## Tamamlanma Kuralı

- Adım 7'den sonra yürütmeyi durdurun.
- Kapsamı genişletmeyin.
- Ek özellik eklemeyin.
