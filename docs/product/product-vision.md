# StudyOS — Product Vision (SSOT)

**Belge Durumu:** Aktif — tüm sprintlerin referansı  
**Sürüm:** 1.0  
**Tarih:** 2026-07-19 — Product Vision Reset  
**Kaynak:** Product Vision Reset (Meeting-035)

> Bundan sonraki bütün geliştirmeler bu belgeye uymak zorundadır.  
> Özellik eklemek, bu vizyonu güçlendirmiyorsa reddedilir.  
> **Değişmez tasarım prensipleri:** [`design-principles.md`](design-principles.md) (11 kural).  
> **Learning Operating System:** [`learning-operating-system.md`](learning-operating-system.md) (v2.0 — düşünme mekanizması + LOS Principles).  
> **System Alignment Audit:** [`system-alignment-audit.md`](system-alignment-audit.md) (mevcut sistem vs LOS — sprint değildir).  
> **Mevcut ürün UX gap audit:** [`ux-vision-gap-audit.md`](ux-vision-gap-audit.md) (implementasyon planı değil).

---

## 1. Amaç

StudyOS bir görev yöneticisi, not uygulaması, pomodoro veya AI chatbot değildir.

StudyOS; **öğrencinin hazırladığı sınavı anlayan, onu sürekli gözlemleyen, davranışlarını öğrenen ve zamanla kişiselleşen yapay zekâ destekli bir öğrenme işletim sistemidir.**

Ürünün amacı özellik sunmak değil; **kullanıcının mümkün olduğunca az düşünerek çalışmasını sağlamaktır.**

Kullanıcı sadece çalışır. StudyOS geri kalan her şeyi organize eder.

---

## 2. Tasarım felsefesi

> **Complexity belongs to the system, not to the student.**

Kullanıcı uygulamayı açtığında ne yapacağını düşünmemeli. Sistem bugün ne yapacağını söylemeli.

Çok fazla kart / modül / ekran / bilgi = vizyon sapmasıdır.

Her ekran şu soruya cevap vermelidir: *“Kullanıcının şu anda yapması gereken en önemli şey nedir?”* Cevap yoksa ekran yeniden tasarlanır.

---

## 3. Domain hiyerarşisi

```
Exam (Active / Primary)
  → Subject (subject_code)
    → Topic (topic_code)     ← öğrenmenin temel birimi
      → Activities
```

Aktiviteler (Question, Revision, Flashcard, Resource, Pomodoro, Exam, Planner, AI, Statistics) **Topic altında** birleşir. Subject container’dır; Topic öğrenme birimidir.

---

## 4. Sınav = ürün deneyimi

`exam_type` + `branch` yalnızca veri değildir. Her sınav **Exam Experience Pack** ile kendi ürünüdür:

| Pack | Örnek yüzey |
|------|-------------|
| YKS | üniversite, bölüm, TYT/AYT, net, sıralama |
| KPSS (lisans/önlisans/ortaöğretim) | Türkçe…Güncel, puan, branş/seviye |
| YDS | Reading, Grammar, Vocabulary, Translation… |

Dashboard, hedefler, istatistikler, AI dili, plan — Active Exam pack’e göre değişir.

---

## 5. Üç kullanıcı yüzeyi

1. **Today** — tek Next Action + kısa neden (evidence)
2. **Topic Work Surface** — konu seçilince kaynak / soru / flashcard / pomodoro / AI / deneme
3. **Journey** — hedef, ilerleme, Active Exam (derin istatistik ikincil)

Modüller bu yüzeylere hizmet eder; bağımsız “uygulama içinde uygulama” olmaz.

---

## 6. AI ilkeleri

- AI chatbot değil; **davranış koçudur**.
- **RuleEngine karar verir; LLM yalnızca Explain** yapar.
- AI **tekil** doğru/yanlışa göre plan veya davranış değiştirmez.
- Trend gerekir: pencere (N hafta / N deneme), min sample, tekrarlayan sinyal.
- Öneri dili: *neden + hangi veri + hangi trend* (kanıtsız “konu çalış” yok).

---

## 7. Plan ve Pomodoro

- Mevcut çalışma sistemi varsa: önce **gözlem**; ilk gün zorlama yok.
- Sistem yoksa: starter plan + “seni tanıdıkça gelişecek” living disclaimer.
- Plan state: `observe → suggest → accept → adapt`.
- Pomodoro zamanlayıcı değil; **davranış sensörü** (süre, saat, odak, ders kırılımı).

---

## 8. Kullanıcı seçimi ve prompt

- Kullanıcı mümkün olduğunca **az seçim** yapar.
- Kullanıcı **prompt yazmaz**. Intent (subject/topic/count/exam) → System Prompt Builder → harici üretim (ör. NotebookLM) → sonuç Topic’e bağlanır.

---

## 9. Değişmez teknik kilitler

- Subject-first; Topic canonical `topic_code`
- Primary ≠ Active Exam
- RuleEngine karar / LLM Explain Only
- Additive API tercihi; big-bang rewrite yok
- Journey-merkezli Dashboard yönü korunur (Today OS’e evrilir)

---

## 10. Sprint kapısı (gate)

Her sprint planı onaya gelmeden:

1. Kullanıcının düşünme yükünü azaltıyor mu?
2. Exam Experience Pack’e mi, genel modüle mi hizmet ediyor?
3. Topic canonical identity korunuyor mu?
4. RuleEngine mi karar veriyor? LLM sadece Explain mi?
5. Tekil olayla plan/AI mutate edilmiyor mu?
6. Today / Topic / Journey yüzeylerinden hangisine yazılıyor?
7. [`design-principles.md`](design-principles.md) — kullanıcı modül mü yönetiyor? Dashboard kontrol paneli mi? Feature “bugünkü çalışmayı kolaylaştırıyor mu?”

Her sprint sonunda: *Bu sprint ikinci beyin vizyonuna yaklaştırdı mı?* Hayırsa tamamlanmış sayılmaz.

---

## 11. Roadmap özeti (3.2+)

Detay: [`docs/planning/roadmap-vision-aligned.md`](../planning/roadmap-vision-aligned.md)

| Faz | Sprintler | Odak |
|-----|-----------|------|
| A Learning unit | 3.2.B → 3.2.D | Topic Hub → Activity codes → Work Surface |
| B Second brain | 3.3.A → 3.3.D | Today OS → Exam Packs → Trend RE → Explain |
| C Living system | 3.4.A → 3.4.D | Observation → Living plan → Pomodoro graph → Content gen |

---

## 12. Teşhis (Vision Reset anı)

Domain omurgası (Profile, Subject/Topic catalog, Primary/Active, RuleEngine, Journey Hub) vizyona yakın.  
Ürün omurgası hâlâ **modül OS**. Sonraki sprintler özellik şişirmek için değil; **Today → Topic Work Surface → Trend → Living Plan** döngüsünü tamamlamak içindir.
