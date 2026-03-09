# Servis Masası — SLA Tanımları

## Incident Öncelik Seviyeleri

| Öncelik | Tanım | Yanıt Süresi | Çözüm Süresi |
|---------|-------|-------------|-------------|
| **P1 - Kritik** | Tüm kullanıcıları etkileyen, iş durması | [15 dk] | [4 saat] |
| **P2 - Yüksek** | Çoğu kullanıcıyı etkileyen, ciddi performans kaybı | [30 dk] | [8 saat] |
| **P3 - Orta** | Sınırlı kullanıcı etkilenen, geçici çözüm mevcut | [2 saat] | [24 saat] |
| **P4 - Düşük** | Tek kullanıcı, düşük etki | [4 saat] | [72 saat] |

## Escalation Kuralları
- P1: Derhal L2'ye escalate, 30 dk içinde L3 + Yönetici bilgilendirmesi
- P2: 1 saat içinde çözülemezse L2'ye escalate
- P3: 4 saat içinde çözülemezse L2'ye escalate
- P4: 24 saat içinde çözülemezse L2'ye escalate

## Çalışma Saatleri
- Normal mesai: [09:00 - 18:00]
- 7/24 destek: [Sadece P1-P2 için]
