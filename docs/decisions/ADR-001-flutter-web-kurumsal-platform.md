# ADR-001 — Kurumsal Web Platformu için Flutter Web Seçimi

**Tarih:** 2026-07-06  
**Durum:** Kabul Edildi  
**Karar Veren:** Proje Sahibi  
**Oturum:** Meeting-007 (açık soru kapandı)  
**Etkilenen Belge:** `docs/architecture/software-architecture.md`

---

## Bağlam

StudyOS Kurumsal Web Platformu, dershane ve eğitim kurumları yöneticileri ile öğretmenler tarafından kullanılacak bir web tabanlı yönetim panelidir.

Meeting-007'de bu platformun hangi frontend teknolojisiyle geliştirileceği açık soru olarak bırakılmıştı:

- **Seçenek A:** Flutter Web
- **Seçenek B:** React / Next.js

---

## Değerlendirilen Seçenekler

### Seçenek A — Flutter Web

- ✅ Mobil uygulama ile aynı dil (Dart) ve framework (Flutter).
- ✅ Widget, tema ve tasarım sistemi mobil ile paylaşılır.
- ✅ İki kişilik ekip için tek teknoloji yığını — öğrenme maliyeti sıfır.
- ✅ Kurumsal platform SEO gerektirmeyen, giriş gerektiren bir yönetim panelidir.
- ❌ Flutter Web, native web (React/Next.js) kadar SEO dostu değil.
- ❌ Büyük PDF ve tablo render performansı React'a göre zayıf olabilir.
- ❌ Web erişilebilirlik (ARIA) desteği React kadar olgun değil.

### Seçenek B — React / Next.js

- ✅ Geniş web ekosistemi, çok sayıda UI kütüphanesi.
- ✅ SEO optimizasyonu (Next.js SSR).
- ✅ Web standartlarına tam uyum, erişilebilirlik.
- ❌ Ekip Dart ve Flutter kullanacak; JavaScript/TypeScript ek öğrenme maliyeti.
- ❌ İki ayrı UI/UX sistem bakımı.
- ❌ Kurumsal panel için SEO avantajı bu projede kritik değil.

---

## Alınan Karar

**Flutter Web** kullanılacaktır.

---

## Sonuçlar

**Avantajlar:**
- Tek kod tabanı yaklaşımı: mobil ve web aynı Dart ekibiyle geliştirilir.
- Ortak widget kütüphanesi; `core/theme/`, `shared/widgets/` bileşenleri her iki platformda kullanılabilir.
- Geliştirme hızı ve bakım kolaylığı.

**Kabul Edilen Trade-off'lar:**
- Flutter Web performansı (özellikle ilk yükleme) native web'e göre daha yavaş olabilir — yönetim paneli bağlamında kabul edilebilir.
- Web erişilebilirlik standartları gelecekte ayrıca değerlendirilecek.

**Mimari Etki:**
- Proje yapısı: `studyos_mobile` (Flutter mobil) + `studyos_web` (Flutter Web) — ayrı projeler, ortak paketler.
- Ortak widget ve model katmanları bir Flutter paketi olarak extract edilebilir (gelecek optimizasyon).
