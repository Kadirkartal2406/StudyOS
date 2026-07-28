# StudyOS — UX Vizyon Gap Audit

**Belge Durumu:** Resmi değerlendirme (implementasyon planı değil)  
**Tarih:** 2026-07-19  
**Referans:** [`design-principles.md`](design-principles.md), [`product-vision.md`](product-vision.md)  
**Kapsam:** Mevcut Flutter ekranları, navigasyon, bilgi mimarisi, kullanıcı akışları  
**Yasak:** Kod, migration, endpoint, sprint/implementasyon planı

---

## Teşhis (tek cümle)

StudyOS teknik olarak öğrenme OS omurgasına yaklaşıyor; ürün olarak hâlâ öğrencinin yönettiği bir **özellik paneli (modül OS)**. Topic Work Surface yok; Dashboard Today değil; Goal/Plan/Revision/Resource/Chat kullanıcıya açık.

---

## Navigasyon

| Mevcut | Vizyon |
|--------|--------|
| Dashboard · Plan · Pomodoro · İstatistik · Profil | **Today · Topic Work Surface · Journey** |

Profil sekmesi aslında Bildirim Ayarları. Plan ve Pomodoro bağımsız uygulamalar. Today bir yüzey değil, Dashboard içinde bir kart şeridi.

---

## Bilgi mimarisi

| Katman | Vizyon | Mevcut | Sapma |
|--------|--------|--------|-------|
| Exam | Experience Pack | `exam_type` + layout strategy | Pack deneyimi sığ |
| Subject | Kapsayıcı | Hub = çalışma merkezi + 7 modül launcher | Öğrenme birimi gibi |
| Topic | Work Surface | Catalog listesi (tıklanmaz) + free-text | **Kritik boşluk** |
| Activities | Topic altında | Bağımsız CRUD modülleri | Dağınık |
| AI | Intent + Explain | Coach okuma + serbest Chat | Prompt ihlali |
| Plan | observe→suggest→accept→adapt | CRUD + Adaptive wizard | Kullanıcı planlıyor |

---

## Ekran bazlı değerlendirme

Her ekran için: kaldırmalı / taşımalı / sadeleşmeli / otomatikleşmeli / kullanıcının vermemesi gereken kararlar.

### Dashboard (Journey Hub) — **kontrol paneli, Today değil**

- **Kaldır:** Subject preview; Plan preview tekrarı; AI Coach kartı; hero’da gün/hafta/ay üçlü ilerleme yükü
- **Taşı:** Journey metrikleri → Journey; Active Exam → Journey/ayar; ders listesi → Subject container
- **Sadeleştir:** Next Action + günlük ilerleme + kalan bloklar + 1 satır Journey
- **Otomatikleştir:** Next Action RuleEngine’den
- **Vermesin:** Hangi modüle / derse gideceğini seçmek

### Bottom Nav — **modül OS**

- **Kaldır:** Plan / Pomodoro / İstatistik bağımsız sekmeleri
- **Taşı:** Pomodoro → Topic; Plan → sistem içi; İstatistik → Journey ikincil
- **Sadeleştir:** En fazla Today · bağlam · Journey
- **Vermesin:** Günün akışını 5 sekmeden seçmek

### Onboarding — **kısmen uyumlu**

- **Kaldır:** TYT/AYT’yi ayrı sınav ürünü gibi sunmak
- **Taşı:** Hedef detayları → Journey; baseline → gözlem
- **Sadeleştir:** Pack seçimi + müsaitlik + süre + living disclaimer
- **Otomatikleştir:** Katalog, starter plan, revision seed
- **Vermesin:** İlk günden hedef motoru / ders kurma

### Derslerim — **Subject’i birim gibi sunuyor**

- **Kaldır:** “Çalışılacak yer” metrik kartı algısı
- **Taşı:** İlerleme → Journey / Topic sinyali
- **Sadeleştir:** Container listesi → Topic’e geçiş
- **Otomatikleştir:** Active Exam ders seti
- **Vermesin:** Hangi ders modülüne gireceğini planlamak

### Subject Hub — **en ağır vizyon sapmalarından**

- **Kaldır:** 7 action chip; AI/Flashcard/Resources/Planner kart yığını
- **Taşı:** Bugün → Today; AI → Explain/Today; konular → Topic girişi
- **Sadeleştir:** Kısa durum + Topic listesi (tek iş: konuya gir)
- **Otomatikleştir:** Revision/plan/resource Subject altında
- **Vermesin:** Hangi modülü açacağını

### Topic yüzeyi — **YOK (kritik boşluk)**

- Tüm aktiviteler buraya bağlanmalı
- Work Surface: çalış / pomodoro / kaynak / soru / AI analizi
- Kullanıcı konu free-text yazmamalı; `topic_code` seçmeli

### Study Plan (+ formlar) — **kullanıcı planner**

- **Kaldır:** FAB CRUD, reorder, title/subject/topic/dakika/soru formları
- **Taşı:** Start/complete → Today/Topic; kaynaklar → Topic
- **Sadeleştir:** Salt okunur bugünkü bloklar + tek aksiyon
- **Otomatikleştir:** Üretim, sıra, süre, konu
- **Vermesin:** Ne çalışacağını planlamak

### Adaptive Planner — **wizard = kullanıcı plan kuruyor**

- **Kaldır:** 4 adımlı üretim sihirbazını ürün yüzeyi olarak
- **Taşı:** Gözlem sonrası sistem önerisi; kabul → Today
- **Sadeleştir:** İsteğe bağlı “öneriyi kabul et”
- **Vermesin:** Exam/net/gün/saat’i yeniden girmek (profilde var)

### Goals CRUD — **Prensip 1 ihlali**

- **Kaldır:** List/add/edit/detail
- **Taşı:** Salt okunur hedef → Journey; Explain kalabilir
- **Otomatikleştir:** Hedef oluşturma / güncelleme
- **Vermesin:** Goal type, target, priority, tarihler

### Revision — **kullanıcı tekrar motoru**

- **Kaldır:** Manuel FAB, generate butonu, ayrı `/revisions`
- **Taşı:** Due → Today Next Action veya Topic
- **Sadeleştir:** Çalışırken Good/Again
- **Otomatikleştir:** Generate, schedule
- **Vermesin:** Ne zaman üret / manuel kart ekle

### Resources — **organizasyon kullanıcıda**

- **Kaldır:** Global kütüphane yönetimi
- **Taşı:** Ekleme → Topic (gerekirse)
- **Sadeleştir:** URL/PDF ekle, konu bağlamında
- **Vermesin:** Kaynak klasörleme

### Pomodoro — **bağımsız zamanlayıcı**

- **Kaldır:** Bottom nav’dan bağımsız ana giriş
- **Taşı:** Topic / Next Action bağlamında; history → Journey
- **Sadeleştir:** Başlat/bitir; süre varsayılanı sistemden
- **Vermesin:** Hangi ders için pomodoro aramak

### Questions — **subject-first; topic free-text**

- **Taşı:** Kayıt → Topic; dağılım → Journey
- **Sadeleştir:** Intent D/Y/B; konu seçili gelir
- **Vermesin:** Konu yazmak; ders seçerek girmek

### Exams — **deneme modülü**

- **Taşı:** Sonuç → Journey/pack; zayıflık → Topic
- **Sadeleştir:** Sonuç gir → sistem sinyal üretir
- **Vermesin:** Tek denemeyle planı elle yeniden kurmak (Prensip 6)

### AI Coach — **kısmen uyumlu**

- Okuma / RuleEngine — iyi yön
- Dashboard’daki tekrar kartı kalkmalı; Today’e tek Explain

### AI Chat — **Prensip 5 ihlali**

- **Kaldır:** Serbest “Mesaj yaz…”; conversation yönetimi
- **Taşı:** Intent seçimli Explain (Topic/Today)
- **Vermesin:** Prompt yazmak

### Achievements — **Prensip 1**

- **Kaldır:** Ayrı ekran
- **Taşı:** Nadir mikro kutlama → Today
- **Vermesin:** Başarıları kontrol et / yönet

### Statistics — **derin panel**

- Bottom nav ana sekme olmamalı
- Özet → Journey; konu trendi → Topic
- **Vermesin:** Rapordan bugünü planlamak

### Profil (= Bildirimler) — **sahte profil**

- Bildirimler → ayarlar derinliği
- Active Exam / hedef → Journey

### Memory / AI Settings

- Ana akıştan çıkar; privacy toggle yeter
- **Vermesin:** AI’ya ne ezberleteceğini manuel girmek

---

## Yasak kararlar (özet)

1. Günün planını elle kurmak  
2. Goal oluşturmak  
3. Tekrar üretmek / manuel kart  
4. Kaynak kütüphanesi organize etmek  
5. Achievement’lara bakmak  
6. Modül seçmek (Hub / bottom nav)  
7. Serbest AI prompt  
8. Konuyu free-text yazmak  
9. Subject’i çalışma yüzeyi sanmak  
10. Tek olay/net ile yön değiştirmek  

---

## Hedef yüzeyler (yeniden organizasyon — plan değil)

1. **Today** — Next Action, günlük ilerleme, kalan bloklar, kısa Journey  
2. **Topic Work Surface** — çalış, pomodoro, soru, kaynak, AI Explain  
3. **Journey** — Active/Primary Exam, salt okunur hedef, ilerleme, deneme özeti  

**Sistem içi (modül olarak açılmaz):** Goal Engine, Revision Engine, Adaptive Planner, Achievements, Memory, Resource organization, AI Chat threads.

---

## Prensip skoru

| # | Prensip | Durum |
|---|---------|-------|
| 1 | Kullanıcı modül yönetmez | İhlal |
| 2 | Dashboard = Today | İhlal |
| 3 | Subject ≠ öğrenme birimi | Kısmi |
| 4 | Topic = Work Surface | Yok |
| 5 | Prompt yazmaz | İhlal |
| 6 | Tek olayla karar yok | Belirsiz UX |
| 7 | RE / LLM Explain | Kısmi |
| 8 | Önce gözlem | Zayıf |
| 9 | Sınav = ürün | Sığ |
| 10 | Bugünkü çalışmayı kolaylaştır | Çoğu özellik hayır |
| 11 | İkinci beyin | Uzak |

---

## Sonuç

Yeni özellik eklemek vizyonu yaklaştırmaz. Mevcut yüzeylerin **Today / Topic / Journey**’ye indirgenmesi ve motorların kullanıcıdan gizlenmesi gerekir.

Bu belge sprint veya implementasyon sırası içermez.
