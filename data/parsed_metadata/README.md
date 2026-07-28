# parsed_metadata

Parser çıktısı. Her resmi oturum için bir JSON.

## Yol şeması

```
parsed_metadata/
  {exam}/
    [{pack}/]
      {year_or_session}.json
```

Örnekler:

- `kpss/lisans/2021.json`
- `yks/tyt/2025.json`
- `ales/2021_1.json`
- `yokdil/ingilizce/fen/2026.json`

## İzin verilen alanlar

- `exam_code`, `pack`, `session_id`, `source_pdf` (göreli yol)
- `question_count`
- `answer_key` (yalnızca A–E harf dizisi; metin yok)
- `page_count`
- `subject_distribution`
- `topic_distribution`
- `skill_distribution`
- `exam_duration_minutes`
- `language`
- `difficulty_estimation`
- `reading_time_sec_avg`

Şema örneği: [`_schema.example.json`](_schema.example.json)

## Yasak

- Soru gövdesi (stem)
- Şık metinleri
- Açıklama / çözüm metni
- Telifli paragraf alıntısı

M26’da gerçek parse dosyası üretilmez; yalnızca yapı + şema hazırdır.
