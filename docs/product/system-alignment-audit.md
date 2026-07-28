# StudyOS — System Alignment Audit

**Belge Durumu:** Resmi — Kalıcı denetim (sprint / kod / API değildir)  
**Sürüm:** 1.0  
**Tarih:** 2026-07-19  
**Referans:**  
[`product-vision.md`](product-vision.md) · [`design-principles.md`](design-principles.md) · [`learning-operating-system.md`](learning-operating-system.md) · [`ux-vision-gap-audit.md`](ux-vision-gap-audit.md)

> Bu belge mevcut sistemin **gerçek durumunu** LOS ve Design Principles’a göre ortaya koyar.  
> Sprint planı, implementasyon sırası talimatı veya kod tasarımı değildir.  
> Yeni özellik geliştirmeden önce bu hizalama tamamlanmalıdır.

---

## Genel teşhis

StudyOS onlarca sprint sonunda **zengin bir modül OS** haline gelmiştir.  
Yeni Product Vision ve Learning Operating System ise **modül OS’i reddeder**.

| Katman | Bugün | LOS |
|--------|-------|-----|
| Ürün birimi | Ekran / CRUD modülü | Learning Loop |
| Öğrenme birimi | Subject (+ free-text topic) | Topic (`topic_code`) + Evidence + Confidence |
| Karar | Kullanıcı + kısmen RuleEngine | RuleEngine (eşiği); LLM Explain Only |
| Bugün yüzeyi | Journey Hub Dashboard | Today Engine → tek Next Action |
| Plan | Kullanıcı CRUD + Adaptive wizard | Living Plan (observe→suggest→accept→adapt) |
| Observation / Confidence | Kodda yok | Zorunlu LOS katmanları |
| Navigasyon | Dashboard · Plan · Pomodoro · İstatistik · Profil | Today · Topic · Journey |

**Özet skor (ürün ortalaması): ~3.2 / 10** — domain omurgası (Exam/Subject/Topic catalog, RuleEngine çekirdeği) var; ürün davranışı hâlâ eski vizyon.

---

## Özellik: Dashboard (Journey Hub)

### 1. Bugünkü amacı nedir?
Active Exam + Primary hedef + journey barları + bugünkü görevler + AI tip + ders/plan önizlemesi sunan giriş hub’ı.

### 2. LOS’taki gerçek amacı ne olmalı?
**Today Engine projeksiyonu:** tek Next Action, günlük ilerleme, kalan bloklar, kısa Journey satırı. Kontrol paneli değil.

### 3. Bugünkü davranış
Kullanıcı kartları okur, Active Exam değiştirir, Plan/Pomodoro/Revision/Subjects/AI Coach’a dağılır.

### 4. Vizyondaki davranış
Açar → Next Action’ı görür → çalışır. Modül seçmez.

### 5. Problemler
Dashboard = Journey Hub + kart yığını. Next Action yok. Sense→Decide→Project zinciri kullanıcıya yansımıyor. Design Principle 2 ihlali.

### 6. Sistem neyi kullanıcıya yaptırıyor?
Hangi karta / modüle gideceğini seçmeyi; bugünü kendi yorumlamayı.

### 7. Aslında bunu sistem mi yapmalı?
Evet — Decision + Today Engine.

### 8. Ne olmalı?
**Sadeleşmeli + Today’e dönüşmeli.** Journey metrikleri Journey’ye. Kart kalabalığı kalkmalı.

### 9. LOS puanı: **3 / 10**
Aggregation ve RuleEngine tip var; Today OS değil.

---

## Özellik: Bottom Navigation

### 1. Bugünkü amacı
Beş sekmeli modül erişimi: Dashboard, Plan, Pomodoro, İstatistik, Profil(=bildirim).

### 2. LOS’taki amacı
En fazla üç yüzey: Today · Topic (bağlam) · Journey. Modül fırlatıcı değil.

### 3. Bugünkü davranış
Kullanıcı gününü Plan/Pomodoro/İstatistik arasında böler.

### 4. Vizyondaki davranış
Today’den çalışır; derin istatistik Journey’de; Pomodoro Topic içinde.

### 5. Problemler
Modül OS’in iskeleti. Principle 1–2, LOS §13.1–2 ihlali.

### 6. Kullanıcıya yaptırılan
OS’i işletmek.

### 7. Sistem mi yapmalı?
Navigasyon politikası sistem ürün kararı; kullanıcı araç seçmemeli.

### 8. Ne olmalı?
**Sadeleşmeli / yeniden çerçevelenmeli** — Plan/Pomodoro/İstatistik sekme olarak kalkmalı veya ikincilleşmeli.

### 9. Puan: **1 / 10**

---

## Özellik: Onboarding / Learning Profile

### 1. Bugünkü amacı
Exam targets, branch, net/üniversite, müsaitlik, baseline; hard gate.

### 2. LOS’taki amacı
Exam pack bağlamı + Observation başlangıcı + (gerekirse) starter Living Plan sözleşmesi. Goal motoru değil.

### 3. Bugünkü davranış
Çok adımlı form doldurur; “hedef” alanları girer.

### 4. Vizyondaki davranış
Sınavını ve müsaitliğini söyler; sistem gözlem veya starter planı kurar; living disclaimer.

### 5. Problemler
Kısmen uyumlu ama hedef/CRUD kokusu var; Observation Mode ürün olarak yok; TYT/AYT ayrı sınav gibi.

### 6. Kullanıcıya yaptırılan
İlk günden parametre yönetimi.

### 7. Sistem mi?
Subject seed / starter plan / observation kapıları sistemde.

### 8. Ne olmalı?
**Sadeleşmeli.** Hedef detayı Journey’ye (salt okunur). Observation açık sözleşme.

### 9. Puan: **5 / 10**

---

## Özellik: Subjects (Derslerim)

### 1. Bugünkü amacı
Active Exam’e göre ders listesi; metrik kartları; Subject Hub’a giriş.

### 2. LOS’taki amacı
Subject = kapsayıcı. Topic’e geçiş listesi; öğrenme birimi değil.

### 3. Bugünkü davranış
Dersi seçer → Hub’a girer → modül seçer.

### 4. Vizyondaki davranış
Gerekirse kapsayıcıya bakar → Topic seçer → çalışır. Veya Today doğrudan Topic’e götürür.

### 5. Problemler
Subject çalışma merkezi gibi. Topic tıklanmaz.

### 6. Kullanıcıya yaptırılan
Ders-seviyesinde navigasyon planı.

### 7. Sistem mi?
Ders seti Active Exam’den; Next Action Topic seçer.

### 8. Ne olmalı?
**Sadeleşmeli** — container. Hub modül launcher kalkmalı.

### 9. Puan: **4 / 10**

---

## Özellik: Subject Hub

### 1. Bugünkü amacı
Subject work center: 7 action chip + progress/today/revision/planner/exam/AI/resources/topics/flashcards kartları.

### 2. LOS’taki amacı
Kısa durum + Topic listesi. Aktivite Subject’te dağılmaz; Topic Work Surface’te birleşir.

### 3. Bugünkü davranış
Modül fırlatır (soru, tekrar, plan, pomodoro, deneme, kaynak, planner).

### 4. Vizyondaki davranış
Konuya girer. Modül seçmez.

### 5. Problemler
En ağır vizyon sapmalarından. Subject = öğrenme birimi gibi. LOS Principle 3 ihlali.

### 6. Kullanıcıya yaptırılan
Hangi aracı açacağını kararlaştırmak.

### 7. Sistem mi?
Evet — Today/Topic hangi aktivitenin uygun olduğuna karar verir.

### 8. Ne olmalı?
**Sadeleşmeli / büyük ölçüde Topic’e taşınmalı.** Action bar kaldırılmalı veya gizlenmeli.

### 9. Puan: **2 / 10**

---

## Özellik: Topic Catalog / Topic yüzeyi

### 1. Bugünkü amacı
Catalog seed + Hub’da salt okunur liste (`topic_code` display). Activity bağ yok. Work Surface yok.

### 2. LOS’taki amacı
Öğrenme birimi + Work Surface + Evidence bağlama noktası. Confidence/Decide burada yaşar.

### 3. Bugünkü davranış
Konuları görür; tıklayamaz. Formlarda free-text topic yazar.

### 4. Vizyondaki davranış
Topic’e girer; çalışır, pomodoro, kaynak, soru, Explain.

### 5. Problemler
**Kritik boşluk.** Catalog var, ürün yok. Tüm Evidence free-text / subject-first.

### 6. Kullanıcıya yaptırılan
Konuyu metin olarak hatırlamak / yazmak.

### 7. Sistem mi?
Catalog seçimi + aktivite bağlama sistemde; kullanıcı intent seçer.

### 8. Ne olmalı?
**Topic Work Surface olarak kurulmalı** (yeni yüzey — mevcut “özellik şişirme” değil, omurga). Aktiviteler Topic’e taşınır.

### 9. Puan: **1 / 10** (catalog 4, ürün 0 → birleşik 1)

---

## Özellik: Study Plan

### 1. Bugünkü amacı
Günlük plan CRUD: ekle, düzenle, sil, sırala, start/complete/skip.

### 2. LOS’taki amacı
Living Plan’ın günlük yansıması + Today blokları. Kullanıcı plan tasarlamaz.

### 3. Bugünkü davranış
Plan yöneticisi gibi çalışır; bloğu elle kurar.

### 4. Vizyondaki davranış
Next Action’ı yapar; complete. Plan üretimi sistemde.

### 5. Problemler
Principle 1 ihlali. Living Plan / Observation yok. `topic_code` yok.

### 6. Kullanıcıya yaptırılan
Planner olmak.

### 7. Sistem mi?
Evet — üret, sırala, adapte et.

### 8. Ne olmalı?
**Sistem içine + Today’e.** CRUD yüzeyi kaldırılmalı / demote. Bottom nav Plan kalkmalı.

### 9. Puan: **2 / 10**

---

## Özellik: Adaptive Planner

### 1. Bugünkü amacı
Wizard (exam/net/gün/saat) → RuleEngine draft → accept → study plans.

### 2. LOS’taki amacı
Suggest→Accept parçası; Observation sonrası. Parametreler profilde varsa tekrar sorulmaz. Living Plan motoru.

### 3. Bugünkü davranı
Kullanıcı plan sihirbazı çalıştırır.

### 4. Vizyondaki davranış
Sistem önerir; kullanıcı kabul/reddeder.

### 5. Problemler
Kullanıcıya açık planner modülü. Observation yok. Accept sonrası “living adapt” yok.

### 6. Kullanıcıya yaptırılan
Plan parametrelerini yeniden girmek.

### 7. Sistem mi?
Generate sistem; accept kullanıcı niyeti.

### 8. Ne olmalı?
**Sistem içine taşınmalı.** UI olarak wizard modülü değil; Suggest yüzeyi.

### 9. Puan: **4 / 10** (RuleEngine doğru; ürün yüzeyi yanlış)

---

## Özellik: Goals

### 1. Bugünkü amacı
Goal CRUD + progress + Explain.

### 2. LOS’taki amacı
İç motor. Journey’de salt okunur hedef. Kullanıcı Goal yönetmez.

### 3. Bugünkü davranış
Hedef oluşturur, düzenler, siler, tip/öncelik seçer.

### 4. Vizyondaki davranış
Hedefini Journey’de görür; sistem günceller.

### 5. Problemler
Principle 1 doğrudan ihlal.

### 6. Kullanıcıya yaptırılan
Goal Engine işletmek.

### 7. Sistem mi?
Evet.

### 8. Ne olmalı?
**Sistem içine + Journey’ye.** Kullanıcı CRUD kaldırılmalı.

### 9. Puan: **1 / 10**

---

## Özellik: Revision

### 1. Bugünkü amacı
Due kartlar, generate, manuel ekle, Good/Again/Hard/Easy, explain.

### 2. LOS’taki amacı
İç motor + Today/Topic sert girdisi. Kullanıcı revision yönetmez; çalışırken yanıtlar.

### 3. Bugünkü davranış
Tekrar uygulamasını işletir; generate/manuel ekler.

### 4. Vizyondaki davranış
Today “tekrar zamanı” derse yapar; Good/Again verir.

### 5. Problemler
Ayrı modül. Manuel/generate kullanıcıda. `topic_code` yok.

### 6. Kullanıcıya yaptırılan
SRS yöneticisi olmak.

### 7. Sistem mi?
Generate/schedule sistem; review etkileşimi kullanıcı.

### 8. Ne olmalı?
**Sistem içine + Today/Topic’e.** Ayrı `/revisions` demote.

### 9. Puan: **3 / 10**

---

## Özellik: Resources

### 1. Bugünkü amacı
Global/plan kaynak CRUD (title, URL, tip).

### 2. LOS’taki amacı
Topic Work Surface’te gerekirse kaynak ekleme. Organizasyon sistemde.

### 3. Bugünkü davranış
Kaynak kütüphanesi yönetir.

### 4. Vizyondaki davranış
Konudayken kaynak ekler; klasörlemez.

### 5. Problemler
Principle 1. Topic bağ yok.

### 6. Kullanıcıya yaptırılan
Resource organize etmek.

### 7. Sistem mi?
Organizasyon evet; ekleme intent kullanıcı.

### 8. Ne olmalı?
**Topic’e taşınmalı;** global kütüphane kaldırılmalı/demote.

### 9. Puan: **2 / 10**

---

## Özellik: Pomodoro / Study Sessions

### 1. Bugünkü amacı
Bağımsız zamanlayıcı + history; bottom nav.

### 2. LOS’taki amacı
Davranış sensörü; Topic/Next Action bağlamında. Sense girdisi.

### 3. Bugünkü davranış
Süre seçer, başlatır; ders bağlamı zayıf.

### 4. Vizyondaki davranış
Next Action/Topic’ten başlatır; bitirir. Sistem kaydeder.

### 5. Problemler
Bağımsız app. Evidence Topic’e zayıf bağlanır.

### 6. Kullanıcıya yaptırılan
Hangi ders için timer açacağını aramak.

### 7. Sistem mi?
Bağlam ve varsayılan süre sistem; start/stop kullanıcı.

### 8. Ne olmalı?
**Topic / Today’e taşınmalı.** Nav sekmesi kalkmalı. History → Journey ikincil.

### 9. Puan: **4 / 10**

---

## Özellik: Questions

### 1. Bugünkü amacı
Soru kaydı CRUD + istatistik; subject + free-text topic.

### 2. LOS’taki amacı
Topic Work Surface’te Performance Evidence girişi. Intent: D/Y/B (+ zorluk).

### 3. Bugünkü davranış
Kayıt formu doldurur; konu yazar; stats’a bakar.

### 4. Vizyondaki davranış
Konudayken sonucu girer; trend sistemde.

### 5. Problemler
Subject-first CRUD app. Confidence Engine yok. Tek kayıt Decide’i bozabilir zihniyet.

### 6. Kullanıcıya yaptırılan
Tracking uygulaması işletmek.

### 7. Sistem mi?
Aggregate/Confidence/Decide sistem; ham sonuç kullanıcı.

### 8. Ne olmalı?
**Topic’e taşınmalı;** stats Journey. CRUD sadeleşmeli.

### 9. Puan: **3 / 10**

---

## Özellik: Exam Tracking

### 1. Bugünkü amacı
Deneme CRUD + net/trend stats.

### 2. LOS’taki amacı
Exam pack Journey sinyali + Evidence (dikkat: tek deneme Living Plan değiştirmez).

### 3. Bugünkü davranış
Deneme girer, grafik okur, planı elle kurma eğilimi.

### 4. Vizyondaki davranış
Sonuç girer; sistem Topic sinyali üretir; Decide eşiği bekler.

### 5. Problemler
Modül OS. Pack deneyimi sığ. Topic kırılımı zayıf.

### 6. Kullanıcıya yaptırılan
Deneme uygulaması + yorumlama.

### 7. Sistem mi?
Yorum/trend/Decide sistem; sonuç girişi kullanıcı.

### 8. Ne olmalı?
**Journey’ye + Evidence’a.** Pack’e göre sade giriş.

### 9. Puan: **4 / 10**

---

## Özellik: Statistics

### 1. Bugünkü amacı
Özet/günlük/haftalık/aylık/dersler; bottom nav ana sekme.

### 2. LOS’taki amacı
Journey ikincil; Topic trendi Work Surface’te. Today’i planlamak için değil.

### 3. Bugünkü davranış
Rapor okuyarak yön arar.

### 4. Vizyondaki davranış
Çalışır; gerekirse Journey’de bakar.

### 5. Problemler
Ana navigasyon. Bugünkü çalışmayı zorlaştırabilir (Principle 10).

### 6. Kullanıcıya yaptırılan
Kendi Decide’i olmak.

### 7. Sistem mi?
Evet — Decide kullanıcıya rapor dayatmaz.

### 8. Ne olmalı?
**Journey’ye taşınmalı;** nav’dan çıkarılmalı.

### 9. Puan: **3 / 10**

---

## Özellik: AI Coach (insights)

### 1. Bugünkü amacı
RuleEngine overview/recommendations/trends — okuma paneli.

### 2. LOS’taki amacı
Decide çıktısının Explain/Today reason katmanı. Ayrı “AI app” değil.

### 3. Bugünkü davranış
Insight listesi gezer.

### 4. Vizyondaki davranış
Today’de nedeni görür; gerekirse Explain.

### 5. Problemler
Doğru motor, yanlış yüzey. Dashboard’da ikinci kart.

### 6. Kullanıcıya yaptırılan
Hangi insight’ı “kullanacağını” seçmek.

### 7. Sistem mi?
Öneri seçimi Decide; dil Explain.

### 8. Ne olmalı?
**Today / Journey’ye sadeleşmeli.** Ayrı ekran demote.

### 9. Puan: **6 / 10**

---

## Özellik: AI Chat

### 1. Bugünkü amacı
Serbest “Mesaj yaz…” sohbeti; conversation yönetimi.

### 2. LOS’taki amacı
Yok / yasak. Intent seçimli Explain. Prompt yazılmaz.

### 3. Bugünkü davranış
Prompt yazar; thread yönetir.

### 4. Vizyondaki davranış
“Neden?” / “Bu konuyu açıkla” intent’i seçer.

### 5. Problemler
Design Principle 5 + LOS Principle 7 ağır ihlal. LLM Decide’e kayma riski.

### 6. Kullanıcıya yaptırılan
Chatbot işletmek.

### 7. Sistem mi?
Prompt builder sistemde.

### 8. Ne olmalı?
**Kaldırılmalı veya Explain-only intent’e indirgenmeli.** Serbest chat ürün yüzeyi olmamalı.

### 9. Puan: **0 / 10**

---

## Özellik: Memory / AI Settings

### 1. Bugünkü amacı
Memory CRUD + provider ayarları.

### 2. LOS’taki amacı
Learning Memory iç motor (davranış modeli). Kullanıcı ezber editörü değil. Settings derinlikte.

### 3. Bugünkü davranış
Manuel memory ekler; AI ayarı kurcaları.

### 4. Vizyondaki davranış
Sistem öğrenir; privacy toggle yeter.

### 5. Problemler
Learning Memory ≠ kullanıcı not defteri. CRUD sapması.

### 6. Kullanıcıya yaptırılan
AI’ya ne ezberleteceğini yazmak.

### 7. Sistem mi?
Evet.

### 8. Ne olmalı?
**Sistem içine.** Privacy → ayarlar. CRUD demote/kaldır.

### 9. Puan: **2 / 10**

---

## Özellik: Achievements

### 1. Bugünkü amacı
Rozet listesi, check, explain.

### 2. LOS’taki amacı
İç motor; nadir mikro geri bildirim. Karar üretmez.

### 3. Bugünkü davranış
Başarı ekranına bakar / kontrol eder.

### 4. Vizyondaki davranış
Bakmaz; sistem sessizce işler veya Today’de mikro kutlar.

### 5. Problemler
Principle 1. Decide’e karışma riski düşük ama dikkat dağıtır.

### 6. Kullanıcıya yaptırılan
Achievement yönetmek/izlemek.

### 7. Sistem mi?
Evet.

### 8. Ne olmalı?
**Sistem içine / Today mikro.** Ekran kaldırılmalı.

### 9. Puan: **2 / 10**

---

## Özellik: Profile (Bildirim Ayarları)

### 1. Bugünkü amacı
“Profil” sekmesi → bildirim toggles. Gerçek Journey/profile yok.

### 2. LOS’taki amacı
Journey (hedef, Active/Primary, ilerleme) + ayarlar derinliği.

### 3. Bugünkü davranış
Bildirim aç/kapa.

### 4. Vizyondaki davranış
Journey’ye bakar; ayar nadiren.

### 5. Problemler
Sahte profil. Journey yüzeyi eksik.

### 6. Kullanıcıya yaptırılan
—

### 7. Sistem mi?
Journey projeksiyonu sistem; prefs kullanıcı.

### 8. Ne olmalı?
**Journey’ye dönüşmeli;** bildirimler ayarlara.

### 9. Puan: **2 / 10**

---

## Özellik: NotebookLM / Content Generation

### 1. Bugünkü amacı
Üründe yok (UI yok). Flashcards placeholder.

### 2. LOS’taki amacı
Evidence üretici; Intent → System Prompt → Topic’e bağla → outcome → Evidence.

### 3. Bugünkü davranış
—

### 4. Vizyondaki davranış
Topic içinde intent ile üretim; prompt yazmaz.

### 5. Problemler
Eksik omurga parçası; ama “yanlış modül” değil — henüz yok. Önce Topic/Evidence bağlanmalı.

### 6–7. —
Sistem prompt + Topic bağ.

### 8. Ne olmalı?
**Topic’e bağlanarak eklenmeli** — bağımsız NotebookLM app olarak değil. Şimdilik yokluğu, yanlış varlıktan iyidir.

### 9. Puan: **n/a (0 varlık / omurga hazır değil)** — hizalama borcu: Topic+Evidence önce.

---

## Özellik: Confidence / Observation / Living Plan (LOS motorları)

### 1. Bugünkü amacı
Kodda **adlandırılmış olarak yok**.

### 2. LOS’taki amacı
LOS’in kalbi.

### 3–5. Problemler
RuleEngine/Insight/Planner/Revision var ama Confidence Engine, Observation Mode, Living Plan state machine ürünleşmemiş. Bu yüzden Decide çoğu zaman ya kullanıcıda ya anlık kuralda.

### 8. Ne olmalı?
**Sistem içine kurulmalı** — kullanıcıya ekran olarak değil, davranış olarak.

### 9. Puan: **0 / 10** (yokluk)

---

## Skor tablosu (özet)

| Özellik | Puan |
|---------|------|
| Dashboard | 3 |
| Bottom Nav | 1 |
| Onboarding | 5 |
| Subjects | 4 |
| Subject Hub | 2 |
| Topic yüzeyi | 1 |
| Study Plan | 2 |
| Adaptive Planner | 4 |
| Goals | 1 |
| Revision | 3 |
| Resources | 2 |
| Pomodoro | 4 |
| Questions | 3 |
| Exams | 4 |
| Statistics | 3 |
| AI Coach | 6 |
| AI Chat | 0 |
| Memory / AI Settings | 2 |
| Achievements | 2 |
| Profile | 2 |
| Confidence / Observation / Living Plan | 0 |
| **Ürün ortalaması (yaklaşık)** | **~2.6–3.2** |

---

## En kritik 10 dönüşüm maddesi

*(Öncelik sırası — bu bir sprint planı değildir; dönüşüm omurgasıdır. Yeni özellik şişirmeden önce bu hizalama.)*

1. **Dashboard → Today OS**  
   Tek Next Action + ilerleme + kalan bloklar + kısa Journey. Kart hub’ı bitsin.

2. **Navigasyon → Today · Topic · Journey**  
   Plan / Pomodoro / İstatistik / sahte Profil sekmeleri modül OS’i yaşatıyor; kırılmalı.

3. **Topic → Work Surface + `topic_code` Evidence**  
   Catalog’u ürüne çevir. Tüm aktiviteler Topic’e bağlansın. Free-text topic bitsin.

4. **Subject Hub → Container**  
   Modül launcher kaldırılsın. Subject yalnızca Topic’e giden kapı.

5. **Study Plan + Adaptive Planner → Living Plan (sistem içi)**  
   Kullanıcı CRUD/wizard bitsin. observe→suggest→accept→adapt.

6. **Goals / Revision / Achievements / Resource org → sistem içi motorlar**  
   Kullanıcı yüzeyi kapanır veya Today/Topic/Journey’ye iner.

7. **Pomodoro → sensör (Today/Topic bağlamı)**  
   Bağımsız timer app bitsin.

8. **AI Chat → kaldır / Explain-only intent**  
   Serbest prompt yasak. AI Coach → Today reason.

9. **Confidence Engine + Observation Mode**  
   Decide’in eşiği yoksa LOS işlemez. Ekran değil, davranış.

10. **Statistics / Exam yorumu → Journey; Questions/Resources → Topic**  
    Raporla Decide etmek bitsin; Evidence Topic’te, özet Journey’de.

---

## Mesafe özeti

```
Eski vizyon (Modül OS)  ████████████████░░░░  ~80% ürün davranışı
Yeni vizyon (LOS)       ████░░░░░░░░░░░░░░░░  ~20% (catalog, RuleEngine çekirdek, Active Exam)
```

Domain tohumları (Subject/Topic catalog, Primary≠Active, RuleEngine insights, Journey alanları) LOS’e **yakın**.  
Kullanıcıya açılan yüzeyler ve CRUD akışları LOS’ten **uzak**.

**Sonuç cümlesi:**  
StudyOS bugün “çok özellikli sınav asistanı”; LOS ise “kanıt toplayıp karar veren işletim sistemi” ister. Aradaki boşluk yeni sprintlerle doldurulmaz — önce mevcut sistem bu belgeye göre hizalanır.

---

## Belge ilişkisi

| Belge | Rol |
|-------|-----|
| Product Vision / Design Principles / LOS | Hedef |
| UX Vision Gap Audit | UX sapma haritası |
| **System Alignment Audit** | Tüm sistem (ekran + API + entity davranışı) gerçek durum |

Bu denetim güncellenmeden “yeni özellik” vizyon sapması riskidir.
