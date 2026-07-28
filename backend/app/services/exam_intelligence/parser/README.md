# Official Exam Intelligence Parser (M27)

Heuristic PDF analysis for StudyOS. **No LLM. No question-text persistence.**

## Pipeline

```
Official PDF
  → Parser (this package)
  → Metadata          (data/parsed_metadata/)
  → Style Stats       (data/exam_style_stats/)
  → Style DNA         (data/exam_style_profiles/)
  → QIE               (future — reads DNA only)
  → Gemini / LLM      (future — never reads PDF)
```

## Modules

| Module | Role |
|--------|------|
| `pdf_loader` | pypdf text extract (memory only) |
| `page_reader` | exam/year/pack inference from path |
| `question_locator` | number → page / length stats (transient blob) |
| `answer_key_locator` | `1:A` style keys only |
| `layout_analyzer` | paragraph / option / table / visual ratios |
| `subject_detector` | keyword → subject/topic codes |
| `topic_detector` | catalog blueprints by question number |
| `difficulty_estimator` | 0–100 heuristic |
| `reading_estimator` | seconds heuristic |
| `style_extractor` | per subject/topic stats |
| `style_dna_builder` | exam-level DNA JSON |
| `metadata_writer` | safe JSON writer + forbidden-field guard |
| `validation` | count / key / subject checks |
| `pipeline` | orchestration |

Scanned / empty-text PDFs fall back to answer-key shells or catalog expected counts, then `topic_detector` blueprints assign subject/topic **codes only**.

## Run

From `backend/`:

```bash
python -m scripts.parse_official_exams
python -m scripts.parse_official_exams --limit 5
```

## Forbidden

- Stem / choices / explanation in any written JSON
- PDF copy / OCR dataset / question bank
- Calls into Decision / QIE / Assessment / Coach / generation APIs

## Output safety

`metadata_writer.write_json` rejects forbidden keys (`stem`, `choices`, …).
Question locator clears `_transient_text` after heuristics.
