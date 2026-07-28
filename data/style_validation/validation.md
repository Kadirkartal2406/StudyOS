# StudyOS Style Validation Report (M27.6)

## Summary

- Contracts checked: **200**
- Contract failures: **0**
- Overall ready for M28: **True**
- Mean quality score: **100.0**

## Exam Quality Scores

| Exam | Mean Score | Contracts | Warnings |
|------|------------|-----------|----------|
| AGS | 100.0 | 2 | 0 |
| ALES | 100.0 | 35 | 0 |
| AYT | 100.0 | 26 | 0 |
| DGS | 100.0 | 18 | 0 |
| KPSS | 100.0 | 37 | 0 |
| LGS | 100.0 | 14 | 0 |
| TYT | 100.0 | 25 | 0 |
| YDS | 100.0 | 9 | 0 |
| YDT | 100.0 | 22 | 0 |
| YOKDIL | 100.0 | 12 | 0 |

## Best / Weakest Contracts

- Best: `ags_matematik__problemler` — **100.0**
- Weakest: `unknown__general` — **100.0**

## Clusters

- `reading_heavy`: 105
- `reasoning_heavy`: 37
- `calculation_heavy`: 19
- `knowledge_recall`: 12
- `mixed_general`: 11
- `language_rules`: 10
- `spatial_geometry`: 6

Cluster structure: **OK**

## Similarity

- [PASS] `kpss_turkce__paragraf` ↔ `yds_ingilizce__reading` = 0.812 (high)
- [PASS] `kpss_turkce__paragraf` ↔ `tyt_geometri__ucgenler` = 0.691 (low)
- [PASS] `ales_matematik__problemler` ↔ `tyt_matematik__problemler` = 0.689 (high)
- [PASS] `yds_ingilizce__reading` ↔ `ayt_fizik__hareket` = 0.667 (very_low)
- [PASS] `kpss_turkce__paragraf` ↔ `yokdil_ingilizce__fen` = 0.784 (high)
- [PASS] `tyt_matematik__problemler` ↔ `dgs_matematik__problemler` = 0.848 (high)
- [PASS] relative Δ=0.121 ['kpss_turkce__paragraf', 'yds_ingilizce__reading'] ≥ ['kpss_turkce__paragraf', 'tyt_geometri__ucgenler']
- [PASS] relative Δ=0.022 ['ales_matematik__problemler', 'tyt_matematik__problemler'] ≥ ['yds_ingilizce__reading', 'ayt_fizik__hareket']
- [PASS] relative Δ=0.157 ['tyt_matematik__problemler', 'dgs_matematik__problemler'] ≥ ['kpss_turkce__paragraf', 'tyt_geometri__ucgenler']

## Difficulty

- Checked: 200
- Failed: 0
- Avg max jump: 1.08

## Warnings (sample)

_No warnings._

## Suggestions

- Style layer looks healthy — safe to proceed to M28 Question Author AI.
