# Sprint-2.0 — AI Study Coach Insight Engine

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-018  
**Kapsam:** InsightEngine + RuleEngine + `GET /ai/*` + Flutter `ai_coach` + Dashboard kartı  
**LLM:** Yok (NullAIProvider stub)

---

## Amaç

Çalışma / soru verilerinden rule-based içgörü ve öneri üretmek; gerçek LLM entegrasyonu olmadan AI Koç UI iskeletini ve API yüzeyini kurmak.

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | Canlı hesap; `ai_insights` DB tablosu yok |
| B1 | Authenticated student; premium gate yok |
| C1 | Dashboard additive: `today_ai_recommendation` (+ code) + kart |
| D1 | Doğruluk/soru trendi = QuestionRecord; süre/pomodoro/streak = Session/Statistics |
| E2 | 5 GET + tam AI Coach ekranı + Dashboard kartı + `AIProvider` stub |
| F1 | Feature matrix S-15 v1.1 kalır; insight foundation notu |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| `InsightEngine` + `InsightContext` | ✅ |
| `RuleEngine` (eşik sabitleri) | ✅ |
| `AiInsightsService` + schemas | ✅ |
| `GET /ai/overview\|recommendations\|trends\|performance\|productivity` | ✅ |
| `NullAIProvider` / `AIProvider` stub | ✅ |
| Dashboard `today_ai_recommendation*` | ✅ |
| Unit + integration testler | ✅ |
| Insight snapshot migration | ❌ (A1 bilerek yok) |
| `POST /ai/study-coach` LLM | ❌ (sonraki) |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/ai_coach` Clean Architecture | ✅ |
| AI Coach ekranı (özet / öneri / trend / performans / verimlilik) | ✅ |
| Route `/ai-coach` | ✅ |
| Dashboard “Bugünün AI Önerisi” kartı | ✅ |
| Quick action “AI Koç” | ✅ |
| Model / repository / widget testler | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 125 passed |
| `ruff check` (AI slice) | All checks passed |
| `flutter test` | 85 passed |

---

## Bilinen Sınırlamalar

- Gerçek LLM / Gemini yok; öneriler kural tabanlı Türkçe mesajlar.
- Öneriler her istekte yeniden hesaplanır (cache/persist yok).
- Premium / subscription gate yok.
- `POST /ai/study-coach`, `generate-plan`, `usage` henüz yok.
- S-15 tam ürün özelliği hâlâ v1.1.

---

## Bir Sonraki Sprint Önerisi

Gemini `AIProvider` adaptörü, sohbet endpoint’i, isteğe bağlı insight cache tablosu, premium gate.
