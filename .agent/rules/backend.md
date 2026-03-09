

# Backend Workspace Rules

Activation: Always On

Bu dosya, bu workspace içindeki tüm backend çalışmalarında
Agent'ın uyması gereken proje özel kuralları tanımlar.

---

## 1. Kullanılacak Teknoloji Stack'i

- Python 3.10+ zorunludur
- CrewAI framework ile agent orkestrasyon yapılır
- OpenAI GPT modelleri kullanılır (varsayılan: gpt-4o-mini)
- Trello API entegrasyonu için `trello_helper.py` modülü kullanılır
- API geliştirmelerinde FastAPI tercih edilir
- Harici framework KULLANILMAZ (Django, Flask vb.)
  (Kart açıklamasında belirtilmişse hariçtir)

---

## 2. Proje Yapısı Kuralları

- Her yeni özellik ayrı Python dosyasında olmalıdır
- Monolith-first yaklaşım: Karmaşıklık eklenmeden büyütme yapılmaz
- Skill dosyaları `.agent/skills/` altında SKILL.md formatıyla tanımlanır
- Rule dosyaları `.agent/rules/` altında tutulur
- Tamamlanan projeler `Projects/{proje_adı}/` dizinine yazılır (Bkz. Kural 12)
- Raporlar `generated_reports/` altına yazılır
- `__pycache__` ve `venv` klasörleri VCS dışında tutulur

---

## 3. Agent Geliştirme Kuralları

- Her agent CrewAI `Agent` sınıfı ile oluşturulur
- Agent'lar `Agent(role, goal, backstory, llm)` yapısını kullanır
- `allow_delegation=False` varsayılandır (açıkça istenmedikçe)
- `verbose=False` production'da, `verbose=True` geliştirmede kullanılır
- Task'lar `Task(description, agent, expected_output, context)` ile tanımlanır
- Crew iş akışı varsayılan olarak `Process.sequential` kullanır
- Her agent'a uygun `.agent/skills/` altındaki SKILL.md enjekte edilir
- Agent backstory'sine skill içeriği f-string ile eklenir

---

## 4. Skill Yükleme Standartları

- Skill'ler `.agent/skills/{skill_name}/SKILL.md` yolundan yüklenir
- Eski `skills/` klasörü KULLANILMAZ
- `load_skill()` fonksiyonu `.agent/skills/` dizininden okur
- Her skill YAML frontmatter (name, description) içermelidir
- Skill bulunamazsa uyarı loglanır, hata fırlatılmaz

---

## 5. Trello Entegrasyon Kuralları

- Kart iş akışı: `Backlog → In Progress → Code Review → Testing → Done`
- Her geçişte `trello.move_card()` çağrılmalıdır
- Her kritik adımda `trello.add_comment()` ile log bırakılır
- Bug'lar ayrı kartlar olarak `Bugs` listesine oluşturulur
- Kart parse edilemezse kartın üstüne hata yorumu yazılır ve `return False`

---

## 6. Güvenlik Kuralları

- API key'ler ve token'lar `.env` dosyasından okunmalıdır
- Hardcoded credential YASAKTIR (mevcut kodda uyarıdır, yeni kodda KABUL EDİLMEZ)
- `os.environ` üzerinden environment variable kullanılır
- Hassas veriler loglara yazılmaz

---

## 7. Hata Yönetimi

- Tüm dış API çağrıları `try-except` içinde olmalıdır
- Trello API hatalarında kart üzerine hata bilgisi yazılır
- Windows encoding sorunları için `sys.stdout/stderr` UTF-8 olarak wrap edilir
- Windows'ta eksik signal'lar (`SIGHUP`, `SIGQUIT` vb.) stub olarak tanımlanır

---

## 8. Dashboard Entegrasyonu

- `update_dashboard()` ile agent durumu, task, proje ve step bilgisi gönderilir
- Dashboard çalışmıyorsa hata sessizce görmezden gelinir (`except: pass`)
- Her kritik adımda dashboard güncellemesi yapılır

---

## 9. Kod Çıktı Kuralları

- AI tarafından üretilen kodlar mutlaka markdown code block içinde olmalıdır
- Kod çıkarma işlemi `extract_code()` fonksiyonu ile yapılır
- Üretilen dosyalar UTF-8 encoding ile kaydedilir
- Kod istatistikleri (satır, boyut, dil) loglanır ve Trello'ya yazılır

---

## 10. Scope Disiplini

Agent:
- Bu dosyada tanımlı olmayan ek teknoloji öneremez
- Kapsam dışı refactor yapamaz
- "İstersen bunu da yapabilirim" önerisinde bulunamaz

SADECE istenen görevi yerine getirir.

---

## 11. Belirsizlik Durumu

Eğer:
- İstek eksikse
- Çelişkili bir durum varsa

Agent:
1. DURUR
2. NETLEŞTİRME SORAR
3. Cevap gelene kadar ilerlemez

---

## 12. Proje Çıktı Dizini Kuralları

Backlog'dan gelen bir proje talebi tamamlandığında,
tüm proje dosyaları `ai_ajanlar -jira-ent` kök dizini altındaki
**`Projects/` dizinine** proje adıyla bir klasör olarak yazılır.

### Dizin Yapısı
```
ai_ajanlar -jira-ent/
├── Projects/
│   ├── ProjeAdi_1/
│   │   ├── main.py
│   │   ├── requirements.txt   (varsa)
│   │   └── README.md          (varsa)
│   ├── ProjeAdi_2/
│   │   ├── backend_api.py
│   │   ├── App.jsx
│   │   └── styles.css
│   └── ...
├── trello_orchestrator_v3.py
├── .agent/
└── ...
```

### Kurallar
- Proje klasör adı `project_name` alanından türetilir
- Klasör adında boşluklar `_` (alt çizgi) ile değiştirilir
- Özel karakterler kaldırılır (sadece alfanümerik ve `_` `-`)
- `Projects/` dizini yoksa otomatik oluşturulur
- Her proje kendi alt klasörüne yazılır, dosyalar kök dizine DAĞITILMAZ
- Fullstack projelerde backend ve frontend dosyaları aynı proje klasöründe tutulur
- Aynı isimde klasör varsa sonuna `_v2`, `_v3` gibi versiyon eki eklenir
- Tamamlanan projenin dizin yolu Trello kartına yorum olarak yazılır

---

Bu kuralların ihlali, proje standartlarının ihlali sayılır.
