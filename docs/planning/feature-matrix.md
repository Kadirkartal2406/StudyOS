# StudyOS — Özellik Matrisi (Feature Matrix)

**Belge Durumu:** Onay Bekliyor — Kapsam Dondurma  
**Sürüm:** 1.0  
**Oluşturuldu:** 2026-07-04 — Meeting-005  
**Kaynak Belgeler:** `docs/requirements/`, `docs/presentations/studyos-presentation-v1.md`  
**Hedef:** MVP geliştirme için ürün kapsamını tanımlamak ve dondurmak

> Bu belge, neyin geliştirileceğini tanımlar. Nasıl geliştirileceğini değil.  
> Öncelik açıklaması: **Zorunlu** = MVP'de olmalı · **Olmalı** = v1.1'de hedef · **Olabilir** = v2.0+ · **Olmayacak** = Kapsam dışı

---

## 1. Öğrenci Mobil Uygulaması — Özellik Listesi

> **Kaynak:** `docs/requirements/institution-platform-requirements.md` (içerik olarak Öğrenci Uygulaması)

### 1.1 Kimlik ve Hesap Yönetimi

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-01 | Kayıt / Giriş | E-posta ve şifre ile hesap oluşturma ve giriş | Öğrenci | Zorunlu | MVP |
| S-02 | Mod Seçimi | Sınav modu (YKS/LGS/KPSS) veya Üniversite modu seçimi | Öğrenci | Zorunlu | MVP |
| S-03 | Profil Yönetimi | Ad, soyad, hedef sınav, fotoğraf düzenleme | Öğrenci | Zorunlu | MVP |
| S-04 | Bulut Senkronizasyonu | Tüm verinin farklı cihazlarda eşzamanlı olarak tutulması | Öğrenci | Zorunlu | MVP |
| S-05 | Şifre Sıfırlama | E-posta ile şifre yenileme | Öğrenci | Zorunlu | MVP |

### 1.2 Çalışma Planlama

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-06 | Günlük Çalışma Planı | Kullanıcı tarafından oluşturulan günlük çalışma programı | Öğrenci | Zorunlu | MVP |
| S-07 | AI Plan Oluşturma | Performans verisine göre AI'ın otomatik haftalık plan üretmesi | Öğrenci | Olmalı | v1.1 |
| S-08 | Konu Takibi | Çalışılan konuları işaretleme ve ilerleme görüntüleme | Öğrenci | Zorunlu | MVP |
| S-09 | Soru Takibi | Çözülen soru sayısını konu bazında kaydetme | Öğrenci | Zorunlu | MVP |
| S-10 | Pomodoro Zamanlayıcı | Özelleştirilebilir odaklanma ve mola zamanlayıcısı | Öğrenci | Zorunlu | MVP |

### 1.3 Analiz ve Değerlendirme

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-11 | Yanlış Defteri | Yanlış yapılan soruların kaydedildiği dijital not sistemi | Öğrenci | Olmalı | v1.1 |
| S-12 | Akıllı Tekrar Sistemi | Yanlış soruların spaced-repetition mantığıyla hatırlatılması | Öğrenci | Olmalı | v1.1 |
| S-13 | Deneme Sınavı Analizi | Deneme sonuçlarını girerek konu/soru bazlı analiz yapma | Öğrenci | Olmalı | v1.1 |
| S-14 | İstatistik ve Grafikler | Günlük/haftalık/aylık çalışma ve başarı grafikleri | Öğrenci | Zorunlu | MVP |

### 1.4 Yapay Zeka Özellikleri

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-15 | AI Çalışma Koçu | Kişiselleştirilmiş akademik rehberlik ve öneri sistemi | Öğrenci | Olmalı | v1.1 |
| S-16 | AI Plan Oluşturma | Performans analizine göre uyarlanabilir çalışma planı | Öğrenci | Olmalı | v1.1 |

> Not: S-07 ile S-16 aynı özelliğe karşılık gelmektedir. Bkz. Bölüm 6 — Tespit Edilen Sorunlar.

### 1.5 Bildirimler ve Hatırlatıcılar

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-17 | Akıllı Bildirimler | Çalışma hatırlatıcıları ve motivasyon bildirimleri | Öğrenci | Zorunlu | MVP |
| S-18 | Günlük Hedef Bildirimi | Günlük çalışma hedefine ulaşılmadığında bildirim | Öğrenci | Zorunlu | MVP |

### 1.6 Gelir ve Abonelik

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-19 | Premium Üyelik | Aylık/yıllık ücretli üyelik ile tam özellik erişimi | Öğrenci | Zorunlu | MVP |
| S-20 | Ödüllü Reklam | İzlenen reklamlar karşılığında uygulama içi avantaj kazanma | Öğrenci | Olmalı | v1.1 |
| S-21 | Uygulama İçi Satın Alma | Tek seferlik özellik veya içerik satın alma | Öğrenci | Olabilir | v2.0 |

### 1.7 Üniversite Modülü (Genişletilmiş İçerik)

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-22 | Üniversite Modu | Ders bazlı planlama, ödev takibi, sınav takvimi | Üniversite Öğrencisi | Olabilir | v2.0 |
| S-23 | PDF Analizi | Yüklenen PDF belgelerinin AI ile özetlenmesi | Öğrenci | Olabilir | v2.0 |
| S-24 | AI Özet | Konu ve doküman özetlerinin AI tarafından oluşturulması | Öğrenci | Olabilir | v2.0 |
| S-25 | Flashcard | Dijital kartlarla ezberleme ve tekrar sistemi | Öğrenci | Olabilir | v2.0 |
| S-26 | Kariyer Özellikleri | Kariyer tavsiyesi ve sınav sonrası yönlendirme | Öğrenci | Olabilir | v2.0 |

### 1.8 Sosyal Özellikler

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-27 | Çalışma Grupları | Arkadaşlarla ortak çalışma grupları oluşturma | Öğrenci | Olmayacak | Gelecek |
| S-28 | Liderlik Tablosu | Kurum veya grup içinde çalışma sıralaması | Öğrenci | Olmayacak | Gelecek |
| S-29 | Sosyal Profil | Diğer öğrencilerle bağlantı kurma ve ilerleme paylaşma | Öğrenci | Olmayacak | Gelecek |

### 1.9 Platform Genişletme

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| S-30 | Ana Ekran Widget | Telefon ana ekranında günlük plan ve istatistik widget | Öğrenci | Olmayacak | Gelecek |
| S-31 | Akıllı Saat Desteği | WearOS / watchOS ile temel bildirim ve zamanlayıcı | Öğrenci | Olmayacak | Gelecek |

---

## 2. Kurumsal Web Platformu — Özellik Listesi

> **Kaynak:** `docs/requirements/student-platform-requirements.md` (içerik olarak Kurumsal Platform)

### 2.1 Kurum ve Yapı Yönetimi

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-01 | Kurum Kaydı | Yeni kurum hesabı oluşturma ve doğrulama | Kurum Yöneticisi | Zorunlu | MVP |
| K-02 | Şube Yönetimi | Birden fazla şube oluşturma ve şube bazlı yönetim | Kurum Yöneticisi | Zorunlu | MVP |
| K-03 | Sınıf Oluşturma | Şube içinde sınıf/grup tanımlama | Kurum Yöneticisi | Zorunlu | MVP |
| K-04 | Öğretmen Hesabı | Öğretmen kaydı ve sisteme davet | Kurum Yöneticisi | Zorunlu | MVP |
| K-05 | Öğrenci Daveti | Öğrenciyi sisteme davet etme ve sınıfa atama | Kurum Yöneticisi / Öğretmen | Zorunlu | MVP |
| K-06 | Rol ve Yetki Yönetimi | Yönetici, öğretmen, öğrenci rollerine göre erişim kontrolü | Kurum Yöneticisi | Zorunlu | MVP |

### 2.2 Eğitim Yönetimi

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-07 | Ders Programı | Haftalık/günlük ders takvimi oluşturma ve yönetme | Öğretmen | Zorunlu | MVP |
| K-08 | Dijital Yoklama | Sınıf yoklamalarını dijital ortamda kaydetme | Öğretmen | Zorunlu | MVP |
| K-09 | Ödev Oluşturma | Sınıfa ödev tanımlama ve son teslim tarihi belirleme | Öğretmen | Olmalı | v1.1 |
| K-10 | Ödev Teslim Takibi | Ödev teslim durumlarını öğrenci bazında izleme | Öğretmen | Olmalı | v1.1 |
| K-11 | Duyuru Sistemi | Sınıf veya kuruma toplu duyuru yayınlama | Öğretmen / Yönetici | Zorunlu | MVP |
| K-12 | PDF ve Doküman Yükleme | Ders materyallerini PDF ve doküman olarak paylaşma | Öğretmen | Zorunlu | MVP |
| K-13 | Video Ders Paylaşımı | Video içerik yükleme veya bağlantı paylaşma | Öğretmen | Olmalı | v1.1 |

### 2.3 Sınav ve Değerlendirme

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-14 | Deneme Sınavı Oluşturma | Deneme sınavı tanımlama ve sınıfa atama | Öğretmen / Yönetici | Zorunlu | MVP |
| K-15 | Optik Sonuç Aktarımı | Kağıt tabanlı sınav sonuçlarını sisteme aktarma | Öğretmen / Yönetici | Olmalı | v1.1 |
| K-16 | Deneme Analizleri | Sınav sonuçlarını konu/öğrenci bazında analiz etme | Öğretmen / Yönetici | Zorunlu | MVP |
| K-17 | Konu Bazlı Başarı Analizi | Konulara göre sınıf başarı oranlarını görüntüleme | Öğretmen / Yönetici | Zorunlu | MVP |
| K-18 | Öğrenci Gelişim Raporu | Bireysel öğrenci ilerleme raporu oluşturma | Öğretmen / Yönetici | Olmalı | v1.1 |

### 2.4 Raporlama ve Analitik

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-19 | Sınıf İstatistikleri | Sınıf genelinde çalışma ve başarı özeti | Öğretmen / Yönetici | Zorunlu | MVP |
| K-20 | Kurum İstatistikleri | Tüm şube ve sınıfları kapsayan kurum geneli analitik | Kurum Yöneticisi | Olmalı | v1.1 |
| K-21 | Rapor Dışa Aktarma | Raporları PDF veya Excel olarak indirme | Kurum Yöneticisi | Olmalı | v1.1 |

### 2.5 Yapay Zeka Özellikleri

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-22 | AI Akademik Danışman | Kuruma özel yapay zeka ile akademik öneriler | Öğretmen / Yönetici | Olmalı | v1.1 |
| K-23 | Riskli Öğrenci Tespiti | Başarı trendi düşen öğrencileri otomatik tespit ve uyarı | Öğretmen / Yönetici | Olmalı | v1.1 |

### 2.6 Veli ve İletişim

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-24 | Veli Erişimi | Veliye öğrencinin ilerlemesini görüntüleme paneli | Veli | Olmalı | v1.1 |
| K-25 | Mesajlaşma Sistemi | Öğretmen-öğrenci ve öğretmen-veli mesajlaşması | Öğretmen / Veli | Olabilir | v2.0 |

### 2.7 Gelişmiş Özellikler

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| K-26 | Canlı Ders | Anlık video ders yayını ve interaktif ders deneyimi | Öğretmen / Öğrenci | Olabilir | v2.0 |
| K-27 | Çoklu Kurum Yönetimi | Birden fazla kurumu tek hesaptan yönetme | Üst Yönetici | Olmayacak | Gelecek |
| K-28 | LMS Özellikleri | Tam öğrenme yönetim sistemi işlevleri | Kurum Yöneticisi | Olmayacak | Gelecek |
| K-29 | Üçüncü Taraf API | Dış sistemlerle entegrasyon için açık API | Geliştirici | Olmayacak | Gelecek |

---

## 3. Ortak / Entegrasyon Özellikleri

Bu özellikler her iki platformun birlikte çalışmasını sağlar.

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| E-01 | Ortak Kullanıcı Hesabı | Öğrenci aynı kimlik bilgileriyle her iki platforma erişir | Öğrenci | Zorunlu | MVP |
| E-02 | Çalışma Süresi Senkronu | Öğrencinin mobil uygulamadaki çalışma süreleri kuruma iletilir | Öğrenci / Kurum | Olmalı | v1.1 |
| E-03 | Deneme Sonucu Senkronu | Öğrencinin deneme sonuçları her iki platformda görünür | Öğrenci / Kurum | Olmalı | v1.1 |
| E-04 | Ödev Bildirimi | Kurumda oluşturulan ödevler öğrencinin mobil uygulamasına düşer | Öğrenci | Olmalı | v1.1 |
| E-05 | Materyal Senkronu | Kurumun yüklediği PDF ve materyaller mobilde erişilebilir olur | Öğrenci | Olmalı | v1.1 |
| E-06 | AI Analiz Paylaşımı | Her iki platformdaki AI analizleri ortak bulut üzerinden paylaşılır | Öğrenci / Kurum | Olmalı | v1.1 |
| E-07 | Başarı Grafiği Senkronu | Öğrencinin başarı grafikleri kurum paneline aktarılır | Kurum | Olmalı | v1.1 |

---

## 4. Sistem / Altyapı Özellikleri

| # | Özellik Adı | Açıklama | Hedef Kullanıcı | Öncelik | Sürüm |
|---|------------|---------|----------------|---------|-------|
| A-01 | Güvenli Kimlik Doğrulama | Token tabanlı güvenli oturum yönetimi | Tüm | Zorunlu | MVP |
| A-02 | KVKK / GDPR Uyumu | Kişisel veri işleme ve saklama politikaları | Tüm | Zorunlu | MVP |
| A-03 | %99 Erişilebilirlik Hedefi | Sistem kesinti süresi yılda en fazla 87 saat | Tüm | Zorunlu | MVP |
| A-04 | Günlük Otomatik Yedekleme | Tüm verilerin günlük yedeğinin alınması | Sistem | Zorunlu | MVP |
| A-05 | Loglama ve Hata Takibi | Sistem hatalarının kayıt altına alınması ve izlenmesi | Sistem | Zorunlu | MVP |
| A-06 | Ölçeklenebilir Mimari | Kullanıcı artışına göre otomatik kaynak yönetimi | Sistem | Zorunlu | MVP |
| A-07 | API Performans Hedefi | Ortalama API yanıt süresi 3 saniyenin altında | Sistem | Zorunlu | MVP |

---

## 5. MVP Kapsamı

MVP'de yalnızca **Zorunlu** öncelikli özellikler bulunur. Aşağıdaki liste MVP'yi tanımlar.

### 5.1 Öğrenci Uygulaması — MVP

| Kod | Özellik |
|-----|---------|
| S-01 | Kayıt / Giriş |
| S-02 | Mod Seçimi |
| S-03 | Profil Yönetimi |
| S-04 | Bulut Senkronizasyonu |
| S-05 | Şifre Sıfırlama |
| S-06 | Günlük Çalışma Planı |
| S-08 | Konu Takibi |
| S-09 | Soru Takibi |
| S-10 | Pomodoro Zamanlayıcı |
| S-14 | İstatistik ve Grafikler |
| S-17 | Akıllı Bildirimler |
| S-18 | Günlük Hedef Bildirimi |
| S-19 | Premium Üyelik |

**Toplam MVP Öğrenci Özelliği: 13**

### 5.2 Kurumsal Platform — MVP

| Kod | Özellik |
|-----|---------|
| K-01 | Kurum Kaydı |
| K-02 | Şube Yönetimi |
| K-03 | Sınıf Oluşturma |
| K-04 | Öğretmen Hesabı |
| K-05 | Öğrenci Daveti |
| K-06 | Rol ve Yetki Yönetimi |
| K-07 | Ders Programı |
| K-08 | Dijital Yoklama |
| K-11 | Duyuru Sistemi |
| K-12 | PDF ve Doküman Yükleme |
| K-14 | Deneme Sınavı Oluşturma |
| K-16 | Deneme Analizleri |
| K-17 | Konu Bazlı Başarı Analizi |
| K-19 | Sınıf İstatistikleri |

**Toplam MVP Kurumsal Özellik: 14**

### 5.3 Ortak — MVP

| Kod | Özellik |
|-----|---------|
| E-01 | Ortak Kullanıcı Hesabı |
| A-01 | Güvenli Kimlik Doğrulama |
| A-02 | KVKK / GDPR Uyumu |
| A-03 | %99 Erişilebilirlik Hedefi |
| A-04 | Günlük Otomatik Yedekleme |
| A-05 | Loglama ve Hata Takibi |
| A-06 | Ölçeklenebilir Mimari |
| A-07 | API Performans Hedefi |

**Toplam MVP Ortak/Altyapı Özelliği: 8**

### 5.4 MVP Özeti

| Platform | Özellik Sayısı |
|----------|---------------|
| Öğrenci Uygulaması | 13 |
| Kurumsal Platform | 14 |
| Ortak / Altyapı | 8 |
| **Toplam** | **35** |

---

## 6. Tespit Edilen Sorunlar

Bu bölüm kaynak belgelerde tespit edilen tekrar, eksiklik ve tutarsızlıkları listeler.

### 6.1 Yinelenen Özellikler

| Yineleme | Açıklama |
|----------|---------|
| S-07 ↔ S-16 | "AI Plan Oluşturma" iki kez tanımlandı. Bu belgede tek özellik olarak birleştirildi (S-07, S-16 kaldırıldı). |

### 6.2 Eksik Özellikler

Kaynak belgelerde adı geçen ancak yeterince tanımlanmayan özellikler:

| Eksik | Nerede Geçiyor | Durum |
|-------|----------------|-------|
| Uygulama içi satın alma mekanizması | Gelir modelinde adı geçiyor | İçerik belirsiz — **[ONAY GEREKTİRİR]** |
| Optik cevap kağıdı formatı | K-15'te adı geçiyor | Hangi format desteklenecek? — **[ONAY GEREKTİRİR]** |
| Veli hesabı nasıl oluşturulacak? | K-24'te adı geçiyor | Davet sistemi mi, kurum tanımlamalı mı? — **[ONAY GEREKTİRİR]** |
| Premium üyeliğin hangi özellikleri kapsamadığı | S-19'da adı geçiyor | Ücretsiz sürüm sınırları belirsiz — **[ONAY GEREKTİRİR]** |

### 6.3 Tutarsız Gereksinimler

| Tutarsızlık | Kaynak | Açıklama |
|------------|--------|---------|
| Dosya adı ↔ İçerik uyuşmazlığı | `docs/requirements/` | Öğrenci gereksinimlerini içeren dosya `institution-platform-requirements.md`, kurumsal gereksinimler ise `student-platform-requirements.md` olarak adlandırılmış. Bu durum Meeting-001'de tespit edildi, içerik korundu. Dosya yeniden adlandırması önerilir. **[ONAY GEREKTİRİR]** |
| Kurumsal MVP ↔ Sunum tutarsızlığı | Gereksinim belgesi vs. Sunum | Sunum materyallerinde Kurumsal MVP'ye mesajlaşma ve canlı ders dahil edilmişti; gereksinim belgesi bunları V3'e koyuyor. Bu matrikte gereksinim belgesi esas alındı. |

---

## 7. Öneriler

> **Uyarı:** Bu bölümdeki hiçbir öneri otomatik olarak kapsama eklenmez.  
> Tümü **[ONAY GEREKTİRİR]** etiketlidir ve proje sahibinin kararına tabidir.

| # | Öneri | Gerekçe | Önerilen Sürüm |
|---|-------|---------|----------------|
| R-01 | Ücretsiz plan sınırlarının açıkça tanımlanması | Öğrencinin premium'a geçiş motivasyonu ve gelir modeli için kritik | MVP öncesi |
| R-02 | Kurum kaydı için onay mekanizması | Sahte kurum kayıtlarını önlemek için admin onayı veya e-posta doğrulama | MVP |
| R-03 | Öğrenci–Kurum bağlantı akışının tanımlanması | Öğrenci kuruma nasıl bağlanacak? Davet kodu mu, e-posta mı? | MVP öncesi |
| R-04 | Gereksinim dosyalarının yeniden adlandırılması | İsimlendirme karışıklığı ileride ciddi hatalara yol açabilir | Hemen |
| R-05 | Çevrimdışı mod | Öğrencinin internet yokken de plan ve pomodoro kullanabilmesi | v1.1 |
| R-06 | Çoklu dil desteği (i18n) | Uluslararası pazara açılım hedefi varsa altyapı baştan kurulmalı | v2.0 |
| R-07 | Öğretmen performans raporu | Hangi öğretmenin ödevlerinin takip edildiği, yoklama düzenli mi | v2.0 |

---

## 8. Gelecek Sürümler

### MVP (İlk Yayın)
Bkz. Bölüm 5 — 35 özellik.

### v1.1
Tüm **Olmalı** öncelikli özellikler:

- Öğrenci: S-07, S-11, S-12, S-13, S-15, S-20
- Kurumsal: K-09, K-10, K-13, K-15, K-18, K-20, K-21, K-22, K-23, K-24
- Entegrasyon: E-02, E-03, E-04, E-05, E-06, E-07

**Tahmini v1.1 özellik sayısı: 22**

### v2.0
Tüm **Olabilir** öncelikli özellikler:

- Öğrenci: S-21, S-22, S-23, S-24, S-25, S-26
- Kurumsal: K-25, K-26

**Tahmini v2.0 özellik sayısı: 8**

### Gelecek (Kapsam Dışı — Şimdilik)
- Öğrenci: S-27, S-28, S-29, S-30, S-31
- Kurumsal: K-27, K-28, K-29

**Bu özellikler kapsam dışıdır. Dahil edilmeleri için ayrı bir toplantı ve onay gerekir.**

---

## 9. Özellik Sayısı Özeti

| Kategori | Toplam | MVP | v1.1 | v2.0 | Gelecek |
|----------|--------|-----|------|------|---------|
| Öğrenci Uygulaması | 31 | 13 | 6 | 6 | 5 |
| Kurumsal Platform | 29 | 14 | 10 | 2 | 3 |
| Entegrasyon | 7 | 1 | 6 | — | — |
| Altyapı | 7 | 7 | — | — | — |
| **Toplam** | **74** | **35** | **22** | **8** | **8** |
