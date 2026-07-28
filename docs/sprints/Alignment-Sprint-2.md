# Alignment Sprint-2 — Subject → Learning Container

**Durum:** Onaylandı — implementasyon tamamlandı  
**Tür:** Alignment Sprint (feature sprint değil)  
**Backlog:** System Alignment Audit — kritik dönüşüm #4  
**Bağımlılık:** Alignment Sprint-1 (Today OS) tamamlandı  
**Tamamlandı:** 2026-07-20  
**Referans:** Product Vision · Design Principles · LOS v2.0 · System Alignment Audit · Alignment-Sprint-1

---

## 0. Alignment Sprint nedir?

Feature sprint değildir. Mevcut yüzeyi Learning Operating System’e hizalar.

```
Feature OS (Subject = work center + modül launcher)
    ↓
LOS (Subject = Learning Container → Topic seçimi)
```

Kurallar: sadeleştir · birleştir · sistem içine al · otomatikleştir.  
Yeni modül yok. Breaking / migration yok. Additive tercih.

---

## 1. Bu sprintin merkezi

**Merkez değil:** Subject Hub redesign / yeni kartlar.  
**Merkez:** Subject’i **Learning Container** yapmak.

Kullanıcının Subject yüzeyindeki **tek kararı:**

> Hangi konuyu çalışacağım?

```
Exam / Today
    ↓
Subject (Container)
    ↓
Topic listesi (tek Primary etkileşim)
    ↓
(Topic Work Surface → Alignment #3 — bu sprintte YOK)
```

---

## 2. Davranış hedefi

Subject’e giren kullanıcı:

- modül seçmez (Soru / Tekrar / Plan / Pomodoro / Deneme / Kaynak / Planner)
- AI / Resources / Planner kartlarında gezinmez
- “hangi aracı açayım?” diye düşünmez

yalnızca **konu listesinden bir Topic seçer** (veya listede gezinir).

Pasif bilgi hub → aktif konu seçimi.

---

## 3. Başarı kriteri

> Subject ekranına giren kullanıcı modül seçmez; yalnızca çalışacağı konuyu seçer.

Ölçülebilir smoke:

1. Subject Hub’da **modül action chip barı yok**.  
2. Revision / Planner / Exam / AI / Resources / Flashcards **kartları Today/Subject yüzeyinde yok** (launcher CTA yok).  
3. Ana içerik = **Topic listesi** (`topic_code` + ad).  
4. Kısa Subject özeti (isim + isteğe bağlı tek satır durum) — panel yığını değil.  
5. Topic satırı etkileşimli (seçim); Work Surface / Topic Detail route **açılmaz** (bu sprint).  
6. Bottom nav / Today / Living Plan değişmez.

---

## 4. Mevcut ihlaller

| Bugün | LOS |
|-------|-----|
| `SubjectHubActions` 7 chip | Modül launcher — yasak |
| Revision / Planner / Exam / AI / Resources / Flashcards kartları | Sistem içi motorlar / Topic’e ait |
| Topics listesi tıklanmaz, altta gömülü | Merkez olmalı |
| AppBar “Subject Hub” / work center dili | Container dili |

Audit skoru Subject Hub: **2/10** → hedef bu sprintte davranışsal sıçrama.

---

## 5. Today Surface composition (Subject Container)

### Kalır (sade)

1. **Header** — Subject display title (`subject_code` identity)  
2. **Kısa özet** — en fazla 1–2 satır (örn. progress % veya “bugün X dk” — tek bilgi şeridi; kart yığını değil)  
3. **Topics** — birincil liste; kullanıcının tek seçim yüzeyi  

### Subject yüzeyinden kalkar (UI demote)

- `SubjectHubActions` (tümü)  
- `SubjectHubRevisionCard` (+ onOpen)  
- `SubjectHubPlannerCard`  
- `SubjectHubExamCard`  
- `SubjectHubAiCard`  
- `SubjectHubResourcesCard`  
- `SubjectHubFlashcardsCard`  
- Ayrı `SubjectHubTodayCard` / şişmiş `ProgressCard` — özet şeridine indirgenir veya kalkar  

Widget dosyaları silinmez (additive / geri alınabilir); **Subject screen composition’dan çıkarılır**.

### Sistem içine / sonraya

| Parça | Nereye |
|-------|--------|
| Revision / Plan / Pomodoro / Questions | Today Next Action + ileride Topic Work Surface |
| AI | Today reason / Explain (#8) |
| Resources | Topic Work Surface (#3) |
| Flashcards | Topic / sistem içi |

---

## 6. Topic seçimi (Work Surface olmadan)

**Bu sprintte:** Topic Detail / Work Surface route **yok**.

Topic satırı:

- Görsel olarak birincil (liste merkezi).  
- `onTap` → **seçim** (highlight / selected `topic_code` state).  
- Modül deep-link **yok** (`/questions?subject_code=` vb. yasak).  
- Work Surface’e navigate **yok**.

Seçim, Alignment #3’e hazırlık: kullanıcı kararı “bu konu” olarak görünür; çalışma yüzeyi sonraki alignment’da açılır.

İsteğe bağlı mikro kopya (CTA değil): “Konu seçildi — çalışma yüzeyi yakında” / sessiz seçim. İkinci Primary Action olamaz.

---

## 7. Backend

**Tercih:** Flutter-first demote; API alanları **silinmez** (breaking yok).

| Seçenek | Açıklama |
|---------|---------|
| **A (önerilen)** | `GET .../subjects/{code}` aynı kalır. Client Container layout kullanır; kullanılmayan section’lar render edilmez. |
| **B (additive opsiyonel)** | Response’a `hub_layout: "container"` veya `primary_section: "topics"` echo — istemciler için ipucu. Zorunlu değil. |

Migration yok. Topic catalog endpoint’leri korunur.  
Activity’lere `topic_code` FK **bu sprintte yok** (#3 / #5 scope).

---

## 8. Flutter etkisi

- `subject_hub_screen.dart` composition yeniden yazılır → Container layout.  
- AppBar: “Subject Hub” → Subject adı veya “Ders”.  
- `SubjectHubTopicsCard` → Topics olarak merkez; satırlar seçilebilir.  
- `subjects_screen.dart` (liste): zaten container listesi; hafif kopya/UX uyumu yeterli; modül eklenmez.  
- Testler: action chip / AI / Resources kartı yok; topics görünür ve tıklanınca seçilir; deep-link modül yok.

---

## 9. Explicit non-goals

- Topic Work Surface / Topic Detail ekranı  
- Today / Next Action Engine değişikliği  
- Navigation → Today · Topic · Journey yapı değişimi  
- Living Plan / Study Plan CRUD  
- Confidence / Observation Engine  
- AI Explain / AI Chat  
- NotebookLM  
- Goals / Revision / Resources sistem-içi taşımanın tamamı (yalnızca Subject UI demote)  
- `topic_code` activity migration  
- Breaking API field silme  
- Yeni bottom tab / yeni feature modülü  

---

## 10. Riskler

| Risk | Mitigasyon |
|------|------------|
| Topic seçimi “boş” hissedilir (Work Surface yok) | Başarı = modül seçmeme + konu seçme; #3’te yüzey açılır; kopya net |
| Kullanıcı eski launcher arar | Alignment bilinçli; chip geri gelmez |
| API hâlâ şişman | Additive disiplin; UI demote yeterli |
| Scope creep (#3) | Non-goals sert |

---

## 11. Implementasyon sırası (onay sonrası)

1. Flutter: Subject Hub Container composition + Topics seçilebilir liste  
2. Widget testleri (launcher yok / topics merkez)  
3. Opsiyonel additive API flag (B) — yalnızca gerekirse  
4. Doküman: bu sprint “tamamlandı” + Meeting notu  

Onaysız kod yok.

---

## 12. Tek cümlelik özet

> Alignment Sprint-2, Subject’i çalışma merkezi olmaktan çıkarır; **Learning Container** yapar — tek karar Topic seçimidir; Work Surface ve diğer LOS motorları sonraki alignment’lara bırakılır.
