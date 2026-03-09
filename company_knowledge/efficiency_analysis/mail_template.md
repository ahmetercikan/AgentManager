# Verimlilik Analizi — Mail Şablonu

## Aylık GMY Rapor Maili

### Konu
Verimlilik Analizi Raporları - [GMY Adı] - [Ay Yılı] | SDPY

### Ekler
1. Çalışan Verimliliği Raporu (kişi bazlı Berqun verileri)
2. 100 Altı BQ Detay Raporu

### Mail İçeriği

---

Merhaba,

Verimlilik Analizi uygulamasında yapılan Çalışan Verimliliği kapsamında, çalışanlarımızın verimlilik raporları GMY'lik bazında düzenlenmiştir.
Verimlilik Analizi Raporlar, çalışanlarımızın gelişimini desteklemek ve şirketimizin hedeflerine daha etkin bir şekilde ulaşmasına katkı sunmak amacıyla paylaşılmaktadır.

Raporların içeriği, çalışanlarımızın günlük faaliyetleri, verimlilik göstergeleri ve belirlenen BQ puanı hedefine ulaşma durumu gibi önemli verileri kapsamaktadır. Bu veriler, çalışanlarımızın daha verimli ve etkili bir çalışma ortamında bulunmaları için gerekli yönlendirmeleri yapmamıza olanak tanıyacaktır.
Çalışanlarımızın gizliliği ve verilerinin korunması konusunda tüm önlemler alınmakta olup, raporlar sadece yetkilendirilmiş kişiler tarafından incelenecektir. Verimlilik Analizi uygulaması üzerinden toplanan veriler, çalışanlarımızın profesyonel gelişimini desteklemek ve iş süreçlerimizi iyileştirmek için kullanılacaktır.

Domain özelinde BQ puanı 100 altında olan kişi sayısı : [SAYI] (Detayını ekli dosyada bulabilirsiniz.)
3 gün ve üzeri VPN yapmayan kişi sayısı : [SAYI] (Detayını ekli dosyada bulabilirsiniz.)
Riskli Davranış Örüntüleri Değerlendirmesi
[RİSKLİ DURUM VARSA YAZILIR / "Riskli durum izlenmemiştir."]

Rapor Türü
- Çalışan Verimliliği: İlgili GMY'liklere bağlı ekiplerin, kişi ve takım bazında hazırlanan raporudur. Bu raporun içeriğinde, personelin aktif çalışılan ay içerisindeki beklenen çalışma gün sayısı, BQ (Business Quality) puanı, verimli/verimsiz çalıştığı süreler, çalışma günleri/çalışma günleri dışında harcadığı fazla mesai süreleri, bilgisayar üzerinde hareketsiz geçirdiği süreler, işe başlama ve işi bitirme süreleri gibi başlıca önemli veriler yer almaktadır.

- 100 Puan Altı BQ Puan Alan Çalışan Faaliyetleri: Çalışan Verimliliği raporunda BQ (Business Quality) puanı 100'in altında olan personelin, aktif çalışılan ay içerisindeki verimli/verimsiz tüm zamanları, kullanılan uygulama verileri, BQ (Business Quality) grafiği, gün içerisinde geçirilen zamanın saatlik grafiği gibi başlıca önemli veriler bulunmaktadır.

- 3 Gün ve üzeri VPN Yapmayanlar: Verimlilik Analizi uygulaması, gün içerisinde tüm personel hareketlerini bir dosya da toplamakta ve bu dosyadaki verileri VPN aracılığı ile sunucuya iletmektedir. Bu dosya içerisinde VPN bağlantısı son 3 gün içinde gerçekleşmeyen personelin listesi verilmiştir. Bu listedeki personel'e VPN yapmaları ile ilgili bilgi verilmelidir. Bilgi Güvenliği sebebi ile bu bilgileri VPN aracılığı ile toplamamız gerekmektedir.

Çalışan Faaliyetleri: Çalışan Verimliliği raporunda, tüm personelin aktif çalışılan ay içerisindeki verimli/verimsiz tüm zamanları, kullanılan uygulama verileri, BQ (Business Quality) grafiği, gün içerisinde geçirilen zamanın saatlik grafiği gibi başlıca önemli veriler bulunmaktadır.

Verimlilik Analizi raporunda, personelin kullanmış olduğu Verimsiz uygulamaların Verimli olduğunu düşünüyorsanız, bu uygulamaları verimlilikanalizi@dgpaysit.com mail adresine iletebilirsiniz.

Verimlilik Analizi Raporlarını değerlendirmek için ihtiyaç duyacağınız yardımcı döküman ekte "Verimlilik Analizi Rapor Statü Açıklamaları" yer almaktadır.
Raporlama aylık periyotlarda yapılacaktır.
Destek ve İhtiyaçlarınız durumunda verimlilikanalizi@dgpaysit.com maili üzerinden bizimle iletişime geçebilirsiniz.

Bu süreçte göstereceğiniz anlayış ve iş birliği için şimdiden teşekkür ederiz.

Saygılarımızla,

---

## Dinamik Alanlar (Agent'ın Doldurması Gereken)
| Alan | Açıklama | Kaynak |
|------|----------|--------|
| `[GMY Adı]` | Raporun gönderildiği GMY'lik | GMyL listesinden |
| `[Ay Yılı]` | Raporun ait olduğu dönem | Berqun API'den |
| `[SAYI]` - BQ < 100 | Domain özelinde BQ puanı 100 altında kişi sayısı | Berqun API'den hesaplanır |
| `[SAYI]` - VPN | 3+ gün VPN yapmayan kişi sayısı | Berqun API'den |
| `[RİSKLİ DURUM]` | Riskli davranış varsa açıklama | Berqun API'den analiz |
| Ek dosya 1 | Kişi bazlı Berqun verileri (Excel/PDF) | Berqun API'den indirilen rapor |
| Ek dosya 2 | 100 altı BQ detayı | Berqun API filtreleme |
