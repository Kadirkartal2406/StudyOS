# Alignment Sprint-1 — Next Action Engine (Today Projection)

**Durum:** Onaylandı — implementasyon tamamlandı  
**Tür:** Alignment Sprint (feature sprint değil)  
**Backlog:** System Alignment Audit — kritik dönüşüm #1  
**Tamamlandı:** 2026-07-20  
**Referans:** Product Vision · Design Principles · LOS v2.0 · UX Gap Audit · System Alignment Audit

---

## 0. Alignment Sprint nedir?

Bu sprint bir “Dashboard redesign” veya yeni özellik sprinti değildir.

**Alignment Sprint**, mevcut StudyOS yüzeyini Learning Operating System vizyonuna hizalar.

```
Feature OS  →  Learning Operating System
```

Kurallar:

- Yeni modül eklenmez.
- Öncelik: sadeleştir · birleştir · sistem içine al · otomatikleştir.
- Her değişiklik şu sorudan geçer: *Bu, StudyOS’u ikinci beyin vizyonuna yaklaştırıyor mu?*
- Alignment backlog öncelik sırası değişmez.

Bundan sonraki tüm sprintler aynı mantıkla ilerler. Bu belge o sözleşmenin ilk örneğidir.

---

## 1. Bu sprintin gerçek merkezi

**Merkez: Next Action Engine** — LOS Decision Engine’in ilk görünür implementasyonu.

Dashboard / Today Screen yalnızca bunun **yansımasıdır**.

Bütün kararlar şu soruya göre alınır:

> Bugün kullanıcıya göstereceğimiz **tek şey** ne olmalı?

Kartları azaltmak hedef değildir.  
**Today oluşturmak** hedeftir.

```
Decision Engine Projection v0
  (Observation > Decision; tek next_action)
        ↓
Today Engine
        ↓
Today Projection (API SSOT)
        ↓
Today Screen (tek Primary Action + bağlam)
```

---

## 2. Davranış hedefi (ürün)

Today bilgi göstermemelidir. Today **harekete geçirmelidir**.

Kullanıcı uygulamayı açınca:

- düşünmeyecek
- seçim yapmayacak
- modül aramayacak

yalnızca **çalışmaya başlayacak**.

Pasif hub → aktif Today.

---

## 3. Başarı kriteri

Başarı “Dashboard değişti” değildir.

> Kullanıcı uygulamayı açtıktan sonra **5 saniye içinde**, hiç düşünmeden, çalışmaya başlayabiliyor mu?

Ölçülebilir smoke:

1. Açılışta **yalnızca bir** Primary Action / CTA görünür.
2. CTA’ya basmak için ek seçim gerekmez; ikinci CTA yoktur.
3. Subject / Plan / AI Coach kartı / modül listesi Today’de yok.
4. Reason satırı Next Action’ın altındadır (ayrı AI okuma değil).
5. Bağlam satırları (kalan blok, tekrar, trend notu) tıklanabilir birincil görev değildir.

---

## 4. Üç katman (Today yalnızca ekran değildir)

| Katman | Rol |
|--------|-----|
| **Today Engine** | Günlük projeksiyon mantığı: Decision çıktısını Today alanlarına çevirir (ilerleme, kalan sinyal, journey satırı). |
| **Today Projection** | Backend SSOT payload: `next_action` + Today alanları. Tüm istemciler (mobile, ileride widget/web/watch) aynı kararı alır. |
| **Today Screen** | Flutter yalnızca render eder. Decision istemcide **yoktur**. |

---

## 5. Next Action Engine = Decision Engine Projection (v0)

Next Action “geçici heuristic hack” değildir.

Mimari tanım:

> **Decision Engine Projection** — LOS Decide→Project aşamasının ilk implementasyonu.

v0 kurallar basit olabilir; yapı Confidence / Observation / Living Plan geldiğinde **aynı projection üzerinden büyür**.

### Tek karar (zorunlu)

StudyOS aynı anda birden fazla birincil görev göstermez.  
Projection’da **tek** `next_action` vardır. İkinci aksiyon alanı yok.

### v0 karar önceliği (sunucu)

Observation / yetersiz kanıt her zaman kesin Decide’ten önce gelir (§13).

Kanıt yeterliyse (v0 basit eşikler):

1. Due revision → Next Action = tekrar  
2. Bugün incomplete plan → Next Action = o blok  

Kanıt yetersiz veya emin değilse → **güvenli varsayılan** (§13); uydurma “kesin zayıf konu” yok.

`reason` RuleEngine evidence / kural metninden gelir.  
AI recommendation **bağımsız kart değildir**; Next Action’ın reason/dil katmanına **erer**.

Kullanıcı “AI tavsiyesi okumaz”. Sistem “bugün şunu yap” der.

---

## 6. Today Projection içeriği (izinli yüzey)

### Kahraman — Next Action (tek Primary Action)

Örnek biçim:

```
✓ TYT Matematik · Problemler
25 dakika çalış
[ Başla ]   ← tek CTA
```

- Başlık (ne yapılacak)
- Reason / süre bağlamı
- **Yalnızca bir** primary CTA

### Destek — yalnızca bağlam (asla ikinci CTA değil)

Kullanıcı “Hangisini yapayım?” diye düşünmemelidir. Aşağıdakiler bilgi satırıdır; tıklanınca alternatif görev seçtirmez:

- Bugün 2 blok kaldı  
- 1 tekrar bekliyor  
- Son 2 haftada bu konuda düşüş var *(varsa; v0’da opsiyonel/kısıtlı)*

**Günlük ilerleme** — hareket bağlamı (CTA değil)

**Journey satırı** — mikro bağlam. Today Journey ekranına dönüşmez. Kahraman her zaman Next Action’tır.

---

## 7. Deep link — geçici vs hedef mimari

### Bu sprint (geçici)

Topic Work Surface henüz yok. CTA mevcut yüzeylere deep link edebilir (plan / revision / pomodoro).

### Hedef mimari (zorunlu kayıt)

```
Next Action
    ↓
Topic Work Surface
    ↓
Araçlar (pomodoro, soru, kaynak, …)
```

Geçici deep link borçtur; Alignment #3 (Topic Work Surface) bunu kapatır. Bu sprint hedef mimariyi bozacak kalıcı “modül hub” CTA’sı üretmez.

---

## 8. Mevcut ihlaller (neden Alignment)

1. Journey Hub + çoklu kart → seçim yükü  
2. Today Tasks → Plan / Pomodoro / Revision modül seçimi  
3. AI Coach ayrı kart + Koç escape  
4. Subject / Plan preview → hub davranışı  
5. Hero journey paneli → Today’i Journey’ye çevirme riski  
6. Decision istemciye dağılmış / yok → SSOT yok  

---

## 9. Kaldırılacak / eritilecek / taşınacak

### Today yüzeyinden kalkar

- Subject preview  
- Plan preview  
- Ayrı AI Coach kartı + `/ai-coach` CTA  
- Üçlü journey bar / stage paneli  
- Modül tile listesi (Plan / Pomodoro / Revision)

### Eritilir

- AI recommendation + reason → **Next Action reason**  
- Plan/revision sayıları → **kalan sinyal cümlesi** (liste değil)

### Journey’ye bırakılır (bu sprintte Journey ekranı yok)

- Haftalık/aylık %, stage, Primary detay, dominant Active switcher  
- Today’de yalnızca mikro Journey satırı kalır  
- Active Exam erişimi: AppBar menü / geçici demote (nav #2’ye kadar)

---

## 10. Backend (yalnızca seçenek B)

**A yok.** Decision istemcide olmaz.

- `GET /dashboard` (veya aynı kaynak) additive **Today Projection** üretir.
- Zorunlu: `next_action` (title, reason, action_type, deep_link_hint — geçici).
- Today Engine alanları: progress, remaining summary strings, journey line.
- Mevcut alanlar silinmez (breaking yok); Today Screen kullanmaz.
- Migration / yeni tablo yok.
- RuleEngine / plan / revision verisinden sunucu türetir.

Flutter: parse + render. Karar yok.

---

## 11. Flutter etkisi

- Dashboard screen → **Today Screen** (Decision yok).  
- Composition: Next Action → Progress → Remaining signal → Journey line.  
- Bottom nav yapısı değişmez; label “Today” olabilir (Alignment #2 değil).  
- Testler başarı kriterine göre (5 sn / tek CTA / kart yokluğu).

Yeni feature modülü yok. Dashboard feature içinde Alignment.

---

## 12. Next Action tek olmalıdır

StudyOS hiçbir zaman kullanıcıya aynı anda birden fazla birincil görev göstermez.

- Bir yüzeyde **yalnızca bir Primary Action** bulunur.
- Diğer her şey yalnızca bağlamdır.
- Bağlam satırları ikinci CTA, ikinci “görev kartı” veya seçim listesi olamaz.
- Kullanıcı “Hangisini yapayım?” diye düşünmemelidir.

> StudyOS her zaman **tek karar** üretir. Bu, Learning Operating System’in temel davranışıdır.

Flutter’da birden fazla `FilledButton` / eşit ağırlıklı aksiyon yasaktır.  
Backend projection’da `next_actions[]` (çoğul) üretilmez.

---

## 13. Today başarısız olabilir (Observation > Decision)

Bazı günlerde sistem yeterli kanıta sahip olmayabilir.

Bu durumda StudyOS **karar uydurmaz**.

- Emin olmadığı konuda kesin öneri üretmez (“bu konu zayıf, şunu yap” iddiası yok).
- **Observation Mode, Decision Mode’dan her zaman önceliklidir.**

*(Bu sprintte tam Observation Engine kurulmaz — Alignment #9. Ancak Decision Projection v0 bu öncelik kuralına uymak zorundadır.)*

### Güvenli varsayılanlar (uydurma değil)

Kanıt yetersizken tek Next Action şunlardan biri olur:

- Kısa odak çalışması öner  
- İlk / sıradaki plan bloğunu öner (varsa)  
- Gözleme devam et diliyle güvenli çalışma (reason: henüz yeterli sinyal yok)

`reason` açıkça belirsizliği yansıtabilir (“Seni tanımaya devam ediyoruz”).  
Kesinlik iddiası yoksa `confidence_tone` / eşdeğer bayrak düşük kalır (additive alan; ileride Confidence Engine ile birleşir).

---

## 14. Explicit non-goals

- Topic Work Surface / `topic_code` bağlama  
- Navigation → Today · Topic · Journey yapı değişimi  
- Living Plan / Study Plan CRUD kaldırma  
- Goals / Revision / Resources / Achievements sistem-içi taşıma  
- Pomodoro sensör refactor  
- AI Chat / Explain endpoint  
- Tam Confidence Engine / tam Observation Mode ürünü (öncelik kuralı §13 hariç)  
- NotebookLM  
- Statistics → Journey ekranı  
- Subject Hub sadeleştirme  
- Breaking API silme / migration  
- Birden fazla Primary Action / görev seçtiren Today  

---

## 15. Riskler

| Risk | Mitigasyon |
|------|------------|
| v0 kural kalitesi | Observation önceliği; uydurma yasak; güvenli varsayılan |
| İkinci CTA kaçakları | §12 sert kural; test: tek FilledButton |
| Bağlamın “görev” gibi görünmesi | Tıklanmaz / birincil stil yok |
| Geçici deep link alışkanlığı | Hedef mimari belgede sabit; #3’te kesilir |
| Journey satırının şişmesi | Tek satır; bar/panel yasak |
| Scope creep | Non-goals sert |

---

## 16. Implementasyon sırası (onay sonrası)

1. Backend: Decision Engine Projection v0 + Today Projection (§12–13 kuralları) + test  
2. Flutter: model/entity parse  
3. Today Screen: tek Primary Action + bağlam satırları + AI eritme  
4. Test: 5 sn / tek CTA / uydurma yok + doküman güncellemesi  

Onaysız kod yok.

---

## 17. Tek cümlelik özet

> Alignment Sprint-1, Dashboard’ı süslemez; **tek kararlı Next Action Engine’i** doğurur — kanıt yetmezse uydurmaz, Observation’ı Decide’ten önde tutar; Today Projection SSOT backend’de, Flutter yalnızca render.
