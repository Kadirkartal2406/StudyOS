# qie_cache

Aynı blueprint ile tekrar üretimde LLM çağrısını azaltmak için önbellek.

## Cache key (mantıksal)

```
exam + subject + topic + difficulty + question_count + style_version
```

Dosya adı önerisi (hash veya düzgün slug):

```
qie_cache/
  {exam}__{subject}__{topic}__{difficulty}__n{count}__{style_version}.json
```

## İçerik

- Plan özeti (skill, bloom, distractor — metin değilse tercih)
- Üretilmiş soru payload’ı (AI çıktısı; resmi sınav metni değil)
- `created_at`, `expires_at`, `hit_policy`

**M26:** Yalnızca yapı. Cache okuma/yazma kodu sonraki sprint.

Şema: [`_schema.example.json`](_schema.example.json)
