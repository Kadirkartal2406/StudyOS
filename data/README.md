# StudyOS Official Exam Intelligence Repository

**Sprint M26** — Kalıcı veri katmanı.

Bu dizin, Question Intelligence Engine (QIE), Exam Style DNA ve gelecekteki AI soru üretimi için **resmi sınavlardan türetilen analiz verilerinin** tutulduğu modüler repository’dir.

## Pipeline (hedef)

```
Official Exams
  → Parser (M27)
  → Style Learning (M27.5)
  → Style Validation (M27.6)
  → Blueprint / QIE Plan
  → Question Author AI (M29)
  → Question Review AI (M30)
  → Virtual Student (M31)
  → Quality Gate / Difficulty / Similarity
  → Final Question
```

**Kritik kural:** LLM asla PDF okumaz. Yalnızca Style Contract / Style DNA okur.

### M27 çalıştırma

```bash
cd backend
python -m scripts.parse_official_exams
```

### M27.5 Style Learning

```bash
cd backend
python -m scripts.learn_exam_styles
```

### M27.6 Style Validation

```bash
cd backend
python -m scripts.validate_exam_styles
```

### M29 Question Author AI

QIE Orchestrator üzerinden otomatik (Author → frozen gates). Paket: `backend/app/services/question_author/`.

### M30 Question Review AI

Author sonrası baş editör katmanı (`backend/app/services/question_review/`). Soru üretmez; `review_score < 90` ise bir kez Author rewrite ister.

### M31 Virtual Student Simulation

Öğrenci gibi çözen kalite katmanı (`backend/app/services/question_virtual_student/`). Soru üretmez; FAIL olursa Review’e en fazla 1 bounce.

## Klasörler

| Klasör | Amaç |
|--------|------|
| [`official_exams/`](official_exams/) | Ham resmi PDF’ler (telifli; değiştirilmez) |
| [`parsed_metadata/`](parsed_metadata/) | Parser çıktısı — **soru/şık metni YOK** |
| [`exam_style_profiles/`](exam_style_profiles/) | Sınav bazlı Style DNA (M27) |
| [`exam_style_stats/`](exam_style_stats/) | Ders / konu istatistikleri |
| [`exam_style_contracts/`](exam_style_contracts/) | Konu Style Contract (M27.5) |
| [`exam_style_profiles_learned/`](exam_style_profiles_learned/) | Sınav thinking profile (M27.5) |
| [`style_validation/`](style_validation/) | M27.6 kalite doğrulama raporları |
| [`generated_questions/`](generated_questions/) | AI üretilmiş sorular (ileride) |
| [`quality_reports/`](quality_reports/) | Üretim kalite raporları |
| [`human_review/`](human_review/) | Beta / öğretmen geri bildirimi |
| [`qie_cache/`](qie_cache/) | QIE üretim önbelleği |
| [`embeddings/`](embeddings/) | Semantic similarity (ileride; şimdilik boş) |

## Bu sprintte yapılmayanlar

- PDF parse
- Soru üretimi
- AI çağrısı
- Decision / Confidence / Living Plan / Coach / Assessment / QIE pipeline kod değişikliği

Parser, Style DNA doldurma ve QIE bağlantısı **sonraki sprintlerde** gelir.

## Telif

`official_exams/` içindeki PDF’ler resmi kaynaklardır.  
`parsed_metadata/`, `exam_style_profiles/` ve `exam_style_stats/` içinde **asla** soru metni, şık metni veya cevap açıklaması tutulmaz — yalnızca istatistiksel / yapısal metadata.
