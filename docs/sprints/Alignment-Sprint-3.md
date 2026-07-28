# Alignment Sprint-3 — Topic Work Surface

**Durum:** Tamamlandı  
**Tür:** Alignment Sprint  
**Backlog:** System Alignment Audit #3  
**Tamamlandı:** 2026-07-20  
**Referans:** LOS v2.0 · AS-1 · AS-2 · Product Vision · Design Principles

---

## 0. Alignment Sprint

Feature sprint değil. Topic’i liste satırından **Work Surface**’e hizalar.

---

## 1. Merkez

Topic = StudyOS’un çalışma yüzeyi.

```
Today → Subject (Container) → Topic (Work Surface)
```

### Değişmez ilke

> **Topic Work Surface karar üretmez.**  
> Yalnızca Today / Decision Engine Projection tarafından üretilen kararı **uygular**.

---

## 2. Onaylı revizyonlar (uygulandı)

1. Today mümkün olduğunca **Topic Work Surface**’e yönlendirir; plan/pomodoro ekranına doğrudan gitmez.  
2. Secondary tools: **Pomodoro · Kaynak · Soru Kaydı · Revision Durumu** — AI Explain / NotebookLM görünmez.  
3. Ayrı additive **work-surface** projection endpoint.  
4. Primary Action **amaç odaklı** (“Bu konu üzerinde çalış / tekrar yap”); araçlar aksiyonun içinde açılır.  
5. Kavram: **Learning State** (Current State değil).

---

## 3. Teslimat

### Backend

- `GET /learning-profile/subjects/{subject_code}/topics/{topic_code}/work-surface`
- `TopicWorkSurfaceProjection`: Learning State + `primary_action` (Decision) + secondary tools
- Next Action Engine: amaç odaklı copy; `deep_link_hint` → `/subjects/.../topics/...`
- `build_action_for_topic` — Work Surface kapsamında Decision kuralları

### Flutter

- Route: `/subjects/:subjectCode/topics/:topicCode`
- `TopicWorkSurfaceScreen` — Learning State, tek Primary, 4 secondary
- Subject Topics → Work Surface navigasyonu
- Today CTA mevcut `deep_link_hint` ile Work Surface’e gider

---

## 4. Non-goals (korundu)

Living Plan · Confidence · Observation ürünü · Today/Decision mimari rewrite · Nav/Journey redesign · NotebookLM/Explain algoritması · RuleEngine genişletme · topic_code migration

---

## 5. Başarı

Kullanıcı çalışmayı Topic Work Surface’te başlatır; tek Primary Action; karar Decision Engine’den gelir.
