# exam_style_profiles

Sınav bazlı **Style DNA** — QIE ve Prompt Builder’ın okuyacağı katman.

LLM PDF değil, buradaki profili kullanır.

## Dosyalar

| Dosya | Sınav |
|-------|--------|
| `KPSS.json` | KPSS (genel lisans bandı) |
| `TYT.json` | YKS TYT |
| `AYT.json` | YKS AYT |
| `ALES.json` | ALES |
| `YDS.json` | YDS |
| `YOKDIL.json` | YÖKDİL |
| `LGS.json` | LGS |
| `AGS.json` | AGS |
| `DGS.json` | DGS |

## Tipik alanlar

- `paragraph_ratio`, `paragraph_length_avg`
- `reasoning_style`, `reading_load`
- `bloom_distribution`
- `option_length_avg`, `distractor_style`
- `language_level`, `difficulty_band`
- `question_flow`, `time_pressure`
- `choice_count`, `style_version`

**Soru metni yok.** Değerler M26’da tahmini iskelet; parser sonrası güncellenir.
