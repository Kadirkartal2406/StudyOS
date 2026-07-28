# StudyOS — Değişmez Tasarım Prensipleri

**Belge Durumu:** Resmi — Kalıcı  
**Sürüm:** 1.0  
**Tarih:** 2026-07-19  
**Üst belge:** [`product-vision.md`](product-vision.md) · [`learning-operating-system.md`](learning-operating-system.md)

> Bundan sonraki her ekran, API, mimari karar ve UX bu prensiplere göre değerlendirilir.  
> Teknik doğruluk yetmez; ürün vizyonuna uygunluk zorunludur.

StudyOS bir özellik koleksiyonu değildir.  
StudyOS **öğrencinin ikinci beynidir.**

---

## 1. Kullanıcı modülleri yönetmeyecek

Kullanıcı Goal oluşturmaz, Revision yönetmez, Achievement bakmaz, Planner oluşturmaz, Resource organize etmez.

Bunlar **sistemin iç mekanizmalarıdır.**

Kullanıcı yalnızca:

- Bugün ne yapacağını görür
- Çalışır
- Gerekirse konu seçer
- Gerekirse kaynak ekler
- Gerekirse soru çözer

Sistem geri kalan her şeyi kendisi yönetir.

---

## 2. Dashboard bir kontrol paneli değildir

**Dashboard = Today.**

İlk ekranda cevap: *Bugün ne yapacağım?*

Dashboard’da onlarca kart olmaz. İzinli yüzey:

- Next Action
- Günlük ilerleme
- Kalan çalışma blokları
- Kısa Journey özeti

Bunun dışında mümkün olduğunca boş kalır.

---

## 3. Subject öğrenme birimi değildir

Subject yalnızca kapsayıcıdır. Asıl öğrenme birimi **Topic**’tir.

```
Exam → Subject → Topic → Study → Data → AI → Next Action
```

Bu hiyerarşi korunur.

---

## 4. Topic bir sayfa değildir

Topic bir **Work Surface**’tir.

Konuya girildiğinde kullanıcı çalışır, pomodoro başlatır, kaynak/PDF ekler, NotebookLM quiz üretir, AI analizi görür.

Tüm aktiviteler Topic etrafında döner. Topic yalnızca bilgi gösteren ekran olmaz.

---

## 5. Kullanıcı prompt yazmayacak

NotebookLM, LLM, AI Coach, Question Generator, Planner, Explain — hepsi **sistem promptlarıyla** çalışır.

Kullanıcı yalnızca intent seçer (konu, soru sayısı, zorluk…). Prompt’u sistem üretir.

---

## 6. AI tek olaya göre karar vermeyecek

Tek yanlış ≠ zayıf konu.  
Tek doğru ≠ öğrendi.

AI; trend, confidence, sample size, consistency, time, accuracy, revision history, çalışma alışkanlığını birlikte değerlendirir.

**Minimum veri oluşmadan plan değiştirilmez.**

---

## 7. AI yalnızca önerir

**Rule Engine karar verir. LLM yalnızca açıklar.**

LLM plan üretmez, hedef üretmez, ders seçmez, karar vermez.

---

## 8. Mevcut sistem varsa önce onu öğren

İlk gün kullanıcıyı değiştirmeye çalışma. Önce gözlemle, veri topla, sonra öner.

Sistemi yoksa: hedef + müsaitlik + süreye göre başlangıç planı; planın zamanla kişiselleşeceği açıkça belirtilir.

---

## 9. Her sınav ayrı ürün gibi

YKS, KPSS Lisans / Önlisans / Ortaöğretim, YDS, ALES… aynı ekranın filtrelenmiş hali değildir.

Her biri kendi deneyimine sahiptir. Onboarding, hedefler, dashboard, subject/topic yapısı sınava göre değişebilir.

---

## 10. Her yeni özellik şu sorudan geçer

> Bu özellik, kullanıcının **bugünkü çalışmasını daha kolay mı** yapıyor?

Hayırsa: reddet, ertele veya başka yere taşı.

---

## 11. Ana amaç ve sprint kabul kriteri

StudyOS; öğrencinin yerine düşünen, yönlendiren, davranışını öğrenen, zamanla kişiselleşen AI destekli **öğrenme işletim sistemidir.**

Her sprint sonunda zorunlu değerlendirme:

> **Bu sprint StudyOS’u gerçekten ikinci beyin vizyonuna yaklaştırdı mı?**

Yaklaştırmadıysa sprint tamamlanmış sayılmaz.
