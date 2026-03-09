# Jira Management — Workflow Kuralları

## Proje Yapılandırma Standartları
- Board tipi: [Scrum / Kanban]
- Sprint süresi: [2 hafta]
- Backlog grooming: [Her Çarşamba]
- Sprint planning: [Pazartesi sabahı]

## Issue Tipleri ve Workflow
| Issue Tipi | Workflow Durumları |
|-----------|-------------------|
| Epic | Open → In Progress → Done |
| Story | To Do → In Progress → Code Review → QA → Done |
| Bug | Open → In Progress → Fixed → Verified → Closed |
| Task | To Do → In Progress → Done |

## Öncelik Tanımları
- **Blocker**: Başka işleri engelleyen, hemen çözülmeli
- **Critical**: Ciddiye alınan, sprint içinde çözülmeli
- **Major**: Normal öncelikli, planlanmış
- **Minor**: Düşük öncelikli, fırsat olduğunda
- **Trivial**: Kozmetik, backlog'da kalabilir

## JQL Şablonları
```
# Sprint içindeki tüm açık issue'lar
sprint in openSprints() AND status != Done

# Bu hafta çözülmesi gereken P1/P2 bug'lar
type = Bug AND priority in (Blocker, Critical) AND sprint in openSprints()

# Bir kişiye atanmış devam eden işler
assignee = [kullanıcı] AND status = "In Progress"
```
