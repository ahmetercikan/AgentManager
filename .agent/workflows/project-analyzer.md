---
description: project-analyzer
---

# Proje Analizi ve Stratejik Geliştirme Skill'i

Bu skill, ajanın bir projeyi uçtan uca incelemesini, zayıf noktaları tespit etmesini ve uygulanabilir geliştirme önerileri sunmasını sağlar.

## Kullanım Senaryoları
- Yeni bir repoyu anlamlandırma.
- Mevcut projenin mimari ve işlevsel eksiklerini bulma.
- Brainstorming seansları için yapılandırılmış geri bildirim alma.

## Analiz Protokolü (İş Akışı)
Ajan, projeyi şu adımlarla incelemelidir:

1. **Kapsam Keşfi:** `README.md`, `package.json` veya ana yapılandırma dosyalarını inceleyerek projenin amacını belirle.
2. **Mimari İnceleme:** Dosya yapısını ve kullanılan teknolojileri (stack) analiz et.
3. **Kod Kalitesi ve Güvenlik:** Potansiyel bug'ları, performans darboğazlarını ve güvenlik açıklarını tara.
4. **Geliştirme Önerileri:** Aşağıdaki kategorilerde en az 3'er öneri sun:
    - **Teknik İyileştirme:** (Refactoring, performans, yeni kütüphaneler)
    - **Kullanıcı Deneyimi (UX):** (Eksik özellikler, akış iyileştirmeleri)
    - **Sürdürülebilirlik:** (Dokümantasyon, test kapsamı, CI/CD)

## Çıktı Formatı
Analiz sonuçlarını her zaman şu başlıklarla sun:
### 🎯 Proje Özeti
### 🔍 Kritik Bulgular
### 🚀 Geliştirme Önerileri (Kısa, Orta ve Uzun Vade)
### 💡 Brainstorming: "Peki ya şöyle olsaydı?" (Yaratıcı fikirler)