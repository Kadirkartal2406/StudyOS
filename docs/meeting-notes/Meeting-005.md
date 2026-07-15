# Meeting-005 — Ürün Kapsam Dondurma ve Özellik Matrisi

**Tarih:** 2026-07-04  
**Katılımcı AI:** Claude (Anthropic) — Sonnet 4.6  
**Oturum Hedefi:** StudyOS için tam özellik listesini oluşturmak ve MVP kapsamını dondurmak  
**Durum:** Tamamlandı — Onay Bekliyor  
**Önceki Toplantı:** Meeting-004 — AI Geliştirme Anayasası

---

## Yapılanlar

### 1. Okunan Belgeler
- `docs/project/ai-rules.md` — Anayasa
- `docs/requirements/institution-platform-requirements.md` — Öğrenci Uygulaması gereksinimleri
- `docs/requirements/student-platform-requirements.md` — Kurumsal Platform gereksinimleri
- `docs/presentations/studyos-presentation-v1.md` — Referans için başlık düzeyinde tarandı

### 2. Özellik Matrisi Oluşturuldu
`docs/planning/feature-matrix.md` dosyası oluşturuldu.

**Kapsam:**

| Kategori | Toplam Özellik |
|----------|---------------|
| Öğrenci Uygulaması | 31 |
| Kurumsal Platform | 29 |
| Entegrasyon | 7 |
| Altyapı | 7 |
| **Toplam** | **74** |

### 3. MVP Kapsamı Tanımlandı

| Platform | MVP Özellik Sayısı |
|----------|-------------------|
| Öğrenci Uygulaması | 13 |
| Kurumsal Platform | 14 |
| Ortak / Altyapı | 8 |
| **Toplam** | **35** |

### 4. Sürüm Dağılımı

| Sürüm | Özellik Sayısı |
|-------|---------------|
| MVP | 35 |
| v1.1 | 22 |
| v2.0 | 8 |
| Gelecek | 8 |

---

## Alınan Kararlar

| # | Karar | Gerekçe |
|---|-------|---------|
| D-001 | Yinelenen "AI Plan Oluşturma" özelliği tek özellikte birleştirildi | Kaynak belgede iki kez tanımlanmıştı; S-07 olarak birleştirildi |
| D-002 | Sunum belgesindeki Kurumsal MVP tanımı değil, gereksinim belgesi esas alındı | Gereksinim belgesi birincil kaynak; sunum ikincil |
| D-003 | Sosyal özellikler (S-27, S-28, S-29) ve platform genişletme (S-30, S-31) kapsam dışı bırakıldı | MVP ve v2.0 için çekirdek ürün yeterli; bu özellikler erken karmaşıklık yaratır |
| D-004 | 7 iyileştirme önerisi ayrı bölümde toplandı; hiçbiri otomatik olarak kapsama eklenmedi | AI Anayasası Bölüm 8: Nihai karar proje sahibine aittir |

---

## Oluşturulan / Güncellenen Dosyalar

| Dosya | İşlem | Açıklama |
|-------|-------|----------|
| `docs/planning/feature-matrix.md` | **OLUŞTURULDU** | 74 özellikli tam matris, MVP tanımı, sorun tespiti, öneriler |
| `docs/planning/` | **OLUŞTURULDU** | Yeni klasör — planlama belgeleri için |
| `docs/meeting-notes/Meeting-005.md` | **OLUŞTURULDU** | Bu toplantı notu |

---

## Açık Sorular — [ONAY GEREKTİRİR]

| # | Soru | Öncelik |
|---|------|---------|
| AQ-001 | Ücretsiz plan hangi özellikleri kapsıyor? Premium sınırı nerede başlıyor? | Yüksek — MVP öncesi |
| AQ-002 | Öğrenci kuruma nasıl bağlanır? Davet kodu mu, e-posta eşleşmesi mi? | Yüksek — MVP öncesi |
| AQ-003 | Veli hesabı nasıl oluşturulur? Kurum tanımlar mı, kendisi mi kayıt olur? | Orta — v1.1 öncesi |
| AQ-004 | Optik cevap kağıdı aktarımı hangi formatı destekleyecek? | Orta — v1.1 öncesi |
| AQ-005 | Gereksinim dosyaları yeniden adlandırılsın mı? (adlandırma uyuşmazlığı) | Düşük — isteğe bağlı |

---

## Kalite Kontrol

```
[x] Oturum hedefi tamamlandı
[x] Toplantı notu oluşturuldu
[x] 4 karar belgelendi
[x] Değiştirilen/oluşturulan dosyalar listelendi
[x] Adlandırma kurallarına uyuldu
[x] Yinelenen özellik tespit edildi ve birleştirildi (S-07/S-16)
[x] Tutarsızlıklar Bölüm 6'da raporlandı
[x] Öneriler ayrı bölümde tutuldu, kapsama eklenmedi
[x] Onay gerektiren maddeler işaretlendi
[x] Bir sonraki adım netleştirildi
```

---

## Bir Sonraki Adım

**Meeting-006 önerisi:** Teknik Mimari Tasarımı

Özellik matrisi onaylandıktan sonra `docs/architecture/` altında teknik mimari belgesi oluşturulabilir:
- Uygulama bileşenleri
- API tasarım ilkeleri
- Veri modeli ana hatları
- Güvenlik mimarisi

> Bu matrisin geçerli olabilmesi için proje sahibinin 5 açık soruyu yanıtlaması önerilir.