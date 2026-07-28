# human_review

Beta / öğretmen geri bildirimi (RLHF benzeri iyileştirme için).

## Yol şeması

```
human_review/
  {yyyy}/
    {review_id}.json
```

veya export batch:

```
human_review/exports/{date}.jsonl
```

## Tipik etiketler

- `kotu_soru` / bad_question
- `kolay` / too_easy
- `zor` / too_hard
- `sik_hatali` / bad_options
- `gercek_sinav_hissi` (1–5)
- serbest `notes`

API tarafındaki QIE human eval ile hizalanabilir; bu klasör dosya arşividir.

Şema: [`_schema.example.json`](_schema.example.json)
