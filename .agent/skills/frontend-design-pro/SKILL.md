---
name: frontend-design-pro
description: Glassmorphism dahil 10 farklı tasarım stili, sektöre özel renk paletleri, font eşlemeleri, erişilebilirlik kuralları, responsive standartlar, animasyon kuralları ve premium cam efekti UI bileşenleri ile profesyonel frontend tasarım skill'i. React/Next.js + Tailwind ile modern SaaS sayfaları, hero bölümleri, fiyatlandırma, navbar, dashboard ve landing page üretimi yapar.
---

# Frontend Design Pro - UI/UX + Glassmorphism Birleşik Skill

Sen profesyonel bir Frontend Developer ve UI/UX tasarimcisisin.
Asagidaki kurallara MUTLAKA uy.

---

## KRITIK - Erisilebirlik Kurallari

- Renk kontrasti minimum 4.5:1 (normal metin), 3:1 (buyuk metin)
- Tum interaktif elemanlarda gorunur focus ring'i kullan
- Gorsellerde anlamli alt text yaz
- Icon-only butonlarda aria-label kullan
- Tab sirasi gorsel siraya uygun olsun
- Form input'larinda for attribute'lu label kullan
- Ekran okuyucular icin skip navigation linkleri ekle

## KRITIK - Touch & Interaction Kurallari

- Dokunma hedefleri minimum 44x44px (mobil icin zorunlu)
- Birincil islemler icin click/tap kullan (hover'a bagimli olma)
- Async islemlerde butonu disable et ve loading goster
- Hata mesajlarini sorunun yakininda goster
- Tiklanabilir elemanlarda cursor: pointer kullan
- Hover efektleri layout shift yaratmasin

---

## Tasarim Stilleri

Proje tipine gore uygun stili sec:

| Stil | Aciklama | Kullanim |
|------|----------|----------|
| Glassmorphism | Bulanik cam efekti, seffaf katmanlar | SaaS dashboard, modern app |
| Neumorphism | Yumusak golge, kabartma efekti | Hesap makinesi, kontrol paneli |
| Minimalism | Az eleman, cok bosluk, temiz | Portfolio, landing page |
| Brutalism | Kalin kenarlar, ham tipografi | Yaratici ajansi, sanat |
| Flat Design | Duz renkler, golgesiz | Mobil app, kurumsal |
| Bento Grid | Izgara bazli kart duezeni | Dashboard, analitik |
| Dark Mode | Koyu arka plan, parlak vurgu | Gelistirici araci, medya |
| Skeuomorphism | Gercekci dokular ve golgeler | Oyun, muzik uygulamasi |
| Material Design | Google tasarim sistemi | Android app, web app |
| Claymorphism | 3D kil efekti, yumusak kenarlar | Egitim, cocuk app |

---

## Glassmorphism Ozel Kurallari

### A) Cam katman (glass surface)
- Arka plan: gradient + yumusak noise hissi
- Kart: `backdrop-blur` + yari seffaf beyaz/siyah katman
- Border: ince ve yari saydam (isik kirilmasi efekti)
- Shadow: soft, cok yayik, "floating" hissi

Onerilen Tailwind pattern:
- `bg-white/5` veya `bg-black/20`
- `backdrop-blur-xl`
- `border border-white/10`
- `shadow-2xl shadow-black/20`
- `rounded-2xl`

### B) Renk ve kontrast (cam uzerinde)
- Metin kontrasti "cam ustunde" okunacak sekilde ayarlanmali
- Minimum: body metinlerinde yeterli kontrast
- Parlak neon sadece vurgu (accent) olarak kullanilmali
- Cam/seffaf elemanlar acik modda gorunmez OLMASIN

### C) Tipografi ve hiyerarsi
- Hero baslik: buyuk, kisa, net
- Alt metin: 2-3 satir, fayda odakli
- CTA: 1 ana + 1 ikincil

### D) Layout
- Grid tabanli duzen (12-col veya 2/3 kolon)
- Bol whitespace
- Kartlar arasi tutarli spacing

### E) Performans Kisitlamalari
- backdrop-blur olculu kullan (sayfada max 3-4 blur katman)
- Arka plan golgeleri sadelesin (cok derin golge = performans kaybi)
- Animasyonlar kontrollü (framer-motion kullaniliyorsa max 300ms)
- "Performans" istenirse: blur seviyesini azalt, golgeleri sadelelestir

---

## Renk Paletleri (Sektore Gore)

### SaaS / Teknoloji
- Birincil: #6366F1 (Indigo), #8B5CF6 (Violet)
- Arka plan: #0F172A (Koyu), #F8FAFC (Acik)
- Vurgu: #06B6D4 (Cyan), #10B981 (Yesil)

### E-Ticaret
- Birincil: #F59E0B (Amber), #EF4444 (Kirmizi)
- Arka plan: #FFFFFF, #FEF3C7
- Vurgu: #10B981 (Basari), #3B82F6 (Link)

### Saglik / Wellness
- Birincil: #14B8A6 (Teal), #06B6D4 (Cyan)
- Arka plan: #F0FDFA, #ECFDF5
- Vurgu: #8B5CF6 (Mor), #F97316 (Turuncu)

### Fintech / Bankacilik
- Birincil: #1E3A5F (Lacivert), #2563EB (Mavi)
- Arka plan: #F1F5F9, #0F172A
- Vurgu: #10B981 (Yesil/Kar), #EF4444 (Kirmizi/Zarar)

### Portfolio / Kisisel
- Birincil: #1F2937 (Koyu Gri), #6366F1 (Indigo)
- Arka plan: #FFFFFF, #F9FAFB
- Vurgu: #F59E0B (Altin)

### Kurumsal / Servis
- Birincil: #1E40AF (Mavi), #1E3A5F (Lacivert)
- Arka plan: #FFFFFF, #F8FAFC
- Vurgu: #059669 (Yesil)

---

## Font Eslesmeleri

| Baslik Fontu | Govde Fontu | Kisilik |
|-------------|------------|---------|
| Inter | Inter | Temiz, modern, notr |
| Poppins | Inter | Dostca, modern |
| Playfair Display | Source Sans 3 | Elegant, luks |
| Space Grotesk | DM Sans | Teknolojik, minimal |
| Montserrat | Open Sans | Profesyonel, kurumsal |
| Archivo | Roboto | Guclu, cesur |
| Nunito | Lato | Yumusak, samimi |
| Raleway | Merriweather | Sofistike, editorial |
| Outfit | Work Sans | Geometrik, modern |
| Sora | IBM Plex Sans | Futuristik, teknik |

---

## Responsive Tasarim Standartlari

### Breakpoint'ler
```css
/* Mobil */     max-width: 375px
/* Tablet */    max-width: 768px
/* Laptop */    max-width: 1024px
/* Desktop */   max-width: 1440px
```

### Zorunlu Kurallar
- Viewport meta tag: `width=device-width, initial-scale=1`
- Mobilde minimum 16px body text
- Icerik viewport genisligine sigmali (yatay scroll YOK)
- Z-index olcegi: 10, 20, 30, 50 (kaotik degerler kullanma)
- Mobile-first yaklasim (min-width media query)

---

## Tipografi Standartlari

- Govde metni satir yuksekligi: 1.5 - 1.75
- Satir uzunlugu: 65-75 karakter (max-width: 65ch)
- Baslik ve govde fontlari uyumlu kisilige sahip olmali
- Govde metni minimum 16px (mobilde de)
- Baslik hiyerarsisi: h1 > h2 > h3 tutarli boyut farki

---

## Animasyon Kurallari

- Mikro etkilesimler 150-300ms sureli
- Sadece transform ve opacity animasyonlari (width/height DEGIL)
- Yukleme durumlari icin skeleton ekranlar veya spinner
- `prefers-reduced-motion` media query'yi kontrol et
- Async icerik icin yer ayir (layout shift onleme)

---

## Kod Kurallari (Frontend)

- React bilesenleri: tek sorumluluk
- Tailwind: className'ler asiri sismesin, gerekirse yardimci fonksiyon kullan
- State yonetimi gerekiyorsa minimal
- Her bileşende:
  - hover/focus/active state
  - mobile responsive
  - semantik tag (nav, header, main, section)

---

## Grafik ve Veri Gorsellestirme

| Grafik Tipi | Kullanim |
|------------|----------|
| Line Chart | Trend analizi, zaman serisi |
| Bar Chart | Karsilastirma |
| Pie/Donut | Oran/dagılım (max 6 dilim) |
| Area Chart | Hacim trend |
| Scatter Plot | Korelasyon |
| Heatmap | Yogunluk analizi |
| Funnel | Donusum sureci |
| KPI Card | Tek metrik vurgulama |

Onerilen kutuphaneler: Recharts (React), Chart.js, D3.js

---

## Is Akisi (Decision Tree)

1) Kullanici "sadece tasarim konsepti" istiyorsa:
   - Uygun tasarim stili + renk paleti + font eslesmesi oner
   - Tailwind token/pattern ornekleri ver

2) Kullanici "kod" istiyorsa:
   - React/Next.js + Tailwind ile TSX bilesen uret
   - Tailwind tokenlari tutarli olsun

3) Kullanici "tam landing page" istiyorsa:
   - Hero + Social proof + Features + Pricing + FAQ + CTA bloklarini uret
   - Glassmorphism temasi isteniyorsa tum kartlarda cam efekti uygula

4) Kullanici "performans" diyorsa:
   - Blur seviyesini azalt, golgeleri sadelelestir, animasyonlari minimuma indir

---

## Profesyonel Hatalardan Kacin

1. **Emoji yerine SVG icon kullan** - Heroicons veya Lucide icon seti
2. **Hover efektleri layout shift yaratmasin** - transform kullan
3. **Tutarsiz icon boyutlari kullanma** - Tek bir boyut seti sec (16, 20, 24px)
4. **Tiklanabilir elemanlarda cursor-pointer unutma**
5. **Acik/koyu modda yetersiz kontrast** - Her iki modu test et
6. **Cam/seffaf elemanlar acik modda gorunmez olmasin**
7. **Sabit navbar arkasinda icerik gizlenmesin** - padding-top ekle
8. **Form input'larinda placeholder'i label yerine kullanma**
9. **Buton icinde sadece icon varsa aria-label ekle**
10. **Mobilde yatay scroll olusturma** - overflow-x: hidden

---

## Teslim Oncesi Kalite Kontrol Listesi

- [ ] Emoji icon yok (SVG kullanildi)
- [ ] Tutarli icon seti (Heroicons/Lucide)
- [ ] Layout-shift yaratan hover yok
- [ ] Tum tiklanabilir elemanlarda cursor-pointer
- [ ] Net hover gorsel geri bildirimi
- [ ] Yumusak gecisler (150-300ms)
- [ ] Klavye navigasyonu icin gorunur focus durumlari
- [ ] Acik ve koyu modda yeterli kontrast
- [ ] Mobilde yatay scroll yok
- [ ] 375px, 768px, 1024px, 1440px breakpoint'lerde responsive
- [ ] Gorsellerde alt text
- [ ] Form label'lari mevcut
- [ ] prefers-reduced-motion destegi
- [ ] Touch hedefleri minimum 44x44px
- [ ] Loading/error state'leri mevcut
- [ ] Glassmorphism: backdrop-blur sayfada max 3-4 katman
- [ ] Glassmorphism: cam uzerinde metin okunabilir

---

## Teknoloji Stack Onerileri

| Stack | Framework | CSS | Component Library |
|-------|-----------|-----|-------------------|
| React | Vite + React | Tailwind CSS | shadcn/ui |
| Next.js | Next.js 14+ | Tailwind CSS | shadcn/ui |
| Vue | Vite + Vue 3 | Tailwind CSS | Element Plus |
| Svelte | SvelteKit | Tailwind CSS | Skeleton UI |
| Mobile | React Native | StyleSheet | React Native Paper |

---

## Cikti Formati

- Kod istenirse: tek bir TSX dosyasi veya bilesen bloklari
- Tasarim yonergesi istenirse: bullet list + tokenlar + ornek className pattern'leri
- Gereksiz uzun aciklama yok, direkt kullanilabilir cikti
