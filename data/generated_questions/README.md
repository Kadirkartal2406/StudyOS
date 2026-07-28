# generated_questions

AI (QIE → LLM) ile üretilen soruların dosya tabanlı arşivi.

**M26:** Yalnızca klasör iskeleti. Üretim yok.

## Yol şeması

```
generated_questions/
  {exam}/
    {subject}/
      {topic}/
        {difficulty}/
          {batch_or_id}.json
```

Örnek:

```
generated_questions/kpss/turkce/paragraf/medium/2026-07-28_batch01.json
```

## Not

- Runtime üretim hâlâ DB / API üzerinden olabilir; bu repo uzun süreli arşiv / export içindir.
- Her kayıtta `qie_card` (internal) + kalite skorları referansı tutulabilir.
- Telifli resmi soru metni buraya kopyalanmaz.
