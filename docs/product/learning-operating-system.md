# StudyOS — Learning Operating System

**Belge Durumu:** Resmi — En üst seviye ürün mimarisi (Product Vision eşdeğeri)  
**Sürüm:** 2.0  
**Tarih:** 2026-07-19  
**Referans belgeler:**  
[`product-vision.md`](product-vision.md) · [`design-principles.md`](design-principles.md) · [`ux-vision-gap-audit.md`](ux-vision-gap-audit.md) · [`../project/ai-rules.md`](../project/ai-rules.md) · [`../architecture/software-architecture.md`](../architecture/software-architecture.md) · [`../architecture/api-design.md`](../architecture/api-design.md) · [`../planning/feature-matrix.md`](../planning/feature-matrix.md)

> Bu belge StudyOS’un **düşünme mekanizmasını** tanımlar.  
> Yazılım mimarisi, API, veritabanı, sprint veya ekran tasarımı değildir.  
> Bundan sonraki bütün özellikler bu belgeye uymak zorundadır.

---

## Önsöz

StudyOS bir sınav uygulaması değildir.

Klasik sınav uygulamaları içerik sunar, istatistik gösterir, kullanıcıya planlama yükünü bırakır.  
StudyOS ise kullanıcıyı **gözlemler**, davranışını **öğrenir**, kanıt **toplar**, güven **oluşturur**, kural motoruyla **karar verir** ve zaman içinde daha doğru şekilde **adapte olur**.

Bu belge ekranlardan değil şu kavramlardan konuşur:

davranış · gözlem · kanıt · güven · karar · öğrenme · adaptasyon

---

## 1. Learning Operating System nedir?

### 1.1 Tanım

**Learning Operating System (LOS)**; sınav bağlamını taşıyan, çalışma davranışını sürekli duyan, Topic biriminde kanıt biriktiren, Confidence ile belirsizliği yöneten, RuleEngine ile karar veren ve Learning Memory ile kişiselleşen işletim sistemidir.

Kullanıcıya görünen üç çıktı yüzeyi vardır: **Today**, **Topic Work Surface**, **Journey**.  
Bunlar ürünün kendisi değildir; LOS’in kullanıcıya yansıyan **projeksiyonudur**.

Goal, Revision, Planner, Achievement, Resource organization, Memory — kullanıcıya “modül” olarak sunulmaz. Bunlar LOS’in **iç motorlarıdır**.

### 1.2 StudyOS nasıl düşünür?

Sistem her zaman şu soruları sorar:

1. Bu olay hangi Exam / Subject / Topic’e ait?
2. Bu olay kanıt mı, gürültü mü?
3. Bu Topic hakkında ne kadar eminiz? (Confidence + belirsizlik)
4. Trend tekrarlıyor mu, yoksa tek seferlik mi?
5. Şu an Observation mı, Suggest mi, Today mutasyonu mu, Living Plan mutasyonu mu gerekir?
6. Kullanıcıya gösterilecek tek Next Action nedir?
7. Bu deneyimden Memory’ye ne yazılmalı?

LLM bu soruların hiçbirine **karar** vermez. LLM yalnızca mevcut kararın **nedenini** açıklar.

### 1.3 Kullanıcı açtığında sistem ne yapar?

Kullanıcının gördüğü: Next Action ve çalışmaya başlamak.  
Sistemin yaptığı (görünmez):

| Sıra | Sistem süreci |
|------|----------------|
| 1 | Active Exam + Primary bağlamı ve Exam Experience Pack kurallarını yükler |
| 2 | Observation Mode durumunu ve son Decision snapshot’ını çözer |
| 3 | Evidence aggregate’lerinden Confidence / Trend / due revision sinyallerini okur |
| 4 | Learning Memory’den chronotype, tempo, receptivity özetini alır |
| 5 | Decision Engine policy seçer (`HOLD_OBS` / `SUGGEST` / `MUTATE_TODAY` / …) |
| 6 | Today Engine tek Next Action + kalan blok özeti üretir |
| 7 | Kullanıcı çalışırken her olayı Sense → Bind → Evidence zincirine yazar |
| 8 | Oturum sonunda Aggregate → Confidence → (gerekirse) Decide yeniden çalışır |
| 9 | Learning Memory yavaş güncellenir |

Kullanıcı “hangi modülü açayım?” diye düşünmez. Sistem düşünür; kullanıcı çalışır.

### 1.4 Karar birimi

```
Exam (Primary ≠ Active)
  → Subject (kapsayıcı)
    → Topic (öğrenme birimi)
      → Evidence + Confidence + Trend
        → Decision
          → Next Action / Living Plan policy
```

Subject ders kutusu, Topic öğrenmenin atomudur. Karar Topic’te doğar; Exam pack kararın dilini ve öncelik uzayını biçimlendirir.

---

## 2. Core Learning Loop

LOS’in kalbi kapalı döngüdür. Tek olay döngüyü “bitirmez”; çoğu olay yalnızca Sense ve Evidence üretir.

```
        ┌─────────────────────────────────────────────────────┐
        │                                                     │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 1. SENSE     │  Davranış sensörü: oturum, soru, pomodoro,  │
 │              │  mola, kaynak, deneme, quiz, iptal…         │
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 2. BIND      │  Olayı Exam / Subject / Topic kimliğine     │
 │              │  bağla. Bağlanamayan olay zayıf evidence’dır│
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 3. EVIDENCE  │  Ham olayı kanıt kaydına dönüştür           │
 │              │  (kalite, gürültü bayrakları)               │
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 4. AGGREGATE │  Gün / hafta / trend pencerelerinde özetle  │
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 5. CONFIDENCE│  Topic inancı + belirsizlik                 │
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 6. TREND     │  Yön, tutarlılık, unutma, tekrarlayan sinyal│
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 7. DECIDE    │  RuleEngine → policy                        │
 └──────┬───────┘                                             │
        │                                                     │
   ┌────┼──────┬────────────┬──────────────┐                  │
   ▼    ▼      ▼            ▼              ▼                  │
 HOLD  SUGGEST MUTATE_TODAY MUTATE_PLAN  EXPLAIN_ONLY         │
   │    │      │            │              │                  │
   └────┴──────┴────────────┴──────────────┘                  │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 8. PROJECT   │  Today / Journey’ye yansıt (Next Action)    │
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │ 9. STUDY     │  Kullanıcı çalışır                          │
 └──────┬───────┘                                             │
        ▼                                                     │
 ┌──────────────┐                                             │
 │10. LEARN     │  Learning Memory güncelle ──────────────────┘
 └──────────────┘
```

### Aşama ilişkileri

| Aşama | Amaç | Sonraki aşamayı nasıl besler |
|-------|------|------------------------------|
| Sense | Dünyayı duymak | Bind olmadan Evidence güvenilmez |
| Bind | Anlam vermek | Topic’siz aggregate yanlıştır |
| Evidence | Kanıt üretmek | Aggregate’in hammaddesi |
| Aggregate | Gürültüyü azaltmak | Confidence tek olaya bakmaz |
| Confidence | Ne biliyoruz? | Decide belirsizlik kapısı |
| Trend | Yön nedir? | Tekrarlayan sinyal şartı |
| Decide | Ne yapmalı? | Policy seçimi |
| Project | Kullanıcıya sadeleştir | Tek Next Action |
| Study | Gerçek dünya | Yeni Sense |
| Learn | Uzun bellek | Gelecek Decide’i bias eder |

### Policy sözlüğü

| Policy | Anlam |
|--------|--------|
| `HOLD_OBS` | Dokunma; gözlemle |
| `SUGGEST` | Öneri; onay / erteleme niyeti |
| `MUTATE_TODAY` | Bugünün sırası / Next Action güncellenir |
| `MUTATE_PLAN` | Living Plan uyarlanır (yüksek eşik) |
| `EXPLAIN_ONLY` | Yeni karar yok; mevcut durumun dili |

**Kural:** Sense her zaman çalışır. Decide nadiren çalışır.

---

## 3. Evidence Engine

Evidence Engine, “doğru-yanlış sayacı” değildir. Topic üzerindeki öğrenme durumunu etkileyen **bağlanmış gözlemlerin** üretim ve sınıflandırma katmanıdır.

### 3.1 Kategoriler

#### A. Performance Evidence

Soru sonuçları (D/Y/B), zorluk ağırlıklı accuracy, deneme net/kırılım, NotebookLM / sistem quiz outcome, revision self-rate (Good / Again / Hard).

#### B. Effort Evidence

Konu çalışma süresi, soru hacmi, kaynak açma/tamamlama, pomodoro tamamlama, oturum uzunluğu ve parçalanma.

#### C. Temporal Evidence

Çalışma saati, haftanın günü, oturumlar arası boşluk, tekrara gecikme, unutma vekili (uzun temas yok + düşen performans).

#### D. Behavioral Micro-Evidence

Mola davranışı (erken mola, uzayan mola), pomodoro abort, yarım bırakılmış oturum, planlanan bloğu atlama (pasif gözlem).

#### E. Consistency Evidence

Aktif gün oranı, günlük süre varyansı, neglect (uzun süre dokunulmayan Topic/Subject), plan adherence (önerileni yapma oranı — kullanıcıya CRUD dayatmadan).

#### F. Preference Evidence

Kaynak tipi tercihi, pomodoro süresi tercihi, konu revisited kalıpları → öncelikle Learning Memory’ye akar.

#### G. Meta Evidence

Confidence history, trend history, öneri kabul/red, Observation süresi — Decide’in kendi geçmişi.

### 3.2 Vadeler

| Vade | Kavramsal pencere | Tipik kullanım |
|------|-------------------|----------------|
| Anlık | tek olay / tek oturum | Sense, Bind, Evidence; Decide etmez |
| Kısa | 1–3 gün | Today, due revision, günlük tempo |
| Orta | ~1–3 hafta | Confidence, Trend, SUGGEST, MUTATE_TODAY |
| Uzun | ay+ / journey | Learning Memory, Living Plan politikası |

### 3.3 Gözlem vs karar

| Kullanım | Örnek |
|----------|--------|
| Yalnızca gözlem | Preference, tek mola, tek iptal, tek doğru/yanlış |
| Karara aday (aggregate sonrası) | Orta vadeli accuracy + sample, tekrarlayan neglect, due revision, çok oturumlu tempo kayması |
| Karar üretmez | Achievement, dekoratif streak kutlaması, tek deneme net’i tek başına |

**Prensip:** Karar üreten kanıt her zaman **aggregated, quality-filtered ve confidence-weighted**’dır.

### 3.4 Evidence quality

Aşağıdakiler düşük kalite sayılır ve Decide’i zayıflatır:

- Aşırı kısa “tıklama” oturumu
- Topic’e bağlanamayan olay
- Çelişkili veya eksik kayıt
- Açıkça gürültü (yanlışlıkla açılıp kapanma)

---

## 4. Confidence Engine

Confidence, Topic için **inanç + belirsizlik** çiftidir. “Öğrendin / öğrenmedin” bayrağı değildir.

### 4.1 Bileşenler

| Faktör | Rol |
|--------|-----|
| Sample size | Az örnek → yüksek belirsizlik |
| Consistency | Aynı yönde tekrar → inanç güçlenir |
| Recency | Yeni kanıt eskiyi aşındırır |
| Trend | Eğim; tek nokta değil |
| Forgetting | Temas yokluğu + önceki yüksek inanç → decay |
| Evidence quality | Zayıf kanıt az ağırlık |
| Source diversity | Yalnız kolay soru ≠ sağlam inanç |
| Confidence history | Ani sıçrama şüphelidir; yumuşatma |

### 4.2 Nasıl oluşur?

Cold start: düşük inanç + yüksek belirsizlik = **bilinmiyor** (zayıf demek değildir).

Her aggregate turunda:

1. Yeni evidence quality-weight ile girer  
2. Sample büyüdükçe belirsizlik düşer  
3. Consistency trend ile hizalanırsa inanç kayar  
4. Forgetting, uzun sessizlikte inancı aşındırır  
5. History, tek günün abartılı etkisini keser  

### 4.3 Nasıl artar / düşer?

| Durum | Davranış |
|-------|----------|
| Tek doğru | İnanç neredeyse değişmez |
| Tek yanlış | İnanç neredeyse değişmez |
| Tutarlı başarı (yeterli sample) | İnanç yavaş yükselir, belirsizlik düşer |
| Tutarlı hata / çöküş trendi | İnanç daha hızlı düşer (asimetri) |
| Uzun unutma | İnanç decay; belirsizlik artabilir |
| Çelişkili kaynaklar | Belirsizlik artar; Decide tutuklanır |

### 4.4 Değişim hızı

- **Yavaş yüksel, kontrollü düş.** Öğrenmeyi “kazanmak” zor; kaybetmek (unutma + tekrarlayan hata) daha görünür olmalı ama panik yaratmamalı.
- **Belirsizlik kapısı:** Belirsizlik yüksekken skor “iyi” görünse bile Decide agresif olmaz.
- **Floor/ceiling yok gibi davran:** Asla mutlak 0/1; her zaman yeni evidence’a açık.
- **Cross-topic izolasyon:** Bir Topic olayı başka Topic confidence’ını doğrudan değiştirmez.

### 4.5 Decide’e etkisi

| Durum | Etki |
|-------|------|
| Bilinmiyor | Observation / exposure |
| Düşük inanç + düşük belirsizlik | Tamir adayı (Today / revision) |
| Yüksek inanç + düşük belirsizlik | Bakım; öncelik düşük |
| Çelişkili | Daha fazla örnek; plan dokunulmaz |

---

## 5. Decision Engine

Decision Engine = **RuleEngine**. LLM karar vermez.

### 5.1 Karar prensipleri

1. **Minimum evidence** yoksa karar yok.  
2. **Tekrarlayan sinyal** yoksa Living Plan yok.  
3. **Today operasyoneldir; Living Plan sözleşmedir** — eşikleri farklıdır.  
4. **Thrashing yasağı:** Aynı kararı kısa sürede tekrar tekrar verme.  
5. **Kullanıcı iradesi:** Red/cooldown Decide’i bağlar.  
6. **Exam pack bağlamı:** Aynı kural farklı pack’te farklı öncelik üretebilir; ama Decide hâlâ RuleEngine’dir.  
7. **Explain ayrımı:** Dil üretmek karar üretmek değildir.

### 5.2 Ne zaman hiçbir şey yapmamalı?

- Evidence yetersiz veya kalitesiz  
- Belirsizlik yüksek  
- Thrashing / cooldown aktif  
- Olay gürültü  

→ `HOLD_OBS`

### 5.3 Ne zaman yalnızca gözlem?

- Observation Mode zorunlu penceresi  
- Kullanıcının kendi sistemi var; henüz model yok  
- Yeni pack / bağlam sonrası kısa kalibrasyon  
- Confidence “bilinmiyor”  

→ Sense + Evidence + Memory; ACT minimal.

### 5.4 Ne zaman öneri?

- Yeterli orta vadeli aggregate  
- İyileştirme sinyali var ama zorunluluk yok  
- Kullanıcı receptivity uygun  

→ `SUGGEST` (kabul / ertele / yok say)

### 5.5 Ne zaman Today değişmeli?

`MUTATE_TODAY` (düşük–orta eşik):

- Next Action tamamlandı  
- Kritik due revision penceresi  
- Günlük tempo sapması için yeniden sıralama  
- Active Exam switch (Primary değişmez)  

Today değişimi Living Plan sözleşmesini bozmaz.

### 5.6 Ne zaman Living Plan güncellenmeli?

`MUTATE_PLAN` (yüksek eşik):

- Haftalık tekrarlayan Topic trendi  
- Kalıcı tempo / müsaitlik kayması (Memory)  
- Suggest → Accept tamamlandı  
- Observation kapıları kapandı  

Tek oturum, tek yanlış, tek deneme → asla.

### 5.7 Ne zaman kullanıcıdan onay?

- Living Plan’ı anlamlı değiştirmeden önce (`SUGGEST` → accept)  
- Observation’dan agresif adaptasyona ilk geçişte  
- Kullanıcının sistemi varken ilk büyük sapma önerisinde  

Today’in rutin Next Action zinciri için sürekli onay istenmez (aksi halde ikinci beyin ölür).

---

## 6. Observation Mode

### 6.1 Amaç

İlk dönemde sistemi kullanıcıya dayatma. Önce anla, sonra yönlendir.

### 6.2 Çalışma sistemi olan kullanıcı

- Starter planı zorla giydirme  
- Mevcut ritmi Sense et (saat, süre, konu dağılımı, tutarlılık)  
- Policy çoğunlukla `HOLD_OBS`; nadiren küçük `SUGGEST`  
- Today, alışkanlığa yakın güvenli Next Action üretebilir  
- Yeterli karşılaştırma verisi sonrası kişiselleştir

### 6.3 Çalışma sistemi olmayan kullanıcı

- Exam pack + müsaitlik + süre ile **starter Living Plan**  
- Açık sözleşme: *Seni tanıdıkça yaşayan şekilde optimize olacak*  
- Erken `MUTATE_PLAN` seyrek; günlük `MUTATE_TODAY` ölçülü  
- Observation yine vardır: varsayımlar doğrulanana kadar yüksek belirsizlik

### 6.4 Süre: takvim değil kanıt yoğunluğu

Observation “X gün sonra bitsin” diye değil, **kapılar** ile biter:

| Kapı | Anlam |
|------|--------|
| Minimum aktif çalışma günü | Gerçek oturumlar oluştu |
| Minimum Topic evidence | Birden fazla Topic’te sample |
| Minimum temporal sample | Saat/alışkanlık için tekrar |
| Stability | Tempo aşırı kaotik değil |

Kapılar dolmadan gerçek `MUTATE_PLAN` yok.  
Kapılar dolunca Observation gevşer; Decide tam politikaya geçer.

Observation’da Today boş kalmaz; ama Next Action “kesin teşhis” değil **güvenli varsayılandır**. Dil: henüz tanıyoruz.

---

## 7. Learning Memory

Learning Memory, kullanıcının zamanla oluşan **davranış modelidir**. Not listesi veya kullanıcıya açık CRUD değildir.

### 7.1 Öğrenilen alanlar

| Alan | İçerik |
|------|--------|
| Chronotype | Verimli saat dilimleri |
| Tempo | Tipik günlük/haftalık süre |
| Difficulty signature | Zorlandığı Topic/Subject kalıpları |
| Acquisition speed | Hızlı ilerlenen alanlar |
| Forgetting curve | Unutma eğilimi yüksek Topic’ler |
| Pomodoro signature | Süre tercihi, abort, odak |
| Break signature | Mola uzatma / erken kaçış |
| Resource preference | Video / PDF / soru / üretim |
| Schedule signature | Hafta içi/sonu, patlamalı/düzenli |
| Motivation dips | Düşüş günleri, iptal kümeleri |
| Plan receptivity | Öneri kabul/red oranı |
| Exam context | Active/Primary, hedef yönü |

### 7.2 Oluşum (kavramsal)

1. Preference ve Consistency Evidence yavaşça Memory’ye süzülür  
2. Tek olay overwrite etmez (yumuşak güncelleme)  
3. Memory, Decide’i **bias** eder; yerine geçmez  
4. Privacy kapısı ürün kararıdır; Memory editörü ana ürün değildir  

Memory okunur: Today (chronotype), Living Plan (tempo/receptivity), Explain (“seni şöyle gözlemledik”).

---

## 8. Today Engine

Today Engine, Decision Engine’in **günlük projeksiyonudur**. Amaç: şu an yapılacak en doğru tek şey.

### 8.1 Mantık sırası (kavramsal)

1. Sert bağlam: Active Exam, kalan süre, Observation bayrağı  
2. Due revision (unutma riski)  
3. Living Plan’ın bugünkü sözleşmesi  
4. Confidence & Trend (zayıf + kesinleşmiş öncelikli)  
5. Learning Memory (chronotype, tempo)  
6. Bugün tamamlananlar  

Çıktı: **tek Next Action** + kalan blok özeti + günlük ilerleme + kısa Journey satırı + RuleEngine reason.

### 8.2 Next Action seçimi

Seçici RuleEngine’dir.

Tipik öncelik:

1. Kritik due revision  
2. Living Plan sıradaki blok  
3. Düşük confidence + düşük belirsizlik (tamir)  
4. Exposure (bilinmeyen Topic — sample büyüt)  
5. Bakım (yüksek confidence — seyrek)

### 8.3 Etkileşimler

| Girdi | Today’e etkisi |
|-------|----------------|
| Confidence | Belirsizse dayatma yok; kesin zayıfsa öncelik |
| Trend | Tek gün kötü → hafif yeniden sıra; çok günlük → Suggest/Plan adayı |
| Revision Need | Sert girdi; ayrı “revision uygulaması” değil |
| Living Plan | Günlük sözleşmenin omurgası |
| Evidence (kısa vade) | Tempo sapması, tamamlanan bloklar |

Today tamamen **kanıt + politika + sözleşme** ile oluşur; kart koleksiyonu ile değil.

---

## 9. Living Plan

### 9.1 Nedir?

Living Plan; Exam pack + müsaitlik + Confidence/Trend + Learning Memory’ye göre yaşayan **orta vadeli çalışma sözleşmesidir**.

Kullanıcının sürüklediği statik takvim değildir.  
Sistem üretir → kullanıcı kabul eder → sistem adapte eder.

```
observe → suggest → accept → adapt
              ↑_________|
           (red → cooldown → hold veya daha küçük suggest)
```

### 9.2 Ne zaman değişir?

- Accept sonrası adapt  
- Yüksek eşikli `MUTATE_PLAN` (§5.6)  
- Kalıcı tempo/müsaitlik değişimi  
- Anlamlı Exam pack bağlam değişimi (yeniden kalibrasyon)

### 9.3 Ne zaman değişmez?

- Tek yanlış/doğru/deneme  
- Tek kaçırılan gün  
- Rutin Today yeniden sıralaması  
- Observation zorunlu penceresi  
- Red cooldown / thrashing koruması

### 9.4 Reddetme hakkı

1. Eski accept sürümü korunur  
2. Red → Memory (receptivity)  
3. Cooldown: aynı öneri hemen gelmez  
4. Today mevcut sözleşme içinde çalışır  
5. Sonra daha küçük alternatif önerilebilir; ısrar yok

### 9.5 Adaptasyon agresifliği

- **Kademeli.** Big-bang yeniden yazım yok.  
- Erken dönem muhafazakâr; Memory olgunlaştıkça ölçülü cesaret.  
- LLM planı değiştiremez.  
- RuleEngine değiştirebilir — yalnızca eşik aşılınca.

---

## 10. NotebookLM’in sistemdeki rolü

NotebookLM (ve benzeri üretim) izole “soru servisi” değildir. **Evidence üretici bileşendir.**

```
User Intent (konu / adet / zorluk…)
    ↓
System Prompt Builder   ← kullanıcı prompt yazmaz
    ↓
Harici üretim
    ↓
Topic’e bağla
    ↓
Kullanıcı çözer
    ↓
Outcome → Evidence Engine
    ↓
Aggregate → Confidence / Trend → (gerekirse) Decide → Today
```

### Bağlama kuralları

- Üretim ve sonuç **Topic** altına yazılır  
- Quiz outcome Performance Evidence’tır  
- Tek quiz Living Plan’ı değiştirmez  
- Learning Loop içinde Sense’in meşru kaynağıdır; Decide değildir  
- Explain, “neden bu üretim”i Today/Decision gerekçesine bağlayabilir  

Serbest sohbet ve kullanıcı prompt’u LOS’in parçası değildir.

---

## 11. Algoritmik fark — neden Learning Operating System?

| Boyut | Klasik sınav uygulaması | StudyOS LOS |
|-------|-------------------------|-------------|
| Ürün birimi | Modül / içerik / ekran | Kapalı Learning Loop |
| Öğrenme birimi | Ders listesi veya konu metni | Topic + Evidence + Confidence |
| Karar sahibi | Kullanıcı veya sohbet AI | RuleEngine + eşikler |
| LLM | Planlayan / chatbot | Explain Only |
| Zaman modeli | Anlık skor | Trend + sample + forgetting |
| İlk gün | Hemen optimize et | Observation Mode |
| Plan | Statik veya kullanıcı CRUD | Living Plan (accept→adapt) |
| Hafıza | Yok veya not | Learning Memory |
| Bugün | Dashboard kartları | Today Engine → tek Next Action |
| İçerik üretimi | İzole quiz | Evidence’a bağlı üretim |

**StudyOS’u LOS yapan prensipler:**

1. Complexity belongs to the system.  
2. Sense her zaman; Decide nadiren.  
3. Tek olay karar değildir.  
4. Confidence = inanç + belirsizlik.  
5. Today operasyon; Living Plan sözleşme.  
6. İç motorlar kullanıcıya modül olarak açılmaz.  
7. Her Exam pack ayrı ürün deneyimi bağlamıdır; Decide yine kural tabanlıdır.

Bir cümle:

> StudyOS, öğrencinin yerine sürekli kanıt toplayıp güvenle karar veren bir işletim sistemidir; öğrenci yalnızca çalışır.

---

## 12. Belge hiyerarşisi

| Belge | Rol |
|-------|-----|
| Product Vision | Ne için varız |
| Design Principles | Değişmez ürün kuralları |
| **Learning Operating System** | Nasıl düşünürüz (bu belge) |
| UX Vision Gap Audit | Mevcut sapma haritası (UX) |
| System Alignment Audit | Mevcut sistem vs LOS (tam denetim) |
| AI Rules | Geliştirici AI anayasası (bu LOS’e bağlı) |
| Software Architecture / API Design / Feature Matrix | Uygulama katmanı — LOS’e aykırı özellik eklenemez |

Çelişki varsa: önce LOS ve Vision düzeltilir veya özellik reddedilir. “Özellik var diye LOS eğilmez.”

---

## 13. Learning Operating System Principles

*(Manifesto — her özellik bu ilkelere uymak zorundadır. Product Vision ve Design Principles’ı tamamlar; çelişmez.)*

1. **Öğrenci çalışır; sistem düşünür.**  
   Kullanıcı modül yönetmez. Goal, Revision, Planner, Achievement, Resource organization iç motordur.

2. **Ürün ekran değil, döngüdür.**  
   Sense → Evidence → Aggregate → Confidence → Trend → Decide → Project → Study → Learn. Ekran yalnızca projeksiyondur.

3. **Karar birimi Topic’tir.**  
   Subject kapsayıcıdır. Evidence Topic’e bağlanmadan karar doğmaz.

4. **Sense her zaman çalışır; Decide nadiren çalışır.**  
   Her olay kanıt olabilir; her olay karar değildir.

5. **Tek olay sistemı kandıramaz.**  
   Tek doğru = öğrendi değildir. Tek yanlış = zayıf değildir. Trend, sample, consistency şarttır.

6. **Confidence inançtır, rozet değildir.**  
   Belirsizlik yüksekken sistem eminmiş gibi davranmaz.

7. **RuleEngine karar verir; LLM açıklar.**  
   LLM plan üretmez, hedef seçmez, ders dayatmaz, Living Plan yazmaz.

8. **Önce gözlem, sonra yön.**  
   Observation Mode olmadan agresif adaptasyon yoktur. Sistemi olan kullanıcıya ilk gün yeni din dayatılmaz.

9. **Today operasyondur; Living Plan sözleşmedir.**  
   Today sık ve hafif değişebilir. Living Plan seyrek, eşikli ve tercihen kabul ile değişir.

10. **Reddetmek öğrenmektir.**  
    Kullanıcı öneriyi reddedebilir. Red cezalandırılmaz; Memory’ye yazılır; cooldown işler.

11. **Üretim Evidence’tır.**  
    NotebookLM ve benzeri çıktılar Learning Loop’a Topic üzerinden girer; izole içerik oyunu değildir.

12. **Kişiselleşme yavaş ve kanıtlıdır.**  
    Learning Memory tek günden oluşmaz. Adaptasyon kademelidir; thrashing yasaktır.

13. **Her sınav bağlamdır, her özellik Today’e hizmet eder.**  
    Exam Experience Pack Decide’in uzayını biçimlendirir. “Bugünkü çalışmayı kolaylaştırmıyorsa” özellik sapmadır.

14. **İkinci beyin testi.**  
    Bir özellik StudyOS’u kullanıcının yerine daha iyi düşündürüyor mu? Hayırsa — özellik değildir; gürültüdür.

---

## 14. Kabul cümlesi

Her gelecek iş için:

> Bu iş Learning Loop’u güçlendiriyor mu — yoksa yeni bir kullanıcı yönetim yüzeyi mi ekliyor?

İkincisiyse vizyon sapmasıdır ve reddedilir.
