# Berqun API Referansı

## Sunucu
- URL: https://app.berqun.com (veya app2.berqun.com, us1.berqun.com)
- On-premise: https://{ip-adresi}

## Kimlik Doğrulama
- **POST** `/api/v1/login?user_name={email}&password={sifre}`
- Dönen `auth_token` her istekte Header'da gönderilir:
  `Authorization: Bearer {auth_token}`

## Raporlama İçin Kullanılan API'ler

### Personel Listesi
- **GET/POST** `/api/v1/staff_list`
- Tüm personel listesi, her birinin `staff_guid` bilgisi
- Bu GUID, diğer API çağrılarında kullanılır

### Kullanıcı Dashboard (BQ Puanları)
- **POST** `/api/v1/user_dashboard?date={yyyy-mm-dd}&person_guid={guid}&period_type_id={id}`
- Period tipleri:
  - `13001` → Gün
  - `13002` → Hafta
  - `13003` → Ay (**aylık rapor için bu kullanılır**)
  - `13004` → Yıl
- BQ puanı, verimli/verimsiz süre, uygulama verileri döner

### Personel Aktivite Listesi (Tüm Personel)
- **POST** `/api/v1/staff_activity_list?date={yyyy-mm-dd}&all_staff_flag=1`
- Tüm personelin günlük aktivite verileri

### Personel Aktivite Listesi (Tek Kişi)
- **POST** `/api/v1/staff_activity_list?date={yyyy-mm-dd}&staff_guid={guid}`
- Belirli bir personelin günlük aktivitesi

### Aylık Çalışma Takvimi
- **POST** `/api/v1/calendar_staff_monthly_list`
- Parametre: `date` (ayın herhangi bir günü, ör: 2025-02-01)
- Tüm personelin aylık çalışma takvimi

### Organizasyon Yapısı
- **POST** `/api/v1/organization_upsert` — Departman hiyerarşisi
- **POST** `/api/v1/organization_staff_upsert` — Departman üyeleri ve yöneticileri

## .env Değişkenleri
```
BERQUN_SERVER=app.berqun.com
BERQUN_USERNAME=kullanici@sirket.com
BERQUN_PASSWORD=sifre
```
