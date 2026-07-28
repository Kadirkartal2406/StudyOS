# official_exams

Ham resmi sınav PDF’leri. **Source of truth — değiştirilmez, parse edilmez (M26).**

## Mevcut yerleşim (korunur)

Mevcut PDF’ler silinmedi / taşınmadı. Örnekler:

```
official_exams/
  kpss/lisans/2021.pdf
  kpss/önlisans/...
  yks/tyt/2025.pdf
  yks/ayt/...
  yks/ydt/2026_ingilizce.pdf
  ales/1/2021.pdf
  yökdil/fen_bilimleri.pdf
  lgs/sayısal/...
  yds/...
  ags/...
  dgs/...
```

## Hedef klasör standardı (yeni oturumlar için)

Yeni indirilen PDF’ler mümkünse şu yapıya konur (`exam.pdf` adı tercih edilir):

```
official_exams/
  kpss/
    lisans/
      2021/exam.pdf
      2022/exam.pdf
    onlisans/
    ortaogretim/
  yks/
    tyt/
      2025/exam.pdf
      2026/exam.pdf
    ayt/
      2026/exam.pdf
    ydt/
      ingilizce/2026/exam.pdf
      almanca/2026/exam.pdf
  ales/
    2021_1/exam.pdf
    2021_2/exam.pdf
  yds/
    2026/exam.pdf
  yokdil/
    ingilizce/
      fen/2026/exam.pdf
      saglik/2026/exam.pdf
      sosyal/2026/exam.pdf
  lgs/
    sayisal/2025/exam.pdf
    sozel/2025/exam.pdf
```

Boş yıl klasörleri (`…/2021/`, `…/2026/` vb.) **standart iskelet** içindir; mevcut `.pdf` dosyaları yerinde kalır. Taşıma isteğe bağlı sonraki sprintte yapılabilir.

## Kurallar

1. PDF içeriğini düzenleme / yeniden adlandırma zorunluluğu yok (M26).
2. Parser bu klasörü yalnızca okur.
3. LLM / Gemini bu klasöre erişmez.
