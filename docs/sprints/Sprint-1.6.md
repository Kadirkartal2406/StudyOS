# Sprint-1.6 — Statistics & Analytics

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-014  
**Kapsam:** Backend statistics API + Flutter istatistik ekranı + Dashboard overview genişletmesi

---

## Amaç

Öğrenci çalışma verisini (oturum + plan) özetleyip grafiklerle görebilsin; Dashboard streak/pomodoro gibi özet metrikleri aynı kaynaktan alsın.

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| `Statistics` schemas / repository / service | ✅ |
| `GET /statistics/overview\|daily\|weekly\|monthly\|subjects\|topics\|productivity\|heatmap\|streak` | ✅ |
| Dashboard → `StatisticsService.get_overview` + şema alanları | ✅ |
| Unit + integration testler | ✅ |
| Yeni DB tablosu yok (Session + Plan aggregate) | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/statistics` Clean Architecture | ✅ |
| StatisticsScreen (Özet / Günlük / Haftalık / Aylık / Dersler) + fl_chart | ✅ |
| Router `/statistics`, bottom nav, Dashboard quick action | ✅ |
| Dashboard model yeni overview alanları | ✅ |
| Model / repository / provider / widget testler | ✅ |

---

## Alınan Kararlar

1. **API path:** `/statistics/overview|…` (eski taslak `/statistics/me/*` yerine).
2. **Kaynak:** `StudySession` + `StudyPlan` JOIN; plansız oturumlar `"Serbest"`.
3. **Dashboard:** overview alanları StatisticsService üzerinden (çift hesap yok).
4. **Chart:** mevcut `fl_chart` kütüphanesi.
5. **QuestionStatistics tablosu:** bu sprintte yok.

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 97 passed |
| `ruff check` | All checks passed |
| `mypy app` | Success |
| `flutter analyze` | No issues found |
| `flutter test` | 65 passed |

---

## Bilinen Sınırlamalar

- Streak, tamamlanmış oturum günlerine göre hesaplanır (`actual_duration_minutes == 0` olsa bile).
- Öğretmen/kurum öğrenci istatistikleri ve manuel soru girişi ertelendi.
- Heatmap varsayılan 30 gün.

---

## Bir Sonraki Sprint Önerisi

Plan kartından Pomodoro bağlama UX'i, oturum geçmişi UI, veya QuestionStatistics / öğretmen görünümü.
