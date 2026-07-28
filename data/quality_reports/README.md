# quality_reports

Her üretim (veya batch) için kalite raporu.

## Yol şeması

```
quality_reports/
  {exam}/
    {yyyy}/
      {batch_or_question_id}.json
```

## Tipik alanlar

- `style_score`
- `difficulty_score`
- `similarity_score`
- `grammar_score`
- `blueprint_score`
- `duplicate_score`
- `overall_score`
- `generation_model`
- `generation_time_ms`
- `prompt_version`, `style_version`
- `passed_quality_gate` (bool)

Şema: [`_schema.example.json`](_schema.example.json)

M26’da gerçek rapor üretilmez.
