# exam_style_stats

Ders / konu bazlı istatistik katmanı. Style DNA’yı konu düzeyinde besler.

## Yol şeması

```
exam_style_stats/
  {exam}/
    {subject}/
      [{topic}/]
        stats.json
```

Örnek:

```
exam_style_stats/kpss/turkce/paragraf/stats.json
exam_style_stats/tyt/turkce/paragraf/stats.json
```

## Tipik alanlar (soru metni yok)

- `paragraph_avg`, `sentence_count_avg`
- `difficulty_band`, `difficulty_distribution`
- `reasoning_type`, `skill_type`
- `reading_time_sec_avg`
- `option_distribution`
- `distractor_pattern`
- `vocabulary_level`
- `sample_size`, `source`

Şema: [`_schema.example.json`](_schema.example.json)  
Örnek iskelet: [`kpss/turkce/paragraf/stats.json`](kpss/turkce/paragraf/stats.json)
