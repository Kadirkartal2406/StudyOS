# StudyOS — Project Presentation Outline

---

## Slide 1 — Title Slide

**Title:** StudyOS: AI-Destekli Eğitim Ekosistemi
**Subtitle:** Öğrenci Mobil Uygulaması & Kurumsal Yönetim Platformu

**Purpose:** Sunumun ilk izlenimini oluşturur. Projenin adını, kapsamını ve iki bileşenli yapısını ilk anda netleştirir.

**Key Points:**
- Proje adı: StudyOS
- İki ürün: Öğrenci Mobil Uygulaması + Kurumsal (Dershane) Web Platformu
- Ortak altyapı üzerinde çalışan tek eğitim ekosistemi

**Suggested Visual:** StudyOS logosu veya iki ürünü yan yana gösteren basit bir ikon çifti (telefon + masaüstü ekranı).

---

## Slide 2 — Problem

**Title:** Mevcut Sorun

**Purpose:** Sunumun geri kalanı için motivasyonu kurar. Dinleyicilerin neden bu projeye ihtiyaç duyulduğunu anlamasını sağlar.

**Key Points:**
- KPSS, YKS, LGS gibi sınavlara hazırlanan öğrencilerin dağınık araçlarla çalışması gerekiyor.
- Üniversite öğrencileri ve bireysel öğrenenler için merkezi bir çalışma platformu yok.
- Dershaneler ve eğitim kurumları öğrenci takibi, yoklama, ödev ve deneme yönetimini ayrı araçlarla yapıyor.
- Öğrenci verisi ile kurum verisi arasında entegrasyon yok; veri kaybı ve tekrarlı iş ortaya çıkıyor.

**Suggested Visual:** Dağınık araçları (ajanda, not defteri, farklı uygulamalar, excel) gösteren basit bir liste veya ikon grubu.

---

## Slide 3 — Proposed Solution

**Title:** Çözüm: StudyOS Ekosistemi

**Purpose:** Projenin temel cevabını özetler. Tek platformda hem öğrenci hem kurum ihtiyaçlarının nasıl karşılandığını gösterir.

**Key Points:**
- Öğrenciler için: yapay zeka destekli çalışma koçu, deneme analizi, konu takibi ve verimlilik araçları tek mobil uygulamada.
- Kurumlar için: sınıf yönetimi, yoklama, ödev takibi, raporlama tek web platformunda.
- İki ürün ortak API ve veritabanı servisleri üzerinden çift yönlü veri alışverişi yapar.
- Öğrenci verisi kurum paneline, kurum verileri öğrenci uygulamasına senkronize akar.

**Suggested Visual:** İki blok (Öğrenci Uygulaması ↔ Ortak API ↔ Kurumsal Platform) şeklinde basit bir mimari şeması.

---

## Slide 4 — Target Audience

**Title:** Hedef Kitle

**Purpose:** Projenin kimi hedeflediğini netleştirir ve paydaşların kendilerini sunumda görmesini sağlar.

**Key Points:**
- **Öğrenci tarafı:** Sınav öğrencileri (KPSS, YKS, LGS), üniversite öğrencileri, bireysel öğrenenler.
- **Kurum tarafı:** Dershaneler, kurslar, eğitim kurumları ve bunların şubeleri.
- **İkincil kullanıcılar:** Öğretmenler, veliler (veli erişim modülü aracılığıyla).

**Suggested Visual:** Üç kullanıcı profil ikonu (öğrenci, kurum yöneticisi, öğretmen) ve kısa etiketler.

---

## Slide 5 — Student Platform

**Title:** Öğrenci Platformu — Mobil Uygulama

**Purpose:** Öğrenci uygulamasının kapsamını ve sunduğu temel değeri açıklar.

**Key Points:**
- Günlük çalışma planı oluşturma
- Konu ve soru takibi
- Pomodoro zamanlayıcı
- Deneme analizi
- Yanlış defteri
- Akıllı tekrar sistemi
- İstatistik ve grafikler
- Bildirimler ve hatırlatıcılar
- Bulut senkronizasyonu
- Android ve iOS desteği

**Suggested Visual:** Mobil uygulama ekran akışını gösteren 3–4 ekranın yatay sıralaması (onboarding → çalışma planı → deneme analizi → istatistik).

---

## Slide 6 — Institution Platform

**Title:** Kurumsal Platform — Web Yönetim Paneli

**Purpose:** Dershane ve eğitim kurumlarına yönelik web platformunun kapsamını açıklar.

**Key Points:**
- Kurum ve şube yönetimi
- Sınıf oluşturma ve öğrenci/öğretmen atama
- Dijital yoklama
- Ders programı oluşturma
- Ödev oluşturma ve teslim takibi
- PDF, kitap ve doküman yükleme
- Video ders paylaşımı
- Deneme sınavı oluşturma ve optik sonuç aktarımı
- Duyuru sistemi
- Yetkilendirme ve rol yönetimi
- Rapor dışa aktarma

**Suggested Visual:** Web dashboard ekran görüntüsü taslağı veya özellik gruplarını gösteren 3 sütunlu bir kart düzeni (Yönetim / İçerik / Raporlama).

---

## Slide 7 — AI-Powered Features

**Title:** Yapay Zeka Özellikleri

**Purpose:** Projenin rekabet avantajının merkezinde yer alan AI özelliklerini ön plana çıkarır.

**Key Points:**
- **Öğrenci uygulamasında:**
  - AI çalışma koçu — kişisel çalışma rehberliği
  - AI plan oluşturma — hedefe göre otomatik program
  - Akıllı tekrar sistemi — zayıf konuları önceliklendirme
- **Kurumsal platformda:**
  - AI akademik danışman
  - Riskli öğrenci tespiti — başarı düşüşlerini erken uyarı
  - Konu bazlı başarı analizi
  - Öğrenci gelişim raporları
- AI analizleri her iki platformda da kullanılabilir.

**Suggested Visual:** İki sütunlu tablo: sol sütun "Öğrenci AI Özellikleri", sağ sütun "Kurum AI Özellikleri".

---

## Slide 8 — Integration & Architecture

**Title:** Entegrasyon ve Mimari

**Purpose:** İki ürünün teknik olarak nasıl bir arada çalıştığını gösterir; platformlar arası veri akışını netleştirir.

**Key Points:**
- İki bağımsız uygulama: Öğrenci Mobil Uygulaması + Kurumsal Web Platformu
- Ortak API ve veritabanı servisleri üzerinden güvenli haberleşme
- Senkronize olan veriler:
  - Çalışma süreleri
  - Deneme sonuçları
  - Ödevler
  - PDF ve materyaller
  - AI analizleri
  - Öğrenci başarı grafikleri

**Suggested Visual:** Merkeze "Ortak API ve Veritabanı" yerleştirilen, solda mobil uygulama, sağda web platformu bulunan iki yönlü ok diyagramı.

---

## Slide 9 — Competitive Advantages

**Title:** Rekabet Avantajları

**Purpose:** StudyOS'u mevcut çözümlerden ayıran unsurları özetler ve projenin değer önerisini güçlendirir.

**Key Points:**
- Öğrenci ve kurum ihtiyaçlarını tek ekosistemde birleştiren entegre yaklaşım
- AI destekli kişiselleştirilmiş çalışma koçluğu ve riskli öğrenci tespiti
- Optik sonuç aktarımı ile sınav sonuçlarının dijitale taşınması
- KVKK/GDPR uyumlu, güvenli veri yönetimi
- %99 erişilebilirlik hedefi ile yüksek güvenilirlik
- Veli erişimi ile şeffaf takip imkânı
- Ölçeklenebilir mimari — kurumdan kuruma büyüyebilen yapı

**Suggested Visual:** Avantajları vurgulayan bir "Neden StudyOS?" ikon + kısa etiket kartları düzeni.

---

## Slide 10 — Release Roadmap

**Title:** Sürüm Yol Haritası

**Purpose:** Projenin aşamalı gelişim planını gösterir; ekibe ve paydaşlara hangi özelliklerin ne zaman geleceğini netleştirir.

**Key Points:**

| Sürüm | Öğrenci Uygulaması | Kurumsal Platform |
|-------|--------------------|-------------------|
| **MVP** | Giriş, çalışma planı, konu takibi, pomodoro, istatistik | Kurum, sınıf, öğrenci, öğretmen, PDF, deneme |
| **V2** | AI koç, deneme analizi, yanlış defteri, akıllı tekrar | AI analiz, veli paneli, gelişmiş raporlama |
| **V3** | Üniversite modülü, PDF analizi, AI özet, flashcard, kariyer | Canlı ders, mesajlaşma, ödev sistemi, optik okuma |
| **V4** | Sosyal özellikler, çalışma grupları, liderlik tablosu, widget, saat desteği | Çoklu kurum yönetimi, LMS özellikleri, API entegrasyonları |

**Suggested Visual:** Dört aşamalı yatay zaman çizelgesi (MVP → V2 → V3 → V4), her adımın altında kısa özellik özetleriyle.

---

## Slide 11 — Revenue Model

**Title:** Gelir Modeli

**Purpose:** Projenin sürdürülebilirliğini gösterir; iş modelini paydaşlara ve yatırımcılara aktarır.

**Key Points:**
- **Öğrenci Uygulaması:**
  - Premium abonelik
  - Ödüllü reklamlar
  - Uygulama içi satın alma
- **Kurumsal Platform:**
  - Kurum başına aylık / yıllık lisans
  - Öğrenci başına lisans
  - Premium AI modülleri
  - Kurumsal raporlama paketleri
- Her iki taraf için kurumsal lisans ortak bir büyüme kanalı oluşturur.

**Suggested Visual:** İki sütunlu gelir kaynağı kartları (Öğrenci Geliri / Kurum Geliri).

---

## Slide 12 — Technical Infrastructure

**Title:** Teknik Altyapı

**Purpose:** Projenin hangi teknoloji temeli üzerine inşa edileceğini gösterir; ekibin teknik güvenilirliğini ortaya koyar.

**Key Points:**
- **Mobil:** Flutter (Android ve iOS)
- **Backend:** FastAPI
- **Veritabanı:** PostgreSQL
- **Bulut ve Kimlik Doğrulama:** Firebase
- **AI Entegrasyonu:** AI API
- **CI/CD:** GitHub Actions
- Ortalama API yanıt süresi hedefi: < 3 saniye
- Güvenli kullanıcı doğrulama, KVKK/GDPR uyumu, günlük otomatik yedekleme

**Suggested Visual:** Teknoloji yığınını gösteren katmanlı blok diyagramı (Mobil → API → Veritabanı → Bulut Servisleri).

---

## Slide 13 — Long-Term Vision

**Title:** Uzun Vadeli Vizyon

**Purpose:** Projenin nereye gittiğini gösterir; büyük resmi sunar ve dinleyicilerde heyecan yaratır.

**Key Points:**
- Öğrenci uygulaması ve kurumsal platform bağımsız ürünler olarak büyür.
- Ortak kullanıcı hesabı, API ve veri altyapısı sayesinde tek bir eğitim ekosistemi olarak çalışır.
- Gelecekte: çoklu kurum yönetimi, LMS özellikleri, sosyal öğrenme, widget ve saat desteği.
- Geliştirme yol haritası: Analiz → UI/UX → Backend → Mobil → AI → Test → Beta → Yayın → Pazarlama

**Suggested Visual:** "Bugün" ve "Gelecek" kutularını birbirine bağlayan bir büyüme oku veya ekosistem dairesi.

---

## Slide 14 — Summary & Call to Action

**Title:** Özet ve Sonraki Adımlar

**Purpose:** Sunumu kapatır; dinleyicileri temel mesajla bırakır ve bir sonraki adımı netleştirir.

**Key Points:**
- StudyOS: Öğrenciden kuruma, bireyden dershaneye uçtan uca eğitim platformu.
- İki bağımsız ürün, tek entegre ekosistem.
- AI destekli, KVKK uyumlu, ölçeklenebilir.
- MVP kapsamı netleştirildi; geliştirme aşamaları planlandı.
- **Sonraki adımlar:** UI/UX tasarımı, backend mimarisi, sprint planlaması.

**Suggested Visual:** Üç ikon: Öğrenci uygulaması + Kurumsal platform + AI — altında "Tek Ekosistem" başlığı.

---

## Presentation Summary

| Alan | Bilgi |
|------|-------|
| **Toplam Slayt Sayısı** | 14 slayt |
| **Tahmini Sunum Süresi** | 12–14 dakika (slayt başına ortalama ~55 saniye) |

---

## Recommendations

1. **Dil seçimi:** Slaytlar Türkçe hazırlanabilir (hedef kitle yerel); yabancı paydaşlar için İngilizce paralel sürüm oluşturulabilir.
2. **Slide 10 (Roadmap):** Tablonun görsel bir zaman çizelgesine dönüştürülmesi anlaşılırlığı artırır; sunum aracının izin verdiği ölçüde renkli şerit kullanın.
3. **Slide 7 (AI):** AI özelliklerini soyut bırakmak yerine, kısa bir kullanıcı senaryosu (örnek: "Ali denemeyi girdi, AI zayıf konuları tespit etti ve çalışma planını güncelledi") anlatım gücünü artırır.
4. **Slide 8 (Entegrasyon):** Teknik olmayan izleyiciler için mimari diyagramını olabildiğince sade tutun; iki kutu ve iki yönlü ok yeterlidir.
5. **Slayt geçişi:** Slide 2 (Problem) kapanır kapanmaz Slide 3 (Çözüm) açılması dramatik bir etki sağlar; bu geçişi hızlı tutun.
6. **Yedek slayt:** Tam özellik listeleri ekstra slayt olarak hazırda tutulabilir; sunuma eklenmeyip yalnızca soru-cevap bölümünde kullanılmak üzere ayrı tutulabilir.