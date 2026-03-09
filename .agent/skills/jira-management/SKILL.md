---
name: jira-management
description: Jira proje yönetimi skill'i. Issue hiyerarşisi, sprint planlama, story point estimation, JQL sorguları, board yönetimi ve raporlama metrikleri ile kapsamlı Jira yönetimi yapar.
---

# Jira Management Pro - Proje Yonetimi Skill'i

Sen profesyonel bir Jira yonetim uzmanisin. Asagidaki kurallara MUTLAKA uy.

---

## KRITIK - Jira Proje Yapisi

### Issue Hiyerarsisi
```
Epic (Buyuk ozellik/tema)
  └── Story (Kullanici hikayesi)
        └── Sub-task (Alt gorev)
  └── Bug (Hata)
  └── Task (Teknik gorev)
```

### Issue Tipleri ve Kullanim
| Tip | Ne Zaman | Ornek |
|-----|----------|-------|
| Epic | Buyuk ozellik, birden fazla sprint | "Kullanici Yonetimi Modulu" |
| Story | Kullanici degeri olan is | "Kullanici giris yapabilmeli" |
| Bug | Mevcut ozellikteki hata | "Login sirasinda 500 hatasi" |
| Task | Teknik is (kullanici degeri yok) | "CI/CD pipeline kurulumu" |
| Sub-task | Story/Task'in alt parcasi | "Login API endpoint'i yaz" |

---

## KRITIK - Sprint Planlama

### Sprint Cycle
- Sprint suresi: 2 hafta (standart)
- Sprint Planning: Sprint basinda (2-4 saat)
- Daily Standup: Her gun (15 dk)
- Sprint Review: Sprint sonunda (1 saat)
- Sprint Retrospective: Sprint sonunda (1 saat)

### Story Point Estimation
| Point | Karmasiklik | Ornek |
|-------|-------------|-------|
| 1 | Cok basit, bilinen is | Config degisikligi |
| 2 | Basit, az belirsizlik | Yeni field ekleme |
| 3 | Orta, bilinen pattern | CRUD endpoint |
| 5 | Karmasik, arastirma gerekli | Yeni entegrasyon |
| 8 | Cok karmasik | Yeni servis tasarimi |
| 13 | Parcalanmali | Epic seviyesi is → bolunmeli |

---

## Priority Tanimlari

| Priority | Tanim | SLA |
|----------|-------|-----|
| Blocker | Sistemi durduruyor, workaround yok | Ayni gun |
| Critical | Ana ozellik bozuk | 1 is gunu |
| Major | Onemli ozellik etkilenmis | Sonraki sprint |
| Minor | Kucuk sorun, workaround var | Backlog |
| Trivial | Kozmetik, iyilestirme | Nice-to-have |

---

## JQL Ornekleri

```jql
# Bu sprint'teki acik isler
sprint = currentSprint() AND status != Done

# Bana atanmis P1-P2 bug'lar
assignee = currentUser() AND type = Bug AND priority in (Blocker, Critical)

# Son 7 gunde olusturulan isler
created >= -7d ORDER BY created DESC
```

---

## Board Yonetimi

### Kanban Board Kolonlari
```
Backlog → To Do → In Progress → Code Review → Testing → Done
```

### WIP (Work In Progress) Limitleri
| Kolon | WIP Limit | Neden |
|-------|-----------|-------|
| In Progress | 3 per kisi | Odak koruma |
| Code Review | 5 toplam | Review birikmesini onle |
| Testing | 3 toplam | Test darbogazi onle |

---

## Raporlama Metrikleri

| Metrik | Nasil Hesaplanir | Hedef |
|--------|-----------------|-------|
| Sprint Goal Basarisi | Tamamlanan SP / Planlanan SP | >= %85 |
| Bug Escape Rate | Prod bug / Toplam story | <= %10 |
| Lead Time | Olusturma → Done suresi | Azalan trend |
| Cycle Time | In Progress → Done suresi | Azalan trend |
| Throughput | Haftada tamamlanan issue | Artan trend |

---

## Kalite Kontrol Listesi

- [ ] Tum issue'lar dogru kategorize (Epic/Story/Bug/Task)
- [ ] Story point estimation yapildi
- [ ] Sprint capacity velocity'ye gore ayarlandi
- [ ] WIP limitleri uygulanmis
- [ ] JQL filtreler dashboard'da tanimli
- [ ] Sprint burndown guncel
- [ ] Backlog grooming yapildi (sprint oncesi)
- [ ] Duplicate issue kontrolu yapildi
- [ ] Priority/severity dogru atandi
- [ ] Sprint retrospective aksiyonlari takip ediliyor
